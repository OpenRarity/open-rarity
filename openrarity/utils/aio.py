import asyncio
from typing import Any, Coroutine

from aiolimiter import AsyncLimiter
from tqdm.asyncio import tqdm_asyncio  # type: ignore


async def ratelimited_gather(num: int, coros: Coroutine[Any, Any, Any]) -> list[Any]:
    """
    Runs all coroutines and using a leaky bucket strategy to limit the speed of submission. The rate is configured by the `num` parameter.

    Parameters
    ----------
    num : int
        The rate limit of coroutines per second to submit.
    coros : Coroutine[Any, Any, Any]
        List of coroutines.

    Returns
    -------
    list[Any]
        List of return values from the provided coroutines.
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
