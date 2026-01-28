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

"""CWAF Tools"""

import os
from datetime import datetime, timezone
from typing import Callable, Optional, List, Union

from dotenv import load_dotenv
from fastmcp import Context

from cwaf_external_mcp.context.context_manager import context_manager
from cwaf_external_mcp.httpclient.aiohttp_client import get_async_client
from cwaf_external_mcp.model.api_error import ApiError
from cwaf_external_mcp.model.cwaf_error_response import CWAFErrorResponse
from cwaf_external_mcp.model.cwaf_response import CWAFResponse, Meta
from cwaf_external_mcp.model.policy_dto import Policy, PolicySettings, PolicyConfig
from cwaf_external_mcp.model.rule_dto import Rule
from cwaf_external_mcp.model.site import Site
from cwaf_external_mcp.model.site_domain import SiteDomain
from cwaf_external_mcp.utilities.logging import get_logger
from cwaf_external_mcp.utilities.parameters_parser import (
    _coerce_list,
    _to_int,
    _to_bool,
)

load_dotenv()
logger = get_logger(__name__)

BASE_SITES_URL = os.environ.get("BASE_SITES_URL", "https://api.imperva.com/sites-mgmt")
BASE_DOMAINS_URL = os.environ.get(
    "BASE_DOMAINS_URL", "https://api.imperva.com/site-domain-manager"
)
BASE_POLICIES_URL = os.environ.get(
    "BASE_POLICIES_URL", "https://api.imperva.com/policies"
)
BASE_RULES_URL = os.environ.get("BASE_RULES_URL", "https://my.imperva.com/api/prov")


async def get_rules_api(
    account_id: Optional[Union[int, str]],
    context: Optional[Context] = None,
    site_ids: Optional[Union[List[int], str]] = None,
    sub_accounts_ids: Optional[Union[List[int], str]] = None,
    rules_ids: Optional[Union[List[int], str]] = None,
    names: Optional[Union[List[str], str]] = None,
    categories: Optional[Union[List[str], str]] = None,
    page_num: Union[int, str] = 0,
    page_size: Union[int, str] = None,
) -> CWAFResponse | CWAFErrorResponse:
    """
    get site domains api

    :param account_id: The ID of the account.
    :param site_ids: list of sites IDs.
    :param sub_accounts_ids: list of sub-accounts IDs.
    :param rules_ids: list of rules IDs.
    :param categories: list of rules categories.
    :param names: list of rules names.
    :param page_num: The page number to fetch.
    :param page_size: The number of items per page.
    """
    logger.info(
        "Fetching rules for account %s, with filters site_ids: %s, subaccount_ids: %s, policies_ids: %s, names: %s, policy_types: %s",
        account_id,
        site_ids,
        sub_accounts_ids,
        rules_ids,
        names,
        categories,
    )

    url = BASE_RULES_URL + "/v3/rules"

    try:
        account_id_n = _to_int(account_id)
        sub_accounts_ids_n = _coerce_list(sub_accounts_ids, int)
        site_ids_n = _coerce_list(site_ids, int)
        rules_ids_n = _coerce_list(rules_ids, int)
        names_n = _coerce_list(names, str)
        categories_n = _coerce_list(categories, str)
        page_num_n = _to_int(page_num)
        page_size_n = _to_int(page_size)
    except Exception as e:
        logger.error("Error parsing parameters for get_rules_api: %s", e, exc_info=True)
        return CWAFErrorResponse(
            errors=[
                ApiError(
                    code=400,
                    message="Bad Request",
                    detail="Invalid tool arguments",
                )
            ]
        )

    params = {}
    if account_id_n:
        if os.environ.get("USE_CAID_ON_RULES", "true").lower() == "true":
            params["caid"] = account_id_n
        else:
            params["accountId"] = account_id_n
    if page_num_n:
        params["page_num"] = page_num_n
    if page_size_n:
        params["page_size"] = page_size_n
    if site_ids_n:
        params["siteIds"] = ",".join(map(str, site_ids_n))
    if sub_accounts_ids_n:
        params["subAccIds"] = ",".join(map(str, sub_accounts_ids_n))
    if names_n:
        params["names"] = ",".join(names_n)
    if rules_ids_n:
        params["ruleIds"] = ",".join(map(str, rules_ids_n))
    if categories_n:
        params["categories"] = ",".join(categories_n)

    res, _ = await invoke_request_with_pagination_handling(
        url, params, get_rules_from_response, context
    )
    return res


async def get_polices_of_account_by_filter_api(
    account_id: Optional[Union[int, str]],
    context: Optional[Context] = None,
    site_ids: Optional[Union[List[int], str]] = None,
    sub_accounts_ids: Optional[Union[List[int], str]] = None,
    policies_ids: Optional[Union[List[int], str]] = None,
    policy_types: Optional[Union[List[str], str]] = None,
    extended: Union[bool, str] = True,
    names: Optional[list[str]] = None,
    page_num: Union[int, str] = 0,
    page_size: Union[int, str] = None,
) -> CWAFResponse | CWAFErrorResponse:
    """
    Fetches the list of policies for a given account by filters.

    :param account_id: The ID of the account.
    :param site_ids: list of sites IDs.
    :param sub_accounts_ids: list of sub-accounts IDs.
    :param policies_ids: list of policies IDs.
    :param policy_types: list of policy types.
    :param extended: whether to fetch extended policy details.
    :param names: list of policies names.
    :param page_num: The page number to fetch.
    :param page_size: The number of items per page.

    :return: A list of dictionaries containing site details.
    """

    url = BASE_POLICIES_URL + "/v3/policies"

    logger.info(
        "Fetching policies for account %s, with filters site_ids: %s, subaccount_ids: %s, policies_ids: %s, names: %s, policy_types: %s",
        account_id,
        site_ids,
        sub_accounts_ids,
        policies_ids,
        names,
        policy_types,
    )

    try:
        account_id_n = _to_int(account_id)
        sub_accounts_ids_n = _coerce_list(sub_accounts_ids, int)
        site_ids_n = _coerce_list(site_ids, int)
        policies_ids_n = _coerce_list(policies_ids, int)
        names_n = _coerce_list(names, str)
        policy_types_n = _coerce_list(policy_types, str)
        extended_n = _to_bool(extended)
        page_num_n = _to_int(page_num)
        page_size_n = _to_int(page_size)
    except Exception as e:
        logger.error(
            "Error parsing parameters for get_polices_of_account_by_filter_api: %s",
            e,
            exc_info=True,
        )
        return CWAFErrorResponse(
            errors=[
                ApiError(
                    code=400,
                    message="Bad Request",
                    detail="Invalid tool arguments",
                )
            ]
        )

    params = {"extended": str(extended_n).lower()}
    if account_id_n:
        params["caid"] = account_id_n
    if page_num_n:
        params["page"] = page_num_n
    if page_size_n:
        params["size"] = page_size_n
    if site_ids_n:
        params["assetIds"] = ",".join(map(str, site_ids_n))
    if sub_accounts_ids_n:
        params["subAccIds"] = ",".join(map(str, sub_accounts_ids_n))
    if names_n:
        params["names"] = ",".join(names_n)
    if policies_ids_n:
        params["policyIds"] = ",".join(map(str, policies_ids_n))
    if policy_types_n:
        params["types"] = ",".join(policy_types_n)

    res, _ = await invoke_request_with_pagination_handling(
        url, params, get_policy_from_response, context
    )
    return res


async def get_site_domains_api(
    account_id: Optional[Union[int, str]],
    context: Optional[Context] = None,
    domain_ids: Optional[Union[List[int], str]] = None,
    site_ids: Optional[Union[List[int], str]] = None,
    names: Optional[Union[List[str], str]] = None,
    page_num: Union[int, str] = 0,
    page_size: Union[int, str] = None,
) -> CWAFResponse | CWAFErrorResponse:
    """
    get site domains api

    :param account_id: The ID of the account.
    :param site_ids: list of sites IDs.
    :param domain_ids: list of domain IDs.
    :param names: list of domain names.
    :param page_num: The page number to fetch.
    :param page_size: The number of items per page.
    """
    logger.info("Fetching domains for account %s", account_id)

    try:
        account_id_n = _to_int(account_id)
        domain_ids_n = _coerce_list(domain_ids, int)
        site_ids_n = _coerce_list(site_ids, int)
        names_n = _coerce_list(names, str)
        page_num_n = _to_int(page_num)
        page_size_n = _to_int(page_size)
    except Exception as e:
        logger.error(
            "Error parsing parameters for get_site_domains_api: %s", e, exc_info=True
        )
        return CWAFErrorResponse(
            errors=[
                ApiError(
                    code=400,
                    message="Bad Request",
                    detail="Invalid tool arguments",
                )
            ]
        )

    url = BASE_DOMAINS_URL + "/v3/domains"
    params = {}
    if account_id_n:
        params["caid"] = account_id_n
    if site_ids_n:
        params["siteIds"] = ",".join(map(str, site_ids_n))
    if domain_ids_n:
        params["domainIds"] = ",".join(map(str, domain_ids_n))
    if names_n:
        params["names"] = ",".join(names_n)
    if page_num_n:
        params["page"] = page_num_n
    if page_size_n:
        params["size"] = page_size_n
    res, _ = await invoke_request_with_pagination_handling(
        url, params, get_site_domain_from_response, context
    )
    return res


async def get_account_sites(
    account_id: Optional[Union[int, str]],
    context: Optional[Context] = None,
    external_site_ids: Optional[Union[List[int], str]] = None,
    names: Optional[Union[List[str], str]] = None,
    sub_account_ids: Optional[Union[List[int], str]] = None,
    page_num: Union[int, str] = 0,
    page_size: Union[int, str] = None,
) -> CWAFResponse | CWAFErrorResponse:
    """
    Fetches the list of sites for a given account.

    :param account_id: The ID of the account.
    :param names: list of sites names.
    :param external_site_ids: list of external sites IDs.
    :param sub_account_ids: list of subaccount IDs.
    :param page_num: The page number to fetch.
    :param page_size: The number of items per page.

    :return: A list of dictionaries containing site details.
    """
    logger.info("Fetching sites for account %s", account_id)

    try:
        account_id_n = _to_int(account_id)
        external_site_ids_n = _coerce_list(external_site_ids, int)
        sub_account_ids_n = _coerce_list(sub_account_ids, int)
        names_n = _coerce_list(names, str)
        page_num_n = _to_int(page_num)
        page_size_n = _to_int(page_size)
    except Exception as e:
        logger.error(
            "Error parsing parameters for get_account_sites: %s", e, exc_info=True
        )
        return CWAFErrorResponse(
            errors=[
                ApiError(
                    code=400,
                    message="Bad Request",
                    detail="Invalid tool arguments",
                )
            ]
        )

    params = {}
    if account_id_n:
        params["caid"] = account_id_n
    if page_num_n:
        params["page"] = page_num_n
    if page_size_n:
        params["size"] = page_size_n
    if external_site_ids_n:
        params["siteIds"] = ",".join(map(str, external_site_ids_n))
    if names_n:
        params["names"] = ",".join(names_n)
    if sub_account_ids_n:
        params["subAccIds"] = ",".join(map(str, sub_account_ids_n))

    url = BASE_SITES_URL + "/v3/sites/extended"
    res, _ = await invoke_request_with_pagination_handling(
        url, params, get_site_from_response, context
    )
    return res


async def invoke_request_with_pagination_handling(
    url: str,
    params: dict,
    mapper_func: Callable[[dict], SiteDomain | Site | Policy | Rule],
    context: Optional[Context] = None,
) -> tuple[CWAFResponse | CWAFErrorResponse, bool]:
    """Invoke an HTTP GET request with pagination handling."""

    MCP_HEADER_NAME = os.environ.get("MCP_HEADER_NAME", "x-mcp-imperva")

    MCP_HEADER_VALUE = os.environ.get("MCP_HEADER_VALUE", "cwaf-external-mcp")

    HEADERS = {
        "Content-Type": "application/json",
        MCP_HEADER_NAME: MCP_HEADER_VALUE,
    }

    HEADERS.update(context_manager.get_headers())

    try:
        logger.info("calling %s, with params %s", url, params)
        full_data = []
        response = await get_async_client().get(url, headers=HEADERS, params=params)
        logger.info(f"response: {response}")
        data = await response.json(content_type=None)
        logger.info("response from %s, with params %s: %s", url, params, data)
        if response.status != 200:
            if context:
                await context.error(data)
            response = (
                data["errors"]
                if "errors" in data
                else (
                    data["body"]["errors"]
                    if "body" in data and "errors" in data["body"]
                    else [
                        CWAFErrorResponse(
                            errors=[
                                ApiError(
                                    status=500,
                                    title="internal error",
                                    detail="",
                                )
                            ]
                        )
                    ]
                )
            )

            return (
                CWAFErrorResponse(
                    errors=[get_api_error_from_response(r) for r in response]
                ),
                False,
            )
        response = data["data"]
        pagination_data = get_pagination_data(data["meta"])
        links = data["links"] if "links" in data else {}
        full_data += [mapper_func(r) for r in response]
        return CWAFResponse(data=full_data, meta=pagination_data, links=links), True
    except Exception:
        logger.exception("Error invoking %s with params %s", url, params)
        return (
            CWAFErrorResponse(
                errors=[
                    ApiError(
                        status=500,
                        title="internal error",
                        detail="",
                    )
                ]
            ),
            False,
        )


def get_pagination_data(pagination_data):
    """Get pagination data from response metadata."""
    return Meta(
        page=pagination_data["page"] if "page" in pagination_data else None,
        size=pagination_data["size"] if "size" in pagination_data else None,
        totalElements=(
            pagination_data["totalElements"]
            if "totalElements" in pagination_data
            else None
        ),
        totalPages=(
            pagination_data["totalPages"] if "totalPages" in pagination_data else None
        ),
    )


def get_rules_from_response(r: dict) -> Rule:
    """Convert response dictionary to Rule object."""
    return Rule(
        rule_id=r["rule"]["rule_id"],
        site_id=r["site_id"],
        account_id=r["account_id"],
        name=r["rule"]["name"],
        action=r["rule"]["action"],
        enabled=r["rule"]["enabled"],
        filter=r["rule"]["filter"] if "filter" in r["rule"] else None,
        dc_id=r["rule"]["dcId"] if "dcId" in r["rule"] else None,
        overrideWafRule=(
            r["rule"]["overrideWafRule"] if "overrideWafRule" in r["rule"] else None
        ),
        overrideWafAction=(
            r["rule"]["overrideWafAction"] if "overrideWafAction" in r["rule"] else None
        ),
        rate_interval=(
            r["rule"]["rateInterval"] if "rateInterval" in r["rule"] else None
        ),
        rate_context=r["rule"]["rateContext"] if "rateContext" in r["rule"] else None,
        to_url=r["rule"]["to"] if "to" in r["rule"] else None,
        from_url=r["rule"]["from"] if "from" in r["rule"] else None,
        response_code=(
            r["rule"]["responseCode"] if "responseCode" in r["rule"] else None
        ),
        port_forwarding_value=(
            r["rule"]["portForwardingValue"]
            if "portForwardingValue" in r["rule"]
            else None
        ),
        port_forwarding_context=(
            r["rule"]["portForwardingContext"]
            if "portForwardingContext" in r["rule"]
            else None
        ),
        multiple_deletions=(
            r["rule"]["multipleDeletions"] if "multipleDeletions" in r["rule"] else None
        ),
        rewrite_existing=(
            r["rule"]["rewriteExisting"] if "rewriteExisting" in r["rule"] else None
        ),
        add_missing=r["rule"]["addMissing"] if "addMissing" in r["rule"] else None,
        rewrite_name=r["rule"]["rewriteName"] if "rewriteName" in r["rule"] else None,
    )


def get_site_domain_from_response(r: dict) -> SiteDomain:
    """Convert response dictionary to SiteDomain object."""
    return SiteDomain(
        id=r["id"],
        name=r["domain"],
        status=r["status"],
        site_id=r["siteId"],
        creation_date=(
            datetime.fromtimestamp(r["creationDate"] / 1000, tz=timezone.utc)
        ).strftime("%Y-%m-%d %H:%M:%S"),
        aRecords=r["arecords"] if "arecords" in r else None,
        cname=r["cname"],
    )


def get_api_error_from_response(r: dict) -> ApiError:
    """Convert response dictionary to APiError object."""
    return ApiError(
        code=(r["code"] if "code" in r else None),
        message=r["message"] if "message" in r else None,
        status=(r["status"] if "status" in r else None),
        title=(r["title"] if "title" in r else None),
        detail=(r["detail"] if "detail" in r else None),
    )


def get_policy_from_response(r: dict) -> Policy:
    """Convert response dictionary to Site object."""
    return Policy(
        id=r["id"],
        policyType=r["policyType"],
        name=r["name"],
        accountId=r["accountId"],
        enabled=r["enabled"],
        description=r["description"],
        lastModified=r["lastModified"],
        lastModifiedBy=r["lastModifiedBy"],
        policySettings=(
            get_policy_settings_from_response(r["policySettings"])
            if "policySettings" in r and r["policySettings"] is not None
            else None
        ),
        defaultPolicyConfig=(
            get_default_policy_config_from_response(r["defaultPolicyConfig"])
            if "defaultPolicyConfig" in r and r["defaultPolicyConfig"] is not None
            else None
        ),
        assetsIds=r["assetsIds"],
        subaccountIds=r["subaccountIds"],
    )


def get_policy_settings_from_response(policy_settings: list) -> list[PolicySettings]:
    """Convert response dictionary to PolicySettings object."""
    return [
        PolicySettings(
            id=r["id"],
            policyId=r["policyId"],
            settingsAction=r["settingsAction"],
            policySettingType=r["policySettingType"],
            data=r["data"] if "data" in r else None,
            policyDataExceptions=(
                r["policyDataExceptions"] if "policyDataExceptions" in r else None
            ),
        )
        for r in policy_settings
    ]


def get_default_policy_config_from_response(policy_config: list) -> list[PolicyConfig]:
    """Convert response dictionary to PolicyConfig object."""
    return [
        PolicyConfig(
            id=r["id"],
            policyId=r["policyId"],
            accountId=r["accountId"],
            assetType=r["assetType"],
        )
        for r in policy_config
    ]


def get_site_from_response(r: dict) -> Site:
    """Convert response dictionary to Site object."""
    return Site(
        id=r["id"],
        name=r["name"],
        isDefaultSite=r["isDefaultSite"] if "isDefaultSite" in r else None,
        accountId=r["accountId"],
        refId=r["refId"],
        active=r["active"],
        cnames=r["cname"] if "cname" in r else None,
        siteStatus=r["siteStatus"],
        creationTime=(
            datetime.fromtimestamp(r["creationTime"] / 1000, tz=timezone.utc)
        ).strftime("%Y-%m-%d %H:%M:%S"),
        attributes=r["attributes"] if "attributes" in r else None,
        type=r["type"],
        deploymentKeys=r["deploymentKeys"] if "deploymentKeys" in r else None,
    )
