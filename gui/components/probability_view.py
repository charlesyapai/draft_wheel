"""
Probability View Component
Handles the probability display and sigmoid chart
"""
from gui.components.modern_probability_view import ModernProbabilityView
from gui.components.modern_toolkit import ThemeManager

class ProbabilityView:
    """Component for displaying probabilities and sigmoid chart"""
    
    def __init__(self, parent, ui_config):
        """
        Initialize the probability view
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dict
        """
        self.parent = parent
        self.ui_config = ui_config
        self.player_colors = {}
        
        # Create theme manager
        self.theme_manager = ThemeManager("dark")
        
        # Create modern probability view
        self.modern_view = ModernProbabilityView(parent, self.theme_manager)
        
    def update_probabilities(self, probs, player_mmrs, ideal_mmr, role_prefs=None):
        """
        Update probability display
        
        Args:
            probs: Dict of {player: probability}
            player_mmrs: Dict of {player: mmr}
            ideal_mmr: Ideal MMR for the pick
            role_prefs: Dict of {player: preference} for the current role
        """
        if not probs:
            self.clear()
            return
            
        # Update colors based on UI config
        team_colors = self.ui_config.get("team_colors", [])
        if team_colors:
            # Set team colors if available
            idx = 0
            player_colors = {}
            for p in probs.keys():
                color = team_colors[idx % len(team_colors)]
                player_colors[p] = color
                idx += 1
            self.player_colors = player_colors
            self.modern_view.set_player_colors(player_colors)
        
        # Update the modern view
        self.modern_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)
    
    def clear(self):
        """Clear the probability display"""
        self.modern_view.clear()
        self.player_colors = {}
    
    def get_player_colors(self):
        """
        Get the current player colors
        
        Returns:
            dict: Map of player names to colors
        """
        return self.player_colors.copy()


# Legacy class, kept for compatibility
class SigmoidChartView:
    """Legacy sigmoid chart view for compatibility"""
    
    def __init__(self, parent, ui_config):
        """
        Initialize the sigmoid chart view
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dict
        """
        self.parent = parent
        self.ui_config = ui_config
        self.player_colors = {}
        
    def draw_final_probability_curve(self, data_list, ideal_mmr):
        """
        Legacy method - does nothing, as chart is handled by ModernProbabilityView
        
        Args:
            data_list: List of (player, mmr, diff, probability) tuples
            ideal_mmr: Ideal MMR value to show as reference line
        """
        # Functionality now handled by ModernProbabilityView
        pass
    
    def clear(self):
        """Clear the sigmoid chart"""
        # Functionality now handled by ModernProbabilityView
        pass
    
    def set_player_colors(self, colors):
        """
        Set player colors for chart
        
        Args:
            colors: Dict of {player: color}
        """
        self.player_colors = colors.copy() 