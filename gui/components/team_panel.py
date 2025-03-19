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
        
        # Enable mousewheel scrolling - bind to canvas directly instead of all widgets
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
            
            # Create a drag handle at the top
            drag_handle = tk.Frame(team_card, bg=team_bg, height=5, cursor="fleur")
            drag_handle.pack(side=tk.TOP, fill=tk.X)
            
            # Set up drag and drop for reordering
            drag_handle.bind("<ButtonPress-1>", lambda e, w=team_container: self._drag_start(e, w))
            drag_handle.bind("<B1-Motion>", self._drag_motion)
            drag_handle.bind("<ButtonRelease-1>", self._drag_end)
            
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
            self.drag_data["widget"].config(relief=tk.RAISED)
            
            # Clear drag data
            self.drag_data["widget"] = None
            self.drag_data["item"] = None 