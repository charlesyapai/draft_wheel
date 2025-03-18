import tkinter as tk
from tkinter import ttk
import random
import os
from PIL import Image, ImageTk

# import the chart classes
from gui.charts import MMRBucketChartView, RoleDistributionChartView




class DraftGUI:
    def __init__(self, master, config: dict, logic):
        self.master = master
        self.config = config
        self.logic = logic

        # Define default configurations
        self.default_ui_config = {
            # Fonts
            "text_font_type": "Arial",
            "text_font_size": 9,
            "header_font_size": 12,
            "subheader_font_size": 10,
            "button_font_size": 11,
            "tree_font_size": 11,
            "tree_header_font_size": 10,
            
            # Role Button Specific Settings
            "role_button_font_type": "Segoe UI",  # Modern clean font (alternatives: Verdana, Roboto, Helvetica Neue)
            "role_button_font_size": 9,
            "role_button_padding": 2,
            "role_button_width": 5,  # Width in characters
            "role_button_spacing": 1, # Spacing between buttons
            
            # Colors
            "main_bg_color": "#F5F5F5",
            "frame_bg_color": "#EEEEEE",
            "controls_bg_color": "#DDDDDD",
            "canvas_bg_color": "white",
            "sigmoid_bg_color": "#FFB6C1",
            "button_fg_color": "brown",
            "button_select_color": "#FFD700",
            "pointer_color": "red",
            "banner_bg_color": "#CCCCCC",
            "teams_bg_color": "#F0F0F0",
            
            # Dimensions
            "min_window_width": 900,
            "min_window_height": 600,
            "wheel_size": 700,
            "wheel_height": 200,
            "mmr_chart_width": 600,
            "mmr_chart_height": 150,
            "role_chart_width": 600,
            "role_chart_height": 180,
            "sigmoid_chart_width": 400,
            "sigmoid_chart_height": 250,
            "role_listbox_height": 8,
            
            # Layout
            "padding": 5,
            "button_padding": 5,
            "frame_padding": 10,
            "left_panel_weight": 1,
            "center_panel_weight": 3,
            "right_panel_weight": 2,
            "scale_frame_weight": 3,
            "prob_frame_weight": 2,
            "chart_left_weight": 2,
            "chart_right_weight": 1,
            
            # Team colors
            "team_colors": ["#FFD700", "#ADFF2F", "#40E0D0", "#FF69B4", "#FF7F50", "#9ACD32", "#9370DB", "#FFB6C1"]
        }
        
        # Get UI settings from config, using defaults if not specified
        self.ui_config = self.default_ui_config.copy()
        ui_settings = self.config.get("ui_settings", {})
        for key, value in ui_settings.items():
            self.ui_config[key] = value

        # Extract commonly used values for readability
        self.text_font_type = self.ui_config["text_font_type"]
        self.text_font_size = self.ui_config["text_font_size"]
        self.button_font_size = self.ui_config["button_font_size"]
        self.header_font_size = self.ui_config["header_font_size"]
        self.wheel_size = self.ui_config["wheel_size"]
        self.wheel_height = self.ui_config["wheel_height"]
        self.padding = self.ui_config["padding"]
        
        # Configure the root window to be resizable
        master.resizable(True, True)
        
        # Set minimum window size to prevent controls from disappearing
        master.minsize(self.ui_config["min_window_width"], self.ui_config["min_window_height"])
        
        # Make the main window expand when resized
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Set up styles for widgets
        self._configure_styles()

        # Set up variables
        self.friction_var = tk.DoubleVar(value=0.99)
        self.banner_visible = tk.BooleanVar(value=True)
        
        # Set up layout
        self._create_main_layout()
        self._create_center_layout()
        self._create_control_panels()
        self._create_chart_frames()
        
        # Build the role list frames
        self.build_role_list()
        
        # Initialize banner visibility
        self.toggle_banner()

        # Set default role to "carry" (Pos 1)
        self.role_var.set("carry")
        
        # Internal variables
        self.scale_segments = []
        self.pointer_x = 0.0
        self.pointer_vel = 0.0
        self.bouncing = False
        self.pick_team = None
        self.pick_role = None
        self.player_colors = {}
        self.sigmoid_data = None
        self.sigmoid_ideal_mmr = 0
        self.banner_img = None
        
        # Initial refresh of data
        self.refresh_all()
        
        # Set initial pane sizes - do this after everything is built
        self.master.update()
        left_sash_pos = int(self.ui_config["min_window_width"] * 0.25)  # 25% of min width
        center_sash_pos = int(self.ui_config["min_window_width"] * 1.25)  # 75% of min width
        self.main_paned.sashpos(0, left_sash_pos)
        self.main_paned.sashpos(1, center_sash_pos)

    def _set_role_and_preview(self, role):
        """Set the selected role and trigger preview automatically"""
        self.role_var.set(role)
        # After a short delay to let role selection update visually
        self.master.after(50, self.preview_slices)
        
    def _configure_styles(self):
        """Configure ttk styles based on UI config"""
        style = ttk.Style()
        
        # Treeview styles
        style.configure("Treeview",
                        font=(self.text_font_type, self.ui_config["tree_font_size"], "bold"),
                        rowheight=28)
        style.configure("Treeview.Heading",
                        font=(self.text_font_type, self.ui_config["tree_header_font_size"], "bold"))
        
        # Button styles
        style.configure("Normal.TButton",
                        font=(self.text_font_type, self.button_font_size, "bold"),
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
        
        # Create a canvas for the left frame to make it scrollable
        self.left_canvas = tk.Canvas(self.left_frame_container, bg=self.ui_config["main_bg_color"])
        self.left_scrollbar = ttk.Scrollbar(self.left_frame_container, orient=tk.VERTICAL, 
                                           command=self.left_canvas.yview)
        self.left_canvas.configure(yscrollcommand=self.left_scrollbar.set)
        
        self.left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Center pane
        self.center_frame = tk.Frame(self.main_paned, bg=self.ui_config["frame_bg_color"])
        self.main_paned.add(self.center_frame, weight=self.ui_config["center_panel_weight"])

        # Right frame
        self.right_frame = tk.Frame(self.main_paned, bd=2, relief=tk.GROOVE)
        self.main_paned.add(self.right_frame, weight=self.ui_config["right_panel_weight"])

        # Set up teams display with scrollbars that respond to resize
        self.teams_canvas = tk.Canvas(self.right_frame, bg=self.ui_config["teams_bg_color"])
        self.teams_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.teams_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical",
                                           command=self.teams_canvas.yview)
        self.teams_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.teams_canvas.configure(yscrollcommand=self.teams_scrollbar.set)
        self.teams_inner_frame = tk.Frame(self.teams_canvas, bg=self.ui_config["teams_bg_color"])
        self.teams_canvas_window = self.teams_canvas.create_window((0, 0), window=self.teams_inner_frame, anchor="nw")
        
        # Bind event to resize the inner frame when canvas changes
        def _on_teams_configure(event):
            self.teams_canvas.configure(scrollregion=self.teams_canvas.bbox("all"))
            
        # Bind event to resize the canvas window when teams_canvas size changes
        def _on_canvas_configure(event):
            self.teams_canvas.itemconfig(self.teams_canvas_window, width=event.width)
            
        self.teams_inner_frame.bind("<Configure>", _on_teams_configure)
        self.teams_canvas.bind("<Configure>", _on_canvas_configure)

    def _create_center_layout(self):
        """Create center panel layout"""
        # Center frame layout - use weights for proper resizing
        self.center_frame.rowconfigure(0, weight=0)  # Top controls
        self.center_frame.rowconfigure(1, weight=1)  # Scale and probs
        self.center_frame.rowconfigure(2, weight=2)  # Charts
        self.center_frame.columnconfigure(0, weight=1)

        # Top controls frame
        self.top_center_frame = tk.Frame(self.center_frame, bg=self.ui_config["controls_bg_color"])
        self.top_center_frame.grid(row=0, column=0, sticky="ew", pady=self.padding)

        # Stats label
        self.stats_label_var = tk.StringVar(value="Pool Avg: ?, Drafted Avg: ?")
        self.stats_label = tk.Label(
            self.top_center_frame, 
            textvariable=self.stats_label_var,
            bg=self.ui_config["controls_bg_color"], 
            font=(self.text_font_type, self.ui_config["subheader_font_size"], "bold")
        )
        self.stats_label.pack(side=tk.TOP, anchor=tk.W, padx=self.padding, pady=2)

        # Scale and probability frame - use PanedWindow for resizable sections
        self.scale_prob_frame = ttk.PanedWindow(self.center_frame, orient=tk.HORIZONTAL)
        self.scale_prob_frame.grid(row=1, column=0, sticky="nsew", pady=self.padding)

        # Use frame for scale to allow proper resizing
        self.scale_frame = tk.Frame(self.scale_prob_frame, bg=self.ui_config["frame_bg_color"])
        self.scale_prob_frame.add(self.scale_frame, weight=self.ui_config["scale_frame_weight"])
        self.scale_frame.rowconfigure(0, weight=1)
        self.scale_frame.columnconfigure(0, weight=1)

        self.scale_canvas = tk.Canvas(self.scale_frame, bg=self.ui_config["canvas_bg_color"])
        self.scale_canvas.pack(fill=tk.BOTH, expand=True, padx=self.ui_config["frame_padding"], pady=self.padding)
        
        # Probabilities frame
        self.prob_frame = tk.Frame(self.scale_prob_frame, bg=self.ui_config["frame_bg_color"])
        self.scale_prob_frame.add(self.prob_frame, weight=self.ui_config["prob_frame_weight"])
        self.prob_frame.rowconfigure(0, weight=0)
        self.prob_frame.rowconfigure(1, weight=1)
        self.prob_frame.columnconfigure(0, weight=1)

        tk.Label(
            self.prob_frame, 
            text="Probabilities", 
            bg=self.ui_config["frame_bg_color"],
            font=(self.text_font_type, self.ui_config["subheader_font_size"], "bold")
        ).grid(row=0, column=0, sticky="w")

        # Prob tree with scrollbar
        prob_tree_frame = tk.Frame(self.prob_frame)
        prob_tree_frame.grid(row=1, column=0, sticky="nsew")
        
        self.prob_tree = ttk.Treeview(
            prob_tree_frame, 
            columns=("player", "mmr", "diff", "prob", "pref"),
            show="headings"
        )
        self.prob_tree.heading("player", text="Player")
        self.prob_tree.heading("mmr", text="MMR")
        self.prob_tree.heading("diff", text="Diff")
        self.prob_tree.heading("prob", text="Probability")
        self.prob_tree.heading("pref", text="Pref")

        self.prob_tree.column("player", width=100)
        self.prob_tree.column("mmr", width=50)
        self.prob_tree.column("diff", width=50)
        self.prob_tree.column("prob", width=70)
        self.prob_tree.column("pref", width=40)
        
        # Add scrollbars to prob_tree
        prob_tree_yscroll = ttk.Scrollbar(prob_tree_frame, orient="vertical", command=self.prob_tree.yview)
        prob_tree_xscroll = ttk.Scrollbar(prob_tree_frame, orient="horizontal", command=self.prob_tree.xview)
        self.prob_tree.configure(yscrollcommand=prob_tree_yscroll.set, xscrollcommand=prob_tree_xscroll.set)
        
        self.prob_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prob_tree_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        prob_tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_chart_frames(self):
        """Create chart frames in bottom panel"""
        # Bottom charts frame - make horizontal PanedWindow for left/right division
        self.bottom_charts_frame = ttk.PanedWindow(self.center_frame, orient=tk.HORIZONTAL)
        self.bottom_charts_frame.grid(row=2, column=0, sticky="nsew", pady=self.padding)
        
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
        
        # Sigmoid canvas
        self.sigmoid_canvas = tk.Canvas(self.right_chart_frame, bg=self.ui_config["sigmoid_bg_color"])
        self.sigmoid_canvas.pack(fill=tk.BOTH, expand=True, padx=self.padding*2, pady=self.padding*2)
        
        # Create chart objects
        self.mmr_chart = MMRBucketChartView(
            self.mmr_bucket_chart_frame,
            width=self.ui_config["mmr_chart_width"],
            height=self.ui_config["mmr_chart_height"],
            text_font=(self.text_font_type, self.text_font_size, "bold")
        )
        self.role_chart = RoleDistributionChartView(
            self.role_chart_frame,
            width=self.ui_config["role_chart_width"],
            height=self.ui_config["role_chart_height"],
            text_font=(self.text_font_type, self.text_font_size, "bold")
        )

        # Banner frame for overlay
        self.bottom_banner_frame = tk.Frame(self.center_frame, bg=self.ui_config["banner_bg_color"])
        
        # Bind resize events
        self.scale_canvas.bind("<Configure>", self._on_scale_canvas_resize)
        self.sigmoid_canvas.bind("<Configure>", self._on_sigmoid_canvas_resize)

    def _on_scale_canvas_resize(self, event):
        """Handle scale canvas resize"""
        self.wheel_size = event.width
        self.wheel_height = event.height
        if hasattr(self, 'scale_segments') and self.scale_segments:
            self.draw_scale(self.scale_segments)
    
    def _on_sigmoid_canvas_resize(self, event):
        """Handle sigmoid canvas resize"""
        if hasattr(self, 'sigmoid_data') and self.sigmoid_data:
            self.draw_final_probability_curve(
                self.sigmoid_canvas, 
                self.sigmoid_data, 
                self.sigmoid_ideal_mmr
            )

    def _create_control_panels(self):
        """Create control panels with buttons"""
        # Top controls - using frames for better layout
        self.top_controls_frame_1 = tk.Frame(self.top_center_frame, bg=self.ui_config["controls_bg_color"])
        self.top_controls_frame_1.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.top_controls_frame_2 = tk.Frame(self.top_center_frame, bg=self.ui_config["controls_bg_color"])
        self.top_controls_frame_2.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        # Add a new frame for the banner toggle (3rd row)
        self.top_controls_frame_3 = tk.Frame(self.top_center_frame, bg=self.ui_config["controls_bg_color"])
        self.top_controls_frame_3.pack(side=tk.TOP, fill=tk.X, pady=2)

        # Add banner toggle checkbox to the new row
        self.banner_toggle = ttk.Checkbutton(
            self.top_controls_frame_3, 
            text="Show Banner", 
            variable=self.banner_visible,
            command=self.toggle_banner
        )
        self.banner_toggle.pack(side=tk.RIGHT, padx=self.padding*2)

        # Row 1: Team selection and role buttons
        tk.Label(
            self.top_controls_frame_1, 
            text="Select Team:", 
            bg=self.ui_config["controls_bg_color"]
        ).pack(side=tk.LEFT, padx=self.padding)
        
        self.team_var = tk.StringVar()
        self.team_combo = ttk.Combobox(
            self.top_controls_frame_1, 
            textvariable=self.team_var,
            font=(self.text_font_type, self.ui_config["button_font_size"])
        )
        self.team_combo.pack(side=tk.LEFT, padx=self.padding)

        self.btn_new_team = ttk.Button(
            self.top_controls_frame_1, 
            text="New Team", 
            style="Normal.TButton",
            command=self.create_team_popup
        )
        self.btn_new_team.pack(side=tk.LEFT, padx=self.padding)

        self.btn_add_captain = ttk.Button(
            self.top_controls_frame_1, 
            text="Add Captain", 
            style="Normal.TButton",
            command=self.add_captain_popup
        )
        self.btn_add_captain.pack(side=tk.LEFT, padx=self.padding)

        # Role selection with buttons
        tk.Label(
            self.top_controls_frame_1, 
            text="Select Role:", 
            bg=self.ui_config["controls_bg_color"]
        ).pack(side=tk.LEFT, padx=self.padding)
        
        self.role_var = tk.StringVar()
        self.role_var.trace_add("write", self.on_role_selected)

        # Create a frame to hold the buttons side by side
        role_buttons_frame = tk.Frame(self.top_controls_frame_1, bg=self.ui_config["controls_bg_color"])
        role_buttons_frame.pack(side=tk.LEFT, padx=self.padding)

        # Define the mapping from position labels to actual role values
        self.position_to_role = {
            "Pos 1": "carry",
            "Pos 2": "mid",
            "Pos 3": "offlane",
            "Pos 4": "soft_support",
            "Pos 5": "hard_support"
        }
        self.role_to_position = {v: k for k, v in self.position_to_role.items()}

        # Create buttons for each position - with configurable spacing
        self.role_buttons = {}
        for pos, role in self.position_to_role.items():
            # Update command to both set role AND trigger preview
            btn = ttk.Button(
                role_buttons_frame, 
                text=pos,
                style="Default.RoleButton.TButton",
                command=lambda r=role: self._set_role_and_preview(r)
            )
            btn.pack(side=tk.LEFT, padx=self.ui_config["role_button_spacing"])
            self.role_buttons[pos] = btn

        # Row 2: Action buttons and settings
        # Remove Preview button as it's now automatically triggered by role buttons
        
        self.btn_spin = ttk.Button(
            self.top_controls_frame_2, 
            text="Spin", 
            style="Normal.TButton",
            command=self.spin_clicked
        )
        self.btn_spin.pack(side=tk.LEFT, padx=self.padding)

        self.btn_undo = ttk.Button(
            self.top_controls_frame_2, 
            text="Undo", 
            style="Normal.TButton",
            command=self.undo_pick
        )
        self.btn_undo.pack(side=tk.LEFT, padx=self.padding)

        self.btn_save = ttk.Button(
            self.top_controls_frame_2, 
            text="Save", 
            style="Normal.TButton",
            command=self.save_draft
        )
        self.btn_save.pack(side=tk.LEFT, padx=self.padding)

        self.btn_load = ttk.Button(
            self.top_controls_frame_2, 
            text="Load", 
            style="Normal.TButton",
            command=self.load_draft
        )
        self.btn_load.pack(side=tk.LEFT, padx=self.padding)

        self.randomness_label_var = tk.StringVar(value="Randomness: N/A")
        self.randomness_label = tk.Label(
            self.top_controls_frame_2, 
            textvariable=self.randomness_label_var, 
            bg=self.ui_config["controls_bg_color"]
        )
        self.randomness_label.pack(side=tk.LEFT, padx=self.padding*2)

        tk.Label(
            self.top_controls_frame_2, 
            text="Lubricant:", 
            bg=self.ui_config["controls_bg_color"]
        ).pack(side=tk.LEFT, padx=self.padding)
        
        self.friction_spin = tk.Spinbox(
            self.top_controls_frame_2, 
            from_=0.980, 
            to=0.998, 
            increment=0.002,
            textvariable=self.friction_var, 
            width=5
        )
        self.friction_spin.pack(side=tk.LEFT, padx=self.padding)

    def on_role_selected(self, *args):
        """Update button styling based on selected role"""
        selected_role = self.role_var.get()
        selected_pos = self.role_to_position.get(selected_role, "")
        
        # Update button styling
        for pos, btn in self.role_buttons.items():
            if pos == selected_pos:
                btn.configure(style="Selected.RoleButton.TButton")
            else:
                btn.configure(style="Default.RoleButton.TButton")

    def setup_banner(self):
        """Set up the banner frame with the image"""
        # Clear existing banner content
        for widget in self.bottom_banner_frame.winfo_children():
            widget.destroy()
            
        banner_path = "banner.png"
        if os.path.exists(banner_path):
            try:
                # Make sure to keep a reference to the image to prevent garbage collection
                self.banner_img = ImageTk.PhotoImage(Image.open(banner_path))
                banner_label = tk.Label(self.bottom_banner_frame, image=self.banner_img)
                banner_label.pack(fill=tk.BOTH, expand=True)
                
                # Store the label reference to prevent garbage collection
                self._banner_label_ref = banner_label
                
                print("[INFO] Banner loaded successfully")
            except Exception as e:
                print(f"[WARNING] Could not load banner: {e}")
                tk.Label(
                    self.bottom_banner_frame, 
                    text="(Banner error)", 
                    bg=self.ui_config["banner_bg_color"]
                ).pack(fill=tk.BOTH, expand=True)
        else:
            # Create a placeholder label for the banner
            placeholder_label = tk.Label(
                self.bottom_banner_frame, 
                text="Custom Draft Tool", 
                bg=self.ui_config["banner_bg_color"], 
                font=(self.text_font_type, self.header_font_size, "bold")
            )
            placeholder_label.pack(fill=tk.BOTH, expand=True, pady=self.padding*2)
            print("[INFO] No banner.png found, using text placeholder")

    def toggle_banner(self):
        """Toggle banner visibility to overlay the charts when visible"""
        if self.banner_visible.get():
            # Show banner as an overlay on top of the charts
            self.setup_banner()
            
            # Make the banner cover the charts area by using the same grid cell
            self.bottom_banner_frame.grid(row=2, column=0, sticky="nsew")
            
            # Bring the banner to the front
            self.bottom_banner_frame.lift()
            print("[INFO] Banner displayed (covering charts)")
        else:
            # Hide banner to reveal charts
            self.bottom_banner_frame.grid_forget()
            print("[INFO] Banner hidden (charts visible)")
        
        # Force update to ensure layout changes take effect
        self.master.update_idletasks()

    # Build role list frames
    def build_role_list(self):
        """Create the role list frames in the left panel"""
        # Create the container frame for roles
        self.roles_container = tk.Frame(self.left_canvas, bg=self.ui_config["main_bg_color"])
        self.left_canvas_window = self.left_canvas.create_window((0, 0), window=self.roles_container, anchor="nw")
        
        # Create role frames
        self.role_frames = {}
        for r in self.logic.players_by_role:
            # Create a frame for this role
            role_container = tk.Frame(self.roles_container, bd=2, relief=tk.RIDGE)
            role_container.pack(side=tk.TOP, fill=tk.X, padx=self.padding, pady=self.padding, expand=True)
            
            # Title label
            lbl = tk.Label(
                role_container, 
                text=r.upper(), 
                font=(self.text_font_type, self.text_font_size, "bold")
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
            
            self.role_frames[r] = lb
        
        # Configure scrolling behavior
        def on_frame_configure(event):
            self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        
        def on_canvas_configure(event):
            # When canvas is resized, adjust the window width to match
            canvas_width = event.width
            self.left_canvas.itemconfig(self.left_canvas_window, width=canvas_width)
        
        self.roles_container.bind("<Configure>", on_frame_configure)
        self.left_canvas.bind("<Configure>", on_canvas_configure)

    # Draw the final probability curve
    def draw_final_probability_curve(self, canvas, data_list, ideal_mmr):
        """
        Draw a scatter plot of each player's final probability (y-axis)
        vs. actual MMR (x-axis) instead of MMR difference ratio.

        data_list: list of (playerName, mmr, diff_val, finalProb)
        ideal_mmr: float, the team's ideal MMR for this pick (displayed as reference line)
        """
        # Store the data for potential redraw on window resize
        self.sigmoid_data = data_list
        self.sigmoid_ideal_mmr = ideal_mmr

        # Clear any existing drawings
        canvas.delete("all")

        # Get the canvas dimensions
        w = int(canvas.winfo_width())
        h = int(canvas.winfo_height())

        # If the canvas is too small, skip drawing for now
        if w < 50 or h < 50:
            return

        # 1) Determine the MMR range and maximum probability
        min_mmr = float('inf')
        max_mmr = float('-inf')
        max_prob = 0.0
        
        for (_, pm, _, prob_val) in data_list:
            if pm < min_mmr:
                min_mmr = pm
            if pm > max_mmr:
                max_mmr = pm
            if prob_val > max_prob:
                max_prob = prob_val

        # Add 10% padding to MMR range
        mmr_range = max_mmr - min_mmr
        if mmr_range < 100:  # Ensure a minimum range
            mmr_range = 100
            min_mmr = max(0, min_mmr - 50)
            max_mmr = min_mmr + mmr_range
        
        min_mmr = max(0, min_mmr - mmr_range * 0.05)
        max_mmr = max_mmr + mmr_range * 0.05

        # Give a 10% buffer for probability so points don't hit the top edge
        y_max_value = max_prob * 1.1
        if y_max_value < 0.05:
            y_max_value = 0.05  # minimal range

        # 2) Define axes margin/padding
        x_axis_pad = 50  # left margin to draw Y axis
        y_axis_pad = 30  # bottom margin for X axis label
        top_pad    = 25  # top padding so labels/points aren't clipped
        right_pad  = 20  # a little right padding

        # Draw the X-axis (horizontal)
        canvas.create_line(
            x_axis_pad, h - y_axis_pad,  # start
            w - right_pad, h - y_axis_pad,  # end
            fill="black", width=2
        )

        # Draw the Y-axis (vertical)
        canvas.create_line(
            x_axis_pad, h - y_axis_pad,  # start
            x_axis_pad, top_pad,         # end
            fill="black", width=2
        )

        # Helper function to map (mmr, probability) -> canvas coordinates
        def to_canvas_coords(mmr_val, prob_val):
            """
            mmr_val in [min_mmr..max_mmr]
            prob_val in [0..y_max_value]
            Returns (x, y) in canvas space.
            """
            # X: left -> right
            x_min = x_axis_pad
            x_max = w - right_pad
            # Convert mmr to fraction of range
            rx = (mmr_val - min_mmr) / (max_mmr - min_mmr) if max_mmr > min_mmr else 0.5
            cx = x_min + (x_max - x_min) * rx

            # Y: bottom -> top (invert so bigger prob is higher)
            y_min = top_pad
            y_max = h - y_axis_pad
            ry = prob_val / y_max_value
            cy = y_max - (y_max - y_min) * ry

            return (cx, cy)

        # 3) Draw reference line for ideal MMR if it's within our range
        if min_mmr <= ideal_mmr <= max_mmr:
            ideal_x, _ = to_canvas_coords(ideal_mmr, 0)
            # Vertical dotted line
            canvas.create_line(
                ideal_x, h - y_axis_pad,
                ideal_x, top_pad,
                fill="blue", width=1, dash=(4, 4)
            )
            # Label
            canvas.create_text(
                ideal_x, top_pad - 5,
                text=f"Ideal MMR: {int(ideal_mmr)}",
                fill="blue",
                font=(self.text_font_type, 8, "bold"),
                anchor="s"
            )

        # 4) Draw scatter points for each player
        for (p, pm, _, prob_val) in data_list:
            # Map to canvas coords
            (cx, cy) = to_canvas_coords(pm, prob_val)

            # Circle radius and color
            radius = 4
            color = self.player_colors.get(p, "red")  # or pick a default

            # Draw a small circle for the player's point
            canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=color)

            # Label the point with the player's name (slightly above the circle)
            canvas.create_text(
                cx, cy - 10,
                text=p,
                fill=color,
                font=(self.text_font_type, 8, "bold")
            )

        # 5) Draw X-axis ticks (MMR values)
        num_x_ticks = 5
        mmr_step = (max_mmr - min_mmr) / num_x_ticks
        
        for i in range(num_x_ticks + 1):
            tick_mmr = min_mmr + (mmr_step * i)
            tx, ty = to_canvas_coords(tick_mmr, 0)
            # Tick mark
            canvas.create_line(tx, ty, tx, ty + 5, fill="black")
            # Label below the axis - round to nearest integer for cleaner display
            canvas.create_text(tx, ty + 15, text=f"{int(tick_mmr)}", font=(self.text_font_type, 8))

        # 6) Draw Y-axis ticks (probability)
        num_y_ticks = 5
        for i in range(num_y_ticks + 1):
            tick_prob = (y_max_value / num_y_ticks) * i
            tx, ty = to_canvas_coords(min_mmr, tick_prob)
            # Tick mark
            canvas.create_line(tx, ty, tx - 5, ty, fill="black")
            # Label to the left of the axis
            canvas.create_text(tx - 20, ty, text=f"{tick_prob:.2f}", font=(self.text_font_type, 8))

        # 7) Axis Labels
        # X-axis label
        x_label_x = (w - x_axis_pad - right_pad) / 2 + x_axis_pad
        x_label_y = h - 10
        canvas.create_text(
            x_label_x, x_label_y,
            text="Player MMR",
            font=(self.text_font_type, 9, "bold")
        )

        # Y-axis label (vertical)
        y_label_x = 15
        y_label_y = (h - y_axis_pad - top_pad) / 2 + top_pad
        canvas.create_text(
            y_label_x, y_label_y,
            text="Final Probability",
            font=(self.text_font_type, 9, "bold"),
            angle=90
        )
    def draw_scale(self, segs):
        """Draw the scale with player segments"""
        self.scale_canvas.delete("all")
        w = self.wheel_size
        h = self.wheel_height
        self.scale_canvas.create_rectangle(0, 0, w, h, outline="black", width=2, fill="white")
        for idx, (p, start, end) in enumerate(segs):
            x1 = (start/100) * w
            x2 = (end/100) * w
            color = self._team_color(idx)
            self.player_colors[p] = color
            self.scale_canvas.create_rectangle(x1, 0, x2, h, fill=color, outline="")

            cx = (x1+x2)/2
            cy = h/2
            if (x2-x1) > 20:  # Only show text if segment is wide enough
                self.scale_canvas.create_text(cx, cy,
                                          text=p,
                                          font=(self.text_font_type, self.text_font_size, "bold"),
                                          fill="black",
                                          angle=90)

    # REFRESH
    def refresh_all(self):
        """Refresh all display elements"""
        self.refresh_teams_combo()
        self.refresh_roles_listboxes()
        self.refresh_teams_display()
        self.draw_mmr_bucket_chart()
        self.draw_role_chart()

    def refresh_teams_combo(self):
        """Update teams dropdown"""
        teams=list(self.logic.get_teams_data().keys())
        self.team_combo["values"]=teams

    def refresh_roles_listboxes(self):
        """Update role listboxes with current players"""
        p_by_role=self.logic.get_players_by_role()
        for r, lb in self.role_frames.items():
            lb.delete(0, tk.END)
            if r in p_by_role:
                for player in p_by_role[r]:
                    mmr=self.logic.all_players[player]["mmr"]
                    
                    # Find preference for this role
                    pref = 1  # Default preference
                    for role_info in self.logic.all_players[player]["roles"]:
                        if role_info[0] == r:
                            pref = role_info[1]
                            break
                            
                    lb.insert(tk.END, f"{pref} | {player} | {mmr}")

    def refresh_teams_display(self):
        """Refresh the teams display in right panel"""
        for w in self.teams_inner_frame.winfo_children():
            w.destroy()

        all_teams= self.logic.get_teams_data()
        idx=0
        role_to_num=self.logic.role_to_number

        for tid, tinfo in all_teams.items():
            team_bg= self._team_color(idx)
            team_card= tk.Frame(self.teams_inner_frame, bd=2, relief=tk.RAISED, bg=team_bg)
            # let user click => sets that team
            team_card.bind("<Button-1>", lambda e,team_id=tid: self.on_team_box_clicked(team_id))

            # If you want 2 columns => use .grid(...) instead of .pack(...)
            team_card.pack(side=tk.TOP, fill=tk.X, anchor="nw", pady=self.padding, padx=self.padding)

            tk.Label(
                team_card, 
                text=f"Team: {tid}",
                bg=team_bg, 
                font=(self.text_font_type, self.header_font_size, "bold")
            ).pack(side=tk.TOP, anchor=tk.W)

            avg_mmr_int=int(tinfo["average_mmr"]) if tinfo["players"] else 0
            tk.Label(
                team_card, 
                text=f"Average MMR: {avg_mmr_int}",
                bg=team_bg
            ).pack(side=tk.TOP, anchor=tk.W)

            count= len(tinfo["players"])
            tk.Label(
                team_card, 
                text=f"Players Count: {count}",
                bg=team_bg
            ).pack(side=tk.TOP, anchor=tk.W)

            plist_frame= tk.Frame(team_card, bg=team_bg)
            plist_frame.pack(side=tk.TOP, fill=tk.X, padx=self.padding*2, pady=self.padding)

            for (pname, role) in tinfo["players"]:
                if role=="(Captain)":
                    line=f"(Captain) {pname}"
                else:
                    role_str= role_to_num.get(role,"?")
                    line=f"{role_str} {pname}"
                lbl=tk.Label(
                    plist_frame, 
                    text=line, 
                    bg=team_bg,
                    font=(self.text_font_type, self.text_font_size, "normal")
                )
                lbl.pack(side=tk.TOP, anchor=tk.W)

            idx+=1

    def on_team_box_clicked(self, team_id:str):
        """Handle team selection from team box click"""
        self.team_var.set(team_id)

    # CHARTS
    def draw_mmr_bucket_chart(self):
        """Draw the MMR bucket chart"""
        stats = self.logic.get_mmr_bucket_stats()
        self.mmr_chart.draw(stats, self.logic.all_players, self.logic)

    def draw_role_chart(self):
        """Draw the role distribution chart"""
        stats = self.logic.get_role_distribution_stats()
        self.role_chart.draw(stats, self.logic)

    # PREVIEW / SPIN
    def preview_slices(self):
        """Preview probability slices for current team and role"""
        team_id=self.team_var.get()
        self.team_id = team_id
        role=self.role_var.get()
        if team_id not in self.logic.get_teams_data():
            return

        # If empty
        if role in self.logic.players_by_role and not self.logic.players_by_role[role]:
            fallback_role=self.ask_for_fallback_role(role)
            if not fallback_role:
                return
            actual_role= fallback_role
        else:
            actual_role= role

        base_random= self._get_base_randomness(team_id)
        self.randomness_label_var.set(f"Randomness: {base_random:.2f}")

        # Gather 'ideal_mmr' for display
        ideal_mmr = self.logic.get_ideal_mmr_for_pick(team_id, actual_role)

        # Show pool vs drafted MMR averages
        pool_avg = self.logic.get_pool_average_mmr()
        drafted_avg = self.logic.get_drafted_average_mmr()
        self.stats_label_var.set(f"Pool Avg: {int(pool_avg)}  |  Drafted Avg: {int(drafted_avg)}")

        # Calculate probabilities
        probs = self.logic.compute_probabilities(team_id, actual_role)
        if not probs:
            self.scale_canvas.delete("all")
            self.sigmoid_canvas.delete("all")  # clear the sigmoid canvas as well
            for item in self.prob_tree.get_children():
                self.prob_tree.delete(item)
            return

        # Clear old items
        for item in self.prob_tree.get_children():
            self.prob_tree.delete(item)
        self.player_colors.clear()
        self.scale_segments = []

        # 1) Build data (player, mmr, diff, prob) and sort by MMR
        data_list = []
        for p, prob_val in probs.items():
            pm = self.logic.all_players[p]["mmr"]
            diff_val = abs(pm - ideal_mmr)
            data_list.append((p, pm, diff_val, prob_val))
        # Sort by MMR ascending (change to descending if you prefer)
        data_list.sort(key=lambda x: x[1])

        # 2) Populate the Treeview in sorted order
        idx = 0
        total_prob = sum(x[3] for x in data_list)
        current_angle = 0.0  # used for the scale drawing
        for (p, pm, diff_val, prob_val) in data_list:
            prob_pct = prob_val * 100.0
            prob_str = f"{prob_pct:.1f}%"

            # color
            color = self._team_color(idx)
            self.player_colors[p] = color

            # Insert row into tree
            style_name = f"ColorStyle_{idx}"
            s = ttk.Style()
            s.configure(style_name, background=color,
                        font=(self.text_font_type, self.text_font_size, "bold"))
                        
            # Get preference for this role
            pref = 1  # Default preference
            for role_info in self.logic.all_players[p]["roles"]:
                if role_info[0] == actual_role:
                    pref = role_info[1]
                    break

            row_id = self.prob_tree.insert("", "end", values=(p, int(pm), int(diff_val), prob_str, pref))
            self.prob_tree.item(row_id, tags=(style_name,))
            self.prob_tree.tag_configure(style_name, background=color)

            idx += 1

        # 3) Build scale segments (like before) for the main wheel canvas
        segs = self.build_segments(probs)
        self.scale_segments = segs
        self.draw_scale(segs)

        # 4) Draw the sigmoid/ratio curve on self.sigmoid_canvas
        self.draw_final_probability_curve(self.sigmoid_canvas, data_list, ideal_mmr)

    def ask_for_fallback_role(self, original_role:str):
        """Ask user for fallback role when original is empty"""
        popup=tk.Toplevel(self.master)
        popup.title("Empty Role Pool")
        tk.Label(popup, text=f"No players left for role: {original_role}. Select fallback:").pack(pady=self.padding)
        fallback_var=tk.StringVar()
        fallback_combo=ttk.Combobox(popup, textvariable=fallback_var,
                                    values=list(self.logic.players_by_role.keys()))
        fallback_combo.pack(pady=self.padding)

        choice=[None]
        def confirm():
            chosen=fallback_var.get()
            if chosen and chosen in self.logic.players_by_role:
                choice[0]= chosen
            popup.destroy()

        def cancel():
            popup.destroy()

        ttk.Button(popup, text="OK", command=confirm).pack(side=tk.LEFT, padx=self.padding*4, pady=self.padding*2)
        ttk.Button(popup, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=self.padding*4, pady=self.padding*2)

        popup.wait_window()
        return choice[0]

    def spin_clicked(self):
        """Handle spin button click"""
        team_id=self.team_var.get()
        role=self.role_var.get()
        if team_id not in self.logic.get_teams_data():
            return

        if role in self.logic.players_by_role and not self.logic.players_by_role[role]:
            fallback_role=self.ask_for_fallback_role(role)
            if not fallback_role:
                return
            actual_role_to_spin=fallback_role
        else:
            actual_role_to_spin= role

        base_random= self._get_base_randomness(team_id)
        self.randomness_label_var.set(f"Randomness: {base_random:.2f}")

        probs= self.logic.compute_probabilities(team_id, actual_role_to_spin)
        if not probs:
            return

        segs= self.build_segments(probs)
        if not segs:
            return

        self.scale_segments=segs
        self.pick_team= team_id
        # we assign them to the original role, even if we fallback
        self.pick_role= role

        self.pointer_x= random.uniform(0,100)
        self.pointer_vel= random.uniform(-5,5)
        if abs(self.pointer_vel)<1:
            self.pointer_vel=5 if self.pointer_vel>=0 else -5

        self.bouncing=True
        self.update_bounce()

    def update_bounce(self):
        """Update pointer animation during spin"""
        if not self.bouncing:
            return
        friction=self.friction_var.get()
        self.pointer_x+= self.pointer_vel
        if self.pointer_x<0:
            self.pointer_x= abs(self.pointer_x)
            self.pointer_vel= -self.pointer_vel
        elif self.pointer_x>100:
            excess= self.pointer_x-100
            self.pointer_x= 100- excess
            self.pointer_vel= -self.pointer_vel

        self.pointer_vel*= friction
        self.draw_scale(self.scale_segments)
        self.draw_pointer()

        if abs(self.pointer_vel)<0.2:
            self.bouncing=False
            chosen= self.logic.pick_player_from_position(
                self.pick_team, self.pick_role, self.pointer_x, self.scale_segments
            )
            self.scale_canvas.delete("all")
            self.draw_scale([])
            self.refresh_all()
            if chosen:
                w=int(self.scale_canvas.winfo_width()/2)
                h=int(self.scale_canvas.winfo_height()/2)
                chosen_color= self.player_colors.get(chosen,"red")
                text_id= self.scale_canvas.create_text(
                    w,h,
                    text=chosen,
                    fill="black",
                    font=(self.text_font_type, self.text_font_size+6,"bold"),
                    anchor="center"
                )
                bbox=self.scale_canvas.bbox(text_id)
                if bbox:
                    rect_id=self.scale_canvas.create_rectangle(bbox, fill=chosen_color, outline="")
                    self.scale_canvas.tag_raise(text_id, rect_id)
            return
        else:
            self.master.after(20, self.update_bounce)

    def build_segments(self, probs:dict):
        """Build segments for wheel based on probabilities"""
        segs=[]
        current=0.0
        for p,val in probs.items():
            width= val*100.0
            segs.append((p, current, current+width))
            current+= width
        return segs

    def draw_pointer(self):
        """Draw the pointer on wheel during spin"""
        w=self.scale_canvas.winfo_width()
        h=self.scale_canvas.winfo_height()
        px=(self.pointer_x/100)* w
        self.scale_canvas.create_line(px, 0, px, h, width=4, fill=self.ui_config["pointer_color"])

    # UNDO / SAVE / LOAD
    def undo_pick(self):
        """Undo the last player pick"""
        undone=self.logic.undo_last_pick()
        if undone:
            print(f"[UNDO] Removed {undone} from team.")
        self.refresh_all()

    def save_draft(self):
        """Save the current draft state"""
        self.logic.save_state("data/draft_remaining.csv", "data/draft_teams.csv")
        print("[GUI] Saved state.")

    def load_draft(self):
        """Load a saved draft state"""
        self.logic.load_state("data/draft_remaining.csv", "data/draft_teams.csv")
        print("[GUI] Loaded state.")
        self.refresh_all()
        for item in self.prob_tree.get_children():
            self.prob_tree.delete(item)
        self.scale_canvas.delete("all")

    # CAPTAIN
    def add_captain_popup(self):
        """Open popup to add a captain to a team"""
        team_id=self.team_var.get()
        if not team_id:
            return
        popup=tk.Toplevel(self.master)
        popup.title(f"Add Captain to {team_id}")

        tk.Label(popup, text="Captain Name:").pack(pady=self.padding)
        name_var=tk.StringVar()
        e_name=tk.Entry(popup, textvariable=name_var)
        e_name.pack(pady=self.padding)

        tk.Label(popup, text="Captain MMR:").pack(pady=self.padding)
        mmr_var=tk.StringVar()
        e_mmr=tk.Entry(popup, textvariable=mmr_var)
        e_mmr.pack(pady=self.padding)

        def confirm():
            cname= name_var.get().strip()
            if not cname:
                popup.destroy()
                return
            try:
                cmmr=int(mmr_var.get())
            except:
                cmmr=0
            self.logic.add_captain_to_team(team_id,cname,cmmr)
            self.refresh_all()
            popup.destroy()
        ttk.Button(popup, text="Confirm", command=confirm).pack(pady=self.padding*2)

    def create_team_popup(self):
        """Open popup to create a new team"""
        popup=tk.Toplevel(self.master)
        popup.title("Create New Team")
        tk.Label(popup, text="Team Name:").pack(side=tk.TOP, pady=self.padding)
        name_var=tk.StringVar()
        entry=tk.Entry(popup, textvariable=name_var)
        entry.pack(side=tk.TOP, pady=self.padding)
        def confirm():
            tname=name_var.get().strip()
            if tname:
                self.logic.register_team(tname)
                self.refresh_all()
            popup.destroy()
        ttk.Button(popup, text="Confirm",style="Normal.TButton", command=confirm).pack(side=tk.TOP, pady=self.padding*2)

    # UTILS
    def _get_base_randomness(self, team_id:str)->float:
        """Get base randomness value for team"""
        teams_data=self.logic.get_teams_data()
        if team_id not in teams_data:
            return 0.0
        n=len(teams_data[team_id]["players"])
        return self.logic.randomness_levels.get(n,0.30)

    def _team_color(self, idx: int):
        """Get team color based on index"""
        team_colors = self.ui_config["team_colors"]
        return team_colors[idx % len(team_colors)]
