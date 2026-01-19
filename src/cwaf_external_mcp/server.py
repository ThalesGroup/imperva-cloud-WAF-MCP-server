"""MCP server Tools"""

import os
import threading
from typing import Optional, Union, List

from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from prometheus_client import start_http_server

from cwaf_external_mcp.auth.auth_factory import create_auth_from_config
from cwaf_external_mcp.httpclient.connection_pool_metrics import (
    poll_connection_pool_metrics,
)
from cwaf_external_mcp.mcp_tools.cwaf_tools import (
    get_account_sites,
    get_site_domains_api,
    get_polices_of_account_by_filter_api,
    get_rules_api,
)
from cwaf_external_mcp.model.cwaf_error_response import CWAFErrorResponse
from cwaf_external_mcp.model.cwaf_response import CWAFResponse
from cwaf_external_mcp.utilities.logging import get_logger

load_dotenv()

logger = get_logger(__name__)

if os.environ.get("PROMETHEUS_CLIENT_ENABLED", "false").lower() == "true":
    start_http_server(int(os.environ.get("PROMETHEUS_PORT", "9050")))

SERVER_PORT = int(os.environ.get("SERVER_PORT", "8050"))


# Create an MCP server
cwaf_mcp = FastMCP(name="Cloud WAF Tools")

MY_routes = ["get_rules_of_account_tool"]


@cwaf_mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint to verify the server is running."""
    return PlainTextResponse("OK")


@cwaf_mcp.tool()
async def get_rules_of_account_tool(
    context: Context,
    account_id: Optional[Union[int, str]],
    site_ids: Optional[Union[List[int], str]] = None,
    sub_accounts_ids: Optional[Union[List[int], str]] = None,
    rules_ids: Optional[Union[List[int], str]] = None,
    categories: Optional[Union[List[str], str]] = None,
    names: Optional[Union[List[str], str]] = None,
    page_num: Optional[Union[int, str]] = None,
    page_size: Optional[Union[int, str]] = None,
) -> CWAFResponse | CWAFErrorResponse:
    """
    Fetches the custom rules details associated with the sites under the given account.
    The supported type of rules are:
        rate rules, security rules, forward rules, redirect rules, rewrite rules

    Parameters:
        account_id (int): Unique identifier of the sub-account, if the account in context is the main account associated to the used API_ID this field MUST be empty (Optional)
        site_ids (list of numbers): list of sites IDs, only rules assigned to sites with those IDs will retrieve, if it exists (Optional)
        rules_ids (list of numbers): list of rules IDs, only rules with those IDs will retrieve, if it exists (Optional)
        sub_accounts_ids (list of numbers): list of subaccounts IDs, only rules assigned to sites under those subaccounts will retrieve, if it exists. (Optional)
        names (list of strings): list of rules names, only rules with those names will retrieve, if it exists. (Optional)
        categories (list of strings): list of rules categories, only rules with those types will retrieve, if it exists. possible values are "WafOverride","WafOverride","RewriteResponse","SimplifiedRedirect","Security","Rates","Rewrite","Redirect". (Optional)
        page_num (int) Optional: The page number to fetch. Defaults to 0.
        page_size (int) Optional: The number of items per page. Defaults to 100

    Returns:
        On success: CWAFResponse: an object with the following properties:
            data: a list of Rules objects, if there are no rules associated with the site, an empty list will be returned:
                  For each rule type, a different set of properties is available:
                Rule:{
                    rule_id: int --> The unique identifier for the rule.
                    site_id: int --> The unique identifier for the site that this rule assigned to.
                    account_id: int --> The unique identifier for the account that the site that this rule assigned to belongs.
                    name: str --> The name of the rule.
                    action: str --> The action to be taken when the rule matches (e.g., "ALLOW", "BLOCK", "REDIRECT", for security rules, and "rewrite url", "rewrite header" ... for delivery rule).
                    enabled: bool = True  --> Indicates whether the rule is currently enabled. Defaults to True.
                    filter: str --> Optional filter expression for the rule. This is used to match specific conditions. (can exists on all rule types)
                    dc_id: int --> The ID of the data center where the rule is applied. (only exists on ForwardRule)
                    overrideWafRule: str --> The WAF rule to override. (only exists on OverrideWafRule)
                    overrideWafAction: str --> The action to take when overriding the WAF rule. (only exists on OverrideWafRule)
                    rate_interval: int --> The time interval for rate limiting in seconds. (only exists on RatesRule)
                    rate_context:str --> The context for the rate limiting rule. (only exists on RatesRule)
                    to_url: str --> The URL to redirect to. (only exists on RedirectRule)
                    from_url: str --> The URL to redirect from. (only exists on RedirectRule)
                    response_code: int --> The HTTP response code to return for the redirect. (only exists on RedirectRule)
                    port_forwarding_value: str --> The port forwarding value for the rule. (only exists on RewritePortRule)
                    port_forwarding_context: str --> The context for the port forwarding rule. (only exists on RewritePortRule)
                    multiple_deletions: bool --> Indicates whether multiple deletions are allowed for the rewrite rule. (only exists on RewriteRule)
                    rewrite_existing: bool --> Indicates whether existing rules should be rewritten. (only exists on RewriteRule)
                    add_missing: bool --> Indicates whether missing rules should be added. (only exists on RewriteRule)
                    rewrite_name: bool --> The name of the rewrite rule. (only exists on RewriteRule)
                    sendNotifications: bool --> Indicates whether notifications should be sent when the rule is triggered. (only exists on SecurityRule)
                    blockDurationDetails: SecurityRuleBlockDurationDetails --> Details about the block duration for security rules. (only exists on SecurityRule)
                    error_response_data: str --> The data for the custom error response. (only exists on CustomErrorResponseRule)
                    error_response_format: str --> The format of the custom error response. (only exists on CustomErrorResponseRule)
                }
                SecurityRuleBlockDurationDetails object is used to define the block duration for security rules:
                        SecurityRuleBlockDurationDetails:{
                                blockRandomizedDurationMaxValue: int --> The maximum value for randomized block duration in seconds.
                                blockRandomizedDurationMinValue: int --> The minimum value for randomized block duration in seconds.
                                blockFixedDurationValue: int --> The fixed value for block duration in seconds.
                                blockDurationPeriodType: str --> The type of block duration period ("randomized" or "fixed").
                        }
            meta: Meta object containing pagination information:
                Meta:{
                    size: int --> The number of items per page.
                    page: int --> The current page number.
                    totalElements: int --> The total number of elements across all pages. (only available when all_pages is True)
                    totalPages: int --> The total number of pages available. (only available when all_pages is True)
                }

        On failure: a list of ApiError objects:
            ApiError:{
                status: int --> The HTTP status code of the error.
                title: str --> A brief title describing the error.
                detail: Optional[str] = None --> A detailed description of the error, if available.
                source: Optional[str] = None --> The source of the error, if applicable.
            }
    """
    return await get_rules_api(
        account_id=account_id,
        site_ids=site_ids,
        sub_accounts_ids=sub_accounts_ids,
        rules_ids=rules_ids,
        categories=categories,
        names=names,
        page_num=page_num,
        page_size=page_size,
        context=context,
    )


@cwaf_mcp.tool()
async def get_polices_of_account_by_filter_tool(
    context: Context,
    account_id: Optional[Union[int, str]],
    site_ids: Optional[Union[List[int], str]] = None,
    sub_accounts_ids: Optional[Union[List[int], str]] = None,
    policies_ids: Optional[Union[List[int], str]] = None,
    policy_types: Optional[Union[List[str], str]] = None,
    extended: Union[bool, str] = True,
    names: Optional[Union[List[str], str]] = None,
    page_num: Optional[Union[int, str]] = None,
    page_size: Optional[Union[int, str]] = None,
) -> CWAFResponse | CWAFErrorResponse:
    """
    Fetches all policies of a given account.

    Parameters:
        account_id (int): Unique identifier of the sub-account, if the account in context is the main account associated to the used API_ID this field MUST be empty (Optional)
        site_ids (list of numbers): list of sites IDs, only policies assigned to sites with those IDs will retrieve, if it exists (Optional)
        policies_ids (list of numbers): list of policies IDs, only policies with those IDs will retrieve, if it exists (Optional)
        sub_accounts_ids (list of numbers): list of subaccounts IDs, only policies allowed by those subaccounts will retrieve, if it exists. (Optional)
        names (list of strings): list of policies names, only policies with those names will retrieve, if it exists. (Optional)
        policy_types (list of strings): list of policy types, only policies with those types will retrieve, if it exists. possible values are "WAF_RULES", "ACL", "WHITELIST". (Optional)
        extended (bool): whether to retrieve the full policy details, or only the basic information (without the policySettings and defaultPolicyConfig fields). Defaults to True. (Optional)
        page_num (int) Optional: The page number to fetch. Default to 0.
        page_size (int) Optional: The number of items per page. Defaults to 20, max 100.

    Returns:
        On success: CWAFResponse: an object with the following properties:
        data: a list of Policy objects (described below), if there are no rules associated with the site, an empty list will be returned
        meta: Meta object containing pagination information:
            Meta:{
                size: int --> The number of items per page.
                page: int --> The current page number.
                totalElements: int --> The total number of elements across all pages.
                totalPages: int --> The total number of pages available.
            }
        links: dict --> An object containing pagination links (if applicable).
            Policy: {
                id: int --> The unique identifier for the policy.
                name: str --> The policy name.
                description: str --> A brief description of the policy.
                enabled: bool --> Indicates whether the policy is currently enabled.
                accountId: int --> The unique identifier of the account to which the policy belongs.
                policyType: str --> The type of the policy, possible values are "WAF_RULES", "ACL", "WHITELIST"
                lastModifiedBy: str --> The user who last modified the policy.
                lastModified: int --> The timestamp of the last modification in milliseconds since epoch.
                defaultPolicyConfig: list of PolicyConfig objects --> if this is not the default policy this will be an empty list.
                policySettings: List of PolicySetting objects --> The settings of the policy. (will be different for each policy type, for example, ACL policies will have a list of ACL rules, WAF policies will have a list of WAF rules, etc.)
                assetsIds: List of int --> The list of site IDs to which the policy is attached. (if the assetsIds parameter was given in the request, this list will contain only the site IDs that match the given site_ids).
                subaccountIds: List of int --> The list of subaccount IDs that can use this policy. (if all subaccounts can use this policy, this list will contain only the '*' value).
            }
            PolicyConfig: {
                id: int --> The unique identifier for the policy configuration. (you can ignore it)
                policyId: str --> The unique identifier of the default policy.
                accountId: int --> The unique identifier of the account to which the policy belongs.
                assetType: str --> the asset type, will always be 'WEBSITE' for now.
            }
            PolicySetting: {
                id: int --> The unique identifier for the policy setting.
                policyId: int --> The unique identifier of the policy to which the setting belongs.
                settingsAction: str --> The action to be taken for the setting, possible values are "ALLOW", "BLOCK", "MASK", "IGNORE", "BLOCK_IP", "BLOCK_USER", "ALERT".
                policySettingType: str --> The type of the policy setting.
                                           possible values for "WAF_RULES" are: "REMOTE_FILE_INCLUSION", "ILLEGAL_RESOURCE_ACCESS", "CROSS_SITE_SCRIPTING", "SQL_INJECTION","RESP_DATA_LEAK"
                                           possible values for "ACL" and "WHITELIST" are: "IP","URL","GEO".
                data: list of PolicySettingData objects --> The data associated with the policy setting, this will be different for each policy type, for example, ACL policies will have a list URLs, WHITELIST policies will have a list of IPs.
                                                            PolicySettingData is not available for "WAF_RULES" policy type.
                policyDataExceptions: list of PolicyDataException objects --> The exceptions for the policy setting, this will be different for each policy type, for example, ACL policies will have a list of URLs, WHITELIST policies will have a list of IPs.
            }
            PolicySettingData: {
                urls: list of UrlsDto --> The URLs associated with the policy setting. available only for "ACL" policy type.
                ips: list of str --> The IPs associated with the policy setting.
                geo: GeoDto --> The geographical location associated with the policy setting. available only for "ACL" policy type.
            }
            UrlsDto: {
                UrlPattern: str --> The URL pattern associated with the policy setting. possible values are "CONTAINS", "NOT_SUFFIX", "NOT_PREFIX","SUFFIX","PREFIX","NOT_CONTAINS","NOT_EQUALS","EQUALS"
                url: str --> The URL associated with the policy setting.
            }
            GeoDto: {
                continents : list of str --> The continents associated with the policy setting.
                countries: list of str --> The countries associated with the policy setting.
            }
            policyDataExceptions: {
                id: int --> The unique identifier for the policy data exception.
                policySettingId: int --> The unique identifier of the policy setting to which the exception belongs.
                data: list of ExceptionData objects --> The Filter/s of the exception.
                comment : str --> A comment describing the exception.
                lastModified: str --> The date (UTC) of the last modification since field.
                lastModifiedBy : str --> The user who last modified the exception.
                exceptionAssetMapping - list of ExceptionAssetMapping objects --> The asset mapping of the exception.
            }
            ExceptionData: {
                ExceptionType: str --> The type of the exception, possible values are "USER_AGENT", "HTTP_PARAM", "SITE_ID","URL_CONTAINS","CLIENT_ID","URL_NOT_SUFFIX","URL_NOT_PREFIX",
                                       "URL_SUFFIX","URL_PREFIX","URL_NOT_CONTAINS","URL_NOT_EQUALS","URL","IP","GEO"
                values: list of str --> Values of the exception vary based on the exceptionType parameter.
            }
            ExceptionAssetMapping: {
                id: int --> The unique identifier for the exception asset mapping.
                policyDataExceptionsId: int --> The unique identifier of the policy data exception to which the asset mapping belongs.
                assetId: int --> The unique identifier of the asset to which the exception applies. (e.g., site ID)
                assetType: str --> The type of the asset, currently only "WEBSITE" is supported.
            }

        On failure: a list of ApiError objects:
            ApiError:{
                status: int --> The HTTP status code of the error.
                title: str --> A brief title describing the error.
                detail: Optional[str] = None --> A detailed description of the error, if available.
                source: Optional[str] = None --> The source of the error, if applicable.
            }
    """
    return await get_polices_of_account_by_filter_api(
        account_id=account_id,
        site_ids=site_ids,
        sub_accounts_ids=sub_accounts_ids,
        policies_ids=policies_ids,
        policy_types=policy_types,
        extended=extended,
        names=names,
        page_num=page_num,
        page_size=page_size,
        context=context,
    )


@cwaf_mcp.tool()
async def get_domains_by_filters_tool(
    context: Context,
    account_id: Optional[Union[int, str]],
    domain_ids: Optional[Union[List[int], str]] = None,
    site_ids: Optional[Union[List[int], str]] = None,
    names: Optional[Union[List[str], str]] = None,
    page_num: Optional[Union[int, str]] = None,
    page_size: Optional[Union[int, str]] = None,
) -> CWAFResponse | CWAFErrorResponse:
    """
    Fetches the domains associated with a specific site under a given account.
    To get a single domain details provide the domain ID, or the domain name.
    Use the most effective filter according to the context, for example, if you have the domain ID use it; if you have the domain name use it.
    If you get an empty list, it means that the domain does not exist, or you do not have access to it, avoid getting all domains and filter on your side.
    Note: CloudWAF site can have multiple domains.

    Parameters:
        account_id (int): Unique identifier of the sub-account, if the account in context is the main account associated to the used API_ID this field MUST be empty (Optional)
        site_ids: (list of numbers) list of sites IDs.
        domain_ids: (list of numbers) list of domain IDs.
        names: (list of strings) list of domain names.
        page_num (number) Optional: The page number to fetch. Defaults to 0.
        page_size (number) Optional: The number of items per page. Defaults to 10, valid values are 10,25,50,100.

    Returns:
        On success: CWAFResponse: an object with the following properties:
            data: a list of SiteDomain objects, if there are no domains associated with the site, an empty list will be returned:
                SiteDomain:{
                    name: str --> The domain name.
                    id: int --> The unique identifier for the domain.
                    status: str --> The current status of the domain. Possible values include "UNKNOWN", "NOT_CONFIGURED", and "CONFIGURED".
                    creation_date: str --> The date (UTC) when the domain was created.
                    aRecords: str --> The A records associated with the domain, only applicable for Apex domains.
                    cname: str --> The CNAME record of Imperva that this domain should use (only applicable for sub-domain, Note: this is not the domain of the site)
                }
            meta: Meta object containing pagination information:
                Meta:{
                    size: int --> The number of items per page. [max: 500, default: 20]
                    page: int --> The current page number.
                    totalElements: int --> The total number of elements across all pages.
                    totalPages: int --> The total number of pages available.
                }
            links: dict --> Additional links related to the response, if any.
                   available links:
                    - self: The URL to the current resource.
                    - first: The URL to the first page of results.
                    - last: The URL to the last page of results.
                    - next: The URL to the next page of results, if available.
                    - prev: The URL to the previous page of results, if available.

        On failure: a list of ApiError objects:
            ApiError:{
                status: int --> The HTTP status code of the error.
                title: str --> A brief title describing the error.
                detail: str --> A detailed description of the error, if available.
                source: str --> The source of the error, if applicable.
            }
    """
    return await get_site_domains_api(
        account_id=account_id,
        site_ids=site_ids,
        domain_ids=domain_ids,
        names=names,
        page_num=page_num,
        page_size=page_size,
        context=context,
    )


@cwaf_mcp.tool()
async def get_sites_details_of_a_given_account_tool(
    context: Context,
    account_id: Optional[Union[int, str]],
    site_ids: Optional[Union[List[int], str]] = None,
    names: Optional[Union[List[str], str]] = None,
    sub_account_ids: Optional[Union[List[int], str]] = None,
    page_num: Optional[Union[int, str]] = None,
    page_size: Optional[Union[int, str]] = None,
) -> CWAFResponse | CWAFErrorResponse:
    """
    Fetches the list of sites for a given account.
    To get a single site details provide the site Id or the site name.
    Use the most effective filter according to the context, for example, if you have the site ID use it; if you have the site name use it;
    If you get an empty list, it means that the site does not exist, or you do not have access to it, avoid getting all sites and filter on your side.
    Terminology: The site name is not always the domain name, to get the list of domains use the domains_get_domains_of_specific_site_tool.

    Parameters:
        account_id (int): Unique identifier of the sub-account, if the account in context is the main account associated to the used API_ID this field MUST be empty (Optional)
        names (list of strings): list of sites names, only sites with those names will retrieve, if exists. (Optional)
        site_ids (list of numbers): list of external sites IDs, only sites with those IDs will retrieve, if exists (Optional)
        sub_account_ids (list of numbers): list of subaccount IDs, only sites under the matching subaccounts will retrieve, if exists. (Optional)
        page_num (int) Optional: The page number to fetch. Defaults to 0.
        page_size (int) Optional: The number of items per page. Defaults to 10, valid values are 10,25,50,100.

    Returns:
        On success: CWAFResponse: an object with the following properties:
            data: a list of Site objects:
                Site:{
                    name: str --> The site name. (the site name is not always the domain name, to get the list of domains use the appropriate tool)
                    id: int --> The unique identifier for the site.
                    accountId: int --> The unique identifier of the account to which the site belongs.
                    type: str --> The type of the site (e.g., "CWAF" or "LOACL").
                    refId: Optional[str] = None --> An optional external reference identifier for the site.
                    active: bool --> Indicates whether the site is currently active.
                    cnames: str --> The CNAME record customer required to put on the domains of the site to pass traffic to Imperva CWAF. (Note: this is not the domain of the site)
                    attributes: Optional[dict[str, str]] = None --> Optional key-value pairs for storing additional site-specific metadata.
                    creationTime: str --> The timestamp in milliseconds since epoch, indicating when the site was created.
                    siteStatus: Optional[str] = None --> The current status of the site, such as "CONFIGURED", "NOT_CONFIGURED", "PARTIALLY_CONFIGURED.
                }
            meta: Meta object containing pagination information:
                Meta:{
                    size: int --> The number of items per page. [supported values are 10,25,50,100]
                    page: int --> The current page number.
                    totalElements: int --> The total number of elements across all pages.
                    totalPages: int --> The total number of pages available.
                }
            links: dict --> Additional links related to the response, if any.
                   available links:
                    - self: The URL to the current resource.
                    - first: The URL to the first page of results.
                    - last: The URL to the last page of results.
                    - next: The URL to the next page of results, if available.
                    - prev: The URL to the previous page of results, if available.

        On failure: a list of ApiError objects:
            ApiError:{
                status: int --> The HTTP status code of the error.
                title: str --> A brief title describing the error.
                detail: Optional[str] = None --> A detailed description of the error, if available.
                source: Optional[str] = None --> The source of the error, if applicable.
            }
    """
    return await get_account_sites(
        account_id=account_id,
        names=names,
        external_site_ids=site_ids,
        sub_account_ids=sub_account_ids,
        page_num=page_num,
        page_size=page_size,
        context=context,
    )


# Run the server
def main():
    """Main method."""
    auth_strategy = create_auth_from_config()
    for middleware in auth_strategy.get_middlewares():
        cwaf_mcp.add_middleware(middleware)
    if os.environ.get("PROMETHEUS_CLIENT_ENABLED", "false").lower() == "true":
        threading.Thread(target=poll_connection_pool_metrics, daemon=True).start()
    if os.environ.get("STDIO", "true").lower() == "true":
        logger.info("Running server with stdio transport")
        cwaf_mcp.run(transport="stdio")
    else:
        logger.info("Running server with streamable-http transport")
        cwaf_mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=SERVER_PORT,
            uvicorn_config={
                "http": "h11",
                "h11_max_incomplete_event_size": 65536,
                "root_path": os.environ.get("BASE_PATH", "/mcp"),
            },
        )


if __name__ == "__main__":
    main()
