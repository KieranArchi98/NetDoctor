"""
Settings view implementation.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QLineEdit, QCheckBox, QPushButton, QComboBox, 
    QScrollArea, QFrame, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSettings
from netdoctor.gui.widgets.ui_components import SectionHeader, CardContainer
from netdoctor.core import utils
from netdoctor import config

class SettingsView(QWidget):
    """View for application settings and dependency management."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("NetDoctor", "Settings")
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = SectionHeader("Settings", "Configure application behavior and manage dependencies")
        header.add_action_button("Save Settings", self.save_settings, "primary")
        layout.addWidget(header)
        
        # Scroll area for settings content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(24)
        
        # --- General Settings Section ---
        general_card = CardContainer(hover_elevation=False)
        general_layout = QVBoxLayout(general_card)
        general_layout.addWidget(QLabel("<b>General Settings</b>"))
        
        # Timeouts
        timeout_grid = QHBoxLayout()
        self.ping_timeout = self._add_setting_row("Ping Timeout (s):", QSpinBox(), general_layout)
        self.ping_timeout.setRange(1, 30)
        
        self.port_scan_timeout = self._add_setting_row("Port Scan Timeout (s):", QSpinBox(), general_layout)
        self.port_scan_timeout.setRange(1, 30)
        
        # Concurrency
        self.port_threads = self._add_setting_row("Port Scan Threads:", QSpinBox(), general_layout)
        self.port_threads.setRange(1, 500)
        
        content_layout.addWidget(general_card)
        
        # --- Appearance Section ---
        appearance_card = CardContainer(hover_elevation=False)
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.addWidget(QLabel("<b>Appearance</b>"))
        
        self.theme_combo = self._add_setting_row("Theme:", QComboBox(), appearance_layout)
        self.theme_combo.addItems(["Dark (Default)", "Light"])
        
        content_layout.addWidget(appearance_card)
        
        # --- External Tools Section ---
        tools_card = CardContainer(hover_elevation=False)
        tools_layout = QVBoxLayout(tools_card)
        tools_layout.addWidget(QLabel("<b>External Tools</b>"))
        
        nmap_layout = QHBoxLayout()
        self.nmap_path_input = QLineEdit()
        self.nmap_path_input.setPlaceholderText("Auto-detected or custom path")
        nmap_btn = QPushButton("Browse")
        nmap_btn.clicked.connect(self.browse_nmap)
        nmap_layout.addWidget(self.nmap_path_input)
        nmap_layout.addWidget(nmap_btn)
        
        tools_layout.addWidget(QLabel("Nmap Path:"))
        tools_layout.addLayout(nmap_layout)
        
        content_layout.addWidget(tools_card)
        
        # --- Dependencies Section ---
        dep_card = CardContainer(hover_elevation=False)
        dep_layout = QVBoxLayout(dep_card)
        dep_layout.addWidget(QLabel("<b>Dependency Status</b>"))
        
        self.dep_status_label = QLabel("Detecting...")
        self.dep_status_label.setWordWrap(True)
        dep_layout.addWidget(self.dep_status_label)
        
        refresh_dep_btn = QPushButton("Refresh Dependencies")
        refresh_dep_btn.clicked.connect(self.refresh_dependencies)
        dep_layout.addWidget(refresh_dep_btn)
        
        content_layout.addWidget(dep_card)
        
        # --- Privacy & Legal Section ---
        privacy_card = CardContainer(hover_elevation=False)
        privacy_layout = QVBoxLayout(privacy_card)
        privacy_layout.addWidget(QLabel("<b>Privacy & Legal</b>"))
        
        disclaimer = QLabel(
            "This tool is for educational and authorized diagnostic purposes only. "
            "Unauthorized network scanning may be illegal or violate terms of service. "
            "By using this application, you agree to take full responsibility for your actions."
        )
        disclaimer.setWordWrap(True)
        disclaimer.setStyleSheet("color: #94a3b8; font-size: 11px;")
        privacy_layout.addWidget(disclaimer)
        
        self.privacy_check = QCheckBox("I acknowledge and agree to the terms.")
        privacy_layout.addWidget(self.privacy_check)
        
        content_layout.addWidget(privacy_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Initial dependency check
        self.refresh_dependencies()

    def _add_setting_row(self, label: str, widget: QWidget, parent_layout: QVBoxLayout):
        """Helper to add a labeled setting row."""
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addStretch()
        row.addWidget(widget)
        parent_layout.addLayout(row)
        return widget

    def browse_nmap(self):
        """Open file dialog to browse for nmap executable."""
        path, _ = QFileDialog.getOpenFileName(self, "Find Nmap Executable", "", "Executables (*.exe nmap);;All Files (*)")
        if path:
            self.nmap_path_input.setText(path)

    def refresh_dependencies(self):
        """Check for optional dependencies and update UI."""
        deps = utils.get_all_dependencies()
        status_text = ""
        
        for name, info in deps.items():
            status = "✅ Installed" if info.get("installed") else "❌ Not Found"
            version = info.get("version")
            v_text = f" (v{version})" if version and version != "unknown" else ""
            status_text += f"• <b>{name.capitalize()}</b>: {status}{v_text}\n"
            
        self.dep_status_label.setText(status_text)

    def load_settings(self):
        """Load settings from QSettings or defaults and update config."""
        ping_to = int(self.settings.value("ping_timeout", config.DEFAULT_PING_TIMEOUT))
        ps_to = int(self.settings.value("port_scan_timeout", config.DEFAULT_PORT_SCAN_TIMEOUT))
        threads = int(self.settings.value("port_threads", config.DEFAULT_PORT_SCAN_THREADS))
        nmap_p = self.settings.value("nmap_path", "")
        privacy_ack = self.settings.value("privacy_acknowledged", "false") == "true"
        theme_idx = int(self.settings.value("theme_idx", 0))

        # Update UI
        self.ping_timeout.setValue(ping_to)
        self.port_scan_timeout.setValue(ps_to)
        self.port_threads.setValue(threads)
        self.theme_combo.setCurrentIndex(theme_idx)
        self.nmap_path_input.setText(nmap_p)
        self.privacy_check.setChecked(privacy_ack)

        # Update global config for runtime use
        config.DEFAULT_PING_TIMEOUT = ping_to
        config.DEFAULT_PORT_SCAN_TIMEOUT = ps_to
        config.DEFAULT_PORT_SCAN_THREADS = threads
        config.NMAP_PATH = nmap_p
        config.PRIVACY_ACKNOWLEDGED = privacy_ack

    def save_settings(self):
        """Save current settings to QSettings."""
        self.settings.setValue("ping_timeout", self.ping_timeout.value())
        self.settings.setValue("port_scan_timeout", self.port_scan_timeout.value())
        self.settings.setValue("port_threads", self.port_threads.value())
        self.settings.setValue("theme_idx", self.theme_combo.currentIndex())
        self.settings.setValue("nmap_path", self.nmap_path_input.text().strip())
        self.settings.setValue("privacy_acknowledged", "true" if self.privacy_check.isChecked() else "false")
        
        # Update global config (runtime)
        config.DEFAULT_PING_TIMEOUT = self.ping_timeout.value()
        config.DEFAULT_PORT_SCAN_TIMEOUT = self.port_scan_timeout.value()
        config.DEFAULT_PORT_SCAN_THREADS = self.port_threads.value()
        config.NMAP_PATH = self.nmap_path_input.text().strip()
        config.PRIVACY_ACKNOWLEDGED = self.privacy_check.isChecked()
        
        QMessageBox.information(self, "Success", "Settings saved successfully.")
