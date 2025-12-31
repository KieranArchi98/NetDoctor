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
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24) # Standard 8px scale (3 * 8)

        # Custom Header (Dashboard + User Info)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        # Left: Dashboard Title
        title_container = QWidget()
        title_lines = QVBoxLayout(title_container)
        title_lines.setContentsMargins(0, 0, 0, 0)
        title_lines.setSpacing(4)
        
        page_title = QLabel("Dashboard")
        page_title.setObjectName("pageTitle")
        page_title.setStyleSheet("font-size: 32px; font-weight: 800; color: #f8fafc;")
        
        page_subtitle = QLabel("Overview of system and network status")
        page_subtitle.setObjectName("sectionSubtitle")
        page_subtitle.setStyleSheet("font-size: 14px; color: #94a3b8;")
        
        title_lines.addWidget(page_title)
        title_lines.addWidget(page_subtitle)
        header_layout.addWidget(title_container)
        
        header_layout.addStretch()
        
        # Right: User Session Info in a subtle pill
        current_user = getpass.getuser()
        user_container = QWidget()
        user_container.setObjectName("userBadge")
        user_container.setStyleSheet("""
            QWidget#userBadge {
                background-color: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 10px;
            }
        """)
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(12, 6, 12, 6)
        user_layout.setSpacing(8)
        
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 14px;")
        user_label = QLabel(current_user)
        user_label.setStyleSheet("font-weight: 700; color: #3b82f6; font-size: 13px; text-transform: uppercase;")
        
        user_layout.addWidget(user_icon)
        user_layout.addWidget(user_label)
        header_layout.addWidget(user_container, 0, Qt.AlignVCenter)
        
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

        # Row 2: Dynamic System Metrics
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)
        
        self.cpu_card = KPICard("CPU Utilization", "0.0%")
        self.mem_card = KPICard("Memory Usage", "0.0%")
        self.disk_card = KPICard("Disk Usage", "0.0%")
        
        metrics_layout.addWidget(self.cpu_card)
        metrics_layout.addWidget(self.mem_card)
        metrics_layout.addWidget(self.disk_card)
        layout.addLayout(metrics_layout)

        # Row 3: Process Tables with Card Wrappers
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(24)

        from pathlib import Path
        icon_dir = Path(__file__).parent.parent.parent / "resources" / "icons"

        # Table 1: Top Applications (User)
        apps_card = CardContainer()
        apps_layout = QVBoxLayout(apps_card)
        apps_layout.setContentsMargins(16, 16, 16, 16)
        apps_layout.setSpacing(12)
        
        apps_header = SectionHeader(
            "Top Applications", 
            "User processes sorted by CPU usage",
            icon_path=str(icon_dir / "system.svg")
        )
        apps_layout.addWidget(apps_header)
        
        self.app_table = self._create_process_table()
        apps_layout.addWidget(self.app_table)
        tables_layout.addWidget(apps_card)

        # Table 2: Background Processes (System)
        procs_card = CardContainer()
        procs_layout = QVBoxLayout(procs_card)
        procs_layout.setContentsMargins(16, 16, 16, 16)
        procs_layout.setSpacing(12)
        
        procs_header = SectionHeader(
            "System Services", 
            "Background processes sorted by CPU usage",
            icon_path=str(icon_dir / "system.svg")
        )
        procs_layout.addWidget(procs_header)
        
        self.proc_table = self._create_process_table()
        procs_layout.addWidget(self.proc_table)
        tables_layout.addWidget(procs_card)

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
        
        # Initial load and fade-in
        self.refresh_dashboard()
        
        # Entrance animations
        from netdoctor.gui.widgets.animations import fade_in
        fade_in(self, duration=400)

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
        """Update system metrics and process tables."""
        if not psutil:
            return

        try:
            # Update System Metrics
            cpu_percent = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.cpu_card.set_value(f"{cpu_percent:.1f}%")
            self.mem_card.set_value(f"{mem.percent:.1f}%")
            self.disk_card.set_value(f"{disk.percent:.1f}%")

            current_user = getpass.getuser()
            user_procs = []
            sys_procs = []
            
            # Iterate processes (prime CPU percent manually on first run if needed)
            for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    # Simple user filter
                    username = p.info.get('username')
                    if username and current_user in username:
                        user_procs.append(p)
                    else:
                        sys_procs.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
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

