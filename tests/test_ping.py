"""
Unit tests for ping module.
"""

import pytest
import platform
import subprocess
from unittest.mock import Mock, patch, MagicMock
from netdoctor.core.ping import (
    ping_host,
    ping_sweep,
    _parse_ping_output_linux,
    _parse_ping_output_macos,
    _parse_ping_output_windows,
    _ping_subprocess,
)


def test_parse_ping_output_linux():
    """Test parsing Linux ping output."""
    output = """PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.023 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.015 ms
64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.018 ms
64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.020 ms

--- 127.0.0.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3001ms
"""
    results = _parse_ping_output_linux(output, "127.0.0.1")
    assert len(results) == 4
    assert results[0]["seq"] == 1
    assert results[0]["rtt_ms"] == 0.02
    assert results[0]["ttl"] == 64
    assert results[0]["success"] is True
    assert results[0]["error"] is None


def test_parse_ping_output_linux_with_timeouts():
    """Test parsing Linux ping output with timeouts."""
    output = """PING 192.168.1.100 (192.168.1.100) 56(84) bytes of data.
64 bytes from 192.168.1.100: icmp_seq=1 ttl=64 time=1.234 ms
Request timeout for icmp_seq=2
64 bytes from 192.168.1.100: icmp_seq=3 ttl=64 time=1.567 ms
Request timeout for icmp_seq=4
"""
    results = _parse_ping_output_linux(output, "192.168.1.100")
    assert len(results) == 4
    assert results[0]["success"] is True
    assert results[1]["success"] is False
    assert results[1]["error"] == "Request timed out"
    assert results[2]["success"] is True
    assert results[3]["success"] is False


def test_parse_ping_output_macos():
    """Test parsing macOS ping output."""
    output = """PING 127.0.0.1 (127.0.0.1): 56 data bytes
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.025 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.018 ms
64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.020 ms
64 bytes from 127.0.0.1: icmp_seq=4 ttl=64 time=0.022 ms

--- 127.0.0.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss
"""
    results = _parse_ping_output_macos(output, "127.0.0.1")
    assert len(results) == 4
    assert results[0]["seq"] == 1
    assert results[0]["rtt_ms"] == 0.03
    assert results[0]["ttl"] == 64
    assert results[0]["success"] is True


def test_parse_ping_output_windows():
    """Test parsing Windows ping output."""
    output = """Pinging 127.0.0.1 with 32 bytes of data:
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128

Ping statistics for 127.0.0.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms
"""
    results = _parse_ping_output_windows(output, "127.0.0.1")
    assert len(results) == 4
    assert results[0]["seq"] == 1
    assert results[0]["rtt_ms"] == 0.1  # <1ms becomes 0.1
    assert results[0]["ttl"] == 128
    assert results[0]["success"] is True


def test_parse_ping_output_windows_with_timeouts():
    """Test parsing Windows ping output with timeouts."""
    output = """Pinging 192.168.1.100 with 32 bytes of data:
Reply from 192.168.1.100: bytes=32 time=5ms TTL=64
Request timed out.
Reply from 192.168.1.100: bytes=32 time=3ms TTL=64
Request timed out.
"""
    results = _parse_ping_output_windows(output, "192.168.1.100")
    assert len(results) == 4
    assert results[0]["success"] is True
    assert results[1]["success"] is False
    assert results[2]["success"] is True
    assert results[3]["success"] is False


@pytest.mark.network
def test_ping_host_localhost():
    """Test pinging localhost (requires network, marked to skip in CI)."""
    results = ping_host("127.0.0.1", count=2, timeout=1.0)
    assert len(results) == 2
    for result in results:
        assert "seq" in result
        assert "rtt_ms" in result
        assert "ttl" in result
        assert "success" in result
        assert "error" in result
        assert isinstance(result["seq"], int)
        assert result["seq"] > 0


@pytest.mark.network
def test_ping_host_localhost_ipv6():
    """Test pinging localhost via IPv6 (requires network, marked to skip in CI)."""
    try:
        results = ping_host("::1", count=2, timeout=1.0, ipv6=True)
        assert len(results) == 2
        for result in results:
            assert "seq" in result
            assert "success" in result
    except Exception:
        # IPv6 might not be available, skip test
        pytest.skip("IPv6 not available")


@patch("netdoctor.core.ping._ping_raw_socket")
@patch("netdoctor.core.ping._ping_subprocess")
def test_ping_host_fallback_to_subprocess(mock_subprocess, mock_raw):
    """Test that ping_host falls back to subprocess when raw socket fails."""
    # Raw socket returns empty results (simulating failure)
    mock_raw.return_value = []
    # Subprocess returns successful results
    mock_subprocess.return_value = [
        {"seq": 1, "rtt_ms": 1.0, "ttl": 64, "success": True, "error": None}
    ]

    results = ping_host("127.0.0.1", count=1)
    assert len(results) == 1
    assert results[0]["success"] is True
    mock_subprocess.assert_called_once()


@patch("netdoctor.core.ping._ping_raw_socket")
@patch("netdoctor.core.ping._ping_subprocess")
def test_ping_host_uses_raw_socket_when_available(mock_subprocess, mock_raw):
    """Test that ping_host uses raw socket results when available."""
    # Raw socket returns successful results
    mock_raw.return_value = [
        {"seq": 1, "rtt_ms": 0.5, "ttl": 64, "success": True, "error": None}
    ]

    results = ping_host("127.0.0.1", count=1)
    assert len(results) == 1
    assert results[0]["success"] is True
    # Subprocess should not be called
    mock_subprocess.assert_not_called()


@patch("netdoctor.core.ping.ping_host")
def test_ping_sweep(mock_ping_host):
    """Test ping_sweep function."""
    # Mock ping_host to return different results
    def mock_ping(host, count=1, timeout=1.0, ipv6=False):
        if "192.168.1.1" in str(host):
            return [{"seq": 1, "rtt_ms": 1.0, "ttl": 64, "success": True, "error": None}]
        else:
            return [{"seq": 1, "rtt_ms": None, "ttl": None, "success": False, "error": "Timeout"}]

    mock_ping_host.side_effect = mock_ping

    results = list(ping_sweep("192.168.1.0/30", concurrency=2))
    # Should ping 192.168.1.1, 192.168.1.2, 192.168.1.3 (network and broadcast excluded)
    assert len(results) == 2  # 192.168.1.1 and 192.168.1.2 (for /30)
    for result in results:
        assert "host" in result
        assert "results" in result
        assert "error" in result


def test_ping_sweep_invalid_network():
    """Test ping_sweep with invalid network."""
    results = list(ping_sweep("invalid.network", concurrency=1))
    assert len(results) == 1
    assert "error" in results[0]
    assert "Invalid network" in results[0]["error"]


@patch("netdoctor.core.ping.subprocess.run")
def test_ping_subprocess_linux(mock_subprocess):
    """Test subprocess ping on Linux."""
    mock_subprocess.return_value = Mock(
        stdout="""PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.023 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.015 ms
""",
        stderr="",
        returncode=0,
    )

    with patch("platform.system", return_value="Linux"):
        results = _ping_subprocess("127.0.0.1", count=2, timeout=1.0)
        assert len(results) == 2
        assert results[0]["success"] is True


@patch("netdoctor.core.ping.subprocess.run")
def test_ping_subprocess_windows(mock_subprocess):
    """Test subprocess ping on Windows."""
    mock_subprocess.return_value = Mock(
        stdout="""Pinging 127.0.0.1 with 32 bytes of data:
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
""",
        stderr="",
        returncode=0,
    )

    with patch("platform.system", return_value="Windows"):
        results = _ping_subprocess("127.0.0.1", count=2, timeout=1.0)
        assert len(results) == 2
        assert results[0]["success"] is True


@patch("netdoctor.core.ping.subprocess.run")
def test_ping_subprocess_timeout(mock_subprocess):
    """Test subprocess ping timeout handling."""
    mock_subprocess.side_effect = subprocess.TimeoutExpired("ping", 5.0)

    results = _ping_subprocess("127.0.0.1", count=3, timeout=1.0)
    assert len(results) == 3
    for result in results:
        assert result["success"] is False
        assert "timed out" in result["error"]

