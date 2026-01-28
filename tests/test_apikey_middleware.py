# Copyright Thales 2026
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest
from unittest import mock

from cwaf_external_mcp.auth.apikey_middleware import APIKeyMiddleware


@pytest.mark.asyncio
async def test_apikey_middleware_initialization():
    """Test APIKeyMiddleware initialization with api_id and api_key."""
    api_id = 12345
    api_key = "test_api_key_123"

    middleware = APIKeyMiddleware(api_id, api_key)

    assert middleware.api_id == api_id
    assert middleware.api_key == api_key


@pytest.mark.asyncio
async def test_on_message_with_tools_call_method(monkeypatch):
    """Test on_message sets headers when method is 'tools/call'."""
    api_id = 12345
    api_key = "test_api_key_123"

    middleware = APIKeyMiddleware(api_id, api_key)

    # Mock the context
    mock_context = mock.Mock()
    mock_context.method = "tools/call"

    # Mock call_next
    expected_result = "call_next_result"
    mock_call_next = mock.AsyncMock(return_value=expected_result)

    # Mock context_manager
    mock_context_manager = mock.Mock()

    with mock.patch(
        "cwaf_external_mcp.auth.apikey_middleware.context_manager",
        mock_context_manager,
    ):
        result = await middleware.on_message(mock_context, mock_call_next)

    # Verify headers were set
    mock_context_manager.set_headers.assert_called_once_with(
        {
            "x-api-id": str(api_id),
            "x-api-key": api_key,
        }
    )

    # Verify call_next was called
    mock_call_next.assert_called_once_with(mock_context)

    # Verify result is returned from call_next
    assert result == expected_result


@pytest.mark.asyncio
async def test_on_message_with_non_tools_call_method(monkeypatch):
    """Test on_message does not set headers when method is not 'tools/call'."""
    api_id = 12345
    api_key = "test_api_key_123"

    middleware = APIKeyMiddleware(api_id, api_key)

    # Mock the context with a different method
    mock_context = mock.Mock()
    mock_context.method = "other/method"

    # Mock call_next
    expected_result = "call_next_result"
    mock_call_next = mock.AsyncMock(return_value=expected_result)

    # Mock context_manager
    mock_context_manager = mock.Mock()

    with mock.patch(
        "cwaf_external_mcp.auth.apikey_middleware.context_manager",
        mock_context_manager,
    ):
        result = await middleware.on_message(mock_context, mock_call_next)

    # Verify headers were NOT set
    mock_context_manager.set_headers.assert_not_called()

    # Verify call_next was called
    mock_call_next.assert_called_once_with(mock_context)

    # Verify result is returned from call_next
    assert result == expected_result


@pytest.mark.asyncio
async def test_on_message_passes_exceptions():
    """Test on_message propagates exceptions from call_next."""
    api_id = 12345
    api_key = "test_api_key_123"

    middleware = APIKeyMiddleware(api_id, api_key)

    # Mock the context
    mock_context = mock.Mock()
    mock_context.method = "tools/call"

    # Mock call_next to raise an exception
    test_exception = ValueError("Test exception")
    mock_call_next = mock.AsyncMock(side_effect=test_exception)

    # Mock context_manager
    mock_context_manager = mock.Mock()

    with mock.patch(
        "cwaf_external_mcp.auth.apikey_middleware.context_manager",
        mock_context_manager,
    ):
        with pytest.raises(ValueError) as exc_info:
            await middleware.on_message(mock_context, mock_call_next)

    assert exc_info.value == test_exception


@pytest.mark.asyncio
async def test_on_message_converts_api_id_to_string():
    """Test on_message converts api_id to string in headers."""
    api_id = 99999
    api_key = "test_key"

    middleware = APIKeyMiddleware(api_id, api_key)

    # Mock the context
    mock_context = mock.Mock()
    mock_context.method = "tools/call"

    # Mock call_next
    mock_call_next = mock.AsyncMock(return_value=None)

    # Mock context_manager and capture the call
    mock_context_manager = mock.Mock()

    with mock.patch(
        "cwaf_external_mcp.auth.apikey_middleware.context_manager",
        mock_context_manager,
    ):
        await middleware.on_message(mock_context, mock_call_next)

    # Verify the api_id was converted to string
    call_args = mock_context_manager.set_headers.call_args[0][0]
    assert isinstance(call_args["x-api-id"], str)
    assert call_args["x-api-id"] == "99999"
    assert call_args["x-api-key"] == api_key
