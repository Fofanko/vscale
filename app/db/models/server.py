from __future__ import annotations

from typing import List

from sqlalchemy import Column, Integer, DateTime, Boolean, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .key import Key
from ...vscale.schemas.vscale_api import (
    ServerCreationResponse as Py_ServerCreationResponse,
)


class Server(Base):
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(64), comment="Статус сервера")
    deleted = Column(
        DateTime,
        comment="Время удаления сервера",
        index=True,
        nullable=True,
        default=None,
    )
    active = Column(Boolean, comment="Маркер запуска сервера")
    location = Column(String(16), comment="Распроложение сервера")
    locked = Column(Boolean, comment="")
    hostname = Column(String(255), comment="Наименование хоста")
    created = Column(DateTime, comment="Время создания сервера")
    made_from = Column(
        String(255), comment="Id образа или бэкапа, на основе которого создан сервер"
    )
    name = Column(String(255), comment="Имя сервера")
    ext_ctid = Column(Integer, comment="Идентификатор сервера в vscale.io")
    rplan = Column(String(16), comment="Id тарифного плана")
    keys = relationship("Key", back_populates="server")

    public_address_gateway = Column(
        String(64), comment="Публичный гейтвей", nullable=True
    )
    public_address_netmask = Column(
        String(64), comment="Публичная маска сети", nullable=True
    )
    public_address_address = Column(
        String(64), comment="Публичный адрес", nullable=True
    )

    private_address_gateway = Column(
        String(64), comment="Приватный гейтвей", nullable=True
    )
    private_address_netmask = Column(
        String(64), comment="Приватная маска сети", nullable=True
    )
    private_address_address = Column(
        String(64), comment="Приватный адрес", nullable=True
    )

    @classmethod
    def from_vscale_create_response(
        cls, server_data: Py_ServerCreationResponse
    ) -> Server:
        """
        Создает объект Server из данных полученных из ответа запроса на создание сервера
        :param server_data: ответ запроса на создание сервера
        :return: объект Server
        """
        data = server_data.dict()
        public_address: dict = data.pop("public_address")
        private_address: dict = data.pop("private_address")
        data["ext_ctid"] = data.pop("ctid")
        for key, val in public_address.items():
            data[f"public_address_{key}"] = str(val)
        for key, val in private_address.items():
            data[f"private_address_{key}"] = str(val)

        keys: List[dict] = data.pop("keys")

        server = cls(**data)  # type: ignore
        server.keys = [Key.from_vscale_create_response(key) for key in keys]

        return server
