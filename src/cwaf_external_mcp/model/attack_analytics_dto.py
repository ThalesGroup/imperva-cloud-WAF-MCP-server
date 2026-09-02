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

"""Attack Analytics DTOs."""

from typing import Any, List, Optional

from pydantic import BaseModel


class AttackedSiteInfo(BaseModel):
    """Information about an attacked site."""

    site_id: Optional[int] = None
    site_name: Optional[str] = None


class CountryDominance(BaseModel):
    """Dominance information for a country."""

    dominance: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None


class IpDominance(BaseModel):
    """Dominance information for an IP address."""

    dominance: Optional[str] = None
    ip: Optional[str] = None
    reputation: Optional[List[str]] = None


class ToolDominance(BaseModel):
    """Dominance information for an attack tool."""

    dominance: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None


class ShinyObject(BaseModel):
    """Dominant value object."""

    dominance: Optional[str] = None
    value: Optional[str] = None


class DdosData(BaseModel):
    """DDoS-specific attack data."""

    max_BPS_passed: Optional[float] = None
    max_BPS_blocked: Optional[float] = None
    network_traffic_data_list: Optional[List[dict]] = None


class Incident(BaseModel):
    """Single attack analytics incident."""

    id: Optional[str] = None
    main_sentence: Optional[str] = None
    secondary_sentence: Optional[str] = None
    false_positive: Optional[bool] = None
    events_count: Optional[int] = None
    events_blocked_percent: Optional[int] = None
    first_event_time: Optional[int] = None
    last_event_time: Optional[int] = None
    severity: Optional[str] = None
    severity_explanation: Optional[str] = None
    dominant_attack_country: Optional[CountryDominance] = None
    dominant_attack_ip: Optional[IpDominance] = None
    dominant_attacked_host: Optional[ShinyObject] = None
    dominant_attack_tool: Optional[ToolDominance] = None
    dominant_attack_violation: Optional[str] = None
    only_custom_rule_based: Optional[bool] = None
    how_common: Optional[str] = None
    incident_type: Optional[str] = None
    ddos_data: Optional[DdosData] = None


class Violation(BaseModel):
    """A single WAF rule violation."""

    rule_description: Optional[str] = None
    action: Optional[str] = None
    violation_context: Optional[str] = None


class Cookie(BaseModel):
    """HTTP cookie data."""

    name: Optional[str] = None
    value: Optional[str] = None
    domain: Optional[str] = None
    expiration: Optional[str] = None
    path: Optional[str] = None
    persistent: Optional[bool] = None
    secure: Optional[bool] = None
    traceability: Optional[str] = None


class Event(BaseModel):
    """Single event that participated in an attack."""

    event_id: Optional[int] = None
    method: Optional[str] = None
    host: Optional[str] = None
    query_string: Optional[str] = None
    url_path: Optional[str] = None
    response_code: Optional[str] = None
    session_id: Optional[str] = None
    main_client_ip: Optional[str] = None
    country_code: Optional[List[str]] = None
    client_application: Optional[str] = None
    declared_client_application: Optional[str] = None
    destination_ip: Optional[str] = None
    referrer: Optional[str] = None
    is_event_blocked: Optional[bool] = None
    violations: Optional[List[Violation]] = None
    headers: Optional[List[dict]] = None
    cookies: Optional[List[Cookie]] = None
    reporter: Optional[str] = None
    creation_time: Optional[str] = None


class IncidentStats(BaseModel):
    """Full statistics for a single incident."""

    id: Optional[str] = None
    events_count: Optional[int] = None
    blocked_events_timeseries: Optional[List[dict]] = None
    alerted_events_timeseries: Optional[List[dict]] = None
    attack_ips: Optional[List[dict]] = None
    attack_agents: Optional[List[dict]] = None
    attack_tools: Optional[List[dict]] = None
    attack_tool_types: Optional[List[dict]] = None
    violations_blocked: Optional[List[dict]] = None
    violations_alerted: Optional[List[dict]] = None
    attack_urls: Optional[List[dict]] = None
    attacked_hosts: Optional[List[dict]] = None
    attack_class_c: Optional[List[dict]] = None
    attack_geolocations: Optional[List[dict]] = None
    waf_origins_of_alerts: Optional[List[dict]] = None
    waf_origins_of_blocks: Optional[List[dict]] = None
    waf_origins_entities: Optional[List[dict]] = None
    rules_list: Optional[List[dict]] = None
    associated_cve: Optional[List[str]] = None


class GeneralInsightData(BaseModel):
    """General data for an insight."""

    attacked_site_info: Optional[AttackedSiteInfo] = None
    status: Optional[str] = None
    snoozedUntil: Optional[int] = None


class Insight(BaseModel):
    """A single insight entry for a vulnerable site."""

    type: Optional[str] = None
    insightDetails: Optional[GeneralInsightData] = None
    additionalDetails: Optional[dict] = None


class InsightSummaryVOApi(BaseModel):
    """Summary of a single insight recommendation."""

    type: Optional[str] = None
    mainSentence: Optional[str] = None
    secondarySentence: Optional[str] = None
    moreInfo: Optional[str] = None
    recommendation: Optional[str] = None
    vulnerableSites: Optional[List[Insight]] = None
    timestamp: Optional[str] = None
    additionalDetails: Optional[dict] = None


class InsightsDataApi(BaseModel):
    """Container for a list of insight summaries."""

    insights: Optional[List[InsightSummaryVOApi]] = None


class AttackAnalyticsResponse(BaseModel):
    """Response wrapper for Attack Analytics API calls."""

    data: Any
