"""
Probability View Component
Handles the probability display and sigmoid chart
"""
import tkinter as tk
from tkinter import ttk

class ProbabilityView:
    """Component for displaying probabilities and sigmoid chart"""
    
    def __init__(self, parent, ui_config):
        """
        Initialize the probability view
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dict
        """
        self.parent = parent
        self.ui_config = ui_config
        self.player_colors = {}
        self.sigmoid_data = None
        self.sigmoid_ideal_mmr = 0
        
        # Create probability tree view
        self._create_probability_tree()
        
    def _create_probability_tree(self):
        """Create the probability tree view"""
        # Label for section
        tk.Label(
            self.parent, 
            text="Probabilities", 
            bg=self.ui_config["frame_bg_color"],
            font=(self.ui_config["text_font_type"], self.ui_config["subheader_font_size"], "bold")
        ).grid(row=0, column=0, sticky="w")

        # Prob tree with scrollbar
        prob_tree_frame = tk.Frame(self.parent)
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
        
    def update_probabilities(self, probs, player_mmrs, ideal_mmr, role_prefs=None):
        """
        Update probability display
        
        Args:
            probs: Dict of {player: probability}
            player_mmrs: Dict of {player: mmr}
            ideal_mmr: Ideal MMR for the pick
            role_prefs: Dict of {player: preference} for the current role
        """
        if not probs:
            self.clear()
            return
            
        # Clear existing items
        for item in self.prob_tree.get_children():
            self.prob_tree.delete(item)
        
        # Build data (player, mmr, diff, prob) and sort by MMR
        data_list = []
        for p, prob_val in probs.items():
            pm = player_mmrs[p]
            diff_val = abs(pm - ideal_mmr)
            pref = role_prefs.get(p, 1) if role_prefs else 1
            data_list.append((p, pm, diff_val, prob_val, pref))
            
        # Sort by MMR ascending
        data_list.sort(key=lambda x: x[1])
        
        # Store for sigmoid chart
        self.sigmoid_data = [(p, pm, diff_val, prob_val) for p, pm, diff_val, prob_val, _ in data_list]
        self.sigmoid_ideal_mmr = ideal_mmr
        
        # Populate the Treeview in sorted order
        idx = 0
        for (p, pm, diff_val, prob_val, pref) in data_list:
            prob_pct = prob_val * 100.0
            prob_str = f"{prob_pct:.1f}%"

            # Assign color
            color = self._get_color(idx)
            self.player_colors[p] = color

            # Insert row into tree
            style_name = f"ColorStyle_{idx}"
            s = ttk.Style()
            s.configure(style_name, background=color,
                        font=(self.ui_config["text_font_type"], self.ui_config["text_font_size"], "bold"))

            row_id = self.prob_tree.insert("", "end", values=(p, int(pm), int(diff_val), prob_str, pref))
            self.prob_tree.item(row_id, tags=(style_name,))
            self.prob_tree.tag_configure(style_name, background=color)

            idx += 1
    
    def clear(self):
        """Clear the probability display"""
        for item in self.prob_tree.get_children():
            self.prob_tree.delete(item)
        self.player_colors = {}
        self.sigmoid_data = None
    
    def _get_color(self, idx):
        """
        Get a color for a player
        
        Args:
            idx: Player index
            
        Returns:
            str: Color hex code
        """
        colors = self.ui_config["team_colors"]
        return colors[idx % len(colors)]
    
    def get_player_colors(self):
        """
        Get the current player colors
        
        Returns:
            dict: Map of player names to colors
        """
        return self.player_colors.copy()


class SigmoidChartView:
    """Sigmoid chart view for probability visualization"""
    
    def __init__(self, parent, ui_config):
        """
        Initialize the sigmoid chart view
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dict
        """
        self.parent = parent
        self.ui_config = ui_config
        self.player_colors = {}
        
        # Create canvas for sigmoid chart
        self.sigmoid_canvas = tk.Canvas(parent, bg=ui_config["sigmoid_bg_color"])
        self.sigmoid_canvas.pack(fill=tk.BOTH, expand=True, 
                                padx=ui_config["padding"]*2, 
                                pady=ui_config["padding"]*2)
        
        # Bind resize event
        self.sigmoid_canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Data for redrawing
        self.data_list = None
        self.ideal_mmr = 0
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize by redrawing"""
        if self.data_list:
            self.draw_final_probability_curve(self.data_list, self.ideal_mmr)
    
    def draw_final_probability_curve(self, data_list, ideal_mmr):
        """
        Draw a scatter plot of probability vs MMR
        
        Args:
            data_list: List of (player, mmr, diff, probability) tuples
            ideal_mmr: Ideal MMR value to show as reference line
        """
        # Store data for redrawing on resize
        self.data_list = data_list
        self.ideal_mmr = ideal_mmr
        
        # Clear canvas
        self.sigmoid_canvas.delete("all")
        
        # Get canvas dimensions
        w = int(self.sigmoid_canvas.winfo_width())
        h = int(self.sigmoid_canvas.winfo_height())
        
        # If canvas is too small, skip drawing
        if w < 50 or h < 50:
            return
            
        # Determine the MMR range and maximum probability
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

        # Add padding to MMR range
        mmr_range = max_mmr - min_mmr
        if mmr_range < 100:  # Ensure a minimum range
            mmr_range = 100
            min_mmr = max(0, min_mmr - 50)
            max_mmr = min_mmr + mmr_range
        
        min_mmr = max(0, min_mmr - mmr_range * 0.05)
        max_mmr = max_mmr + mmr_range * 0.05

        # Buffer for probability
        y_max_value = max_prob * 1.1
        if y_max_value < 0.05:
            y_max_value = 0.05  # minimal range

        # Define axes padding
        x_axis_pad = 50  # left margin for Y axis
        y_axis_pad = 30  # bottom margin for X axis
        top_pad = 25     # top padding
        right_pad = 20   # right padding

        # Draw the X-axis (horizontal)
        self.sigmoid_canvas.create_line(
            x_axis_pad, h - y_axis_pad,  # start
            w - right_pad, h - y_axis_pad,  # end
            fill="black", width=2
        )

        # Draw the Y-axis (vertical)
        self.sigmoid_canvas.create_line(
            x_axis_pad, h - y_axis_pad,  # start
            x_axis_pad, top_pad,         # end
            fill="black", width=2
        )

        # Helper function to map coordinates
        def to_canvas_coords(mmr_val, prob_val):
            # X: left -> right
            x_min = x_axis_pad
            x_max = w - right_pad
            rx = (mmr_val - min_mmr) / (max_mmr - min_mmr) if max_mmr > min_mmr else 0.5
            cx = x_min + (x_max - x_min) * rx

            # Y: bottom -> top (invert)
            y_min = top_pad
            y_max = h - y_axis_pad
            ry = prob_val / y_max_value
            cy = y_max - (y_max - y_min) * ry

            return (cx, cy)

        # Draw reference line for ideal MMR
        if min_mmr <= ideal_mmr <= max_mmr:
            ideal_x, _ = to_canvas_coords(ideal_mmr, 0)
            # Vertical dotted line
            self.sigmoid_canvas.create_line(
                ideal_x, h - y_axis_pad,
                ideal_x, top_pad,
                fill="blue", width=1, dash=(4, 4)
            )
            # Label
            self.sigmoid_canvas.create_text(
                ideal_x, top_pad - 5,
                text=f"Ideal MMR: {int(ideal_mmr)}",
                fill="blue",
                font=(self.ui_config["text_font_type"], 8, "bold"),
                anchor="s"
            )

        # Draw scatter points for each player
        for (p, pm, _, prob_val) in data_list:
            # Map to canvas coords
            (cx, cy) = to_canvas_coords(pm, prob_val)

            # Circle radius and color
            radius = 4
            color = self.player_colors.get(p, "red")  # or pick a default

            # Draw circle for player point
            self.sigmoid_canvas.create_oval(cx - radius, cy - radius, 
                                         cx + radius, cy + radius, 
                                         fill=color)

            # Label with player name
            self.sigmoid_canvas.create_text(
                cx, cy - 10,
                text=p,
                fill=color,
                font=(self.ui_config["text_font_type"], 8, "bold")
            )

        # Draw X-axis ticks (MMR values)
        num_x_ticks = 5
        mmr_step = (max_mmr - min_mmr) / num_x_ticks
        
        for i in range(num_x_ticks + 1):
            tick_mmr = min_mmr + (mmr_step * i)
            tx, ty = to_canvas_coords(tick_mmr, 0)
            # Tick mark
            self.sigmoid_canvas.create_line(tx, ty, tx, ty + 5, fill="black")
            # Label below the axis
            self.sigmoid_canvas.create_text(tx, ty + 15, 
                                         text=f"{int(tick_mmr)}", 
                                         font=(self.ui_config["text_font_type"], 8))

        # Draw Y-axis ticks (probability)
        num_y_ticks = 5
        for i in range(num_y_ticks + 1):
            tick_prob = (y_max_value / num_y_ticks) * i
            tx, ty = to_canvas_coords(min_mmr, tick_prob)
            # Tick mark
            self.sigmoid_canvas.create_line(tx, ty, tx - 5, ty, fill="black")
            # Label to the left of the axis
            self.sigmoid_canvas.create_text(tx - 20, ty, 
                                         text=f"{tick_prob:.2f}", 
                                         font=(self.ui_config["text_font_type"], 8))

        # Axis Labels
        # X-axis label
        x_label_x = (w - x_axis_pad - right_pad) / 2 + x_axis_pad
        x_label_y = h - 10
        self.sigmoid_canvas.create_text(
            x_label_x, x_label_y,
            text="Player MMR",
            font=(self.ui_config["text_font_type"], 9, "bold")
        )

        # Y-axis label (vertical)
        y_label_x = 15
        y_label_y = (h - y_axis_pad - top_pad) / 2 + top_pad
        self.sigmoid_canvas.create_text(
            y_label_x, y_label_y,
            text="Final Probability",
            font=(self.ui_config["text_font_type"], 9, "bold"),
            angle=90
        )
    
    def clear(self):
        """Clear the sigmoid chart"""
        self.sigmoid_canvas.delete("all")
        self.data_list = None
        self.ideal_mmr = 0
    
    def set_player_colors(self, colors):
        """
        Set player colors for chart
        
        Args:
            colors: Dict of {player: color}
        """
        self.player_colors = colors.copy() 