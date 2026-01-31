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
from starlette.requests import Request
from starlette.datastructures import Headers


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv("API_ID", "123")
    monkeypatch.setenv("API_KEY", "abc")
    monkeypatch.setenv("PROMETHEUS_CLIENT_ENABLED", "false")
    monkeypatch.setenv("STDIO", "true")


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test the health check endpoint returns OK."""
    from cwaf_external_mcp.server import health_check

    # Create a mock request
    mock_request = mock.Mock(spec=Request)
    mock_request.headers = Headers()

    response = await health_check(mock_request)

    assert response.body == b"OK"
    assert response.status_code == 200


def test_server_module_loads_correctly():
    """Test that server module loads and has expected attributes."""
    import cwaf_external_mcp.server as server_module

    # Verify the module has the expected FastMCP instance
    assert hasattr(server_module, "cwaf_mcp")
    assert hasattr(server_module, "main")
    assert hasattr(server_module, "health_check")
    # Verify tool functions exist (they're wrapped by FastMCP)
    assert hasattr(server_module, "get_rules_of_account_tool")
    assert hasattr(server_module, "get_polices_of_account_by_filter_tool")
    assert hasattr(server_module, "get_domains_by_filters_tool")
    assert hasattr(server_module, "get_sites_details_of_a_given_account_tool")


def test_server_port_constant():
    """Test SERVER_PORT constant is set correctly."""
    import cwaf_external_mcp.server as server_module

    # Should be 8050 from the env fixture or default
    assert server_module.SERVER_PORT == 8050


def test_main_with_stdio(monkeypatch):
    """Test main function with stdio transport."""
    monkeypatch.setenv("STDIO", "true")
    monkeypatch.setenv("PROMETHEUS_CLIENT_ENABLED", "false")

    with mock.patch("cwaf_external_mcp.server.cwaf_mcp") as mock_mcp:
        with mock.patch(
            "cwaf_external_mcp.server.create_auth_from_config"
        ) as mock_auth:
            mock_auth_instance = mock.Mock()
            mock_auth_instance.get_middlewares.return_value = []
            mock_auth.return_value = mock_auth_instance

            from cwaf_external_mcp.server import main

            main()

            mock_mcp.run.assert_called_once_with(transport="stdio")


def test_main_with_http_transport(monkeypatch):
    """Test main function with HTTP transport."""
    monkeypatch.setenv("STDIO", "false")
    monkeypatch.setenv("PROMETHEUS_CLIENT_ENABLED", "false")
    monkeypatch.setenv("SERVER_PORT", "8050")
    monkeypatch.setenv("BASE_PATH", "/mcp")

    with mock.patch("cwaf_external_mcp.server.cwaf_mcp") as mock_mcp:
        with mock.patch(
            "cwaf_external_mcp.server.create_auth_from_config"
        ) as mock_auth:
            mock_auth_instance = mock.Mock()
            mock_auth_instance.get_middlewares.return_value = []
            mock_auth.return_value = mock_auth_instance

            from cwaf_external_mcp.server import main

            main()

            mock_mcp.run.assert_called_once()
            call_kwargs = mock_mcp.run.call_args[1]
            assert call_kwargs["transport"] == "streamable-http"
            assert call_kwargs["host"] == "0.0.0.0"
            assert call_kwargs["port"] == 8050
