"""ADaM 相关业务逻辑。"""

import json
from config import CDISC_API_BASE
from utils.http_client import cdisc_get
from utils.formatters import (
    truncate_json_response,
    truncate_json_string,
    remove_all_analysis_variables,
    remove_links_parent_refs,
)

ALLOWED_ADAM_DATASTRUCTURE_COMBINATIONS = {
    "adam-nca-1-0": ["ADNCA"],
    "adamig-1-0": ["ADSL", "BDS"],
    "adamig-1-1": ["ADSL", "BDS"],
    "adam-occds-1-0": ["OCCDS"],
    "adam-occds-1-1": ["OCCDS", "AE"],
    "adam-adae-1-0": ["ADAE"],
    "adam-poppk-1-0": ["ADPPK"],
    "adam-tte-1-0": ["ADTTE"],
    "adamig-1-2": ["ADSL", "BDS"],
    "adam-md-1-0": ["ADDL", "MDOCCDS", "MDBDS", "MDTTE"],
    "adamig-1-3": ["ADSL", "BDS", "TTE"],
}


async def get_adam_product_info(product: str) -> str:
    """
    Get ADAM Product and Datastructures information from CDISC Library.
    Use this tool to get ADAM product data, and datastructures information.

    Args:
        product: The ADAM product type. Common values: adam-2-1, adam-adae-1-0, adam-md-1-0, adam-nca-1-0, adam-occds-1-0, adam-occds-1-1, adam-poppk-1-0, adam-tte-1-0, adamig-1-0, adamig-1-1, adamig-1-2, adamig-1-3.

    Returns:
        JSON string containing the ADAM product details and datastructures information, or an error message.
    """
    url = f"{CDISC_API_BASE}/adam/{product}"
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    remove_all_analysis_variables(result)
    return truncate_json_string(json.dumps(result, ensure_ascii=False))


async def get_adam_datastructure_info(product: str, datastructure: str) -> str:
    """
    Get ADAM Datastructure information from CDISC Library.
    Use this tool to get specific ADAM datastructure data.

    Args:
        product: The ADAM product type. Valid values: adam-nca-1-0 (ADNCA), adamig-1-0/1-1 (ADSL, BDS), adam-occds-1-0 (OCCDS), adam-occds-1-1 (OCCDS, AE), adam-adae-1-0 (ADAE), adam-poppk-1-0 (ADPPK), adam-tte-1-0 (ADTTE), adamig-1-2 (ADSL, BDS), adam-md-1-0 (ADDL, MDOCCDS, MDBDS, MDTTE), adamig-1-3 (ADSL, BDS, TTE).
        datastructure: The datastructure name. Must be a valid combination with the product.

    Returns:
        JSON string containing the ADAM datastructure details, or an error message.
    """
    if product not in ALLOWED_ADAM_DATASTRUCTURE_COMBINATIONS:
        valid = ", ".join(ALLOWED_ADAM_DATASTRUCTURE_COMBINATIONS.keys())
        return f"Error: Invalid product '{product}'. Valid products are: {valid}"
    allowed_ds = ALLOWED_ADAM_DATASTRUCTURE_COMBINATIONS[product]
    if datastructure not in allowed_ds:
        return f"Error: Invalid datastructure '{datastructure}' for product '{product}'. Valid datastructures are: {', '.join(allowed_ds)}"
    url = f"{CDISC_API_BASE}/adam/{product}/datastructures/{datastructure}"
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    remove_links_parent_refs(result)
    return truncate_json_string(json.dumps(result, ensure_ascii=False))
