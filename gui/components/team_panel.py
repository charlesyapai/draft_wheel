"""
Team Panel Component
Manages the display and interaction with teams
"""
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

class TeamPanel:
    """Team panel component for displaying and interacting with teams"""
    
    def __init__(self, parent, ui_config, on_team_selected_callback):
        """
        Initialize the team panel
        
        Args:
            parent: Parent widget
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
        
        # Keep track of drag and drop state
        self.drag_data = {"x": 0, "y": 0, "item": None, "widget": None, "start_y": 0}
        
        # Use gaming theme colors to match role list panel
        self.bg_color = "#1E1E2F"  # Dark blue/purple background
        self.frame_color = "#282840"  # Slightly lighter frame background
        self.text_color = "#00FFFF"  # Cyan text for gaming theme
        self.heading_color = "#FF00FF"  # Magenta for headings
        self.selection_color = "#4040A0"  # Selection background
        self.hover_color = "#3A3A5A"  # Hover color
        
        # Configure the parent frame with the gaming theme
        parent.configure(bg=self.bg_color)
        
        # Set up teams display with scrollbars that respond to resize
        self.teams_canvas = tk.Canvas(parent, bg=self.bg_color, bd=0, highlightthickness=0)
        self.teams_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a custom-themed scrollbar
        style = ttk.Style()
        style.configure("Gaming.Vertical.TScrollbar",
                        background=self.frame_color,
                        troughcolor=self.bg_color,
                        arrowcolor=self.text_color)
        
        self.teams_scrollbar = ttk.Scrollbar(parent, orient="vertical",
                                           command=self.teams_canvas.yview,
                                           style="Gaming.Vertical.TScrollbar")
        self.teams_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.teams_canvas.configure(yscrollcommand=self.teams_scrollbar.set)
        self.teams_inner_frame = tk.Frame(self.teams_canvas, bg=self.bg_color)
        self.teams_canvas_window = self.teams_canvas.create_window((0, 0), window=self.teams_inner_frame, anchor="nw")
        
        # Bind event to resize the inner frame when canvas changes
        self.teams_inner_frame.bind("<Configure>", self._on_teams_configure)
        self.teams_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Enable mousewheel scrolling - bind to canvas directly
        self.teams_canvas.bind("<MouseWheel>", self._on_mousewheel)
        # For Linux/Unix systems that use Button-4/Button-5 for scrolling
        self.teams_canvas.bind("<Button-4>", lambda e: self.teams_canvas.yview_scroll(-1, "units"))
        self.teams_canvas.bind("<Button-5>", lambda e: self.teams_canvas.yview_scroll(1, "units"))
        
    def _on_teams_configure(self, event):
        """Handle teams container resize"""
        self.teams_canvas.configure(scrollregion=self.teams_canvas.bbox("all"))
            
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.teams_canvas.itemconfig(self.teams_canvas_window, width=event.width)
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        # Simple direct scrolling - scroll by 2 units for smoother experience
        self.teams_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
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
        
        # Find best monospace font
        font_family = "Courier"
        font_size = self.ui_config["text_font_size"]
        
        # Try to find a good monospace font
        available_fonts = tkfont.families()
        monospace_options = ["Courier", "Consolas", "Courier New", "Monaco", "DejaVu Sans Mono"]
        for font in monospace_options:
            if font in available_fonts:
                font_family = font
                break
                
        header_font = (self.ui_config["text_font_type"], self.ui_config["text_font_size"] + 1, "bold")
        player_font = (font_family, font_size, "bold")

        for tid, tinfo in teams_data.items():
            # Use stored color index or assign a new one
            if tid not in self.team_color_indices:
                self.team_color_indices[tid] = idx
            
            color_idx = self.team_color_indices[tid]
            team_bg = self._team_color(color_idx)
            
            # Create a main container for the team card with border
            team_container = tk.Frame(self.teams_inner_frame, bd=2, relief=tk.GROOVE, 
                                     highlightthickness=2, 
                                     bg=self.frame_color,
                                     highlightbackground=self.bg_color)
            team_container.pack(side=tk.TOP, fill=tk.X, anchor="nw", 
                               pady=self.ui_config["padding"], 
                               padx=self.ui_config["padding"])
            
            # Store the container reference for selection highlighting
            self.team_containers[tid] = team_container
            
            # Highlight the currently selected team if applicable
            if tid == current_team:
                team_container.config(highlightbackground=self.text_color)
                self.selected_team_container = team_container
            
            # Create a drag handle at the top
            drag_handle = tk.Frame(team_container, bg=self.frame_color, height=5, cursor="fleur")
            drag_handle.pack(side=tk.TOP, fill=tk.X)
            
            # Set up drag and drop for reordering
            drag_handle.bind("<ButtonPress-1>", lambda e, w=team_container: self._drag_start(e, w))
            drag_handle.bind("<B1-Motion>", self._drag_motion)
            drag_handle.bind("<ButtonRelease-1>", self._drag_end)
            
            # Create a header frame with team name and color picker
            header_frame = tk.Frame(team_container, bg=self.frame_color)
            header_frame.pack(side=tk.TOP, fill=tk.X, anchor="nw", padx=5, pady=2)
            
            # Team name label with gaming-themed style
            name_label = tk.Label(
                header_frame,
                text=f"TEAM: {tid.upper()}",
                bg=self.frame_color,
                fg=self.heading_color,
                font=header_font
            )
            name_label.pack(side=tk.LEFT, anchor=tk.W, padx=(0, 5))
            
            # Create a team-specific color button
            self._create_color_picker(header_frame, team_bg, tid)
            
            # Team stats with gaming theme
            stats_frame = tk.Frame(team_container, bg=self.frame_color)
            stats_frame.pack(side=tk.TOP, fill=tk.X, anchor="nw", padx=5, pady=2)
            
            avg_mmr_int = int(tinfo["average_mmr"]) if tinfo["players"] else 0
            mmr_label = tk.Label(
                stats_frame,
                text=f"Average MMR: {avg_mmr_int:,}",
                bg=self.frame_color,
                fg=self.text_color,
                font=player_font
            )
            mmr_label.pack(side=tk.TOP, anchor=tk.W)
            
            count = len(tinfo["players"])
            count_label = tk.Label(
                stats_frame,
                text=f"Players: {count}/5",
                bg=self.frame_color,
                fg=self.text_color,
                font=player_font
            )
            count_label.pack(side=tk.TOP, anchor=tk.W)
            
            # Players list frame with gaming theme
            plist_frame = tk.Frame(team_container, bg=self.frame_color)
            plist_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            # Display players with role using a consistent format
            role_to_num = {
                "carry": "POS 1",
                "mid": "POS 2",
                "offlane": "POS 3",
                "soft_support": "POS 4", 
                "hard_support": "POS 5"
            }
            
            # Create a listbox for players with gaming theme
            players_listbox = tk.Listbox(
                plist_frame,
                height=min(5, max(1, len(tinfo["players"]))),
                font=player_font,
                bg="#303050",  # Dark blue/purple background
                fg=self.text_color,  # Cyan text
                selectbackground=self.selection_color,  # Purple selection
                selectforeground="#FFFFFF",  # White text for selected items
                borderwidth=0,  # Remove border
                highlightthickness=0  # Remove highlight border
            )
            players_listbox.pack(side=tk.TOP, fill=tk.X, expand=True)
            
            # Add players to listbox
            for (pname, role) in tinfo["players"]:
                if role == "(Captain)":
                    line = f"(CAPTAIN) {pname}"
                else:
                    role_str = role_to_num.get(role, "???")
                    line = f"{role_str:<7} {pname}"
                    
                players_listbox.insert(tk.END, line)
            
            # Make entire card clickable and add visual feedback
            self._make_clickable(team_container, tid, team_container)
            
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
                container.config(highlightbackground=self.hover_color)
            e.widget.config(cursor="hand2")
        
        def on_leave(e, container=container):
            if container != self.selected_team_container:
                container.config(highlightbackground=self.bg_color)
            e.widget.config(cursor="")
        
        def on_click(e, tid=tid, container=container):
            self.on_team_selected(tid, container)
            return "break"  # Prevent propagation
        
        widget.bind("<Enter>", lambda e: on_enter(e, container))
        widget.bind("<Leave>", lambda e: on_leave(e, container))
        widget.bind("<Button-1>", lambda e: on_click(e, tid, container))
        
        for child in widget.winfo_children():
            if hasattr(child, 'is_color_button') or isinstance(child, tk.Listbox):
                continue  # Skip the color button and listbox
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
            self.selected_team_container.config(highlightbackground=self.bg_color)
        
        # Set new selection
        if container:
            container.config(highlightbackground=self.text_color)
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
            bg=self.frame_color,
            fg="#FFFFFF",
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

    def _drag_start(self, event, widget):
        """Start dragging a team container"""
        # Record initial position
        self.drag_data["widget"] = widget
        self.drag_data["start_y"] = event.y_root
        self.drag_data["item"] = widget.winfo_id()
        
        # Change appearance to indicate dragging
        widget.config(relief=tk.GROOVE)
        
    def _drag_motion(self, event):
        """Handle dragging motion"""
        if not self.drag_data["widget"]:
            return
            
        # Calculate how far we've moved
        delta_y = event.y_root - self.drag_data["start_y"]
        
        # Only move if we've dragged far enough
        if abs(delta_y) > 10:
            # Get all team containers and their positions
            containers = self.teams_inner_frame.winfo_children()
            positions = [(c, c.winfo_y()) for c in containers]
            positions.sort(key=lambda x: x[1])  # Sort by Y position
            
            # Find current widget index in sorted position list
            current_idx = next((i for i, (c, _) in enumerate(positions) if c == self.drag_data["widget"]), -1)
            
            # Calculate potential new position
            new_idx = current_idx
            if delta_y < 0 and current_idx > 0:  # Moving up
                new_idx = current_idx - 1
            elif delta_y > 0 and current_idx < len(positions) - 1:  # Moving down
                new_idx = current_idx + 1
                
            # If position changed, update layout
            if new_idx != current_idx:
                # Unpack the widget
                self.drag_data["widget"].pack_forget()
                
                # Repack at new position
                containers.remove(self.drag_data["widget"])
                containers.insert(new_idx, self.drag_data["widget"])
                
                # Repack all containers in the new order
                for c in containers:
                    c.pack_forget()
                    
                for c in containers:
                    c.pack(side=tk.TOP, fill=tk.X, anchor="nw", 
                           pady=self.ui_config["padding"], 
                           padx=self.ui_config["padding"])
                
                # Reset drag start position for continuous dragging
                self.drag_data["start_y"] = event.y_root
                
    def _drag_end(self, event):
        """End dragging operation"""
        if self.drag_data["widget"]:
            # Restore appearance
            self.drag_data["widget"].config(relief=tk.GROOVE)
            
            # Clear drag data
            self.drag_data["widget"] = None
            self.drag_data["item"] = None 