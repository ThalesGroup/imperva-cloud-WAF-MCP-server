# tests/test_context_manager.py
import pytest
from contextvars import Token

from cwaf_external_mcp.context.context_manager import ContextManager, context_manager
from cwaf_external_mcp.context.mcp_context import MCPContext


def test_context_manager_initialization():
    """Test ContextManager initializes with default MCPContext."""
    cm = ContextManager()

    context = cm.get_current_context()
    assert isinstance(context, MCPContext)
    assert context.trace_id is None
    assert context.headers == {}


def test_set_and_get_current_context():
    """Test setting and getting current context."""
    cm = ContextManager()

    new_context = MCPContext(trace_id="test_trace_123", headers={"key": "value"})
    token = cm.set_current_context(new_context)

    assert isinstance(token, Token)

    retrieved_context = cm.get_current_context()
    assert retrieved_context.trace_id == "test_trace_123"
    assert retrieved_context.headers == {"key": "value"}


def test_reset_token():
    """Test reset_token restores previous context."""
    cm = ContextManager()

    # Get initial context
    initial_context = cm.get_current_context()
    initial_trace_id = initial_context.trace_id

    # Set new context
    new_context = MCPContext(trace_id="new_trace", headers={"new": "header"})
    token = cm.set_current_context(new_context)

    # Verify new context is set
    assert cm.get_current_context().trace_id == "new_trace"

    # Reset to previous context
    cm.reset_token(token)

    # Verify context is reset
    restored_context = cm.get_current_context()
    assert restored_context.trace_id == initial_trace_id


def test_set_and_get_current_trace_id():
    """Test setting and getting trace_id."""
    cm = ContextManager()

    token = cm.set_current_trace_id("trace_456")

    assert isinstance(token, Token)
    assert cm.get_current_trace_id() == "trace_456"


def test_set_and_get_headers():
    """Test setting and getting headers."""
    cm = ContextManager()

    headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}
    token = cm.set_headers(headers)

    assert isinstance(token, Token)

    retrieved_headers = cm.get_headers()
    assert retrieved_headers == headers
    assert retrieved_headers["Authorization"] == "Bearer token"
    assert retrieved_headers["Content-Type"] == "application/json"


def test_set_trace_id_preserves_headers():
    """Test setting trace_id preserves existing headers."""
    cm = ContextManager()

    # Set initial headers
    initial_headers = {"key1": "value1"}
    cm.set_headers(initial_headers)

    # Set trace_id
    cm.set_current_trace_id("trace_789")

    # Verify headers are preserved
    assert cm.get_headers() == initial_headers
    assert cm.get_current_trace_id() == "trace_789"


def test_set_headers_preserves_trace_id():
    """Test setting headers preserves existing trace_id."""
    cm = ContextManager()

    # Set initial trace_id
    cm.set_current_trace_id("trace_abc")

    # Set headers
    new_headers = {"key2": "value2"}
    cm.set_headers(new_headers)

    # Verify trace_id is preserved
    assert cm.get_current_trace_id() == "trace_abc"
    assert cm.get_headers() == new_headers


def test_multiple_context_updates():
    """Test multiple updates to context."""
    cm = ContextManager()

    # First update
    cm.set_current_trace_id("trace1")
    cm.set_headers({"header1": "value1"})

    assert cm.get_current_trace_id() == "trace1"
    assert cm.get_headers() == {"header1": "value1"}

    # Second update
    cm.set_current_trace_id("trace2")
    assert cm.get_current_trace_id() == "trace2"

    # Third update
    cm.set_headers({"header2": "value2"})
    assert cm.get_headers() == {"header2": "value2"}
    assert cm.get_current_trace_id() == "trace2"


def test_context_isolation_with_tokens():
    """Test that tokens properly isolate context changes."""
    cm = ContextManager()

    # Set initial state
    cm.set_current_trace_id("initial")

    # Create nested context
    token1 = cm.set_current_trace_id("nested1")
    assert cm.get_current_trace_id() == "nested1"

    # Create another nested context
    token2 = cm.set_current_trace_id("nested2")
    assert cm.get_current_trace_id() == "nested2"

    # Reset to nested1
    cm.reset_token(token2)
    assert cm.get_current_trace_id() == "nested1"

    # Reset to initial
    cm.reset_token(token1)
    assert cm.get_current_trace_id() == "initial"


def test_empty_headers_update():
    """Test setting empty headers."""
    cm = ContextManager()

    # Set some headers first
    cm.set_headers({"key": "value"})
    assert cm.get_headers() == {"key": "value"}

    # Set empty headers
    cm.set_headers({})
    assert cm.get_headers() == {}


def test_none_trace_id():
    """Test setting None as trace_id."""
    cm = ContextManager()

    # Set a trace_id first
    cm.set_current_trace_id("some_trace")
    assert cm.get_current_trace_id() == "some_trace"

    # Set None trace_id
    cm.set_current_trace_id(None)
    assert cm.get_current_trace_id() is None


def test_global_context_manager_instance():
    """Test that global context_manager instance is properly initialized."""
    # Verify the global instance exists and is a ContextManager
    assert isinstance(context_manager, ContextManager)

    # Verify it works as expected
    context_manager.set_current_trace_id("global_trace")
    assert context_manager.get_current_trace_id() == "global_trace"


def test_context_manager_with_complex_headers():
    """Test context manager with various header formats."""
    cm = ContextManager()

    complex_headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "Content-Type": "application/json",
        "X-Custom-Header": "custom-value",
        "Accept": "application/json, text/plain, */*",
    }

    cm.set_headers(complex_headers)

    retrieved_headers = cm.get_headers()
    assert retrieved_headers == complex_headers
    assert len(retrieved_headers) == 4


def test_context_is_mutable_through_reference():
    """Test that modifying context through reference updates the stored context."""
    cm = ContextManager()

    # Note: This test verifies current behavior where the context
    # is mutable through direct reference
    context = cm.get_current_context()
    original_trace_id = context.trace_id

    # Directly modifying the returned context
    context.trace_id = "modified_trace"

    # Get context again - the exact behavior depends on implementation
    # This test documents the current behavior
    retrieved_context = cm.get_current_context()

    # In the current implementation, if we just get the context and modify it,
    # the change persists because ContextVar returns the same instance
    assert retrieved_context.trace_id == "modified_trace"
