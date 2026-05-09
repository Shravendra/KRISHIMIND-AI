from __future__ import annotations
from typing import Any, Dict, List

class SimpleRetriever:
    def __init__(self, documents: List[str] | None = None):
        self.documents = documents or [
            "FAO recommends integrated pest management and timely scouting.",
            "Crop disease control works best when symptoms are confirmed before spraying.",
            "Good irrigation timing reduces heat and drought stress.",
            "Soil pH and nutrient balance strongly affect yield.",
        ]

    def retrieve(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        q = set(query.lower().split())
        scored = []
        for doc in self.documents:
            d = set(doc.lower().split())
            score = len(q & d) / max(1, len(q | d))
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"content": doc, "score": score} for score, doc in scored[:k] if score > 0]
