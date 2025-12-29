"""
Card widgets for displaying metrics and summaries.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from typing import Optional


class KPICard(QWidget):
    """
    KPI card widget for displaying metrics with title and value.
    
    Features:
    - Rounded corners
    - Title and value display
    - Hover elevation effect
    
    Example:
        card = KPICard("CPU Usage", "45%")
        card.set_value("50%")
    """

    def __init__(self, title: str, value: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setObjectName("kpiCardTitle")
        layout.addWidget(self.title_label)

        # Value label
        self.value_label = QLabel(value)
        self.value_label.setObjectName("kpiCardValue")
        layout.addWidget(self.value_label)
    
    def set_value(self, value: str):
        """Update the value displayed."""
        self.value_label.setText(value)
    
    def set_title(self, title: str):
        """Update the title displayed."""
        self.title_label.setText(title)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self.setProperty("hover", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave for hover effect."""
        self.setProperty("hover", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)


class StatCard(QWidget):
    """
    Stat card with icon, value, and change indicator.
    
    Example:
        card = StatCard("📊", "1,234", "+12%", "Total Requests")
    """
    
    def __init__(self, icon: str, value: str, change: str = "", title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Icon and value row
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setObjectName("statCardIcon")
        top_layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("statCardValue")
        top_layout.addWidget(value_label)
        top_layout.addStretch()
        
        if change:
            change_label = QLabel(change)
            change_label.setObjectName("statCardChange")
            top_layout.addWidget(change_label)
        
        layout.addLayout(top_layout)
        
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("statCardTitle")
            layout.addWidget(title_label)
        
    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self.setProperty("hover", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave for hover effect."""
        self.setProperty("hover", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)
