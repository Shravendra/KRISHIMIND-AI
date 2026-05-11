"""Vector memory — stores conversation embeddings for semantic recall.

In production this talks to Qdrant. In dev/test it falls back to a simple
cosine-similarity search over an in-process list.
"""

import os
import json
import math
from typing import List, Dict, Any, Optional
from datetime import datetime

from shared.utils.logging import get_logger

logger = get_logger("memory.vector_memory")

_QDRANT_URL     = os.getenv("QDRANT_URL", "http://localhost:6333")
_QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
_COLLECTION     = "krishimind_conversations"
_EMBED_DIM      = 1536  # text-embedding-ada-002 / text-embedding-3-small

# ── Lightweight in-process fallback ─────────────────────────────────────────
_local_vectors: List[Dict] = []  # [{"id", "vector", "payload"}, ...]

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    _qdrant = AsyncQdrantClient(url=_QDRANT_URL, api_key=_QDRANT_API_KEY or None)
    _use_qdrant = True
    logger.info("qdrant_connected", extra={"url": _QDRANT_URL})
except Exception as exc:
    _qdrant = None  # type: ignore
    _use_qdrant = False
    logger.warning("qdrant_unavailable_fallback", extra={"error": str(exc)})


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb + 1e-9)


async def _embed(text: str) -> List[float]:
    """Generate an embedding vector for `text`.

    Uses OpenAI embeddings when available; falls back to a deterministic
    hash-based pseudo-embedding for offline/test environments.
    """
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        resp = await client.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding
    except Exception:
        # Deterministic pseudo-embedding — NOT semantically meaningful,
        # only here so the rest of the pipeline doesn't crash offline.
        h = hash(text)
        import random
        rng = random.Random(h)
        return [rng.gauss(0, 1) for _ in range(_EMBED_DIM)]


class VectorMemory:
    """Stores and retrieves semantically similar past conversation snippets."""

    async def store(self, session_id: str, user_message: str, assistant_response: str) -> None:
        """Embed and store a user↔assistant exchange."""
        combined = f"User: {user_message}\nAssistant: {assistant_response}"
        vector = await _embed(combined)

        payload = {
            "session_id": session_id,
            "user_message": user_message,
            "assistant_response": assistant_response[:500],  # truncate for storage
            "stored_at": datetime.utcnow().isoformat(),
        }

        if _use_qdrant:
            try:
                from qdrant_client.models import PointStruct
                import uuid
                point = PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload)
                await _qdrant.upsert(collection_name=_COLLECTION, points=[point])
                return
            except Exception as exc:
                logger.warning("qdrant_store_error", extra={"error": str(exc)})

        _local_vectors.append({"vector": vector, "payload": payload})

    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Return the `top_k` most semantically relevant past exchanges."""
        query_vec = await _embed(query)

        if _use_qdrant:
            try:
                results = await _qdrant.search(
                    collection_name=_COLLECTION,
                    query_vector=query_vec,
                    limit=top_k,
                )
                return [r.payload for r in results]
            except Exception as exc:
                logger.warning("qdrant_search_error", extra={"error": str(exc)})

        # In-process fallback
        scored = [
            (_cosine(query_vec, item["vector"]), item["payload"])
            for item in _local_vectors
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:top_k]]
