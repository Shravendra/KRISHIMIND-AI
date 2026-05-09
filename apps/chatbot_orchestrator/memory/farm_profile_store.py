from __future__ import annotations
from typing import Dict, Any

class FarmProfileStore:
    def __init__(self):
        self._profiles: Dict[str, Dict[str, Any]] = {}

    def upsert(self, farmer_id: str, profile: Dict[str, Any]) -> None:
        self._profiles[farmer_id] = {**self._profiles.get(farmer_id, {}), **profile}

    def get(self, farmer_id: str) -> Dict[str, Any]:
        return self._profiles.get(farmer_id, {})
