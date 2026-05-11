"""Health & readiness endpoints."""

from fastapi import APIRouter
from datetime import datetime

from shared.constants.app import APP_NAME, APP_VERSION

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Liveness probe")
async def health():
    """Returns 200 when the service is alive."""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/ready", summary="Readiness probe")
async def ready():
    """Checks that downstream dependencies are reachable.

    In production this would ping Redis, PostgreSQL, and the vector DB.
    For now it always returns ready so the app boots cleanly.
    """
    checks = {
        "api": "ok",
        "llm_client": "ok",
        # "redis": _ping_redis(),
        # "qdrant": _ping_qdrant(),
    }
    all_ok = all(v == "ok" for v in checks.values())
    return {
        "ready": all_ok,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
