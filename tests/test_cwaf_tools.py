# tests/test_cwaf_tools.py
import pytest
from unittest import mock

import cwaf_external_mcp.mcp_tools.cwaf_tools as cwaf_tools


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("API_ID", "123")
    monkeypatch.setenv("API_KEY", "abc")


@pytest.mark.asyncio
async def test_get_rules_api_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(
        return_value={"data": [{}], "meta": {}, "links": {}}
    )
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response
    monkeypatch.setattr(cwaf_tools, "get_rules_from_response", lambda r: "rule")
    result = await cwaf_tools.get_rules_api(1)
    assert hasattr(result, "data")
    assert result.data == ["rule"]


@pytest.mark.asyncio
async def test_get_rules_api_invalid_args(monkeypatch):
    monkeypatch.setattr(cwaf_tools, "_to_int", lambda x: int("fail"))
    result = await cwaf_tools.get_rules_api("bad")
    assert hasattr(result, "errors")
    assert result.errors[0].code == 400


@pytest.mark.asyncio
async def test_get_polices_of_account_by_filter_api_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(
        return_value={"data": [{}], "meta": {}, "links": {}}
    )
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response
    monkeypatch.setattr(cwaf_tools, "get_policy_from_response", lambda r: "policy")
    result = await cwaf_tools.get_polices_of_account_by_filter_api(1)
    assert hasattr(result, "data")
    assert result.data == ["policy"]


@pytest.mark.asyncio
async def test_get_site_domains_api_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(
        return_value={"data": [{}], "meta": {}, "links": {}}
    )
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response
    monkeypatch.setattr(cwaf_tools, "get_site_domain_from_response", lambda r: "domain")
    result = await cwaf_tools.get_site_domains_api(1)
    assert hasattr(result, "data")
    assert result.data == ["domain"]


@pytest.mark.asyncio
async def test_get_account_sites_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(
        return_value={"data": [{}], "meta": {}, "links": {}}
    )
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response
    monkeypatch.setattr(cwaf_tools, "get_site_from_response", lambda r: "site")
    result = await cwaf_tools.get_account_sites(1)
    assert hasattr(result, "data")
    assert result.data == ["site"]


@pytest.mark.asyncio
async def test_invoke_request_with_pagination_handling_http_error(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 500
    mock_response.json = mock.AsyncMock(return_value={"errors": [{"code": 500}]})
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response
    monkeypatch.setattr(
        cwaf_tools, "get_api_error_from_response", lambda r: mock.Mock(code=r["code"])
    )
    res, ok = await cwaf_tools.invoke_request_with_pagination_handling(
        "url", {}, lambda r: r, None
    )
    assert hasattr(res, "errors")
    assert ok is False
