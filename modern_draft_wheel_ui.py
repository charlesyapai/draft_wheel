"""
Modern Draft Wheel
A modernized, gaming-themed UI for the Draft Wheel
"""
import os
import sys
import tkinter as tk
from tkinter import ttk

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import core logic
from logic.draft_logic import DraftLogic
from config.loader import ConfigRetrieval

# Import modern UI components
from gui.components import (
    ThemeManager, 
    ModernFrame, 
    ModernWheel, 
    ModernProbabilityView,
    ModernDraftControls,
    ModernButton
)

class ModernDraftWheel:
    """Modern Draft Wheel application"""
    
    def __init__(self, root, config):
        """
        Initialize the modern draft wheel
        
        Args:
            root: Tk root window
            config: Application configuration
        """
        self.root = root
        self.config = config
        
        # Set window title and size
        root.title("Modern Draft Wheel")
        root.geometry("1400x800")
        
        # Create theme manager
        self.theme_manager = ThemeManager("cyber")
        self.theme = self.theme_manager.get_theme()
        
        # Create draft logic
        self.logic = DraftLogic(config)
        
        # Set up main layout
        self._setup_main_layout()
        
        # Create UI components
        self._create_header()
        self._create_wheel_panel()
        self._create_probability_panel()
        self._create_teams_panel()
        self._create_controls_panel()
        
        # Set initial theme
        self._apply_theme(self.theme)
        
        # Register for theme changes
        self.theme_manager.register_listener(self._apply_theme)
        
        # Initialize draft state
        self.refresh_all()
    
    def _setup_main_layout(self):
        """Create the main application layout"""
        # Configure root window
        self.root.configure(bg=self.theme["app_bg"])
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg=self.theme["app_bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top section (header)
        self.header_frame = tk.Frame(self.main_frame, bg=self.theme["app_bg"])
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create main content area with paned window
        self.main_paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left section (wheel and probability)
        self.left_pane = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.left_pane, weight=3)
        
        # Right section (teams and controls)
        self.right_pane = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.right_pane, weight=1)
        
        # Create panels for components
        self.wheel_frame = tk.Frame(self.left_pane, bg=self.theme["panel_bg"])
        self.left_pane.add(self.wheel_frame, weight=1)
        
        self.probability_frame = tk.Frame(self.left_pane, bg=self.theme["panel_bg"])
        self.left_pane.add(self.probability_frame, weight=1)
        
        self.teams_frame = tk.Frame(self.right_pane, bg=self.theme["panel_bg"])
        self.right_pane.add(self.teams_frame, weight=2)
        
        self.controls_frame = tk.Frame(self.right_pane, bg=self.theme["panel_bg"])
        self.right_pane.add(self.controls_frame, weight=1)
    
    def _create_header(self):
        """Create the application header"""
        # Get font configurations
        header_fonts = self.config.get("ui_settings", {}).get("fonts", {}).get("headers", {})
        header_font_family = header_fonts.get("family", "Segoe UI")
        header_font_size = header_fonts.get("size", 14)
        header_font_weight = header_fonts.get("weight", "bold")
        
        # Create header frame
        header = ModernFrame(
            self.header_frame,
            title="Draft Wheel",
            theme_manager=self.theme_manager,
            height=70,
            collapsible=False
        )
        header.pack(fill=tk.X)
        
        # Create header content
        header_content = tk.Frame(
            header.content_frame,
            bg=self.theme["panel_bg"]
        )
        header_content.pack(fill=tk.BOTH, expand=True)
        
        # Logo/title
        logo_text = tk.Label(
            header_content,
            text="DRAFT WHEEL",
            font=(header_font_family, int(header_font_size * 1.5), header_font_weight),
            bg=self.theme["panel_bg"],
            fg=self.theme["accent"]
        )
        logo_text.pack(side=tk.LEFT, padx=20)
        
        # Theme selector
        theme_frame = tk.Frame(header_content, bg=self.theme["panel_bg"])
        theme_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        tk.Label(
            theme_frame,
            text="Theme:",
            font=(header_font_family, int(header_font_size * 0.8)),
            bg=self.theme["panel_bg"],
            fg=self.theme["text"]
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Theme combobox
        self.theme_var = tk.StringVar(value=self.theme_manager.current_theme)
        self.theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=list(self.theme_manager.THEMES.keys()),
            width=10,
            state="readonly"
        )
        self.theme_combo.pack(side=tk.LEFT)
        
        # Bind theme selection event
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_selected)
        
        # Draft action buttons
        actions_frame = tk.Frame(header_content, bg=self.theme["panel_bg"])
        actions_frame.pack(side=tk.RIGHT, padx=20)
        
        # Save button
        self.save_btn = ttk.Button(
            actions_frame,
            text="Save Draft",
            command=self._on_save_clicked
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Load button
        self.load_btn = ttk.Button(
            actions_frame,
            text="Load Draft",
            command=self._on_load_clicked
        )
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # Undo button
        self.undo_btn = ttk.Button(
            actions_frame,
            text="Undo Pick",
            command=self._on_undo_clicked
        )
        self.undo_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_wheel_panel(self):
        """Create the wheel panel"""
        # Create wheel container
        wheel_container = ModernFrame(
            self.wheel_frame,
            title="Draft Wheel",
            theme_manager=self.theme_manager
        )
        wheel_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas for wheel
        self.wheel_canvas = tk.Canvas(
            wheel_container.content_frame,
            bg=self.theme["panel_bg"],
            highlightthickness=0
        )
        self.wheel_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create wheel component
        self.wheel = ModernWheel(
            self.wheel_canvas,
            theme_manager=self.theme_manager,
            friction=0.99
        )
        
        # Create result overlay frame (initially hidden)
        self.result_frame = tk.Frame(
            wheel_container.content_frame,
            bg=self.theme["panel_bg"]
        )
        
        # Create result label and widgets (will be populated when spin completes)
        self.result_title = tk.Label(
            self.result_frame,
            text="Player Assigned!",
            font=("Segoe UI", 18, "bold"),
            bg=self.theme["panel_bg"],
            fg=self.theme["accent"]
        )
        self.result_title.pack(pady=(20, 10))
        
        # Player info will be added dynamically
        self.result_player_info = tk.Frame(
            self.result_frame,
            bg=self.theme["panel_bg"]
        )
        self.result_player_info.pack(fill=tk.X, expand=True, padx=20)
        
        # Return to wheel button
        self.return_btn = ModernButton(
            self.result_frame,
            text="Continue Draft",
            theme_manager=self.theme_manager,
            size="medium",
            command=self._hide_result_panel
        )
        self.return_btn.pack(pady=(15, 20))
    
    def _create_probability_panel(self):
        """Create the probability view panel"""
        # Create probability view
        self.probability_view = ModernProbabilityView(
            self.probability_frame,
            self.theme_manager
        )
    
    def _create_teams_panel(self):
        """Create the teams panel"""
        # Create teams container
        self.teams_container = ModernFrame(
            self.teams_frame,
            title="Teams",
            theme_manager=self.theme_manager,
            collapsible=True
        )
        self.teams_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create teams scrollable area
        self.teams_canvas = tk.Canvas(
            self.teams_container.content_frame,
            bg=self.theme["panel_bg"],
            highlightthickness=0
        )
        self.teams_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        teams_scrollbar = ttk.Scrollbar(
            self.teams_container.content_frame,
            orient=tk.VERTICAL,
            command=self.teams_canvas.yview
        )
        teams_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.teams_canvas.configure(yscrollcommand=teams_scrollbar.set)
        
        # Create teams inner frame
        self.teams_inner_frame = tk.Frame(self.teams_canvas, bg=self.theme["panel_bg"])
        teams_window = self.teams_canvas.create_window(
            (0, 0),
            window=self.teams_inner_frame,
            anchor=tk.NW
        )
        
        # Update scrollregion when the inner frame changes size
        def _on_teams_configure(event):
            self.teams_canvas.configure(scrollregion=self.teams_canvas.bbox("all"))
        
        def _on_canvas_configure(event):
            self.teams_canvas.itemconfig(teams_window, width=event.width)
        
        self.teams_inner_frame.bind("<Configure>", _on_teams_configure)
        self.teams_canvas.bind("<Configure>", _on_canvas_configure)
        
        # Add "New Team" button at the top
        new_team_frame = tk.Frame(self.teams_container.content_frame, bg=self.theme["panel_bg"])
        new_team_frame.pack(fill=tk.X, pady=5, before=self.teams_canvas)
        
        new_team_btn = ModernButton(
            new_team_frame,
            text="New Team",
            theme_manager=self.theme_manager,
            size="small"
        )
        new_team_btn.pack(side=tk.RIGHT, padx=10)
    
    def _create_controls_panel(self):
        """Create the controls panel"""
        # Create draft controls
        roles = list(self.logic.players_by_role.keys())
        
        # Get friction settings from config
        friction_settings = {
            "friction_min": 0.95,
            "friction_max": 0.999,
            "friction_default": 0.99
        }
        if self.config.get("ui_settings", {}).get("wheel_friction"):
            friction_settings.update(self.config["ui_settings"]["wheel_friction"])
        
        self.draft_controls = ModernDraftControls(
            self.controls_frame,
            theme_manager=self.theme_manager,
            role_list=roles,
            config=friction_settings
        )
        
        # Connect control callbacks
        self.draft_controls.on_team_selected = self._on_team_selected
        self.draft_controls.on_role_selected = self._on_role_selected
        self.draft_controls.on_spin_clicked = self._on_spin_clicked
        self.draft_controls.on_friction_changed = self._on_friction_changed
    
    def _apply_theme(self, theme):
        """Apply theme to all components"""
        self.theme = theme
        
        # Update root window
        self.root.configure(bg=theme["app_bg"])
        self.main_frame.configure(bg=theme["app_bg"])
        self.header_frame.configure(bg=theme["app_bg"])
        
        # Update frames
        self.wheel_frame.configure(bg=theme["panel_bg"])
        self.probability_frame.configure(bg=theme["panel_bg"])
        self.teams_frame.configure(bg=theme["panel_bg"])
        self.controls_frame.configure(bg=theme["panel_bg"])
        
        # Update team display
        for widget in self.teams_inner_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=theme["panel_bg"])
                
                # Update nested widgets
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=theme["panel_bg"], fg=theme["text"])
    
    def _on_theme_selected(self, event):
        """Handle theme selection"""
        new_theme = self.theme_var.get()
        self.theme_manager.set_theme(new_theme)
    
    def _on_team_selected(self, team_id):
        """Handle team selection"""
        self.update_role_indicators(team_id)
        self._preview_probabilities()
    
    def _on_role_selected(self, role):
        """Handle role selection"""
        self._preview_probabilities()
    
    def _on_spin_clicked(self):
        """Handle spin button click"""
        # Get selected team and role
        team_id = self.draft_controls.get_selected_team()
        role = self.draft_controls.get_selected_role()
        
        if not team_id or team_id not in self.logic.get_teams_data():
            return
        
        # Check if role is available
        if role not in self.logic.players_by_role or not self.logic.players_by_role[role]:
            # TODO: Handle fallback role selection
            return
        
        # Get probabilities
        probs = self.logic.compute_probabilities(team_id, role)
        if not probs:
            return
        
        # Build wheel segments
        segs = self.wheel.build_segments(probs)
        if not segs:
            return
        
        # Start wheel spinning
        def on_spin_complete(selected_player):
            if selected_player:
                # Update draft logic with the picked player
                self.logic.pick_player_from_position(team_id, role, self.wheel.pointer_x, segs)
                
                # Show player result panel
                if selected_player in self.logic.all_players:
                    mmr = self.logic.all_players[selected_player].get("mmr", 0)
                    self._show_player_result(selected_player, team_id, role, mmr)
                
                # Refresh all data
                self.refresh_all()
        
        # Spin the wheel
        self.wheel.spin(segs, on_spin_complete)
    
    def _on_friction_changed(self, value):
        """Handle friction slider change"""
        self.wheel.set_friction(value)
    
    def _on_save_clicked(self):
        """Handle save button click"""
        self.logic.save_state("data/draft_remaining.csv", "data/draft_teams.csv")
    
    def _on_load_clicked(self):
        """Handle load button click"""
        self.logic.load_state("data/draft_remaining.csv", "data/draft_teams.csv")
        self.refresh_all()
    
    def _on_undo_clicked(self):
        """Handle undo button click"""
        self.logic.undo_last_pick()
        self.refresh_all()
    
    def _preview_probabilities(self):
        """Preview probabilities for selected team and role"""
        # Get selected team and role
        team_id = self.draft_controls.get_selected_team()
        role = self.draft_controls.get_selected_role()
        
        if not team_id or not role:
            return
        
        # Get probabilities from logic
        probs = self.logic.compute_probabilities(team_id, role)
        if not probs:
            # Clear displays
            self.wheel.clear()
            self.probability_view.clear()
            return
        
        # Build wheel segments
        segs = self.wheel.build_segments(probs)
        self.wheel.draw_wheel(segs)
        
        # Get player MMRs
        player_mmrs = {p: self.logic.all_players[p]["mmr"] for p in probs.keys()}
        
        # Get ideal MMR for this pick
        ideal_mmr = self.logic.get_ideal_mmr_for_pick(team_id, role)
        
        # Get role preferences
        role_prefs = {}
        for p in probs.keys():
            for r, prio in self.logic.all_players[p]["roles"]:
                if r == role:
                    role_prefs[p] = prio
        
        # Set player colors for wheel
        # Generate colors if not already set
        player_colors = {}
        team_colors = self.config.get("ui_settings", {}).get("team_colors", [])
        if team_colors:
            idx = 0
            for p in probs.keys():
                color = team_colors[idx % len(team_colors)]
                player_colors[p] = color
                idx += 1
        
        # Update displays
        self.wheel.set_player_colors(player_colors)
        self.probability_view.set_player_colors(player_colors)
        self.probability_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)
    
    def update_role_indicators(self, team_id):
        """Update role indicators based on selected team"""
        if not team_id:
            return
            
        # Get unfilled roles for team
        unfilled_roles = self.logic.get_unfilled_roles_for_team(team_id)
        
        # Get the MMR bucket stats for role distribution
        mmr_bucket_stats = self.logic.get_mmr_bucket_stats()
        
        # Calculate role statistics and update indicators for each role
        for role in self.logic.players_by_role.keys():
            # Get list of players for this role
            players = self.logic.players_by_role.get(role, [])
            count = len(players)
            
            # Calculate average MMR
            if count > 0:
                total_mmr = sum(self.logic.all_players[p]["mmr"] for p in players)
                avg_mmr = total_mmr / count
            else:
                avg_mmr = 0
            
            # Calculate priority counts (only consider first two priorities)
            priorities = {1: 0, 2: 0}
            for p in players:
                for r, prio in self.logic.all_players[p]["roles"]:
                    if r == role and prio <= 2:  # Only count first two priorities
                        priorities[prio] = priorities.get(prio, 0) + 1
            
            # Calculate core/support/mixed counts for this role
            core_support_stats = self._calculate_core_support_stats(role, players)
            
            # Update indicator
            self.draft_controls.set_role_stats(
                role, 
                count, 
                avg_mmr, 
                priorities, 
                core_support_stats
            )
            
            # If current role is not available, try to switch to an available one
            if role == self.draft_controls.get_selected_role() and (role not in unfilled_roles or count == 0):
                available_roles = [r for r in unfilled_roles if len(self.logic.players_by_role.get(r, [])) > 0]
                if available_roles:
                    self.draft_controls.role_var.set(available_roles[0])

        # Update MMR bucket stats
        self.draft_controls.set_mmr_bucket_stats(mmr_bucket_stats)
    
    def _calculate_core_support_stats(self, role, players):
        """
        Calculate core/support/mixed statistics for a specific role
        
        Args:
            role: Role name
            players: List of players for this role
            
        Returns:
            Dict with core_only, support_only, mixed counts
        """
        core_roles = ["carry", "mid", "offlane"]
        support_roles = ["soft_support", "hard_support"]
        
        core_only = 0
        support_only = 0
        mixed = 0
        
        for player in players:
            # Get player's roles and their priorities
            player_roles = self.logic.all_players[player]["roles"]
            
            # Count roles in their top 2 priorities
            top_roles = [r for r, prio in player_roles if prio <= 2]
            
            # Check if player has only core roles, only support roles, or mixed
            has_core = any(r in core_roles for r in top_roles)
            has_support = any(r in support_roles for r in top_roles)
            
            if has_core and has_support:
                mixed += 1
            elif has_core:
                core_only += 1
            elif has_support:
                support_only += 1
                
        return {
            "core_only": core_only,
            "support_only": support_only,
            "mixed": mixed
        }
    
    def update_teams_display(self):
        """Update teams display panel"""
        # Clear existing teams
        for widget in self.teams_inner_frame.winfo_children():
            widget.destroy()
        
        # Get team data
        teams_data = self.logic.get_teams_data()
        if not teams_data:
            return
        
        # Get team colors
        team_colors = self.config.get("ui_settings", {}).get("team_colors", [])
        
        # Create team panels
        for idx, (team_id, team_info) in enumerate(teams_data.items()):
            # Create team container
            team_frame = ModernFrame(
                self.teams_inner_frame,
                title=f"Team {team_id}",
                theme_manager=self.theme_manager,
                collapsible=True
            )
            team_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Team info
            info_frame = tk.Frame(
                team_frame.content_frame,
                bg=self.theme["panel_bg"]
            )
            info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Team color indicator
            color = team_colors[idx % len(team_colors)] if team_colors else "#CCCCCC"
            color_indicator = tk.Frame(
                info_frame,
                bg=color,
                width=10,
                height=20
            )
            color_indicator.pack(side=tk.LEFT, padx=5)
            
            # Team MMR
            avg_mmr = team_info.get("average_mmr", 0)
            mmr_label = tk.Label(
                info_frame,
                text=f"Avg MMR: {int(avg_mmr)}",
                bg=self.theme["panel_bg"],
                fg=self.theme["text"],
                font=("Segoe UI", 10)
            )
            mmr_label.pack(side=tk.LEFT, padx=10)
            
            # Players list
            players = team_info.get("players", [])
            
            for player, assigned_role in players:
                # Create player row
                player_frame = tk.Frame(
                    team_frame.content_frame,
                    bg=self.theme["panel_bg"]
                )
                player_frame.pack(fill=tk.X, padx=5, pady=2)
                
                # Player name
                player_label = tk.Label(
                    player_frame,
                    text=player,
                    bg=self.theme["panel_bg"],
                    fg=self.theme["text"],
                    font=("Segoe UI", 10),
                    anchor="w"
                )
                player_label.pack(side=tk.LEFT, padx=5)
                
                # Player role
                role_label = tk.Label(
                    player_frame,
                    text=f"Role: {assigned_role}",
                    bg=self.theme["panel_bg"],
                    fg=self.theme["text_secondary"],
                    font=("Segoe UI", 9),
                    anchor="e"
                )
                role_label.pack(side=tk.RIGHT, padx=5)
                
                # Player MMR if available
                if player in self.logic.all_players:
                    mmr = self.logic.all_players[player].get("mmr", 0)
                    mmr_label = tk.Label(
                        player_frame,
                        text=f"MMR: {mmr}",
                        bg=self.theme["panel_bg"],
                        fg=self.theme["text_secondary"],
                        font=("Segoe UI", 9)
                    )
                    mmr_label.pack(side=tk.RIGHT, padx=5)
    
    def refresh_all(self):
        """Refresh all UI components"""
        # Update team list in combobox
        team_ids = list(self.logic.get_teams_data().keys())
        self.draft_controls.set_team_list(team_ids)
        
        # Update teams display
        self.update_teams_display()
        
        # Update role indicators
        self.update_role_indicators(self.draft_controls.get_selected_team())
        
        # Preview current selection
        self._preview_probabilities()
    
    def _show_player_result(self, player, team_id, role, mmr):
        """Display the selected player result after spinning"""
        # Get font configurations
        header_fonts = self.config.get("ui_settings", {}).get("fonts", {}).get("headers", {})
        general_fonts = self.config.get("ui_settings", {}).get("fonts", {}).get("general", {})
        header_font_family = header_fonts.get("family", "Segoe UI")
        header_font_size = header_fonts.get("size", 14)
        general_font_family = general_fonts.get("family", "Segoe UI")
        general_font_size = general_fonts.get("size", 10)
        
        # Clear previous info
        for widget in self.result_player_info.winfo_children():
            widget.destroy()
        
        # Hide wheel canvas and show result frame
        self.wheel_canvas.pack_forget()
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Get player color
        team_colors = self.config.get("ui_settings", {}).get("team_colors", [])
        team_idx = list(self.logic.get_teams_data().keys()).index(team_id) if team_id in self.logic.get_teams_data() else 0
        color = team_colors[team_idx % len(team_colors)] if team_colors else "#0077FF"
        
        # Create player name header
        name_label = tk.Label(
            self.result_player_info,
            text=player,
            font=(header_font_family, int(header_font_size * 1.8), "bold"),
            bg=self.theme["panel_bg"],
            fg=color
        )
        name_label.pack(pady=(0, 10))
        
        # Create info panel
        info_frame = tk.Frame(self.result_player_info, bg=self.theme["panel_bg"])
        info_frame.pack(fill=tk.X, pady=5)
        
        # Team assignment
        team_label = tk.Label(
            info_frame,
            text=f"Team: {team_id}",
            font=(general_font_family, int(general_font_size * 1.4)),
            bg=self.theme["panel_bg"],
            fg=self.theme["text"]
        )
        team_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Role assignment
        role_display = self.draft_controls.role_display.get(role, role)
        role_label = tk.Label(
            info_frame,
            text=f"Role: {role_display}",
            font=(general_font_family, int(general_font_size * 1.4)),
            bg=self.theme["panel_bg"],
            fg=self.theme["text"]
        )
        role_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # MMR display
        mmr_label = tk.Label(
            info_frame,
            text=f"MMR: {mmr}",
            font=(general_font_family, int(general_font_size * 1.4)),
            bg=self.theme["panel_bg"],
            fg=self.theme["text"]
        )
        mmr_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Color bar
        color_bar = tk.Frame(
            self.result_player_info,
            height=4,
            bg=color
        )
        color_bar.pack(fill=tk.X, pady=10)
    
    def _hide_result_panel(self):
        """Hide the result panel and show the wheel again"""
        self.result_frame.pack_forget()
        self.wheel_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


def main():
    """Main entry point"""
    # Load config
    config_path = "data/draft_wheel_configs.yaml"
    cfg_obj = ConfigRetrieval(config_path)
    cfg = cfg_obj.get_config()
    
    # Create root window
    root = tk.Tk()
    
    # Create application
    app = ModernDraftWheel(root, cfg)
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main() 