"""
HikmahYT - Style Configuration
Modern dark theme with gradient-like accents
"""

# Color Palette
COLORS = {
    # Primary
    "bg_dark": "#0f0f0f",
    "bg_main": "#181818",
    "bg_secondary": "#212121",
    "bg_card": "#272727",
    "bg_card_hover": "#333333",
    "bg_input": "#1e1e1e",
    
    # Accent
    "accent_primary": "#ff0050",
    "accent_secondary": "#ff3366",
    "accent_gradient_start": "#ff0050",
    "accent_gradient_end": "#ff6b35",
    "accent_blue": "#3ea6ff",
    "accent_green": "#2ecc71",
    "accent_purple": "#9b59b6",
    "accent_orange": "#ff6b35",
    
    # Text
    "text_primary": "#ffffff",
    "text_secondary": "#aaaaaa",
    "text_muted": "#717171",
    "text_accent": "#ff0050",
    
    # States
    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c",
    "info": "#3ea6ff",
    
    # Border
    "border": "#333333",
    "border_focus": "#ff0050",
    
    # Progress
    "progress_bg": "#333333",
    "progress_fill": "#ff0050",
}

# Font Configuration
FONTS = {
    "logo": ("Segoe UI Black", 28, "bold"),
    "logo_accent": ("Segoe UI Black", 28, "bold"),
    "heading": ("Segoe UI", 22, "bold"),
    "subheading": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 13),
    "body_bold": ("Segoe UI", 13, "bold"),
    "small": ("Segoe UI", 11),
    "tiny": ("Segoe UI", 10),
    "button": ("Segoe UI Semibold", 13),
    "tag": ("Segoe UI", 10, "bold"),
}

# Widget Dimensions
DIMENSIONS = {
    "window_width": 1100,
    "window_height": 750,
    "min_width": 900,
    "min_height": 650,
    "card_corner": 15,
    "button_corner": 10,
    "input_corner": 12,
    "entry_height": 48,
    "button_height": 45,
    "sidebar_width": 220,
    "thumbnail_width": 320,
    "thumbnail_height": 180,
}

# Animation
ANIMATION = {
    "hover_duration": 150,
    "transition_duration": 300,
}