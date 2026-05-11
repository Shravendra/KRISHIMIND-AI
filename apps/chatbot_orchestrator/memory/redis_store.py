"""Redis-backed conversation history store.

Falls back to an in-process dict when Redis is unavailable (dev/test mode).
"""

import json
import os
from typing import List, Dict, Any, Optional

from shared.utils.logging import get_logger
from shared.constants.app import REDIS_CHAT_HISTORY_PREFIX, MAX_CHAT_HISTORY_MESSAGES

logger = get_logger("memory.redis_store")

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# In-process fallback store  { key: [message, ...] }
_local_store: Dict[str, List[Dict]] = {}

try:
    import redis.asyncio as aioredis
    _redis_client = aioredis.from_url(_REDIS_URL, decode_responses=True)
    _use_redis = True
    logger.info("redis_connected", extra={"url": _REDIS_URL})
except Exception as exc:
    _redis_client = None  # type: ignore
    _use_redis = False
    logger.warning("redis_unavailable_fallback", extra={"error": str(exc)})


class RedisStore:
    """Stores and retrieves per-session chat history."""

    def _key(self, session_id: str) -> str:
        return f"{REDIS_CHAT_HISTORY_PREFIX}{session_id}"

    # ── Write ────────────────────────────────────────────────────────────────

    async def append_message(self, session_id: str, role: str, content: str) -> None:
        """Append a single message to the session's history list."""
        message = {"role": role, "content": content}

        if _use_redis:
            try:
                key = self._key(session_id)
                await _redis_client.rpush(key, json.dumps(message))
                # Keep the list bounded
                await _redis_client.ltrim(key, -MAX_CHAT_HISTORY_MESSAGES, -1)
                # 24-hour TTL; reset on each write
                await _redis_client.expire(key, 86_400)
                return
            except Exception as exc:
                logger.warning("redis_write_error", extra={"error": str(exc)})

        # Fallback
        buf = _local_store.setdefault(self._key(session_id), [])
        buf.append(message)
        if len(buf) > MAX_CHAT_HISTORY_MESSAGES:
            _local_store[self._key(session_id)] = buf[-MAX_CHAT_HISTORY_MESSAGES:]

    # ── Read ─────────────────────────────────────────────────────────────────

    async def get_history(self, session_id: str, limit: int = MAX_CHAT_HISTORY_MESSAGES) -> List[Dict[str, Any]]:
        """Return the last `limit` messages for a session."""
        if _use_redis:
            try:
                key = self._key(session_id)
                raw_msgs = await _redis_client.lrange(key, -limit, -1)
                return [json.loads(m) for m in raw_msgs]
            except Exception as exc:
                logger.warning("redis_read_error", extra={"error": str(exc)})

        buf = _local_store.get(self._key(session_id), [])
        return buf[-limit:]

    # ── Delete ───────────────────────────────────────────────────────────────

    async def clear_history(self, session_id: str) -> None:
        """Delete all messages for a session."""
        if _use_redis:
            try:
                await _redis_client.delete(self._key(session_id))
                return
            except Exception as exc:
                logger.warning("redis_delete_error", extra={"error": str(exc)})

        _local_store.pop(self._key(session_id), None)
