from typing import List

import pytest

from app.utils.helper import do_with_retry


@pytest.mark.asyncio
async def test_retry() -> None:
    mas: List[bool] = []

    retry_count = 3

    @do_with_retry(Exception, 0, retry_count)
    async def increment(_mas: List) -> None:
        _mas.append(True)
        raise Exception

    try:
        await increment(mas)
    except Exception:
        pass
    finally:
        assert len(mas) == retry_count
