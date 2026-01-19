"""MCPContext model."""

from typing import Optional

from pydantic import BaseModel


class MCPContext(BaseModel):
    """Context information for MCP execution."""

    trace_id: Optional[str] = None
    headers: dict[str, str] = {}
