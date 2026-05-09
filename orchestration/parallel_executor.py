from __future__ import annotations
import asyncio
from typing import Awaitable, Iterable, List, TypeVar

T = TypeVar("T")

async def run_parallel(tasks: Iterable[Awaitable[T]]) -> List[T]:
    return await asyncio.gather(*tasks)
