"""
Sidebar navigation widget with PyDracula-style design.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize, QPoint
from PySide6.QtGui import QIcon, QPixmap
from typing import List, Tuple, Optional


class ActiveIndicator(QWidget):
    """Sliding indicator that highlights the active sidebar item."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navIndicator")
        self.setFixedWidth(4)
        self.setFixedHeight(30)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # FIX: Don't block clicks
        self.hide()
        
    def move_to(self, target_y: int, duration: int = 250):
        """Animate to new Y position."""
        if not self.isVisible():
            self.move(0, target_y)
            self.show()
            return
            
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(0, target_y))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()


class NavigationButton(QPushButton):
    """Reusable navigation button with icon and text."""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.button_text = text
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setText(f"{icon}    {text}")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(45)
    
    def mousePressEvent(self, event):
        """Handle button press with haptic pop feedback."""
        from netdoctor.gui.widgets.animations import haptic_pop
        haptic_pop(self, scale=1.03, duration=150)
        super().mousePressEvent(event)


class Sidebar(QWidget):
    """
    Fixed left sidebar with logo and navigation buttons.
    """
    
    page_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(260)
        # Ensure the sidebar fills the vertical space of the window
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        self.nav_buttons: List[NavigationButton] = []
        self.current_page: Optional[str] = None
        self.is_collapsed = False
        self.button_page_map = {}
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the sidebar UI."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Background container that sits behind the navigation and logo
        self._background = QWidget(self)
        self._background.setObjectName("sidebarBackground")
        # Allow clicks to pass through to the navigation buttons
        self._background.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._background.lower()
        self._background.show()
        
        # Logo section
        self.logo_widget = self._create_logo_section()
        self.main_layout.addWidget(self.logo_widget)
        
        # Navigation container with indicator
        self.nav_container = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 10, 0, 0)
        self.nav_layout.setSpacing(4)
        self.main_layout.addWidget(self.nav_container)
        
        # Active Indicator
        self.indicator = ActiveIndicator(self.nav_container)
        
        self.add_navigation_items([
            ("▦", "Dashboard"),
            ("⇄", "Ping"),
            ("⌖", "PortScan"),
            ("🖳", "System"),
            ("🗎", "Reports"),
            ("⚙", "Settings"),
        ])
        
        
        self.main_layout.addStretch()

    def resizeEvent(self, event):
        """Ensure the background fills the entire sidebar when resized."""
        super().resizeEvent(event)
        if hasattr(self, "_background") and self._background:
            self._background.setGeometry(self.rect())
        
    def _create_logo_section(self) -> QWidget:
        logo_widget = QWidget()
        logo_widget.setObjectName("sidebarLogo")
        logo_layout = QVBoxLayout(logo_widget)  # Vertical for single logo centering
        logo_layout.setContentsMargins(10, 30, 10, 30)
        logo_layout.setSpacing(0)
        
        # Icon/Logo
        self.logo_icon = QLabel()
        self.logo_icon.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("Assets/temp2.png")
        if not pixmap.isNull():
            # Use a larger size for the main logo
            self.logo_icon.setPixmap(pixmap.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Fallback if image not found
            self.logo_icon.setText("NetDoctor")
            self.logo_icon.setStyleSheet("font-weight: 800; font-size: 20px; color: #3b82f6;")
            
        logo_layout.addWidget(self.logo_icon)
        
        return logo_widget
    
    def add_navigation_items(self, items: List[Tuple[str, str]]):
        for icon, page_name in items:
            btn = NavigationButton(icon, page_name)
            self.nav_buttons.append(btn)
            self.button_page_map[btn] = page_name
            btn.clicked.connect(lambda checked, b=btn: self._on_button_clicked(b))
            self.nav_layout.addWidget(btn)
        
        if self.nav_buttons:
            self.set_active_page(self.button_page_map[self.nav_buttons[0]])
    
    def _on_button_clicked(self, button: NavigationButton):
        page_name = self.button_page_map.get(button)
        if page_name:
            self.set_active_page(page_name)
            self.page_changed.emit(page_name)
    
    def set_active_page(self, page_name: str):
        self.current_page = page_name
        
        for btn in self.nav_buttons:
            active = self.button_page_map.get(btn) == page_name
            btn.setChecked(active)
            if active:
                # Update indicator position
                # We need to wait for layout to be ready, but for now we can estimate
                # or use button geometry if already shown.
                # Adding a small delay or using QTimer/event loop might be safer
                # but let's try direct move first.
                target_y = btn.y() + (btn.height() - self.indicator.height()) // 2
                self.indicator.move_to(target_y)
    
    def get_current_page(self) -> Optional[str]:
        return self.current_page
    
    def toggle_collapse(self):
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self):
        if self.is_collapsed:
            return
        self.is_collapsed = True
        self.setFixedWidth(80)
        self.indicator.hide()
        for btn in self.nav_buttons:
            btn.setText(btn.icon_text)
            btn.setFixedWidth(60)
        self.logo_widget.hide()
    
    def expand(self):
        if not self.is_collapsed:
            return
        self.is_collapsed = False
        self.setFixedWidth(260)
        self.indicator.show()
        for btn in self.nav_buttons:
            btn.setText(f"{btn.icon_text}    {btn.button_text}")
            btn.setFixedWidth(-1)
        self.logo_widget.show()

