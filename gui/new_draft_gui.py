# gui/new_draft_gui.py
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

# Import configuration
from gui.config import load_config

# Import component modules
from gui.components.team_panel import TeamPanel
from gui.components.wheel_display import WheelDisplay
from gui.components.probability_view import ProbabilityView, SigmoidChartView
from gui.components.role_panel import RolePanel, RoleListPanel
from gui.components.control_panel import ControlPanel, BannerPanel

# Import the chart classes
from gui.charts import MMRBucketChartView, RoleDistributionChartView

class DraftGUI:
    """Main Draft GUI class that integrates all components"""
    
    def __init__(self, master, config: dict, logic):
        """
        Initialize the Draft GUI
        
        Args:
            master: Tkinter root window
            config: Application configuration
            logic: Draft logic backend
        """
        self.master = master
        self.config = config
        self.logic = logic
        
        # Load UI configuration
        self.ui_config = load_config(config.get("ui_config_file"))
        
        # Apply UI configuration from main config if specified
        if "ui_settings" in config:
            for key, value in config["ui_settings"].items():
                self.ui_config[key] = value
        
        # Configure the root window
        self._configure_window()
        
        # Set up styles for widgets
        self._configure_styles()
        
        # Set up variables
        self.friction_var = tk.DoubleVar(value=0.99)
        self.banner_visible = tk.BooleanVar(value=True)
        
        # Internal variables
        self.pick_team = None
        self.pick_role = None
        
        # Set up the main layout
        self._create_main_layout()
        
        # Initialize components
        self._initialize_components()
        
        # Initialize banner visibility
        self.toggle_banner()

        # Set default role to "carry" (Pos 1)
        self.role_panel.set_role("carry")
        
        # Initial refresh of data
        self.refresh_all()
        
        # Set initial pane sizes
        self.master.update()
        left_sash_pos = int(self.ui_config["min_window_width"] * 0.25)  # 25% of min width
        center_sash_pos = int(self.ui_config["min_window_width"] * 1.5)  # 75% of min width
        self.main_paned.sashpos(0, left_sash_pos)
        self.main_paned.sashpos(1, center_sash_pos)
        
    def _configure_window(self):
        """Configure the root window"""
        self.master.title("WildCards Drafter - Built by Chraos")
        self.master.resizable(True, True)
        
        # Set minimum window size to prevent controls from disappearing
        self.master.minsize(self.ui_config["min_window_width"], self.ui_config["min_window_height"])
        
        # Make the main window expand when resized
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
    def _configure_styles(self):
        """Configure ttk styles based on UI config"""
        style = ttk.Style()
        
        # Treeview styles
        style.configure("Treeview",
                        font=(self.ui_config["text_font_type"], 
                              self.ui_config["tree_font_size"], "bold"),
                        rowheight=28)
        style.configure("Treeview.Heading",
                        font=(self.ui_config["text_font_type"], 
                              self.ui_config["tree_header_font_size"], "bold"))
        
        # Button styles
        style.configure("Normal.TButton",
                        font=(self.ui_config["text_font_type"], 
                              self.ui_config["button_font_size"], "bold"),
                        padding=0,
                        foreground=self.ui_config["button_fg_color"])
        
        # Role button styles - using specific role button settings
        style.configure("Default.RoleButton.TButton", 
                        font=(self.ui_config["role_button_font_type"], 
                              self.ui_config["role_button_font_size"], 
                              "bold"),
                        padding=self.ui_config["role_button_padding"],
                        width=self.ui_config["role_button_width"])
                        
        style.configure("Selected.RoleButton.TButton", 
                        font=(self.ui_config["role_button_font_type"], 
                              self.ui_config["role_button_font_size"], 
                              "bold"),
                        padding=self.ui_config["role_button_padding"],
                        width=self.ui_config["role_button_width"],
                        background=self.ui_config["button_select_color"])
        
    def _create_main_layout(self):
        """Create the main layout with panels"""
        # Use PanedWindow for main layout to allow resizing
        self.main_paned = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Left frame for role pools
        self.left_frame_container = tk.Frame(self.main_paned)
        self.main_paned.add(self.left_frame_container, weight=self.ui_config["left_panel_weight"])
        
        # Center pane
        self.center_frame = tk.Frame(self.main_paned, bg=self.ui_config["frame_bg_color"])
        self.main_paned.add(self.center_frame, weight=self.ui_config["center_panel_weight"])

        # Right frame
        self.right_frame = tk.Frame(self.main_paned, bd=2, relief=tk.GROOVE)
        self.main_paned.add(self.right_frame, weight=self.ui_config["right_panel_weight"])
        
        # Center frame layout - use weights for proper resizing
        self.center_frame.rowconfigure(0, weight=0)  # Top controls
        self.center_frame.rowconfigure(1, weight=1)  # Scale and probs
        self.center_frame.rowconfigure(2, weight=2)  # Charts
        self.center_frame.columnconfigure(0, weight=1)
        
        # Scale and probability frame - use PanedWindow for resizable sections
        self.scale_prob_frame = ttk.PanedWindow(self.center_frame, orient=tk.HORIZONTAL)
        self.scale_prob_frame.grid(row=1, column=0, sticky="nsew", pady=self.ui_config["padding"])

        # Use frame for scale to allow proper resizing
        self.scale_frame = tk.Frame(self.scale_prob_frame, bg=self.ui_config["frame_bg_color"])
        self.scale_prob_frame.add(self.scale_frame, weight=self.ui_config["scale_frame_weight"])
        self.scale_frame.rowconfigure(0, weight=1)
        self.scale_frame.columnconfigure(0, weight=1)
        
        # Probabilities frame
        self.prob_frame = tk.Frame(self.scale_prob_frame, bg=self.ui_config["frame_bg_color"])
        self.scale_prob_frame.add(self.prob_frame, weight=self.ui_config["prob_frame_weight"])
        self.prob_frame.rowconfigure(0, weight=0)
        self.prob_frame.rowconfigure(1, weight=1)
        self.prob_frame.columnconfigure(0, weight=1)
        
        # Bottom charts frame - make horizontal PanedWindow for left/right division
        self.bottom_charts_frame = ttk.PanedWindow(self.center_frame, orient=tk.HORIZONTAL)
        self.bottom_charts_frame.grid(row=2, column=0, sticky="nsew", pady=self.ui_config["padding"])
        
        # Left side will contain the vertical stacked charts
        self.left_charts_frame = ttk.PanedWindow(self.bottom_charts_frame, orient=tk.VERTICAL)
        self.bottom_charts_frame.add(self.left_charts_frame, weight=self.ui_config["chart_left_weight"])
        
        # Right side will contain the sigmoid chart
        self.right_chart_frame = tk.Frame(
            self.bottom_charts_frame, 
            bg=self.ui_config["frame_bg_color"], 
            bd=1, 
            relief=tk.GROOVE
        )
        self.bottom_charts_frame.add(self.right_chart_frame, weight=self.ui_config["chart_right_weight"])
        
        # MMR bucket chart frame
        self.mmr_bucket_chart_frame = tk.Frame(self.left_charts_frame, bg=self.ui_config["frame_bg_color"])
        self.left_charts_frame.add(self.mmr_bucket_chart_frame, weight=1)
        
        # Role distribution chart frame
        self.role_chart_frame = tk.Frame(self.left_charts_frame, bg=self.ui_config["frame_bg_color"])
        self.left_charts_frame.add(self.role_chart_frame, weight=1)
        
    def _initialize_components(self):
        """Initialize all the UI components"""
        # Control Panel component
        self.control_panel = ControlPanel(self.center_frame, self.ui_config)
        
        # Set up button handlers
        self.control_panel.set_button_command('spin', self.spin_clicked)
        self.control_panel.set_button_command('undo', self.undo_pick)
        self.control_panel.set_button_command('save', self.save_draft)
        self.control_panel.set_button_command('load', self.load_draft)
        self.control_panel.set_button_command('new_team', self.create_team_popup)
        self.control_panel.set_button_command('add_captain', self.add_captain_popup)
        
        # Connect friction variable
        self.friction_var = self.control_panel.friction_var
        
        # Connect banner toggle
        self.banner_visible = self.control_panel.banner_visible
        self.control_panel.set_banner_toggle_command(self.toggle_banner)
        
        # Role Panel component
        self.role_panel = RolePanel(self.center_frame, self.ui_config, self.preview_slices)
        self.role_panel.create_role_buttons(self.control_panel.top_controls_frame_1)
        
        # Role List Panel component
        self.role_list_panel = RoleListPanel(self.left_frame_container, self.ui_config)
        self.role_list_panel.build_role_lists(self.logic.players_by_role.keys())
        
        # Wheel Display component
        self.wheel_display = WheelDisplay(self.scale_frame, self.ui_config)
        
        # Probability View component
        self.probability_view = ProbabilityView(self.prob_frame, self.ui_config)
        
        # Sigmoid Chart View component
        self.sigmoid_chart = SigmoidChartView(self.right_chart_frame, self.ui_config)
        
        # Team Panel component
        self.team_panel = TeamPanel(self.right_frame, self.ui_config, self.on_team_selected)
        
        # Create chart objects
        self.mmr_chart = MMRBucketChartView(
            self.mmr_bucket_chart_frame,
            width=self.ui_config["mmr_chart_width"],
            height=self.ui_config["mmr_chart_height"],
            text_font=(self.ui_config["text_font_type"], self.ui_config["text_font_size"], "bold")
        )
        
        self.role_chart = RoleDistributionChartView(
            self.role_chart_frame,
            width=self.ui_config["role_chart_width"],
            height=self.ui_config["role_chart_height"],
            text_font=(self.ui_config["text_font_type"], self.ui_config["text_font_size"], "bold")
        )
        
        # Banner Panel component
        self.banner_panel = BannerPanel(self.center_frame, self.ui_config)
        self.banner_panel.setup_banner()
    
    def on_team_selected(self, team_id):
        """
        Handle team selection
        
        Args:
            team_id: Selected team ID
        """
        self.control_panel.set_selected_team(team_id)
        # Trigger preview to update
        self.preview_slices()
    
    def toggle_banner(self):
        """Toggle banner visibility"""
        if self.banner_visible.get():
            # Show banner as an overlay on top of the charts
            self.banner_panel.show({"row": 2, "column": 0, "sticky": "nsew"})
            print("[INFO] Banner displayed (covering charts)")
        else:
            # Hide banner to reveal charts
            self.banner_panel.hide()
            print("[INFO] Banner hidden (charts visible)")
        
        # Force update to ensure layout changes take effect
        self.master.update_idletasks()
    
    # REFRESH METHODS
    def refresh_all(self):
        """Refresh all display elements"""
        self.refresh_teams_combo()
        self.refresh_roles_listboxes()
        self.refresh_teams_display()
        self.draw_mmr_bucket_chart()
        self.draw_role_chart()

    def refresh_teams_combo(self):
        """Update teams dropdown"""
        teams = list(self.logic.get_teams_data().keys())
        self.control_panel.update_team_combo(teams)

    def refresh_roles_listboxes(self):
        """Update role listboxes with current players"""
        p_by_role = self.logic.get_players_by_role()
        self.role_list_panel.update_role_lists(p_by_role, self.logic.all_players)

    def refresh_teams_display(self):
        """Refresh the teams display in right panel"""
        all_teams = self.logic.get_teams_data()
        current_team = self.control_panel.get_selected_team()
        self.team_panel.refresh_teams_display(all_teams, current_team)
    
    # CHART METHODS
    def draw_mmr_bucket_chart(self):
        """Draw the MMR bucket chart"""
        stats = self.logic.get_mmr_bucket_stats()
        self.mmr_chart.draw(stats, self.logic.all_players, self.logic)

    def draw_role_chart(self):
        """Draw the role distribution chart"""
        stats = self.logic.get_role_distribution_stats()
        self.role_chart.draw(stats, self.logic)
    
    # PREVIEW / SPIN METHODS
    def preview_slices(self):
        """Preview probability slices for current team and role"""
        team_id = self.control_panel.get_selected_team()
        self.team_id = team_id
        role = self.role_panel.get_selected_role()
        
        if team_id not in self.logic.get_teams_data():
            return

        # Check if role is empty
        if role in self.logic.players_by_role and not self.logic.players_by_role[role]:
            fallback_role = self.ask_for_fallback_role(role)
            if not fallback_role:
                return
            actual_role = fallback_role
        else:
            actual_role = role

        # Calculate randomness
        base_random = self._get_base_randomness(team_id)
        self.control_panel.update_randomness_label(base_random)

        # Gather 'ideal_mmr' for display
        ideal_mmr = self.logic.get_ideal_mmr_for_pick(team_id, actual_role)

        # Show pool vs drafted MMR averages
        pool_avg = self.logic.get_pool_average_mmr()
        drafted_avg = self.logic.get_drafted_average_mmr()
        self.control_panel.update_stats_label(pool_avg, drafted_avg)

        # Calculate probabilities
        probs = self.logic.compute_probabilities(team_id, actual_role)
        if not probs:
            self.wheel_display.clear()
            self.sigmoid_chart.clear()
            self.probability_view.clear()
            return
            
        # Build role preferences mapping for current role
        role_prefs = {}
        for player in probs.keys():
            for role_info in self.logic.all_players[player]["roles"]:
                if role_info[0] == actual_role:
                    role_prefs[player] = role_info[1]
                    break
            if player not in role_prefs:
                role_prefs[player] = 1  # Default preference

        # Process probabilities
        player_mmrs = {p: self.logic.all_players[p]["mmr"] for p in probs.keys()}
        
        # Update probability view
        self.probability_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)
        
        # Build segments and draw wheel
        segments = self.wheel_display.build_segments(probs)
        self.wheel_display.draw_scale(segments)
        
        # Share player colors with sigmoid chart
        self.sigmoid_chart.set_player_colors(self.probability_view.get_player_colors())
        
        # Draw sigmoid chart
        self.sigmoid_chart.draw_final_probability_curve(
            self.probability_view.sigmoid_data, 
            ideal_mmr
        )

    def ask_for_fallback_role(self, original_role: str):
        """
        Ask user for fallback role when original is empty
        
        Args:
            original_role: Original role that is empty
            
        Returns:
            str: Selected fallback role or None if cancelled
        """
        popup = tk.Toplevel(self.master)
        popup.title("Empty Role Pool")
        tk.Label(popup, text=f"No players left for role: {original_role}. Select fallback:").pack(pady=self.ui_config["padding"])
        fallback_var = tk.StringVar()
        fallback_combo = ttk.Combobox(popup, textvariable=fallback_var,
                                    values=list(self.logic.players_by_role.keys()))
        fallback_combo.pack(pady=self.ui_config["padding"])

        choice = [None]
        def confirm():
            chosen = fallback_var.get()
            if chosen and chosen in self.logic.players_by_role:
                choice[0] = chosen
            popup.destroy()

        def cancel():
            popup.destroy()

        ttk.Button(popup, text="OK", command=confirm).pack(side=tk.LEFT, padx=self.ui_config["padding"]*4, pady=self.ui_config["padding"]*2)
        ttk.Button(popup, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=self.ui_config["padding"]*4, pady=self.ui_config["padding"]*2)

        popup.wait_window()
        return choice[0]

    def spin_clicked(self):
        """Handle spin button click"""
        team_id = self.control_panel.get_selected_team()
        role = self.role_panel.get_selected_role()
        
        if team_id not in self.logic.get_teams_data():
            return

        # Check if role is empty and ask for fallback
        if role in self.logic.players_by_role and not self.logic.players_by_role[role]:
            fallback_role = self.ask_for_fallback_role(role)
            if not fallback_role:
                return
            actual_role_to_spin = fallback_role
        else:
            actual_role_to_spin = role

        # Calculate and display randomness
        base_random = self._get_base_randomness(team_id)
        self.control_panel.update_randomness_label(base_random)

        # Calculate probabilities and build wheel segments
        probs = self.logic.compute_probabilities(team_id, actual_role_to_spin)
        if not probs:
            return

        segments = self.wheel_display.build_segments(probs)
        if not segments:
            return

        # Store the team and role for the pick
        self.pick_team = team_id
        # We assign them to the original role, even if we fallback
        self.pick_role = role

        # Start spin animation
        self.wheel_display.friction = self.friction_var
        success = self.wheel_display.spin(self._on_spin_complete)
        
        return success
    
    def _on_spin_complete(self, final_position):
        """
        Handle spin completion
        
        Args:
            final_position: Final pointer position (0-100)
        """
        chosen = self.logic.pick_player_from_position(
            self.pick_team, self.pick_role, final_position, 
            self.wheel_display.scale_segments
        )
        
        if chosen:
            # Get color for winner display
            player_color = self.wheel_display.player_colors.get(chosen, "red")
            
            # Get player's MMR
            player_mmr = self.logic.all_players[chosen]["mmr"]
            
            # Get formatted position (role)
            # Try to get role number mapping if available
            role_display = self.pick_role
            if hasattr(self.logic, 'role_to_number') and self.pick_role in self.logic.role_to_number:
                role_display = f"{self.pick_role} (Pos {self.logic.role_to_number[self.pick_role]})"
            
            # Display winner with all details
            self.wheel_display.display_winner(
                chosen, 
                player_color,
                team_id=self.pick_team,
                mmr=player_mmr,
                role=role_display
            )
            
        # Refresh all data
        self.refresh_all()
    
    # TEAM AND PLAYER MANAGEMENT METHODS
    def create_team_popup(self):
        """Open popup to create a new team"""
        popup = tk.Toplevel(self.master)
        popup.title("Create New Team")
        tk.Label(popup, text="Team Name:").pack(side=tk.TOP, pady=self.ui_config["padding"])
        name_var = tk.StringVar()
        entry = tk.Entry(popup, textvariable=name_var)
        entry.pack(side=tk.TOP, pady=self.ui_config["padding"])
        
        def confirm():
            tname = name_var.get().strip()
            if tname:
                self.logic.register_team(tname)
                self.refresh_all()
            popup.destroy()
            
        ttk.Button(popup, text="Confirm", style="Normal.TButton", command=confirm).pack(side=tk.TOP, pady=self.ui_config["padding"]*2)

    def add_captain_popup(self):
        """Open popup to add a captain to a team"""
        team_id = self.control_panel.get_selected_team()
        if not team_id:
            return
            
        popup = tk.Toplevel(self.master)
        popup.title(f"Add Captain to {team_id}")

        tk.Label(popup, text="Captain Name:").pack(pady=self.ui_config["padding"])
        name_var = tk.StringVar()
        e_name = tk.Entry(popup, textvariable=name_var)
        e_name.pack(pady=self.ui_config["padding"])

        tk.Label(popup, text="Captain MMR:").pack(pady=self.ui_config["padding"])
        mmr_var = tk.StringVar()
        e_mmr = tk.Entry(popup, textvariable=mmr_var)
        e_mmr.pack(pady=self.ui_config["padding"])

        def confirm():
            cname = name_var.get().strip()
            if not cname:
                popup.destroy()
                return
            try:
                cmmr = int(mmr_var.get())
            except:
                cmmr = 0
            self.logic.add_captain_to_team(team_id, cname, cmmr)
            self.refresh_all()
            popup.destroy()
            
        ttk.Button(popup, text="Confirm", command=confirm).pack(pady=self.ui_config["padding"]*2)
    
    # SAVE AND LOAD METHODS
    def undo_pick(self):
        """Undo the last player pick"""
        undone = self.logic.undo_last_pick()
        if undone:
            print(f"[UNDO] Removed {undone} from team.")
            messagebox.showinfo("Undo", f"Removed {undone} from team.")
        else:
            messagebox.showinfo("Undo", "Nothing to undo.")
        self.refresh_all()

    def save_draft(self):
        """Save the current draft state"""
        try:
            self.logic.save_state("data/draft_remaining.csv", "data/draft_teams.csv")
            print("[GUI] Saved state.")
            messagebox.showinfo("Save", "Draft state saved successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to save state: {e}")
            messagebox.showerror("Save Error", f"Failed to save: {str(e)}")

    def load_draft(self):
        """Load a saved draft state"""
        try:
            self.logic.load_state("data/draft_remaining.csv", "data/draft_teams.csv")
            print("[GUI] Loaded state.")
            messagebox.showinfo("Load", "Draft state loaded successfully.")
            self.refresh_all()
            self.wheel_display.clear()
            self.sigmoid_chart.clear()
            self.probability_view.clear()
        except Exception as e:
            print(f"[ERROR] Failed to load state: {e}")
            messagebox.showerror("Load Error", f"Failed to load: {str(e)}")
    
    # UTILITY METHODS
    def _get_base_randomness(self, team_id: str) -> float:
        """
        Get base randomness value for team
        
        Args:
            team_id: Team ID to get randomness for
            
        Returns:
            float: Randomness value
        """
        teams_data = self.logic.get_teams_data()
        if team_id not in teams_data:
            return 0.0
        n = len(teams_data[team_id]["players"])
        return self.logic.randomness_levels.get(n, 0.30) 