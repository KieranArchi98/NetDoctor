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
    QSplitter,
)
from PySide6.QtCore import QThreadPool, Qt
from typing import Optional
import pyqtgraph as pg

from netdoctor import config

import uuid
from datetime import datetime

from netdoctor.gui.widgets.results_table import ResultsTableView
from netdoctor.gui.widgets.ui_components import SectionHeader, CardContainer, LoadingOverlay
from netdoctor.gui.widgets.cards import KPICard
from netdoctor.workers.task_worker import TaskWorker, WorkerSignals
from netdoctor.core import ping
from netdoctor.storage import history


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
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        from pathlib import Path
        icon_dir = Path(__file__).parent.parent.parent / "resources" / "icons"

        # Page header
        header = SectionHeader(
            "Ping Tool", 
            "Test network connectivity and measure latency",
            icon_path=str(icon_dir / "ping.svg")
        )
        header.add_action_button("Export CSV", self.export_csv, "secondary")
        layout.addWidget(header)

        # Input section in a card
        input_card = CardContainer()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(24, 24, 24, 24)
        input_layout.setSpacing(20)

        # Host and Options row
        form_layout = QHBoxLayout()
        form_layout.setSpacing(32)

        # Host input
        host_group = QVBoxLayout()
        host_group.setSpacing(8)
        host_label = QLabel("TARGET HOST")
        host_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1px;")
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("127.0.0.1 or example.com")
        self.host_input.setFixedHeight(40)
        host_group.addWidget(host_label)
        host_group.addWidget(self.host_input)
        form_layout.addLayout(host_group, 1)

        # Count input
        count_group = QVBoxLayout()
        count_group.setSpacing(8)
        count_label = QLabel("PACKET COUNT")
        count_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1px;")
        self.count_input = QSpinBox()
        self.count_input.setMinimum(1)
        self.count_input.setMaximum(100)
        self.count_input.setValue(4)
        self.count_input.setFixedHeight(40)
        self.count_input.setMinimumWidth(100)
        count_group.addWidget(count_label)
        count_group.addWidget(self.count_input)
        form_layout.addLayout(count_group)
        
        input_layout.addLayout(form_layout)

        # Action buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addStretch()
        
        self.start_button = QPushButton("Start Ping")
        self.start_button.setObjectName("primaryButton")
        self.start_button.setFixedWidth(140)
        self.start_button.setFixedHeight(42)
        self.start_button.clicked.connect(self.start_ping)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("dangerButton")
        self.stop_button.setFixedWidth(100)
        self.stop_button.setFixedHeight(42)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_ping)
        
        # Add press animations
        from netdoctor.gui.widgets.animations import scale_press
        self.start_button.pressed.connect(lambda: scale_press(self.start_button))
        self.stop_button.pressed.connect(lambda: scale_press(self.stop_button))
        
        button_row.addWidget(self.stop_button)
        button_row.addWidget(self.start_button)
        input_layout.addLayout(button_row)
        
        layout.addWidget(input_card)

        # Metrics row (KPI Cards)
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(24)
        
        self.min_rtt_card = KPICard("MIN LATENCY", "--", self)
        self.avg_rtt_card = KPICard("AVG LATENCY", "--", self)
        self.max_rtt_card = KPICard("MAX LATENCY", "--", self)
        
        metrics_row.addWidget(self.min_rtt_card)
        metrics_row.addWidget(self.avg_rtt_card)
        metrics_row.addWidget(self.max_rtt_card)
        
        layout.addLayout(metrics_row)

        # Results section - dynamic splitter
        self.results_splitter = QSplitter(Qt.Horizontal)
        self.results_splitter.setHandleWidth(1)
        self.results_splitter.setStyleSheet("QSplitter::handle { background-color: transparent; }")

        # Table card
        table_card = CardContainer()
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(20, 20, 20, 20)
        table_card_layout.setSpacing(16)
        
        table_header = QLabel("RESPONSE LOG")
        table_header.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1.5px;")
        table_card_layout.addWidget(table_header)

        self.results_table = ResultsTableView(["seq", "host", "rtt_ms", "ttl", "status"])
        table_card_layout.addWidget(self.results_table)

        self.results_splitter.addWidget(table_card)

        # Chart card
        chart_card = CardContainer()
        chart_card_layout = QVBoxLayout(chart_card)
        chart_card_layout.setContentsMargins(20, 20, 20, 20)
        chart_card_layout.setSpacing(16)

        chart_header = QLabel("LATENCY TREND")
        chart_header.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1.5px;")
        chart_card_layout.addWidget(chart_header)

        self.chart = pg.PlotWidget()
        self.chart.setBackground("transparent")
        self.chart.showGrid(x=True, y=True, alpha=0.1)
        self.chart.setAntialiasing(True)
        
        # Setup Axis
        styles = {"color": "#94a3b8", "font-size": "10px"}
        self.chart.setLabel("left", "RTT (ms)", **styles)
        self.chart.setLabel("bottom", "Packet Seq", **styles)
        
        self.chart_line = self.chart.plot([], [], 
            pen=pg.mkPen(color="#3b82f6", width=3, cosmetic=True),
            symbol='o', symbolSize=8, symbolBrush="#3b82f6",
            fillLevel=0, brush=(59, 130, 246, 30) # Soft blue fill
        )
        chart_card_layout.addWidget(self.chart)

        self.results_splitter.addWidget(chart_card)
        self.results_splitter.setSizes([600, 400])

        layout.addWidget(self.results_splitter, 1)
        
        # Entrance animations
        from netdoctor.gui.widgets.animations import fade_in
        fade_in(self, duration=400)
        
        # Empty state label (hidden by default)
        self.empty_state = QLabel("Enter a host and click 'Start Ping' to begin")
        self.empty_state.setObjectName("sectionSubtitle")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.hide()
        layout.addWidget(self.empty_state)
        
        # Loading overlay
        self.loading_overlay = LoadingOverlay(self)

    def start_ping(self):
        """Start ping operation."""
        host = self.host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Error", "Please enter a host to ping")
            return

        if not config.PRIVACY_ACKNOWLEDGED:
            QMessageBox.warning(self, "Privacy Warning", "You must acknowledge the privacy/legal terms in Settings before running scans.")
            return

        count = self.count_input.value()
        self.ping_results = []

        # Clear previous results
        self.results_table.model.clear()
        self.chart_line.setData([], [])
        self.empty_state.hide()
        
        # Reset KPI cards
        self.min_rtt_card.set_value("--")
        self.avg_rtt_card.set_value("--")
        self.max_rtt_card.set_value("--")

        # Disable start, enable stop
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.host_input.setEnabled(False)
        self.count_input.setEnabled(False)
        
        # Show loading state if it's likely to take a while
        if count > 1:
            self.loading_overlay.start(f"Pinging {host}...")

        # Create worker
        signals = WorkerSignals(parent=self)
        signals.row.connect(self.on_ping_result)
        signals.finished.connect(self.on_ping_finished)
        signals.error.connect(self.on_ping_error)

        def ping_task(signals, cancel_flag):
            all_results = []
            for i in range(count):
                if cancel_flag.is_set():
                    break
                # Single ping for responsiveness
                results = ping.ping_host(host, count=1, timeout=2.0)
                if results:
                    result = results[0]
                    signals.row.emit(result)
                    all_results.append(result)
            return all_results

        self.current_worker = TaskWorker(ping_task, signals)
        QThreadPool.globalInstance().start(self.current_worker)

    def stop_ping(self):
        """Stop ping operation."""
        if self.current_worker:
            self.current_worker.cancel()
        # Do NOT call on_ping_finished here. The worker will emit finished signal.

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

        # Update chart and KPIs
        if result.get("success") and result.get("rtt_ms") is not None:
            seqs = [r.get("seq", 0) for r in self.ping_results if r.get("success") and r.get("rtt_ms") is not None]
            rtts = [r.get("rtt_ms", 0) for r in self.ping_results if r.get("success") and r.get("rtt_ms") is not None]
            if seqs and rtts:
                self.chart_line.setData(seqs, rtts)
                
                # Update metrics
                min_rtt = min(rtts)
                max_rtt = max(rtts)
                avg_rtt = sum(rtts) / len(rtts)
                
                self.min_rtt_card.set_value(f"{min_rtt:.1f}ms")
                self.max_rtt_card.set_value(f"{max_rtt:.1f}ms")
                self.avg_rtt_card.set_value(f"{avg_rtt:.1f}ms")

    def on_ping_finished(self, result):
        """Handle ping completion."""
        # Capture target before clearing
        target_host = self.host_input.text().strip()

        # Only ignore if this signal is strictly from an OLD worker
        if self.sender() and self.current_worker:
             if self.sender() != self.current_worker.signals:
                 return

        self.start_button.setEnabled(True)
        self.count_input.setEnabled(True)
        self.host_input.setEnabled(True)
        self.host_input.clear()
        self.stop_button.setEnabled(False)
        self.loading_overlay.stop()
        self.current_worker = None
        
        # Save session to history
        if self.ping_results:
            session_id = f"ping_{uuid.uuid4().hex[:8]}"
            meta = {
                "tool": "Ping",
                "target": target_host,
                "timestamp": datetime.now().isoformat()
            }
            history.save_session(session_id, meta, self.ping_results)
        
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
                if self.window() and hasattr(self.window(), "show_toast"):
                    self.window().show_toast(f"Results exported to {Path(filename).name}", "success")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
