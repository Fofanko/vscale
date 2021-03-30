from datetime import datetime
from typing import Dict

import pytest

from app.db.models.server import Server
from app.tests.test_vscale.test_vscale_adapter import (
    mock_create_server,
    mock_remove_server,
)
from app.vscale.adapter import VScaleAdapter
from app.vscale.client import VScaleAPIClient


@pytest.fixture(scope="module")
def mock_vscale_adapter() -> VScaleAdapter:
    client = VScaleAPIClient(token="", base_url="")
    setattr(client, "create_server", mock_create_server)
    setattr(client, "remove_server", mock_remove_server)
    return VScaleAdapter(client=client)


@pytest.fixture(scope="module")
def server() -> Server:
    data: Dict = {
        "status": "started",
        "deleted": None,
        "active": True,
        "location": "spb0",
        "locked": False,
        "hostname": "cs10299.vscale.ru",
        "created": datetime.now(),
        "made_from": "ubuntu_14.04_64_002_master",
        "name": "MyServer",
        "ext_ctid": "10299",
        "rplan": "huge",
        "keys": [],
        "public_address_gateway": None,
        "public_address_netmask": None,
        "public_address_address": None,
        "private_address_gateway": None,
        "private_address_netmask": None,
        "private_address_address": None,
    }
    return Server(**data)  # type: ignore
