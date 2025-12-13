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
)
from PySide6.QtCore import QThreadPool, Qt
import pyqtgraph as pg

from netdoctor.workers.task_worker import TaskWorker, WorkerSignals
from netdoctor.core import ping
from netdoctor.gui.widgets.results_table import ResultsTableView


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
        layout.setSpacing(16)

        # Header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Host input
        host_label = QLabel("Host:")
        host_label.setStyleSheet("color: #E6EEF3;")
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("127.0.0.1 or example.com")
        self.host_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #111827;
                color: #E6EEF3;
                border: 1px solid #374151;
                padding: 8px;
                border-radius: 4px;
            }
        """
        )

        # Count input
        count_label = QLabel("Count:")
        count_label.setStyleSheet("color: #E6EEF3;")
        self.count_input = QSpinBox()
        self.count_input.setMinimum(1)
        self.count_input.setMaximum(100)
        self.count_input.setValue(4)
        self.count_input.setStyleSheet(
            """
            QSpinBox {
                background-color: #111827;
                color: #E6EEF3;
                border: 1px solid #374151;
                padding: 8px;
                border-radius: 4px;
            }
        """
        )

        # Buttons
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #14B8A6;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0D9488;
            }
            QPushButton:disabled {
                background-color: #374151;
                color: #9CA3AF;
            }
        """
        )
        self.start_button.clicked.connect(self.start_ping)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: #EF4444;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:disabled {
                background-color: #374151;
                color: #9CA3AF;
            }
        """
        )
        self.stop_button.clicked.connect(self.stop_ping)

        self.export_button = QPushButton("Export CSV")
        self.export_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3B82F6;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """
        )
        self.export_button.clicked.connect(self.export_csv)

        header_layout.addWidget(host_label)
        header_layout.addWidget(self.host_input, 1)
        header_layout.addWidget(count_label)
        header_layout.addWidget(self.count_input)
        header_layout.addWidget(self.start_button)
        header_layout.addWidget(self.stop_button)
        header_layout.addWidget(self.export_button)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Results section - split view
        results_layout = QHBoxLayout()
        results_layout.setSpacing(16)

        # Table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)

        table_label = QLabel("Results")
        table_label.setStyleSheet("color: #E6EEF3; font-size: 14px; font-weight: bold;")
        table_layout.addWidget(table_label)

        self.results_table = ResultsTableView(["seq", "host", "rtt_ms", "ttl", "status"])
        table_layout.addWidget(self.results_table)

        results_layout.addWidget(table_widget, 1)

        # Chart
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.setContentsMargins(0, 0, 0, 0)

        chart_label = QLabel("Latency Chart")
        chart_label.setStyleSheet("color: #E6EEF3; font-size: 14px; font-weight: bold;")
        chart_layout.addWidget(chart_label)

        self.chart = pg.PlotWidget()
        self.chart.setBackground("#111827")
        self.chart.setLabel("left", "RTT (ms)", color="#E6EEF3")
        self.chart.setLabel("bottom", "Sequence", color="#E6EEF3")
        self.chart.getAxis("left").setPen(pg.mkPen(color="#E6EEF3"))
        self.chart.getAxis("bottom").setPen(pg.mkPen(color="#E6EEF3"))
        self.chart_line = self.chart.plot([], [], pen=pg.mkPen(color="#14B8A6", width=2))
        chart_layout.addWidget(self.chart)

        results_layout.addWidget(chart_widget, 1)

        layout.addLayout(results_layout, 1)

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
