"""Rule DTO Model."""

from typing import Optional
from pydantic import BaseModel, Field


class SecurityRuleBlockDurationDetails(BaseModel):
    """Data Transfer Object for Security Rule Block Duration Details."""

    blockRandomizedDurationMaxValue: Optional[int] = None
    blockRandomizedDurationMinValue: Optional[int] = None
    blockFixedDurationValue: Optional[int] = None
    blockDurationPeriodType: Optional[str] = None


class Rule(BaseModel):
    """Data Transfer Object for Rule."""

    rule_id: int
    site_id: int
    account_id: int
    name: str
    action: str
    enabled: bool = True
    filter: Optional[str] = None
    # ForwardRule
    dc_id: Optional[int] = None
    # OverrideWafRule
    overrideWafRule: Optional[str] = None
    overrideWafAction: Optional[str] = None
    # RatesRule
    rate_interval: Optional[int] = None
    rate_context: Optional[str] = None
    # RedirectRule
    to_url: Optional[str] = Field(alias="to", default=None)
    from_url: Optional[str] = Field(alias="from", default=None)
    response_code: Optional[int] = None
    # RewritePortRule
    port_forwarding_value: Optional[str] = None
    port_forwarding_context: Optional[str] = None
    # RewriteRule
    multiple_deletions: Optional[bool] = None
    rewrite_existing: Optional[bool] = None
    add_missing: Optional[bool] = None
    rewrite_name: Optional[str] = None
    # SecurityRule
    sendNotifications: Optional[bool] = None
    blockDurationDetails: Optional[SecurityRuleBlockDurationDetails] = None
    # CustomErrorResponseRule
    error_response_data: Optional[str] = None
    error_response_format: Optional[str] = None
