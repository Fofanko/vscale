import aiohttp

from app.utils.helper import do_with_retry
from app.vscale.exceptions import (
    TooManyRequestsException,
    NoObjectToCreateFromException,
    UnexpectedException,
    NoLocationFoundException,
    NoRplanFoundException,
    VScaleClientAPIDeleteException,
)
from app.vscale.schemas.vscale_api import (
    ServerCreationRequest,
    ServerCreationResponse,
    ServerDeleteResponse,
)


class VScaleAPIClient:
    def __init__(self, token: str, base_url: str):
        """
        Http клиент для vscale
        :param token: токен доступа к vscale
        :param base_url: базовый url к vscale api
        """
        self._token = token
        self._base_url = base_url

    @do_with_retry(TooManyRequestsException)
    async def create_server(
        self, server_info: ServerCreationRequest
    ) -> ServerCreationResponse:
        """
        Отправляет http запрос на создание сервера
        :param server_info: конфигурация сервреа (тело запроса)
        :return: результат запроса
        """
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(
                f"{self._base_url}/scalets",
                json=server_info.dict(exclude_none=True),
                headers={"X-Token": self._token},
            ) as resp:
                data = await resp.json()
                if resp.status == 404:
                    if data["error"]["status"] == 404:
                        raise NoObjectToCreateFromException(server_info.name)
                    raise UnexpectedException(server_info.name)
                elif resp.status == 400:
                    if data["error"]["status"] == 523:
                        raise NoLocationFoundException(server_info.name)
                    raise UnexpectedException(server_info.name)
                elif resp.status == 500:
                    raise NoRplanFoundException(
                        server_info.name
                    )  # По доке должна приходить как 400, но приходит 500-ая
                elif resp.status == 429:
                    raise TooManyRequestsException(server_info.name)
                elif resp.status != 201:
                    raise UnexpectedException(server_info.name)

                return ServerCreationResponse(**data)

    @do_with_retry(TooManyRequestsException)
    async def remove_server(self, ctid: int) -> ServerDeleteResponse:
        """
        Отправляет http запрос на удаление сервера
        :param ctid: идентификатор сервера в vscale
        :return: результат запроса
        """
        async with aiohttp.ClientSession() as http_session:
            async with http_session.delete(
                f"{self._base_url}/scalets/{ctid}", headers={"X-Token": self._token}
            ) as resp:
                if resp.status != 200:
                    raise VScaleClientAPIDeleteException(ctid)
                data = await resp.json()
                return ServerDeleteResponse(**data)
