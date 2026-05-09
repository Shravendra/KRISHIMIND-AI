from __future__ import annotations

def verify_mcp_token(token: str | None) -> bool:
    return bool(token and len(token) > 10)
