"""CWAF Response DTO Model."""

from typing import Optional, Any

from pydantic import BaseModel

from cwaf_external_mcp.model.policy_dto import Policy
from cwaf_external_mcp.model.rule_dto import Rule
from cwaf_external_mcp.model.site import Site
from cwaf_external_mcp.model.site_domain import SiteDomain


class Meta(BaseModel):
    """Metadata for paginated responses."""

    size: Optional[int]
    page: Optional[int]
    totalElements: Optional[int]
    totalPages: Optional[int]


class CWAFResponse(BaseModel):
    """Data Transfer Object for CWAF Response."""

    data: list[Site | SiteDomain | Policy | Rule | Any]
    meta: Meta
    links: dict = {}
