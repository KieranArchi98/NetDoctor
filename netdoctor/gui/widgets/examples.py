"""
Example usage of UI components.

This file demonstrates how to use each component with the PyDracula-inspired blue theme.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PySide6.QtCore import QTimer

from netdoctor.gui.widgets.ui_components import (
    CardContainer,
    SectionHeader,
    IconButton,
    ToastNotification,
    ModalDialog,
    LoadingSpinner,
    ProgressIndicator,
)
from netdoctor.gui.widgets.cards import KPICard, StatCard


def example_kpi_card(parent=None):
    """Example: KPI Card usage."""
    card = KPICard("CPU Usage", "45.2%", parent)
    # Update value later
    card.set_value("50.1%")
    return card


def example_stat_card(parent=None):
    """Example: Stat Card usage."""
    card = StatCard("📊", "1,234", "+12%", "Total Requests", parent)
    # Update value later
    card.set_value("1,456")
    return card


def example_card_container(parent=None):
    """Example: Card Container usage."""
    card = CardContainer(parent, hover_elevation=True)
    layout = QVBoxLayout(card)
    
    title = QLabel("Card Title")
    title.setObjectName("sectionTitle")
    layout.addWidget(title)
    
    content = QLabel("Card content goes here...")
    layout.addWidget(content)
    
    return card


def example_section_header(parent=None):
    """Example: Section Header usage."""
    header = SectionHeader("Section Title", "Optional subtitle", parent)
    
    # Add action button
    header.add_action_button("Action", lambda: print("Clicked!"), "primary")
    
    return header


def example_icon_button(parent=None):
    """Example: Icon Button usage."""
    btn = IconButton("⚙️", "Settings", parent)
    btn.clicked.connect(lambda: print("Settings clicked"))
    return btn


def example_toast_notification(parent=None):
    """Example: Toast Notification usage."""
    toast = ToastNotification("Operation completed successfully!", "success", duration=3000, parent=parent)
    toast.show_toast()
    return toast


def example_modal_dialog(parent=None):
    """Example: Modal Dialog usage."""
    dialog = ModalDialog("Confirm Action", "Are you sure you want to proceed?")
    dialog.add_button("Cancel", "secondary", dialog.reject)
    dialog.add_button("Confirm", "primary", dialog.accept)
    return dialog


def example_loading_spinner(parent=None):
    """Example: Loading Spinner usage."""
    spinner = LoadingSpinner(parent, size=32)
    spinner.start()
    
    # Stop after 3 seconds (example)
    QTimer.singleShot(3000, spinner.stop)
    
    return spinner


def example_progress_indicator(parent=None):
    """Example: Progress Indicator usage."""
    progress = ProgressIndicator("Processing files...", parent)
    progress.setRange(0, 100)
    progress.setValue(50)
    return progress


def example_complete_layout():
    """Example: Complete layout using multiple components."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(16)
    
    # Section header with action button
    header = SectionHeader("Dashboard", "System overview and metrics")
    header.add_action_button("Refresh", lambda: print("Refresh"), "primary")
    layout.addWidget(header)
    
    # KPI Cards in a row
    cards_layout = QHBoxLayout()
    cards_layout.setSpacing(16)
    
    cpu_card = KPICard("CPU Usage", "45%")
    memory_card = KPICard("Memory Usage", "62%")
    disk_card = KPICard("Disk Usage", "38%")
    
    cards_layout.addWidget(cpu_card)
    cards_layout.addWidget(memory_card)
    cards_layout.addWidget(disk_card)
    
    layout.addLayout(cards_layout)
    
    # Card container with content
    card = CardContainer()
    card_layout = QVBoxLayout(card)
    card_layout.setSpacing(12)
    
    card_title = QLabel("Recent Activity")
    card_title.setObjectName("sectionTitle")
    card_layout.addWidget(card_title)
    
    card_content = QLabel("Activity content here...")
    card_layout.addWidget(card_content)
    
    layout.addWidget(card)
    
    # Icon buttons row
    buttons_layout = QHBoxLayout()
    buttons_layout.setSpacing(8)
    
    settings_btn = IconButton("⚙️", "Settings")
    help_btn = IconButton("❓", "Help")
    info_btn = IconButton("ℹ️", "Info")
    
    buttons_layout.addWidget(settings_btn)
    buttons_layout.addWidget(help_btn)
    buttons_layout.addWidget(info_btn)
    buttons_layout.addStretch()
    
    layout.addLayout(buttons_layout)
    layout.addStretch()
    
    return widget


if __name__ == "__main__":
    # Example usage demonstration
    app = QApplication([])
    
    # Create example layout
    widget = example_complete_layout()
    widget.show()
    
    # Show toast notification
    toast = ToastNotification("Application loaded!", "success", parent=widget)
    QTimer.singleShot(500, lambda: toast.show_toast())
    
    app.exec()

