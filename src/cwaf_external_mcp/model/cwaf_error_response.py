"""CWAF Error Response Model."""

from pydantic import BaseModel

from cwaf_external_mcp.model.api_error import ApiError


class CWAFErrorResponse(BaseModel):
    """Data Transfer Object for CWAF Error Response."""

    errors: list[ApiError]
