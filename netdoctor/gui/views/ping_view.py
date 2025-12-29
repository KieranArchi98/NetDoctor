"""
UI and glue for ping module.
"""

import csv
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QSpinBox,
    QFileDialog,
    QMessageBox,
    QFrame,
)
from PySide6.QtCore import QThreadPool, Qt
from typing import Optional
import pyqtgraph as pg

from netdoctor.workers.task_worker import TaskWorker, WorkerSignals
from netdoctor.core import ping
from netdoctor.gui.widgets.results_table import ResultsTableView
from netdoctor.gui.widgets.ui_components import SectionHeader, CardContainer, LoadingSpinner


class PingView(QWidget):
    """Ping view with table and chart."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_worker: Optional[TaskWorker] = None
        self.ping_results = []
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Page header
        header = SectionHeader("Ping Tool", "Test network connectivity and measure latency")
        header.add_action_button("Export CSV", self.export_csv, "secondary")
        layout.addWidget(header)

        # Input section in a card
        input_card = CardContainer(hover_elevation=False)
        input_layout = QVBoxLayout(input_card)
        input_layout.setSpacing(16)

        # Host input row
        host_row = QHBoxLayout()
        host_row.setSpacing(12)
        host_label = QLabel("Host:")
        host_label.setMinimumWidth(80)
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("127.0.0.1 or example.com")
        host_row.addWidget(host_label)
        host_row.addWidget(self.host_input, 1)
        input_layout.addLayout(host_row)

        # Options row
        options_row = QHBoxLayout()
        options_row.setSpacing(12)
        
        count_label = QLabel("Count:")
        count_label.setMinimumWidth(80)
        self.count_input = QSpinBox()
        self.count_input.setMinimum(1)
        self.count_input.setMaximum(100)
        self.count_input.setValue(4)
        self.count_input.setMaximumWidth(100)
        
        options_row.addWidget(count_label)
        options_row.addWidget(self.count_input)
        options_row.addStretch()
        
        # Action buttons
        self.start_button = QPushButton("Start Ping")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self.start_ping)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("dangerButton")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_ping)
        
        # Add press animations
        from netdoctor.gui.widgets.button_helpers import add_press_animation
        add_press_animation(self.start_button)
        add_press_animation(self.stop_button)
        
        options_row.addWidget(self.start_button)
        options_row.addWidget(self.stop_button)
        input_layout.addLayout(options_row)
        
        layout.addWidget(input_card)

        # Results section - split view
        results_layout = QHBoxLayout()
        results_layout.setSpacing(20)

        # Table card
        table_card = CardContainer(hover_elevation=False)
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setSpacing(12)
        
        table_header = QLabel("Results")
        table_header.setObjectName("sectionTitle")
        table_card_layout.addWidget(table_header)

        self.results_table = ResultsTableView(["seq", "host", "rtt_ms", "ttl", "status"])
        table_card_layout.addWidget(self.results_table)

        results_layout.addWidget(table_card, 1)

        # Chart card
        chart_card = CardContainer(hover_elevation=False)
        chart_card_layout = QVBoxLayout(chart_card)
        chart_card_layout.setSpacing(12)

        chart_header = QLabel("Latency Chart")
        chart_header.setObjectName("sectionTitle")
        chart_card_layout.addWidget(chart_header)

        self.chart = pg.PlotWidget()
        self.chart.setBackground("#1e293b")  # bg_sidebar
        self.chart.setLabel("left", "RTT (ms)", color="#f1f5f9")  # text_primary
        self.chart.setLabel("bottom", "Sequence", color="#f1f5f9")  # text_primary
        self.chart.getAxis("left").setPen(pg.mkPen(color="#f1f5f9"))  # text_primary
        self.chart.getAxis("bottom").setPen(pg.mkPen(color="#f1f5f9"))  # text_primary
        self.chart_line = self.chart.plot([], [], pen=pg.mkPen(color="#3b82f6", width=2))  # primary_blue
        chart_card_layout.addWidget(self.chart)

        results_layout.addWidget(chart_card, 1)

        layout.addLayout(results_layout, 1)
        
        # Empty state label (hidden by default)
        self.empty_state = QLabel("Enter a host and click 'Start Ping' to begin")
        self.empty_state.setObjectName("sectionSubtitle")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.hide()
        layout.addWidget(self.empty_state)

    def start_ping(self):
        """Start ping operation."""
        host = self.host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Error", "Please enter a host to ping")
            return

        count = self.count_input.value()
        self.ping_results = []

        # Clear previous results
        self.results_table.model.clear()
        self.chart_line.setData([], [])
        self.empty_state.hide()

        # Disable start, enable stop
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.host_input.setEnabled(False)
        self.count_input.setEnabled(False)

        # Create worker
        signals = WorkerSignals()
        signals.row.connect(self.on_ping_result)
        signals.finished.connect(self.on_ping_finished)
        signals.error.connect(self.on_ping_error)

        def ping_task(signals, cancel_flag):
            results = ping.ping_host(host, count=count, timeout=2.0)
            for result in results:
                if cancel_flag.is_set():
                    break
                signals.row.emit(result)
            return results

        self.current_worker = TaskWorker(ping_task, signals)
        QThreadPool.globalInstance().start(self.current_worker)

    def stop_ping(self):
        """Stop ping operation."""
        if self.current_worker:
            self.current_worker.cancel()
        self.on_ping_finished(None)

    def on_ping_result(self, result: dict):
        """Handle ping result."""
        self.ping_results.append(result)
        host = self.host_input.text().strip()

        # Add to table
        table_row = {
            "seq": result.get("seq", ""),
            "host": host,
            "rtt_ms": result.get("rtt_ms", "N/A"),
            "ttl": result.get("ttl", "N/A"),
            "status": "Success" if result.get("success") else "Failed",
        }
        self.results_table.model.add_row(table_row)

        # Update chart
        if result.get("success") and result.get("rtt_ms") is not None:
            seqs = [r.get("seq", 0) for r in self.ping_results if r.get("success") and r.get("rtt_ms")]
            rtts = [r.get("rtt_ms", 0) for r in self.ping_results if r.get("success") and r.get("rtt_ms")]
            if seqs and rtts:
                self.chart_line.setData(seqs, rtts)

    def on_ping_finished(self, result):
        """Handle ping completion."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.host_input.setEnabled(True)
        self.count_input.setEnabled(True)
        self.current_worker = None
        
        # Show empty state if no results
        if not self.ping_results:
            self.empty_state.show()

    def on_ping_error(self, error_msg: str):
        """Handle ping error."""
        QMessageBox.critical(self, "Error", f"Ping failed: {error_msg}")
        self.on_ping_finished(None)

    def export_csv(self):
        """Export results to CSV."""
        if not self.ping_results:
            QMessageBox.information(self, "Info", "No results to export")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "", "CSV Files (*.csv);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["seq", "host", "rtt_ms", "ttl", "status", "error"])
                    writer.writeheader()
                    for result in self.ping_results:
                        writer.writerow(
                            {
                                "seq": result.get("seq", ""),
                                "host": self.host_input.text().strip(),
                                "rtt_ms": result.get("rtt_ms", ""),
                                "ttl": result.get("ttl", ""),
                                "status": "Success" if result.get("success") else "Failed",
                                "error": result.get("error", ""),
                            }
                        )
                QMessageBox.information(self, "Success", f"Results exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
