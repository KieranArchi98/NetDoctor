"""
GUI views for each diagnostic module.
"""

from netdoctor.gui.views.ping_view import PingView
from netdoctor.gui.views.system_view import SystemView
from netdoctor.gui.views.portscan_view import PortScanView
from netdoctor.gui.views.dashboard_view import DashboardView

__all__ = [
    "PingView",
    "SystemView",
    "PortScanView",
    "DashboardView",
]
