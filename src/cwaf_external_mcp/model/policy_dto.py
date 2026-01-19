"""Data Transfer Objects for Policy related data."""

from typing import Optional

from pydantic import BaseModel


class ExceptionData(BaseModel):
    """Data Transfer Object for Exception Data."""

    exceptionType: str
    values: list[str]


class ExceptionAssetMapping(BaseModel):
    """Data Transfer Object for Exception Asset Mapping."""

    id: int
    policyDataExceptionsId: int
    assetId: int
    assetType: str


class PolicyDataException(BaseModel):
    """Data Transfer Object for Policy Data Exception."""

    id: int
    policySettingsId: int
    lastModifiedBy: int
    lastModified: str
    comment: Optional[str] = None
    data: Optional[list[ExceptionData]] = None
    exceptionAssetMapping: Optional[list[ExceptionAssetMapping]] = None


class GeoDto(BaseModel):
    """Data Transfer Object for Geo Data."""

    countries: Optional[list[str]] = None
    continents: Optional[list[str]] = None


class UrlsDto(BaseModel):
    """Data Transfer Object for URLs Data."""

    url: Optional[str] = None
    UrlPattern: Optional[str] = None


class PolicySettingData(BaseModel):
    """Data Transfer Object for Policy Setting Data."""

    geo: Optional[GeoDto] = None
    ips: Optional[list[str]] = None
    urls: Optional[list[UrlsDto]] = None


class PolicySettings(BaseModel):
    """Data Transfer Object for Policy Settings."""

    id: int
    policyId: int
    settingsAction: str
    policySettingType: str
    data: Optional[PolicySettingData] = None
    policyDataExceptions: Optional[list[PolicyDataException]] = None


class PolicyConfig(BaseModel):
    """Data Transfer Object for Policy Config."""

    id: int
    policyId: int
    accountId: int
    assetType: str


class Policy(BaseModel):
    """Data Transfer Object for Policy."""

    id: int
    policyType: str
    name: str
    accountId: int
    enabled: bool
    description: str
    lastModified: str
    lastModifiedBy: int
    policySettings: Optional[list[PolicySettings]] = None
    defaultPolicyConfig: Optional[list[PolicyConfig]] = None
    assetsIds: Optional[list[int]]
    subaccountIds: Optional[list[str | int]]
