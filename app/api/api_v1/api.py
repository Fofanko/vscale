from fastapi import APIRouter

from app.api.api_v1.endpoints import server

api_router = APIRouter()

api_router.include_router(server.router, prefix="/servers", tags=["servers"])
