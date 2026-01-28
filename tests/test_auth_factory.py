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
import os

from cwaf_external_mcp.auth.auth_factory import create_auth_from_config
from cwaf_external_mcp.auth.api_key_auth import ApiKeyAuthStrategy
from cwaf_external_mcp.auth.auth_base import AuthStrategy


def test_create_auth_from_config_with_api_key_mode(monkeypatch):
    """Test create_auth_from_config returns ApiKeyAuthStrategy for api_key mode."""
    monkeypatch.setenv("AUTH_MODE", "api_key")
    monkeypatch.setenv("API_ID", "123")
    monkeypatch.setenv("API_KEY", "test_key")

    auth = create_auth_from_config()

    assert isinstance(auth, ApiKeyAuthStrategy)
    assert auth.api_id == 123
    assert auth.api_key == "test_key"


def test_create_auth_from_config_defaults_to_api_key_mode(monkeypatch):
    """Test create_auth_from_config defaults to api_key mode when AUTH_MODE is not set."""
    # Remove AUTH_MODE from environment if it exists
    monkeypatch.delenv("AUTH_MODE", raising=False)
    monkeypatch.setenv("API_ID", "456")
    monkeypatch.setenv("API_KEY", "default_key")

    auth = create_auth_from_config()

    assert isinstance(auth, ApiKeyAuthStrategy)
    assert auth.api_id == 456
    assert auth.api_key == "default_key"


def test_create_auth_from_config_with_plugin_mode_valid_auth(monkeypatch):
    """Test create_auth_from_config with plugin mode returns custom AuthStrategy."""

    # Create a mock AuthStrategy class
    class MockAuthStrategy(AuthStrategy):
        def get_middlewares(self):
            return []

    # Mock factory function that returns our mock strategy
    mock_factory = mock.Mock(return_value=MockAuthStrategy())

    # Mock the importlib.import_module
    mock_module = mock.Mock()
    setattr(mock_module, "create_auth", mock_factory)

    monkeypatch.setenv("AUTH_MODE", "plugin")
    monkeypatch.setenv("AUTH_PROVIDER", "test.module:create_auth")

    with mock.patch("importlib.import_module", return_value=mock_module):
        auth = create_auth_from_config()

    assert isinstance(auth, MockAuthStrategy)
    mock_factory.assert_called_once()


def test_create_auth_from_config_with_plugin_mode_invalid_auth(monkeypatch):
    """Test create_auth_from_config with plugin mode raises TypeError for invalid auth."""

    # Mock factory function that returns an invalid object
    mock_factory = mock.Mock(return_value="not_an_auth_strategy")

    # Mock the importlib.import_module
    mock_module = mock.Mock()
    setattr(mock_module, "create_auth", mock_factory)

    monkeypatch.setenv("AUTH_MODE", "plugin")
    monkeypatch.setenv("AUTH_PROVIDER", "test.module:create_auth")

    with mock.patch("importlib.import_module", return_value=mock_module):
        with pytest.raises(TypeError) as exc_info:
            create_auth_from_config()

    assert "Auth provider factory must return an AuthStrategy" in str(exc_info.value)


def test_create_auth_from_config_with_plugin_mode_missing_provider(monkeypatch):
    """Test create_auth_from_config with plugin mode raises KeyError when AUTH_PROVIDER is missing."""
    monkeypatch.setenv("AUTH_MODE", "plugin")
    monkeypatch.delenv("AUTH_PROVIDER", raising=False)

    with pytest.raises(KeyError):
        create_auth_from_config()


def test_create_auth_from_config_with_unknown_mode(monkeypatch):
    """Test create_auth_from_config raises ValueError for unknown AUTH_MODE."""
    monkeypatch.setenv("AUTH_MODE", "unknown_mode")

    with pytest.raises(ValueError) as exc_info:
        create_auth_from_config()

    assert "Unknown AUTH_MODE: 'unknown_mode'" in str(exc_info.value)


def test_create_auth_from_config_with_plugin_mode_module_import_error(monkeypatch):
    """Test create_auth_from_config with plugin mode propagates ImportError."""
    monkeypatch.setenv("AUTH_MODE", "plugin")
    monkeypatch.setenv("AUTH_PROVIDER", "nonexistent.module:create_auth")

    with mock.patch(
        "importlib.import_module", side_effect=ImportError("Module not found")
    ):
        with pytest.raises(ImportError) as exc_info:
            create_auth_from_config()

    assert "Module not found" in str(exc_info.value)


def test_create_auth_from_config_with_plugin_mode_attribute_error(monkeypatch):
    """Test create_auth_from_config with plugin mode propagates AttributeError."""
    # Mock module without the expected attribute
    mock_module = mock.Mock(spec=[])

    monkeypatch.setenv("AUTH_MODE", "plugin")
    monkeypatch.setenv("AUTH_PROVIDER", "test.module:nonexistent_attr")

    with mock.patch("importlib.import_module", return_value=mock_module):
        with pytest.raises(AttributeError):
            create_auth_from_config()


def test_create_auth_from_config_with_plugin_mode_parses_provider_path(monkeypatch):
    """Test create_auth_from_config correctly parses AUTH_PROVIDER path."""

    # Create a mock AuthStrategy class
    class MockAuthStrategy(AuthStrategy):
        def get_middlewares(self):
            return []

    mock_factory = mock.Mock(return_value=MockAuthStrategy())
    mock_module = mock.Mock()
    setattr(mock_module, "my_factory", mock_factory)

    monkeypatch.setenv("AUTH_MODE", "plugin")
    monkeypatch.setenv("AUTH_PROVIDER", "my.custom.module:my_factory")

    with mock.patch("importlib.import_module", return_value=mock_module) as mock_import:
        auth = create_auth_from_config()

    # Verify the module path was parsed correctly
    mock_import.assert_called_once_with("my.custom.module")
    assert isinstance(auth, MockAuthStrategy)
