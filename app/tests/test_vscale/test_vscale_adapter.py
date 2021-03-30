from copy import copy
from datetime import datetime
from ipaddress import IPv4Address

import pytest

from app.db.models.server import Server
from app.schemas.servers import ServerIn
from app.vscale.adapter import VScaleAdapter
from app.vscale.exceptions import (
    NoLocationFoundException,
    NoRplanFoundException,
    NoObjectToCreateFromException,
    TooManyRequestsException,
    NotAllServersCreatedException,
    VScaleClientAPIDeleteException,
    NotAllServersDeleteException,
)
from app.vscale.schemas.vscale_api import (
    ServerCreationRequest,
    ServerCreationResponse,
    Address,
    Key,
    ServerDeleteResponse,
)


async def mock_create_server(
    server_info: ServerCreationRequest,
) -> ServerCreationResponse:
    if server_info.name == "no_location_found":
        raise NoLocationFoundException(name=server_info.name)

    if server_info.name == "no_rplan_found":
        raise NoRplanFoundException(name=server_info.name)

    if server_info.name == "no_object_to_create_from":
        raise NoObjectToCreateFromException(name=server_info.name)

    if server_info.name == "too_many_requests":
        raise TooManyRequestsException(name=server_info.name)

    return ServerCreationResponse(
        status="defined",
        deleted=None,
        public_address=Address(
            netmask="255.255.255.0",
            gateway=IPv4Address("95.213.191.1"),
            address=IPv4Address("95.213.191.121"),
        ),
        active=False,
        location=server_info.location,
        locked=True,
        hostname="cs11533.vscale.io",
        created=datetime.now(),
        keys=[Key(name="somekeyname", id=16)],
        private_address=Address(),
        made_from=server_info.make_from,
        name=server_info.name,
        ctid=11,
        rplan=server_info.rplan,
    )


async def mock_remove_server(ctid: int) -> ServerDeleteResponse:
    if ctid == 0:
        raise VScaleClientAPIDeleteException(ctid)

    return ServerDeleteResponse(
        hostname="cs10299.vscale.ru",
        locked=False,
        location="spb0",
        rplan="huge",
        name="MyServer",
        active=True,
        keys=[],
        public_address=Address(
            netmask="255.255.255.0",
            gateway=IPv4Address("95.213.191.1"),
            address=IPv4Address("95.213.191.121"),
        ),
        status="deleted",
        made_from="ubuntu_14.04_64_002_master",
        ctid=10299,
        private_address=Address(),
    )


@pytest.mark.asyncio
async def test_server_created(mock_vscale_adapter: VScaleAdapter) -> None:
    servers = await mock_vscale_adapter.create_shutdown_servers(
        [
            ServerIn(
                location="test_location",
                rplan="test_plan",
                name="test_name",
                make_from="test_make_from",
                keys=[5],
            )
        ]
    )
    assert servers[0].name == "test_name"


@pytest.mark.asyncio
async def test_servers_created(mock_vscale_adapter: VScaleAdapter) -> None:
    servers = await mock_vscale_adapter.create_shutdown_servers(
        [
            ServerIn(
                location="test_location",
                rplan="test_plan",
                name="test_name1",
                make_from="test_make_from",
                keys=[5],
            ),
            ServerIn(
                location="test_location",
                rplan="test_plan",
                name="test_name2",
                make_from="test_make_from",
                keys=[5],
            ),
        ]
    )
    assert len(servers) == 2
    assert set(map(lambda server: server.name, servers)) == {"test_name1", "test_name2"}


@pytest.mark.asyncio
async def test_fail_create_server(mock_vscale_adapter: VScaleAdapter) -> None:
    exception = None
    try:
        await mock_vscale_adapter.create_shutdown_servers(
            [
                ServerIn(
                    location="test_location",
                    rplan="test_rplan",
                    name="no_location_found",
                    make_from="test_make_from",
                    keys=[5],
                ),
            ]
        )
    except NotAllServersCreatedException as e:
        exception = e

    assert exception is not None
    assert len(exception.already_established) == 0
    print(exception.content)
    assert exception.content["no_location_found"]["code"] == "NO_LOCATION_FOUND"


@pytest.mark.asyncio
async def test_successful_and_fail_create_server(
    mock_vscale_adapter: VScaleAdapter,
) -> None:
    exception = None
    try:
        await mock_vscale_adapter.create_shutdown_servers(
            [
                ServerIn(
                    location="test_location",
                    rplan="test_plan",
                    name="test_name",
                    make_from="test_make_from",
                    keys=[5],
                ),
                ServerIn(
                    location="test_location",
                    rplan="test_rplan",
                    name="no_rplan_found",
                    make_from="test_make_from",
                    keys=[5],
                ),
            ]
        )
    except NotAllServersCreatedException as e:
        exception = e

    assert exception is not None
    assert exception.already_established[0].name == "test_name"
    assert exception.content["no_rplan_found"]["code"] == "NO_RPLAN_FOUND"


@pytest.mark.asyncio
async def test_server_delete(
    mock_vscale_adapter: VScaleAdapter, server: Server
) -> None:
    await mock_vscale_adapter.remove_servers([server])
    assert server.status == "deleted"


@pytest.mark.asyncio
async def test_server_delete_with_fail(
    mock_vscale_adapter: VScaleAdapter, server: Server
) -> None:
    server2 = copy(server)
    server2.ext_ctid = 0
    exception = None
    try:
        await mock_vscale_adapter.remove_servers([server, server2])
    except NotAllServersDeleteException as e:
        exception = e
    assert exception is not None
    print(exception.already_deleted)
    print(exception.internal_exps)
    assert exception.already_deleted[0].ext_ctid == server.ext_ctid
    assert exception.internal_exps[0].server.ext_ctid == server2.ext_ctid
