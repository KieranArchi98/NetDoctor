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

from netdoctor import config
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
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        from pathlib import Path
        icon_dir = Path(__file__).parent.parent.parent / "resources" / "icons"

        # Page header
        header = SectionHeader(
            "Port Scanner", 
            "Scan TCP ports and retrieve service banners",
            icon_path=str(icon_dir / "portscan.svg")
        )
        layout.addWidget(header)

        # Input section in card
        input_card = CardContainer()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(24, 24, 24, 24)
        input_layout.setSpacing(20)

        # Form grid-like layout
        form_row = QHBoxLayout()
        form_row.setSpacing(32)

        # 1. Host Input
        host_group = QVBoxLayout()
        host_group.setSpacing(8)
        host_label = QLabel("TARGET HOST")
        host_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1px;")
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("e.g., 127.0.0.1")
        self.host_input.setFixedHeight(40)
        host_group.addWidget(host_label)
        host_group.addWidget(self.host_input)
        form_row.addLayout(host_group, 2)

        # 2. Port Range
        port_group = QVBoxLayout()
        port_group.setSpacing(8)
        port_label = QLabel("PORT RANGE")
        port_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1px;")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("80,443,8000-8010")
        self.port_input.setText("80,443,8080")
        self.port_input.setFixedHeight(40)
        port_group.addWidget(port_label)
        port_group.addWidget(self.port_input)
        form_row.addLayout(port_group, 2)

        # 3. Settings (Threads + Banner)
        settings_group = QVBoxLayout()
        settings_group.setSpacing(8)
        settings_label = QLabel("SCAN SETTINGS")
        settings_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1px;")
        
        settings_controls = QHBoxLayout()
        settings_controls.setSpacing(12)
        
        self.thread_input = QSpinBox()
        self.thread_input.setMinimum(1)
        self.thread_input.setMaximum(500)
        self.thread_input.setValue(50)
        self.thread_input.setFixedHeight(40)
        self.thread_input.setToolTip("Thread count")
        
        self.banner_checkbox = QCheckBox("Banner")
        self.banner_checkbox.setToolTip("Enable banner grabbing")
        self.banner_checkbox.setStyleSheet("font-size: 12px; color: #94a3b8;")
        
        settings_controls.addWidget(self.thread_input)
        settings_controls.addWidget(self.banner_checkbox)
        
        settings_group.addWidget(settings_label)
        settings_group.addLayout(settings_controls)
        form_row.addLayout(settings_group, 1)

        input_layout.addLayout(form_row)

        # Action buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addStretch()
        
        self.start_button = QPushButton("Start Port Scan")
        self.start_button.setObjectName("primaryButton")
        self.start_button.setFixedWidth(160)
        self.start_button.setFixedHeight(42)
        self.start_button.clicked.connect(self.start_scan)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("dangerButton")
        self.stop_button.setFixedWidth(100)
        self.stop_button.setFixedHeight(42)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scan)
        
        # Add press animations
        from netdoctor.gui.widgets.animations import scale_press
        self.start_button.pressed.connect(lambda: scale_press(self.start_button))
        self.stop_button.pressed.connect(lambda: scale_press(self.stop_button))
        
        button_row.addWidget(self.stop_button)
        button_row.addWidget(self.start_button)
        input_layout.addLayout(button_row)
        
        layout.addWidget(input_card)

        # Results section
        results_card = CardContainer()
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(16)

        results_label = QLabel("SCAN RESULTS")
        results_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1.5px;")
        results_layout.addWidget(results_label)

        self.results_table = ResultsTableView(["port", "state", "service", "banner"])
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_banner_context_menu)
        results_layout.addWidget(self.results_table)

        layout.addWidget(results_card, 1)

        # Entrance animations
        from netdoctor.gui.widgets.animations import fade_in
        fade_in(self, duration=400)

    def start_scan(self):
        """Start port scan."""
        host = self.host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Error", "Please enter a host to scan")
            return

        if not config.PRIVACY_ACKNOWLEDGED:
            QMessageBox.warning(self, "Privacy Warning", "You must acknowledge the privacy/legal terms in Settings before running scans.")
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
        signals = WorkerSignals(parent=self)
        signals.row.connect(self.on_scan_result)
        signals.finished.connect(self.on_scan_finished)
        signals.error.connect(self.on_scan_error)

        def scan_task(signals, cancel_flag):
            results = []
            for result in portscanner.scan_ports_iter(
                host, ports, timeout=1.0, concurrency=threads, banner_grab=banner_grab
            ):
                if cancel_flag.is_set():
                    break
                signals.row.emit(result)
                results.append(result)
            return results

        self.current_worker = TaskWorker(scan_task, signals)
        QThreadPool.globalInstance().start(self.current_worker)

    def stop_scan(self):
        """Stop port scan."""
        if self.current_worker:
            self.current_worker.cancel()
        # Do NOT call on_scan_finished here. The worker will emit finished signal.

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
        """Handle scan orientation."""
        # Capture inputs before clearing
        target_host = self.host_input.text().strip()
        target_ports = self.port_input.text().strip()

        # Only ignore if this signal is strictly from an OLD worker
        if self.sender() and self.current_worker:
             if self.sender() != self.current_worker.signals:
                 return

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.host_input.clear()
        self.port_input.clear()
        self.thread_input.setEnabled(True)
        self.current_worker = None
        
        if self.scan_results and self.window() and hasattr(self.window(), "show_toast"):
            self.window().show_toast(f"Scan complete: {len(self.scan_results)} open ports found", "success")
        
        # Save session to history
        if self.scan_results:
            session_id = f"scan_{uuid.uuid4().hex[:8]}"
            meta = {
                "tool": "PortScan",
                "target": target_host,
                "timestamp": datetime.now().isoformat(),
                "ports": target_ports
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
