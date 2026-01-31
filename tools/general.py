"""通用业务：Product List、CDASH/CDASHIG、QRS。"""

import json
from config import CDISC_API_BASE
from utils.http_client import cdisc_get
from utils.formatters import truncate_json_response

# CDASHIG
CDASHIG_CLASSES = ["Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose"]
CDASHIG_DOMAINS = [
    "AG", "CM", "EC", "EX", "ML", "PR", "SU", "AE", "CE", "DS", "DV", "HO", "MH", "SA",
    "CP", "CV", "DA", "DD", "EG", "GF", "IE", "LB", "MB", "MI", "MK", "MS", "NV", "OE",
    "PC", "PE", "RE", "RP", "RS", "SC", "TR", "TU", "UR", "VS", "FA", "SR", "CO", "DM",
]
# CDASH Model
CDASH_CLASSES = [
    "Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose",
    "Identifiers", "AssociatedPersonsIdentifiers", "Timing",
]
CDASH_DOMAINS = ["AE", "CO", "DM", "DS", "MH", "MS"]

ALLOWED_QRS_COMBINATIONS = {
    "AIMS01": ["2-0"], "APCH1": ["1-0"], "ATLAS1": ["1-0"], "CGI02": ["2-1"],
    "HAMA1": ["2-1"], "KFSS1": ["2-0"], "KPSS1": ["2-0"], "PGI01": ["1-1"],
    "SIXMW1": ["1-0"],
}


async def get_product_list() -> str:
    """
    Get the master list of all CDISC Library API products and their available versions.
    When users inquire about CDISC-related products, you can first search the product list using this tool.
    Use this tool when the user asks about available CDISC standards, supported versions (e.g., "What versions of SDTM are available?"), or wants to explore the catalog.

    Returns:
        A JSON string containing the list of products (href, title, type) and their classes.
    """
    url = f"{CDISC_API_BASE}/products?expand=false"
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False)


async def get_cdashig_class_info(version: str, className: str | None = None) -> str:
    """
    Get CDASH Implementation Guide (CDASHIG) Classes from CDISC Library.

    Use this tool to list all available CDASHIG Classes (if className is omitted) or get detailed definition for a specific Class (e.g., 'Interventions').

    Args:
        version: The CDASHIG version. Common values: ["1-1-1", "2-0", "2-1", "2-2", "2-3"].
        className: ["Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose"]. If omitted, returns the list of all available classes for the version.

    Returns:
        JSON string containing the CDASHIG Class details, or an error message.
    """
    base_url = f"{CDISC_API_BASE}/cdashig/{version}/classes"
    if className:
        if className not in CDASHIG_CLASSES:
            return f"Error: className is invalid, got '{className}'"
        url = f"{base_url}/{className}/domains"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_cdashig_domain_info(version: str, domains: str | None = None) -> str:
    """
    Get CDASH Implementation Guide (CDASHIG) Domains from CDISC Library.

    Use this tool to list all available CDASHIG Domains (if domains is omitted) or get detailed definition for a specific Domain (e.g., 'AG').

    Args:
        version: The CDASHIG version. Common values: ["1-1-1", "2-0", "2-1", "2-2", "2-3"].
        domains: The CDASHIG Domain name. If omitted, returns the list of all available domains for the version.

    Returns:
        JSON string containing the CDASHIG Domain details, or an error message.
    """
    base_url = f"{CDISC_API_BASE}/cdashig/{version}/domains"
    if domains:
        if domains not in CDASHIG_DOMAINS:
            return f"Error: domains is invalid, got '{domains}'"
        url = f"{base_url}/{domains}"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_cdashig_scenarios_info(version: str, scenario: str | None = None) -> str:
    """
    Get CDASH Implementation Guide (CDASHIG) Scenarios from CDISC Library.

    Use this tool to list all available CDASHIG Scenarios (if scenario is omitted) or get detailed definition for a specific Scenario (e.g., 'DS', "AE", "SAE").

    Args:
        version: The CDASHIG version. Common values: ["1-1-1", "2-0", "2-1", "2-2", "2-3"].
        scenario: The CDASHIG Scenario name. If omitted, returns the list of all available scenarios for the version.

    Returns:
        JSON string containing the CDASHIG Scenario details, or an error message.
    """
    base_url = f"{CDISC_API_BASE}/cdashig/{version}/scenarios"
    url = f"{base_url}/{scenario}" if scenario else base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_cdash_model_class_info(version: str, className: str | None = None) -> str:
    """
    Get CDASH Model Class from CDISC Library.

    Use this tool to list all available CDASH Model Class (if className is omitted) or get detailed definition for a specific Class (e.g., 'Interventions').

    Args:
        version: The CDASH Model version. Common values: ["1-0", "1-1", "1-2", "1-3"].
        className: ["Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "Identifiers", "AssociatedPersonsIdentifiers", "Timing"]. If omitted, returns the list of all available classes for the version.

    Returns:
        JSON string containing the CDASH Model Class details, or an error message.
    """
    base_url = f"{CDISC_API_BASE}/cdash/{version}/classes"
    if className:
        if className not in CDASH_CLASSES:
            return f"Error: className is invalid, got '{className}'"
        url = f"{base_url}/{className}"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_cdash_model_domain_info(version: str, domain: str | None = None) -> str:
    """
    Get CDASH Model Domain from CDISC Library.

    Use this tool to list all available CDASH Model Domain (if domain is omitted) or get detailed definition for a specific Domain (e.g., 'AG').

    Args:
        version: The CDASH Model version. Common values: ["1-0", "1-1", "1-2", "1-3"].
        domain: ["AE", "CO", "DM", "DS", "MH", "MS"]. If omitted, returns the list of all available domains for the version.

    Returns:
        JSON string containing the CDASH Model Domain details, or an error message.
    """
    base_url = f"{CDISC_API_BASE}/cdash/{version}/domains"
    if domain:
        if domain not in CDASH_DOMAINS:
            return f"Error: domain is invalid, got '{domain}'"
        url = f"{base_url}/{domain}"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_qrs_info(instrument: str, version: str) -> str:
    """
    Get QRS Instrument Product information from CDISC Library.
    Use this tool to get specific QRS Instrument Product data.

    Args:
        instrument: The QRS Instrument name. Valid values: AIMS01 (2-0), APCH1 (1-0), ATLAS1 (1-0), CGI02 (2-1), HAMA1 (2-1), KFSS1 (2-0), KPSS1 (2-0), PGI01 (1-1), SIXMW1 (1-0).
        version: The version for the instrument (must match the valid combination).

    Returns:
        JSON string containing the QRS Instrument Product details, or an error message.
    """
    if instrument not in ALLOWED_QRS_COMBINATIONS:
        valid = ", ".join(ALLOWED_QRS_COMBINATIONS.keys())
        return f"Error: Invalid instrument '{instrument}'. Valid instruments are: {valid}"
    if version not in ALLOWED_QRS_COMBINATIONS[instrument]:
        valid = ", ".join(ALLOWED_QRS_COMBINATIONS[instrument])
        return f"Error: Invalid version '{version}' for instrument '{instrument}'. Valid versions are: {valid}"
    url = f"{CDISC_API_BASE}/qrs/instruments/{instrument}/versions/{version}"
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)
