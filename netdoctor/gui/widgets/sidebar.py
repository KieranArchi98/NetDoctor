"""
Sidebar navigation widget with PyDracula-style design.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QIcon, QPixmap
from typing import List, Tuple, Optional


class NavigationButton(QPushButton):
    """Reusable navigation button with icon and text."""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.button_text = text
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setText(f"{icon}  {text}")
        self.setCursor(Qt.PointingHandCursor)
        self._hover_animation = None
    
    def enterEvent(self, event):
        """Handle mouse enter with subtle animation."""
        from netdoctor.gui.widgets.animations import scale_press
        super().enterEvent(event)
        # Subtle scale animation on hover (very fast)
        if not self.isChecked():
            # Only animate if not already active
            pass  # Hover effect is handled by CSS
    
    def mousePressEvent(self, event):
        """Handle button press with feedback animation."""
        from netdoctor.gui.widgets.animations import scale_press
        # Quick press feedback
        scale_press(self, scale=0.97, duration=150)
        super().mousePressEvent(event)


class Sidebar(QWidget):
    """
    Fixed left sidebar with logo and navigation buttons.
    
    Features:
    - Logo section at top
    - Vertical navigation buttons
    - Active page indicator
    - Optional collapse/expand functionality
    - Signals for page switching
    """
    
    # Signal emitted when navigation button is clicked
    page_changed = Signal(str)  # Emits page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        
        # Navigation state
        self.nav_buttons: List[NavigationButton] = []
        self.current_page: Optional[str] = None
        self.is_collapsed = False
        
        # Views mapping - stores the page name for each button
        self.button_page_map = {}
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo and title section
        self.logo_widget = self._create_logo_section()
        layout.addWidget(self.logo_widget)
        
        # Navigation buttons container
        self.nav_container = QWidget()
        nav_layout = QVBoxLayout(self.nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        layout.addWidget(self.nav_container)
        
        # Add default navigation items
        self.add_navigation_items([
            ("▦", "Dashboard"),
            ("⇄", "Ping"),
            ("⌖", "PortScan"),
            ("🖳", "System"),
            ("🗎", "Reports"),
            ("⚙", "Settings"),
        ])
        
        # Add spacer at bottom
        layout.addStretch()
        
        # Optional: Add collapse/expand button (can be enabled later)
        # self.collapse_button = self._create_collapse_button()
        # layout.addWidget(self.collapse_button)
        
    def _create_logo_section(self) -> QWidget:
        """Create the logo and title section."""
        logo_widget = QWidget()
        logo_widget.setObjectName("sidebarLogo")
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo Image
        logo_label = QLabel()
        logo_pixmap = QPixmap("Assets/temp2.PNG")
        if not logo_pixmap.isNull():
            # Scale to fit reasonably (e.g., width of 180px or height of 50px)
            scaled_pixmap = logo_pixmap.scaled(
                180, 50, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("NetDoctor") # Fallback
            
        logo_layout.addWidget(logo_label)
        
        return logo_widget
    
    def add_navigation_items(self, items: List[Tuple[str, str]]):
        """
        Add navigation items to the sidebar.
        
        Args:
            items: List of (icon, page_name) tuples
        """
        nav_layout = self.nav_container.layout()
        
        for icon, page_name in items:
            btn = NavigationButton(icon, page_name)
            self.nav_buttons.append(btn)
            self.button_page_map[btn] = page_name
            
            # Connect button click to internal handler
            btn.clicked.connect(lambda checked, b=btn: self._on_button_clicked(b))
            
            nav_layout.addWidget(btn)
        
        # Set first button as active by default
        if self.nav_buttons:
            self.set_active_page(self.button_page_map[self.nav_buttons[0]])
    
    def _on_button_clicked(self, button: NavigationButton):
        """Handle navigation button click with animation."""
        page_name = self.button_page_map.get(button)
        if page_name:
            self.set_active_page(page_name)
            self.page_changed.emit(page_name)
    
    def set_active_page(self, page_name: str):
        """
        Set the active page and update button states.
        
        Args:
            page_name: Name of the page to activate
        """
        self.current_page = page_name
        
        # Uncheck all buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)
        
        # Find and check the button for this page
        for btn in self.nav_buttons:
            if self.button_page_map.get(btn) == page_name:
                btn.setChecked(True)
                break
    
    def get_current_page(self) -> Optional[str]:
        """Get the currently active page name."""
        return self.current_page
    
    def toggle_collapse(self):
        """Toggle sidebar collapse/expand state."""
        # Animation for collapse/expand
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self):
        """Collapse the sidebar to show only icons."""
        if self.is_collapsed:
            return
        
        self.is_collapsed = True
        # Animate width change
        animation = QPropertyAnimation(self, b"minimumWidth")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.setStartValue(240)
        animation.setEndValue(60)
        animation.start()
        
        animation2 = QPropertyAnimation(self, b"maximumWidth")
        animation2.setDuration(200)
        animation2.setEasingCurve(QEasingCurve.InOutQuad)
        animation2.setStartValue(240)
        animation2.setEndValue(60)
        animation2.start()
        
        # Hide text in buttons (keep only icons)
        for btn in self.nav_buttons:
            icon_only = btn.icon_text
            btn.setText(icon_only)
            btn.setFixedWidth(60)
        
        # Hide subtitle if it exists
        subtitle = self.logo_widget.findChild(QLabel, "sidebarSubtitle")
        if subtitle:
            subtitle.hide()
    
    def expand(self):
        """Expand the sidebar to show full text."""
        if not self.is_collapsed:
            return
        
        self.is_collapsed = False
        # Animate width change
        animation = QPropertyAnimation(self, b"minimumWidth")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.setStartValue(60)
        animation.setEndValue(240)
        animation.start()
        
        animation2 = QPropertyAnimation(self, b"maximumWidth")
        animation2.setDuration(200)
        animation2.setEasingCurve(QEasingCurve.InOutQuad)
        animation2.setStartValue(60)
        animation2.setEndValue(240)
        animation2.start()
        
        # Show full text in buttons
        for btn in self.nav_buttons:
            full_text = f"{btn.icon_text}  {btn.button_text}"
            btn.setText(full_text)
            btn.setFixedWidth(-1)  # Reset to default
        
        # Show subtitle if it exists
        subtitle = self.logo_widget.findChild(QLabel, "sidebarSubtitle")
        if subtitle:
            subtitle.show()

