"""
Test application for the modernized UI components
Demonstrates the modernized probability view with gaming-themed UI
"""
import os
import sys
import tkinter as tk
import random
from tkinter import ttk

# Add project root to system path to allow imports to work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import our modernized components
from gui.components.modern_toolkit import ThemeManager, ModernFrame
from gui.components.modern_probability_view import ModernProbabilityView

def generate_test_data(num_players=10):
    """
    Generate random test data for probability view
    
    Returns:
        tuple: (player_colors, player_mmrs, probs, ideal_mmr, role_prefs)
    """
    # Player names
    players = [f"Player{i}" for i in range(1, num_players + 1)]
    
    # Generate random MMRs (1000-3000)
    player_mmrs = {p: random.randint(1000, 3000) for p in players}
    
    # Set ideal MMR somewhere in the middle
    ideal_mmr = random.randint(1800, 2200)
    
    # Generate probabilities based on MMR closeness to ideal
    total_weight = 0
    weights = {}
    
    for p, mmr in player_mmrs.items():
        # Weight inversely proportional to distance from ideal MMR
        dist = abs(mmr - ideal_mmr)
        weight = 1.0 / (1.0 + dist/500.0)
        weights[p] = weight
        total_weight += weight
    
    # Normalize weights to get probabilities
    probs = {p: w/total_weight for p, w in weights.items()}
    
    # Generate role preferences (1-3)
    role_prefs = {p: random.randint(1, 3) for p in players}
    
    # Generate player colors
    colors = [
        "#FF5252", "#FF4081", "#9C27B0", "#673AB7", 
        "#3F51B5", "#2196F3", "#03A9F4", "#00BCD4",
        "#009688", "#4CAF50", "#8BC34A", "#CDDC39",
        "#FFEB3B", "#FFC107", "#FF9800", "#FF5722"
    ]
    
    player_colors = {p: random.choice(colors) for p in players}
    
    return player_colors, player_mmrs, probs, ideal_mmr, role_prefs

def main():
    """Launch the test application"""
    # Create root window
    root = tk.Tk()
    root.title("Modern UI Demo - Draft Wheel")
    root.geometry("1200x800")
    
    # Create theme manager
    theme_manager = ThemeManager(initial_theme="cyber")
    theme = theme_manager.get_theme()
    
    # Set window background
    root.configure(bg=theme["app_bg"])
    
    # Create main frame
    main_frame = tk.Frame(root, bg=theme["app_bg"])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create header
    header_frame = ModernFrame(
        main_frame,
        title="Modern Probability View Demo",
        theme_manager=theme_manager,
        height=80,
        collapsible=False
    )
    header_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Header content
    header_content = tk.Frame(
        header_frame.content_frame,
        bg=theme["panel_bg"]
    )
    header_content.pack(fill=tk.BOTH, expand=True)
    
    # Logo text
    logo_text = tk.Label(
        header_content,
        text="DRAFT WHEEL",
        font=("Segoe UI", 24, "bold"),
        bg=theme["panel_bg"],
        fg=theme["accent"]
    )
    logo_text.pack(side=tk.LEFT, padx=20)
    
    # Theme selector
    theme_frame = tk.Frame(header_content, bg=theme["panel_bg"])
    theme_frame.pack(side=tk.RIGHT, padx=20, pady=10)
    
    tk.Label(
        theme_frame,
        text="Theme:",
        font=("Segoe UI", 12),
        bg=theme["panel_bg"],
        fg=theme["text"]
    ).pack(side=tk.LEFT, padx=(0, 10))
    
    # Theme combobox
    theme_var = tk.StringVar(value=theme_manager.current_theme)
    theme_combo = ttk.Combobox(
        theme_frame,
        textvariable=theme_var,
        values=list(theme_manager.THEMES.keys()),
        width=10,
        state="readonly"
    )
    theme_combo.pack(side=tk.LEFT)
    
    # Create content area
    content_frame = tk.Frame(main_frame, bg=theme["app_bg"])
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create modern probability view
    probability_view = ModernProbabilityView(content_frame, theme_manager)
    
    # Create footer
    footer_frame = ModernFrame(
        main_frame,
        title="Controls",
        theme_manager=theme_manager,
        height=60,
        collapsible=False
    )
    footer_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Footer content
    footer_content = tk.Frame(
        footer_frame.content_frame,
        bg=theme["panel_bg"]
    )
    footer_content.pack(fill=tk.BOTH, expand=True)
    
    # Refresh button
    refresh_btn = tk.Button(
        footer_content,
        text="Generate Random Data",
        command=lambda: refresh_data(probability_view),
        bg=theme["accent"],
        fg="white",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        padx=20,
        pady=5
    )
    refresh_btn.pack(side=tk.LEFT, padx=20, pady=10)
    
    # Function to update frame colors on theme change
    def update_frame_colors(theme):
        root.configure(bg=theme["app_bg"])
        main_frame.configure(bg=theme["app_bg"])
        content_frame.configure(bg=theme["app_bg"])
        header_content.configure(bg=theme["panel_bg"])
        logo_text.configure(bg=theme["panel_bg"], fg=theme["accent"])
        theme_frame.configure(bg=theme["panel_bg"])
        footer_content.configure(bg=theme["panel_bg"])
        refresh_btn.configure(bg=theme["accent"])
        
        # Update theme label
        for widget in theme_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["panel_bg"], fg=theme["text"])
    
    # Register theme change listener
    theme_manager.register_listener(update_frame_colors)
    
    # Handle theme selection
    def on_theme_selected(event):
        new_theme = theme_var.get()
        theme_manager.set_theme(new_theme)
    
    theme_combo.bind("<<ComboboxSelected>>", on_theme_selected)
    
    # Generate initial data
    refresh_data(probability_view)
    
    # Start the main loop
    root.mainloop()

def refresh_data(probability_view):
    """Generate new random data and update the view"""
    # Generate random data
    player_colors, player_mmrs, probs, ideal_mmr, role_prefs = generate_test_data()
    
    # Set player colors
    probability_view.set_player_colors(player_colors)
    
    # Update probability view
    probability_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)

if __name__ == "__main__":
    main() 