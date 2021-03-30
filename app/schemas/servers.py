from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ServerIn(BaseModel):
    location: str
    rplan: str
    name: str
    make_from: str
    keys: Optional[List[int]]
    password: Optional[str] = None


class Key(BaseModel):
    id: int
    external_id: int
    name: str

    class Config:
        orm_mode = True


class Server(BaseModel):
    id: int
    status: str
    deleted: Optional[datetime]
    active: bool
    location: str
    locked: bool
    hostname: str
    created: datetime
    made_from: str
    name: str
    ext_ctid: int
    rplan: str
    keys: List[Key]

    public_address_gateway: str
    public_address_netmask: str
    public_address_address: str

    private_address_gateway: str
    private_address_netmask: str
    private_address_address: str

    class Config:
        orm_mode = True
