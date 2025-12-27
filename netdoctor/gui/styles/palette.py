"""
Color palette for NetDoctor dark theme.
Blue-based professional color scheme.
"""

# Dark-mode blue color palette
PALETTE = {
    # Accent colors
    "primary_blue": "#4A90E2",  # Primary accent blue - bright, professional
    "secondary_blue": "#5BA3F5",  # Secondary accent blue - lighter variant
    "blue_hover": "#6BB6FF",  # Hover state for blue elements
    "blue_active": "#3A7BC8",  # Active/pressed state
    
    # Background colors
    "bg_main": "#1E1E2E",  # Main application background
    "bg_secondary": "#252538",  # Secondary panels, cards
    "bg_sidebar": "#181825",  # Sidebar background (darker)
    "bg_card": "#1F1F2F",  # Card/widget background
    "bg_elevated": "#2A2A3E",  # Elevated surfaces (hover states)
    
    # Border and divider colors
    "border": "#313244",  # Standard borders
    "border_light": "#3E3E52",  # Lighter borders for emphasis
    "border_focus": "#4A90E2",  # Focused input borders
    
    # Text colors
    "text_primary": "#E4E4E7",  # Primary text - high contrast
    "text_secondary": "#A1A1AA",  # Secondary text - medium contrast
    "text_muted": "#71717A",  # Muted text - low contrast
    "text_accent": "#4A90E2",  # Accent text color
    
    # Interactive states
    "hover": "#2A2A3E",  # General hover background
    "hover_light": "#313244",  # Light hover overlay
    "active": "#1F2937",  # Active selection background
    "active_accent": "#4A90E2",  # Active selection with accent
    "selection": "rgba(74, 144, 226, 0.15)",  # Selection highlight (transparent blue)
    
    # Status colors
    "error": "#EF4444",  # Error/red
    "error_hover": "#F87171",  # Error hover state
    "warning": "#F59E0B",  # Warning/orange
    "warning_hover": "#FBBF24",  # Warning hover state
    "success": "#10B981",  # Success/green
    "success_hover": "#34D399",  # Success hover state
    "info": "#3B82F6",  # Info blue
    "info_hover": "#60A5FA",  # Info hover state
    
    # Specialized UI elements
    "button_primary": "#4A90E2",  # Primary button background
    "button_primary_hover": "#5BA3F5",  # Primary button hover
    "button_primary_text": "#FFFFFF",  # Primary button text
    "button_secondary": "#313244",  # Secondary button background
    "button_secondary_hover": "#3E3E52",  # Secondary button hover
    "button_danger": "#EF4444",  # Danger button background
    "button_danger_hover": "#F87171",  # Danger button hover
    "button_disabled": "#1F1F2F",  # Disabled button background
    "button_disabled_text": "#71717A",  # Disabled button text
    
    # Input fields
    "input_bg": "#181825",  # Input background
    "input_border": "#313244",  # Input border
    "input_focus": "#4A90E2",  # Input focus border
    "input_text": "#E4E4E7",  # Input text color
    "input_placeholder": "#71717A",  # Placeholder text
    
    # Table/List
    "table_header": "#181825",  # Table header background
    "table_header_text": "#4A90E2",  # Table header text
    "table_row_even": "#1F1F2F",  # Even row background
    "table_row_odd": "#181825",  # Odd row background
    "table_border": "#313244",  # Table borders
    "table_selection": "rgba(74, 144, 226, 0.2)",  # Selected row
    
    # Scrollbar
    "scrollbar_bg": "#181825",  # Scrollbar background
    "scrollbar_handle": "#313244",  # Scrollbar handle
    "scrollbar_handle_hover": "#3E3E52",  # Scrollbar handle hover
}


def get_qss_palette() -> str:
    """
    Return QSS-ready color palette as comments.
    Since QSS doesn't support CSS variables, this serves as documentation.
    """
    qss = "/* NetDoctor Blue Dark Theme Color Palette */\n"
    qss += "/* Primary Accent Colors */\n"
    qss += f"/* primary_blue: {PALETTE['primary_blue']} */\n"
    qss += f"/* secondary_blue: {PALETTE['secondary_blue']} */\n"
    qss += f"/* blue_hover: {PALETTE['blue_hover']} */\n"
    qss += f"/* blue_active: {PALETTE['blue_active']} */\n\n"
    
    qss += "/* Background Colors */\n"
    qss += f"/* bg_main: {PALETTE['bg_main']} */\n"
    qss += f"/* bg_secondary: {PALETTE['bg_secondary']} */\n"
    qss += f"/* bg_sidebar: {PALETTE['bg_sidebar']} */\n"
    qss += f"/* bg_card: {PALETTE['bg_card']} */\n"
    qss += f"/* bg_elevated: {PALETTE['bg_elevated']} */\n\n"
    
    qss += "/* Border Colors */\n"
    qss += f"/* border: {PALETTE['border']} */\n"
    qss += f"/* border_light: {PALETTE['border_light']} */\n"
    qss += f"/* border_focus: {PALETTE['border_focus']} */\n\n"
    
    qss += "/* Text Colors */\n"
    qss += f"/* text_primary: {PALETTE['text_primary']} */\n"
    qss += f"/* text_secondary: {PALETTE['text_secondary']} */\n"
    qss += f"/* text_muted: {PALETTE['text_muted']} */\n"
    qss += f"/* text_accent: {PALETTE['text_accent']} */\n\n"
    
    qss += "/* Interactive States */\n"
    qss += f"/* hover: {PALETTE['hover']} */\n"
    qss += f"/* active: {PALETTE['active']} */\n"
    qss += f"/* selection: {PALETTE['selection']} */\n\n"
    
    qss += "/* Status Colors */\n"
    qss += f"/* error: {PALETTE['error']} */\n"
    qss += f"/* warning: {PALETTE['warning']} */\n"
    qss += f"/* success: {PALETTE['success']} */\n"
    qss += f"/* info: {PALETTE['info']} */\n\n"
    
    return qss


if __name__ == "__main__":
    # Print palette for verification
    print("NetDoctor Color Palette")
    print("=" * 50)
    for category, color in PALETTE.items():
        print(f"{category:25} : {color}")
    
    print("\n" + "=" * 50)
    print("\nQSS Documentation:")
    print(get_qss_palette())

