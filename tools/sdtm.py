"""SDTM / SEND 相关业务逻辑（SDTMIG、SDTM Model、SENDIG）。"""

from config import CDISC_API_BASE
from utils.http_client import cdisc_get
from utils.formatters import truncate_json_response


SDTMIG_CLASSES = [
    "GeneralObservations", "Interventions", "Events", "Findings", "FindingsAbout",
    "SpecialPurpose", "TrialDesign", "StudyReference", "Relationship",
]
SDTMIG_DATASETS = [
    "AG", "CM", "EC", "EX", "ML", "PR", "SU", "AE", "BE", "CE", "DS", "DV", "HO", "MH",
    "BS", "CP", "DA", "DD", "EG", "FT", "GF", "IE", "IS", "LB", "MB", "MI", "MK", "MS",
    "NV", "OE", "PC", "PE", "PP", "QS", "RE", "RP", "RS", "SC", "SS", "TR", "TU", "UR",
    "VS", "FA", "SR", "CO", "DM", "SE", "SM", "SV", "TA", "TD", "TE", "TI",
]
SDTM_CLASSES = [
    "GeneralObservations", "Interventions", "Events", "Findings", "FindingsAbout",
    "SpecialPurpose", "AssociatedPersons", "TrialDesign", "StudyReference", "Relationship",
]
SDTM_DATASETS = [
    "DM", "CO", "SE", "SJ", "SV", "SM", "TE", "TA", "TX", "TT", "TP", "TV", "TD", "TM",
    "TI", "TS", "AC", "DI", "OI", "RELREC", "SUPPQUAL", "POOLDEF", "RELSUB", "RELREF",
    "DR", "APRELSUB", "RELSPEC",
]
SENDIG_CLASSES = [
    "GeneralObservations", "SpecialPurpose", "Interventions", "Events", "Findings",
    "TrialDesign", "Relationship",
]
SENDIG_DATASETS = [
    "DM", "CO", "SE", "EX", "DS", "BW", "BG", "CL", "DD", "FW", "LB", "MA", "MI", "OM",
    "PM", "PC", "PP", "SC", "TF", "VS", "EG", "CV", "RE", "TE", "TA", "TX", "TS",
    "RELREC", "SUPPQUAL", "POOLDEF",
]


async def get_sdtmig_class_info(version: str, className: str | None = None) -> str:
    """
    Get SDTM Implementation Guide (SDTMIG) Class information or the list of Datasets within a class.

    Use this tool to:
    1. List all available Observation Classes (if className is omitted).
    2. List all Datasets (Domains) contained within a specific Class (e.g., 'Interventions').

    This tool DOES NOT return detailed variables for datasets. It only returns the list/structure. If you want to get the detailed variables for a specific dataset, use `get_sdtmig_dataset_info` tool.

    Args:
        version: The SDTMIG version. all available versions: ["3-1-2", "3-1-3", "3-2", "3-3", "3-4", "ap-1-0", "md-1-0", "md-1-1"].
        className: The name of the SDTMIG Class all available classes: ["GeneralObservations", "Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "TrialDesign", "StudyReference", "Relationship"]. If omitted, returns the list of all available classes for the version.

    Returns:
        JSON string containing the Class details and the list of Datasets it contains, or an error message if the class is not found.
    """
    base_url = f"{CDISC_API_BASE}/sdtmig/{version}/classes"
    if className:
        if className not in SDTMIG_CLASSES:
            return f"Error: className is invalid, got '{className}'"
        url = f"{base_url}/{className}/datasets?expand=false"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_sdtmig_dataset_info(version: str, dataset: str) -> str:
    """
    Get detailed metadata (variables, structure) for a specific SDTMIG Dataset (Domain).

    Use this tool when the user explicitly asks for the detailed variables, structure, or metadata of a specific domain (e.g., "Show me the variables in AE", "What is the structure of DM?").

    Args:
        version: The SDTMIG version. all available versions: ["3-1-2", "3-1-3", "3-2", "3-3", "3-4", "ap-1-0", "md-1-0", "md-1-1"].
        dataset: The 2-character domain code. If omitted, returns the list of all available datasets for the version.

    Returns:
        JSON string containing the detailed variable list and metadata for the requested dataset.
    """
    if dataset not in SDTMIG_DATASETS:
        return f"Error: dataset is invalid, got '{dataset}'"
    url = f"{CDISC_API_BASE}/sdtmig/{version}/datasets/{dataset}"
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_sdtm_model_class_info(version: str, className: str | None = None) -> str:
    """
    Get Study Data Tabulation Model (SDTM) Class from CDISC Library.

    Use this tool to:
    1. List all available SDTM Classes (if className is omitted).
    2. Get detailed definition for a specific Class (e.g., 'Interventions').

    Args:
        version: The SDTM version. Common values: ["1-2", "1-3", "1-4", "1-5", "1-6", "1-7", "1-8", "2-0", "2-1"].
        className: The name of the SDTM Class: ["GeneralObservations", "Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "AssociatedPersons", "TrialDesign", "StudyReference", "Relationship"]. If omitted, returns the list of all available classes for the version.

    Returns:
        JSON string containing the Class details, or an error message if the class is not found.
    """
    base_url = f"{CDISC_API_BASE}/sdtm/{version}/classes"
    if className:
        if className not in SDTM_CLASSES:
            return f"Error: className is invalid, got '{className}'"
        url = f"{base_url}/{className}"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_sdtm_model_dataset_info(version: str, dataset: str | None = None) -> str:
    """
    Get Study Data Tabulation Model (SDTM) Dataset(domains) Definition (Core Metadata) from CDISC Library.

    Use this tool when the user explicitly asks for the detailed variables, structure, or metadata of a specific domain (e.g., "Show me the variables in DM", "What is the structure of RELREC?").

    Args:
        version: The SDTM version. Common values: ["1-2", "1-3", "1-4", "1-5", "1-6", "1-7", "1-8", "2-0", "2-1"].
        dataset: The name of the SDTM Dataset(domains). If omitted, returns the list of all available datasets for the version.

    Returns:
        JSON string containing the SDTM Dataset(domains) definition details, or an error message.
    """
    base_url = f"{CDISC_API_BASE}/sdtm/{version}/datasets"
    if dataset:
        if dataset not in SDTM_DATASETS:
            return f"Error: dataset is invalid, got '{dataset}'"
        url = f"{base_url}/{dataset}"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_sendig_class_info(version: str, className: str | None = None) -> str:
    """
    Get SEND Implementation Guide (SENDIG) Class from CDISC Library.

    Use this tool to:
    1. List all available SENDIG Classes (if className is omitted).
    2. Get detailed definition for a specific Class (e.g., 'Interventions').

    Args:
        version: The SENDIG version. Common values: ["3-0", "3-1-1", "3-1", "ar-1-0", "dart-1-1", "genetox-1-0"].
        className: The name of the SENDIG Class: ["GeneralObservations", "SpecialPurpose", "Interventions", "Events", "Findings", "TrialDesign", "Relationship"]. If omitted, returns the list of all available classes for the version.

    Returns:
        JSON string containing the Class details, or an error message if the class is not found.
    """
    base_url = f"{CDISC_API_BASE}/sendig/{version}/classes"
    if className:
        if className not in SENDIG_CLASSES:
            return f"Error: className is invalid, got '{className}'"
        url = f"{base_url}/{className}"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)


async def get_sendig_dataset_info(version: str, dataset: str | None = None) -> str:
    """
    Get SEND Implementation Guide (SENDIG) Dataset(domains) Definition (Core Metadata) from CDISC Library.

    Use this tool when the user explicitly asks for the detailed variables, structure, or metadata of a specific domain (e.g., "Show me the variables in LB", "What is the structure of DM?").

    Args:
        version: The SENDIG version. Common values: ["3-0", "3-1-1", "3-1", "ar-1-0", "dart-1-1", "genetox-1-0"].
        dataset: The name of the SENDIG Dataset(domains). If omitted, returns the list of all available datasets for the version.

    Returns:
        JSON string containing the SENDIG Dataset(domains) definition details, or an error message.
    """
    base_url = f"{CDISC_API_BASE}/sendig/{version}/datasets"
    if dataset:
        if dataset not in SENDIG_DATASETS:
            return f"Error: dataset is invalid, got '{dataset}'"
        url = f"{base_url}/{dataset}"
    else:
        url = base_url
    result = await cdisc_get(url)
    if isinstance(result, str):
        return result
    return truncate_json_response(result)
