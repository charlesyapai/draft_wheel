# gui/config.py
"""
Configuration module for Draft GUI
Centralizes all UI settings and configurations
"""

DEFAULT_UI_CONFIG = {
    # Fonts
    "text_font_type": "Arial",
    "text_font_size": 9,
    "header_font_size": 12,
    "subheader_font_size": 10,
    "button_font_size": 11,
    "tree_font_size": 11,
    "tree_header_font_size": 10,
    
    # Role Button Specific Settings
    "role_button_font_type": "Segoe UI",  # Modern clean font
    "role_button_font_size": 9,
    "role_button_padding": 2,
    "role_button_width": 5,  # Width in characters
    "role_button_spacing": 1, # Spacing between buttons
    
    # Colors
    "main_bg_color": "#F5F5F5",
    "frame_bg_color": "#EEEEEE",
    "controls_bg_color": "#DDDDDD",
    "canvas_bg_color": "white",
    "sigmoid_bg_color": "#1E1E2F",  # Dark blue/purple gaming background
    "sigmoid_grid_color": "#444466",  # Subtle grid lines
    "sigmoid_axis_color": "#8080FF",  # Bright blue axes
    "sigmoid_text_color": "#FFFFFF",  # White text
    "sigmoid_point_color": "#00FFFF",  # Cyan points
    "sigmoid_line_color": "#FF00FF",  # Magenta curve
    "sigmoid_ideal_line_color": "#00FF00",  # Bright green ideal line
    "button_fg_color": "brown",
    "button_select_color": "#FFD700",
    "pointer_color": "red",
    "banner_bg_color": "#CCCCCC",
    "teams_bg_color": "#F0F0F0",
    "team_selected_border_color": "#1E90FF",  # Bright blue for selected team
    "team_hover_border_color": "#A0A0A0",     # Medium gray for hover effect
    
    # Dimensions
    "min_window_width": 900,
    "min_window_height": 600,
    "wheel_size": 700,
    "wheel_height": 200,
    "mmr_chart_width": 600,
    "mmr_chart_height": 150,
    "role_chart_width": 600,
    "role_chart_height": 180,
    "sigmoid_chart_width": 400,
    "sigmoid_chart_height": 250,
    "role_listbox_height": 8,
    
    # Layout
    "padding": 5,
    "button_padding": 5,
    "frame_padding": 10,
    "left_panel_weight": 1,
    "center_panel_weight": 3,
    "right_panel_weight": 2,
    "scale_frame_weight": 3,
    "prob_frame_weight": 2,
    "chart_left_weight": 2,
    "chart_right_weight": 1,
    
    # Team colors
    "team_colors": ["#FFD700", "#ADFF2F", "#40E0D0", "#FF69B4", "#FF7F50", "#9ACD32", "#9370DB", "#FFB6C1"]
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
                
            return config
        except Exception as e:
            print(f"Error loading config file: {e}")
            return DEFAULT_UI_CONFIG.copy()
    else:
        return DEFAULT_UI_CONFIG.copy() 