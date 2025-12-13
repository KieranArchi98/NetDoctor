"""
Ping logic module.

ICMP ping using raw sockets where permitted, with subprocess fallback.
"""

import socket
import struct
import time
import subprocess
import platform
import re
from typing import List, Dict, Any, Optional, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

from netdoctor.config import DEFAULT_PING_TIMEOUT, DEFAULT_PING_SWEEP_THREADS


def _create_icmp_socket(ipv6: bool = False) -> Optional[socket.socket]:
    """
    Create a raw ICMP socket if permitted.

    Args:
        ipv6: If True, create IPv6 socket (ICMPv6)

    Returns:
        Socket object or None if not permitted/not supported
    """
    try:
        if ipv6:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.settimeout(1.0)
        return sock
    except (OSError, PermissionError, socket.error):
        # Raw sockets require root/admin privileges
        return None


def _icmp_checksum(data: bytes) -> int:
    """Calculate ICMP checksum."""
    checksum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            word = (data[i] << 8) + data[i + 1]
        else:
            word = data[i] << 8
        checksum += word
    while checksum >> 16:
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return (~checksum) & 0xFFFF


def _ping_raw_socket(host: str, count: int = 4, timeout: float = 2.0, ipv6: bool = False) -> List[Dict[str, Any]]:
    """
    Ping using raw ICMP socket (requires root/admin).

    Args:
        host: Hostname or IP address
        count: Number of ping packets to send
        timeout: Timeout per ping in seconds
        ipv6: Use IPv6

    Returns:
        List of ping result dictionaries
    """
    results = []
    sock = _create_icmp_socket(ipv6)
    if sock is None:
        return results  # Fallback will be used

    try:
        # Resolve hostname
        if ipv6:
            addr_info = socket.getaddrinfo(host, None, socket.AF_INET6)[0]
            dest_addr = addr_info[4][0]
        else:
            dest_addr = socket.gethostbyname(host)

        # ICMP type 8 = echo request, code 0
        icmp_type = 128 if ipv6 else 8
        icmp_code = 0
        identifier = 12345  # Process ID or random
        sequence = 0

        for seq in range(count):
            sequence = seq + 1
            # Build ICMP packet
            checksum = 0
            header = struct.pack("!BBHHH", icmp_type, icmp_code, checksum, identifier, sequence)
            data = struct.pack("!d", time.time())  # Timestamp
            checksum = _icmp_checksum(header + data)
            header = struct.pack("!BBHHH", icmp_type, icmp_code, checksum, identifier, sequence)

            packet = header + data
            start_time = time.time()

            try:
                sock.sendto(packet, (dest_addr, 0))
                sock.settimeout(timeout)
                response, addr = sock.recvfrom(1024)
                rtt = (time.time() - start_time) * 1000  # Convert to milliseconds

                # Parse response (simplified - real parsing would check ICMP type/code)
                ttl = response[8] if not ipv6 else None
                results.append(
                    {
                        "seq": sequence,
                        "rtt_ms": round(rtt, 2),
                        "ttl": ttl,
                        "success": True,
                        "error": None,
                    }
                )
            except socket.timeout:
                results.append(
                    {
                        "seq": sequence,
                        "rtt_ms": None,
                        "ttl": None,
                        "success": False,
                        "error": "Request timed out",
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "seq": sequence,
                        "rtt_ms": None,
                        "ttl": None,
                        "success": False,
                        "error": str(e),
                    }
                )

            time.sleep(0.1)  # Small delay between pings

    except Exception as e:
        # If raw socket fails, return empty results (fallback will be used)
        pass
    finally:
        sock.close()

    return results


def _parse_ping_output_linux(output: str, host: str) -> List[Dict[str, Any]]:
    """Parse Linux ping output."""
    results = []
    lines = output.split("\n")

    # Pattern: 64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.023 ms
    pattern = r"icmp_seq=(\d+).*ttl=(\d+).*time=([\d.]+)\s*ms"
    for line in lines:
        match = re.search(pattern, line)
        if match:
            seq = int(match.group(1))
            ttl = int(match.group(2))
            rtt = float(match.group(3))
            results.append(
                {
                    "seq": seq,
                    "rtt_ms": round(rtt, 2),
                    "ttl": ttl,
                    "success": True,
                    "error": None,
                }
            )

    # Pattern for timeouts: Request timeout for icmp_seq X
    timeout_pattern = r"Request timeout for icmp_seq=(\d+)"
    for line in lines:
        match = re.search(timeout_pattern, line)
        if match:
            seq = int(match.group(1))
            results.append(
                {
                    "seq": seq,
                    "rtt_ms": None,
                    "ttl": None,
                    "success": False,
                    "error": "Request timed out",
                }
            )

    return sorted(results, key=lambda x: x["seq"])


def _parse_ping_output_macos(output: str, host: str) -> List[Dict[str, Any]]:
    """Parse macOS ping output."""
    results = []
    lines = output.split("\n")

    # Pattern: 64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.023 ms
    pattern = r"icmp_seq=(\d+).*ttl=(\d+).*time=([\d.]+)\s*ms"
    for line in lines:
        match = re.search(pattern, line)
        if match:
            seq = int(match.group(1))
            ttl = int(match.group(2))
            rtt = float(match.group(3))
            results.append(
                {
                    "seq": seq,
                    "rtt_ms": round(rtt, 2),
                    "ttl": ttl,
                    "success": True,
                    "error": None,
                }
            )

    # Pattern for timeouts
    timeout_pattern = r"Request timeout for icmp_seq=(\d+)"
    for line in lines:
        match = re.search(timeout_pattern, line)
        if match:
            seq = int(match.group(1))
            results.append(
                {
                    "seq": seq,
                    "rtt_ms": None,
                    "ttl": None,
                    "success": False,
                    "error": "Request timed out",
                }
            )

    return sorted(results, key=lambda x: x["seq"])


def _parse_ping_output_windows(output: str, host: str) -> List[Dict[str, Any]]:
    """Parse Windows ping output."""
    results = []
    lines = output.split("\n")
    seq = 0

    for line in lines:
        line_lower = line.lower()
        # Check for timeout first
        if "request timed out" in line_lower or "timed out" in line_lower:
            seq += 1
            results.append(
                {
                    "seq": seq,
                    "rtt_ms": None,
                    "ttl": None,
                    "success": False,
                    "error": "Request timed out",
                }
            )
        # Pattern: Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
        # Pattern: Reply from 127.0.0.1: bytes=32 time=5ms TTL=128
        elif "reply from" in line_lower:
            # Match time<1ms or time=5ms
            time_match = re.search(r"time[<=](\d+)ms", line, re.IGNORECASE)
            ttl_match = re.search(r"ttl=(\d+)", line, re.IGNORECASE)
            
            if time_match and ttl_match:
                seq += 1
                time_str = time_match.group(1)
                # Handle <1ms case
                if "<" in line and time_str == "1":
                    rtt = 0.1
                else:
                    rtt = float(time_str)
                ttl = int(ttl_match.group(1))
                results.append(
                    {
                        "seq": seq,
                        "rtt_ms": round(rtt, 2),
                        "ttl": ttl,
                        "success": True,
                        "error": None,
                    }
                )

    return sorted(results, key=lambda x: x["seq"])


def _ping_subprocess(host: str, count: int = 4, timeout: float = 2.0, ipv6: bool = False) -> List[Dict[str, Any]]:
    """
    Ping using system ping command (fallback method).

    Args:
        host: Hostname or IP address
        count: Number of ping packets to send
        timeout: Timeout per ping in seconds
        ipv6: Use IPv6

    Returns:
        List of ping result dictionaries
    """
    system = platform.system().lower()

    if system == "windows":
        # Windows ping command
        cmd = ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), host]
        if ipv6:
            cmd.insert(1, "-6")
    elif system in ["linux", "darwin"]:  # macOS is darwin
        # Linux/macOS ping command
        cmd = ["ping", "-c", str(count), "-W", str(int(timeout)), host]
        if ipv6:
            cmd = ["ping6", "-c", str(count), "-W", str(int(timeout)), host]
    else:
        # Unknown system, try generic
        cmd = ["ping", "-c", str(count), host]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=(count * timeout + 5), check=False
        )
        output = result.stdout + result.stderr

        # Parse based on platform
        if system == "windows":
            return _parse_ping_output_windows(output, host)
        elif system == "darwin":
            return _parse_ping_output_macos(output, host)
        else:  # Linux
            return _parse_ping_output_linux(output, host)
    except subprocess.TimeoutExpired:
        return [
            {
                "seq": i + 1,
                "rtt_ms": None,
                "ttl": None,
                "success": False,
                "error": "Ping command timed out",
            }
            for i in range(count)
        ]
    except Exception as e:
        return [
            {
                "seq": i + 1,
                "rtt_ms": None,
                "ttl": None,
                "success": False,
                "error": f"Ping failed: {str(e)}",
            }
            for i in range(count)
        ]


def ping_host(host: str, count: int = 4, timeout: float = 2.0, ipv6: bool = False) -> List[Dict[str, Any]]:
    """
    Ping a host using raw sockets or subprocess fallback.

    Args:
        host: Hostname or IP address to ping
        count: Number of ping packets to send (default: 4)
        timeout: Timeout per ping in seconds (default: 2.0)
        ipv6: Use IPv6 instead of IPv4 (default: False)

    Returns:
        List of dictionaries with keys: seq, rtt_ms, ttl, success, error
    """
    # Try raw socket first
    results = _ping_raw_socket(host, count, timeout, ipv6)

    # If raw socket failed (empty results or permission denied), use subprocess
    if not results or all(not r.get("success", False) for r in results):
        results = _ping_subprocess(host, count, timeout, ipv6)

    return results


def ping_sweep(
    network_cidr: str, concurrency: int = DEFAULT_PING_SWEEP_THREADS
) -> Iterator[Dict[str, Any]]:
    """
    Ping multiple hosts in a network range in parallel.

    Args:
        network_cidr: Network in CIDR notation (e.g., "192.168.1.0/24")
        concurrency: Maximum number of concurrent pings (default: 10)

    Yields:
        Dictionaries with keys: host, results (list of ping results)
    """
    try:
        network = ipaddress.ip_network(network_cidr, strict=False)
    except ValueError as e:
        yield {"host": network_cidr, "results": [], "error": f"Invalid network: {str(e)}"}
        return

    def ping_single_host(host: str) -> Dict[str, Any]:
        """Ping a single host and return result."""
        try:
            results = ping_host(str(host), count=1, timeout=1.0)
            return {"host": str(host), "results": results, "error": None}
        except Exception as e:
            return {"host": str(host), "results": [], "error": str(e)}

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all ping tasks
        future_to_host = {executor.submit(ping_single_host, host): host for host in network.hosts()}

        # Yield results as they complete
        for future in as_completed(future_to_host):
            try:
                result = future.result()
                yield result
            except Exception as e:
                host = future_to_host[future]
                yield {"host": str(host), "results": [], "error": str(e)}
