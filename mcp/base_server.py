from __future__ import annotations
from fastapi import FastAPI

def create_mcp_app(title: str = "MCP Server") -> FastAPI:
    return FastAPI(title=title)
