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
