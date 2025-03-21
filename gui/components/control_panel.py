"""
Control Panel Component
Handles UI controls and action buttons
"""
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk

class ControlPanel:
    """Control panel for main actions and settings"""
    
    def __init__(self, parent, ui_config):
        """
        Initialize the control panel
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dictionary
        """
        self.parent = parent
        self.ui_config = ui_config
        self.button_handlers = {}
        self.friction_var = tk.DoubleVar(value=0.99)
        self.randomness_label_var = tk.StringVar(value="Randomness: N/A")
        self.stats_label_var = tk.StringVar(value="Pool Avg: ?, Drafted Avg: ?")
        self.banner_visible = tk.BooleanVar(value=True)
        
        # Main control frame
        self.frame = tk.Frame(parent, bg=ui_config["controls_bg_color"])
        self.frame.grid(row=0, column=0, sticky="ew", pady=ui_config["padding"])
        
        # Setup frames
        self._create_stats_label()
        self._create_control_rows()
    
    def _create_stats_label(self):
        """Create the stats label at the top"""
        self.stats_label = tk.Label(
            self.frame, 
            textvariable=self.stats_label_var,
            bg=self.ui_config["controls_bg_color"], 
            font=(self.ui_config["text_font_type"], self.ui_config["subheader_font_size"], "bold")
        )
        self.stats_label.grid(row=0, column=0, sticky="w", padx=self.ui_config["padding"], pady=2)
    
    def _create_control_rows(self):
        """Create control rows with buttons"""
        # Top controls - using frames for better layout
        self.top_controls_frame_1 = tk.Frame(self.frame, bg=self.ui_config["controls_bg_color"])
        self.top_controls_frame_1.grid(row=1, column=0, sticky="ew", pady=2)

        self.top_controls_frame_2 = tk.Frame(self.frame, bg=self.ui_config["controls_bg_color"])
        self.top_controls_frame_2.grid(row=2, column=0, sticky="ew", pady=2)
        
        # Add a new frame for the banner toggle (3rd row)
        self.top_controls_frame_3 = tk.Frame(self.frame, bg=self.ui_config["controls_bg_color"])
        self.top_controls_frame_3.grid(row=3, column=0, sticky="ew", pady=2)

        # Row 1: Team selection and role buttons
        tk.Label(
            self.top_controls_frame_1, 
            text="Select Team:", 
            bg=self.ui_config["controls_bg_color"]
        ).pack(side=tk.LEFT, padx=self.ui_config["padding"])
        
        self.team_var = tk.StringVar()
        self.team_combo = ttk.Combobox(
            self.top_controls_frame_1, 
            textvariable=self.team_var,
            font=(self.ui_config["text_font_type"], self.ui_config["button_font_size"])
        )
        self.team_combo.pack(side=tk.LEFT, padx=self.ui_config["padding"])

        # Row 2: Action buttons and settings
        self.btn_spin = ttk.Button(
            self.top_controls_frame_2, 
            text="Spin", 
            style="Normal.TButton"
        )
        self.btn_spin.pack(side=tk.LEFT, padx=self.ui_config["padding"])

        self.btn_undo = ttk.Button(
            self.top_controls_frame_2, 
            text="Undo", 
            style="Normal.TButton"
        )
        self.btn_undo.pack(side=tk.LEFT, padx=self.ui_config["padding"])

        self.btn_save = ttk.Button(
            self.top_controls_frame_2, 
            text="Save", 
            style="Normal.TButton"
        )
        self.btn_save.pack(side=tk.LEFT, padx=self.ui_config["padding"])

        self.btn_load = ttk.Button(
            self.top_controls_frame_2, 
            text="Load", 
            style="Normal.TButton"
        )
        self.btn_load.pack(side=tk.LEFT, padx=self.ui_config["padding"])

        self.randomness_label = tk.Label(
            self.top_controls_frame_2, 
            textvariable=self.randomness_label_var, 
            bg=self.ui_config["controls_bg_color"]
        )
        self.randomness_label.pack(side=tk.LEFT, padx=self.ui_config["padding"]*2)

        tk.Label(
            self.top_controls_frame_2, 
            text="WD-40:", 
            bg=self.ui_config["controls_bg_color"]
        ).pack(side=tk.LEFT, padx=self.ui_config["padding"])
        
        self.friction_spin = tk.Spinbox(
            self.top_controls_frame_2, 
            from_=0.970, 
            to=0.998, 
            increment=0.002,
            textvariable=self.friction_var, 
            width=5
        )
        self.friction_spin.pack(side=tk.LEFT, padx=self.ui_config["padding"])
        
        # Row 1: Team management buttons
        self.btn_new_team = ttk.Button(
            self.top_controls_frame_1, 
            text="New Team", 
            style="Normal.TButton"
        )
        self.btn_new_team.pack(side=tk.LEFT, padx=self.ui_config["padding"])

        self.btn_add_captain = ttk.Button(
            self.top_controls_frame_1, 
            text="Add Captain", 
            style="Normal.TButton"
        )
        self.btn_add_captain.pack(side=tk.LEFT, padx=self.ui_config["padding"])
        
        # Add label for role selection - role buttons will be added externally
        tk.Label(
            self.top_controls_frame_1, 
            text="Select Role:", 
            bg=self.ui_config["controls_bg_color"]
        ).pack(side=tk.LEFT, padx=self.ui_config["padding"])
        
        # Add banner toggle checkbox to row 3
        self.banner_toggle = ttk.Checkbutton(
            self.top_controls_frame_3, 
            text="Show Banner", 
            variable=self.banner_visible
        )
        self.banner_toggle.pack(side=tk.RIGHT, padx=self.ui_config["padding"]*2)
    
    def set_button_command(self, button_name, command):
        """
        Set command handler for a button
        
        Args:
            button_name: Name of button ('spin', 'undo', 'save', 'load', 'new_team', 'add_captain')
            command: Function to call when button is clicked
        """
        button_map = {
            'spin': self.btn_spin,
            'undo': self.btn_undo,
            'save': self.btn_save,
            'load': self.btn_load,
            'new_team': self.btn_new_team,
            'add_captain': self.btn_add_captain
        }
        
        if button_name in button_map:
            button_map[button_name].configure(command=command)
            self.button_handlers[button_name] = command
    
    def set_banner_toggle_command(self, command):
        """
        Set command for banner toggle
        
        Args:
            command: Function to call when toggle is changed
        """
        self.banner_toggle.configure(command=command)
    
    def update_team_combo(self, team_list):
        """
        Update the team combo box
        
        Args:
            team_list: List of team names
        """
        self.team_combo["values"] = team_list
    
    def get_selected_team(self):
        """
        Get the selected team
        
        Returns:
            str: Team name
        """
        return self.team_var.get()
    
    def set_selected_team(self, team_name):
        """
        Set the selected team
        
        Args:
            team_name: Team name to select
        """
        self.team_var.set(team_name)
    
    def update_stats_label(self, pool_avg, drafted_avg):
        """
        Update the stats label
        
        Args:
            pool_avg: Average MMR of player pool
            drafted_avg: Average MMR of drafted players
        """
        self.stats_label_var.set(f"Pool Avg: {int(pool_avg)}  |  Drafted Avg: {int(drafted_avg)}")
    
    def update_randomness_label(self, randomness):
        """
        Update the randomness label
        
        Args:
            randomness: Randomness value
        """
        self.randomness_label_var.set(f"Randomness: {randomness:.2f}")
    
    def get_friction_value(self):
        """
        Get the friction value
        
        Returns:
            float: Friction value
        """
        return self.friction_var.get()


class BannerPanel:
    """Banner panel for displaying an image or text banner"""
    
    def __init__(self, parent, ui_config):
        """
        Initialize the banner panel
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dictionary
        """
        self.parent = parent
        self.ui_config = ui_config
        self.banner_visible = True
        self.banner_img = None
        self._banner_label_ref = None
        
        # Create banner frame
        self.banner_frame = tk.Frame(parent, bg=ui_config["banner_bg_color"])
        
    def setup_banner(self):
        """Set up the banner image or text"""
        # Clear existing banner content
        for widget in self.banner_frame.winfo_children():
            widget.destroy()
            
        banner_path = "banner.png"
        if os.path.exists(banner_path):
            try:
                # Make sure to keep a reference to the image to prevent garbage collection
                self.banner_img = ImageTk.PhotoImage(Image.open(banner_path))
                banner_label = tk.Label(self.banner_frame, image=self.banner_img)
                banner_label.pack(fill=tk.BOTH, expand=True)
                
                # Store the label reference to prevent garbage collection
                self._banner_label_ref = banner_label
                
                print("[INFO] Banner loaded successfully")
            except Exception as e:
                print(f"[WARNING] Could not load banner: {e}")
                tk.Label(
                    self.banner_frame, 
                    text="(Banner error)", 
                    bg=self.ui_config["banner_bg_color"]
                ).pack(fill=tk.BOTH, expand=True)
        else:
            # Create a placeholder label
            placeholder_label = tk.Label(
                self.banner_frame, 
                text="Custom Draft Tool", 
                bg=self.ui_config["banner_bg_color"], 
                font=(self.ui_config["text_font_type"], self.ui_config["header_font_size"], "bold")
            )
            placeholder_label.pack(fill=tk.BOTH, expand=True, pady=self.ui_config["padding"]*2)
            print("[INFO] No banner.png found, using text placeholder")
    
    def show(self, grid_params=None):
        """
        Show the banner
        
        Args:
            grid_params: Dict with grid parameters
        """
        if grid_params:
            self.banner_frame.grid(**grid_params)
        else:
            self.banner_frame.grid(sticky="nsew")
        self.banner_frame.lift()
        self.banner_visible = True
    
    def hide(self):
        """Hide the banner"""
        self.banner_frame.grid_forget()
        self.banner_visible = False
    
    def toggle(self, grid_params=None):
        """
        Toggle banner visibility
        
        Args:
            grid_params: Grid parameters to use if showing
            
        Returns:
            bool: New visibility state
        """
        if self.banner_visible:
            self.hide()
        else:
            self.show(grid_params)
        
        return self.banner_visible 