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

"""MCP logging middleware."""

from fastmcp.server.middleware import Middleware, MiddlewareContext

from cwaf_external_mcp.context.context_manager import context_manager
from cwaf_external_mcp.utilities.logging import get_logger

logger = get_logger(__name__)


class APIKeyMiddleware(Middleware):
    """log tool request processing."""

    def __init__(self, api_id: int, api_key: str):
        """Initialize the APIKeyMiddleware with API credentials."""
        super().__init__()
        self.api_id = api_id
        self.api_key = api_key

    async def on_message(self, context: MiddlewareContext, call_next):
        if context.method == "tools/call":
            context_manager.set_headers(
                {
                    "x-api-id": str(self.api_id),
                    "x-api-key": self.api_key,
                }
            )
        return await call_next(context)
