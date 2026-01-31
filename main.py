"""FastMCP quickstart example.

Run from the repository root:
    uv run examples/snippets/servers/fastmcp_quickstart.py
"""


import json
import os
from dotenv import load_dotenv
from io import StringIO
import httpx
import math
import pandas as pd
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
async def get_CDISC_Library_api_product_list() -> str:
    """
    Get the master list of all CDISC Library API products and their available versions.
    
    Use this tool when the user asks about available CDISC standards, supported versions 
    (e.g., "What versions of SDTM are available?"), or wants to explore the catalog.
    
    Returns:
        A JSON string containing the list of products (href, title, type) and their classes.
        """

    api_key = os.getenv("CDISC_API_KEY")

    url = "https://api.library.cdisc.org/api/mdr/products?expand=false"

    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            return json.dumps(data, ensure_ascii=False)
    except httpx.TimeoutException:
            return "Error: The request to CDISC Library timed out. Please try again later."
    except httpx.HTTPStatusError as e:
        return f"API Error: CDISC Library returned status {e.response.status_code}."
    except httpx.RequestError as e:
        return f"Network Error: Unable to connect to CDISC Library. Details: {e}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"
    

@mcp.tool()
async def get_sdtmig_class_info(version: str, className: str = None) -> str:
    """
    Get SDTM Implementation Guide (SDTMIG) Class information or the list of Datasets within a class.
    
    Use this tool to:
    1. List all available Observation Classes (if className is omitted).
    2. List all Datasets (Domains) contained within a specific Class (e.g., 'Interventions').
    
    This tool DOES NOT return detailed variables for datasets. It only returns the list/structure. If you want to get the detailed variables for a specific dataset, use `get_sdtmig_dataset_info` tool.

    Args:
        version: The SDTMIG version. all available versions: ["3-1-2", "3-1-3", "3-2", "3-3", "3-4", "ap-1-0", "md-1-0", "md-1-1"].
        className: The name of the SDTMIG Class all available classes: ["GeneralObservations", "Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "TrialDesign", "StudyReference", "Relationship"].
        If omitted, returns the list of all available classes for the version.

    Returns:
        JSON string containing the Class details and the list of Datasets it contains, or an error message if the class is not found.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."

    base_url = f"https://api.library.cdisc.org/api/mdr/sdtmig/{version}/classes"
    if className:
        if className in ["GeneralObservations", "Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "TrialDesign", "StudyReference", "Relationship"]:
            url = f"{base_url}/{className}/datasets?expand=false"
        else:
            return f"Error: className is invalid, got '{className}'"
    else:
        url = base_url

    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }

    async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=hdr, timeout=15.0)
                response.raise_for_status()
                
                data = response.json()
                if len(json.dumps(data)) > 130000:
                    return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
                else:
                    return json.dumps(data)

            except httpx.HTTPStatusError as e:
                return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
            except httpx.RequestError as e:
                return f"Network Error: {str(e)}"
            except Exception as e:
                return f"Execution Error: {str(e)}"


@mcp.tool()
async def get_sdtmig_dataset_info(version: str, dataset: str) -> str:
    """
    Get detailed metadata (variables, structure) for a specific SDTMIG Dataset (Domain).
    
    Use this tool when the user explicitly asks for the detailed variables, structure, or metadata of a specific domain (e.g., "Show me the variables in AE", "What is the structure of DM?").

    Args:
        version: The SDTMIG version. all available versions: ["3-1-2", "3-1-3", "3-2", "3-3", "3-4", "ap-1-0", "md-1-0", "md-1-1"].
        dataset: The 2-character domain code all available datasets: ["AG", "CM", "EC", "EX", "ML", "PR", "SU", "AE", "BE", "CE", "DS", "DV", "HO", "MH", "BS", "CP", "DA", "DD", "EG",
        "FT", "GF", "IE", "IS", "LB", "MB", "MI", "MK", "MS", "NV", "OE", "PC", "PE", "PP", "QS", "RE", "RP", "RS", "SC", "SS", "TR", "TU", "UR", "VS", "FA", "SR", "CO",
        "DM", "SE", "SM", "SV", "TA", "TD", "TE", "TI"]. 
        If omitted, returns the list of all available datasets for the version.
    Returns:
        JSON string containing the detailed variable list and metadata for the requested dataset.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/sdtmig/{version}/datasets"
    if dataset:
        if dataset in ["AG", "CM", "EC", "EX", "ML", "PR", "SU", "AE", "BE", "CE", "DS", "DV", "HO", "MH", "BS", "CP", "DA", "DD", "EG",
        "FT", "GF", "IE", "IS", "LB", "MB", "MI", "MK", "MS", "NV", "OE", "PC", "PE", "PP", "QS", "RE", "RP", "RS", "SC", "SS", "TR", "TU", "UR", "VS", "FA", "SR", "CO",
        "DM", "SE", "SM", "SV", "TA", "TD", "TE", "TI"]:
            url = f"{base_url}/{dataset}"
        else:
            return f"Error: dataset is invalid, got '{dataset}'"
    else:
        url = base_url

    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }

    async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=hdr, timeout=15.0)
                response.raise_for_status()
                
                data = response.json()
                if len(json.dumps(data)) > 130000:
                    return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
                else:
                    return json.dumps(data)

            except httpx.HTTPStatusError as e:
                return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
            except httpx.RequestError as e:
                return f"Network Error: {str(e)}"
            except Exception as e:
                return f"Execution Error: {str(e)}"



@mcp.tool()
async def get_sdtm_model_class_info(version: str, className: str = None) -> str:
    """
    Get Study Data Tabulation Model (SDTM) Class from CDISC Library.
    
    Use this tool to:
    1. List all available SDTM Classes (if className is omitted).
    2. Get detailed definition for a specific Class (e.g., 'Interventions').
    
    Args:
        version: The SDTM version. Common values: ["1-2", "1-3", "1-4", "1-5", "1-6", "1-7", "1-8", "2-0", "2-1"].
        className: The name of the Study Data Tabulation Model (SDTM) Class:
            ["GeneralObservations", "Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "AssociatedPersons", "TrialDesign", "StudyReference", "Relationship"].
            If omitted, returns the list of all available classes for the version.
    
    Returns:
        JSON string containing the Class details, or an error message if the class is not found.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/sdtm/{version}/classes"
    
    if className:
        if className in ["GeneralObservations", "Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "AssociatedPersons", "TrialDesign", "StudyReference", "Relationship"]:
            url = f"{base_url}/{className}"
        else:
            return f"Error: className is invalid, got '{className}'"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"



@mcp.tool()
async def get_sdtm_model_dataset_info(version: str, dataset: str = None) -> str:
    """
    Get Study Data Tabulation Model (SDTM) Dataset(domains) Definition (Core Metadata) from CDISC Library.
    
    Use this tool when the user explicitly asks for the detailed variables, structure, or metadata of a specific domain (e.g., "Show me the variables in DM", "What is the structure of RELREC?").
    
    Args:
        version: The SDTM version. Common values: ["1-2", "1-3", "1-4", "1-5", "1-6", "1-7", "1-8", "2-0", "2-1"].
        dataset: The name of the Study Data Tabulation Model (SDTM) Dataset(domains):
            ["DM", "CO", "SE", "SJ", "SV", "SM", "TE", "TA", "TX", "TT", "TP", "TV", "TD", "TM", "TI", "TS", "AC", 
            "DI", "OI", "RELREC", "SUPPQUAL", "POOLDEF", "RELSUB", "RELREF", "DR", "APRELSUB", "RELSPEC"].
            If omitted, returns the list of all available datasets for the version.
    
    Returns:
        JSON string containing the Study Data Tabulation Model (SDTM) Dataset(domains) definition details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/sdtm/{version}/datasets"
    
    if dataset:
        if dataset in ["DM", "CO", "SE", "SJ", "SV", "SM", "TE", "TA", "TX", "TT", "TP", "TV", "TD", "TM", "TI", "TS", "AC", 
                    "DI", "OI", "RELREC", "SUPPQUAL", "POOLDEF", "RELSUB", "RELREF", "DR", "APRELSUB", "RELSPEC"]:
            url = f"{base_url}/{dataset}"
        else:
            return f"Error: dataset is invalid, got '{dataset}'"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"



@mcp.tool()
async def get_sendig_class_info(version: str, className: str = None) -> str:
    """
    Get SEND Implementation Guide (SENDIG) Class from CDISC Library.
    
    Use this tool to:
    1. List all available SENDIG Classes (if className is omitted).
    2. Get detailed definition for a specific Class (e.g., 'Interventions').
    
    Args:
        version: The SENDIG version. Common values: ["3-0", "3-1-1", "3-1", "ar-1-0", "dart-1-1", "genetox-1-0"].
        className: The name of the SEND Implementation Guide (SENDIG) Class:
            ["GeneralObservations", "SpecialPurpose", "Interventions", "Events", "Findings", "TrialDesign", "Relationship"].
            If omitted, returns the list of all available classes for the version.
    
    Returns:
        JSON string containing the Class details, or an error message if the class is not found.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/sendig/{version}/classes"
    
    if className:
        if className in ["GeneralObservations", "SpecialPurpose", "Interventions", "Events", "Findings", "TrialDesign", "Relationship"]:
            url = f"{base_url}/{className}"
        else:
            return f"Error: className is invalid, got '{className}'"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


@mcp.tool()
async def get_sendig_dataset_info(version: str, dataset: str = None) -> str:
    """
    Get SEND Implementation Guide (SENDIG) Dataset(domains) Definition (Core Metadata) from CDISC Library.
    
    Use this tool when the user explicitly asks for the detailed variables, structure, or metadata of a specific domain (e.g., "Show me the variables in LB", "What is the structure of DM?").
    
    Args:
        version: The SENDIG version. Common values: ["3-0", "3-1-1", "3-1", "ar-1-0", "dart-1-1", "genetox-1-0"].
        dataset: The name of the SEND Implementation Guide (SENDIG) Dataset(domains):
            ["DM", "CO", "SE", "EX", "DS", "BW", "BG", "CL", "DD", "FW", "LB", "MA", "MI", "OM", "PM", "PC", "PP", 
            "SC", "TF", "VS", "EG", "CV", "RE", "TE", "TA", "TX", "TS", "RELREC", "SUPPQUAL", "POOLDEF"].
            If omitted, returns the list of all available datasets for the version.
    
    Returns:
        JSON string containing the SEND Implementation Guide (SENDIG) Dataset(domains) definition details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/sendig/{version}/datasets"
    
    if dataset:
        if dataset in ["DM", "CO", "SE", "EX", "DS", "BW", "BG", "CL", "DD", "FW", "LB", "MA", "MI", "OM", "PM", "PC", "PP", 
            "SC", "TF", "VS", "EG", "CV", "RE", "TE", "TA", "TX", "TS", "RELREC", "SUPPQUAL", "POOLDEF"]:
            url = f"{base_url}/{dataset}"
        else:
            return f"Error: dataset is invalid, got '{dataset}'"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


@mcp.tool()
async def get_cdashig_class_info(version: str, className: str = None) -> str:
    """
    Get CDASH Implementation Guide (CDASHIG) Classes from CDISC Library.
    
    Use this tool to:
    1. List all available CDASHIG Classes (if className is omitted).
    2. Get detailed definition for a specific Class (e.g., 'Interventions').
    
    Args:
        version: The CDASHIG version. Common values: ["1-1-1", "2-0", "2-1", "2-2", "2-3"].
        className: The name of the CDASH Implementation Guide (CDASHIG) Class:
            ["Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose"].
            If omitted, returns the list of all available classes for the version.
    
    Returns:
        JSON string containing the CDASH Implementation Guide (CDASHIG) Class details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/cdashig/{version}/classes"
    
    if className:
        if className in ["Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose"]:
            url = f"{base_url}/{className}/domains"
        else:
            return f"Error: className is invalid, got '{className}'"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


@mcp.tool()
async def get_cdashig_domain_info(version: str, domains: str = None) -> str:
    """
    Get CDASH Implementation Guide (CDASHIG) Domains from CDISC Library.
    
    Use this tool to:
    1. List all available CDASHIG Domains (if domains is omitted).
    2. Get detailed definition for a specific Domain (e.g., 'AG').
    
    Args:
        version: The CDASHIG version. Common values: ["1-1-1", "2-0", "2-1", "2-2", "2-3"].
        domains: The name of the CDASH Implementation Guide (CDASHIG) Domain:
            ["AG", "CM", "EC", "EX", "ML", "PR", "SU", "AE", "CE", "DS", "DV", "HO", "MH", "SA", "CP", "CV", "DA", "DD", "EG", "GF", "IE",
             "LB", "MB", "MI", "MK", "MS", "NV", "OE", "PC", "PE", "RE", "RP", "RS", "SC", "TR", "TU", "UR", "VS", "FA", "SR", "CO", "DM"].
            If omitted, returns the list of all available domains for the version.
    
    Returns:
        JSON string containing the CDASH Implementation Guide (CDASHIG) Domain details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/cdashig/{version}/domains"
    
    if domains:
        if domains in ["AG", "CM", "EC", "EX", "ML", "PR", "SU", "AE", "CE", "DS", "DV", "HO", "MH", "SA", "CP", "CV", "DA", "DD", "EG", "GF", "IE",
             "LB", "MB", "MI", "MK", "MS", "NV", "OE", "PC", "PE", "RE", "RP", "RS", "SC", "TR", "TU", "UR", "VS", "FA", "SR", "CO", "DM"]:
            url = f"{base_url}/{domains}"
        else:
            return f"Error: domains is invalid, got '{domains}'"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


@mcp.tool()
async def get_cdashig_scenarios_info(version: str, scenario: str = None) -> str:
    """
    Get CDASH Implementation Guide (CDASHIG) Scenarios from CDISC Library.
    
    Use this tool to:
    1. List all available CDASHIG Scenarios (if scenario is omitted).
    2. Get detailed definition for a specific Scenario (e.g., 'DS', "AE", "SAE").
    
    Args:
        version: The CDASHIG version. Common values: ["1-1-1", "2-0", "2-1", "2-2", "2-3"].
        scenario: The name of the CDASH Implementation Guide (CDASHIG) Scenario.
            If omitted, returns the list of all available scenarios for the version.
    
    Returns:
        JSON string containing the CDASH Implementation Guide (CDASHIG) Scenario details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/cdashig/{version}/scenarios"
    
    if scenario:
        url = f"{base_url}/{scenario}"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


@mcp.tool()
async def get_cdash_model_class_info(version: str, className: str = None) -> str:
    """
    Get CDASH Model Class from CDISC Library.
    
    Use this tool to:
    1. List all available CDASH Model Class (if className is omitted).
    2. Get detailed definition for a specific Class (e.g., 'Interventions').
    
    Args:
        version: The CDASH Model version. Common values: ["1-0", "1-1", "1-2", "1-3"].
        className: The name of the CDASH Model Class.
            ["Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "Identifiers", "AssociatedPersonsIdentifiers", "Timing"].
            If omitted, returns the list of all available classes for the version.
    
    Returns:
        JSON string containing the CDASH Model Class details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/cdash/{version}/classes"
    
    if className:
        if className in ["Interventions", "Events", "Findings", "FindingsAbout", "SpecialPurpose", "Identifiers", "AssociatedPersonsIdentifiers", "Timing"]:
            url = f"{base_url}/{className}"
        else:
            return f"Error: className is invalid, got '{className}'"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


@mcp.tool()
async def get_cdash_model_domain_info(version: str, domain: str = None) -> str:
    """
    Get CDASH Model Domain from CDISC Library.
    
    Use this tool to:
    1. List all available CDASH Model Domain (if domain is omitted).
    2. Get detailed definition for a specific Domain (e.g., 'AG').
    
    Args:
        version: The CDASH Model version. Common values: ["1-0", "1-1", "1-2", "1-3"].
        domain: The name of the CDASH Model Domain: ["AE", "CO", "DM", "DS", "MH", "MS"].
            If omitted, returns the list of all available domains for the version.
    
    Returns:
        JSON string containing the CDASH Model Domain details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    base_url = f"https://api.library.cdisc.org/api/mdr/cdash/{version}/domains"
    
    if domain:
        if domain in ["AE", "CO", "DM", "DS", "MH", "MS"]:
            url = f"{base_url}/{domain}"
        else:
            return f"Error: domain is invalid, got '{domain}'"
    else:
        url = base_url
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            data = response.json()
            if len(json.dumps(data)) > 130000:
                return json.dumps(data[:130000]) + "..." + "The data is too long, please shorten the request."
            else:
                return json.dumps(data)
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


def remove_all_analysis_variables(obj):
    """删除所有 analysisVariables 里面的内容（清空该层级）"""
    if isinstance(obj, dict):
        if 'analysisVariables' in obj:
            obj['analysisVariables'] = []
        for k, v in obj.items():
            remove_all_analysis_variables(v)
    elif isinstance(obj, list):
        for item in obj:
            remove_all_analysis_variables(item)


@mcp.tool()
async def get_adam_product_info(product: str) -> str:
    """
    Get ADAM Product and Datastructures information from CDISC Library.
    Use this tool to get ADAM product data, and datastructures information.
    
    Args:
        product: The ADAM product type. Common values:
            - "adam-2-1" (Analysis Data Model Version 2.1)
            - "adam-adae-1-0" (ADaM Data Structure for Adverse Event Analysis Version 1.0)
            - "adam-md-1-0" (ADaM Implementation Guide for Medical Devices v1.0)
            - "adam-nca-1-0" (ADaM Implementation Guide for Non-compartmental Analysis)
            - "adam-occds-1-0" (ADaM Structure for Occurrence Data Version 1.0)
            - "adam-occds-1-1" (ADaM Structure for Occurrence Data Version 1.1)
            - "adam-poppk-1-0" (Basic Data Structure for Population Pharmacokinetic Analysis)
            - "adam-tte-1-0" (ADaM Basic Data Structure for Time-to-Event Analyses Version 1.0)
            - "adamig-1-0" (Analysis Data Model Implementation Guide Version 1.0)
            - "adamig-1-1" (Analysis Data Model Implementation Guide Version 1.1)
            - "adamig-1-2" (Analysis Data Model Implementation Guide Version 1.2)
            - "adamig-1-3" (Analysis Data Model Implementation Guide Version 1.3)
    
    Returns:
        JSON string containing the ADAM product details and datastructures information, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    url = f"https://api.library.cdisc.org/api/mdr/adam/{product}"
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            json_data = response.json()
            # 删除所有 analysisVariables 的内容
            remove_all_analysis_variables(json_data)
            
            result = json.dumps(json_data)
            if len(result) > 130000:
                return result[:130000] + "..." + "The data is too long, please shorten the request."
            else:
                return result
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"



ALLOWED_adam_datastructure_combinations = {
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
    "adamig-1-3": ["ADSL", "BDS", "TTE"]
}

def remove_links_parent_refs(obj, parent_key=None):
    """只保留 analysisVariables 层级里每个元素的 _links 的 self，其他键都删除"""
    if isinstance(obj, dict):
        if parent_key == 'analysisVariables' and '_links' in obj and isinstance(obj['_links'], dict):
            links = obj['_links']
            if 'self' in links:
                obj['_links'] = {'self': links['self']}
            else:
                obj['_links'] = {}
        for k, v in obj.items():
            remove_links_parent_refs(v, k)
    elif isinstance(obj, list):
        for item in obj:
            remove_links_parent_refs(item, parent_key)

@mcp.tool()
async def get_adam_datastructure_info(product: str, datastructure: str) -> str:
    """
    Get ADAM Datastructure information from CDISC Library.
    Use this tool to get specific ADAM datastructure data.
    
    Args:
        product: The ADAM product type. Valid values:
            - "adam-nca-1-0" (with datastructure: ADNCA)
            - "adamig-1-0" (with datastructures: ADSL, BDS)
            - "adamig-1-1" (with datastructures: ADSL, BDS)
            - "adam-occds-1-0" (with datastructure: OCCDS)
            - "adam-occds-1-1" (with datastructures: OCCDS, AE)
            - "adam-adae-1-0" (with datastructure: ADAE)
            - "adam-poppk-1-0" (with datastructure: ADPPK)
            - "adam-tte-1-0" (with datastructure: ADTTE)
            - "adamig-1-2" (with datastructures: ADSL, BDS)
            - "adam-md-1-0" (with datastructures: ADDL, MDOCCDS, MDBDS, MDTTE)
            - "adamig-1-3" (with datastructures: ADSL, BDS, TTE)
        datastructure: The datastructure name. Must be a valid combination with the product.
    
    Returns:
        JSON string containing the ADAM datastructure details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    # validate product and datastructure combination
    if product not in ALLOWED_adam_datastructure_combinations:
        valid_products = ", ".join(ALLOWED_adam_datastructure_combinations.keys())
        return f"Error: Invalid product '{product}'. Valid products are: {valid_products}"
    
    if datastructure not in ALLOWED_adam_datastructure_combinations[product]:
        valid_datastructures = ", ".join(ALLOWED_adam_datastructure_combinations[product])
        return f"Error: Invalid datastructure '{datastructure}' for product '{product}'. Valid datastructures are: {valid_datastructures}"
    
    url = f"https://api.library.cdisc.org/api/mdr/adam/{product}/datastructures/{datastructure}"
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            json_data = response.json()
            remove_links_parent_refs(json_data)
            result = json.dumps(json_data)
            if len(result) > 130000:
                return result[:130000] + "..." + "The data is too long, please shorten the request."
            else:
                return result
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


ALLOWED_qrs_combinations = {
    "AIMS01": ["2-0"],
    "APCH1": ["1-0"],
    "ATLAS1": ["1-0"],
    "CGI02": ["2-1"],
    "HAMA1": ["2-1"],
    "KFSS1": ["2-0"],
    "KPSS1": ["2-0"],
    "PGI01": ["1-1"],
    "SIXMW1": ["1-0"],
}

@mcp.tool()
async def get_qrs_info(instrument: str, version: str) -> str:
    """
    Get QRS Instrument Product information from CDISC Library.
    Use this tool to get specific QRS Instrument Product data.
    
    Args:
        instrument: The QRS Instrument name. Valid values:
            - "AIMS01" (with version: 2-0)
            - "APCH1" (with version: 1-0)
            - "ATLAS1" (with version: 1-0)
            - "CGI02" (with version: 2-1)
            - "HAMA1" (with version: 2-1)
            - "KFSS1" (with version: 2-0)
            - "KPSS1" (with version: 2-0)
            - "PGI01" (with version: 1-1)
            - "SIXMW1" (with version: 1-0)
    
    Returns:
        JSON string containing the QRS Instrument Product details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
    # validate product and datastructure combination
    if instrument not in ALLOWED_qrs_combinations:
        valid_instruments = ", ".join(ALLOWED_qrs_combinations.keys())
        return f"Error: Invalid instrument '{instrument}'. Valid instruments are: {valid_instruments}"
    
    if version not in ALLOWED_qrs_combinations[instrument]:
        valid_versions = ", ".join(ALLOWED_qrs_combinations[instrument])
        return f"Error: Invalid version '{version}' for instrument '{instrument}'. Valid versions are: {valid_versions}"
    
    url = f"https://api.library.cdisc.org/api/mdr/qrs/instruments/{instrument}/versions/{version}"
    
    hdr = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=hdr, timeout=15.0)
            response.raise_for_status()
            
            json_data = response.json()
            result = json.dumps(json_data)
            if len(result) > 130000:
                return result[:130000] + "..." + "The data is too long, please shorten the request."
            else:
                return result
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"



ct_package = ['adamct-2014-09-26', 'adamct-2015-12-18', 'adamct-2016-03-25', 'adamct-2016-09-30', 'adamct-2016-12-16', 'adamct-2017-03-31', 'adamct-2017-09-29', 
        'adamct-2018-12-21', 'adamct-2019-03-29', 'adamct-2019-12-20', 'adamct-2020-03-27', 'adamct-2020-06-26', 'adamct-2020-11-06', 'adamct-2021-12-17', 
        'adamct-2022-06-24', 'adamct-2023-03-31', 'adamct-2023-06-30', 'adamct-2024-03-29', 'adamct-2024-09-27', 'adamct-2025-03-28', 'adamct-2025-09-26', 
        'cdashct-2014-09-26', 'cdashct-2015-03-27', 'cdashct-2016-03-25', 'cdashct-2016-09-30', 'cdashct-2016-12-16', 'cdashct-2017-09-29', 'cdashct-2018-03-30', 
        'cdashct-2018-06-29', 'cdashct-2018-09-28', 'cdashct-2018-12-21', 'cdashct-2019-03-29', 'cdashct-2019-06-28', 'cdashct-2019-12-20', 'cdashct-2020-11-06', 
        'cdashct-2020-12-18', 'cdashct-2021-03-26', 'cdashct-2021-06-25', 'cdashct-2021-09-24', 'cdashct-2021-12-17', 'cdashct-2022-06-24', 'cdashct-2022-09-30', 
        'cdashct-2022-12-16', 'cdashct-2024-09-27', 'cdashct-2025-03-28', 'coact-2014-12-19', 'coact-2015-03-27', 'ddfct-2022-09-30', 'ddfct-2022-12-16', 
        'ddfct-2023-03-31', 'ddfct-2023-06-30', 'ddfct-2023-09-29', 'ddfct-2023-12-15', 'ddfct-2024-03-29', 'ddfct-2024-09-27', 'ddfct-2025-09-26', 
        'define-xmlct-2019-12-20', 'define-xmlct-2020-03-27', 'define-xmlct-2020-06-26', 'define-xmlct-2020-11-06', 'define-xmlct-2020-12-18', 
        'define-xmlct-2021-03-26', 'define-xmlct-2021-06-25', 'define-xmlct-2021-09-24', 'define-xmlct-2021-12-17', 'define-xmlct-2022-09-30', 'define-xmlct-2022-12-16', 
        'define-xmlct-2023-06-30', 'define-xmlct-2023-12-15', 'define-xmlct-2024-03-29', 'define-xmlct-2024-09-27', 'define-xmlct-2025-03-28', 'define-xmlct-2025-09-26', 
        'glossaryct-2020-12-18', 'glossaryct-2021-12-17', 'glossaryct-2022-12-16', 'glossaryct-2023-12-15', 'glossaryct-2024-09-27', 'glossaryct-2025-09-26', 
        'mrctct-2024-03-29', 'mrctct-2024-09-27', 'mrctct-2025-09-26', 'protocolct-2017-03-31', 'protocolct-2017-06-30', 'protocolct-2017-09-29', 
        'protocolct-2018-03-30', 'protocolct-2018-06-29', 'protocolct-2018-09-28', 'protocolct-2019-03-29', 'protocolct-2019-06-28', 'protocolct-2019-09-27', 
        'protocolct-2019-12-20', 'protocolct-2020-03-27', 'protocolct-2020-06-26', 'protocolct-2020-11-06', 'protocolct-2020-12-18', 'protocolct-2021-03-26', 
        'protocolct-2021-06-25', 'protocolct-2021-09-24', 'protocolct-2021-12-17', 'protocolct-2022-03-25', 'protocolct-2022-06-24', 'protocolct-2022-09-30', 
        'protocolct-2022-12-16', 'protocolct-2023-03-31', 'protocolct-2023-06-30', 'protocolct-2023-09-29', 'protocolct-2023-12-15', 'protocolct-2024-03-29', 
        'protocolct-2024-09-27', 'protocolct-2025-03-28', 'protocolct-2025-09-26', 'qrsct-2015-06-26', 'qrsct-2015-09-25', 'qs-ftct-2014-09-26', 
        'sdtmct-2014-09-26', 'sdtmct-2014-12-19', 'sdtmct-2015-03-27', 'sdtmct-2015-06-26', 'sdtmct-2015-09-25', 'sdtmct-2015-12-18', 'sdtmct-2016-03-25', 
        'sdtmct-2016-06-24', 'sdtmct-2016-09-30', 'sdtmct-2016-12-16', 'sdtmct-2017-03-31', 'sdtmct-2017-06-30', 'sdtmct-2017-09-29', 'sdtmct-2017-12-22', 
        'sdtmct-2018-03-30', 'sdtmct-2018-06-29', 'sdtmct-2018-09-28', 'sdtmct-2018-12-21', 'sdtmct-2019-03-29', 'sdtmct-2019-06-28', 'sdtmct-2019-09-27', 
        'sdtmct-2019-12-20', 'sdtmct-2020-03-27', 'sdtmct-2020-06-26', 'sdtmct-2020-11-06', 'sdtmct-2020-12-18', 'sdtmct-2021-03-26', 'sdtmct-2021-06-25', 
        'sdtmct-2021-09-24', 'sdtmct-2021-12-17', 'sdtmct-2022-03-25', 'sdtmct-2022-06-24', 'sdtmct-2022-09-30', 'sdtmct-2022-12-16', 'sdtmct-2023-03-31', 
        'sdtmct-2023-06-30', 'sdtmct-2023-09-29', 'sdtmct-2023-12-15', 'sdtmct-2024-03-29', 'sdtmct-2024-09-27', 'sdtmct-2025-03-28', 'sdtmct-2025-09-26', 
        'sendct-2014-09-26', 'sendct-2014-12-19', 'sendct-2015-03-27', 'sendct-2015-06-26', 'sendct-2015-09-25', 'sendct-2015-12-18', 'sendct-2016-03-25', 
        'sendct-2016-06-24', 'sendct-2016-09-30', 'sendct-2016-12-16', 'sendct-2017-03-31', 'sendct-2017-06-30', 'sendct-2017-09-29', 'sendct-2017-12-22', 
        'sendct-2018-03-30', 'sendct-2018-06-29', 'sendct-2018-09-28', 'sendct-2018-12-21', 'sendct-2019-03-29', 'sendct-2019-06-28', 'sendct-2019-09-27', 
        'sendct-2019-12-20', 'sendct-2020-03-27', 'sendct-2020-06-26', 'sendct-2020-11-06', 'sendct-2020-12-18', 'sendct-2021-03-26', 'sendct-2021-06-25', 
        'sendct-2021-09-24', 'sendct-2021-12-17', 'sendct-2022-03-25', 'sendct-2022-06-24', 'sendct-2022-09-30', 'sendct-2022-12-16', 'sendct-2023-03-31', 
        'sendct-2023-06-30', 'sendct-2023-09-29', 'sendct-2023-12-15', 'sendct-2024-03-29', 'sendct-2024-09-27', 'sendct-2025-03-28', 'sendct-2025-09-26', 
        'tmfct-2024-09-27']

@mcp.tool()
async def get_package_ct_info(package: str) -> str:
    """
    Get Package CT Product information from CDISC Library.

    adamct — Controlled terminology providing standardized codelists for the CDISC Analysis Data Model (ADaM) datasets and variables.
    cdashct — Controlled terminology subset supporting the CDASH standard for standardized clinical data collection and CRF/eCRF design.
    coact — Controlled terminology for Clinical Outcome Assessments (including questionnaires, clinician and observer-reported outcomes) used in CDISC submissions.
    ddfct — Controlled terminology for the Data Definition Framework (DDF) that defines metadata and attributes for study data definitions under USDM/Define-XML.
    define-xmlct — Controlled terminology that defines standard values used in Define-XML documents to describe CDISC datasets and their metadata.
    glossaryct — Controlled terminology that standardizes CDISC Glossary terms, codes, and definitions for consistent use across standards and documentation.
    mrctct — Controlled terminology based on the Multi-Regional Clinical Trial (MRCT) Center’s plain-language clinical research glossary to support clear communication and health literacy.
    protocolct — Controlled terminology for protocol-related entities and attributes, such as epochs, arms, elements, and other study design constructs.

    Args:
        package: The Package CT Product name. Valid values:
        ['adamct-2014-09-26', 'adamct-2015-12-18', 'adamct-2016-03-25', 'adamct-2016-09-30', 'adamct-2016-12-16', 'adamct-2017-03-31', 'adamct-2017-09-29', 
        'adamct-2018-12-21', 'adamct-2019-03-29', 'adamct-2019-12-20', 'adamct-2020-03-27', 'adamct-2020-06-26', 'adamct-2020-11-06', 'adamct-2021-12-17', 
        'adamct-2022-06-24', 'adamct-2023-03-31', 'adamct-2023-06-30', 'adamct-2024-03-29', 'adamct-2024-09-27', 'adamct-2025-03-28', 'adamct-2025-09-26', 
        'cdashct-2014-09-26', 'cdashct-2015-03-27', 'cdashct-2016-03-25', 'cdashct-2016-09-30', 'cdashct-2016-12-16', 'cdashct-2017-09-29', 'cdashct-2018-03-30', 
        'cdashct-2018-06-29', 'cdashct-2018-09-28', 'cdashct-2018-12-21', 'cdashct-2019-03-29', 'cdashct-2019-06-28', 'cdashct-2019-12-20', 'cdashct-2020-11-06', 
        'cdashct-2020-12-18', 'cdashct-2021-03-26', 'cdashct-2021-06-25', 'cdashct-2021-09-24', 'cdashct-2021-12-17', 'cdashct-2022-06-24', 'cdashct-2022-09-30', 
        'cdashct-2022-12-16', 'cdashct-2024-09-27', 'cdashct-2025-03-28', 'coact-2014-12-19', 'coact-2015-03-27', 'ddfct-2022-09-30', 'ddfct-2022-12-16', 
        'ddfct-2023-03-31', 'ddfct-2023-06-30', 'ddfct-2023-09-29', 'ddfct-2023-12-15', 'ddfct-2024-03-29', 'ddfct-2024-09-27', 'ddfct-2025-09-26', 
        'define-xmlct-2019-12-20', 'define-xmlct-2020-03-27', 'define-xmlct-2020-06-26', 'define-xmlct-2020-11-06', 'define-xmlct-2020-12-18', 
        'define-xmlct-2021-03-26', 'define-xmlct-2021-06-25', 'define-xmlct-2021-09-24', 'define-xmlct-2021-12-17', 'define-xmlct-2022-09-30', 'define-xmlct-2022-12-16', 
        'define-xmlct-2023-06-30', 'define-xmlct-2023-12-15', 'define-xmlct-2024-03-29', 'define-xmlct-2024-09-27', 'define-xmlct-2025-03-28', 'define-xmlct-2025-09-26', 
        'glossaryct-2020-12-18', 'glossaryct-2021-12-17', 'glossaryct-2022-12-16', 'glossaryct-2023-12-15', 'glossaryct-2024-09-27', 'glossaryct-2025-09-26', 
        'mrctct-2024-03-29', 'mrctct-2024-09-27', 'mrctct-2025-09-26', 'protocolct-2017-03-31', 'protocolct-2017-06-30', 'protocolct-2017-09-29', 
        'protocolct-2018-03-30', 'protocolct-2018-06-29', 'protocolct-2018-09-28', 'protocolct-2019-03-29', 'protocolct-2019-06-28', 'protocolct-2019-09-27', 
        'protocolct-2019-12-20', 'protocolct-2020-03-27', 'protocolct-2020-06-26', 'protocolct-2020-11-06', 'protocolct-2020-12-18', 'protocolct-2021-03-26', 
        'protocolct-2021-06-25', 'protocolct-2021-09-24', 'protocolct-2021-12-17', 'protocolct-2022-03-25', 'protocolct-2022-06-24', 'protocolct-2022-09-30', 
        'protocolct-2022-12-16', 'protocolct-2023-03-31', 'protocolct-2023-06-30', 'protocolct-2023-09-29', 'protocolct-2023-12-15', 'protocolct-2024-03-29', 
        'protocolct-2024-09-27', 'protocolct-2025-03-28', 'protocolct-2025-09-26', 'qrsct-2015-06-26', 'qrsct-2015-09-25', 'qs-ftct-2014-09-26', 
        'sdtmct-2014-09-26', 'sdtmct-2014-12-19', 'sdtmct-2015-03-27', 'sdtmct-2015-06-26', 'sdtmct-2015-09-25', 'sdtmct-2015-12-18', 'sdtmct-2016-03-25', 
        'sdtmct-2016-06-24', 'sdtmct-2016-09-30', 'sdtmct-2016-12-16', 'sdtmct-2017-03-31', 'sdtmct-2017-06-30', 'sdtmct-2017-09-29', 'sdtmct-2017-12-22', 
        'sdtmct-2018-03-30', 'sdtmct-2018-06-29', 'sdtmct-2018-09-28', 'sdtmct-2018-12-21', 'sdtmct-2019-03-29', 'sdtmct-2019-06-28', 'sdtmct-2019-09-27', 
        'sdtmct-2019-12-20', 'sdtmct-2020-03-27', 'sdtmct-2020-06-26', 'sdtmct-2020-11-06', 'sdtmct-2020-12-18', 'sdtmct-2021-03-26', 'sdtmct-2021-06-25', 
        'sdtmct-2021-09-24', 'sdtmct-2021-12-17', 'sdtmct-2022-03-25', 'sdtmct-2022-06-24', 'sdtmct-2022-09-30', 'sdtmct-2022-12-16', 'sdtmct-2023-03-31', 
        'sdtmct-2023-06-30', 'sdtmct-2023-09-29', 'sdtmct-2023-12-15', 'sdtmct-2024-03-29', 'sdtmct-2024-09-27', 'sdtmct-2025-03-28', 'sdtmct-2025-09-26', 
        'sendct-2014-09-26', 'sendct-2014-12-19', 'sendct-2015-03-27', 'sendct-2015-06-26', 'sendct-2015-09-25', 'sendct-2015-12-18', 'sendct-2016-03-25', 
        'sendct-2016-06-24', 'sendct-2016-09-30', 'sendct-2016-12-16', 'sendct-2017-03-31', 'sendct-2017-06-30', 'sendct-2017-09-29', 'sendct-2017-12-22', 
        'sendct-2018-03-30', 'sendct-2018-06-29', 'sendct-2018-09-28', 'sendct-2018-12-21', 'sendct-2019-03-29', 'sendct-2019-06-28', 'sendct-2019-09-27', 
        'sendct-2019-12-20', 'sendct-2020-03-27', 'sendct-2020-06-26', 'sendct-2020-11-06', 'sendct-2020-12-18', 'sendct-2021-03-26', 'sendct-2021-06-25', 
        'sendct-2021-09-24', 'sendct-2021-12-17', 'sendct-2022-03-25', 'sendct-2022-06-24', 'sendct-2022-09-30', 'sendct-2022-12-16', 'sendct-2023-03-31', 
        'sendct-2023-06-30', 'sendct-2023-09-29', 'sendct-2023-12-15', 'sendct-2024-03-29', 'sendct-2024-09-27', 'sendct-2025-03-28', 'sendct-2025-09-26', 
        'tmfct-2024-09-27']
    
    Returns:
        JSON string containing the CDASH Model Domain details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
            
    # 1. 检查 package 是否在允许列表中 (依赖上下文中的 ct_package)
    if package not in ct_package:
        return f"Error: Package '{package}' is invalid or not found in known packages."

    base_url = f"https://api.library.cdisc.org/api/mdr/ct/packages/{package}"
    
    # 2. 设置 Headers
    headers = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, headers=headers, timeout=30.0)
            response.raise_for_status()
            raw_data = response.json()
            
            # --- 数据瘦身逻辑 (Data Minification) ---
            # 仅提取 codelists 和 terms 中的核心字段 (conceptId, submissionValue)
            minimized_codelists = []
            
            for cl in raw_data.get("codelists", []):
                clean_cl = {
                    "conceptId": cl.get("conceptId"),
                    "submissionValue": cl.get("submissionValue"),
                    # "definition": cl.get("definition"),
                    "terms": []
                }
                # 处理该 codelist 下的 terms
                if "terms" in cl:
                    for term in cl["terms"]:
                        clean_cl["terms"].append({
                            "conceptId": term.get("conceptId"),
                            "submissionValue": term.get("submissionValue"),
                            # "definition": term.get("definition")
                        })
                
                minimized_codelists.append(clean_cl)
            
            final_data = {"codelists": minimized_codelists}
            # --------------------------------------
            json_str = json.dumps(final_data, separators=(',', ':'))

            if len(json_str) > 130000:
                return json_str[:130000] + "\n... [Truncated]"
            else:
                return json_str
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"



@mcp.tool()
async def get_package_ct_codelist_info(package: str, codelist: str) -> str:
    """
    Get Package CT Product information from CDISC Library.

    adamct — Controlled terminology providing standardized codelists for the CDISC Analysis Data Model (ADaM) datasets and variables.
    cdashct — Controlled terminology subset supporting the CDASH standard for standardized clinical data collection and CRF/eCRF design.
    coact — Controlled terminology for Clinical Outcome Assessments (including questionnaires, clinician and observer-reported outcomes) used in CDISC submissions.
    ddfct — Controlled terminology for the Data Definition Framework (DDF) that defines metadata and attributes for study data definitions under USDM/Define-XML.
    define-xmlct — Controlled terminology that defines standard values used in Define-XML documents to describe CDISC datasets and their metadata.
    glossaryct — Controlled terminology that standardizes CDISC Glossary terms, codes, and definitions for consistent use across standards and documentation.
    mrctct — Controlled terminology based on the Multi-Regional Clinical Trial (MRCT) Center’s plain-language clinical research glossary to support clear communication and health literacy.
    protocolct — Controlled terminology for protocol-related entities and attributes, such as epochs, arms, elements, and other study design constructs.

    Args:
        package: The Package CT Product name. Valid values:
        ['adamct-2014-09-26', 'adamct-2015-12-18', 'adamct-2016-03-25', 'adamct-2016-09-30', etc.]
    
    Returns:
        JSON string containing the CDASH Model Domain details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
            
    # 1. 检查 package 是否在允许列表中 (依赖上下文中的 ct_package)
    if package not in ct_package:
        return f"Error: Package '{package}' is invalid or not found in known packages."

    base_url = f"https://api.library.cdisc.org/api/mdr/ct/packages/{package}/codelists/{codelist}"

    
    # 2. 设置 Headers
    headers = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            # --------------------------------------
            json_str = json.dumps(data, separators=(',', ':'))

            if len(json_str) > 130000:
                return json_str[:130000] + "\n... [Truncated]"
            else:
                return json_str
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"


@mcp.tool()
async def get_package_ct_codelist_term_info(package: str, codelist: str, term: str) -> str:
    """
    Get Package CT Product information from CDISC Library.

    adamct — Controlled terminology providing standardized codelists for the CDISC Analysis Data Model (ADaM) datasets and variables.
    cdashct — Controlled terminology subset supporting the CDASH standard for standardized clinical data collection and CRF/eCRF design.
    coact — Controlled terminology for Clinical Outcome Assessments (including questionnaires, clinician and observer-reported outcomes) used in CDISC submissions.
    ddfct — Controlled terminology for the Data Definition Framework (DDF) that defines metadata and attributes for study data definitions under USDM/Define-XML.
    define-xmlct — Controlled terminology that defines standard values used in Define-XML documents to describe CDISC datasets and their metadata.
    glossaryct — Controlled terminology that standardizes CDISC Glossary terms, codes, and definitions for consistent use across standards and documentation.
    mrctct — Controlled terminology based on the Multi-Regional Clinical Trial (MRCT) Center’s plain-language clinical research glossary to support clear communication and health literacy.
    protocolct — Controlled terminology for protocol-related entities and attributes, such as epochs, arms, elements, and other study design constructs.

    Args:
        package: The Package CT Product name. Valid values:
        ['adamct-2014-09-26', 'adamct-2015-12-18', 'adamct-2016-03-25', 'adamct-2016-09-30', etc.]
        codelist: The codelist name. Valid values:
        ['C103458', etc.]
        term: The term name. Valid values:
        ['C103531', etc.]
    
    Returns:
        JSON string containing the Controlled terminology details, or an error message.
    """
    api_key = os.getenv("CDISC_API_KEY")
    if not api_key:
        return "Error: CDISC_API_KEY environment variable not found."
    
            
    # 1. 检查 package 是否在允许列表中 (依赖上下文中的 ct_package)
    if package not in ct_package:
        return f"Error: Package '{package}' is invalid or not found in known packages."

    base_url = f"https://api.library.cdisc.org/api/mdr/ct/packages/{package}/codelists/{codelist}/terms/{term}"

    
    # 2. 设置 Headers
    headers = {
        'Cache-Control': 'no-cache',
        'api-key': api_key,
        'Accept': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            # --------------------------------------
            json_str = json.dumps(data, separators=(',', ':'))

            if len(json_str) > 130000:
                return json_str[:130000] + "\n... [Truncated]"
            else:
                return json_str
        
        except httpx.HTTPStatusError as e:
            return f"API Error: HTTP {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Execution Error: {str(e)}"



# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")