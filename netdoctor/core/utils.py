"""
Runtime detection utilities for optional dependencies and external tools.
"""

import shutil
import subprocess
import re
import importlib
from typing import Dict, Any, Optional

def check_python_dependency(name: str) -> Dict[str, Any]:
    """
    Check if a Python package is installed.
    
    Args:
        name: Name of the package to check
        
    Returns:
        Dictionary with status and version info
    """
    try:
        module = importlib.import_module(name)
        version = "unknown"
        if hasattr(module, "__version__"):
            version = module.__version__
        elif hasattr(module, "VERSION"):
            version = str(module.VERSION)
            
        return {
            "name": name,
            "installed": True,
            "version": version,
            "error": None
        }
    except ImportError:
        return {
            "name": name,
            "installed": False,
            "version": None,
            "error": "Not installed"
        }

def detect_nmap(custom_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Detect if nmap is installed and return its path and version.
    
    Args:
        custom_path: Optional custom path to nmap executable
        
    Returns:
        Dictionary with 'path', 'version', and 'installed' keys
    """
    nmap_path = custom_path or shutil.which("nmap")
    
    if not nmap_path:
        return {
            "name": "nmap",
            "installed": False,
            "path": None,
            "version": None,
            "error": "Executable not found"
        }

    try:
        result = subprocess.run(
            [nmap_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            version = "unknown"
            for line in result.stdout.split("\n"):
                if "version" in line.lower():
                    version_match = re.search(r"version\s+([\d.]+)", line, re.IGNORECASE)
                    if version_match:
                        version = version_match.group(1)
                        break
            return {
                "name": "nmap",
                "installed": True,
                "path": nmap_path,
                "version": version,
                "error": None
            }
        else:
            return {
                "name": "nmap",
                "installed": False,
                "path": nmap_path,
                "version": None,
                "error": "Command failed"
            }
    except Exception as e:
        return {
            "name": "nmap",
            "installed": False,
            "path": nmap_path,
            "version": None,
            "error": str(e)
        }

def get_all_dependencies() -> Dict[str, Dict[str, Any]]:
    """Get status of all optional dependencies."""
    return {
        "scapy": check_python_dependency("scapy"),
        "pysnmp": check_python_dependency("pysnmp"),
        "nmap": detect_nmap()
    }
