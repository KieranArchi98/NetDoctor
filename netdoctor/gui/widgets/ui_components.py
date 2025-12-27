"""
Reusable UI components styled with PyDracula-inspired blue theme.

Components:
- CardContainer: General-purpose card widget
- SectionHeader: Styled section headers
- IconButton: Icon-only buttons with hover effects
- ToastNotification: Slide-in toast notifications
- ModalDialog: Styled modal dialogs
- LoadingSpinner: Loading indicator
- ProgressIndicator: Progress bar component
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog,
    QFrame, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal, QPoint
from PySide6.QtGui import QFont
from typing import Optional
from netdoctor.gui.widgets.animations import scale_press
from netdoctor.gui.widgets.button_helpers import add_press_animation


class CardContainer(QWidget):
    """
    General-purpose card container with elevation effect.
    
    Features:
    - Rounded corners (10px)
    - Subtle border and background
    - Optional hover elevation
    - Consistent padding
    
    Example:
        card = CardContainer()
        layout = QVBoxLayout(card)
        layout.addWidget(QLabel("Card Content"))
    """
    
    def __init__(self, parent=None, hover_elevation: bool = True):
        super().__init__(parent)
        self.setObjectName("cardContainer")
        self.hover_elevation = hover_elevation
        
        # Set size policy to allow expansion
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        if self.hover_elevation:
            self.setProperty("hover", True)
            self.style().unpolish(self)
            self.style().polish(self)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave for hover effect."""
        if self.hover_elevation:
            self.setProperty("hover", False)
            self.style().unpolish(self)
            self.style().polish(self)
        super().leaveEvent(event)


class SectionHeader(QWidget):
    """
    Styled section header with title and optional action buttons.
    
    Example:
        header = SectionHeader("Section Title")
        header.add_action_button("Action", callback_function)
    """
    
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("sectionHeader")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        title_layout.addWidget(title_label)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("sectionSubtitle")
            title_layout.addWidget(subtitle_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
    
    def add_action_button(self, text: str, callback=None, button_type: str = "secondary"):
        """Add an action button to the header."""
        button = QPushButton(text)
        button.setObjectName(f"{button_type}Button")
        if callback:
            button.clicked.connect(callback)
        
        # Add press animation
        add_press_animation(button, scale=0.96, duration=120)
        
        layout = self.layout()
        layout.insertWidget(layout.count() - 1, button)  # Insert before stretch
        return button


class IconButton(QPushButton):
    """
    Icon-only button with hover effects and tooltip.
    
    Example:
        btn = IconButton("⚙️", "Settings")
        btn.clicked.connect(settings_callback)
    """
    
    def __init__(self, icon: str, tooltip: str = "", parent=None):
        super().__init__(icon, parent)
        self.setObjectName("iconButton")
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(32, 32)
    
    def mousePressEvent(self, event):
        """Handle button press with feedback animation."""
        from netdoctor.gui.widgets.animations import scale_press
        scale_press(self, scale=0.9, duration=100)
        super().mousePressEvent(event)


class ToastNotification(QWidget):
    """
    Slide-in toast notification widget.
    
    Example:
        toast = ToastNotification("Operation completed!", parent=main_window)
        toast.show_toast()
    """
    
    def __init__(self, message: str, toast_type: str = "info", duration: int = 3000, parent=None):
        super().__init__(parent)
        self.setObjectName(f"toast_{toast_type}")
        self.duration = duration
        self.message = message
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        label = QLabel(message)
        label.setObjectName("toastMessage")
        layout.addWidget(label)
        
        close_btn = IconButton("✕", "Close")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        
        # Start hidden
        self.hide()
    
    def show_toast(self, position: Optional[QPoint] = None):
        """Show the toast notification with slide-in animation."""
        # Ensure widget has proper size
        self.adjustSize()
        toast_width = self.width() if self.width() > 0 else 300
        toast_height = self.height() if self.height() > 0 else 60
        
        if self.parent():
            parent_rect = self.parent().geometry()
            if position is None:
                position = QPoint(
                    parent_rect.right() - toast_width - 20,
                    parent_rect.top() + 20
                )
        else:
            if position is None:
                position = QPoint(100, 100)
        
        # Slide-in animation
        start_rect = QRect(position.x() + toast_width, position.y(), toast_width, toast_height)
        end_rect = QRect(position.x(), position.y(), toast_width, toast_height)
        
        self.setGeometry(start_rect)
        self.show()
        
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.start()
        
        # Auto-hide timer
        QTimer.singleShot(self.duration, self.hide_toast)
    
    def hide_toast(self):
        """Hide the toast with slide-out animation."""
        current_rect = self.geometry()
        toast_width = current_rect.width()
        end_rect = QRect(current_rect.x() + toast_width, current_rect.y(), toast_width, current_rect.height())
        
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.InCubic)
        animation.setStartValue(current_rect)
        animation.setEndValue(end_rect)
        animation.finished.connect(self.hide)
        animation.start()


class ModalDialog(QDialog):
    """
    Styled modal dialog with header and action buttons.
    
    Example:
        dialog = ModalDialog("Confirm Action", "Are you sure?")
        dialog.add_button("Cancel", "secondary", dialog.reject)
        dialog.add_button("Confirm", "primary", dialog.accept)
        result = dialog.exec()
    """
    
    def __init__(self, title: str, message: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("modalDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel(title)
        header_label.setObjectName("pageTitle")
        layout.addWidget(header_label)
        
        # Message
        if message:
            message_label = QLabel(message)
            message_label.setObjectName("sectionSubtitle")
            message_label.setWordWrap(True)
            layout.addWidget(message_label)
        
        # Button container
        self.button_container = QWidget()
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addStretch()
        layout.addWidget(self.button_container)
    
    def add_button(self, text: str, button_type: str = "primary", callback=None):
        """Add a button to the dialog."""
        button = QPushButton(text)
        button.setObjectName(f"{button_type}Button")
        if callback:
            button.clicked.connect(callback)
        
        # Add press animation
        add_press_animation(button, scale=0.96, duration=120)
        
        layout = self.button_container.layout()
        layout.insertWidget(layout.count() - 1, button)
        return button
    
    def set_content(self, widget: QWidget):
        """Set custom content widget."""
        layout = self.layout()
        # Insert before button container
        layout.insertWidget(layout.count() - 1, widget)


class LoadingSpinner(QLabel):
    """
    Circular loading spinner indicator using animated text.
    
    Note: For true rotation animation, custom painting would be required.
    This version uses animated text characters as a simple alternative.
    
    Example:
        spinner = LoadingSpinner()
        spinner.start()
    """
    
    def __init__(self, parent=None, size: int = 32):
        super().__init__(parent)
        self.setObjectName("loadingSpinner")
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self._is_spinning = False
        self._frame = 0
        self._frames = ["◐", "◓", "◑", "◒"]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_animation)
        self._timer.setInterval(120)  # Update every 120ms for smoother animation
    
    def _update_animation(self):
        """Update spinner frame."""
        if self._is_spinning:
            self.setText(self._frames[self._frame])
            self._frame = (self._frame + 1) % len(self._frames)
    
    def start(self):
        """Start the spinner animation with fade in."""
        from netdoctor.gui.widgets.animations import fade_in
        self._is_spinning = True
        self._frame = 0
        self.show()
        self._update_animation()
        self._timer.start()
        # Fade in
        self.setWindowOpacity(0.0)
        fade_in(self, duration=200)
    
    def stop(self):
        """Stop the spinner animation with fade out."""
        from netdoctor.gui.widgets.animations import fade_out
        self._is_spinning = False
        self._timer.stop()
        # Fade out then hide
        fade_out(self, duration=150, on_finished=self.hide)


class ProgressIndicator(QProgressBar):
    """
    Styled progress bar with optional label.
    
    Example:
        progress = ProgressIndicator("Processing...")
        progress.setRange(0, 100)
        progress.setValue(50)
    """
    
    def __init__(self, label: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("progressIndicator")
        self.label_text = label
        self.setTextVisible(True)
        
        if label:
            self.setFormat(f"{label}: %p%")
        else:
            self.setFormat("%p%")

