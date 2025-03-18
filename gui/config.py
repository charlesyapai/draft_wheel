# gui/config.py
"""
Configuration module for Draft GUI
Centralizes all UI settings and configurations
"""

DEFAULT_UI_CONFIG = {
    # Fonts
    "text_font_type": "Segoe UI",  # Modern font that works well on most systems
    "text_font_size": 10,
    "header_font_size": 14,
    "subheader_font_size": 12,
    "button_font_size": 11,
    "tree_font_size": 11,
    "tree_header_font_size": 10,
    
    # Role Button Specific Settings
    "role_button_font_type": "Segoe UI",  # Modern clean font
    "role_button_font_size": 10,
    "role_button_padding": 3,
    "role_button_width": 6,  # Width in characters
    "role_button_spacing": 2, # Spacing between buttons
    
    # Colors - Modern Gaming Themed
    "main_bg_color": "#121212",    # Dark gray background
    "frame_bg_color": "#1E1E1E",   # Slightly lighter gray for frames
    "controls_bg_color": "#252525", # Dark controls background
    "canvas_bg_color": "#1E1E1E",   # Dark chart background
    "sigmoid_bg_color": "#101025",  # Dark blue for sigmoid chart
    "button_fg_color": "#00AAFF",   # Bright blue for buttons
    "button_select_color": "#00DDAA", # Teal for selected buttons
    "pointer_color": "#FF3366",     # Bright pink for pointer
    "banner_bg_color": "#101025",   # Dark blue banner
    "teams_bg_color": "#1E1E1E",    # Same as frame for consistency
    "team_selected_border_color": "#00DDAA",  # Teal for selected team
    "team_hover_border_color": "#3399FF",     # Light blue for hover effect
    "text_color": "#FFFFFF",        # White text
    "secondary_text_color": "#AAAACC", # Light blue-gray secondary text
    
    # Dimensions
    "min_window_width": 1024,
    "min_window_height": 768,
    "wheel_size": 800,
    "wheel_height": 250,
    "mmr_chart_width": 700,
    "mmr_chart_height": 200,
    "role_chart_width": 700,
    "role_chart_height": 200,
    "sigmoid_chart_width": 500,
    "sigmoid_chart_height": 300,
    "role_listbox_height": 10,
    
    # Layout
    "padding": 8,
    "button_padding": 8,
    "frame_padding": 12,
    "left_panel_weight": 1,
    "center_panel_weight": 3,
    "right_panel_weight": 2,
    "scale_frame_weight": 3,
    "prob_frame_weight": 2,
    "chart_left_weight": 2,
    "chart_right_weight": 1,
    
    # Team colors - Vibrant Gaming Palette
    "team_colors": [
        "#FF5500", # Bright Orange
        "#00DDFF", # Cyan
        "#FFCC00", # Gold
        "#FF00AA", # Magenta 
        "#00DD88", # Green
        "#AA66FF", # Purple
        "#FF3366", # Pink
        "#66BBFF"  # Light Blue
    ],
    
    # Themes
    "use_modern_ui": True,    # Enable modern UI components
    "current_theme": "cyber", # Default theme (cyber, dark, light)
    "theme_options": ["cyber", "dark", "light"],
    
    # Animation settings
    "enable_animations": True,
    "animation_speed": 300,   # milliseconds
}

# Theme-specific colors that override the defaults
THEME_OVERRIDES = {
    "dark": {
        "main_bg_color": "#121212",
        "frame_bg_color": "#1E1E1E",
        "controls_bg_color": "#252525",
        "canvas_bg_color": "#1E1E1E",
        "sigmoid_bg_color": "#252525",
        "text_color": "#FFFFFF",
        "secondary_text_color": "#BBBBBB",
    },
    "light": {
        "main_bg_color": "#F0F0F0",
        "frame_bg_color": "#FFFFFF",
        "controls_bg_color": "#F5F5F5",
        "canvas_bg_color": "#FFFFFF",
        "sigmoid_bg_color": "#F8F8F8",
        "text_color": "#111111",
        "secondary_text_color": "#555555",
    },
    "cyber": {
        "main_bg_color": "#050510",
        "frame_bg_color": "#0A0A1A",
        "controls_bg_color": "#101025",
        "canvas_bg_color": "#0A0A1A",
        "sigmoid_bg_color": "#101025",
        "button_fg_color": "#00FFAA",
        "button_select_color": "#00DDFF",
        "pointer_color": "#FF2266",
        "banner_bg_color": "#0D0D20",
        "text_color": "#EEEEFF",
        "secondary_text_color": "#AAAACC",
    }
}

def load_config(config_file=None):
    """
    Load configuration from file if provided, otherwise return default
    
    Args:
        config_file: Path to JSON/YAML config file (optional)
        
    Returns:
        dict: Configuration dictionary
    """
    if config_file:
        try:
            import json
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                
            # Merge with defaults (custom settings override defaults)
            config = DEFAULT_UI_CONFIG.copy()
            for key, value in custom_config.items():
                config[key] = value
            
            # Apply theme overrides if specified
            if "current_theme" in config and config["current_theme"] in THEME_OVERRIDES:
                theme_overrides = THEME_OVERRIDES[config["current_theme"]]
                for key, value in theme_overrides.items():
                    config[key] = value
                
            return config
        except Exception as e:
            print(f"Error loading config file: {e}")
            return DEFAULT_UI_CONFIG.copy()
    else:
        config = DEFAULT_UI_CONFIG.copy()
        
        # Apply theme overrides for default theme
        default_theme = config["current_theme"]
        if default_theme in THEME_OVERRIDES:
            theme_overrides = THEME_OVERRIDES[default_theme]
            for key, value in theme_overrides.items():
                config[key] = value
                
        return config 