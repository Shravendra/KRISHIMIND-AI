"""
apps/api_gateway/middleware/logging.py
──────────────────────────────────────
Request/response logging middleware.
"""

from time import perf_counter

from fastapi import Request

from shared.utils.logging import get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next):

    start_time = perf_counter()

    response = await call_next(request)

    process_time = (perf_counter() - start_time) * 1000

    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    return response