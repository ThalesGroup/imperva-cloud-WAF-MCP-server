"""Site DTO."""

from typing import Optional

from pydantic import BaseModel


class Site(BaseModel):
    """Data Transfer Object for Site."""

    name: str
    id: int
    accountId: int
    type: str
    refId: Optional[str] = None
    active: bool
    cnames: Optional[str]
    attributes: Optional[dict[str, str]] = None
    creationTime: str
    siteStatus: Optional[str] = None
    isDefaultSite: Optional[bool] = None
    deploymentKeys: Optional[list[str]] = None
