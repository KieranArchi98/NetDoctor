"""
Animated button widget with press feedback.
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from netdoctor.gui.widgets.animations import scale_press


class AnimatedButton(QPushButton):
    """
    Button with press feedback animation.
    
    Automatically applies scale animation on press for visual feedback.
    """
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """Handle button press with feedback animation."""
        # Apply subtle press animation
        scale_press(self, scale=0.96, duration=120)
        super().mousePressEvent(event)

