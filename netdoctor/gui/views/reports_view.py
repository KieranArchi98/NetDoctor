"""
Reports and History view implementation.
"""

import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QHeaderView,
    QMessageBox, QFileDialog, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt

from netdoctor.storage import history
from netdoctor.core import report
from netdoctor.gui.widgets.ui_components import SectionHeader, CardContainer

class ReportsView(QWidget):
    """View for listing and exporting diagnostic history."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_sessions()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        from pathlib import Path
        icon_dir = Path(__file__).parent.parent.parent / "resources" / "icons"
        
        # Header
        self.header = SectionHeader(
            "Reports & History", 
            "View saved diagnostic sessions and export reports",
            icon_path=str(icon_dir / "reports.svg")
        )
        self.header.add_action_button("Refresh", self.refresh_sessions, "secondary")
        layout.addWidget(self.header)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Vertical)
        
        # Session List Card
        list_card = CardContainer(hover_elevation=False)
        list_layout = QVBoxLayout(list_card)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Timestamp", "Tool", "Target"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Style the table
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        list_layout.addWidget(self.table)
        splitter.addWidget(list_card)
        
        # Details Card
        details_card = CardContainer(hover_elevation=False)
        details_layout = QVBoxLayout(details_card)
        
        details_header = QHBoxLayout()
        details_header.addWidget(QLabel("Session Details"))
        details_header.addStretch()
        
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.setObjectName("secondaryButton")
        self.export_csv_btn.setEnabled(False)
        self.export_csv_btn.clicked.connect(self.export_csv)
        
        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.setObjectName("secondaryButton")
        self.export_json_btn.setEnabled(False)
        self.export_json_btn.clicked.connect(self.export_json)
        
        details_header.addWidget(self.export_csv_btn)
        details_header.addWidget(self.export_json_btn)
        details_layout.addLayout(details_header)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setObjectName("detailsArea")
        details_layout.addWidget(self.details_text)
        
        splitter.addWidget(details_card)
        
        # Set initial splitter sizes (roughly 60% top, 40% bottom)
        layout.addWidget(splitter, 1)
        splitter.setSizes([400, 300])

    def refresh_sessions(self):
        """Refresh the list of sessions from storage."""
        sessions = history.list_sessions()
        self.table.setRowCount(0)
        
        for session in sessions:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(session.get("id", "")))
            self.table.setItem(row_idx, 1, QTableWidgetItem(session.get("timestamp", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(session.get("tool", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(session.get("target", "")))
            
        self.on_selection_changed()
        
        if self.window() and hasattr(self.window(), "show_toast"):
            self.window().show_toast(f"Refreshed {len(sessions)} sessions", "info")

    def on_selection_changed(self):
        """Handle selection change in the table."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.details_text.clear()
            self.export_csv_btn.setEnabled(False)
            self.export_json_btn.setEnabled(False)
            return
            
        session_id = selected_items[0].text()
        session = history.load_session(session_id)
        
        if session:
            self.current_session = session
            self.export_csv_btn.setEnabled(True)
            self.export_json_btn.setEnabled(True)
            
            # Format display text
            text = f"Tool: {session.get('tool')}\n"
            text += f"Target: {session.get('target')}\n"
            text += f"Timestamp: {session.get('timestamp')}\n"
            text += "-" * 40 + "\n\n"
            text += "Results:\n"
            text += report.export_json({"results": session.get("results")})
            
            self.details_text.setPlainText(text)
        else:
            self.details_text.setPlainText("Failed to load session data.")

    def export_csv(self):
        """Export current session to CSV."""
        if not hasattr(self, 'current_session'):
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", 
            f"report_{self.current_session['id']}.csv", 
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                content = report.export_csv(self.current_session)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                if self.window() and hasattr(self.window(), "show_toast"):
                    self.window().show_toast(f"Report saved: {os.path.basename(filename)}", "success")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")

    def export_json(self):
        """Export current session to JSON."""
        if not hasattr(self, 'current_session'):
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", 
            f"report_{self.current_session['id']}.json", 
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                content = report.export_json(self.current_session)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                if self.window() and hasattr(self.window(), "show_toast"):
                    self.window().show_toast(f"Report saved: {os.path.basename(filename)}", "success")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")
