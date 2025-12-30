import pytest
from unittest.mock import MagicMock, patch
from netdoctor.core import utils

def test_check_python_dependency_installed():
    """Test detection of an installed package."""
    # os is definitely installed
    result = utils.check_python_dependency("os")
    assert result["installed"] is True
    assert result["name"] == "os"

def test_check_python_dependency_missing():
    """Test detection of a missing package."""
    result = utils.check_python_dependency("non_existent_package_xyz")
    assert result["installed"] is False
    assert result["error"] == "Not installed"

@patch("shutil.which")
@patch("subprocess.run")
def test_detect_nmap_success(mock_run, mock_which):
    """Test successful nmap detection."""
    mock_which.return_value = "/usr/bin/nmap"
    mock_run.return_value = MagicMock(returncode=0, stdout="Nmap version 7.94\n")
    
    result = utils.detect_nmap()
    assert result["installed"] is True
    assert result["version"] == "7.94"
    assert result["path"] == "/usr/bin/nmap"

@patch("shutil.which")
def test_detect_nmap_missing(mock_which):
    """Test nmap detection when not in PATH."""
    mock_which.return_value = None
    
    result = utils.detect_nmap()
    assert result["installed"] is False
    assert "not found" in result["error"].lower()

def test_get_all_dependencies():
    """Test that all dependencies are checked."""
    with patch("netdoctor.core.utils.check_python_dependency") as mock_check_py, \
         patch("netdoctor.core.utils.detect_nmap") as mock_detect_nmap:
        
        mock_check_py.return_value = {"installed": True}
        mock_detect_nmap.return_value = {"installed": False}
        
        deps = utils.get_all_dependencies()
        assert "scapy" in deps
        assert "pysnmp" in deps
        assert "nmap" in deps
        assert mock_check_py.call_count == 2
        mock_detect_nmap.assert_called_once()
