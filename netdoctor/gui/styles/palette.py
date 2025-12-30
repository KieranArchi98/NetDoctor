"""
Color palette for NetDoctor dark theme.
Blue-based professional color scheme.
"""

# Dark-mode blue color palette (aligned with netdoctor_spec.json)
PALETTE = {
    # Accent colors
    "primary_blue": "#3B82F6",  # Spec accent blue
    "secondary_blue": "#14B8A6",  # Spec accent teal
    "blue_hover": "#60A5FA",  
    "blue_active": "#2563EB",  
    
    # Background colors
    "bg_main": "#0F1724",  # Spec background
    "bg_secondary": "#111827",  # Spec surface
    "bg_sidebar": "#0b1220",  # Spec surface alternative
    "bg_card": "#111827",  
    "bg_elevated": "#1F2937",  
    
    # Border and divider colors
    "border": "#2D3748",  
    "border_light": "#4A5568",  
    "border_focus": "#3B82F6",  
    
    # Text colors
    "text_primary": "#E6EEF3",  # Spec primary text
    "text_secondary": "#9CA3AF",  # Spec muted text
    "text_muted": "#6B7280",  
    "text_accent": "#14B8A6",  
    
    # Interactive states
    "hover": "#1F2937",  
    "hover_light": "#2D3748",  
    "active": "#111827",  
    "active_accent": "#3B82F6",  
    "selection": "rgba(59, 130, 246, 0.2)",  
    
    # Status colors
    "error": "#EF4444",  # Spec alert red
    "error_hover": "#F87171",  
    "warning": "#F97316",  # Spec alert orange
    "warning_hover": "#FB923C",  
    "success": "#10B981",  
    "success_hover": "#34D399",  
    "info": "#3B82F6",  
    "info_hover": "#60A5FA",  
    
    # Specialized UI elements
    "button_primary": "#3B82F6",  
    "button_primary_hover": "#2563EB",  
    "button_primary_text": "#FFFFFF",  
    "button_secondary": "#1F2937",  
    "button_secondary_hover": "#374151",  
    "button_danger": "#EF4444",  
    "button_danger_hover": "#DC2626",  
    "button_disabled": "#111827",  
    "button_disabled_text": "#4B5563",  
    
    # Input fields
    "input_bg": "#0b1220",  
    "input_border": "#2D3748",  
    "input_focus": "#3B82F6",  
    "input_text": "#E6EEF3",  
    "input_placeholder": "#6B7280",  
    
    # Table/List
    "table_header": "#0b1220",  
    "table_header_text": "#14B8A6",  
    "table_row_even": "#111827",  
    "table_row_odd": "#0F1724",  
    "table_border": "#2D3748",  
    "table_selection": "rgba(59, 130, 246, 0.2)",  
    
    # Scrollbar
    "scrollbar_bg": "#0b1220",  
    "scrollbar_handle": "#2D3748",  
    "scrollbar_handle_hover": "#4A5568",  
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

