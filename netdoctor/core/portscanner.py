"""
Port scanning logic module.

TCP connect scanning across ranges with configurable concurrency.
"""

import socket
import subprocess
import shutil
from typing import List, Dict, Any, Union, Optional, Iterator
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


def scan_ports_iter(
    host: str,
    ports: Union[str, int, List[int]],
    timeout: float = 1.0,
    concurrency: int = DEFAULT_PORT_SCAN_THREADS,
    banner_grab: bool = False,
) -> Iterator[Dict[str, Any]]:
    """
    Scan multiple ports on a host and yield results as they complete.
    """
    port_list = _parse_port_range(ports)
    if not port_list:
        return

    def scan_port(port: int) -> Dict[str, Any]:
        return _scan_single_port(host, port, timeout, banner_grab)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_port = {executor.submit(scan_port, port): port for port in port_list}
        for future in as_completed(future_to_port):
            try:
                yield future.result()
            except Exception as e:
                port = future_to_port[future]
                yield {
                    "port": port,
                    "state": "closed",
                    "banner": None,
                    "error": str(e),
                }

def scan_ports(
    host: str,
    ports: Union[str, int, List[int]],
    timeout: float = 1.0,
    concurrency: int = DEFAULT_PORT_SCAN_THREADS,
    banner_grab: bool = False,
) -> List[Dict[str, Any]]:
    """
    Scan multiple ports on a host using TCP connect scanning.
    """
    results = list(scan_ports_iter(host, ports, timeout, concurrency, banner_grab))
    return sorted(results, key=lambda x: x["port"])


from netdoctor.core.utils import detect_nmap
