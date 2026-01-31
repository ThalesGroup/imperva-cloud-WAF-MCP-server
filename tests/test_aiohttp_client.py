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
import aiohttp
import asyncio


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv("API_ID", "123")
    monkeypatch.setenv("API_KEY", "abc")
    monkeypatch.setenv("DISABLE_SSL_VERIFICATION", "false")
    monkeypatch.setenv("CONNECTION_POOL_SIZE", "50")
    monkeypatch.setenv("CONNECTION_POOL_MAX_KEEP_ALIVE", "20")
    monkeypatch.setenv("READ_TIME_OUT", "30.0")
    monkeypatch.setenv("CONNECTION_TIME_OUT", "15.0")
    monkeypatch.setenv("AIOHTTP_DEBUG_MODE_ENABLED", "false")


@pytest.fixture
def event_loop():
    """Create an event loop for each test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_session(event_loop):
    """Reset the global SESSION before each test."""
    import cwaf_external_mcp.httpclient.aiohttp_client as client_module

    client_module.SESSION = None
    yield
    if client_module.SESSION and not client_module.SESSION.closed:
        try:
            event_loop.run_until_complete(client_module.SESSION.close())
        except Exception:
            pass
    client_module.SESSION = None


@pytest.mark.asyncio
async def test_build_session_default_config():
    """Test _build_session creates session with default configuration."""
    from cwaf_external_mcp.httpclient.aiohttp_client import _build_session

    session = _build_session()

    assert isinstance(session, aiohttp.ClientSession)
    assert session.connector.limit == 50
    assert session.connector.limit_per_host == 20
    assert not session.closed
    await session.close()


@pytest.mark.asyncio
async def test_build_session_with_ssl_verification_disabled(monkeypatch):
    """Test _build_session with SSL verification disabled."""
    monkeypatch.setenv("DISABLE_SSL_VERIFICATION", "true")

    from cwaf_external_mcp.httpclient.aiohttp_client import _build_session

    session = _build_session()

    assert isinstance(session, aiohttp.ClientSession)
    assert not session.closed
    await session.close()


@pytest.mark.asyncio
async def test_build_session_with_custom_pool_size(monkeypatch):
    """Test _build_session with custom connection pool size."""
    monkeypatch.setenv("CONNECTION_POOL_SIZE", "100")
    monkeypatch.setenv("CONNECTION_POOL_MAX_KEEP_ALIVE", "30")

    from cwaf_external_mcp.httpclient.aiohttp_client import _build_session

    session = _build_session()

    assert session.connector.limit == 100
    assert session.connector.limit_per_host == 30
    await session.close()


@pytest.mark.asyncio
async def test_build_session_with_debug_mode_enabled(monkeypatch):
    """Test _build_session with aiohttp debug mode enabled."""
    monkeypatch.setenv("AIOHTTP_DEBUG_MODE_ENABLED", "true")

    from cwaf_external_mcp.httpclient.aiohttp_client import _build_session

    session = _build_session()

    assert isinstance(session, aiohttp.ClientSession)
    await session.close()


@pytest.mark.asyncio
async def test_setup_session_creates_new_session():
    """Test setup_session creates a new session."""
    from cwaf_external_mcp.httpclient.aiohttp_client import setup_session, SESSION

    await setup_session()

    import cwaf_external_mcp.httpclient.aiohttp_client as client_module

    assert client_module.SESSION is not None
    assert isinstance(client_module.SESSION, aiohttp.ClientSession)


@pytest.mark.asyncio
async def test_setup_session_reuses_existing_session():
    """Test setup_session reuses existing open session."""
    from cwaf_external_mcp.httpclient.aiohttp_client import setup_session
    import cwaf_external_mcp.httpclient.aiohttp_client as client_module

    await setup_session()
    first_session = client_module.SESSION

    await setup_session()
    second_session = client_module.SESSION

    assert first_session is second_session


@pytest.mark.asyncio
async def test_get_async_client_creates_session_if_none():
    """Test get_async_client creates session if none exists."""
    from cwaf_external_mcp.httpclient.aiohttp_client import get_async_client
    import cwaf_external_mcp.httpclient.aiohttp_client as client_module

    assert client_module.SESSION is None

    client = get_async_client()

    assert isinstance(client, aiohttp.ClientSession)
    assert client_module.SESSION is not None
    await client.close()


@pytest.mark.asyncio
async def test_get_async_client_returns_existing_session():
    """Test get_async_client returns existing session."""
    from cwaf_external_mcp.httpclient.aiohttp_client import get_async_client

    first_client = get_async_client()
    second_client = get_async_client()

    assert first_client is second_client
    await first_client.close()


def test_host_label_with_standard_port():
    """Test _host_label generates correct label for standard port."""
    from cwaf_external_mcp.httpclient.aiohttp_client import _host_label

    mock_key = mock.Mock()
    mock_key.host = "example.com"
    mock_key.port = 443
    mock_key.ssl = True

    label = _host_label(mock_key)

    assert label == "example.com:443"


def test_host_label_with_custom_port():
    """Test _host_label generates correct label for custom port."""
    from cwaf_external_mcp.httpclient.aiohttp_client import _host_label

    mock_key = mock.Mock()
    mock_key.host = "example.com"
    mock_key.port = 8080
    mock_key.ssl = False

    label = _host_label(mock_key)

    assert label == "example.com:8080"


def test_host_label_with_none_port_https():
    """Test _host_label with None port defaults to 443 for SSL."""
    from cwaf_external_mcp.httpclient.aiohttp_client import _host_label

    mock_key = mock.Mock()
    mock_key.host = "example.com"
    mock_key.port = None
    mock_key.ssl = True

    label = _host_label(mock_key)

    assert label == "example.com:443"


def test_host_label_with_none_port_http():
    """Test _host_label with None port defaults to 80 for non-SSL."""
    from cwaf_external_mcp.httpclient.aiohttp_client import _host_label

    mock_key = mock.Mock()
    mock_key.host = "example.com"
    mock_key.port = None
    mock_key.ssl = False

    label = _host_label(mock_key)

    assert label == "example.com:80"


def test_collect_pool_metrics_no_session():
    """Test collect_pool_metrics handles no session gracefully."""
    from cwaf_external_mcp.httpclient.aiohttp_client import collect_pool_metrics
    import cwaf_external_mcp.httpclient.aiohttp_client as client_module

    client_module.SESSION = None

    # Should not raise an exception
    collect_pool_metrics()


@pytest.mark.asyncio
async def test_collect_pool_metrics_closed_session():
    """Test collect_pool_metrics handles closed session gracefully."""
    from cwaf_external_mcp.httpclient.aiohttp_client import collect_pool_metrics
    import cwaf_external_mcp.httpclient.aiohttp_client as client_module

    session = client_module.get_async_client()
    await session.close()

    # Now the session is closed, should handle gracefully
    collect_pool_metrics()


@pytest.mark.asyncio
async def test_collect_pool_metrics_with_active_session():
    """Test collect_pool_metrics collects metrics from active session."""
    from cwaf_external_mcp.httpclient.aiohttp_client import (
        collect_pool_metrics,
        get_async_client,
    )

    session = get_async_client()

    # Mock connector internals
    session.connector._acquired = set()
    session.connector._conns = {}
    session.connector._acquired_per_host = {}

    # Should not raise an exception
    collect_pool_metrics()

    await session.close()
