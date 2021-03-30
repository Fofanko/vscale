from __future__ import annotations

from typing import List

from app.db.models.server import Server


class NotAllServersCreatedException(Exception):
    def __init__(
        self,
        already_established: List[Server],
        internal_exps: List[VScaleClientAPICreateException],
    ) -> None:
        self.already_established = already_established
        self.content = {
            internal_exp.name: {
                "code": internal_exp.code,
                "message": internal_exp.message,
            }
            for internal_exp in internal_exps
        }
        super(NotAllServersCreatedException, self).__init__()


class NotAllServersDeleteException(Exception):
    def __init__(
        self,
        already_deleted: List[Server],
        internal_exps: List[VScaleDeleteServerException],
    ) -> None:
        self.already_deleted = already_deleted
        self.internal_exps = internal_exps
        super(NotAllServersDeleteException, self).__init__()


class VScaleDeleteServerException(Exception):
    def __init__(self, server: Server):
        self.server = server
        super(VScaleDeleteServerException, self).__init__()


class VScaleClientAPIException(Exception):
    def __init__(self) -> None:
        self.code = ""
        self.message = ""
        super(VScaleClientAPIException, self).__init__()


class VScaleClientAPICreateException(VScaleClientAPIException):
    def __init__(self, name: str) -> None:
        self.name = name
        self.code = ""
        self.message = ""
        super(VScaleClientAPICreateException, self).__init__()


class VScaleClientAPIDeleteException(VScaleClientAPIException):
    def __init__(self, ctid: int) -> None:
        self.ctid = ctid
        super(VScaleClientAPIDeleteException, self).__init__()


class TooManyRequestsException(VScaleClientAPICreateException):
    def __init__(self, name: str) -> None:
        super(TooManyRequestsException, self).__init__(name)
        self.code = "TOO_MANY_REQUESTS"
        self.message = "Превышена максимальная частота запросов"


class NoObjectToCreateFromException(VScaleClientAPICreateException):
    def __init__(self, name: str) -> None:
        super(NoObjectToCreateFromException, self).__init__(name)
        self.code = "NO_OBJECT_TO_CREATE_FROM"
        self.message = "Указан несуществующий образ для создания сервера"


class NoLocationFoundException(VScaleClientAPICreateException):
    def __init__(self, name: str) -> None:
        super(NoLocationFoundException, self).__init__(name)
        self.code = "NO_LOCATION_FOUND"
        self.message = "Указан несуществующий дата-центр"


class NoRplanFoundException(VScaleClientAPICreateException):
    def __init__(self, name: str) -> None:
        super(NoRplanFoundException, self).__init__(name)
        self.code = "NO_RPLAN_FOUND"
        self.message = "Указана несуществующая конфигурация"


class UnexpectedException(VScaleClientAPICreateException):
    def __init__(self, name: str) -> None:
        super(UnexpectedException, self).__init__(name)
        self.code = "UNEXPECTED_ERROR"
        self.message = "Непредвиденная ошибка"
