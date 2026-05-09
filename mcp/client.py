from __future__ import annotations
from typing import Any
from mcp.tool_registry import registry

class MCPClient:
    async def call_tool(self, name: str, **kwargs) -> Any:
        return registry.call(name, **kwargs)
