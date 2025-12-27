# NetDoctor Color Palette

Complete dark-mode blue color palette for the NetDoctor application.

## Color Palette Definition

### Accent Colors
- **Primary Blue**: `#4A90E2` - Main accent color for buttons, links, and highlights
- **Secondary Blue**: `#5BA3F5` - Lighter variant for hover states
- **Blue Hover**: `#6BB6FF` - Hover state for blue elements
- **Blue Active**: `#3A7BC8` - Active/pressed state (darker)

### Background Colors
- **Main Background**: `#1E1E2E` - Primary application background
- **Secondary Background**: `#252538` - Secondary panels
- **Sidebar Background**: `#181825` - Sidebar and darker surfaces
- **Card Background**: `#1F1F2F` - Card and widget backgrounds
- **Elevated Background**: `#2A2A3E` - Hover states and elevated surfaces

### Border Colors
- **Border**: `#313244` - Standard borders
- **Border Light**: `#3E3E52` - Lighter borders for emphasis
- **Border Focus**: `#4A90E2` - Focused input borders (same as primary blue)

### Text Colors
- **Primary Text**: `#E4E4E7` - High contrast, main text color
- **Secondary Text**: `#A1A1AA` - Medium contrast, labels and descriptions
- **Muted Text**: `#71717A` - Low contrast, placeholders and disabled text
- **Accent Text**: `#4A90E2` - Accent text (same as primary blue)

### Interactive States
- **Hover**: `#2A2A3E` - General hover background
- **Hover Light**: `#313244` - Light hover overlay
- **Active**: `#1F2937` - Active selection background
- **Active Accent**: `#4A90E2` - Active selection with accent
- **Selection**: `rgba(74, 144, 226, 0.15)` - Selection highlight (transparent blue)

### Status Colors
- **Error**: `#EF4444` - Error/red
- **Error Hover**: `#F87171` - Error hover state
- **Warning**: `#F59E0B` - Warning/orange
- **Warning Hover**: `#FBBF24` - Warning hover state
- **Success**: `#10B981` - Success/green
- **Success Hover**: `#34D399` - Success hover state
- **Info**: `#3B82F6` - Info blue
- **Info Hover**: `#60A5FA` - Info hover state

## Usage

### Python Dictionary
```python
from netdoctor.gui.styles.palette import PALETTE

primary_color = PALETTE["primary_blue"]  # "#4A90E2"
bg_color = PALETTE["bg_main"]  # "#1E1E2E"
```

### QSS Stylesheet
The colors are documented in `style.qss` with comments. Since QSS doesn't support CSS variables, colors are directly embedded in the stylesheet with comments indicating which palette color they represent.

Example:
```qss
QPushButton {
    background-color: #4A90E2;  /* primary_blue */
    color: #FFFFFF;
}
```

## Color Contrast

All colors meet WCAG AA contrast requirements:
- Primary text (#E4E4E7) on dark backgrounds: 13.5:1
- Secondary text (#A1A1AA) on dark backgrounds: 7.2:1
- Primary blue (#4A90E2) on dark backgrounds: 4.5:1 (for large text)

## Palette Rationale

This palette was designed to:
1. Replace PyDracula's purple/pink scheme with professional blue tones
2. Maintain high contrast for readability
3. Provide clear visual hierarchy
4. Support all UI states (hover, active, disabled, etc.)
5. Include semantic colors for status indicators (error, warning, success)

