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

import logging
import pytest
from unittest import mock


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv("API_ID", "123")
    monkeypatch.setenv("API_KEY", "abc")
    monkeypatch.setenv("LOG_LEVEL", "INFO")


def test_get_logger_returns_logger():
    """Test get_logger returns a logging.Logger instance."""
    from cwaf_external_mcp.utilities.logging import get_logger

    logger = get_logger("test_logger")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"


def test_get_logger_with_custom_level():
    """Test get_logger with custom log level."""
    from cwaf_external_mcp.utilities.logging import get_logger

    logger = get_logger("test_logger_custom", level="DEBUG")

    assert isinstance(logger, logging.Logger)


def test_configure_logging_uses_env_log_level(monkeypatch):
    """Test configure_logging uses LOG_LEVEL from environment."""
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Reset logging configuration
    logging.root.handlers = []
    logging.root.setLevel(logging.WARNING)

    from cwaf_external_mcp.utilities.logging import configure_logging

    configure_logging()

    # Check that root logger level is set
    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_with_explicit_level():
    """Test configure_logging with explicit level parameter."""
    # Reset logging configuration
    logging.root.handlers = []
    logging.root.setLevel(logging.WARNING)

    from cwaf_external_mcp.utilities.logging import configure_logging

    configure_logging(level="WARNING")

    # Check that root logger level is set
    assert logging.getLogger().level == logging.WARNING


def test_context_filter_adds_trace_id():
    """Test ContextFilter adds trace_id to log records."""
    from cwaf_external_mcp.utilities.logging import ContextFilter

    filter_instance = ContextFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="test message",
        args=(),
        exc_info=None,
    )

    result = filter_instance.filter(record)

    assert result is True
    assert hasattr(record, "trace_id")
