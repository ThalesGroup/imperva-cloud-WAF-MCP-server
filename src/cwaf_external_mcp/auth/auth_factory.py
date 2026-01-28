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

"""Factory for creating AuthStrategy based on config."""

import os
import importlib
from .auth_base import AuthStrategy
from .api_key_auth import ApiKeyAuthStrategy


def create_auth_from_config() -> AuthStrategy:
    """Decide which AuthStrategy to use based on config."""
    mode = os.getenv("AUTH_MODE", "api_key")

    if mode == "api_key":
        return ApiKeyAuthStrategy()

    if mode == "plugin":
        provider_path = os.environ["AUTH_PROVIDER"]
        module_name, attr_name = provider_path.rsplit(":", 1)
        module = importlib.import_module(module_name)
        factory = getattr(module, attr_name)
        auth = factory()
        if not isinstance(auth, AuthStrategy):
            raise TypeError("Auth provider factory must return an AuthStrategy")
        return auth

    raise ValueError(f"Unknown AUTH_MODE: {mode!r}")
