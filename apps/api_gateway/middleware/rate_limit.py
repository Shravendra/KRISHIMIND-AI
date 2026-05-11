"""Token-bucket rate-limiting middleware (in-memory, Redis-ready)."""

import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from shared.utils.logging import get_logger

logger = get_logger("api.rate_limit")

# ── Simple in-process sliding-window counter ────────────────────────────────
# Structure: { ip: [(timestamp, count), ...] }
_windows: dict[str, list] = defaultdict(list)

WINDOW_SECONDS = 60          # 1-minute rolling window
MAX_REQUESTS_PER_WINDOW = 60  # 60 req / min per IP (generous for dev)
CHAT_MAX_REQUESTS = 20        # tighter limit on the chat endpoint


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter.

    Applies a per-IP limit; the /chat endpoint gets a stricter sub-limit.
    In production swap the in-memory store for Redis INCR + EXPIRE.
    """

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Determine applicable limit
        limit = CHAT_MAX_REQUESTS if "/chat" in path else MAX_REQUESTS_PER_WINDOW

        now = time.time()
        cutoff = now - WINDOW_SECONDS

        # Prune old entries
        _windows[client_ip] = [t for t in _windows[client_ip] if t > cutoff]

        if len(_windows[client_ip]) >= limit:
            logger.warning(
                "rate_limit_exceeded",
                extra={"event": "rate_limit_exceeded", "client_ip": client_ip, "path": path},
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please slow down.",
                    "retry_after_seconds": WINDOW_SECONDS,
                },
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        _windows[client_ip].append(now)

        response = await call_next(request)
        remaining = max(0, limit - len(_windows[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(WINDOW_SECONDS)
        return response


# Convenience alias
rate_limit_middleware = RateLimitMiddleware
