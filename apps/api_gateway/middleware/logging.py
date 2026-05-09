from time import perf_counter
from fastapi import Request
from shared.utils.logging import get_logger

logger = get_logger(__name__)

async def log_requests(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    elapsed_ms = (perf_counter() - start) * 1000
    logger.info("%s %s -> %s in %.1fms", request.method, request.url.path, response.status_code, elapsed_ms)
    return response
