# gui/components/role_panel.py
"""
Role Panel Component
Handles the role selection and display
"""
import tkinter as tk
from tkinter import ttk

class RolePanel:
    """Component for displaying and selecting roles"""
    
    def __init__(self, parent, ui_config, on_role_selected=None):
        """
        Initialize the role panel
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dictionary
            on_role_selected: Callback when role is selected
        """
        self.parent = parent
        self.ui_config = ui_config
        self.on_role_selected_callback = on_role_selected
        
        # Set up role variable
        self.role_var = tk.StringVar()
        self.role_var.trace_add("write", self._on_role_selected)
        
        # Define the mapping from position labels to actual role values
        self.position_to_role = {
            "Pos 1": "carry",
            "Pos 2": "mid",
            "Pos 3": "offlane",
            "Pos 4": "soft_support",
            "Pos 5": "hard_support"
        }
        self.role_to_position = {v: k for k, v in self.position_to_role.items()}
        
        # Store role buttons
        self.role_buttons = {}
    
    def create_role_buttons(self, container):
        """
        Create the role selection buttons
        
        Args:
            container: Container widget for buttons
        """
        # Create a frame to hold the buttons side by side
        role_buttons_frame = tk.Frame(container, bg=self.ui_config["controls_bg_color"])
        role_buttons_frame.pack(side=tk.LEFT, padx=self.ui_config["padding"])
        
        # Create buttons for each position
        for pos, role in self.position_to_role.items():
            btn = ttk.Button(
                role_buttons_frame, 
                text=pos,
                style="Default.RoleButton.TButton",
                command=lambda r=role: self._set_role_and_preview(r)
            )
            btn.pack(side=tk.LEFT, padx=self.ui_config["role_button_spacing"])
            self.role_buttons[pos] = btn

    def _set_role_and_preview(self, role):
        """
        Set the selected role and trigger preview
        
        Args:
            role: Role value to set
        """
        self.role_var.set(role)
        # Call the callback after a short delay
        if self.on_role_selected_callback:
            self.parent.after(50, self.on_role_selected_callback)
    
    def _on_role_selected(self, *args):
        """Update button styling based on selected role"""
        selected_role = self.role_var.get()
        selected_pos = self.role_to_position.get(selected_role, "")
        
        # Update button styling
        for pos, btn in self.role_buttons.items():
            if pos == selected_pos:
                btn.configure(style="Selected.RoleButton.TButton")
            else:
                btn.configure(style="Default.RoleButton.TButton")
    
    def get_selected_role(self):
        """
        Get the currently selected role
        
        Returns:
            str: Selected role value
        """
        return self.role_var.get()
    
    def set_role(self, role):
        """
        Set the current role
        
        Args:
            role: Role to select
        """
        self.role_var.set(role)


class RoleListPanel:
    """Component for displaying role lists"""
    
    def __init__(self, parent, ui_config):
        """
        Initialize the role list panel
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dictionary
        """
        self.parent = parent
        self.ui_config = ui_config
        self.role_frames = {}
        
        # Create a canvas for the left frame to make it scrollable
        self.role_canvas = tk.Canvas(parent, bg=ui_config["main_bg_color"])
        self.role_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, 
                                           command=self.role_canvas.yview)
        self.role_canvas.configure(yscrollcommand=self.role_scrollbar.set)
        
        self.role_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.role_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create container for roles
        self.roles_container = tk.Frame(self.role_canvas, bg=ui_config["main_bg_color"])
        self.role_canvas_window = self.role_canvas.create_window((0, 0), 
                                                              window=self.roles_container, 
                                                              anchor="nw")
        
        # Configure scrolling behavior
        self.roles_container.bind("<Configure>", self._on_frame_configure)
        self.role_canvas.bind("<Configure>", self._on_canvas_configure)
        
    def _on_frame_configure(self, event):
        """Update canvas scroll region when inner frame changes"""
        self.role_canvas.configure(scrollregion=self.role_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Update inner frame width when canvas resizes"""
        canvas_width = event.width
        self.role_canvas.itemconfig(self.role_canvas_window, width=canvas_width)
    
    def build_role_lists(self, role_names):
        """
        Build role list frames
        
        Args:
            role_names: List of role names to display
        """
        # Clear existing frames
        for widget in self.roles_container.winfo_children():
            widget.destroy()
        
        self.role_frames = {}
        
        # Create role frames
        for role in role_names:
            # Create a frame for this role
            role_container = tk.Frame(self.roles_container, bd=2, relief=tk.RIDGE)
            role_container.pack(side=tk.TOP, fill=tk.X, 
                              padx=self.ui_config["padding"], 
                              pady=self.ui_config["padding"], 
                              expand=True)
            
            # Title label
            lbl = tk.Label(
                role_container, 
                text=role.upper(), 
                font=(self.ui_config["text_font_type"], self.ui_config["text_font_size"], "bold")
            )
            lbl.pack(side=tk.TOP, fill=tk.X)
            
            # Add scrollbar to role listboxes
            lb_frame = tk.Frame(role_container)
            lb_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            lb = tk.Listbox(lb_frame, height=self.ui_config["role_listbox_height"])
            lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            lb_scrollbar = ttk.Scrollbar(lb_frame, orient="vertical", command=lb.yview)
            lb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            lb.configure(yscrollcommand=lb_scrollbar.set)
            
            self.role_frames[role] = lb
    
    def update_role_lists(self, players_by_role, player_info=None):
        """
        Update role lists with players
        
        Args:
            players_by_role: Dict of {role: [player_names]}
            player_info: Dict of player information with MMR and preferences
        """
        for role, listbox in self.role_frames.items():
            listbox.delete(0, tk.END)
            
            if role in players_by_role:
                for player in players_by_role[role]:
                    mmr = 0
                    pref = 1  # Default preference
                    
                    # Get player info if available
                    if player_info and player in player_info:
                        mmr = player_info[player]["mmr"]
                        
                        # Check roles preference
                        if "roles" in player_info[player]:
                            for role_info in player_info[player]["roles"]:
                                if role_info[0] == role:
                                    pref = role_info[1]
                                    break
                    
                    listbox.insert(tk.END, f"{pref} | {player} | {mmr}")