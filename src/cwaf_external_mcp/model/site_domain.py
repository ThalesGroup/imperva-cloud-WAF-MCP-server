"""SiteDomain DTO."""

from typing import Optional

from pydantic import BaseModel


class SiteDomain(BaseModel):
    """Data Transfer Object for Site Domain."""

    name: str
    id: int
    site_id: int
    status: str
    creation_date: str
    aRecords: Optional[list[str]] = None
    cname: str
