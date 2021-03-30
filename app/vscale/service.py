from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.server import Server
from app.db.repositories.servers import ServerRepository
from app.schemas.servers import ServerIn as Py_ServerIn, Server as Py_Server
from app.vscale.adapter import VScaleAdapter
from app.vscale.exceptions import (
    NotAllServersCreatedException,
    NotAllServersDeleteException,
)


async def read_servers(db: AsyncSession) -> List[Server]:
    """
    Создает список всех существующих серверов
    :param db: асинхронная сессия подключения к бд
    :return: список существующих серверов
    """
    serv_repo = ServerRepository(db)
    return await serv_repo.read_all_servers()


async def create_servers(
    servers_in: List[Py_ServerIn], db: AsyncSession, vscale_adapter: VScaleAdapter
) -> List[Server]:
    """
    Создает множество серверов в vscale и записывет информацию о созданных серверах в бд
    :param servers_in: конфигурации серверов
    :param db: асинхронная сессия подключения к бд
    :param vscale_adapter: адаптер для vscale
    :return: список созданных серверов
    """
    # Отпарвляем запрос на создание серверов в vscale
    serv_repo = ServerRepository(db)
    try:
        servers = await vscale_adapter.create_shutdown_servers(servers_in)
    except NotAllServersCreatedException as exc:
        # Если получили ошибку при создании, то удаляем созданные сервера и возращаем описание ошибки
        # для каждого неудачно созданного сервера
        if exc.already_established:
            try:
                await vscale_adapter.remove_servers(exc.already_established)
            except NotAllServersDeleteException as delete_exc:
                # Если не получилось удалить какие-либо сервера, то сохраняем их
                not_deleted_servers = [ex.server for ex in delete_exc.internal_exps]
                await serv_repo.create_bulk_servers(not_deleted_servers)
                raise HTTPException(
                    status_code=500,
                    detail={
                        **exc.content,
                        "created_anyway": [
                            Py_Server.from_orm(server).json()
                            for server in not_deleted_servers
                        ],
                    },
                )
        raise HTTPException(status_code=500, detail=exc.content)
    # Сохраняем сервера в бд
    await serv_repo.create_bulk_servers(servers)
    return servers


async def remove_all_servers(
    db: AsyncSession, vscale_adapter: VScaleAdapter
) -> List[Server]:
    """
    Удаляет все существующие сервера
    :param db: асинхронная сессия подключения к бд
    :param vscale_adapter: адаптер для vscale
    :return: список удаленных серверов
    """
    # Получаем все сервера из бд
    serv_repo = ServerRepository(db)
    servers = await serv_repo.read_all_servers()
    if not servers:
        return []
    # Удаляем сервера в vscale, модифицируя status серверов в соответствии с ответом vscale
    try:
        await vscale_adapter.remove_servers(servers)
    except NotAllServersDeleteException as delete_exc:
        # Помечаем сервера которые удалось удалить как удаленные в бд и возвращаем ошибку
        await serv_repo.delete_servers(delete_exc.already_deleted)
        not_deleted_servers = [ex.server for ex in delete_exc.internal_exps]
        raise HTTPException(
            status_code=500,
            detail={
                "deleted": delete_exc.already_deleted,
                "not_deleted": [
                    Py_Server.from_orm(server).json() for server in not_deleted_servers
                ],
            },
        )
    # Удаляем сервера в бд
    await serv_repo.delete_servers(servers)
    return servers
