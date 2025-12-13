"""
Smoke tests for GUI views.

These are basic tests to ensure views can be instantiated without errors.
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from netdoctor.gui.views.ping_view import PingView
from netdoctor.gui.views.system_view import SystemView
from netdoctor.gui.views.portscan_view import PortScanView


@pytest.fixture
def app():
    """Create QApplication for testing Qt widgets."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    return app


def test_ping_view_creation(app):
    """Test that PingView can be created."""
    view = PingView()
    assert view is not None
    assert hasattr(view, "host_input")
    assert hasattr(view, "start_button")
    assert hasattr(view, "results_table")


def test_system_view_creation(app):
    """Test that SystemView can be created."""
    view = SystemView()
    assert view is not None
    assert hasattr(view, "cpu_card")
    assert hasattr(view, "interfaces_table")


def test_portscan_view_creation(app):
    """Test that PortScanView can be created."""
    view = PortScanView()
    assert view is not None
    assert hasattr(view, "host_input")
    assert hasattr(view, "port_input")
    assert hasattr(view, "results_table")


def test_ping_view_ui_elements(app):
    """Test that PingView has required UI elements."""
    view = PingView()
    assert view.host_input is not None
    assert view.count_input is not None
    assert view.start_button is not None
    assert view.stop_button is not None
    assert view.results_table is not None
    assert view.chart is not None


def test_system_view_ui_elements(app):
    """Test that SystemView has required UI elements."""
    view = SystemView()
    assert view.cpu_card is not None
    assert view.memory_card is not None
    assert view.disk_card is not None
    assert view.uptime_card is not None
    assert view.interfaces_table is not None


def test_portscan_view_ui_elements(app):
    """Test that PortScanView has required UI elements."""
    view = PortScanView()
    assert view.host_input is not None
    assert view.port_input is not None
    assert view.thread_input is not None
    assert view.start_button is not None
    assert view.stop_button is not None
    assert view.results_table is not None

