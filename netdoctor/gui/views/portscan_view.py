"""
Port scanner UI.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QSpinBox,
    QMessageBox,
    QTextEdit,
    QCheckBox,
)
from PySide6.QtCore import QThreadPool, Qt
from typing import Optional

import uuid
from datetime import datetime

from netdoctor.workers.task_worker import TaskWorker, WorkerSignals
from netdoctor.core import portscanner
from netdoctor.storage import history
from netdoctor.gui.widgets.results_table import ResultsTableView
from netdoctor.gui.widgets.ui_components import SectionHeader, CardContainer, ModalDialog


class BannerDialog(ModalDialog):
    """Dialog for displaying banner information."""

    def __init__(self, port: int, banner: str, parent=None):
        super().__init__(f"Banner - Port {port}", f"Banner information for port {port}", parent)
        self.setMinimumSize(500, 300)
        
        # Get the layout
        layout = self.layout()
        
        # Create text edit for banner content
        self.banner_text = QTextEdit()
        self.banner_text.setReadOnly(True)
        self.banner_text.setText(banner if banner else "No banner available")
        
        # Insert before button container
        button_container_index = layout.count() - 1
        layout.insertWidget(button_container_index, self.banner_text)
        
        # Update buttons
        self.add_button("Close", "secondary", self.accept)


class PortScanView(QWidget):
    """Port scanner view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_worker: Optional[TaskWorker] = None
        self.scan_results = []
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Page header
        header = SectionHeader("Port Scanner", "Scan TCP ports and retrieve service banners")
        layout.addWidget(header)

        # Input section in card
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

        # Port range and options row
        options_row = QHBoxLayout()
        options_row.setSpacing(12)

        port_label = QLabel("Ports:")
        port_label.setMinimumWidth(80)
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("80,443,8000-8010")
        self.port_input.setText("80,443,8080")

        thread_label = QLabel("Threads:")
        self.thread_input = QSpinBox()
        self.thread_input.setMinimum(1)
        self.thread_input.setMaximum(500)
        self.thread_input.setValue(50)
        self.thread_input.setMaximumWidth(100)

        banner_label = QLabel("Banner Grab:")
        self.banner_checkbox = QCheckBox()

        options_row.addWidget(port_label)
        options_row.addWidget(self.port_input, 1)
        options_row.addWidget(thread_label)
        options_row.addWidget(self.thread_input)
        options_row.addWidget(banner_label)
        options_row.addWidget(self.banner_checkbox)
        options_row.addStretch()
        input_layout.addLayout(options_row)

        # Action buttons row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)

        self.start_button = QPushButton("Start Scan")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self.start_scan)

        self.stop_button = QPushButton("Stop Scan")
        self.stop_button.setObjectName("dangerButton")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scan)
        
        # Add press animations
        from netdoctor.gui.widgets.button_helpers import add_press_animation
        add_press_animation(self.start_button)
        add_press_animation(self.stop_button)
        
        buttons_row.addWidget(self.start_button)
        buttons_row.addWidget(self.stop_button)
        buttons_row.addStretch()
        input_layout.addLayout(buttons_row)

        layout.addWidget(input_card)

        # Results section
        results_section = SectionHeader("Scan Results", "Discovered open ports and services")
        layout.addWidget(results_section)

        # Results table in card
        results_card = CardContainer(hover_elevation=False)
        results_card_layout = QVBoxLayout(results_card)
        results_card_layout.setContentsMargins(0, 0, 0, 0)

        self.results_table = ResultsTableView(["port", "state", "service", "banner"])
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_banner_context_menu)
        results_card_layout.addWidget(self.results_table)

        layout.addWidget(results_card)

    def start_scan(self):
        """Start port scan."""
        host = self.host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Error", "Please enter a host to scan")
            return

        ports = self.port_input.text().strip()
        if not ports:
            QMessageBox.warning(self, "Error", "Please enter ports to scan")
            return

        threads = self.thread_input.value()
        banner_grab = self.banner_checkbox.isChecked()
        self.scan_results = []

        # Clear previous results
        self.results_table.model.clear()

        # Disable start, enable stop
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.host_input.setEnabled(False)
        self.port_input.setEnabled(False)
        self.thread_input.setEnabled(False)

        # Create worker
        signals = WorkerSignals()
        signals.row.connect(self.on_scan_result)
        signals.finished.connect(self.on_scan_finished)
        signals.error.connect(self.on_scan_error)

        def scan_task(signals, cancel_flag):
            results = portscanner.scan_ports(
                host, ports, timeout=1.0, concurrency=threads, banner_grab=banner_grab
            )
            for result in results:
                if cancel_flag.is_set():
                    break
                signals.row.emit(result)
            return results

        self.current_worker = TaskWorker(scan_task, signals)
        QThreadPool.globalInstance().start(self.current_worker)

    def stop_scan(self):
        """Stop port scan."""
        if self.current_worker:
            self.current_worker.cancel()
        self.on_scan_finished(None)

    def on_scan_result(self, result: dict):
        """Handle scan result."""
        self.scan_results.append(result)

        # Add to table
        table_row = {
            "port": result.get("port", ""),
            "state": result.get("state", ""),
            "service": self._guess_service(result.get("port", 0)),
            "banner": "View" if result.get("banner") else "",
        }
        self.results_table.model.add_row(table_row)

    def _guess_service(self, port: int) -> str:
        """Guess service name from port number."""
        common_ports = {
            20: "FTP-DATA",
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            3306: "MySQL",
            5432: "PostgreSQL",
            8080: "HTTP-Proxy",
        }
        return common_ports.get(port, "")

    def on_scan_finished(self, result):
        """Handle scan completion."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.thread_input.setEnabled(True)
        self.current_worker = None
        
        # Save session to history
        if self.scan_results:
            session_id = f"scan_{uuid.uuid4().hex[:8]}"
            meta = {
                "tool": "PortScan",
                "target": self.host_input.text().strip(),
                "timestamp": datetime.now().isoformat(),
                "ports": self.port_input.text().strip()
            }
            history.save_session(session_id, meta, self.scan_results)

    def on_scan_error(self, error_msg: str):
        """Handle scan error."""
        QMessageBox.critical(self, "Error", f"Scan failed: {error_msg}")
        self.on_scan_finished(None)

    def show_banner_context_menu(self, position):
        """Show context menu for banner viewing."""
        index = self.results_table.indexAt(position)
        if index.isValid():
            row = index.row()
            result = self.scan_results[row] if row < len(self.scan_results) else None
            if result and result.get("banner"):
                port = result.get("port", 0)
                banner = result.get("banner", "")
                dialog = BannerDialog(port, banner, self)
                dialog.exec()
