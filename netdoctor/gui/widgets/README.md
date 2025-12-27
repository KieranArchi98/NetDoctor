# UI Components

Reusable UI components styled with PyDracula-inspired blue theme.

## Components

### Card Components

#### KPICard
Simple card for displaying key performance indicators with title and value.

```python
from netdoctor.gui.widgets import KPICard

card = KPICard("CPU Usage", "45.2%")
card.set_value("50.1%")
```

#### StatCard
Card with icon, value, change indicator, and optional title.

```python
from netdoctor.gui.widgets import StatCard

card = StatCard("📊", "1,234", "+12%", "Total Requests")
card.set_value("1,456")
```

#### CardContainer
General-purpose card container with optional hover elevation effect.

```python
from netdoctor.gui.widgets import CardContainer
from PySide6.QtWidgets import QVBoxLayout, QLabel

card = CardContainer(hover_elevation=True)
layout = QVBoxLayout(card)
layout.addWidget(QLabel("Card content"))
```

### Navigation Components

#### SectionHeader
Styled section header with title, optional subtitle, and action buttons.

```python
from netdoctor.gui.widgets import SectionHeader

header = SectionHeader("Section Title", "Optional subtitle")
header.add_action_button("Action", callback_function, "primary")
```

#### IconButton
Icon-only button with hover effects and tooltip.

```python
from netdoctor.gui.widgets import IconButton

btn = IconButton("⚙️", "Settings")
btn.clicked.connect(settings_callback)
```

### Dialog Components

#### ModalDialog
Styled modal dialog with header, message, and customizable buttons.

```python
from netdoctor.gui.widgets import ModalDialog

dialog = ModalDialog("Confirm Action", "Are you sure you want to proceed?")
dialog.add_button("Cancel", "secondary", dialog.reject)
dialog.add_button("Confirm", "primary", dialog.accept)
result = dialog.exec()
```

#### ProgressDialog
Modal progress dialog with cancel option.

```python
from netdoctor.gui.widgets import ProgressDialog

dialog = ProgressDialog("Processing files...", cancelable=True)
dialog.set_range(0, 100)
dialog.set_value(50)
if dialog.exec():
    # User cancelled
    pass
```

### Notification Components

#### ToastNotification
Slide-in toast notification with auto-dismiss.

```python
from netdoctor.gui.widgets import ToastNotification

toast = ToastNotification("Operation completed!", "success", duration=3000, parent=main_window)
toast.show_toast()
```

Toast types: `"info"`, `"success"`, `"warning"`, `"error"`

### Progress Components

#### ProgressIndicator
Styled progress bar with optional label.

```python
from netdoctor.gui.widgets import ProgressIndicator

progress = ProgressIndicator("Processing...")
progress.set_range(0, 100)
progress.set_value(50)
```

#### LoadingSpinner
Animated loading spinner indicator.

```python
from netdoctor.gui.widgets import LoadingSpinner

spinner = LoadingSpinner(size=32)
spinner.start()
# ... do work ...
spinner.stop()
```

## Design Features

All components feature:
- **Rounded corners**: 6-10px border-radius
- **Soft shadows**: Subtle elevation through background color changes
- **Hover effects**: Background color transitions on interactive elements
- **Consistent spacing**: Uniform padding and margins
- **Typography hierarchy**: Clear text size and weight variations
- **Blue theme**: Professional blue color palette

## Button Types

When adding buttons to components, use these button types:
- `"primary"`: Primary action (blue)
- `"secondary"`: Secondary action (dark)
- `"danger"`: Destructive action (red)

## Color Palette

Components use the following colors:
- Primary Blue: `#4A90E2`
- Background Card: `#1F1F2F`
- Border: `#313244`
- Text Primary: `#E4E4E7`
- Text Secondary: `#A1A1AA`

## Example: Complete Layout

```python
from netdoctor.gui.widgets import (
    SectionHeader, KPICard, CardContainer, IconButton
)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

widget = QWidget()
layout = QVBoxLayout(widget)
layout.setSpacing(16)

# Section header
header = SectionHeader("Dashboard", "System overview")
header.add_action_button("Refresh", refresh_callback, "primary")
layout.addWidget(header)

# KPI cards row
cards_layout = QHBoxLayout()
cpu_card = KPICard("CPU Usage", "45%")
memory_card = KPICard("Memory Usage", "62%")
cards_layout.addWidget(cpu_card)
cards_layout.addWidget(memory_card)
layout.addLayout(cards_layout)

# Content card
content_card = CardContainer()
card_layout = QVBoxLayout(content_card)
card_layout.addWidget(QLabel("Content here..."))
layout.addWidget(content_card)
```

## Styling

All components are styled via the global QSS stylesheet (`blue_dark.qss`). Component-specific styles use object names for targeted styling.

To customize, modify the QSS file or extend components with additional styling.

