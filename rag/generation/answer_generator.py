from __future__ import annotations
from typing import List, Dict, Any

def generate_answer(query: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
    snippets = [c["content"] for c in contexts]
    if snippets:
        answer = "Based on the knowledge base, the best guidance is: " + " ".join(snippets[:2])
    else:
        answer = "I could not find a strong match in the knowledge base, so please share more details."
    return {
        "answer": answer,
        "citations": snippets[:3],
        "confidence": 0.72 if snippets else 0.40,
    }
