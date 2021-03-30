from datetime import datetime
from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.server import Server


class ServerRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_server(self, server: Server) -> None:
        """
        Создает новую запись о сервере
        :param server: объект Сервера для записи в базу
        :return:
        """
        self._db.add(server)
        await self._db.commit()

    async def create_bulk_servers(self, servers: Sequence[Server]) -> None:
        """
        Создает множество записей Сервера в бд
        :param servers: объекы Сервера для записи в базу
        :return:
        """
        self._db.add_all(servers)
        await self._db.commit()

    async def read_all_servers(self) -> List[Server]:
        """
        Получает список существующих серверов
        :return: список серверов
        """
        stmt = select(Server).where(Server.deleted == None).options(selectinload(Server.keys))  # type: ignore
        return (await self._db.execute(stmt)).scalars().all()

    async def delete_servers(self, servers: Sequence[Server]) -> None:
        """
        Софт удаление серверов
        :param servers: Множество серверов для удаления
        :return:
        """
        now = datetime.now()
        for server in servers:
            server.deleted = now
        self._db.add_all(servers)
        await self._db.commit()
