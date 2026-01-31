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
import time


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv("API_ID", "123")
    monkeypatch.setenv("API_KEY", "abc")


def test_poll_connection_pool_metrics_enabled(monkeypatch):
    """Test poll_connection_pool_metrics when enabled."""
    monkeypatch.setenv("HTTP_CONNECTION_POOL_METRICS_JOB_ENABLED", "true")

    call_count = 0

    def mock_collect():
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            raise KeyboardInterrupt()

    with mock.patch(
        "cwaf_external_mcp.httpclient.connection_pool_metrics.collect_pool_metrics",
        side_effect=mock_collect,
    ):
        with mock.patch(
            "cwaf_external_mcp.httpclient.connection_pool_metrics.time.sleep"
        ):
            from cwaf_external_mcp.httpclient.connection_pool_metrics import (
                poll_connection_pool_metrics,
            )

            try:
                poll_connection_pool_metrics()
            except KeyboardInterrupt:
                pass

            assert call_count == 2


def test_poll_connection_pool_metrics_disabled(monkeypatch):
    """Test poll_connection_pool_metrics when disabled."""
    monkeypatch.setenv("HTTP_CONNECTION_POOL_METRICS_JOB_ENABLED", "false")

    call_count = 0

    def mock_sleep(duration):
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            raise KeyboardInterrupt()

    with mock.patch(
        "cwaf_external_mcp.httpclient.connection_pool_metrics.collect_pool_metrics"
    ) as mock_collect:
        with mock.patch(
            "cwaf_external_mcp.httpclient.connection_pool_metrics.time.sleep",
            side_effect=mock_sleep,
        ):
            from cwaf_external_mcp.httpclient.connection_pool_metrics import (
                poll_connection_pool_metrics,
            )

            try:
                poll_connection_pool_metrics()
            except KeyboardInterrupt:
                pass

            assert not mock_collect.called


def test_poll_connection_pool_metrics_handles_exception(monkeypatch):
    """Test poll_connection_pool_metrics handles exceptions gracefully."""
    monkeypatch.setenv("HTTP_CONNECTION_POOL_METRICS_JOB_ENABLED", "true")

    call_count = 0

    def mock_collect():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("Test error")
        else:
            raise KeyboardInterrupt()

    with mock.patch(
        "cwaf_external_mcp.httpclient.connection_pool_metrics.collect_pool_metrics",
        side_effect=mock_collect,
    ):
        with mock.patch(
            "cwaf_external_mcp.httpclient.connection_pool_metrics.time.sleep"
        ):
            from cwaf_external_mcp.httpclient.connection_pool_metrics import (
                poll_connection_pool_metrics,
            )

            try:
                poll_connection_pool_metrics()
            except KeyboardInterrupt:
                pass

            # Should continue after exception
            assert call_count == 2
