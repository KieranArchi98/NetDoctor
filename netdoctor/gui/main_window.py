"""
Application shell - main window implementation.
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLabel
)
from PySide6.QtGui import QIcon

from netdoctor.gui.views.ping_view import PingView
from netdoctor.gui.views.system_view import SystemView
from netdoctor.gui.views.portscan_view import PortScanView
from netdoctor.gui.views.dashboard_view import DashboardView
from netdoctor.gui.views.reports_view import ReportsView
from netdoctor.gui.views.settings_view import SettingsView
from netdoctor.gui.widgets.sidebar import Sidebar
from netdoctor.gui.widgets.animations import fade_in


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation and stacked content."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetDoctor")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon("Assets/icon1.jpg"))
        
        # View cache - store views for reuse
        self.views = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main window UI."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.on_page_changed)
        main_layout.addWidget(self.sidebar)
        
        # Create stacked widget for content area
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("contentArea")
        main_layout.addWidget(self.stacked_widget, 1)  # Stretch factor = 1
        
        # Initialize views and add to stack
        self._initialize_views()
        
        # Animate sidebar in
        self.sidebar.animate_in(600)
        
        # Set initial page
        initial_page = self.sidebar.get_current_page()
        if initial_page:
            self.switch_to_page(initial_page)
    
    def _initialize_views(self):
        """Initialize all views and add them to the stacked widget."""
        # Add Dashboard view
        dashboard_view = self._get_or_create_view("Dashboard", DashboardView)
        self.stacked_widget.addWidget(dashboard_view)
        self.views["Dashboard"] = dashboard_view
        
        # Add System view
        system_view = self._get_or_create_view("System", SystemView)
        self.stacked_widget.addWidget(system_view)
        self.views["System"] = system_view
        
        # Add Ping view
        ping_view = self._get_or_create_view("Ping", PingView)
        self.stacked_widget.addWidget(ping_view)
        self.views["Ping"] = ping_view

        # Add PortScan view
        portscan_view = self._get_or_create_view("PortScan", PortScanView)
        self.stacked_widget.addWidget(portscan_view)
        self.views["PortScan"] = portscan_view
        
        # Add Reports view
        reports_view = self._get_or_create_view("Reports", ReportsView)
        self.stacked_widget.addWidget(reports_view)
        self.views["Reports"] = reports_view
        
        # Add Settings view
        settings_view = self._get_or_create_view("Settings", SettingsView)
        self.stacked_widget.addWidget(settings_view)
        self.views["Settings"] = settings_view
    
    def _get_or_create_view(self, page_name: str, view_class):
        """
        Get existing view or create new one.
        
        Args:
            page_name: Name of the page
            view_class: View class to instantiate
            
        Returns:
            View widget instance
        """
        if page_name in self.views:
            return self.views[page_name]
        
        view = view_class()
        return view
    
    def _create_placeholder_view(self, page_name: str) -> QWidget:
        """
        Create a placeholder view for pages not yet implemented.
        
        Args:
            page_name: Name of the page
            
        Returns:
            Placeholder widget
        """
        from netdoctor.gui.widgets.ui_components import SectionHeader, CardContainer
        from PySide6.QtCore import Qt
        
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Page header
        header = SectionHeader(page_name, f"{page_name} view - Coming soon")
        layout.addWidget(header)
        
        # Empty state card
        empty_card = CardContainer()
        card_layout = QVBoxLayout(empty_card)
        card_layout.setSpacing(12)
        
        empty_label = QLabel(f"The {page_name} view is under development.\n\nThis feature will be available in a future update.")
        empty_label.setObjectName("sectionSubtitle")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setWordWrap(True)
        card_layout.addWidget(empty_label)
        
        layout.addWidget(empty_card)
        layout.addStretch()
        
        return placeholder
    
    def on_page_changed(self, page_name: str):
        """
        Handle page change signal from sidebar.
        
        Args:
            page_name: Name of the page to switch to
        """
        self.switch_to_page(page_name)
    
    def show_toast(self, message: str, toast_type: str = "info", duration: int = 4000):
        """Show a sliding toast notification."""
        from netdoctor.gui.widgets.ui_components import ToastNotification
        toast = ToastNotification(message, toast_type, duration, self)
        toast.show_toast()

    def switch_to_page(self, page_name: str):
        """
        Switch to the specified page in the stacked widget.
        
        Args:
            page_name: Name of the page to switch to
        """
        if page_name not in self.views:
            # Create placeholder if it doesn't exist
            placeholder = self._create_placeholder_view(page_name)
            self.stacked_widget.addWidget(placeholder)
            self.views[page_name] = placeholder
        
        view = self.views[page_name]
        
        # Find the index of this view in the stacked widget
        index = self.stacked_widget.indexOf(view)
        if index == -1:
            # View not in stack, add it
            index = self.stacked_widget.addWidget(view)
        
        # Get current view for fade out
        current_index = self.stacked_widget.currentIndex()
        current_view = self.stacked_widget.currentWidget() if current_index >= 0 else None
        
        # Switch to the page immediately (required for animation to work)
        self.stacked_widget.setCurrentIndex(index)
        
        # Slide and Fade in animation for the new view
        from netdoctor.gui.widgets.animations import slide_in_from_right
        slide_in_from_right(view, duration=350)
        
        # Update sidebar active state
        self.sidebar.set_active_page(page_name)
