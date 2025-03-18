"""
Modern Draft Controls
Provides UI components for team and role selection
"""
import tkinter as tk
from tkinter import ttk

from gui.components.modern_toolkit import ThemeManager, ModernFrame, ModernButton

class ModernDraftControls:
    """Modern UI for draft controls (team selection, role selection, etc.)"""
    
    def __init__(self, parent, theme_manager=None, role_list=None, config=None):
        """
        Initialize draft controls
        
        Args:
            parent: Parent widget
            theme_manager: Theme manager for styling
            role_list: List of available roles
            config: Application configuration
        """
        self.parent = parent
        self.theme_manager = theme_manager or ThemeManager()
        self.theme = self.theme_manager.get_theme()
        self.config = config or {}
        
        # Default role list
        self.role_list = role_list or ["carry", "mid", "offlane", "soft_support", "hard_support"]
        
        # Role mapping for display
        self.role_display = {
            "carry": "Carry (1)",
            "mid": "Mid (2)",
            "offlane": "Offlane (3)",
            "soft_support": "Soft Support (4)",
            "hard_support": "Hard Support (5)"
        }
        
        # Callbacks
        self.on_team_selected = None
        self.on_role_selected = None
        self.on_spin_clicked = None
        self.on_friction_changed = None
        
        # Variables
        self.team_var = tk.StringVar()
        self.role_var = tk.StringVar()
        
        # Get friction limits from config or use defaults
        friction_min = self.config.get("friction_min", 0.95)
        friction_max = self.config.get("friction_max", 0.999)
        friction_default = self.config.get("friction_default", 0.99)
        self.friction_var = tk.DoubleVar(value=friction_default)
        self.friction_min = friction_min
        self.friction_max = friction_max
        
        # Role statistics
        self.role_stats = {}
        
        # Create UI components
        self._create_frame()
        
        # Register for theme changes
        self.theme_manager.register_listener(self._on_theme_changed)
    
    def _create_frame(self):
        """Create the control panels"""
        # Main controls panel
        self.frame = ModernFrame(
            self.parent,
            title="Draft Controls",
            theme_manager=self.theme_manager
        )
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create content inside a scrollable frame
        self.controls_frame = tk.Frame(
            self.frame.content_frame,
            bg=self.theme["panel_bg"]
        )
        self.controls_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create role selection at the top
        self._create_role_selection()
        
        # Team selection section
        self._create_team_selection()
        
        # Spin controls
        self._create_spin_controls()
    
    def _create_team_selection(self):
        """Create team selection UI"""
        # Team panel
        team_panel = ModernFrame(
            self.controls_frame,
            title="Team Selection",
            theme_manager=self.theme_manager,
            collapsible=True
        )
        team_panel.pack(fill=tk.X, pady=5)
        
        # Team container for clickable team buttons
        self.teams_container = tk.Frame(
            team_panel.content_frame,
            bg=self.theme["panel_bg"]
        )
        self.teams_container.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # We'll add team buttons dynamically later
        
        # New team button at the bottom
        new_team_frame = tk.Frame(
            team_panel.content_frame,
            bg=self.theme["panel_bg"]
        )
        new_team_frame.pack(fill=tk.X, padx=5, pady=5)
        
        new_team_btn = ModernButton(
            new_team_frame,
            text="New Team",
            theme_manager=self.theme_manager,
            size="small"
        )
        new_team_btn.pack(side=tk.RIGHT)
    
    def _create_role_selection(self):
        """Create role selection UI"""
        # Top role selection bar
        role_bar = tk.Frame(
            self.controls_frame,
            bg=self.theme["panel_bg"]
        )
        role_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Store role buttons for later updates
        self.role_buttons = {}
        
        # Create role buttons with equal widths
        for role in self.role_list:
            display_name = self.role_display.get(role, role)
            
            # Create button container
            role_container = tk.Frame(role_bar, bg=self.theme["panel_bg"])
            role_container.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Role button (larger size)
            btn = ModernButton(
                role_container,
                text=display_name,
                theme_manager=self.theme_manager,
                size="large",
                command=lambda r=role: self._handle_role_selection(r)
            )
            btn.pack(side=tk.TOP, fill=tk.X)
            
            # MMR Label below button
            mmr_label = tk.Label(
                role_container,
                text="Avg MMR: --",
                bg=self.theme["panel_bg"],
                fg=self.theme["text_secondary"],
                font=("Segoe UI", 9)
            )
            mmr_label.pack(side=tk.TOP, fill=tk.X)
            
            # Create stats frame (core/support/mixed counts)
            stats_container = tk.Frame(role_container, bg=self.theme["panel_bg"])
            stats_container.pack(side=tk.TOP, fill=tk.X)
            
            # Create tiny labels for core/support/mixed counts
            core_label = tk.Label(
                stats_container,
                text="C:0",
                bg=self.theme["panel_bg"],
                fg=self.theme["success"],
                font=("Segoe UI", 8)
            )
            core_label.pack(side=tk.LEFT, expand=True)
            
            support_label = tk.Label(
                stats_container,
                text="S:0",
                bg=self.theme["panel_bg"],
                fg=self.theme["accent"],
                font=("Segoe UI", 8)
            )
            support_label.pack(side=tk.LEFT, expand=True)
            
            mixed_label = tk.Label(
                stats_container,
                text="M:0",
                bg=self.theme["panel_bg"],
                fg=self.theme["warning"],
                font=("Segoe UI", 8)
            )
            mixed_label.pack(side=tk.LEFT, expand=True)
            
            # Stats container below button
            prio_frame = tk.Frame(role_container, bg=self.theme["panel_bg"])
            prio_frame.pack(side=tk.TOP, fill=tk.X)
            
            # Create icons for priorities (1 and 2 only)
            prio_canvas = tk.Canvas(
                prio_frame,
                width=60,
                height=15,
                bg=self.theme["panel_bg"],
                highlightthickness=0
            )
            prio_canvas.pack(side=tk.TOP)
            
            # Store references for updating
            self.role_buttons[role] = {
                "button": btn,
                "prio_canvas": prio_canvas,
                "mmr_label": mmr_label,
                "core_label": core_label,
                "support_label": support_label,
                "mixed_label": mixed_label
            }
        
        # Set default role
        if self.role_list:
            self.role_var.set(self.role_list[0])
        
        # Create compact role stats panel
        role_stats_panel = ModernFrame(
            self.controls_frame,
            title="Role Distribution",
            theme_manager=self.theme_manager,
            collapsible=True,
            height=120
        )
        role_stats_panel.pack(fill=tk.X, pady=5)
        
        # Create stats content in a more compact format
        self.role_stats_frame = tk.Frame(
            role_stats_panel.content_frame,
            bg=self.theme["panel_bg"]
        )
        self.role_stats_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
    
    def _create_spin_controls(self):
        """Create spin controls UI"""
        # Spin panel
        spin_panel = ModernFrame(
            self.controls_frame,
            title="Wheel Controls",
            theme_manager=self.theme_manager,
            collapsible=True
        )
        spin_panel.pack(fill=tk.X, pady=5)
        
        # Spin frame
        spin_frame = tk.Frame(
            spin_panel.content_frame,
            bg=self.theme["panel_bg"]
        )
        spin_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Create spin button
        self.spin_btn = ModernButton(
            spin_frame,
            text="Spin Wheel",
            theme_manager=self.theme_manager,
            size="medium",
            command=self._handle_spin
        )
        self.spin_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Friction control
        friction_frame = tk.Frame(
            spin_panel.content_frame,
            bg=self.theme["panel_bg"]
        )
        friction_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Friction label
        friction_label = tk.Label(
            friction_frame,
            text="Lubricant:",
            bg=self.theme["panel_bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 10)
        )
        friction_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Lubricant display (higher means more lubricated)
        lubricant_val = (self.friction_var.get() - self.friction_min) / (self.friction_max - self.friction_min) * 100
        self.friction_display = tk.Label(
            friction_frame,
            text=f"{lubricant_val:.0f}%",
            width=4,
            bg=self.theme["panel_bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 10)
        )
        self.friction_display.pack(side=tk.RIGHT, padx=10)
        
        # Friction slider
        self.friction_slider = ttk.Scale(
            friction_frame,
            from_=self.friction_min,
            to=self.friction_max,
            orient=tk.HORIZONTAL,
            variable=self.friction_var,
            command=self._handle_friction_change
        )
        self.friction_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def set_team_list(self, teams):
        """
        Update the team list with clickable buttons
        
        Args:
            teams: List of team IDs
        """
        # Clear existing team buttons
        for widget in self.teams_container.winfo_children():
            widget.destroy()
        
        # Create new team buttons
        self.team_buttons = {}
        
        for i, team_id in enumerate(teams):
            team_btn = ModernButton(
                self.teams_container,
                text=f"Team {team_id}",
                theme_manager=self.theme_manager,
                size="small",
                command=lambda t=team_id: self._handle_team_selection(t)
            )
            team_btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.team_buttons[team_id] = team_btn
            
            # Set default if not already set
            if not self.team_var.get() and i == 0:
                self.team_var.set(team_id)
                # Highlight the first button
                self._highlight_selected_team()
    
    def set_role_stats(self, role, count, avg_mmr, priorities=None, core_support_stats=None):
        """
        Update the role statistics display
        
        Args:
            role: Role name
            count: Number of available players
            avg_mmr: Average MMR of players in this role
            priorities: Dict with priority counts {1: count, 2: count, 3: count}
            core_support_stats: Dict with core/support/mixed counts
        """
        # Store stats for later use
        self.role_stats[role] = {
            "count": count,
            "avg_mmr": avg_mmr,
            "priorities": priorities or {},
            "core_support": core_support_stats or {"core_only": 0, "support_only": 0, "mixed": 0}
        }
        
        # Update role button stats
        if role in self.role_buttons:
            # Update MMR label
            mmr_label = self.role_buttons[role]["mmr_label"]
            mmr_label.config(text=f"Avg MMR: {int(avg_mmr)}")
            
            # Update core/support/mixed labels if stats provided
            if core_support_stats:
                core_count = core_support_stats.get("core_only", 0)
                support_count = core_support_stats.get("support_only", 0)
                mixed_count = core_support_stats.get("mixed", 0)
                
                self.role_buttons[role]["core_label"].config(text=f"C:{core_count}")
                self.role_buttons[role]["support_label"].config(text=f"S:{support_count}")
                self.role_buttons[role]["mixed_label"].config(text=f"M:{mixed_count}")
            
            # Clear existing stats
            prio_canvas = self.role_buttons[role]["prio_canvas"]
            prio_canvas.delete("all")
            
            # Draw priorities indicators (only for first two priorities)
            if priorities:
                # Default colors
                colors = {
                    1: self.theme["success"],  # First priority (green)
                    2: self.theme["warning"]   # Second priority (orange)
                }
                
                total_width = 60
                spacing = 2
                item_width = (total_width - spacing) / 2
                y_center = 7
                
                # Just use priorities 1 and 2
                for prio in range(1, 3):
                    prio_count = priorities.get(prio, 0)
                    x_start = (prio - 1) * (item_width + spacing)
                    
                    # Draw background bar
                    prio_canvas.create_rectangle(
                        x_start, 2,
                        x_start + item_width, 12,
                        fill=colors.get(prio, "#CCCCCC"),
                        outline=""
                    )
                    
                    # Add count text
                    prio_canvas.create_text(
                        x_start + item_width/2, y_center,
                        text=str(prio_count),
                        fill="white",
                        font=("Segoe UI", 7, "bold")
                    )
            
            # Update role button state
            self._update_role_button_state(role)
    
    def set_mmr_bucket_stats(self, stats):
        """
        Update the MMR bucket statistics with a more compact display
        
        Args:
            stats: Dict of bucket statistics
        """
        # Clear existing stats
        for widget in self.role_stats_frame.winfo_children():
            widget.destroy()
            
        # Create compact stats table with two columns
        row_count = 0
        col_count = 2
        
        # Add title
        title_label = tk.Label(
            self.role_stats_frame,
            text="MMR Distribution by Role Type",
            bg=self.theme["panel_bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 9, "bold")
        )
        title_label.grid(row=row_count, column=0, columnspan=2, sticky="w", pady=(0, 5))
        row_count += 1
        
        # Headers in first column
        headers = ["MMR Range", "Core", "Support", "Mixed"]
        col_width = 8
        
        for bucket_idx, (bucket, values) in enumerate(stats.items()):
            col = bucket_idx % col_count
            row = row_count + (bucket_idx // col_count) * 5
            
            # Bucket name
            tk.Label(
                self.role_stats_frame,
                text=bucket,
                bg=self.theme["header_bg"],
                fg=self.theme["text"],
                font=("Segoe UI", 8, "bold"),
                width=col_width
            ).grid(row=row, column=col, sticky="ew", padx=1)
            
            # Core count
            core_count = values.get("core_only", 0)
            tk.Label(
                self.role_stats_frame,
                text=f"Core: {core_count}",
                bg=self.theme["panel_bg"],
                fg=self.theme["success"],
                font=("Segoe UI", 8),
                width=col_width
            ).grid(row=row+1, column=col, sticky="ew", padx=1)
            
            # Support count
            support_count = values.get("support_only", 0)
            tk.Label(
                self.role_stats_frame,
                text=f"Supp: {support_count}",
                bg=self.theme["panel_bg"],
                fg=self.theme["accent"],
                font=("Segoe UI", 8),
                width=col_width
            ).grid(row=row+2, column=col, sticky="ew", padx=1)
            
            # Mixed count
            mixed_count = values.get("mixed", 0)
            tk.Label(
                self.role_stats_frame,
                text=f"Mixed: {mixed_count}",
                bg=self.theme["panel_bg"],
                fg=self.theme["warning"],
                font=("Segoe UI", 8),
                width=col_width
            ).grid(row=row+3, column=col, sticky="ew", padx=1)
            
            # Total
            total = core_count + support_count + mixed_count
            tk.Label(
                self.role_stats_frame,
                text=f"Total: {total}",
                bg=self.theme["panel_bg"],
                fg=self.theme["text"],
                font=("Segoe UI", 8, "bold"),
                width=col_width
            ).grid(row=row+4, column=col, sticky="ew", padx=1, pady=(0, 3))
    
    def _update_role_button_state(self, role):
        """Update the visual state of a role button"""
        # Get stats for this role
        stats = self.role_stats.get(role, {})
        count = stats.get("count", 0)
        
        # Update button appearance based on player count
        button_obj = self.role_buttons[role]["button"]
        
        if count <= 0:
            button_obj.set_state("disabled")
        else:
            button_obj.set_state("normal")
        
        # Highlight selected role
        if role == self.role_var.get():
            button_obj.set_highlighted(True)
        else:
            button_obj.set_highlighted(False)
    
    def set_button_state(self, enabled=True):
        """Enable or disable the spin button"""
        if enabled:
            self.spin_btn.set_state("normal")
        else:
            self.spin_btn.set_state("disabled")
    
    def _handle_team_selection(self, team_id):
        """Handle team selection"""
        self.team_var.set(team_id)
        
        # Highlight the selected team button
        self._highlight_selected_team()
        
        # Call the callback
        if self.on_team_selected:
            self.on_team_selected(team_id)
    
    def _highlight_selected_team(self):
        """Highlight the currently selected team button"""
        selected_team = self.team_var.get()
        
        # Reset all buttons first
        for team_id, button in self.team_buttons.items():
            if team_id == selected_team:
                # Highlight this button
                button.set_highlighted(True)
            else:
                button.set_highlighted(False)
    
    def _handle_role_selection(self, role):
        """Handle role selection"""
        self.role_var.set(role)
        
        # Call the callback
        if self.on_role_selected:
            self.on_role_selected(role)
    
    def _handle_spin(self):
        """Handle spin button click"""
        if self.on_spin_clicked:
            self.on_spin_clicked()
    
    def _handle_friction_change(self, value):
        """Handle friction slider change"""
        # Get current friction value
        friction = float(value)
        
        # Calculate lubricant percentage
        lubricant_pct = (friction - self.friction_min) / (self.friction_max - self.friction_min) * 100
        
        # Update display
        self.friction_display.config(text=f"{lubricant_pct:.0f}%")
        
        # Call callback
        if self.on_friction_changed:
            self.on_friction_changed(friction)
    
    def _on_theme_changed(self, theme):
        """Handle theme changes"""
        self.theme = theme
        
        # Update panel backgrounds
        for widget in self.controls_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=theme["panel_bg"])
                
                # Update child widgets
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=theme["panel_bg"], fg=theme["text"])
                    elif isinstance(child, tk.Frame):
                        child.configure(bg=theme["panel_bg"])
                        
                        # Handle nested widgets
                        for nested in child.winfo_children():
                            if isinstance(nested, tk.Label):
                                nested.configure(bg=theme["panel_bg"], fg=theme["text"])
                            elif isinstance(nested, tk.Canvas):
                                nested.configure(bg=theme["panel_bg"])
        
        # Update role stats displays
        for role in self.role_buttons:
            if role in self.role_stats:
                self.set_role_stats(
                    role,
                    self.role_stats[role]["count"],
                    self.role_stats[role]["avg_mmr"],
                    self.role_stats[role]["priorities"],
                    self.role_stats[role]["core_support"]
                )
    
    def get_selected_team(self):
        """Get the currently selected team"""
        return self.team_var.get()
    
    def get_selected_role(self):
        """Get the currently selected role"""
        return self.role_var.get()
    
    def get_friction_value(self):
        """Get the current friction value"""
        return self.friction_var.get() 