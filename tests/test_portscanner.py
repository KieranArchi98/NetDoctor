"""
Unit tests for portscanner module.
"""

import pytest
import socket
import subprocess
from unittest.mock import Mock, patch, MagicMock
from netdoctor.core.portscanner import (
    scan_ports,
    _scan_single_port,
    _parse_port_range,
    _grab_banner,
    detect_nmap,
)


def test_parse_port_range_single_int():
    """Test parsing a single integer port."""
    assert _parse_port_range(80) == [80]


def test_parse_port_range_list():
    """Test parsing a list of ports."""
    assert _parse_port_range([80, 443, 8080]) == [80, 443, 8080]


def test_parse_port_range_string_single():
    """Test parsing a single port as string."""
    assert _parse_port_range("80") == [80]


def test_parse_port_range_string_multiple():
    """Test parsing comma-separated ports."""
    assert _parse_port_range("80,443,8080") == [80, 443, 8080]


def test_parse_port_range_string_range():
    """Test parsing port ranges."""
    assert _parse_port_range("8000-8002") == [8000, 8001, 8002]


def test_parse_port_range_string_mixed():
    """Test parsing mixed ports and ranges."""
    result = _parse_port_range("80,443,8000-8002,9000")
    assert result == [80, 443, 8000, 8001, 8002, 9000]


def test_parse_port_range_removes_duplicates():
    """Test that duplicate ports are removed."""
    assert _parse_port_range("80,80,443,443") == [80, 443]


def test_parse_port_range_invalid():
    """Test parsing invalid port strings."""
    assert _parse_port_range("invalid,80") == [80]
    assert _parse_port_range("80-invalid") == []


@patch("socket.create_connection")
def test_scan_single_port_open(mock_create_connection):
    """Test scanning an open port."""
    mock_sock = MagicMock()
    mock_create_connection.return_value = mock_sock

    result = _scan_single_port("127.0.0.1", 80, timeout=1.0, banner_grab=False)

    assert result["port"] == 80
    assert result["state"] == "open"
    assert result["banner"] is None
    mock_sock.close.assert_called_once()


@patch("socket.create_connection")
def test_scan_single_port_open_with_banner(mock_create_connection):
    """Test scanning an open port with banner grabbing."""
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b"HTTP/1.1 200 OK\r\nServer: nginx\r\n"
    mock_create_connection.return_value = mock_sock

    result = _scan_single_port("127.0.0.1", 80, timeout=1.0, banner_grab=True)

    assert result["port"] == 80
    assert result["state"] == "open"
    assert result["banner"] is not None
    assert "HTTP" in result["banner"] or "nginx" in result["banner"]
    mock_sock.recv.assert_called_once()


@patch("socket.create_connection")
def test_scan_single_port_closed_timeout(mock_create_connection):
    """Test scanning a closed port (timeout)."""
    mock_create_connection.side_effect = socket.timeout()

    result = _scan_single_port("127.0.0.1", 9999, timeout=1.0)

    assert result["port"] == 9999
    assert result["state"] == "closed"
    assert "timeout" in result.get("error", "").lower()


@patch("socket.create_connection")
def test_scan_single_port_closed_refused(mock_create_connection):
    """Test scanning a closed port (connection refused)."""
    mock_create_connection.side_effect = ConnectionRefusedError()

    result = _scan_single_port("127.0.0.1", 9999, timeout=1.0)

    assert result["port"] == 9999
    assert result["state"] == "closed"
    assert "refused" in result.get("error", "").lower()


@patch("socket.create_connection")
def test_scan_single_port_closed_oserror(mock_create_connection):
    """Test scanning a port with OSError."""
    mock_create_connection.side_effect = OSError("Network unreachable")

    result = _scan_single_port("127.0.0.1", 9999, timeout=1.0)

    assert result["port"] == 9999
    assert result["state"] == "closed"
    assert "error" in result


def test_grab_banner_success():
    """Test successful banner grabbing."""
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b"SSH-2.0-OpenSSH_8.0\r\n"

    banner = _grab_banner(mock_sock, timeout=1.0)

    assert banner is not None
    assert "SSH" in banner or "OpenSSH" in banner
    mock_sock.settimeout.assert_called_once()
    mock_sock.recv.assert_called_once()


def test_grab_banner_timeout():
    """Test banner grabbing with timeout."""
    mock_sock = MagicMock()
    mock_sock.recv.side_effect = socket.timeout()

    banner = _grab_banner(mock_sock, timeout=1.0)

    assert banner is None


def test_grab_banner_empty():
    """Test banner grabbing with empty response."""
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b""

    banner = _grab_banner(mock_sock, timeout=1.0)

    assert banner is None


def test_grab_banner_binary():
    """Test banner grabbing with binary data."""
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b"\x00\x01\x02\x03\xff\xfe"

    banner = _grab_banner(mock_sock, timeout=1.0)

    # Should return hex representation for binary data
    assert banner is not None
    assert isinstance(banner, str)


@patch("netdoctor.core.portscanner._scan_single_port")
def test_scan_ports_single(mock_scan):
    """Test scanning a single port."""
    mock_scan.return_value = {"port": 80, "state": "open", "banner": None}

    results = scan_ports("127.0.0.1", 80, timeout=1.0, concurrency=10)

    assert len(results) == 1
    assert results[0]["port"] == 80
    assert results[0]["state"] == "open"


@patch("netdoctor.core.portscanner._scan_single_port")
def test_scan_ports_multiple(mock_scan):
    """Test scanning multiple ports."""
    def mock_scan_side_effect(host, port, timeout, banner_grab):
        return {"port": port, "state": "open" if port == 80 else "closed", "banner": None}

    mock_scan.side_effect = mock_scan_side_effect

    results = scan_ports("127.0.0.1", [80, 443, 8080], timeout=1.0, concurrency=10)

    assert len(results) == 3
    assert results[0]["port"] == 80
    assert results[1]["port"] == 443
    assert results[2]["port"] == 8080
    # Results should be sorted by port
    assert results[0]["port"] < results[1]["port"] < results[2]["port"]


@patch("netdoctor.core.portscanner._scan_single_port")
def test_scan_ports_range_string(mock_scan):
    """Test scanning ports from a range string."""
    def mock_scan_side_effect(host, port, timeout, banner_grab):
        return {"port": port, "state": "open" if port == 80 else "closed", "banner": None}

    mock_scan.side_effect = mock_scan_side_effect

    results = scan_ports("127.0.0.1", "80-82", timeout=1.0, concurrency=10)

    assert len(results) == 3
    assert [r["port"] for r in results] == [80, 81, 82]


@patch("netdoctor.core.portscanner._scan_single_port")
def test_scan_ports_with_banner_grab(mock_scan):
    """Test scanning ports with banner grabbing enabled."""
    mock_scan.return_value = {
        "port": 80,
        "state": "open",
        "banner": "HTTP/1.1 200 OK",
    }

    results = scan_ports("127.0.0.1", 80, timeout=1.0, banner_grab=True, concurrency=10)

    assert len(results) == 1
    assert results[0]["banner"] == "HTTP/1.1 200 OK"
    # Verify banner_grab was passed to _scan_single_port
    mock_scan.assert_called_with("127.0.0.1", 80, 1.0, True)


@patch("netdoctor.core.portscanner._scan_single_port")
def test_scan_ports_empty_range(mock_scan):
    """Test scanning with empty/invalid port range."""
    results = scan_ports("127.0.0.1", "invalid", timeout=1.0, concurrency=10)

    assert len(results) == 0
    mock_scan.assert_not_called()


@patch("netdoctor.core.portscanner._scan_single_port")
def test_scan_ports_exception_handling(mock_scan):
    """Test that exceptions in port scanning are handled gracefully."""
    mock_scan.side_effect = Exception("Unexpected error")

    results = scan_ports("127.0.0.1", [80, 443], timeout=1.0, concurrency=10)

    assert len(results) == 2
    for result in results:
        assert result["state"] == "closed"
        assert "error" in result


@patch("shutil.which")
@patch("subprocess.run")
def test_detect_nmap_found(mock_subprocess, mock_which):
    """Test detecting nmap when it's installed."""
    mock_which.return_value = "/usr/bin/nmap"
    mock_subprocess.return_value = Mock(
        returncode=0,
        stdout="Nmap version 7.94 ( https://nmap.org )\n",
        stderr="",
    )

    result = detect_nmap()

    assert result is not None
    assert result["path"] == "/usr/bin/nmap"
    assert result["version"] == "7.94"


@patch("shutil.which")
@patch("subprocess.run")
def test_detect_nmap_found_unknown_version(mock_subprocess, mock_which):
    """Test detecting nmap when version can't be parsed."""
    mock_which.return_value = "/usr/bin/nmap"
    mock_subprocess.return_value = Mock(
        returncode=0,
        stdout="Some output without version",
        stderr="",
    )

    result = detect_nmap()

    assert result is not None
    assert result["path"] == "/usr/bin/nmap"
    assert result["version"] == "unknown"


@patch("shutil.which")
def test_detect_nmap_not_found(mock_which):
    """Test detecting nmap when it's not installed."""
    mock_which.return_value = None

    result = detect_nmap()

    assert result is None


@patch("shutil.which")
@patch("subprocess.run")
def test_detect_nmap_subprocess_error(mock_subprocess, mock_which):
    """Test detecting nmap when subprocess fails."""
    mock_which.return_value = "/usr/bin/nmap"
    mock_subprocess.side_effect = subprocess.TimeoutExpired("nmap", 5.0)

    result = detect_nmap()

    # Should return None if subprocess fails
    assert result is None

