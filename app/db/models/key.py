from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .server import Server


class Key(Base):
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, comment="Идентификатор ключа в vscale.io")
    name = Column(String(255), comment="Имя ключа")
    server_id = Column(Integer, ForeignKey("server.id"))
    server = relationship("Server", back_populates="keys")

    @classmethod
    def from_vscale_create_response(cls, key_data: dict) -> Key:
        """
        Создает объект Key из словаря полученного из ответа на запрос создания сервера
        :param key_data: данные о ключах в ответе запроса
        :return: объект Key
        """
        external_id = key_data.pop("id")
        return cls(external_id=external_id, **key_data)  # type: ignore
