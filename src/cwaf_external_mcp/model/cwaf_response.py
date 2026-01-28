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
