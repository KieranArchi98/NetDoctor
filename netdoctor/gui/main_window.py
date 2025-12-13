"""
Application shell - main window implementation.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from netdoctor.gui.views.ping_view import PingView
from netdoctor.gui.views.system_view import SystemView
from netdoctor.gui.views.portscan_view import PortScanView


class MainWindow(QMainWindow):
    """Main application window with navigation rail."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetDoctor")
        self.setMinimumSize(1000, 600)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left navigation rail
        nav_widget = QWidget()
        nav_widget.setFixedWidth(200)
        nav_widget.setStyleSheet(
            """
            QWidget {
                background-color: #111827;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 12px 16px;
                text-align: left;
                color: #9CA3AF;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: #E6EEF3;
            }
            QPushButton:checked {
                background-color: rgba(20, 184, 166, 0.12);
                color: #14B8A6;
            }
        """
        )
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        # Navigation buttons
        nav_items = ["Dashboard", "System", "Network Tools", "Reports", "Settings"]
        self.nav_buttons = []
        self.views = {}

        for item in nav_items:
            btn = QPushButton(item)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, name=item: self.on_nav_clicked(name))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # Set first button as checked
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

        nav_layout.addStretch()

        # Main content area
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(
            """
            QWidget {
                background-color: #0F1724;
            }
        """
        )
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)

        # Placeholder content
        self.content_label = QLabel("Welcome to NetDoctor")
        self.content_label.setStyleSheet(
            """
            QLabel {
                color: #E6EEF3;
                font-size: 24px;
                font-weight: bold;
            }
        """
        )
        self.content_layout.addWidget(self.content_label)

        # Add widgets to main layout
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(self.content_widget, 1)

    def on_nav_clicked(self, name: str):
        """Handle navigation button clicks."""
        # Uncheck all buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)

        # Check the clicked button
        for btn in self.nav_buttons:
            if btn.text() == name:
                btn.setChecked(True)
                break

        # Load appropriate view
        self.load_view(name)

    def load_view(self, view_name: str):
        """Load a view based on name."""
        # Clear current content - remove widgets but don't delete cached views
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                widget = child.widget()
                # Only delete if it's not a cached view
                if widget not in self.views.values():
                    widget.deleteLater()
                # Otherwise just remove from layout (widget stays alive)

        # Load view if not already created
        if view_name not in self.views:
            if view_name == "System":
                self.views[view_name] = SystemView()
            elif view_name == "Network Tools":
                # Show ping view for Network Tools
                self.views[view_name] = PingView()
            elif view_name == "Dashboard":
                # Dashboard shows ping view (can be enhanced later)
                self.views[view_name] = PingView()
            elif view_name == "Port Scan":
                # Port scan view (can be accessed via Network Tools later)
                from netdoctor.gui.views.portscan_view import PortScanView
                self.views[view_name] = PortScanView()
            else:
                # Placeholder for other views
                placeholder = QLabel(f"{view_name} View\n\n(Coming soon)")
                placeholder.setStyleSheet(
                    """
                    QLabel {
                        color: #E6EEF3;
                        font-size: 24px;
                        font-weight: bold;
                    }
                """
                )
                self.views[view_name] = placeholder

        # Add view to layout
        view = self.views[view_name]
        # Check if view is already in the layout
        already_in_layout = False
        for i in range(self.content_layout.count()):
            if self.content_layout.itemAt(i).widget() == view:
                already_in_layout = True
                break
        
        if not already_in_layout:
            self.content_layout.addWidget(view)
