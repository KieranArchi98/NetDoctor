"""
System info module.

psutil wrappers for CPU, memory, disk, network interface metrics.
"""

import socket
import psutil
from typing import Dict, List, Any, Optional


def get_system_overview() -> Dict[str, Any]:
    """
    Get comprehensive system overview information.

    Returns:
        Dictionary containing:
        - cpu_percent: Overall CPU usage percentage (float)
        - per_cpu_percent: List of CPU usage per core (List[float])
        - memory_total: Total memory in bytes (int)
        - memory_used: Used memory in bytes (int)
        - swap: Dictionary with swap_total and swap_used in bytes (Dict[str, int])
        - disk_partitions: List of disk partition info (List[Dict[str, Any]])
        - uptime: System uptime in seconds (float)
        - load_avg: Load average tuple (1min, 5min, 15min) or None if unavailable (Optional[tuple])
        - interfaces: List of network interface info (List[Dict[str, Any]])
    """
    # CPU information
    cpu_percent = psutil.cpu_percent(interval=0.1)
    per_cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)

    # Memory information
    memory = psutil.virtual_memory()
    memory_total = memory.total
    memory_used = memory.used

    # Swap information
    swap = psutil.swap_memory()
    swap_info = {
        "swap_total": swap.total,
        "swap_used": swap.used,
    }

    # Disk partitions
    disk_partitions = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_partitions.append(
                {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                }
            )
        except (PermissionError, OSError):
            # Skip partitions we can't access
            continue

    # Uptime
    uptime = psutil.boot_time()
    import time

    uptime_seconds = time.time() - uptime

    # Load average (Unix/Linux/macOS only)
    try:
        load_avg = psutil.getloadavg()
    except AttributeError:
        # Windows doesn't have load average
        load_avg = None

    # Network interfaces
    interfaces = []
    net_io = psutil.net_io_counters(pernic=True)
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()

    for interface_name in net_if_addrs.keys():
        interface_info = {
            "name": interface_name,
            "ip": None,
            "ipv6": None,
            "mac": None,
            "mtu": None,
            "rx_bytes": 0,
            "tx_bytes": 0,
        }

        # Get IP addresses
        for addr in net_if_addrs.get(interface_name, []):
            if addr.family == socket.AF_INET:
                interface_info["ip"] = addr.address
            elif addr.family == socket.AF_INET6:
                interface_info["ipv6"] = addr.address
            elif addr.family == psutil.AF_LINK:
                interface_info["mac"] = addr.address

        # Get MTU
        if interface_name in net_if_stats:
            stats = net_if_stats[interface_name]
            interface_info["mtu"] = stats.mtu

        # Get I/O counters
        if interface_name in net_io:
            io = net_io[interface_name]
            interface_info["rx_bytes"] = io.bytes_recv
            interface_info["tx_bytes"] = io.bytes_sent

        interfaces.append(interface_info)

    return {
        "cpu_percent": cpu_percent,
        "per_cpu_percent": per_cpu_percent,
        "memory_total": memory_total,
        "memory_used": memory_used,
        "swap": swap_info,
        "disk_partitions": disk_partitions,
        "uptime": uptime_seconds,
        "load_avg": load_avg,
        "interfaces": interfaces,
    }
