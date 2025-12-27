# NetDoctor Styles

This directory contains the styling resources for the NetDoctor application.

## Files

- **`blue_dark.qss`** - Comprehensive QSS theme file with styling for all Qt widgets
- **`palette.py`** - Python color palette definition with all theme colors
- **`style.qss`** - Legacy stylesheet (kept for backwards compatibility)
- **`DESIGN_DECISIONS.md`** - Detailed explanation of design choices
- **`PALETTE_README.md`** - Color palette documentation

## Quick Start

The application automatically loads `blue_dark.qss` if available, falling back to `style.qss`.

## Design Principles

1. **Flat Modern Style** - No 3D bevels, clean flat surfaces
2. **Rounded Corners** - 6-10px border-radius for modern appearance
3. **Professional Blue Palette** - Blue-based color scheme replacing purple/pink
4. **Consistent Spacing** - Uniform padding and margins throughout
5. **Typography Hierarchy** - Clear text size and weight variations
6. **High Contrast** - WCAG AA compliant color combinations

## Widget Coverage

The `blue_dark.qss` stylesheet provides complete styling for:

- ✅ QMainWindow
- ✅ QWidget (base styles)
- ✅ QLabel (with hierarchy variants)
- ✅ QPushButton (primary, secondary, danger variants)
- ✅ QLineEdit, QTextEdit, QPlainTextEdit
- ✅ QComboBox
- ✅ QSpinBox, QDoubleSpinBox
- ✅ QCheckBox, QRadioButton
- ✅ QTableWidget, QTableView
- ✅ QHeaderView
- ✅ QScrollBar (vertical & horizontal)
- ✅ QProgressBar
- ✅ QToolTip
- ✅ QMenu
- ✅ QTabWidget, QTabBar
- ✅ QGroupBox
- ✅ QListWidget
- ✅ QSlider
- ✅ QSplitter
- ✅ QDialog, QMessageBox

Plus custom application-specific widgets (sidebar, KPI cards, navigation buttons).

## Color Palette

See `palette.py` for the complete color definitions. Key colors:

- **Primary Blue**: `#4A90E2`
- **Background Main**: `#1E1E2E`
- **Background Sidebar**: `#181825`
- **Text Primary**: `#E4E4E7`
- **Border**: `#313244`

## Usage

Colors are embedded directly in the QSS file with comments indicating which palette color they represent:

```qss
QPushButton {
    background-color: #4A90E2;  /* primary_blue */
}
```

For programmatic access to colors:

```python
from netdoctor.gui.styles.palette import PALETTE
color = PALETTE["primary_blue"]  # "#4A90E2"
```

