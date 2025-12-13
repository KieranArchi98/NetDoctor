"""
WHOIS wrapper module.

WHOIS lookups via python-whois or subprocess.
"""

import subprocess
import shutil
from typing import Dict, Any, Optional

# Try to import python-whois, but make it optional
try:
    import whois
    PYTHON_WHOIS_AVAILABLE = True
except ImportError:
    PYTHON_WHOIS_AVAILABLE = False
    whois = None


def query_whois(domain: str) -> Dict[str, Any]:
    """
    Query WHOIS information for a domain.

    Args:
        domain: Domain name to query (e.g., "example.com")

    Returns:
        Dictionary with WHOIS information:
        - raw: Raw WHOIS text output
        - parsed: Parsed information (if python-whois available)
        - method: 'python-whois' or 'subprocess'
        - error: Error message if query failed
    """
    result = {
        "raw": None,
        "parsed": None,
        "method": None,
        "error": None,
    }

    # Try python-whois first if available
    if PYTHON_WHOIS_AVAILABLE:
        try:
            whois_data = whois.whois(domain)
            result["method"] = "python-whois"

            # Extract raw text if available
            if hasattr(whois_data, "text"):
                result["raw"] = whois_data.text
            else:
                # Try to reconstruct from parsed data
                result["raw"] = str(whois_data)

            # Extract parsed information
            parsed_info = {}
            if hasattr(whois_data, "domain_name"):
                parsed_info["domain_name"] = (
                    whois_data.domain_name[0] if isinstance(whois_data.domain_name, list) else whois_data.domain_name
                )
            if hasattr(whois_data, "registrar"):
                parsed_info["registrar"] = whois_data.registrar
            if hasattr(whois_data, "creation_date"):
                parsed_info["creation_date"] = (
                    whois_data.creation_date[0]
                    if isinstance(whois_data.creation_date, list)
                    else whois_data.creation_date
                )
            if hasattr(whois_data, "expiration_date"):
                parsed_info["expiration_date"] = (
                    whois_data.expiration_date[0]
                    if isinstance(whois_data.expiration_date, list)
                    else whois_data.expiration_date
                )
            if hasattr(whois_data, "updated_date"):
                parsed_info["updated_date"] = (
                    whois_data.updated_date[0]
                    if isinstance(whois_data.updated_date, list)
                    else whois_data.updated_date
                )
            if hasattr(whois_data, "name_servers"):
                parsed_info["name_servers"] = (
                    whois_data.name_servers if isinstance(whois_data.name_servers, list) else [whois_data.name_servers]
                )
            if hasattr(whois_data, "status"):
                parsed_info["status"] = (
                    whois_data.status if isinstance(whois_data.status, list) else [whois_data.status]
                )

            result["parsed"] = parsed_info
            return result
        except Exception as e:
            # If python-whois fails, fall back to subprocess
            result["error"] = f"python-whois error: {str(e)}"

    # Fallback to subprocess whois command
    whois_path = shutil.which("whois")
    if not whois_path:
        result["error"] = "WHOIS command not found and python-whois not available"
        return result

    try:
        result["method"] = "subprocess"
        whois_result = subprocess.run(
            [whois_path, domain],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if whois_result.returncode == 0:
            result["raw"] = whois_result.stdout
        else:
            # Some whois servers return non-zero exit codes but still provide data
            if whois_result.stdout:
                result["raw"] = whois_result.stdout
            else:
                result["error"] = f"WHOIS command failed: {whois_result.stderr}"
    except subprocess.TimeoutExpired:
        result["error"] = "WHOIS query timed out"
    except Exception as e:
        result["error"] = f"WHOIS query failed: {str(e)}"

    return result
