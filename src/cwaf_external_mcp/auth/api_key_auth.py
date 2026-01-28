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

"""API Key Authentication Strategy."""

import os
from abc import ABC
from typing import List

from fastmcp.server.middleware import Middleware

from .apikey_middleware import APIKeyMiddleware
from .auth_base import AuthStrategy


class ApiKeyAuthStrategy(AuthStrategy, ABC):
    """API Key Authentication Strategy."""

    def __init__(self):
        """Initialize the API Key Authentication Strategy."""
        self.api_id = int(os.environ["API_ID"])
        self.api_key = os.environ["API_KEY"]

    def get_middlewares(self) -> List[Middleware]:
        return [APIKeyMiddleware(self.api_id, self.api_key)]
