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
    QDialog,
    QTextEdit,
    QCheckBox,
)
from PySide6.QtCore import QThreadPool, Qt
from typing import Optional

from netdoctor.workers.task_worker import TaskWorker, WorkerSignals
from netdoctor.core import portscanner
from netdoctor.gui.widgets.results_table import ResultsTableView


class BannerDialog(QDialog):
    """Dialog for displaying banner information."""

    def __init__(self, port: int, banner: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Banner - Port {port}")
        self.setMinimumSize(500, 300)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #0F1724;
            }
            QTextEdit {
                background-color: #111827;
                color: #E6EEF3;
                border: 1px solid #374151;
                font-family: monospace;
                padding: 8px;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        label = QLabel(f"Banner for port {port}:")
        label.setStyleSheet("color: #E6EEF3; font-size: 14px; font-weight: bold;")
        layout.addWidget(label)

        self.banner_text = QTextEdit()
        self.banner_text.setReadOnly(True)
        self.banner_text.setText(banner if banner else "No banner available")
        layout.addWidget(self.banner_text)

        close_button = QPushButton("Close")
        close_button.setStyleSheet(
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
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)


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
        layout.setSpacing(16)

        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(12)

        # Host input
        host_layout = QHBoxLayout()
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
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input, 1)
        header_layout.addLayout(host_layout)

        # Port range and thread count
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)

        port_label = QLabel("Ports:")
        port_label.setStyleSheet("color: #E6EEF3;")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("80,443,8000-8010")
        self.port_input.setText("80,443,8080")
        self.port_input.setStyleSheet(
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

        thread_label = QLabel("Threads:")
        thread_label.setStyleSheet("color: #E6EEF3;")
        self.thread_input = QSpinBox()
        self.thread_input.setMinimum(1)
        self.thread_input.setMaximum(500)
        self.thread_input.setValue(50)
        self.thread_input.setStyleSheet(
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

        banner_label = QLabel("Banner Grab:")
        banner_label.setStyleSheet("color: #E6EEF3;")

        self.banner_checkbox = QCheckBox()
        self.banner_checkbox.setStyleSheet(
            """
            QCheckBox {
                color: #E6EEF3;
            }
        """
        )

        options_layout.addWidget(port_label)
        options_layout.addWidget(self.port_input, 1)
        options_layout.addWidget(thread_label)
        options_layout.addWidget(self.thread_input)
        options_layout.addWidget(banner_label)
        options_layout.addWidget(self.banner_checkbox)
        options_layout.addStretch()

        header_layout.addLayout(options_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.start_button = QPushButton("Start Scan")
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
        self.start_button.clicked.connect(self.start_scan)

        self.stop_button = QPushButton("Stop Scan")
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
        self.stop_button.clicked.connect(self.stop_scan)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addStretch()

        header_layout.addLayout(buttons_layout)
        layout.addLayout(header_layout)

        # Results table
        results_label = QLabel("Scan Results")
        results_label.setStyleSheet("color: #E6EEF3; font-size: 14px; font-weight: bold;")
        layout.addWidget(results_label)

        self.results_table = ResultsTableView(["port", "state", "service", "banner"])
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_banner_context_menu)
        layout.addWidget(self.results_table)

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
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.thread_input.setEnabled(True)
        self.current_worker = None

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
