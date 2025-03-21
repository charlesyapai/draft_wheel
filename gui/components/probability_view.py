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
        # Label for section - with gaming style
        header_frame = tk.Frame(self.parent, bg="#222222", bd=2, relief=tk.GROOVE)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Create a gradient header
        header_canvas = tk.Canvas(header_frame, height=38, bg="#222222", 
                                 highlightthickness=0)
        header_canvas.pack(fill=tk.X, expand=True)
        
        # Draw gradient background
        header_width = self.parent.winfo_width() or 300
        header_canvas.create_rectangle(0, 0, header_width, 38, 
                                      fill="#222222", outline="#444444", width=2)
        
        # Draw decorative accent lines
        for i in range(0, header_width, 20):
            header_canvas.create_line(i, 0, i+10, 38, fill="#333333", width=1)
        
        # Draw corner accents
        corner_size = 10
        accent_color = "#00aaff"
        header_canvas.create_line(0, 0, corner_size, 0, fill=accent_color, width=2)
        header_canvas.create_line(0, 0, 0, corner_size, fill=accent_color, width=2)
        header_canvas.create_line(header_width, 0, header_width-corner_size, 0, 
                                fill=accent_color, width=2)
        header_canvas.create_line(header_width, 0, header_width, corner_size, 
                                fill=accent_color, width=2)
        
        # Title with shadow effect
        header_canvas.create_text(12, 20, text="PROBABILITIES", 
                                 font=(self.ui_config["text_font_type"], 
                                       self.ui_config["subheader_font_size"], "bold"),
                                 fill="#000000", anchor="w")
        header_canvas.create_text(10, 18, text="PROBABILITIES", 
                                 font=(self.ui_config["text_font_type"], 
                                       self.ui_config["subheader_font_size"], "bold"),
                                 fill="#00aaff", anchor="w")

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
                                padx=ui_config["padding"]*3,  # Increased padding 
                                pady=ui_config["padding"]*3)  # Increased padding
        
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
        
        # Create gaming background
        self._draw_gaming_background(w, h)
            
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

        # Define axes padding - increased left padding for y-axis label
        x_axis_pad = 80  # left margin for Y axis - increased from 70
        y_axis_pad = 40  # bottom margin for X axis
        top_pad = 40     # top padding - increased from 30
        right_pad = 40   # right padding - increased from 30

        # Draw the grid first
        self._draw_grid(w, h, x_axis_pad, y_axis_pad, top_pad, right_pad, min_mmr, max_mmr, y_max_value)

        # Draw the X-axis (horizontal) with gaming aesthetic
        self.sigmoid_canvas.create_line(
            x_axis_pad, h - y_axis_pad,  # start
            w - right_pad, h - y_axis_pad,  # end
            fill="#00aaff", width=2
        )
        
        # Draw tick marks and labels on X-axis
        x_ticks = 5
        mmr_range = max_mmr - min_mmr
        for i in range(x_ticks + 1):
            x_pos = x_axis_pad + ((w - x_axis_pad - right_pad) / x_ticks) * i
            tick_mmr = min_mmr + (mmr_range / x_ticks) * i
            
            # Tick mark
            self.sigmoid_canvas.create_line(
                x_pos, h - y_axis_pad,
                x_pos, h - y_axis_pad + 5,
                fill="#00aaff", width=2
            )
            
            # MMR label with shadow
            self.sigmoid_canvas.create_text(
                x_pos+1, h - y_axis_pad + 12,
                text=f"{int(tick_mmr):,}",
                font=(self.ui_config["text_font_type"], 10, "bold"),
                fill="#000000", anchor="n"
            )
            self.sigmoid_canvas.create_text(
                x_pos, h - y_axis_pad + 10,
                text=f"{int(tick_mmr):,}",
                font=(self.ui_config["text_font_type"], 10, "bold"),
                fill="#cccccc", anchor="n"
            )

        # Draw the Y-axis (vertical) with gaming aesthetic
        self.sigmoid_canvas.create_line(
            x_axis_pad, h - y_axis_pad,
            x_axis_pad, top_pad,
            fill="#00aaff", width=2
        )
        
        # Draw tick marks and labels on Y-axis
        y_ticks = 5
        for i in range(y_ticks + 1):
            y_pos = h - y_axis_pad - ((h - y_axis_pad - top_pad) / y_ticks) * i
            tick_prob = (y_max_value / y_ticks) * i
            
            # Tick mark
            self.sigmoid_canvas.create_line(
                x_axis_pad, y_pos,
                x_axis_pad - 5, y_pos,
                fill="#00aaff", width=2
            )
            
            # Probability label with shadow
            self.sigmoid_canvas.create_text(
                x_axis_pad - 11, y_pos+1,
                text=f"{tick_prob:.1%}",
                font=(self.ui_config["text_font_type"], 10, "bold"),
                fill="#000000", anchor="e"
            )
            self.sigmoid_canvas.create_text(
                x_axis_pad - 10, y_pos,
                text=f"{tick_prob:.1%}",
                font=(self.ui_config["text_font_type"], 10, "bold"),
                fill="#cccccc", anchor="e"
            )
            
        # Draw axis titles with gaming aesthetic
        # X-axis title
        self.sigmoid_canvas.create_text(
            w/2+1, h-5,
            text="MMR",
            font=(self.ui_config["text_font_type"], 12, "bold"),
            fill="#000000", anchor="s"
        )
        self.sigmoid_canvas.create_text(
            w/2, h-7,
            text="MMR",
            font=(self.ui_config["text_font_type"], 12, "bold"),
            fill="#00aaff", anchor="s"
        )
        
        # Y-axis title - adjusted position to avoid cutting off
        self.sigmoid_canvas.create_text(
            25, h/2,  # Moved from 10 to 25 to give more space
            text="PROBABILITY",
            font=(self.ui_config["text_font_type"], 12, "bold"),
            fill="#00aaff", angle=90, anchor="s"
        )
        
        # Draw ideal MMR reference line as a thin dotted line
        if ideal_mmr > 0:
            x_ideal = self._mmr_to_x(ideal_mmr, min_mmr, max_mmr, x_axis_pad, w - right_pad)
            
            # Create thin dotted red line
            self.sigmoid_canvas.create_line(
                x_ideal, h - y_axis_pad,
                x_ideal, top_pad,
                width=1,
                fill="#ff0000",
                dash=(3, 3)  # Create dotted line pattern
            )
            
            # Draw label for ideal MMR at the bottom instead of top
            self.sigmoid_canvas.create_text(
                x_ideal+1, h - y_axis_pad - 15,  # Moved up above X axis
                text=f"Ideal MMR: {int(ideal_mmr):,}",
                font=(self.ui_config["text_font_type"], 10, "bold"),
                fill="#000000", anchor="s"  # Changed anchor to south
            )
            self.sigmoid_canvas.create_text(
                x_ideal, h - y_axis_pad - 16,  # Moved up above X axis
                text=f"Ideal MMR: {int(ideal_mmr):,}",
                font=(self.ui_config["text_font_type"], 10, "bold"),
                fill="#ff0000", anchor="s"  # Changed anchor to south
            )

        # Draw data points
        for player, mmr, _, prob in data_list:
            # Calculate position
            x = self._mmr_to_x(mmr, min_mmr, max_mmr, x_axis_pad, w - right_pad)
            y = self._prob_to_y(prob, y_max_value, h - y_axis_pad, top_pad)
            
            player_color = self.player_colors.get(player, "#ffffff")
            
            # Draw the dot
            dot_size = 6
            self.sigmoid_canvas.create_oval(
                x-dot_size, y-dot_size, 
                x+dot_size, y+dot_size, 
                fill=player_color,
                outline="#ffffff",
                width=1
            )
            
            # Draw player name with shadow
            self.sigmoid_canvas.create_text(
                x+1, y-dot_size-6,
                text=player,
                font=(self.ui_config["text_font_type"], 9, "bold"),
                fill="#000000", anchor="s"
            )
            self.sigmoid_canvas.create_text(
                x, y-dot_size-7,
                text=player,
                font=(self.ui_config["text_font_type"], 9, "bold"),
                fill="#ffffff", anchor="s"
            )
            
        # Connect the points to form a curve, sorted by MMR
        sorted_data = sorted(data_list, key=lambda x: x[1])  # sort by MMR
        if sorted_data:
            curve_points = []
            for _, mmr, _, prob in sorted_data:
                x = self._mmr_to_x(mmr, min_mmr, max_mmr, x_axis_pad, w - right_pad)
                y = self._prob_to_y(prob, y_max_value, h - y_axis_pad, top_pad)
                curve_points.extend([x, y])
                
            if len(curve_points) >= 4:  # Need at least 2 points
                self.sigmoid_canvas.create_line(
                    *curve_points,
                    fill="#00aaff", width=2, smooth=True
                )
        
        # Draw chart title
        self._draw_chart_title(w, "PROBABILITY DISTRIBUTION", top_pad-20)
    
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
    
    def _draw_gaming_background(self, w, h):
        """Draw a gaming-style background with gradient and accents"""
        # Draw dark background
        self.sigmoid_canvas.create_rectangle(0, 0, w, h, fill="#222222", outline="")
        
        # Add subtle grid pattern
        for i in range(0, w, 30):
            self.sigmoid_canvas.create_line(i, 0, i, h, fill="#2a2a2a", width=1)
        
        for i in range(0, h, 30):
            self.sigmoid_canvas.create_line(0, i, w, i, fill="#2a2a2a", width=1)
        
        # Draw border
        self.sigmoid_canvas.create_rectangle(0, 0, w, h, fill="", outline="#444444", width=2)
        
        # Add corner accents
        corner_size = 15
        self.sigmoid_canvas.create_line(0, 0, corner_size, 0, fill="#00aaff", width=2)
        self.sigmoid_canvas.create_line(0, 0, 0, corner_size, fill="#00aaff", width=2)
        self.sigmoid_canvas.create_line(w, 0, w-corner_size, 0, fill="#00aaff", width=2)
        self.sigmoid_canvas.create_line(w, 0, w, corner_size, fill="#00aaff", width=2)
        self.sigmoid_canvas.create_line(0, h, corner_size, h, fill="#00aaff", width=2)
        self.sigmoid_canvas.create_line(0, h, 0, h-corner_size, fill="#00aaff", width=2)
        self.sigmoid_canvas.create_line(w, h, w-corner_size, h, fill="#00aaff", width=2)
        self.sigmoid_canvas.create_line(w, h, w, h-corner_size, fill="#00aaff", width=2)
    
    def _draw_grid(self, w, h, x_axis_pad, y_axis_pad, top_pad, right_pad, min_mmr, max_mmr, y_max):
        """Draw grid lines for the chart"""
        # Draw horizontal grid lines
        y_ticks = 5
        for i in range(1, y_ticks + 1):
            y_pos = h - y_axis_pad - ((h - y_axis_pad - top_pad) / y_ticks) * i
            
            # Dashed grid line
            dash_pattern = (5, 3)
            self.sigmoid_canvas.create_line(
                x_axis_pad, y_pos,
                w - right_pad, y_pos,
                fill="#444444",
                width=1,
                dash=dash_pattern
            )
        
        # Draw vertical grid lines
        x_ticks = 5
        mmr_range = max_mmr - min_mmr
        for i in range(1, x_ticks + 1):
            x_pos = x_axis_pad + ((w - x_axis_pad - right_pad) / x_ticks) * i
            
            # Dashed grid line
            dash_pattern = (5, 3)
            self.sigmoid_canvas.create_line(
                x_pos, h - y_axis_pad,
                x_pos, top_pad,
                fill="#444444",
                width=1,
                dash=dash_pattern
            )
    
    def _draw_chart_title(self, w, title, y_pos):
        """Draw chart title with gaming aesthetic"""
        title_width = len(title) * 10
        padding = 15
        
        # Draw title background with adjusted position
        self.sigmoid_canvas.create_rectangle(
            w/2 - title_width/2 - padding,
            y_pos - 10,  # Adjusted position
            w/2 + title_width/2 + padding,
            y_pos + 10,  # Adjusted position
            fill="#191919",
            outline="#00aaff",
            width=2
        )
        
        # Draw title text with shadow - adjusted position
        self.sigmoid_canvas.create_text(
            w/2+1, y_pos+1,
            text=title,
            font=(self.ui_config["text_font_type"], 11, "bold"),
            fill="#000000"
        )
        self.sigmoid_canvas.create_text(
            w/2, y_pos,
            text=title,
            font=(self.ui_config["text_font_type"], 11, "bold"),
            fill="#00aaff"
        )
    
    def _mmr_to_x(self, mmr, min_mmr, max_mmr, x_min, x_max):
        """Convert MMR value to X coordinate"""
        mmr_range = max_mmr - min_mmr
        if mmr_range == 0:
            return x_min
        return x_min + ((mmr - min_mmr) / mmr_range) * (x_max - x_min)
    
    def _prob_to_y(self, prob, max_prob, y_max, y_min):
        """Convert probability value to Y coordinate"""
        if max_prob == 0:
            return y_max
        return y_max - (prob / max_prob) * (y_max - y_min) 