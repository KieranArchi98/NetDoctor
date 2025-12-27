"""
Progress dialog and loading indicators.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import Qt
from typing import Optional

from netdoctor.gui.widgets.ui_components import ProgressIndicator, LoadingSpinner


class ProgressDialog(QDialog):
    """
    Modal progress dialog with cancel option.
    
    Example:
        dialog = ProgressDialog("Processing files...", cancelable=True)
        dialog.set_range(0, 100)
        dialog.set_value(50)
        if dialog.exec():
            # User clicked cancel
            pass
    """
    
    def __init__(self, message: str = "Processing...", cancelable: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("progressDialog")
        self.setWindowTitle("Progress")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.cancelled = False
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Message label
        message_label = QLabel(message)
        message_label.setObjectName("sectionTitle")
        layout.addWidget(message_label)
        
        # Progress bar
        self.progress_bar = ProgressIndicator()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        if cancelable:
            cancel_button = QPushButton("Cancel")
            cancel_button.setObjectName("secondaryButton")
            cancel_button.clicked.connect(self.on_cancel)
            button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def set_range(self, minimum: int, maximum: int):
        """Set the progress bar range."""
        self.progress_bar.setRange(minimum, maximum)
    
    def set_value(self, value: int):
        """Set the progress bar value."""
        self.progress_bar.setValue(value)
    
    def set_format(self, format_str: str):
        """Set the progress bar format string."""
        self.progress_bar.setFormat(format_str)
    
    def on_cancel(self):
        """Handle cancel button click."""
        self.cancelled = True
        self.reject()
    
    def is_cancelled(self) -> bool:
        """Check if the dialog was cancelled."""
        return self.cancelled
