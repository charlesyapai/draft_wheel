#!/usr/bin/env python3
"""
Modern Draft Wheel Application
A modernized, gaming-themed UI for the Draft Wheel
"""
import os
import sys
import tkinter as tk
import argparse

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import configuration and logic
from config.loader import ConfigRetrieval

# Import the ModernDraftWheel class
from modern_draft_wheel_ui import ModernDraftWheel

def main():
    """Main entry point for the application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Modern Draft Wheel Application")
    parser.add_argument('--config', default="data/draft_wheel_configs.yaml", 
                        help="Path to config file")
    parser.add_argument('--theme', default="cyber", choices=["cyber", "dark", "light"],
                        help="Initial theme to use")
    args = parser.parse_args()
    
    # Load configuration
    try:
        cfg_obj = ConfigRetrieval(args.config)
        cfg = cfg_obj.get_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Create root window
    root = tk.Tk()
    root.title("Modern Draft Wheel")
    root.geometry("1400x800")
    
    # Create application
    app = ModernDraftWheel(root, cfg)
    
    # Set initial theme
    app.theme_manager.set_theme(args.theme)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 