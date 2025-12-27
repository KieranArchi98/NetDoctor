"""
Helper functions for adding press animations to buttons.
"""

from PySide6.QtWidgets import QPushButton
from netdoctor.gui.widgets.animations import scale_press


def add_press_animation(button: QPushButton, scale: float = 0.96, duration: int = 120):
    """
    Add press feedback animation to a button.
    
    Args:
        button: Button to animate
        scale: Scale factor (0.96 = 4% smaller)
        duration: Animation duration in ms
    """
    if not button:
        return
    
    original_press = button.mousePressEvent
    
    def animated_press(event):
        scale_press(button, scale=scale, duration=duration)
        original_press(event)
    
    button.mousePressEvent = animated_press

