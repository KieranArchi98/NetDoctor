"""
Animation utilities for smooth UI transitions.
"""

from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, QAbstractAnimation, QRect, QPoint, QSize
)
from PySide6.QtWidgets import QWidget
from typing import Optional, Callable


def fade_in(widget: QWidget, duration: int = 200, on_finished: Optional[Callable] = None):
    """
    Fade in animation for a widget.
    
    Args:
        widget: Widget to animate
        duration: Animation duration in ms
        on_finished: Optional callback when animation completes
    """
    if not widget:
        return
    
    widget.setProperty("opacity", 0.0)
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    
    if on_finished:
        animation.finished.connect(on_finished)
    
    animation.start()
    return animation


def fade_out(widget: QWidget, duration: int = 150, on_finished: Optional[Callable] = None):
    """
    Fade out animation for a widget.
    
    Args:
        widget: Widget to animate
        duration: Animation duration in ms
        on_finished: Optional callback when animation completes
    """
    if not widget:
        return
    
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(widget.windowOpacity() if widget.windowOpacity() > 0 else 1.0)
    animation.setEndValue(0.0)
    animation.setEasingCurve(QEasingCurve.InCubic)
    
    if on_finished:
        animation.finished.connect(on_finished)
    
    animation.start()
    return animation


def slide_in_from_right(widget: QWidget, duration: int = 250, on_finished: Optional[Callable] = None):
    """
    Slide in animation from the right side.
    
    Args:
        widget: Widget to animate
        duration: Animation duration in ms
        on_finished: Optional callback when animation completes
    """
    if not widget:
        return
    
    parent = widget.parentWidget()
    if not parent:
        return
    
    end_pos = widget.pos()
    start_pos = QPoint(parent.width(), end_pos.y())
    
    widget.move(start_pos)
    
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setStartValue(start_pos)
    animation.setEndValue(end_pos)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    
    # Also fade in
    fade_anim = QPropertyAnimation(widget, b"windowOpacity")
    fade_anim.setDuration(duration)
    fade_anim.setStartValue(0.0)
    fade_anim.setEndValue(1.0)
    fade_anim.setEasingCurve(QEasingCurve.OutCubic)
    
    group = QParallelAnimationGroup()
    group.addAnimation(animation)
    group.addAnimation(fade_anim)
    
    if on_finished:
        group.finished.connect(on_finished)
    
    group.start()
    return group


def slide_out_to_left(widget: QWidget, duration: int = 200, on_finished: Optional[Callable] = None):
    """
    Slide out animation to the left side.
    
    Args:
        widget: Widget to animate
        duration: Animation duration in ms
        on_finished: Optional callback when animation completes
    """
    if not widget:
        return
    
    parent = widget.parentWidget()
    if not parent:
        return
    
    start_pos = widget.pos()
    end_pos = QPoint(-widget.width(), start_pos.y())
    
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setStartValue(start_pos)
    animation.setEndValue(end_pos)
    animation.setEasingCurve(QEasingCurve.InCubic)
    
    # Also fade out
    fade_anim = QPropertyAnimation(widget, b"windowOpacity")
    fade_anim.setDuration(duration)
    fade_anim.setStartValue(1.0)
    fade_anim.setEndValue(0.0)
    fade_anim.setEasingCurve(QEasingCurve.InCubic)
    
    group = QParallelAnimationGroup()
    group.addAnimation(animation)
    group.addAnimation(fade_anim)
    
    if on_finished:
        group.finished.connect(on_finished)
    
    group.start()
    return group


def scale_press(widget: QWidget, scale: float = 0.95, duration: int = 100):
    """
    Button press feedback animation with scale effect.
    
    Args:
        widget: Widget to animate (usually a button)
        scale: Scale factor (0.95 = 5% smaller)
        duration: Animation duration in ms
    """
    if not widget:
        return
    
    # Store original size
    original_size = widget.size()
    scaled_size = QSize(int(original_size.width() * scale), int(original_size.height() * scale))
    
    # Scale down
    scale_down = QPropertyAnimation(widget, b"geometry")
    scale_down.setDuration(duration // 2)
    scale_down.setStartValue(widget.geometry())
    scale_down.setEndValue(QRect(
        widget.x() + (original_size.width() - scaled_size.width()) // 2,
        widget.y() + (original_size.height() - scaled_size.height()) // 2,
        scaled_size.width(),
        scaled_size.height()
    ))
    scale_down.setEasingCurve(QEasingCurve.InOutQuad)
    
    # Scale back up
    scale_up = QPropertyAnimation(widget, b"geometry")
    scale_up.setDuration(duration // 2)
    scale_up.setStartValue(scale_down.endValue())
    scale_up.setEndValue(widget.geometry())
    scale_up.setEasingCurve(QEasingCurve.OutCubic)
    
    sequence = QSequentialAnimationGroup()
    sequence.addAnimation(scale_down)
    sequence.addAnimation(scale_up)
    
    sequence.start()
    return sequence


def pulse(widget: QWidget, scale: float = 1.05, duration: int = 600, loops: int = -1):
    """
    Pulse animation for loading/attention states.
    
    Args:
        widget: Widget to animate
        scale: Scale factor for pulse
        duration: Full pulse cycle duration in ms
        loops: Number of loops (-1 for infinite)
    """
    if not widget:
        return
    
    original_size = widget.size()
    scaled_size = QSize(int(original_size.width() * scale), int(original_size.height() * scale))
    
    # Scale up
    scale_up = QPropertyAnimation(widget, b"geometry")
    scale_up.setDuration(duration // 2)
    scale_up.setStartValue(widget.geometry())
    scale_up.setEndValue(QRect(
        widget.x() + (original_size.width() - scaled_size.width()) // 2,
        widget.y() + (original_size.height() - scaled_size.height()) // 2,
        scaled_size.width(),
        scaled_size.height()
    ))
    scale_up.setEasingCurve(QEasingCurve.InOutQuad)
    
    # Scale down
    scale_down = QPropertyAnimation(widget, b"geometry")
    scale_down.setDuration(duration // 2)
    scale_down.setStartValue(scale_up.endValue())
    scale_down.setEndValue(widget.geometry())
    scale_down.setEasingCurve(QEasingCurve.InOutQuad)
    
    sequence = QSequentialAnimationGroup()
    sequence.addAnimation(scale_up)
    sequence.addAnimation(scale_down)
    
    if loops > 0:
        sequence.setLoopCount(loops)
    elif loops == -1:
        sequence.setLoopCount(-1)  # Infinite
    
    sequence.start()
    return sequence

def haptic_pop(widget: QWidget, scale: float = 1.05, duration: int = 150):
    """
    Subtle 'pop' animation for energetic click feedback.
    
    Args:
        widget: Widget to animate
        scale: Pop scale factor
        duration: Animation duration
    """
    if not widget:
        return
        
    original_size = widget.size()
    scaled_size = QSize(int(original_size.width() * scale), int(original_size.height() * scale))
    
    pop_up = QPropertyAnimation(widget, b"geometry")
    pop_up.setDuration(duration // 3)
    pop_up.setStartValue(widget.geometry())
    pop_up.setEndValue(QRect(
        widget.x() - (scaled_size.width() - original_size.width()) // 2,
        widget.y() - (scaled_size.height() - original_size.height()) // 2,
        scaled_size.width(),
        scaled_size.height()
    ))
    pop_up.setEasingCurve(QEasingCurve.OutCubic)
    
    pop_down = QPropertyAnimation(widget, b"geometry")
    pop_down.setDuration(duration * 2 // 3)
    pop_down.setStartValue(pop_up.endValue())
    pop_down.setEndValue(widget.geometry())
    pop_down.setEasingCurve(QEasingCurve.OutElastic)
    
    sequence = QSequentialAnimationGroup()
    sequence.addAnimation(pop_up)
    sequence.addAnimation(pop_down)
    sequence.start()
    return sequence
