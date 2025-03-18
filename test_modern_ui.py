"""
Test application for Modern UI components
"""
import tkinter as tk
import random
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import our components
from gui.components.modern_toolkit import ThemeManager, ModernButton
from gui.components.modern_probability_view import ModernProbabilityView

def generate_test_data(num_players=8):
    """Generate random test data for the probability view"""
    player_names = ["Player" + str(i+1) for i in range(num_players)]
    
    # Generate random MMRs between 1000 and 2500
    player_mmrs = {p: random.randint(1000, 2500) for p in player_names}
    
    # Generate random probabilities that sum to 1.0
    raw_probs = [random.random() for _ in range(num_players)]
    total = sum(raw_probs)
    probs = {p: prob / total for p, prob in zip(player_names, raw_probs)}
    
    # Calculate ideal MMR as average
    ideal_mmr = sum(player_mmrs.values()) / len(player_mmrs)
    
    # Generate random role preferences (1-3)
    role_prefs = {p: random.randint(1, 3) for p in player_names}
    
    return probs, player_mmrs, ideal_mmr, role_prefs

def main():
    """Main test application"""
    # Create root window
    root = tk.Tk()
    root.title("Modern UI Test")
    root.geometry("1200x800")
    
    # Create theme manager
    theme_manager = ThemeManager("cyber")  # Start with cyber theme
    
    # Create main container with panel manager
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create a header section
    header_bg = theme_manager.get_theme()["header_bg"]
    header_fg = theme_manager.get_theme()["text"]
    header = tk.Frame(main_frame, bg=header_bg, height=60)
    header.pack(fill=tk.X)
    
    # Add title to header
    title = tk.Label(
        header, 
        text="DRAFT WHEEL", 
        font=("Segoe UI", 20, "bold"),
        bg=header_bg,
        fg=header_fg
    )
    title.pack(side=tk.LEFT, padx=20, pady=10)
    
    # Add theme selector to header
    theme_frame = tk.Frame(header, bg=header_bg)
    theme_frame.pack(side=tk.RIGHT, padx=20, pady=10)
    
    # Theme label
    theme_label = tk.Label(
        theme_frame,
        text="Theme:",
        font=("Segoe UI", 12),
        bg=header_bg,
        fg=header_fg
    )
    theme_label.pack(side=tk.LEFT, padx=5)
    
    # Theme buttons
    for theme_name in ["cyber", "dark", "light"]:
        btn = ModernButton(
            theme_frame,
            text=theme_name.capitalize(),
            command=lambda tn=theme_name: theme_manager.set_theme(tn),
            theme_manager=theme_manager,
            size="small"
        )
        btn.pack(side=tk.LEFT, padx=5)
    
    # Create modern probability view
    prob_view = ModernProbabilityView(main_frame, theme_manager)
    
    # Generate random test data
    probs, player_mmrs, ideal_mmr, role_prefs = generate_test_data(8)
    
    # Update probability view with test data
    prob_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)
    
    # Create footer with control buttons
    footer_bg = theme_manager.get_theme()["header_bg"]
    footer = tk.Frame(main_frame, bg=footer_bg, height=50)
    footer.pack(fill=tk.X, side=tk.BOTTOM)
    
    # Add buttons to footer
    refresh_btn = ModernButton(
        footer,
        text="Refresh Data",
        command=lambda: refresh_data(prob_view),
        theme_manager=theme_manager,
        size="medium"
    )
    refresh_btn.pack(side=tk.RIGHT, padx=20, pady=10)
    
    # Register theme change callback for header and footer
    def update_frame_colors(theme):
        header_bg = theme["header_bg"]
        header_fg = theme["text"]
        header.configure(bg=header_bg)
        title.configure(bg=header_bg, fg=header_fg)
        theme_frame.configure(bg=header_bg)
        theme_label.configure(bg=header_bg, fg=header_fg)
        footer.configure(bg=header_bg)
    
    theme_manager.register_listener(update_frame_colors)
    
    # Start the main loop
    root.mainloop()

def refresh_data(prob_view):
    """Refresh the probability view with new random data"""
    probs, player_mmrs, ideal_mmr, role_prefs = generate_test_data(8)
    prob_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)

if __name__ == "__main__":
    main() 