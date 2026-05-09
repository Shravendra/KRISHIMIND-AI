from __future__ import annotations
from typing import Dict, List

def extract_image_signals(image_inputs: List[Dict[str, str]]) -> List[str]:
    signals = []
    for item in image_inputs:
        value = (item.get("url") or item.get("path") or "").lower()
        if any(k in value for k in ["spot", "blight", "rust", "leaf", "yellow"]):
            signals.append("possible_leaf_issue")
        if any(k in value for k in ["dry", "curl", "wilt"]):
            signals.append("water_stress")
    return list(dict.fromkeys(signals))
