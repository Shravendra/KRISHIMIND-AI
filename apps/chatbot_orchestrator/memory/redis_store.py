from __future__ import annotations
from typing import Any, Dict, List
from collections import defaultdict

try:
    import redis.asyncio as redis
except Exception:
    redis = None

class RedisStore:
    def __init__(self, url: str | None = None):
        self.url = url
        self._fallback: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._client = None

    async def connect(self) -> None:
        if redis and self.url:
            self._client = redis.from_url(self.url, decode_responses=True)

    async def append_message(self, conversation_id: str, payload: Dict[str, Any]) -> None:
        if self._client:
            await self._client.rpush(conversation_id, str(payload))
        else:
            self._fallback[conversation_id].append(payload)

    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        if self._client:
            values = await self._client.lrange(conversation_id, 0, -1)
            return [{"raw": v} for v in values]
        return self._fallback.get(conversation_id, [])
