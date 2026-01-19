"""Base class for authentication strategies."""

from abc import ABC, abstractmethod
from typing import List
from fastmcp.server.middleware import Middleware


class AuthStrategy(ABC):
    """Abstract base class for authentication strategies."""

    @abstractmethod
    def get_middlewares(self) -> List[Middleware]:
        """Return a list of middlewares for the authentication strategy."""
        return []
