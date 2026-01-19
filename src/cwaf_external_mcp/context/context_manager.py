"""Context manager for handling MCPContext using contextvars."""

from contextvars import ContextVar, Token
from typing import Dict

from cwaf_external_mcp.context.mcp_context import MCPContext


class ContextManager:
    """Manages MCPContext using context variables."""

    def __init__(self):
        self.current_context: ContextVar[MCPContext] = ContextVar(
            "current_context", default=MCPContext()
        )

    def set_current_context(self, context: MCPContext) -> Token:
        """Set the current MCPContext and return a token for resetting."""
        return self.current_context.set(context)

    def get_current_context(self) -> MCPContext:
        """Get the current MCPContext."""
        return self.current_context.get()

    def reset_token(self, token: Token) -> None:
        """Reset the current context to a previous state using the provided token."""
        return self.current_context.reset(token)

    def set_current_trace_id(self, trace_id: str) -> Token:
        """Set the current trace ID in the context."""
        context = MCPContext()
        context.trace_id = trace_id
        context.headers = self.get_current_context().headers
        return self.set_current_context(context)

    def get_current_trace_id(self) -> str:
        """Get the current trace ID from the context."""
        return self.get_current_context().trace_id

    def set_headers(self, headers: Dict[str, str]) -> Token:
        """Set the headers in the current context."""
        context = MCPContext()
        context.headers = headers
        context.trace_id = self.get_current_context().trace_id
        return self.set_current_context(context)

    def get_headers(self) -> Dict[str, str]:
        """Get the headers from the current context."""
        return self.get_current_context().headers


context_manager = ContextManager()
