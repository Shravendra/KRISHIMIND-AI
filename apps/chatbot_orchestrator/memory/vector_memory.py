from __future__ import annotations
from typing import List, Dict

class VectorMemory:
    """Minimal local fallback. Replace with Qdrant/Weaviate in production."""
    def __init__(self):
        self._items: List[Dict[str, str]] = []

    def add(self, text: str, metadata: Dict[str, str] | None = None) -> None:
        self._items.append({"text": text, "metadata": metadata or {}})

    def search(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        q = set(query.lower().split())
        scored = []
        for item in self._items:
            t = set(item["text"].lower().split())
            score = len(q & t) / max(1, len(q | t))
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored[:k] if score > 0]
