import ipaddress
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, validator


class Address(BaseModel):
    gateway: Optional[ipaddress.IPv4Address]
    netmask: Optional[str]
    address: Optional[ipaddress.IPv4Address]


class Key(BaseModel):
    name: str
    id: int


class Server(BaseModel):
    public_address: Address
    private_address: Address
    keys: List[Key]
    status: str
    active: bool
    location: str
    locked: bool
    hostname: str
    rplan: str
    name: str
    made_from: str
    ctid: int


class ServerCreationRequest(BaseModel):
    location: str
    rplan: str
    name: str
    make_from: str
    do_start: bool
    keys: Optional[List[str]]
    password: Optional[str] = None


class ServerCreationResponse(Server):
    created: datetime
    deleted: Optional[datetime]

    @validator("created", pre=True)
    def parse_created(cls, v: Union[str, datetime]) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v, "%d.%m.%Y %H:%M:%S")
        return v


class ServerDeleteResponse(Server):
    pass
