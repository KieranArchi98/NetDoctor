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
    """Reusable navigation button with SVG icon and text."""

    def __init__(self, icon_path: str, text: str, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.button_text = text
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        
        # Set SVG icon
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(20, 20))
        self.setText(f"   {text}")
    
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
        
        from pathlib import Path
        icon_dir = Path(__file__).parent.parent.parent / "resources" / "icons"
        
        self.add_navigation_items([
            (str(icon_dir / "dashboard.svg"), "Dashboard"),
            (str(icon_dir / "ping.svg"), "Ping"),
            (str(icon_dir / "portscan.svg"), "PortScan"),
            (str(icon_dir / "system.svg"), "System"),
            (str(icon_dir / "reports.svg"), "Reports"),
            (str(icon_dir / "settings.svg"), "Settings"),
        ])
        
        
        self.main_layout.addStretch()

    def resizeEvent(self, event):
        """Ensure the background fills the entire sidebar when resized."""
        super().resizeEvent(event)
        if hasattr(self, "_background") and self._background:
            self._background.setGeometry(self.rect())
        
    def animate_in(self, duration: int = 500):
        """Slide-in animation from left."""
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setStartValue(QPoint(-self.width(), self.y()))
        self.animation.setEndValue(QPoint(0, self.y()))
        self.animation.start()

    def _create_logo_section(self) -> QWidget:
        logo_widget = QWidget()
        logo_widget.setObjectName("sidebarLogo")
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 30, 20, 30)
        
        self.logo_label = QLabel("NetDoctor")
        self.logo_label.setStyleSheet("font-weight: 900; font-size: 24px; color: #3B82F6;")
        logo_layout.addWidget(self.logo_label)
        
        self.logo_tagline = QLabel("Diagnostic Toolkit")
        self.logo_tagline.setObjectName("sectionSubtitle")
        logo_layout.addWidget(self.logo_tagline)
        
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
            btn.setText("") # Simple collapse: hide text
            btn.setFixedWidth(60)
        self.logo_widget.hide()
    
    def expand(self):
        if not self.is_collapsed:
            return
        self.is_collapsed = False
        self.setFixedWidth(260)
        self.indicator.show()
        for btn in self.nav_buttons:
            btn.setText(f"   {btn.button_text}")
            btn.setFixedWidth(-1)
        self.logo_widget.show()

