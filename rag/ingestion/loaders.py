from __future__ import annotations
from pathlib import Path
from typing import List

def load_text_files(folder: str) -> List[str]:
    base = Path(folder)
    docs = []
    for path in base.rglob("*.txt"):
        docs.append(path.read_text(encoding="utf-8"))
    return docs
