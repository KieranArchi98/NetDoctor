"""
Unit tests for WHOIS module.
"""

import pytest
import subprocess
from unittest.mock import Mock, patch, MagicMock

from netdoctor.core.whois import query_whois, PYTHON_WHOIS_AVAILABLE


@patch("netdoctor.core.whois.whois")
@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", True)
def test_query_whois_python_whois_success(mock_whois):
    """Test WHOIS query using python-whois."""
    mock_whois_data = Mock()
    mock_whois_data.text = "Domain Name: example.com\nRegistrar: Example Registrar"
    mock_whois_data.domain_name = "example.com"
    mock_whois_data.registrar = "Example Registrar"
    mock_whois_data.creation_date = "2020-01-01"
    mock_whois_data.expiration_date = "2025-01-01"
    mock_whois_data.updated_date = "2023-01-01"
    mock_whois_data.name_servers = ["ns1.example.com", "ns2.example.com"]
    mock_whois_data.status = ["clientTransferProhibited"]

    mock_whois.whois.return_value = mock_whois_data

    result = query_whois("example.com")

    assert result["method"] == "python-whois"
    assert result["raw"] is not None
    assert "example.com" in result["raw"]
    assert result["parsed"] is not None
    assert result["parsed"]["domain_name"] == "example.com"
    assert result["parsed"]["registrar"] == "Example Registrar"
    assert result["error"] is None


@patch("netdoctor.core.whois.whois")
@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", True)
def test_query_whois_python_whois_list_fields(mock_whois):
    """Test WHOIS query with list fields."""
    mock_whois_data = Mock()
    mock_whois_data.text = "Domain Name: example.com"
    mock_whois_data.domain_name = ["example.com", "EXAMPLE.COM"]
    mock_whois_data.creation_date = ["2020-01-01", "2020-01-02"]
    mock_whois_data.expiration_date = "2025-01-01"
    mock_whois_data.updated_date = None
    mock_whois_data.name_servers = None
    mock_whois_data.status = None

    mock_whois.whois.return_value = mock_whois_data

    result = query_whois("example.com")

    assert result["method"] == "python-whois"
    assert result["parsed"]["domain_name"] == "example.com"  # Should take first item
    assert result["parsed"]["creation_date"] == "2020-01-01"


@patch("netdoctor.core.whois.whois")
@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", True)
def test_query_whois_python_whois_no_text_attr(mock_whois):
    """Test WHOIS query when text attribute is not available."""
    mock_whois_data = Mock()
    del mock_whois_data.text  # Remove text attribute
    mock_whois_data.__str__ = Mock(return_value="Domain: example.com")
    mock_whois_data.domain_name = "example.com"

    mock_whois.whois.return_value = mock_whois_data

    result = query_whois("example.com")

    assert result["method"] == "python-whois"
    assert result["raw"] is not None
    assert "example.com" in result["raw"]


@patch("netdoctor.core.whois.whois")
@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", True)
def test_query_whois_python_whois_exception(mock_whois):
    """Test WHOIS query when python-whois raises exception."""
    mock_whois.whois.side_effect = Exception("WHOIS query failed")

    # Should fallback to subprocess
    with patch("shutil.which", return_value="/usr/bin/whois"):
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(
                returncode=0, stdout="Domain: example.com", stderr=""
            )

            result = query_whois("example.com")

            # Should fallback to subprocess
            assert result["method"] == "subprocess" or result["error"] is not None


@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", False)
@patch("shutil.which")
@patch("subprocess.run")
def test_query_whois_subprocess_success(mock_subprocess, mock_which):
    """Test WHOIS query using subprocess."""
    mock_which.return_value = "/usr/bin/whois"
    mock_subprocess.return_value = Mock(
        returncode=0,
        stdout="Domain Name: example.com\nRegistrar: Example Registrar",
        stderr="",
    )

    result = query_whois("example.com")

    assert result["method"] == "subprocess"
    assert result["raw"] is not None
    assert "example.com" in result["raw"]
    assert result["error"] is None
    mock_subprocess.assert_called_once()


@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", False)
@patch("shutil.which")
@patch("subprocess.run")
def test_query_whois_subprocess_nonzero_exit(mock_subprocess, mock_which):
    """Test WHOIS query when subprocess returns non-zero but has output."""
    mock_which.return_value = "/usr/bin/whois"
    mock_subprocess.return_value = Mock(
        returncode=1,
        stdout="Domain Name: example.com",
        stderr="",
    )

    result = query_whois("example.com")

    # Should still use the output if available
    assert result["raw"] is not None
    assert "example.com" in result["raw"]


@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", False)
@patch("shutil.which")
@patch("subprocess.run")
def test_query_whois_subprocess_timeout(mock_subprocess, mock_which):
    """Test WHOIS query timeout."""
    mock_which.return_value = "/usr/bin/whois"
    mock_subprocess.side_effect = subprocess.TimeoutExpired("whois", 10.0)

    result = query_whois("example.com")

    assert result["error"] is not None
    error_lower = result["error"].lower() if result["error"] else ""
    assert "timeout" in error_lower or "timed out" in error_lower


@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", False)
@patch("shutil.which")
def test_query_whois_no_whois_command(mock_which):
    """Test WHOIS query when whois command is not found."""
    mock_which.return_value = None

    result = query_whois("example.com")

    assert result["error"] is not None
    assert "not found" in result["error"].lower() or "not available" in result["error"].lower()


@patch("netdoctor.core.whois.PYTHON_WHOIS_AVAILABLE", False)
@patch("shutil.which")
@patch("subprocess.run")
def test_query_whois_subprocess_exception(mock_subprocess, mock_which):
    """Test WHOIS query when subprocess raises exception."""
    mock_which.return_value = "/usr/bin/whois"
    mock_subprocess.side_effect = Exception("Subprocess error")

    result = query_whois("example.com")

    assert result["error"] is not None
    assert "failed" in result["error"].lower()

