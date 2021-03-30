import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.servers import ServerIn as Py_ServerIn, Server as Py_Server
from app.vscale.adapter import VScaleAdapter
from app.vscale.service import create_servers, remove_all_servers, read_servers

router = APIRouter()


@router.get("/")
async def read_servers_endp(db: AsyncSession = Depends(deps.get_db)) -> Any:
    """
    Возращает существующие сервера
    """
    servers = await read_servers(db)
    return servers


@router.post("/", response_model=List[Py_Server])
async def create_servers_endp(
    servers_in: List[Py_ServerIn],
    db: AsyncSession = Depends(deps.get_db),
    vscale_adapter: VScaleAdapter = Depends(deps.get_vscale_adapter),
) -> Any:
    """
    Создает сервера с заданной конфигурацией
    """
    if not servers_in:
        raise HTTPException(
            status_code=400, detail="Необходимо передать как минимум одну конфигурацию"
        )
    servers = await create_servers(servers_in, db, vscale_adapter)
    return [Py_Server.from_orm(server) for server in servers]


@router.post("/bulk", response_model=List[Py_Server])
async def create_many_servers_endp(
    count: int,
    server_in: Py_ServerIn,
    db: AsyncSession = Depends(deps.get_db),
    vscale_adapter: VScaleAdapter = Depends(deps.get_vscale_adapter),
) -> Any:
    """
    Создает копии сервера в количестве count с заданной конфигурацией
    """
    if count <= 0:
        raise HTTPException(
            status_code=400,
            detail="Количество создаваемых серверов должно быть больше 0",
        )
    # Создадим массив серверов и присовим им уникальные имена путем добавления uuid4
    servers_info = [server_in.copy() for i in range(count)]
    for server in servers_info:
        server.name = f"{server.name}_{uuid.uuid4()}"
    servers = await create_servers(servers_info, db, vscale_adapter)
    return [Py_Server.from_orm(server) for server in servers]


@router.delete("/", response_model=List[Py_Server])
async def remove_all_servers_endp(
    db: AsyncSession = Depends(deps.get_db),
    vscale_adapter: VScaleAdapter = Depends(deps.get_vscale_adapter),
) -> Any:
    """
    Удаляет все существующие сервера
    """
    servers = await remove_all_servers(db, vscale_adapter)
    return [Py_Server.from_orm(server) for server in servers]
