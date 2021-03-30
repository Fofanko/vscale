from functools import wraps
from time import sleep
from typing import Type, Callable, Any, Optional


def do_with_retry(
    retry_exc: Type[Exception],
    retry_base_delay_in_second: float = 1,
    retry_count: int = 5,
) -> Callable:
    """
    Декоратор позволяющий выполнять функцию повторно, при выбрасывании ей исключение определенного типа
    :param retry_exc: исключение по которому будет производиться повторное выпролнение функции
    :param retry_base_delay_in_second: задержка между повторными вызовами в секундах
    :param retry_count: количество повторов
    """

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        async def repeater(*args: Any, **kwargs: Any) -> Any:
            delay = retry_base_delay_in_second
            last_exc: Optional[Exception] = None
            for i in range(retry_count):
                try:
                    return await func(*args, **kwargs)
                except retry_exc as ex:
                    last_exc = ex
                    sleep(delay)
                    delay += 1
            else:
                raise last_exc  # type: ignore

        return repeater

    return wrapper
