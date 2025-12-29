"""
System overview UI.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import QTimer, QThreadPool
from typing import Optional
import pyqtgraph as pg

from netdoctor.workers.task_worker import TaskWorker, WorkerSignals
from netdoctor.core import systeminfo
from netdoctor.gui.widgets.cards import KPICard
from netdoctor.gui.widgets.ui_components import SectionHeader, CardContainer, LoadingSpinner


class SystemView(QWidget):
    """System overview view with KPI cards and live monitoring."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.refresh_timer: Optional[QTimer] = None
        self.cpu_history = []
        self.memory_history = []
        self.max_history = 60  # Keep last 60 data points
        self.init_ui()
        self.load_system_info()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Page header with controls
        header = SectionHeader("System Overview", "Monitor system resources and network interfaces")
        self.stop_monitoring_button = header.add_action_button("Stop Monitoring", self.stop_monitoring, "danger")
        self.stop_monitoring_button.setEnabled(False)
        self.start_monitoring_button = header.add_action_button("Start Monitoring", self.start_monitoring, "primary")
        layout.addWidget(header)

        # KPI Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.cpu_card = KPICard("CPU Usage", "0%")
        self.memory_card = KPICard("Memory Usage", "0%")
        self.disk_card = KPICard("Disk Usage", "0%")
        self.uptime_card = KPICard("Uptime", "0s")

        cards_layout.addWidget(self.cpu_card)
        cards_layout.addWidget(self.memory_card)
        cards_layout.addWidget(self.disk_card)
        cards_layout.addWidget(self.uptime_card)

        layout.addLayout(cards_layout)

        # Charts row in cards
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # CPU chart card
        cpu_chart_card = CardContainer(hover_elevation=False)
        cpu_chart_layout = QVBoxLayout(cpu_chart_card)
        cpu_chart_layout.setSpacing(12)

        cpu_chart_label = QLabel("CPU Usage")
        cpu_chart_label.setObjectName("sectionTitle")
        cpu_chart_layout.addWidget(cpu_chart_label)

        self.cpu_chart = pg.PlotWidget()
        self.cpu_chart.setBackground("#1e293b")  # bg_sidebar
        self.cpu_chart.setLabel("left", "Usage (%)", color="#f1f5f9")  # text_primary
        self.cpu_chart.setLabel("bottom", "Time", color="#f1f5f9")  # text_primary
        self.cpu_chart.setYRange(0, 100)
        self.cpu_chart.getAxis("left").setPen(pg.mkPen(color="#f1f5f9"))  # text_primary
        self.cpu_chart.getAxis("bottom").setPen(pg.mkPen(color="#f1f5f9"))  # text_primary
        self.cpu_line = self.cpu_chart.plot([], [], pen=pg.mkPen(color="#3b82f6", width=2))  # primary_blue
        cpu_chart_layout.addWidget(self.cpu_chart)

        charts_layout.addWidget(cpu_chart_card, 1)

        # Memory chart card
        memory_chart_card = CardContainer(hover_elevation=False)
        memory_chart_layout = QVBoxLayout(memory_chart_card)
        memory_chart_layout.setSpacing(12)

        memory_chart_label = QLabel("Memory Usage")
        memory_chart_label.setObjectName("sectionTitle")
        memory_chart_layout.addWidget(memory_chart_label)

        self.memory_chart = pg.PlotWidget()
        self.memory_chart.setBackground("#1e293b")  # bg_sidebar
        self.memory_chart.setLabel("left", "Usage (%)", color="#f1f5f9")  # text_primary
        self.memory_chart.setLabel("bottom", "Time", color="#f1f5f9")  # text_primary
        self.memory_chart.setYRange(0, 100)
        self.memory_chart.getAxis("left").setPen(pg.mkPen(color="#f1f5f9"))  # text_primary
        self.memory_chart.getAxis("bottom").setPen(pg.mkPen(color="#f1f5f9"))  # text_primary
        self.memory_line = self.memory_chart.plot([], [], pen=pg.mkPen(color="#60a5fa", width=2))  # secondary_blue
        memory_chart_layout.addWidget(self.memory_chart)

        charts_layout.addWidget(memory_chart_card, 1)

        layout.addLayout(charts_layout)

        # Network interfaces section
        interfaces_section = SectionHeader("Network Interfaces", "Active network adapters and statistics")
        layout.addWidget(interfaces_section)

        # Interfaces table in card
        interfaces_card = CardContainer(hover_elevation=False)
        interfaces_card_layout = QVBoxLayout(interfaces_card)
        interfaces_card_layout.setContentsMargins(0, 0, 0, 0)
        
        self.interfaces_table = QTableWidget()
        self.interfaces_table.setColumnCount(6)
        self.interfaces_table.setHorizontalHeaderLabels(["Name", "IP", "MAC", "MTU", "RX Bytes", "TX Bytes"])
        self.interfaces_table.setAlternatingRowColors(True)
        interfaces_card_layout.addWidget(self.interfaces_table)
        
        layout.addWidget(interfaces_card)

    def load_system_info(self):
        """Load system information via worker."""
        signals = WorkerSignals()
        signals.finished.connect(self.on_system_info_loaded)
        signals.error.connect(self.on_system_info_error)

        def system_task(signals, cancel_flag):
            return systeminfo.get_system_overview()

        worker = TaskWorker(system_task, signals)
        QThreadPool.globalInstance().start(worker)

    def on_system_info_loaded(self, data):
        """Handle system info loaded."""
        if not data:
            return

        # Update KPI cards
        cpu_percent = data.get("cpu_percent", 0)
        self.cpu_card.set_value(f"{cpu_percent:.1f}%")

        memory_total = data.get("memory_total", 1)
        memory_used = data.get("memory_used", 0)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        self.memory_card.set_value(f"{memory_percent:.1f}%")

        # Disk usage (use first partition)
        disk_partitions = data.get("disk_partitions", [])
        if disk_partitions:
            disk = disk_partitions[0]
            disk_total = disk.get("total", 1)
            disk_used = disk.get("used", 0)
            disk_percent = (disk_used / disk_total * 100) if disk_total > 0 else 0
            self.disk_card.set_value(f"{disk_percent:.1f}%")
        else:
            self.disk_card.set_value("N/A")

        # Uptime
        uptime_seconds = data.get("uptime", 0)
        uptime_hours = uptime_seconds / 3600
        if uptime_hours < 24:
            self.uptime_card.set_value(f"{uptime_hours:.1f}h")
        else:
            self.uptime_card.set_value(f"{uptime_hours / 24:.1f}d")

        # Update interfaces table
        interfaces = data.get("interfaces", [])
        self.interfaces_table.setRowCount(len(interfaces))
        for row, iface in enumerate(interfaces):
            self.interfaces_table.setItem(row, 0, QTableWidgetItem(str(iface.get("name", ""))))
            self.interfaces_table.setItem(row, 1, QTableWidgetItem(str(iface.get("ip", ""))))
            self.interfaces_table.setItem(row, 2, QTableWidgetItem(str(iface.get("mac", ""))))
            self.interfaces_table.setItem(row, 3, QTableWidgetItem(str(iface.get("mtu", ""))))
            self.interfaces_table.setItem(row, 4, QTableWidgetItem(str(iface.get("rx_bytes", 0))))
            self.interfaces_table.setItem(row, 5, QTableWidgetItem(str(iface.get("tx_bytes", 0))))

    def on_system_info_error(self, error_msg: str):
        """Handle system info error."""
        print(f"System info error: {error_msg}")

    def start_monitoring(self):
        """Start live monitoring."""
        if self.start_monitoring_button:
            self.start_monitoring_button.setEnabled(False)
        if self.stop_monitoring_button:
            self.stop_monitoring_button.setEnabled(True)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_monitoring)
        self.refresh_timer.start(1000)  # 1 second

        # Initial update
        self.update_monitoring()

    def stop_monitoring(self):
        """Stop live monitoring."""
        if self.refresh_timer:
            self.refresh_timer.stop()
            self.refresh_timer = None

        if self.start_monitoring_button:
            self.start_monitoring_button.setEnabled(True)
        if self.stop_monitoring_button:
            self.stop_monitoring_button.setEnabled(False)

    def update_monitoring(self):
        """Update monitoring data."""
        signals = WorkerSignals()
        signals.finished.connect(self.on_monitoring_update)

        def monitoring_task(signals, cancel_flag):
            return systeminfo.get_system_overview()

        worker = TaskWorker(monitoring_task, signals)
        QThreadPool.globalInstance().start(worker)

    def on_monitoring_update(self, data):
        """Handle monitoring update."""
        if not data:
            return

        # Update CPU
        cpu_percent = data.get("cpu_percent", 0)
        self.cpu_card.set_value(f"{cpu_percent:.1f}%")
        self.cpu_history.append(cpu_percent)
        if len(self.cpu_history) > self.max_history:
            self.cpu_history.pop(0)
        self.cpu_line.setData(list(range(len(self.cpu_history))), self.cpu_history)

        # Update Memory
        memory_total = data.get("memory_total", 1)
        memory_used = data.get("memory_used", 0)
        memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0
        self.memory_card.set_value(f"{memory_percent:.1f}%")
        self.memory_history.append(memory_percent)
        if len(self.memory_history) > self.max_history:
            self.memory_history.pop(0)
        self.memory_line.setData(list(range(len(self.memory_history))), self.memory_history)
