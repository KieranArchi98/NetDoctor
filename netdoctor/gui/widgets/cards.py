"""
Small KPI card widgets.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional


class KPICard(QWidget):
    """KPI card widget for displaying metrics."""

    def __init__(self, title: str, value: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #111827;
                border-radius: 8px;
                padding: 16px;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            """
            QLabel {
                color: #9CA3AF;
                font-size: 12px;
                font-weight: normal;
            }
        """
        )
        layout.addWidget(self.title_label)

        # Value label
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            """
            QLabel {
                color: #E6EEF3;
                font-size: 24px;
                font-weight: bold;
            }
        """
        )
        layout.addWidget(self.value_label)

    def set_value(self, value: str):
        """Update the value displayed."""
        self.value_label.setText(value)
