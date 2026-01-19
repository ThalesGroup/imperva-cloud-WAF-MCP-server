"""API error DTO."""

from typing import Optional

from pydantic import BaseModel


class ApiError(BaseModel):
    """Data Transfer Object for API Error."""

    code: Optional[int | str] = None
    status: Optional[int] = None
    title: Optional[str] = None
    message: Optional[str] = None
    detail: Optional[str] = None
    source: Optional[dict[str, str]] | Optional[str] = None
