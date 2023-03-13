import asyncio
from typing import Any, Coroutine

from aiolimiter import AsyncLimiter
from tqdm.asyncio import tqdm_asyncio  # type: ignore


async def ratelimited_gather(num: int, coros: Coroutine[Any, Any, Any]) -> list[Any]:
    """Based on the `AsyncLimiter` value, It will run co-routines asyncroniously.

    Parameters
    ----------
    num : int
        Async limiter value.
    coros : Coroutine[Any, Any, Any]
        List of co-routines

    Returns
    -------
    list[Any]
        Returns co-routine response.
    """
    limiter = AsyncLimiter(num, 1)

    async def _wrap_coro(coro: Coroutine[Any, Any, Any]):
        async with limiter:
            return await coro

    return await tqdm_asyncio.gather(  # type: ignore
        *(_wrap_coro(coro) for coro in coros)  # type: ignore
    )


def raise_exception(exception: Exception):
    raise exception
