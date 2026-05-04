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

import cwaf_external_mcp.mcp_tools.cwaf_tools as cwaf_tools
from cwaf_external_mcp.model.attack_analytics_dto import (
    AttackAnalyticsResponse,
    Incident,
    Event,
    IncidentStats,
    InsightsDataApi,
)


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("API_ID", "123")
    monkeypatch.setenv("API_KEY", "abc")


# ---------------------------------------------------------------------------
# invoke_analytics_get_request
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invoke_analytics_get_request_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(return_value=[{"id": "abc"}])
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response

    result = await cwaf_tools.invoke_analytics_get_request("http://test/url", {})

    assert isinstance(result, AttackAnalyticsResponse)
    assert result.data == [{"id": "abc"}]


@pytest.mark.asyncio
async def test_invoke_analytics_get_request_http_error(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 403
    mock_response.json = mock.AsyncMock(return_value={"message": "Forbidden"})
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response

    result = await cwaf_tools.invoke_analytics_get_request("http://test/url", {})

    assert hasattr(result, "errors")
    assert result.errors[0].status == 403
    assert result.errors[0].detail == "Forbidden"


@pytest.mark.asyncio
async def test_invoke_analytics_get_request_exception(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_client.get.side_effect = Exception("connection error")
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)

    result = await cwaf_tools.invoke_analytics_get_request("http://test/url", {})

    assert hasattr(result, "errors")
    assert result.errors[0].status == 500


# ---------------------------------------------------------------------------
# get_incidents_api
# ---------------------------------------------------------------------------

INCIDENT_PAYLOAD = [
    {
        "id": "ad2c8f40-3e82-11e9-354e-b114829e37eb",
        "main_sentence": "Bad Bots attack from United States",
        "secondary_sentence": "On host acme.com",
        "false_positive": False,
        "events_count": 520,
        "events_blocked_percent": 20,
        "first_event_time": 1548073343000,
        "last_event_time": 1548073399000,
        "severity": "MINOR",
        "severity_explanation": "Highly targeted",
        "incident_type": "REGULAR",
    }
]


@pytest.mark.asyncio
async def test_get_incidents_api_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(return_value=INCIDENT_PAYLOAD)
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response

    result = await cwaf_tools.get_incidents_api(account_id=12345)

    assert isinstance(result, AttackAnalyticsResponse)
    assert result.data == INCIDENT_PAYLOAD


@pytest.mark.asyncio
async def test_get_incidents_api_with_timestamps(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(return_value=INCIDENT_PAYLOAD)
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response

    result = await cwaf_tools.get_incidents_api(
        account_id=12345,
        from_timestamp=1548073343000,
        to_timestamp=1548073999000,
    )

    assert isinstance(result, AttackAnalyticsResponse)
    call_params = mock_client.get.call_args[1]["params"]
    assert call_params["from_timestamp"] == 1548073343000
    assert call_params["to_timestamp"] == 1548073999000


@pytest.mark.asyncio
async def test_get_incidents_api_missing_account_id(monkeypatch):
    result = await cwaf_tools.get_incidents_api(account_id=None)

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


@pytest.mark.asyncio
async def test_get_incidents_api_invalid_args(monkeypatch):
    monkeypatch.setattr(cwaf_tools, "_to_int", lambda x: int("fail"))
    result = await cwaf_tools.get_incidents_api(account_id="bad")

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


# ---------------------------------------------------------------------------
# get_incident_sample_events_api
# ---------------------------------------------------------------------------

SAMPLE_EVENTS_PAYLOAD = {
    "event_id": 123,
    "method": "GET",
    "host": "www.acme.com",
    "url_path": "/admin/login",
    "is_event_blocked": True,
}


@pytest.mark.asyncio
async def test_get_incident_sample_events_api_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(return_value=SAMPLE_EVENTS_PAYLOAD)
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response

    result = await cwaf_tools.get_incident_sample_events_api(
        account_id=12345,
        incident_id="ad2c8f40-3e82-11e9-354e-b114829e37eb",
    )

    assert isinstance(result, AttackAnalyticsResponse)
    assert result.data == SAMPLE_EVENTS_PAYLOAD
    called_url = mock_client.get.call_args[0][0]
    assert "ad2c8f40-3e82-11e9-354e-b114829e37eb" in called_url
    assert "sample-events" in called_url


@pytest.mark.asyncio
async def test_get_incident_sample_events_api_missing_account_id(monkeypatch):
    result = await cwaf_tools.get_incident_sample_events_api(
        account_id=None,
        incident_id="some-uuid",
    )

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


@pytest.mark.asyncio
async def test_get_incident_sample_events_api_missing_incident_id(monkeypatch):
    result = await cwaf_tools.get_incident_sample_events_api(
        account_id=12345,
        incident_id="",
    )

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


@pytest.mark.asyncio
async def test_get_incident_sample_events_api_invalid_args(monkeypatch):
    monkeypatch.setattr(cwaf_tools, "_to_int", lambda x: int("fail"))
    result = await cwaf_tools.get_incident_sample_events_api(
        account_id="bad",
        incident_id="some-uuid",
    )

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


# ---------------------------------------------------------------------------
# get_incident_stats_api
# ---------------------------------------------------------------------------

INCIDENT_STATS_PAYLOAD = {
    "id": "ad2c8f40-3e82-11e9-354e-b114829e37eb",
    "events_count": 520,
    "attack_ips": [{"key": {"ip": "10.0.0.1"}, "value": 100}],
    "attack_urls": [{"key": "/admin.php", "value": 5}],
    "associated_cve": ["CVE-2020-8417"],
}


@pytest.mark.asyncio
async def test_get_incident_stats_api_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(return_value=INCIDENT_STATS_PAYLOAD)
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response

    result = await cwaf_tools.get_incident_stats_api(
        account_id=12345,
        incident_id="ad2c8f40-3e82-11e9-354e-b114829e37eb",
    )

    assert isinstance(result, AttackAnalyticsResponse)
    assert result.data == INCIDENT_STATS_PAYLOAD
    called_url = mock_client.get.call_args[0][0]
    assert "stats" in called_url


@pytest.mark.asyncio
async def test_get_incident_stats_api_missing_account_id(monkeypatch):
    result = await cwaf_tools.get_incident_stats_api(
        account_id=None,
        incident_id="some-uuid",
    )

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


@pytest.mark.asyncio
async def test_get_incident_stats_api_missing_incident_id(monkeypatch):
    result = await cwaf_tools.get_incident_stats_api(
        account_id=12345,
        incident_id="",
    )

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


@pytest.mark.asyncio
async def test_get_incident_stats_api_invalid_args(monkeypatch):
    monkeypatch.setattr(cwaf_tools, "_to_int", lambda x: int("fail"))
    result = await cwaf_tools.get_incident_stats_api(
        account_id="bad",
        incident_id="some-uuid",
    )

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


# ---------------------------------------------------------------------------
# get_insights_api
# ---------------------------------------------------------------------------

INSIGHTS_PAYLOAD = [
    {
        "insights": [
            {
                "type": "BAD_BOTS",
                "mainSentence": "You have bad bot activity",
                "secondarySentence": "On 3 sites",
                "moreInfo": "More info here",
                "recommendation": "Enable Bot Protection",
                "vulnerableSites": [],
                "timestamp": "2024-01-01T00:00:00Z",
                "additionalDetails": {},
            }
        ]
    }
]


@pytest.mark.asyncio
async def test_get_insights_api_success(monkeypatch):
    mock_client = mock.AsyncMock()
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(return_value=INSIGHTS_PAYLOAD)
    monkeypatch.setattr(cwaf_tools, "get_async_client", lambda: mock_client)
    mock_client.get.return_value = mock_response

    result = await cwaf_tools.get_insights_api(account_id=12345)

    assert isinstance(result, AttackAnalyticsResponse)
    assert result.data == INSIGHTS_PAYLOAD
    called_url = mock_client.get.call_args[0][0]
    assert "insights" in called_url


@pytest.mark.asyncio
async def test_get_insights_api_missing_account_id(monkeypatch):
    result = await cwaf_tools.get_insights_api(account_id=None)

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


@pytest.mark.asyncio
async def test_get_insights_api_invalid_args(monkeypatch):
    monkeypatch.setattr(cwaf_tools, "_to_int", lambda x: int("fail"))
    result = await cwaf_tools.get_insights_api(account_id="bad")

    assert hasattr(result, "errors")
    assert result.errors[0].status == 400


# ---------------------------------------------------------------------------
# DTO model validation
# ---------------------------------------------------------------------------


def test_incident_model_optional_fields():
    incident = Incident(id="test-uuid")
    assert incident.id == "test-uuid"
    assert incident.severity is None
    assert incident.ddos_data is None


def test_event_model_optional_fields():
    event = Event(event_id=1, method="GET", host="example.com")
    assert event.event_id == 1
    assert event.violations is None
    assert event.cookies is None


def test_incident_stats_model_optional_fields():
    stats = IncidentStats(id="test-uuid", events_count=100)
    assert stats.events_count == 100
    assert stats.associated_cve is None
    assert stats.attack_ips is None


def test_insights_data_api_model():
    insights = InsightsDataApi(insights=[])
    assert insights.insights == []


def test_attack_analytics_response_wraps_list():
    response = AttackAnalyticsResponse(data=[{"id": "1"}, {"id": "2"}])
    assert len(response.data) == 2


def test_attack_analytics_response_wraps_dict():
    response = AttackAnalyticsResponse(data={"id": "abc", "events_count": 10})
    assert response.data["id"] == "abc"
