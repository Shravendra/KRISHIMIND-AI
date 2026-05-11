"""Farm profile store — persists per-user farm context between sessions.

Backed by Redis (with in-process fallback for dev).
"""

import json
import os
from typing import Dict, Any, Optional

from shared.utils.logging import get_logger
from shared.constants.app import REDIS_FARM_PROFILE_PREFIX

logger = get_logger("memory.farm_profile_store")

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_local_profiles: Dict[str, Dict] = {}

try:
    import redis.asyncio as aioredis
    _redis = aioredis.from_url(_REDIS_URL, decode_responses=True)
    _use_redis = True
except Exception:
    _redis = None  # type: ignore
    _use_redis = False


DEFAULT_PROFILE = {
    "farm_size_acres": None,
    "location": None,
    "state": None,
    "district": None,
    "primary_crops": [],
    "soil_type": None,
    "irrigation_type": "rainfed",
    "farming_type": "conventional",
    "livestock": [],
    "preferred_language": "en",
}


class FarmProfileStore:
    """CRUD operations for per-user farm profiles."""

    def _key(self, user_id: str) -> str:
        return f"{REDIS_FARM_PROFILE_PREFIX}{user_id}"

    async def get(self, user_id: str) -> Dict[str, Any]:
        """Return the farm profile for `user_id`, or sensible defaults."""
        if _use_redis:
            try:
                raw = await _redis.get(self._key(user_id))
                if raw:
                    return {**DEFAULT_PROFILE, **json.loads(raw)}
            except Exception as exc:
                logger.warning("farm_profile_get_error", extra={"error": str(exc)})

        stored = _local_profiles.get(self._key(user_id), {})
        return {**DEFAULT_PROFILE, **stored}

    async def update(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge `updates` into the existing profile and persist."""
        current = await self.get(user_id)
        merged = {**current, **updates}

        if _use_redis:
            try:
                await _redis.set(self._key(user_id), json.dumps(merged))
                return merged
            except Exception as exc:
                logger.warning("farm_profile_update_error", extra={"error": str(exc)})

        _local_profiles[self._key(user_id)] = merged
        return merged

    async def delete(self, user_id: str) -> None:
        """Remove a user's farm profile."""
        if _use_redis:
            try:
                await _redis.delete(self._key(user_id))
                return
            except Exception as exc:
                logger.warning("farm_profile_delete_error", extra={"error": str(exc)})

        _local_profiles.pop(self._key(user_id), None)
