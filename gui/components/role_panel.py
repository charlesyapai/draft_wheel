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
        
        # Use gaming theme colors to match probability distribution
        self.bg_color = "#1E1E2F"  # Dark blue/purple background
        self.frame_color = "#282840"  # Slightly lighter frame background
        self.text_color = "#00FFFF"  # Cyan text for gaming theme
        self.heading_color = "#FF00FF"  # Magenta for headings
        self.selection_color = "#4040A0"  # Selection background
        
        # Configure custom scrollbar style for the theme
        style = ttk.Style()
        style.configure("Gaming.Vertical.TScrollbar", 
                      background=self.bg_color,
                      arrowcolor=self.text_color,
                      bordercolor=self.bg_color,
                      troughcolor=self.bg_color,
                      lightcolor=self.text_color,
                      darkcolor=self.heading_color)
        
        # Create a canvas for the left frame to make it scrollable
        self.role_canvas = tk.Canvas(parent, bg=self.bg_color, highlightthickness=0)
        self.role_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, 
                                         command=self.role_canvas.yview,
                                         style="Gaming.Vertical.TScrollbar")
        self.role_canvas.configure(yscrollcommand=self.role_scrollbar.set)
        
        self.role_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.role_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create container for roles
        self.roles_container = tk.Frame(self.role_canvas, bg=self.bg_color)
        self.role_canvas_window = self.role_canvas.create_window((0, 0), 
                                                              window=self.roles_container, 
                                                              anchor="nw")
        
        # Configure scrolling behavior
        self.roles_container.bind("<Configure>", self._on_frame_configure)
        self.role_canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Add mousewheel scrolling for better UX
        self.role_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Add banner frame at the bottom - will be added after role lists
        self.banner_frame = None
        
    def _on_frame_configure(self, event):
        """Update canvas scroll region when inner frame changes"""
        self.role_canvas.configure(scrollregion=self.role_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Update inner frame width when canvas resizes"""
        canvas_width = event.width
        self.role_canvas.itemconfig(self.role_canvas_window, width=canvas_width)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.role_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
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
        
        # Create role frames in a single column
        for role in role_names:
            # Create a frame for this role with gaming theme
            role_container = tk.Frame(self.roles_container, bd=2, relief=tk.GROOVE, 
                                    bg=self.frame_color, padx=3, pady=3)
            role_container.pack(side=tk.TOP, fill=tk.X, 
                             padx=self.ui_config["padding"], 
                             pady=self.ui_config["padding"],
                             expand=True)
            
            # Title label with gaming theme and more weight
            lbl = tk.Label(
                role_container, 
                text=role.upper(), 
                font=(self.ui_config["text_font_type"], self.ui_config["text_font_size"] + 1, "bold"),
                bg=self.frame_color,
                fg=self.heading_color
            )
            lbl.pack(side=tk.TOP, fill=tk.X)
            
            # Create a frame for the two-column player list
            players_frame = tk.Frame(role_container, bg=self.frame_color)
            players_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            # Create two listboxes side by side
            # Use bolder/larger font for listboxes
            player_font = (self.ui_config["text_font_type"], self.ui_config["text_font_size"], "bold")
            
            # Left column
            left_frame = tk.Frame(players_frame, bg=self.frame_color)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            left_lb = tk.Listbox(left_frame, 
                             height=self.ui_config["role_listbox_height"], 
                             font=player_font,
                             bg="#303050",  # Dark blue/purple background
                             fg=self.text_color,  # Cyan text
                             selectbackground=self.selection_color,  # Purple selection
                             selectforeground="#FFFFFF",  # White text for selected items
                             borderwidth=0,  # Remove border
                             highlightthickness=0)  # Remove highlight border
            left_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Custom styled scrollbar
            left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", 
                                        command=left_lb.yview,
                                        style="Gaming.Vertical.TScrollbar")
            left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            left_lb.configure(yscrollcommand=left_scrollbar.set)
            
            # Right column
            right_frame = tk.Frame(players_frame, bg=self.frame_color)
            right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            right_lb = tk.Listbox(right_frame, 
                              height=self.ui_config["role_listbox_height"], 
                              font=player_font,
                              bg="#303050",  # Dark blue/purple background
                              fg=self.text_color,  # Cyan text
                              selectbackground=self.selection_color,  # Purple selection
                              selectforeground="#FFFFFF",  # White text for selected items
                              borderwidth=0,  # Remove border
                              highlightthickness=0)  # Remove highlight border
            right_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Custom styled scrollbar
            right_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", 
                                         command=right_lb.yview,
                                         style="Gaming.Vertical.TScrollbar")
            right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            right_lb.configure(yscrollcommand=right_scrollbar.set)
            
            # Store both listboxes for this role
            self.role_frames[role] = (left_lb, right_lb)
            
        # Add banner frame at the bottom
        self.banner_frame = tk.Frame(self.roles_container, bg=self.bg_color, 
                                  height=100, bd=2, relief=tk.GROOVE)
        self.banner_frame.pack(side=tk.TOP, fill=tk.X, 
                           padx=self.ui_config["padding"], 
                           pady=self.ui_config["padding"])
        
        # Load the banner image
        self.set_banner_image("\\small_icon.png")
    
    def update_role_lists(self, players_by_role, player_info=None):
        """
        Update role lists with players
        
        Args:
            players_by_role: Dict of {role: [player_names]}
            player_info: Dict of player information with MMR and preferences
        """
        for role, listbox_pair in self.role_frames.items():
            left_lb, right_lb = listbox_pair
            left_lb.delete(0, tk.END)
            right_lb.delete(0, tk.END)
            
            if role in players_by_role:
                players = players_by_role[role]
                # Split the players between the two columns
                mid_point = len(players) // 2 + len(players) % 2  # Ceiling division
                
                # Fill left column
                for i, player in enumerate(players[:mid_point]):
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
                    
                    # Format string with preference as a highlight
                    left_lb.insert(tk.END, f"{pref} | {player} | {mmr}")
                
                # Fill right column
                for i, player in enumerate(players[mid_point:]):
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
                    
                    right_lb.insert(tk.END, f"{pref} | {player} | {mmr}")
                    
    def set_banner_image(self, image_path):
        """
        Set an image in the banner space
        
        Args:
            image_path: Path to the image file
        """
        if self.banner_frame:
            # Clear existing content
            for widget in self.banner_frame.winfo_children():
                widget.destroy()
                
            try:
                # Load and display the image
                from PIL import Image, ImageTk
                img = Image.open(image_path)
                
                # Calculate size to fit banner frame while maintaining aspect ratio
                frame_width = self.banner_frame.winfo_width()
                if frame_width < 10:  # If frame not yet sized, use a reasonable default
                    frame_width = 200
                    
                banner_height = 100  # Fixed height for banner
                
                # Resize image to fit
                img.thumbnail((frame_width - 10, banner_height - 10))
                
                # Convert to PhotoImage and display
                photo = ImageTk.PhotoImage(img)
                image_label = tk.Label(self.banner_frame, image=photo, bg=self.bg_color)
                image_label.image = photo  # Keep a reference to prevent garbage collection
                image_label.pack(fill=tk.BOTH, expand=True)
                
            except Exception as e:
                # If image load fails, show error message
                error_label = tk.Label(self.banner_frame, text=f"Cannot load image: {str(e)}", 
                                    bg=self.bg_color, fg="#FF0000")
                error_label.pack(pady=40)