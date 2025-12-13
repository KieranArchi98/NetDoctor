"""
Port scanning logic module.

TCP connect scanning across ranges with configurable concurrency.
"""

import socket
import subprocess
import shutil
from typing import List, Dict, Any, Union, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from netdoctor.config import DEFAULT_PORT_SCAN_TIMEOUT, DEFAULT_PORT_SCAN_THREADS


def _parse_port_range(ports: Union[str, int, List[int]]) -> List[int]:
    """
    Parse port specification into a list of port numbers.

    Args:
        ports: Can be:
            - int: Single port
            - List[int]: List of ports
            - str: Comma-separated ports or ranges (e.g., "80,443,8000-8010")

    Returns:
        List of port numbers
    """
    if isinstance(ports, int):
        return [ports]
    if isinstance(ports, list):
        return ports

    # Parse string format
    port_list = []
    for part in ports.split(","):
        part = part.strip()
        if "-" in part:
            # Range: 8000-8010
            start, end = part.split("-", 1)
            try:
                start_port = int(start.strip())
                end_port = int(end.strip())
                port_list.extend(range(start_port, end_port + 1))
            except ValueError:
                continue
        else:
            # Single port
            try:
                port_list.append(int(part))
            except ValueError:
                continue

    return sorted(set(port_list))  # Remove duplicates and sort


def _grab_banner(sock: socket.socket, timeout: float = 2.0) -> Optional[str]:
    """
    Attempt to grab a banner from an open socket.

    Args:
        sock: Connected socket
        timeout: Timeout for banner read

    Returns:
        Banner string or None
    """
    try:
        sock.settimeout(timeout)
        # Try to read initial response (common for services like HTTP, FTP, SSH)
        banner = sock.recv(1024)
        if banner:
            # Decode and clean up banner
            try:
                banner_str = banner.decode("utf-8", errors="ignore").strip()
                # Remove newlines and limit length
                banner_str = " ".join(banner_str.split()[:10])  # First 10 words
                return banner_str[:200] if len(banner_str) > 200 else banner_str
            except Exception:
                return banner[:100].hex()  # Return hex if can't decode
    except (socket.timeout, socket.error, OSError):
        pass
    return None


def _scan_single_port(
    host: str, port: int, timeout: float = 1.0, banner_grab: bool = False
) -> Dict[str, Any]:
    """
    Scan a single port.

    Args:
        host: Hostname or IP address
        port: Port number to scan
        timeout: Connection timeout in seconds
        banner_grab: If True, attempt to grab banner after connection

    Returns:
        Dictionary with keys: port, state, banner
    """
    result = {"port": port, "state": "closed", "banner": None}

    try:
        # Attempt TCP connection
        sock = socket.create_connection((host, port), timeout=timeout)
        result["state"] = "open"

        # Optionally grab banner
        if banner_grab:
            banner = _grab_banner(sock, timeout=min(timeout, 2.0))
            result["banner"] = banner

        sock.close()
    except socket.timeout:
        result["state"] = "closed"
        result["error"] = "Connection timeout"
    except ConnectionRefusedError:
        result["state"] = "closed"
        result["error"] = "Connection refused"
    except OSError as e:
        result["state"] = "closed"
        result["error"] = str(e)
    except Exception as e:
        result["state"] = "closed"
        result["error"] = str(e)

    return result


def scan_ports(
    host: str,
    ports: Union[str, int, List[int]],
    timeout: float = 1.0,
    concurrency: int = DEFAULT_PORT_SCAN_THREADS,
    banner_grab: bool = False,
) -> List[Dict[str, Any]]:
    """
    Scan multiple ports on a host using TCP connect scanning.

    Args:
        host: Hostname or IP address to scan
        ports: Port specification (int, list, or string like "80,443,8000-8010")
        timeout: Connection timeout per port in seconds (default: 1.0)
        concurrency: Maximum number of concurrent scans (default: 100)
        banner_grab: If True, attempt to grab banners from open ports (default: False)

    Returns:
        List of dictionaries with keys: port, state (open/closed), banner (optional), error (optional)
    """
    port_list = _parse_port_range(ports)
    if not port_list:
        return []

    results = []

    def scan_port(port: int) -> Dict[str, Any]:
        return _scan_single_port(host, port, timeout, banner_grab)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all port scans
        future_to_port = {executor.submit(scan_port, port): port for port in port_list}

        # Collect results as they complete
        for future in as_completed(future_to_port):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                port = future_to_port[future]
                results.append(
                    {
                        "port": port,
                        "state": "closed",
                        "banner": None,
                        "error": str(e),
                    }
                )

    # Sort results by port number
    return sorted(results, key=lambda x: x["port"])


def detect_nmap() -> Optional[Dict[str, str]]:
    """
    Detect if nmap is installed and return its path and version.

    Returns:
        Dictionary with 'path' and 'version' keys, or None if nmap not found
    """
    # First try to find nmap in PATH
    nmap_path = shutil.which("nmap")
    if not nmap_path:
        return None

    # Try to get version
    try:
        result = subprocess.run(
            [nmap_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            # Parse version from output (e.g., "Nmap version 7.94")
            version_match = None
            for line in result.stdout.split("\n"):
                if "version" in line.lower():
                    # Extract version number
                    import re

                    version_match = re.search(r"version\s+([\d.]+)", line, re.IGNORECASE)
                    if version_match:
                        version = version_match.group(1)
                        return {"path": nmap_path, "version": version}
            # If we got output but couldn't parse version, still return path
            return {"path": nmap_path, "version": "unknown"}
        else:
            # If nmap command failed, return None (nmap might not work)
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        # If we can't run nmap, return None
        return None

    return None
