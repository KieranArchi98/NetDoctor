"""
Unit tests for systeminfo module.
"""

import pytest
import psutil
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from netdoctor.core.systeminfo import get_system_overview


def test_get_system_overview_structure():
    """Test that get_system_overview returns the expected structure."""
    result = get_system_overview()

    # Check all required keys exist
    required_keys = [
        "cpu_percent",
        "per_cpu_percent",
        "memory_total",
        "memory_used",
        "swap",
        "disk_partitions",
        "uptime",
        "load_avg",
        "interfaces",
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"

    # Check types
    assert isinstance(result["cpu_percent"], (int, float))
    assert isinstance(result["per_cpu_percent"], list)
    assert all(isinstance(x, (int, float)) for x in result["per_cpu_percent"])

    assert isinstance(result["memory_total"], int)
    assert isinstance(result["memory_used"], int)

    assert isinstance(result["swap"], dict)
    assert "swap_total" in result["swap"]
    assert "swap_used" in result["swap"]
    assert isinstance(result["swap"]["swap_total"], int)
    assert isinstance(result["swap"]["swap_used"], int)

    assert isinstance(result["disk_partitions"], list)
    for partition in result["disk_partitions"]:
        assert isinstance(partition, dict)
        assert "device" in partition
        assert "mountpoint" in partition
        assert "total" in partition
        assert "used" in partition
        assert isinstance(partition["total"], int)
        assert isinstance(partition["used"], int)

    assert isinstance(result["uptime"], (int, float))
    assert result["uptime"] >= 0

    # load_avg can be None (Windows) or tuple (Unix)
    assert result["load_avg"] is None or isinstance(result["load_avg"], tuple)

    assert isinstance(result["interfaces"], list)
    for interface in result["interfaces"]:
        assert isinstance(interface, dict)
        assert "name" in interface
        assert isinstance(interface["name"], str)
        assert "ip" in interface
        assert "mac" in interface
        assert "mtu" in interface
        assert "rx_bytes" in interface
        assert "tx_bytes" in interface
        assert isinstance(interface["rx_bytes"], int)
        assert isinstance(interface["tx_bytes"], int)


@patch("netdoctor.core.systeminfo.psutil")
@patch("netdoctor.core.systeminfo.socket")
def test_get_system_overview_mocked(mock_socket, mock_psutil):
    """Test get_system_overview with mocked psutil."""
    # Set up socket constants
    import socket as real_socket

    mock_socket.AF_INET = real_socket.AF_INET  # 2
    mock_socket.AF_INET6 = real_socket.AF_INET6  # 10

    # Mock CPU
    mock_psutil.cpu_percent.side_effect = [25.5, [10.0, 20.0, 30.0, 40.0]]

    # Mock memory
    mock_memory = Mock()
    mock_memory.total = 8589934592  # 8GB
    mock_memory.used = 4294967296  # 4GB
    mock_psutil.virtual_memory.return_value = mock_memory

    # Mock swap
    mock_swap = Mock()
    mock_swap.total = 2147483648  # 2GB
    mock_swap.used = 1073741824  # 1GB
    mock_psutil.swap_memory.return_value = mock_swap

    # Mock disk partitions
    mock_partition = Mock()
    mock_partition.device = "/dev/sda1"
    mock_partition.mountpoint = "/"
    mock_partition.fstype = "ext4"
    mock_psutil.disk_partitions.return_value = [mock_partition]

    mock_usage = Mock()
    mock_usage.total = 500107862016  # ~500GB
    mock_usage.used = 250053931008  # ~250GB
    mock_usage.free = 250053931008  # ~250GB
    mock_psutil.disk_usage.return_value = mock_usage

    # Mock boot time
    import time

    mock_psutil.boot_time.return_value = time.time() - 86400  # 1 day ago

    # Mock load average (Unix-like)
    mock_psutil.getloadavg.return_value = (1.5, 1.2, 1.0)

    # Mock network interfaces
    mock_psutil.net_io_counters.return_value = {
        "eth0": Mock(bytes_recv=1000000, bytes_sent=500000)
    }
    mock_psutil.net_if_addrs.return_value = {
        "eth0": [
            Mock(family=real_socket.AF_INET, address="192.168.1.100"),  # AF_INET
            Mock(family=real_socket.AF_INET6, address="fe80::1"),  # AF_INET6
            Mock(family=psutil.AF_LINK, address="00:11:22:33:44:55"),  # AF_LINK
        ]
    }
    mock_psutil.net_if_stats.return_value = {
        "eth0": Mock(mtu=1500)
    }
    mock_psutil.AF_LINK = psutil.AF_LINK

    result = get_system_overview()

    # Verify structure
    assert result["cpu_percent"] == 25.5
    assert result["per_cpu_percent"] == [10.0, 20.0, 30.0, 40.0]
    assert result["memory_total"] == 8589934592
    assert result["memory_used"] == 4294967296
    assert result["swap"]["swap_total"] == 2147483648
    assert result["swap"]["swap_used"] == 1073741824
    assert len(result["disk_partitions"]) == 1
    assert result["disk_partitions"][0]["device"] == "/dev/sda1"
    assert result["load_avg"] == (1.5, 1.2, 1.0)
    assert len(result["interfaces"]) == 1
    assert result["interfaces"][0]["name"] == "eth0"
    assert result["interfaces"][0]["ip"] == "192.168.1.100"
    assert result["interfaces"][0]["mac"] == "00:11:22:33:44:55"
    assert result["interfaces"][0]["mtu"] == 1500
    assert result["interfaces"][0]["rx_bytes"] == 1000000
    assert result["interfaces"][0]["tx_bytes"] == 500000


@patch("netdoctor.core.systeminfo.psutil")
def test_get_system_overview_windows_no_load_avg(mock_psutil):
    """Test that load_avg is None on Windows (no getloadavg)."""
    # Mock CPU
    mock_psutil.cpu_percent.side_effect = [25.0, [25.0]]

    # Mock memory
    mock_memory = Mock()
    mock_memory.total = 8589934592
    mock_memory.used = 4294967296
    mock_psutil.virtual_memory.return_value = mock_memory

    # Mock swap
    mock_swap = Mock()
    mock_swap.total = 2147483648
    mock_swap.used = 1073741824
    mock_psutil.swap_memory.return_value = mock_swap

    # Mock disk partitions
    mock_psutil.disk_partitions.return_value = []

    # Mock boot time
    import time

    mock_psutil.boot_time.return_value = time.time() - 86400

    # Mock load average - AttributeError simulates Windows
    mock_psutil.getloadavg.side_effect = AttributeError("getloadavg not available")

    # Mock network
    mock_psutil.net_io_counters.return_value = {}
    mock_psutil.net_if_addrs.return_value = {}
    mock_psutil.net_if_stats.return_value = {}

    result = get_system_overview()

    assert result["load_avg"] is None


@patch("netdoctor.core.systeminfo.psutil")
def test_get_system_overview_disk_permission_error(mock_psutil):
    """Test that disk partitions with permission errors are skipped."""
    # Mock CPU
    mock_psutil.cpu_percent.side_effect = [25.0, [25.0]]

    # Mock memory
    mock_memory = Mock()
    mock_memory.total = 8589934592
    mock_memory.used = 4294967296
    mock_psutil.virtual_memory.return_value = mock_memory

    # Mock swap
    mock_swap = Mock()
    mock_swap.total = 2147483648
    mock_swap.used = 1073741824
    mock_psutil.swap_memory.return_value = mock_swap

    # Mock disk partitions - one accessible, one with permission error
    mock_partition1 = Mock()
    mock_partition1.device = "/dev/sda1"
    mock_partition1.mountpoint = "/"
    mock_partition1.fstype = "ext4"

    mock_partition2 = Mock()
    mock_partition2.device = "/dev/sdb1"
    mock_partition2.mountpoint = "/mnt/restricted"
    mock_partition2.fstype = "ext4"

    mock_psutil.disk_partitions.return_value = [mock_partition1, mock_partition2]

    # First partition accessible, second raises PermissionError
    mock_usage = Mock()
    mock_usage.total = 500107862016
    mock_usage.used = 250053931008
    mock_usage.free = 250053931008

    def disk_usage_side_effect(mountpoint):
        if mountpoint == "/":
            return mock_usage
        else:
            raise PermissionError("Access denied")

    mock_psutil.disk_usage.side_effect = disk_usage_side_effect

    # Mock boot time
    import time

    mock_psutil.boot_time.return_value = time.time() - 86400

    # Mock load average
    mock_psutil.getloadavg.return_value = (1.0, 1.0, 1.0)

    # Mock network
    mock_psutil.net_io_counters.return_value = {}
    mock_psutil.net_if_addrs.return_value = {}
    mock_psutil.net_if_stats.return_value = {}

    result = get_system_overview()

    # Should only have one partition (the accessible one)
    assert len(result["disk_partitions"]) == 1
    assert result["disk_partitions"][0]["device"] == "/dev/sda1"

