import asyncio
from typing import List

from app.db.models.server import Server
from app.schemas.servers import ServerIn
from app.vscale.client import VScaleAPIClient
from app.vscale.exceptions import (
    VScaleClientAPIException,
    NotAllServersCreatedException,
    VScaleClientAPIDeleteException,
    VScaleDeleteServerException,
    NotAllServersDeleteException,
)
from app.vscale.schemas.vscale_api import (
    ServerCreationRequest,
    ServerDeleteResponse,
)


class VScaleAdapter:
    def __init__(self, *, client: VScaleAPIClient) -> None:
        self._client = client

    async def create_shutdown_servers(self, servers_in: List[ServerIn]) -> List[Server]:
        """
        Создает выключенные сервера в vscale
        :param servers_in: список серверов с их конфигурацией
        :return: набор созданных серверов
        """

        # создаем корутины выполняющие запросы на создание серверов
        create_server_tasks = map(
            lambda server_info: self._create_server(server_info), servers_in
        )

        # Ждем пока все таски завершатся
        done, _ = await asyncio.wait(
            create_server_tasks, return_when=asyncio.ALL_COMPLETED
        )

        # Проходим по всем таскам и собираем созданные сервера и исключения при создании серверов
        servers = []
        exceptions = []
        for request_task in done:
            try:
                servers.append(request_task.result())
            except VScaleClientAPIException as e:
                exceptions.append(e)

        # Если при создании серверов возникли ошибки, то выбрасываем исключение о том,
        # что не все сервера были созданы
        if exceptions:
            raise NotAllServersCreatedException(servers, exceptions)

        return servers

    async def _create_server(self, server_info: ServerIn) -> Server:
        """
        Создает сервер в vscale
        :param server_info: концигурация сервера
        :return: инстанс сервера
        """
        server_create_requests_data = ServerCreationRequest(
            location=server_info.location,
            rplan=server_info.rplan,
            name=server_info.name,
            make_from=server_info.make_from,
            do_start=False,
            keys=server_info.keys,
            password=server_info.password,
        )
        return Server.from_vscale_create_response(
            await self._client.create_server(server_create_requests_data)
        )

    async def remove_servers(self, servers: List[Server]) -> None:
        """
        Удаляет сервера в vscale
        :param servers: список серверов для удаления
        """
        # Подготавливаем корутины для удаления серверов
        remove_server_tasks = map(lambda server: self._remove_server(server), servers)
        # Ждем пока все таски завершатся
        done, _ = await asyncio.wait(
            remove_server_tasks, return_when=asyncio.ALL_COMPLETED
        )

        deleted_servers: List[Server] = []
        exceptions: List[VScaleDeleteServerException] = []
        for request_task in done:
            try:
                server: Server = request_task.result()
                deleted_servers.append(server)
            except VScaleDeleteServerException as e:
                exceptions.append(e)

        if exceptions:
            raise NotAllServersDeleteException(deleted_servers, exceptions)

    async def _remove_server(self, server: Server) -> Server:
        """
        Отправляет запрос на удаления сервера и обновляет данные о нем
        :param server: инстанс сервера
        """
        try:
            remove_server_response: ServerDeleteResponse = (
                await self._client.remove_server(server.ext_ctid)
            )
        except VScaleClientAPIDeleteException as e:
            raise VScaleDeleteServerException(server)
        server.status = remove_server_response.status
        return server
