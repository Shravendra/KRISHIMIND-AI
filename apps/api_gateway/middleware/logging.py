"""
apps/api_gateway/middleware/logging.py
──────────────────────────────────────
Advanced request/response logging middleware for KrishiMind-AI.

Features
────────
• Correlation ID  – generates / forwards X-Request-ID for distributed tracing
• Farmer context  – decodes JWT claims (farmer_id, role) without re-validating
• Route tagging   – classifies paths (agent | chat | auth | health | other)
• Slow-request alerting – WARN when latency exceeds per-route thresholds
• Status-aware log level – INFO / WARNING / ERROR by HTTP status family
• Health-check filtering – skips high-frequency noise endpoints
• Safe query params – strips sensitive keys before logging
• Client IP        – honours X-Forwarded-For (proxy/load-balancer aware)
• Response size    – logs Content-Length when present
• Exception guard  – catches & logs unhandled errors; re-raises for FastAPI
• Context var      – exposes request_id to downstream code via request_id_ctx
"""

from __future__ import annotations

import traceback
import uuid
from contextvars import ContextVar
from time import perf_counter
from typing import Optional

from fastapi import Request, Response
from jose import jwt as jose_jwt
from jose.exceptions import JWTError

from shared.utils.logging import get_logger

logger = get_logger(__name__)

# ── Context variable so any downstream code can read the current request ID ──
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

# ── Tuning knobs ──────────────────────────────────────────────────────────────

# Paths skipped entirely (high-frequency / noise)
_SKIP_PATHS: frozenset[str] = frozenset({
    "/health",
    "/healthz",
    "/readyz",
    "/",
    "/favicon.ico",
})

# Query-string keys whose values are redacted before logging
_SENSITIVE_PARAMS: frozenset[str] = frozenset({
    "token", "api_key", "apikey", "secret", "password", "access_token",
})

# Slow-request thresholds (milliseconds) per route family
_SLOW_THRESHOLDS_MS: dict[str, float] = {
    "agent":  8_000.0,   # AI inference can be slow
    "chat":   6_000.0,
    "auth":     500.0,
    "health":   200.0,
    "other":  2_000.0,
}

# JWT config – read-only decode (no signature verification needed here)
import os
_JWT_SECRET    = os.getenv("SECRET_KEY", "dev-secret-change-in-production-abc123")
_JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _classify_route(path: str) -> str:
    """Map a URL path to a high-level route family tag."""
    if "/agents" in path:
        return "agent"
    if "/chat" in path:
        return "chat"
    if "/auth" in path:
        return "auth"
    if path in _SKIP_PATHS or "/health" in path:
        return "health"
    return "other"


def _safe_query_params(request: Request) -> dict[str, str]:
    """Return query params with sensitive values replaced by [REDACTED]."""
    return {
        k: ("[REDACTED]" if k.lower() in _SENSITIVE_PARAMS else v)
        for k, v in request.query_params.items()
    }


def _extract_client_ip(request: Request) -> str:
    """Resolve the real client IP, respecting X-Forwarded-For."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # The left-most address is the original client
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _extract_farmer_context(request: Request) -> dict[str, Optional[str]]:
    """
    Soft-decode the JWT bearer token to extract farmer_id and role.
    Never raises – returns empty strings on any failure so logging is
    never a source of auth errors.
    """
    context: dict[str, Optional[str]] = {"farmer_id": None, "role": None}
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return context
    token = auth_header[len("Bearer "):]
    try:
        payload = jose_jwt.decode(
            token,
            _JWT_SECRET,
            algorithms=[_JWT_ALGORITHM],
            options={"verify_exp": False},   # logging only, no enforcement
        )
        context["farmer_id"] = payload.get("sub")
        context["role"]      = payload.get("role")
    except JWTError:
        pass
    return context


def _pick_log_level(status_code: int):
    """Return the appropriate logger method for an HTTP status code."""
    if status_code >= 500:
        return logger.error
    if status_code >= 400:
        return logger.warning
    return logger.info


def _response_size(response: Response) -> Optional[int]:
    """Return Content-Length as int, or None if absent / non-numeric."""
    raw = response.headers.get("Content-Length")
    try:
        return int(raw) if raw else None
    except ValueError:
        return None


# ── Middleware entry point ────────────────────────────────────────────────────

async def logging_middleware(request: Request, call_next):
    """
    ASGI middleware that wraps every request with structured, contextual logging.

    Usage (in main.py – already wired):
        app.middleware("http")(logging_middleware)
    """
    path = request.url.path

    # ── 1. Skip noisy infrastructure endpoints ────────────────────────────────
    if path in _SKIP_PATHS:
        return await call_next(request)

    # ── 2. Correlation ID ─────────────────────────────────────────────────────
    request_id = (
        request.headers.get("X-Request-ID")
        or request.headers.get("X-Correlation-ID")
        or str(uuid.uuid4())
    )
    token = request_id_ctx.set(request_id)   # make available downstream

    # ── 3. Collect request metadata ───────────────────────────────────────────
    route_family  = _classify_route(path)
    client_ip     = _extract_client_ip(request)
    farmer_ctx    = _extract_farmer_context(request)
    query_params  = _safe_query_params(request)
    user_agent    = request.headers.get("User-Agent", "")[:200]

    start_time = perf_counter()

    # ── 4. Log the incoming request ───────────────────────────────────────────
    logger.info(
        "request_started",
        extra={
            "event":        "request_started",
            "request_id":   request_id,
            "method":       request.method,
            "path":         path,
            "route_family": route_family,
            "client_ip":    client_ip,
            "user_agent":   user_agent,
            "query_params": query_params,
            **farmer_ctx,
        },
    )

    # ── 5. Call the actual handler ────────────────────────────────────────────
    status_code  = 500
    error_detail: Optional[str] = None
    response: Optional[Response] = None

    try:
        response    = await call_next(request)
        status_code = response.status_code

        # Inject correlation ID into the response so callers can trace it
        response.headers["X-Request-ID"] = request_id

    except Exception as exc:          # pragma: no cover
        error_detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        logger.error(
            "unhandled_exception",
            extra={
                "event":        "unhandled_exception",
                "request_id":   request_id,
                "method":       request.method,
                "path":         path,
                "route_family": route_family,
                "client_ip":    client_ip,
                "exception":    error_detail,
                **farmer_ctx,
            },
        )
        raise

    finally:
        # ── 6. Compute latency & log the completed request ────────────────────
        duration_ms   = (perf_counter() - start_time) * 1000
        slow_threshold = _SLOW_THRESHOLDS_MS.get(route_family, 2_000.0)
        is_slow        = duration_ms > slow_threshold
        resp_size      = _response_size(response) if response else None

        log_fn = _pick_log_level(status_code)
        log_fn(
            "request_finished",
            extra={
                "event":          "request_finished",
                "request_id":     request_id,
                "method":         request.method,
                "path":           path,
                "route_family":   route_family,
                "status_code":    status_code,
                "duration_ms":    round(duration_ms, 2),
                "slow_request":   is_slow,
                "response_bytes": resp_size,
                "client_ip":      client_ip,
                **farmer_ctx,
            },
        )

        # ── 7. Dedicated slow-request warning ────────────────────────────────
        if is_slow:
            logger.warning(
                "slow_request_detected",
                extra={
                    "event":          "slow_request_detected",
                    "request_id":     request_id,
                    "method":         request.method,
                    "path":           path,
                    "route_family":   route_family,
                    "duration_ms":    round(duration_ms, 2),
                    "threshold_ms":   slow_threshold,
                    **farmer_ctx,
                },
            )

        request_id_ctx.reset(token)   # clean up context var

    return response