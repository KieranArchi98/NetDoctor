"""
NetDoctor main entry point.

Bootstrap PySide6 application.
"""

import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


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
        content_widget = QWidget()
        content_widget.setStyleSheet(
            """
            QWidget {
                background-color: #0F1724;
            }
        """
        )
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)

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
        content_layout.addWidget(self.content_label)

        # Add widgets to main layout
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(content_widget, 1)

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

        # Update content (placeholder)
        self.content_label.setText(f"{name} View\n\n(Coming soon)")


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
