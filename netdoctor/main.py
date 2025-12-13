"""
NetDoctor main entry point.

Bootstrap PySide6 application.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from netdoctor.gui.main_window import MainWindow


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # Enable high DPI scaling (deprecated in Qt6, but kept for compatibility)
    try:
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    except AttributeError:
        # Attribute doesn't exist in newer Qt versions
        pass

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
