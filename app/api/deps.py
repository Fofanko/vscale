from typing import AsyncGenerator

from app.core.config import settings
from app.db.session import async_session
from app.vscale.adapter import VScaleAdapter
from app.vscale.client import VScaleAPIClient


async def get_db() -> AsyncGenerator:
    """
    Зависимость для сесси к бд
    """
    try:
        db = async_session()
        yield db
    finally:
        await db.close()


def get_vscale_adapter() -> VScaleAdapter:
    """
    Зависимость для адаптера к vscale
    """
    return VScaleAdapter(
        client=VScaleAPIClient(settings.VSCALE_TOKEN, settings.VSCALE_URL)
    )
