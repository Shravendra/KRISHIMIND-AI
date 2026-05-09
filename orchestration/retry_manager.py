from __future__ import annotations
import asyncio
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")

async def with_retry(factory: Callable[[], Awaitable[T]], retries: int = 2, delay_s: float = 0.5) -> T:
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return await factory()
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                await asyncio.sleep(delay_s)
    raise last_exc
