"""
Modern Probability View
A modernized, gaming-themed implementation of the probability view
with dockable panels, fluid layout, and enhanced visuals
"""
import tkinter as tk

from gui.components.modern_toolkit import ThemeManager, ModernFrame, PanelManager
from gui.components.modern_charts import ModernSigmoidChart, ModernProbabilityTable


class ModernProbabilityView:
    """
    A modernized, gaming-themed implementation of the probability view
    with dockable panels, fluid layout, and enhanced visuals
    """
    
    def __init__(self, parent, theme_manager=None):
        """
        Initialize the modern probability view
        
        Args:
            parent: Parent widget
            theme_manager: Theme manager instance (optional)
        """
        self.parent = parent
        
        # Create theme manager if not provided
        if theme_manager is None:
            self.theme_manager = ThemeManager()
            self.owns_theme_manager = True
        else:
            self.theme_manager = theme_manager
            self.owns_theme_manager = False
        
        # Get current theme
        self.theme = self.theme_manager.get_theme()
        
        # Initialize panel manager
        self.panel_manager = PanelManager()
        
        # Set default colors
        self.player_colors = {}
        
        # Create the main container
        self._create_container()
        
        # Create probability panels
        self._create_probability_panels()
        
        # Create panel controls
        self._create_panel_controls()
    
    def _create_container(self):
        """Create the main container frame"""
        # Create main container frame
        self.container = tk.Frame(
            self.parent,
            bg=self.theme["app_bg"],
            highlightthickness=0
        )
        self.container.pack(fill=tk.BOTH, expand=True)
    
    def _create_probability_panels(self):
        """Create the probability panels"""
        # Create probability table panel
        self.table_panel = ModernFrame(
            self.container,
            title="Probability Table",
            theme_manager=self.theme_manager,
            collapsible=True,
            movable=True
        )
        self.table_panel.place(x=20, y=20, width=400, height=400)
        
        # Create probability table and ensure it fills the panel
        self.probability_table = ModernProbabilityTable(
            self.table_panel.content_frame,
            theme_manager=self.theme_manager
        )
        
        # Force immediate display of the table frame
        self.probability_table.frame.pack(fill=tk.BOTH, expand=True)
        
        # Register panel with manager
        self.panel_manager.register_panel("table", self.table_panel)
        
        # Create sigmoid chart panel
        self.chart_panel = ModernFrame(
            self.container,
            title="Probability Distribution",
            theme_manager=self.theme_manager,
            collapsible=True,
            movable=True
        )
        self.chart_panel.place(x=440, y=20, width=600, height=400)
        
        # Create canvas for sigmoid chart
        self.sigmoid_canvas = tk.Canvas(
            self.chart_panel.content_frame,
            bg=self.theme["panel_bg"],
            highlightthickness=0
        )
        self.sigmoid_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create sigmoid chart
        self.sigmoid_chart = ModernSigmoidChart(
            self.sigmoid_canvas,
            theme_manager=self.theme_manager
        )
        
        # Register panel with manager
        self.panel_manager.register_panel("chart", self.chart_panel)
    
    def _create_panel_controls(self):
        """Create controls for panel layout management"""
        # Create layout control panel
        self.control_panel = ModernFrame(
            self.container,
            title="Layout Controls",
            theme_manager=self.theme_manager,
            collapsible=True,
            movable=True,
            height=120
        )
        self.control_panel.place(x=20, y=440, width=400, height=120)
        
        # Button styling
        button_style = {
            "bg": self.theme["accent"],
            "fg": "white",
            "font": ("Segoe UI", 10, "bold"),
            "bd": 0,
            "padx": 10,
            "pady": 5,
            "width": 15,
            "height": 2,
            "activebackground": self.theme["accent_hover"]
        }
        
        # Reset layout button
        reset_btn = tk.Button(
            self.control_panel.content_frame,
            text="Reset Layout",
            command=self._reset_layout,
            **button_style
        )
        reset_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Toggle table button
        toggle_table_btn = tk.Button(
            self.control_panel.content_frame,
            text="Toggle Table",
            command=lambda: self.panel_manager.toggle_panel("table"),
            **button_style
        )
        toggle_table_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Toggle chart button
        toggle_chart_btn = tk.Button(
            self.control_panel.content_frame,
            text="Toggle Chart",
            command=lambda: self.panel_manager.toggle_panel("chart"),
            **button_style
        )
        toggle_chart_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Register panel with manager
        self.panel_manager.register_panel("controls", self.control_panel)
    
    def _reset_layout(self):
        """Reset panel layout to default positions"""
        # Reset table panel
        self.table_panel.place(x=20, y=20, width=400, height=400)
        self.panel_manager.show_panel("table")
        
        # Reset chart panel
        self.chart_panel.place(x=440, y=20, width=600, height=400)
        self.panel_manager.show_panel("chart")
        
        # Reset control panel
        self.control_panel.place(x=20, y=440, width=400, height=120)
    
    def update_probabilities(self, probs, player_mmrs, ideal_mmr, role_prefs=None):
        """
        Update the probability view with new data
        
        Args:
            probs: Dict of {player: probability}
            player_mmrs: Dict of {player: mmr}
            ideal_mmr: Ideal MMR value
            role_prefs: Dict of {player: preference} for the current role (optional)
        """
        if not probs:
            self.clear()
            return
        
        # Ensure table fills its container
        self.probability_table.frame.pack(fill=tk.BOTH, expand=True)
        
        # Update probability table
        self.probability_table.update_probabilities(
            probs, player_mmrs, ideal_mmr, role_prefs
        )
        
        # Build data list for chart [(player, mmr, diff, prob), ...]
        data_list = []
        for p, prob_val in probs.items():
            pm = player_mmrs[p]
            diff_val = abs(pm - ideal_mmr)
            data_list.append((p, pm, diff_val, prob_val))
        
        # Update sigmoid chart
        self.sigmoid_chart.draw_probability_curve(
            data_list, 
            ideal_mmr,
            self.player_colors
        )
    
    def clear(self):
        """Clear the probability view"""
        self.probability_table.clear()
        self.sigmoid_chart.clear()
    
    def set_player_colors(self, colors):
        """
        Set player colors for chart and table
        
        Args:
            colors: Dict of {player: color}
        """
        self.player_colors = colors.copy()
        
        # Update component colors
        self.probability_table.set_player_colors(colors)
        self.sigmoid_chart.set_player_colors(colors)
