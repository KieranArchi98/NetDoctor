"""
Dashboard/Overview view.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from netdoctor.gui.widgets.ui_components import SectionHeader, CardContainer
from netdoctor.gui.widgets.cards import KPICard, StatCard
import platform
import socket
import shutil
import datetime
import getpass
import uuid
try:
    import psutil
except ImportError:
    psutil = None


class DashboardView(QWidget):
    """Dashboard overview with quick stats and recent activity."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Setup auto-refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start(3000)  # Refresh every 3 seconds

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Custom Header (Dashboard + User Info)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Left: Dashboard Title
        title_container = QWidget()
        title_lines = QVBoxLayout(title_container)
        title_lines.setContentsMargins(0, 0, 0, 0)
        title_lines.setSpacing(2)
        
        page_title = QLabel("Dashboard")
        page_title.setObjectName("pageTitle")
        page_subtitle = QLabel("Overview of system and network status")
        page_subtitle.setObjectName("sectionSubtitle")
        
        title_lines.addWidget(page_title)
        title_lines.addWidget(page_subtitle)
        header_layout.addWidget(title_container)
        
        header_layout.addStretch()
        
        # Right: User Session Info
        current_user = getpass.getuser()
        user_container = QWidget()
        user_container.setObjectName("kpiCard")
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(16, 8, 16, 8)
        user_layout.setSpacing(8)
        
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 16px;")
        user_label = QLabel(f"User: {current_user}")
        user_label.setStyleSheet("font-weight: 600;")
        
        user_layout.addWidget(user_icon)
        user_layout.addWidget(user_label)
        header_layout.addWidget(user_container)
        
        layout.addLayout(header_layout)

        # Quick stats row (Row 1)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        # Gather System Info
        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)
        os_info = f"{platform.system()} {platform.release()}"
        
        # MAC Address
        mac_num = uuid.getnode()
        mac_addr = ':'.join(['{:02x}'.format((mac_num >> elements) & 0xff) for elements in range(0,48,8)][::-1])

        # Row 1 Cards
        system_card = StatCard("💻", hostname, os_info, "System Info")
        network_card = StatCard("🌐", ip_addr, "", "Local IP Address")
        mac_card = StatCard("🔌", mac_addr, "", "MAC Address")

        stats_layout.addWidget(system_card)
        stats_layout.addWidget(network_card)
        stats_layout.addWidget(mac_card)

        layout.addLayout(stats_layout)

        # Process Tables (Split 50/50)
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(16)

        # Table 1: Top Applications (User)
        apps_container = QWidget()
        apps_layout = QVBoxLayout(apps_container)
        apps_layout.setContentsMargins(0, 0, 0, 0)
        apps_header = SectionHeader("Top Applications", "User processes by usage")
        apps_layout.addWidget(apps_header)
        
        self.app_table = self._create_process_table()
        apps_layout.addWidget(self.app_table)
        tables_layout.addWidget(apps_container)

        # Table 2: Background Processes (System)
        procs_container = QWidget()
        procs_layout = QVBoxLayout(procs_container)
        procs_layout.setContentsMargins(0, 0, 0, 0)
        procs_header = SectionHeader("System Processes", "Background services by usage")
        procs_layout.addWidget(procs_header)
        
        self.proc_table = self._create_process_table()
        procs_layout.addWidget(self.proc_table)
        tables_layout.addWidget(procs_container)

        layout.addLayout(tables_layout)

        # Activity card
        activity_card = CardContainer()
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setSpacing(12)

        empty_label = QLabel("No recent activity")
        empty_label.setObjectName("sectionSubtitle")
        empty_label.setAlignment(Qt.AlignCenter)
        activity_layout.addWidget(empty_label)

        layout.addWidget(activity_card)
        
        # Initial load
        self.refresh_dashboard()

    def _create_process_table(self):
        """Create a styled table for processes."""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Name", "PID", "CPU", "Mem"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setRowCount(5)
        table.AlternatingRowColors = True
        return table

    def refresh_dashboard(self):
        """Update process tables dynamically."""
        if not psutil:
            return

        try:
            current_user = getpass.getuser()
            user_procs = []
            sys_procs = []
            
            # Iterate processes
            for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    p.cpu_percent() # Prime cpu_percent
                    # Simple user filter
                    if p.info['username'] and current_user in p.info['username']:
                        user_procs.append(p)
                    else:
                        sys_procs.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort and slice
            user_procs.sort(key=lambda p: p.info['cpu_percent'] or 0, reverse=True)
            sys_procs.sort(key=lambda p: p.info['cpu_percent'] or 0, reverse=True)
            
            self._update_table(self.app_table, user_procs[:5])
            self._update_table(self.proc_table, sys_procs[:5])
            
        except Exception:
            pass

    def _update_table(self, table, procs):
        """Helper to update a table widget."""
        for row, p in enumerate(procs):
            info = p.info
            name_item = QTableWidgetItem(str(info['name']))
            pid_item = QTableWidgetItem(str(info['pid']))
            cpu_item = QTableWidgetItem(f"{info['cpu_percent']:.1f}%")
            mem_item = QTableWidgetItem(f"{info['memory_percent']:.1f}%")
            
            # Update cells directly
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, pid_item)
            table.setItem(row, 2, cpu_item)
            table.setItem(row, 3, mem_item)

