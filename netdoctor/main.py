"""
NetDoctor main entry point.

Bootstrap PySide6 application.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from netdoctor.gui.main_window import MainWindow


def load_stylesheet() -> str:
    """Load the application stylesheet."""
    # Try the comprehensive theme file first, fall back to style.qss
    stylesheet_path = Path(__file__).parent / "gui" / "styles" / "blue_dark.qss"
    if not stylesheet_path.exists():
        stylesheet_path = Path(__file__).parent / "gui" / "styles" / "style.qss"
    try:
        with open(stylesheet_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Stylesheet not found at {stylesheet_path}")
        return ""


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # Enable high DPI scaling (deprecated in Qt6, but kept for compatibility)
    # Qt6 handles this automatically by default now
    pass

    # Load and apply stylesheet
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
