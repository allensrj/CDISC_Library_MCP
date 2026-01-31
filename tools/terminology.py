"""Controlled Terminology (CT) 相关业务逻辑。"""

import json
from config import CDISC_API_BASE, CT_TIMEOUT
from utils.http_client import cdisc_get
from utils.formatters import truncate_json_string, prune_ct_codelists
from config import TRUNCATE_SUFFIX_CT

CT_PACKAGE = [
    "adamct-2014-09-26", "adamct-2015-12-18", "adamct-2016-03-25", "adamct-2016-09-30",
    "adamct-2016-12-16", "adamct-2017-03-31", "adamct-2017-09-29", "adamct-2018-12-21",
    "adamct-2019-03-29", "adamct-2019-12-20", "adamct-2020-03-27", "adamct-2020-06-26",
    "adamct-2020-11-06", "adamct-2021-12-17", "adamct-2022-06-24", "adamct-2023-03-31",
    "adamct-2023-06-30", "adamct-2024-03-29", "adamct-2024-09-27", "adamct-2025-03-28",
    "adamct-2025-09-26", "cdashct-2014-09-26", "cdashct-2015-03-27", "cdashct-2016-03-25",
    "cdashct-2016-09-30", "cdashct-2016-12-16", "cdashct-2017-09-29", "cdashct-2018-03-30",
    "cdashct-2018-06-29", "cdashct-2018-09-28", "cdashct-2018-12-21", "cdashct-2019-03-29",
    "cdashct-2019-06-28", "cdashct-2019-12-20", "cdashct-2020-11-06", "cdashct-2020-12-18",
    "cdashct-2021-03-26", "cdashct-2021-06-25", "cdashct-2021-09-24", "cdashct-2021-12-17",
    "cdashct-2022-06-24", "cdashct-2022-09-30", "cdashct-2022-12-16", "cdashct-2024-09-27",
    "cdashct-2025-03-28", "coact-2014-12-19", "coact-2015-03-27", "ddfct-2022-09-30",
    "ddfct-2022-12-16", "ddfct-2023-03-31", "ddfct-2023-06-30", "ddfct-2023-09-29",
    "ddfct-2023-12-15", "ddfct-2024-03-29", "ddfct-2024-09-27", "ddfct-2025-09-26",
    "define-xmlct-2019-12-20", "define-xmlct-2020-03-27", "define-xmlct-2020-06-26",
    "define-xmlct-2020-11-06", "define-xmlct-2020-12-18", "define-xmlct-2021-03-26",
    "define-xmlct-2021-06-25", "define-xmlct-2021-09-24", "define-xmlct-2021-12-17",
    "define-xmlct-2022-09-30", "define-xmlct-2022-12-16", "define-xmlct-2023-06-30",
    "define-xmlct-2023-12-15", "define-xmlct-2024-03-29", "define-xmlct-2024-09-27",
    "define-xmlct-2025-03-28", "define-xmlct-2025-09-26", "glossaryct-2020-12-18",
    "glossaryct-2021-12-17", "glossaryct-2022-12-16", "glossaryct-2023-12-15",
    "glossaryct-2024-09-27", "glossaryct-2025-09-26", "mrctct-2024-03-29", "mrctct-2024-09-27",
    "mrctct-2025-09-26", "protocolct-2017-03-31", "protocolct-2017-06-30", "protocolct-2017-09-29",
    "protocolct-2018-03-30", "protocolct-2018-06-29", "protocolct-2018-09-28", "protocolct-2019-03-29",
    "protocolct-2019-06-28", "protocolct-2019-09-27", "protocolct-2019-12-20", "protocolct-2020-03-27",
    "protocolct-2020-06-26", "protocolct-2020-11-06", "protocolct-2020-12-18", "protocolct-2021-03-26",
    "protocolct-2021-06-25", "protocolct-2021-09-24", "protocolct-2021-12-17", "protocolct-2022-03-25",
    "protocolct-2022-06-24", "protocolct-2022-09-30", "protocolct-2022-12-16", "protocolct-2023-03-31",
    "protocolct-2023-06-30", "protocolct-2023-09-29", "protocolct-2023-12-15", "protocolct-2024-03-29",
    "protocolct-2024-09-27", "protocolct-2025-03-28", "protocolct-2025-09-26", "qrsct-2015-06-26",
    "qrsct-2015-09-25", "qs-ftct-2014-09-26", "sdtmct-2014-09-26", "sdtmct-2014-12-19",
    "sdtmct-2015-03-27", "sdtmct-2015-06-26", "sdtmct-2015-09-25", "sdtmct-2015-12-18",
    "sdtmct-2016-03-25", "sdtmct-2016-06-24", "sdtmct-2016-09-30", "sdtmct-2016-12-16",
    "sdtmct-2017-03-31", "sdtmct-2017-06-30", "sdtmct-2017-09-29", "sdtmct-2017-12-22",
    "sdtmct-2018-03-30", "sdtmct-2018-06-29", "sdtmct-2018-09-28", "sdtmct-2018-12-21",
    "sdtmct-2019-03-29", "sdtmct-2019-06-28", "sdtmct-2019-09-27", "sdtmct-2019-12-20",
    "sdtmct-2020-03-27", "sdtmct-2020-06-26", "sdtmct-2020-11-06", "sdtmct-2020-12-18",
    "sdtmct-2021-03-26", "sdtmct-2021-06-25", "sdtmct-2021-09-24", "sdtmct-2021-12-17",
    "sdtmct-2022-03-25", "sdtmct-2022-06-24", "sdtmct-2022-09-30", "sdtmct-2022-12-16",
    "sdtmct-2023-03-31", "sdtmct-2023-06-30", "sdtmct-2023-09-29", "sdtmct-2023-12-15",
    "sdtmct-2024-03-29", "sdtmct-2024-09-27", "sdtmct-2025-03-28", "sdtmct-2025-09-26",
    "sendct-2014-09-26", "sendct-2014-12-19", "sendct-2015-03-27", "sendct-2015-06-26",
    "sendct-2015-09-25", "sendct-2015-12-18", "sendct-2016-03-25", "sendct-2016-06-24",
    "sendct-2016-09-30", "sendct-2016-12-16", "sendct-2017-03-31", "sendct-2017-06-30",
    "sendct-2017-09-29", "sendct-2017-12-22", "sendct-2018-03-30", "sendct-2018-06-29",
    "sendct-2018-09-28", "sendct-2018-12-21", "sendct-2019-03-29", "sendct-2019-06-28",
    "sendct-2019-09-27", "sendct-2019-12-20", "sendct-2020-03-27", "sendct-2020-06-26",
    "sendct-2020-11-06", "sendct-2020-12-18", "sendct-2021-03-26", "sendct-2021-06-25",
    "sendct-2021-09-24", "sendct-2021-12-17", "sendct-2022-03-25", "sendct-2022-06-24",
    "sendct-2022-09-30", "sendct-2022-12-16", "sendct-2023-03-31", "sendct-2023-06-30",
    "sendct-2023-09-29", "sendct-2023-12-15", "sendct-2024-03-29", "sendct-2024-09-27",
    "sendct-2025-03-28", "sendct-2025-09-26", "tmfct-2024-09-27",
]


async def get_package_ct_info(package: str) -> str:
    """
    Get Package CT Product information from CDISC Library.

    adamct — Controlled terminology for ADaM. cdashct — for CDASH. coact — Clinical Outcome Assessments. ddfct — Data Definition Framework. define-xmlct — Define-XML. glossaryct — CDISC Glossary. mrctct — MRCT. protocolct — protocol-related.

    Args:
        package: The Package CT Product name (e.g. adamct-2014-09-26, cdashct-2016-03-25, sdtmct-2024-03-29, etc.). Must be in the known packages list.

    Returns:
        JSON string containing the Package CT details (codelists/terms with conceptId, submissionValue), or an error message.
    """
    if package not in CT_PACKAGE:
        return f"Error: Package '{package}' is invalid or not found in known packages."
    url = f"{CDISC_API_BASE}/ct/packages/{package}"
    result = await cdisc_get(url, timeout=CT_TIMEOUT)
    if isinstance(result, str):
        return result
    final_data = prune_ct_codelists(result)
    json_str = json.dumps(final_data, separators=(",", ":"))
    return truncate_json_string(json_str, suffix=TRUNCATE_SUFFIX_CT)


async def get_package_ct_codelist_info(package: str, codelist: str) -> str:
    """
    Get a specific Codelist within a Package CT Product from CDISC Library.

    Args:
        package: The Package CT Product name (must be in the known packages list).
        codelist: The codelist identifier (e.g. C103458).

    Returns:
        JSON string containing the Codelist details, or an error message.
    """
    if package not in CT_PACKAGE:
        return f"Error: Package '{package}' is invalid or not found in known packages."
    url = f"{CDISC_API_BASE}/ct/packages/{package}/codelists/{codelist}"
    result = await cdisc_get(url, timeout=CT_TIMEOUT)
    if isinstance(result, str):
        return result
    json_str = json.dumps(result, separators=(",", ":"))
    return truncate_json_string(json_str, suffix=TRUNCATE_SUFFIX_CT)


async def get_package_ct_codelist_term_info(package: str, codelist: str, term: str) -> str:
    """
    Get a specific Term within a Codelist of a Package CT Product from CDISC Library.

    Args:
        package: The Package CT Product name (must be in the known packages list).
        codelist: The codelist identifier (e.g. C103458).
        term: The term identifier (e.g. C103531).

    Returns:
        JSON string containing the Controlled terminology term details, or an error message.
    """
    if package not in CT_PACKAGE:
        return f"Error: Package '{package}' is invalid or not found in known packages."
    url = f"{CDISC_API_BASE}/ct/packages/{package}/codelists/{codelist}/terms/{term}"
    result = await cdisc_get(url, timeout=CT_TIMEOUT)
    if isinstance(result, str):
        return result
    json_str = json.dumps(result, separators=(",", ":"))
    return truncate_json_string(json_str, suffix=TRUNCATE_SUFFIX_CT)
