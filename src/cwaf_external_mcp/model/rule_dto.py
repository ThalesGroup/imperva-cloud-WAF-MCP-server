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
