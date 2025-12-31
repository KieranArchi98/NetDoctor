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
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        from pathlib import Path
        icon_dir = Path(__file__).parent.parent.parent / "resources" / "icons"
        
        # Header
        header = SectionHeader(
            "Settings", 
            "Configure application behavior and manage dependencies",
            icon_path=str(icon_dir / "settings.svg")
        )
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
        general_card = CardContainer()
        general_layout = QVBoxLayout(general_card)
        general_layout.setContentsMargins(24, 24, 24, 24)
        general_layout.setSpacing(20)
        
        general_label = QLabel("GENERAL SETTINGS")
        general_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1.5px;")
        general_layout.addWidget(general_label)
        
        # Timeouts
        self.ping_timeout = self._add_setting_row("Ping Timeout (s)", QSpinBox(), general_layout)
        self.ping_timeout.setRange(1, 30)
        
        self.port_scan_timeout = self._add_setting_row("Port Scan Timeout (s)", QSpinBox(), general_layout)
        self.port_scan_timeout.setRange(1, 30)
        
        # Concurrency
        self.port_threads = self._add_setting_row("Port Scan Threads", QSpinBox(), general_layout)
        self.port_threads.setRange(1, 500)
        
        content_layout.addWidget(general_card)
        
        # --- Appearance Section ---
        appearance_card = CardContainer()
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(24, 24, 24, 24)
        appearance_layout.setSpacing(20)
        
        appearance_label = QLabel("APPEARANCE")
        appearance_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1.5px;")
        appearance_layout.addWidget(appearance_label)
        
        self.theme_combo = self._add_setting_row("Theme Preference", QComboBox(), appearance_layout)
        self.theme_combo.addItems(["Dark (Default)", "Light"])
        self.theme_combo.setMinimumWidth(150)
        
        content_layout.addWidget(appearance_card)
        
        # --- External Tools Section ---
        tools_card = CardContainer()
        tools_layout = QVBoxLayout(tools_card)
        tools_layout.setContentsMargins(24, 24, 24, 24)
        tools_layout.setSpacing(20)
        
        tools_label = QLabel("EXTERNAL TOOLS")
        tools_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1.5px;")
        tools_layout.addWidget(tools_label)
        
        nmap_row = QVBoxLayout()
        nmap_row.setSpacing(8)
        nmap_label = QLabel("Nmap Executable Path")
        nmap_label.setStyleSheet("color: #94a3b8; font-size: 13px;")
        
        nmap_input_layout = QHBoxLayout()
        nmap_input_layout.setSpacing(12)
        self.nmap_path_input = QLineEdit()
        self.nmap_path_input.setPlaceholderText("Auto-detected or custom path")
        self.nmap_path_input.setFixedHeight(40)
        
        nmap_btn = QPushButton("Browse")
        nmap_btn.setObjectName("secondaryButton")
        nmap_btn.setFixedHeight(40)
        nmap_btn.setFixedWidth(100)
        nmap_btn.clicked.connect(self.browse_nmap)
        
        nmap_input_layout.addWidget(self.nmap_path_input)
        nmap_input_layout.addWidget(nmap_btn)
        
        nmap_row.addWidget(nmap_label)
        nmap_row.addLayout(nmap_input_layout)
        tools_layout.addLayout(nmap_row)
        
        content_layout.addWidget(tools_card)
        
        # --- Dependencies Section ---
        dep_card = CardContainer()
        dep_layout = QVBoxLayout(dep_card)
        dep_layout.setContentsMargins(24, 24, 24, 24)
        dep_layout.setSpacing(20)
        
        dep_header = QHBoxLayout()
        dep_label = QLabel("DEPENDENCY STATUS")
        dep_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 1.5px;")
        dep_header.addWidget(dep_label)
        dep_header.addStretch()
        
        refresh_dep_btn = QPushButton("Refresh")
        refresh_dep_btn.setObjectName("secondaryButton")
        refresh_dep_btn.setFixedWidth(80)
        refresh_dep_btn.clicked.connect(self.refresh_dependencies)
        dep_header.addWidget(refresh_dep_btn)
        
        dep_layout.addLayout(dep_header)
        
        self.dep_status_label = QLabel("Detecting...")
        self.dep_status_label.setWordWrap(True)
        self.dep_status_label.setStyleSheet("color: #e2e8f0; line-height: 1.6;")
        dep_layout.addWidget(self.dep_status_label)
        
        content_layout.addWidget(dep_card)
        
        # --- Privacy & Legal Section ---
        privacy_card = CardContainer()
        privacy_card.setObjectName("legalCard") # Special identifier for legal
        privacy_layout = QVBoxLayout(privacy_card)
        privacy_layout.setContentsMargins(24, 24, 24, 24)
        privacy_layout.setSpacing(20)
        
        privacy_label = QLabel("PRIVACY & LEGAL")
        privacy_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #f87171; letter-spacing: 1.5px;")
        privacy_layout.addWidget(privacy_label)
        
        disclaimer = QLabel(
            "This tool is for educational and authorized diagnostic purposes only. "
            "Unauthorized network scanning may be illegal or violate terms of service. "
            "By using this application, you agree to take full responsibility for your actions."
        )
        disclaimer.setWordWrap(True)
        disclaimer.setStyleSheet("color: #991b1b; background-color: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 6px; font-size: 12px; line-height: 1.5;")
        privacy_layout.addWidget(disclaimer)
        
        self.privacy_check = QCheckBox("I acknowledge and agree to the terms.")
        self.privacy_check.setStyleSheet("color: #e2e8f0; font-weight: 500;")
        privacy_layout.addWidget(self.privacy_check)
        
        content_layout.addWidget(privacy_card)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Entrance animations
        from netdoctor.gui.widgets.animations import fade_in
        fade_in(self, duration=400)
        
        # Initial dependency check
        self.refresh_dependencies()

    def _add_setting_row(self, label: str, widget: QWidget, parent_layout: QVBoxLayout):
        """Helper to add a labeled setting row with hover and group styling."""
        row_widget = QFrame()
        row_widget.setObjectName("settingRow")
        row_widget.setStyleSheet("""
            QFrame#settingRow {
                background-color: rgba(15, 23, 42, 0.3);
                border-radius: 8px;
                border: 1px solid transparent;
            }
            QFrame#settingRow:hover {
                background-color: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(59, 130, 246, 0.2);
            }
        """)
        
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(12, 8, 12, 8)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #e2e8f0; font-size: 13px; font-weight: 500; background: transparent;")
        
        row.addWidget(label_widget)
        row.addStretch()
        
        if isinstance(widget, QSpinBox):
            widget.setFixedHeight(32)
            widget.setFixedWidth(80)
        elif isinstance(widget, QComboBox):
            widget.setFixedHeight(32)
            widget.setMinimumWidth(120)
        elif isinstance(widget, QLineEdit):
            widget.setFixedHeight(32)
            
        row.addWidget(widget)
        parent_layout.addWidget(row_widget)
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
        def get_int_value(key, default):
            val = self.settings.value(key, default)
            try:
                # Handle possible string floats like "1.0"
                return int(float(val))
            except (ValueError, TypeError, AttributeError):
                return int(default)

        ping_to = get_int_value("ping_timeout", config.DEFAULT_PING_TIMEOUT)
        ps_to = get_int_value("port_scan_timeout", config.DEFAULT_PORT_SCAN_TIMEOUT)
        threads = get_int_value("port_threads", config.DEFAULT_PORT_SCAN_THREADS)
        theme_idx = get_int_value("theme_idx", 0)
        
        nmap_p = str(self.settings.value("nmap_path", ""))
        privacy_ack = self.settings.value("privacy_acknowledged", "false") == "true"

        # Update UI
        self.ping_timeout.setValue(ping_to)
        self.port_scan_timeout.setValue(ps_to)
        self.port_threads.setValue(threads)
        self.theme_combo.setCurrentIndex(theme_idx)
        self.nmap_path_input.setText(nmap_p)
        self.privacy_check.setChecked(privacy_ack)

        # Update global config for runtime use
        config.DEFAULT_PING_TIMEOUT = float(ping_to)
        config.DEFAULT_PORT_SCAN_TIMEOUT = float(ps_to)
        config.DEFAULT_PORT_SCAN_THREADS = int(threads)
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
        
        if self.window() and hasattr(self.window(), "show_toast"):
            self.window().show_toast("Settings saved successfully", "success")
