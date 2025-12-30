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
    
    def __init__(self, title: str, subtitle: str = "", icon_path: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("sectionHeader")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Icon
        if icon_path:
            self.icon = QLabel()
            from PySide6.QtGui import QIcon
            pixmap = QIcon(icon_path).pixmap(32, 32)
            self.icon.setPixmap(pixmap)
            layout.addWidget(self.icon)
        
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
        """Handle button press with haptic feedback."""
        from netdoctor.gui.widgets.animations import haptic_pop
        haptic_pop(self, scale=1.1, duration=150)
        super().mousePressEvent(event)


class ToastNotification(QWidget):
    """
    Refined slide-in toast notification widget.
    """
    
    def __init__(self, message: str, toast_type: str = "info", duration: int = 4000, parent=None):
        super().__init__(parent)
        self.setObjectName(f"toast_{toast_type}")
        self.duration = duration
        
        # Transparent background for the widget itself, styling applied to frame
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.SubWindow | Qt.FramelessWindowHint)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.icon_label = QLabel()
        from PySide6.QtGui import QIcon
        # Simple mapping for internal icons or use characters
        icons = {"success": "✅", "error": "❌", "info": "ℹ️", "warning": "⚠️"}
        self.icon_label.setText(icons.get(toast_type, "ℹ️"))
        layout.addWidget(self.icon_label)
        
        self.message_label = QLabel(message)
        self.message_label.setObjectName("toastMessage")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, 1)
        
        self.setFixedWidth(320)
        self.adjustSize()
        
    def show_toast(self):
        """Play slide-in animation."""
        if not self.parent():
            self.show()
            return
            
        parent_rect = self.parent().rect()
        margin = 20
        end_pos = QPoint(parent_rect.width() - self.width() - margin, margin)
        start_pos = QPoint(parent_rect.width(), margin)
        
        self.move(start_pos)
        self.show()
        
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.OutExpo)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()
        
        # Timer for hiding
        QTimer.singleShot(self.duration, self.hide_toast)
        
    def hide_toast(self):
        """Play slide-out animation."""
        current_pos = self.pos()
        end_pos = QPoint(self.parent().width(), current_pos.y())
        
        self.hide_anim = QPropertyAnimation(self, b"pos")
        self.hide_anim.setDuration(300)
        self.hide_anim.setEasingCurve(QEasingCurve.InExpo)
        self.hide_anim.setStartValue(current_pos)
        self.hide_anim.setEndValue(end_pos)
        self.hide_anim.finished.connect(self.deleteLater)
        self.hide_anim.start()


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

