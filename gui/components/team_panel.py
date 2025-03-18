"""
Team Panel Component
Manages the display and interaction with teams
"""
import tkinter as tk
from tkinter import ttk

class TeamPanel:
    """Team panel component for displaying and interacting with teams"""
    
    def __init__(self, parent, ui_config, on_team_selected_callback):
        """
        Initialize the team panel
        
        Args:
            parent: Parent frame/widget
            ui_config: UI configuration dict
            on_team_selected_callback: Callback when team is selected
        """
        self.parent = parent
        self.ui_config = ui_config
        self.on_team_selected_callback = on_team_selected_callback
        
        # Track the currently selected team
        self.selected_team_container = None
        self.team_containers = {}
        self.team_color_indices = {}
        
        # Set up teams display with scrollbars that respond to resize
        self.teams_canvas = tk.Canvas(parent, bg=ui_config["teams_bg_color"])
        self.teams_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.teams_scrollbar = ttk.Scrollbar(parent, orient="vertical",
                                           command=self.teams_canvas.yview)
        self.teams_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.teams_canvas.configure(yscrollcommand=self.teams_scrollbar.set)
        self.teams_inner_frame = tk.Frame(self.teams_canvas, bg=ui_config["teams_bg_color"])
        self.teams_canvas_window = self.teams_canvas.create_window((0, 0), window=self.teams_inner_frame, anchor="nw")
        
        # Bind event to resize the inner frame when canvas changes
        self.teams_inner_frame.bind("<Configure>", self._on_teams_configure)
        self.teams_canvas.bind("<Configure>", self._on_canvas_configure)
        
    def _on_teams_configure(self, event):
        """Handle teams container resize"""
        self.teams_canvas.configure(scrollregion=self.teams_canvas.bbox("all"))
            
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.teams_canvas.itemconfig(self.teams_canvas_window, width=event.width)
        
    def refresh_teams_display(self, teams_data, current_team=None):
        """
        Refresh the teams display
        
        Args:
            teams_data: Dict with team data
            current_team: Currently selected team ID
        """
        for w in self.teams_inner_frame.winfo_children():
            w.destroy()

        idx = 0
        self.selected_team_container = None

        for tid, tinfo in teams_data.items():
            # Use stored color index or assign a new one
            if tid not in self.team_color_indices:
                self.team_color_indices[tid] = idx
            
            color_idx = self.team_color_indices[tid]
            team_bg = self._team_color(color_idx)
            
            # Create a main container for the team card with border
            team_container = tk.Frame(self.teams_inner_frame, bd=2, relief=tk.RAISED, 
                                     highlightthickness=2, 
                                     highlightbackground=self.ui_config["teams_bg_color"])
            team_container.pack(side=tk.TOP, fill=tk.X, anchor="nw", 
                               pady=self.ui_config["padding"], 
                               padx=self.ui_config["padding"])
            
            # Store the container reference for selection highlighting
            self.team_containers[tid] = team_container
            
            # Highlight the currently selected team if applicable
            if tid == current_team:
                team_container.config(highlightbackground=self.ui_config["team_selected_border_color"])
                self.selected_team_container = team_container
            
            # Create the actual team card inside the container
            team_card = tk.Frame(team_container, bg=team_bg)
            team_card.pack(fill=tk.BOTH, expand=True)
            
            # Create a header frame for the team name and color picker
            header_frame = tk.Frame(team_card, bg=team_bg)
            header_frame.pack(side=tk.TOP, fill=tk.X, anchor="nw")
            
            # Team name label
            name_label = tk.Label(
                header_frame,
                text=f"Team: {tid}",
                bg=team_bg,
                font=(self.ui_config["text_font_type"], self.ui_config["header_font_size"], "bold")
            )
            name_label.pack(side=tk.LEFT, anchor=tk.W, padx=(0, 5))
            
            # Create a team-specific color button and menu
            self._create_color_picker(header_frame, team_bg, tid)
            
            # Team stats
            stats_frame = tk.Frame(team_card, bg=team_bg)
            stats_frame.pack(side=tk.TOP, fill=tk.X, anchor="nw", pady=(2, 0))
            
            avg_mmr_int = int(tinfo["average_mmr"]) if tinfo["players"] else 0
            mmr_label = tk.Label(
                stats_frame,
                text=f"Average MMR: {avg_mmr_int}",
                bg=team_bg
            )
            mmr_label.pack(side=tk.TOP, anchor=tk.W)
            
            count = len(tinfo["players"])
            count_label = tk.Label(
                stats_frame,
                text=f"Players Count: {count}",
                bg=team_bg
            )
            count_label.pack(side=tk.TOP, anchor=tk.W)
            
            # Players list
            plist_frame = tk.Frame(team_card, bg=team_bg)
            plist_frame.pack(side=tk.TOP, fill=tk.X, padx=self.ui_config["padding"]*2, pady=self.ui_config["padding"])
            
            # Display players with role
            role_to_num = {
                "carry": "Pos 1",
                "mid": "Pos 2",
                "offlane": "Pos 3",
                "soft_support": "Pos 4",
                "hard_support": "Pos 5"
            }
            
            for (pname, role) in tinfo["players"]:
                if role == "(Captain)":
                    line = f"(Captain) {pname}"
                else:
                    role_str = role_to_num.get(role, "?")
                    line = f"{role_str} {pname}"
                    
                lbl = tk.Label(
                    plist_frame,
                    text=line,
                    bg=team_bg,
                    font=(self.ui_config["text_font_type"], self.ui_config["text_font_size"], "normal")
                )
                lbl.pack(side=tk.TOP, anchor=tk.W)
            
            # Make entire card clickable and add visual feedback
            self._make_clickable(team_card, tid, team_container)
            
            # Update the index for next team
            idx += 1

    def _make_clickable(self, widget, tid, container):
        """
        Make widget and its children clickable to select a team
        
        Args:
            widget: Widget to make clickable
            tid: Team ID
            container: Team container frame for highlighting
        """
        def on_enter(e, container=container):
            if container != self.selected_team_container:
                container.config(highlightbackground=self.ui_config["team_hover_border_color"])
            e.widget.config(cursor="hand2")
        
        def on_leave(e, container=container):
            if container != self.selected_team_container:
                container.config(highlightbackground=self.ui_config["teams_bg_color"])
            e.widget.config(cursor="")
        
        def on_click(e, tid=tid, container=container):
            self.on_team_selected(tid, container)
            return "break"  # Prevent propagation
        
        widget.bind("<Enter>", lambda e: on_enter(e, container))
        widget.bind("<Leave>", lambda e: on_leave(e, container))
        widget.bind("<Button-1>", lambda e: on_click(e, tid, container))
        
        for child in widget.winfo_children():
            if hasattr(child, 'is_color_button'):
                continue  # Skip the color button
            self._make_clickable(child, tid, container)
    
    def on_team_selected(self, team_id, container=None):
        """
        Handle team selection
        
        Args:
            team_id: Selected team ID
            container: Team container widget
        """
        # Update visual selection state
        if self.selected_team_container:
            self.selected_team_container.config(highlightbackground=self.ui_config["teams_bg_color"])
        
        # Set new selection
        if container:
            container.config(highlightbackground=self.ui_config["team_selected_border_color"])
            self.selected_team_container = container
        
        # Call the callback
        if self.on_team_selected_callback:
            self.on_team_selected_callback(team_id)
    
    def _create_color_picker(self, parent_frame, bg_color, team_id):
        """
        Create color picker button and dropdown menu for a team
        
        Args:
            parent_frame: Parent widget
            bg_color: Current background color
            team_id: Team ID
        """
        # Create a small colored button to open the dropdown
        color_btn = tk.Label(
            parent_frame,
            text="🎨",
            bg=bg_color,
            font=(self.ui_config["text_font_type"], self.ui_config["text_font_size"], "normal")
        )
        color_btn.pack(side=tk.RIGHT, padx=5)
        
        # Mark this as a color button so we can identify it later
        color_btn.is_color_button = True
        
        # Create dropdown menu
        colors_menu = tk.Menu(parent_frame, tearoff=0)
        team_colors = self.ui_config["team_colors"]
        
        # Add menu items for each color
        for i, color in enumerate(team_colors):
            # Create a separate function for each color to avoid closure issues
            colors_menu.add_command(
                label=f"Color {i+1}",
                background=color,
                command=lambda idx=i, tid=team_id: self._set_team_color(tid, idx)
            )
        
        # Bind click to show menu
        def show_color_menu(event):
            try:
                colors_menu.tk_popup(event.x_root, event.y_root)
            finally:
                # Make sure to release the grab
                colors_menu.grab_release()
            return "break"  # Prevent event propagation
        
        color_btn.bind("<Button-1>", show_color_menu)
    
    def _set_team_color(self, team_id, color_index):
        """
        Set a team's color
        
        Args:
            team_id: Team ID
            color_index: Color index to use
        """
        self.team_color_indices[team_id] = color_index
        # The actual refresh is handled by the main class
        
    def _team_color(self, idx):
        """
        Get a team color by index
        
        Args:
            idx: Color index
            
        Returns:
            str: Color hex code
        """
        team_colors = self.ui_config["team_colors"]
        return team_colors[idx % len(team_colors)]
        
    def get_team_color_indices(self):
        """
        Get the team color indices mapping
        
        Returns:
            dict: Map of team IDs to color indices
        """
        return self.team_color_indices 