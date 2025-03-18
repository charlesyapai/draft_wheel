"""
Modern Charts Module
Provides sleek, animated chart components for data visualization
"""
import tkinter as tk
import math

class ModernSigmoidChart:
    """A modern, animated sigmoid probability chart"""
    
    def __init__(self, canvas, theme_manager=None):
        """
        Initialize the sigmoid chart
        
        Args:
            canvas: Canvas widget to draw on
            theme_manager: ThemeManager instance for theming
        """
        self.canvas = canvas
        self.theme_manager = theme_manager
        self.theme = theme_manager.get_theme() if theme_manager else None
        
        # Store data for redrawing
        self.data_list = None
        self.ideal_mmr = 0
        self.player_colors = {}
        
        # Animation settings
        self.animation_speed = 500  # ms
        self.animation_active = False
        self.animation_frames = 25
        
        # Bind resize event to redraw chart
        self.canvas.bind("<Configure>", self._on_resize)
        
        # Register for theme changes
        if theme_manager:
            theme_manager.register_listener(self.on_theme_changed)
    
    def _on_resize(self, event):
        """Handle canvas resize events"""
        if self.data_list:
            self.draw_probability_curve(self.data_list, self.ideal_mmr, self.player_colors)
    
    def clear(self):
        """Clear the chart"""
        self.canvas.delete("all")
        self.data_list = None
        self.ideal_mmr = 0
        
    def on_theme_changed(self, theme):
        """Handle theme changes"""
        self.theme = theme
        if self.data_list:
            self.draw_probability_curve(self.data_list, self.ideal_mmr, self.player_colors)
    
    def set_player_colors(self, colors):
        """
        Set player colors for chart
        
        Args:
            colors: Dict of {player: color}
        """
        self.player_colors = colors.copy()
        
        # Update chart if data exists
        if self.data_list:
            self.draw_probability_curve(self.data_list, self.ideal_mmr, self.player_colors)
    
    def draw_probability_curve(self, data_list, ideal_mmr, player_colors=None):
        """
        Draw the probability curve with modern styling
        
        Args:
            data_list: List of (player, mmr, diff, probability) tuples
            ideal_mmr: Ideal MMR value to show as reference line
            player_colors: Dict mapping players to colors
        """
        # Store data for redrawing
        self.data_list = data_list
        self.ideal_mmr = ideal_mmr
        if player_colors:
            self.player_colors = player_colors.copy()
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get canvas dimensions
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # If canvas is too small, skip drawing
        if w < 50 or h < 50:
            return
            
        # Get chart bg color from theme
        bg_color = self.theme["chart_bg"] if self.theme else "#F0F0F0"
        text_color = self.theme["chart_text"] if self.theme else "#333333"
        grid_color = self.theme["chart_grid"] if self.theme else "#CCCCCC"
        accent_color = self.theme["accent"] if self.theme else "#0077FF"
        
        # Fill background with rounded rectangle
        corner_radius = 15
        
        # Add roundrectangle method to Canvas if not present
        if not hasattr(tk.Canvas, 'create_roundrectangle'):
            tk.Canvas.create_roundrectangle = _create_roundrectangle
            
        self.canvas.create_roundrectangle(
            2, 2, w-2, h-2,
            radius=corner_radius,
            fill=bg_color,
            outline=grid_color,
            width=1
        )
        
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
        
        min_mmr = max(0, min_mmr - mmr_range * 0.1)
        max_mmr = max_mmr + mmr_range * 0.1

        # Buffer for probability
        y_max_value = max_prob * 1.2
        if y_max_value < 0.05:
            y_max_value = 0.05  # minimal range

        # Define axes padding
        x_axis_pad = 60  # left margin for Y axis
        y_axis_pad = 40  # bottom margin for X axis
        top_pad = 30     # top padding
        right_pad = 25   # right padding

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
        
        # Draw chart title
        self.canvas.create_text(
            w / 2, 15,
            text="Player Probability Distribution",
            fill=text_color,
            font=("Segoe UI", 11, "bold")
        )
        
        # Draw grid
        grid_steps_x = 5
        grid_steps_y = 4
        
        # Draw horizontal grid lines
        for i in range(grid_steps_y + 1):
            y_val = y_max_value * (i / grid_steps_y)
            _, y = to_canvas_coords(min_mmr, y_val)
            
            # Draw grid line
            self.canvas.create_line(
                x_axis_pad, y, w - right_pad, y,
                fill=grid_color, width=1, dash=(4, 4)
            )
            
            # Y-axis label
            self.canvas.create_text(
                x_axis_pad - 8, y,
                text=f"{y_val:.2f}",
                fill=text_color,
                font=("Segoe UI", 8),
                anchor="e"
            )
        
        # Draw vertical grid lines
        mmr_step = (max_mmr - min_mmr) / grid_steps_x
        for i in range(grid_steps_x + 1):
            mmr_val = min_mmr + mmr_step * i
            x, _ = to_canvas_coords(mmr_val, 0)
            
            # Draw grid line
            self.canvas.create_line(
                x, top_pad, x, h - y_axis_pad,
                fill=grid_color, width=1, dash=(4, 4)
            )
            
            # X-axis label
            self.canvas.create_text(
                x, h - y_axis_pad + 15,
                text=f"{int(mmr_val)}",
                fill=text_color,
                font=("Segoe UI", 8)
            )
        
        # Draw axes
        # X-axis
        self.canvas.create_line(
            x_axis_pad, h - y_axis_pad,
            w - right_pad, h - y_axis_pad,
            fill=text_color, width=2
        )
        
        # Y-axis
        self.canvas.create_line(
            x_axis_pad, h - y_axis_pad,
            x_axis_pad, top_pad,
            fill=text_color, width=2
        )
        
        # Axis labels
        # X-axis label
        self.canvas.create_text(
            w // 2, h - 12,
            text="Player MMR",
            fill=text_color,
            font=("Segoe UI", 10, "bold")
        )
        
        # Y-axis label (vertical)
        self.canvas.create_text(
            20, h // 2,
            text="Probability",
            fill=text_color,
            font=("Segoe UI", 10, "bold")
        )

        # Draw reference line for ideal MMR
        if min_mmr <= ideal_mmr <= max_mmr:
            ideal_x, _ = to_canvas_coords(ideal_mmr, 0)
            
            # Vertical dotted line
            self.canvas.create_line(
                ideal_x, h - y_axis_pad,
                ideal_x, top_pad,
                fill=accent_color, width=2, dash=(6, 4)
            )
            
            # Label with gradient background
            label_width = 100
            label_height = 20
            
            # Create gradient background for label
            self.canvas.create_roundrectangle(
                ideal_x - label_width//2, top_pad - label_height - 5,
                ideal_x + label_width//2, top_pad - 5,
                radius=5,
                fill=accent_color,
                outline=""
            )
            
            # Label text
            self.canvas.create_text(
                ideal_x, top_pad - label_height//2 - 5,
                text=f"Ideal MMR: {int(ideal_mmr)}",
                fill="white",
                font=("Segoe UI", 9, "bold")
            )
        
        # Generate smooth sigmoid curve
        if len(data_list) > 1:
            # Sort data by MMR for curve
            sorted_data = sorted(data_list, key=lambda x: x[1])
            curve_points = []
            
            for (_, mmr, _, prob) in sorted_data:
                x, y = to_canvas_coords(mmr, prob)
                curve_points.append(x)
                curve_points.append(y)
                
            # Add extra points to smooth curve
            if len(sorted_data) > 2:
                self.canvas.create_line(
                    curve_points,
                    fill=accent_color,
                    width=2,
                    smooth=True
                )
        
        # Draw scatter points for each player with glowing effect
        for (p, pm, _, prob_val) in data_list:
            # Map to canvas coords
            (cx, cy) = to_canvas_coords(pm, prob_val)
            
            # Circle radius
            radius = 6
            glow_radius = 12
            
            # Get player color
            color = self.player_colors.get(p, accent_color)
            
            # Create glow effect (use a lighter version of the color instead of transparency)
            glow_color = self._lighten_color(color)
            self.canvas.create_oval(
                cx - glow_radius, cy - glow_radius,
                cx + glow_radius, cy + glow_radius,
                fill=glow_color, outline=""
            )
            
            # Draw circle for player point
            self.canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                fill=color, outline="white", width=2
            )
            
            # Label with player name
            # Create label with background
            text_width = len(p) * 6  # Approximate width based on text length
            self.canvas.create_roundrectangle(
                cx - text_width//2 - 5, cy - 25 - 5,
                cx + text_width//2 + 5, cy - 25 + 10,
                radius=5,
                fill=color,
                outline="white",
                width=1
            )
            
            # Label text
            self.canvas.create_text(
                cx, cy - 25,
                text=p,
                fill="white",
                font=("Segoe UI", 9, "bold")
            )
            
    def _lighten_color(self, hex_color):
        """
        Create a lighter version of a color
        
        Args:
            hex_color: Color in hex format (#RRGGBB)
            
        Returns:
            str: Lightened color
        """
        # Convert hex to rgb
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten by blending with white
        factor = 0.7  # 70% original color, 30% white
        r = int(r * factor + 255 * (1 - factor))
        g = int(g * factor + 255 * (1 - factor))
        b = int(b * factor + 255 * (1 - factor))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'


class ModernProbabilityTable:
    """A modern, animated probability table with advanced styling"""
    
    def __init__(self, parent, theme_manager=None):
        """
        Initialize the probability table
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance for theming
        """
        self.parent = parent
        self.theme_manager = theme_manager
        self.theme = theme_manager.get_theme() if theme_manager else None
        
        # Store data
        self.player_colors = {}
        self.current_data = None
        
        # Create UI components
        self._create_ui()
        
        # Register for theme changes
        if theme_manager:
            theme_manager.register_listener(self.on_theme_changed)
    
    def _create_ui(self):
        """Create the UI components"""
        # Get colors from theme
        bg_color = self.theme["panel_bg"] if self.theme else "#F0F0F0"
        header_bg = self.theme["header_bg"] if self.theme else "#E0E0E0"
        text_color = self.theme["text"] if self.theme else "#333333"
        accent_color = self.theme["accent"] if self.theme else "#0077FF"
        
        # Create main frame
        self.frame = tk.Frame(self.parent, bg=bg_color)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create header
        header_frame = tk.Frame(self.frame, bg=header_bg, height=30)
        header_frame.pack(fill=tk.X, padx=2, pady=(2, 0))
        
        # Title
        tk.Label(
            header_frame,
            text="Player Probabilities",
            bg=header_bg,
            fg=text_color,
            font=("Segoe UI", 11, "bold")
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Create columns header
        cols_frame = tk.Frame(self.frame, bg=bg_color)
        cols_frame.pack(fill=tk.X, padx=2, pady=(0, 0))
        
        # Column headers with gradient background
        header_height = 30
        
        # Player column
        player_header = tk.Canvas(
            cols_frame, height=header_height, width=100,
            bg=bg_color, bd=0, highlightthickness=0
        )
        player_header.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        
        # Draw gradient background
        player_header.create_rectangle(
            0, 0, 100, header_height,
            fill=accent_color, outline=""
        )
        
        # Header text
        player_header.create_text(
            50, header_height//2,
            text="Player",
            fill="white",
            font=("Segoe UI", 10, "bold")
        )
        
        # MMR column
        mmr_header = tk.Canvas(
            cols_frame, height=header_height, width=60,
            bg=bg_color, bd=0, highlightthickness=0
        )
        mmr_header.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        
        # Draw gradient background
        mmr_header.create_rectangle(
            0, 0, 60, header_height,
            fill=accent_color, outline=""
        )
        
        # Header text
        mmr_header.create_text(
            30, header_height//2,
            text="MMR",
            fill="white",
            font=("Segoe UI", 10, "bold")
        )
        
        # Diff column
        diff_header = tk.Canvas(
            cols_frame, height=header_height, width=60,
            bg=bg_color, bd=0, highlightthickness=0
        )
        diff_header.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        
        # Draw gradient background
        diff_header.create_rectangle(
            0, 0, 60, header_height,
            fill=accent_color, outline=""
        )
        
        # Header text
        diff_header.create_text(
            30, header_height//2,
            text="Diff",
            fill="white",
            font=("Segoe UI", 10, "bold")
        )
        
        # Probability column
        prob_header = tk.Canvas(
            cols_frame, height=header_height, width=80,
            bg=bg_color, bd=0, highlightthickness=0
        )
        prob_header.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        
        # Draw gradient background
        prob_header.create_rectangle(
            0, 0, 80, header_height,
            fill=accent_color, outline=""
        )
        
        # Header text
        prob_header.create_text(
            40, header_height//2,
            text="Probability",
            fill="white",
            font=("Segoe UI", 10, "bold")
        )
        
        # Preference column
        pref_header = tk.Canvas(
            cols_frame, height=header_height, width=60,
            bg=bg_color, bd=0, highlightthickness=0
        )
        pref_header.pack(side=tk.LEFT, fill=tk.Y)
        
        # Draw gradient background
        pref_header.create_rectangle(
            0, 0, 60, header_height,
            fill=accent_color, outline=""
        )
        
        # Header text
        pref_header.create_text(
            30, header_height//2,
            text="Pref",
            fill="white",
            font=("Segoe UI", 10, "bold")
        )
        
        # Create scrollable frame for rows
        self.canvas = tk.Canvas(self.frame, bg=bg_color, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(1, 2), padx=2)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(self.canvas, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create inner frame for rows
        self.rows_frame = tk.Frame(self.canvas, bg=bg_color)
        self.canvas.create_window((0, 0), window=self.rows_frame, anchor=tk.NW)
        
        # Update scrollregion when rows frame changes size
        self.rows_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
    def clear(self):
        """Clear the probability table"""
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        
        self.current_data = None
    
    def update_probabilities(self, probs, player_mmrs, ideal_mmr, role_prefs=None):
        """
        Update probability display with animation
        
        Args:
            probs: Dict of {player: probability}
            player_mmrs: Dict of {player: mmr}
            ideal_mmr: Ideal MMR for the pick
            role_prefs: Dict of {player: preference} for the current role
        """
        if not probs:
            self.clear()
            return
        
        # Build data and sort by probability (descending)
        data_list = []
        for p, prob_val in probs.items():
            pm = player_mmrs[p]
            diff_val = abs(pm - ideal_mmr)
            pref = role_prefs.get(p, 1) if role_prefs else 1
            data_list.append((p, pm, diff_val, prob_val, pref))
        
        # Sort by probability descending
        data_list.sort(key=lambda x: x[3], reverse=True)
        
        # Store current data
        self.current_data = data_list
        
        # Clear existing rows
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        
        # Add roundrectangle method to Canvas if not present
        if not hasattr(tk.Canvas, 'create_roundrectangle'):
            tk.Canvas.create_roundrectangle = _create_roundrectangle
        
        # Create row for each player
        row_height = 40
        for idx, (p, pm, diff_val, prob_val, pref) in enumerate(data_list):
            # Format probability as percentage
            prob_pct = prob_val * 100.0
            prob_str = f"{prob_pct:.1f}%"
            
            # Get color for this player
            color = self.player_colors.get(p, "#0077FF")  # Default to accent blue
            
            # Alternate row background slightly
            row_bg = self.theme["panel_bg"] if self.theme else "#F0F0F0"
            if idx % 2 == 1:
                # Slightly darker for odd rows
                row_bg = self._adjust_color_brightness(row_bg, -10)
            
            # Create row frame
            row_frame = tk.Frame(self.rows_frame, bg=row_bg, height=row_height)
            row_frame.pack(fill=tk.X, pady=(0, 1))
            
            # Ensure the frame maintains its height
            row_frame.pack_propagate(False)
            
            # Player cell with colored indicator
            player_frame = tk.Frame(row_frame, bg=row_bg, width=100)
            player_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
            player_frame.pack_propagate(False)
            
            # Color indicator
            indicator = tk.Frame(player_frame, bg=color, width=5)
            indicator.pack(side=tk.LEFT, fill=tk.Y)
            
            # Player name
            tk.Label(
                player_frame,
                text=p,
                bg=row_bg,
                fg=self.theme["text"] if self.theme else "#333333",
                font=("Segoe UI", 10),
                anchor="w"
            ).pack(side=tk.LEFT, padx=(10, 0), pady=5)
            
            # MMR cell
            mmr_frame = tk.Frame(row_frame, bg=row_bg, width=60)
            mmr_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
            mmr_frame.pack_propagate(False)
            
            tk.Label(
                mmr_frame,
                text=str(int(pm)),
                bg=row_bg,
                fg=self.theme["text"] if self.theme else "#333333",
                font=("Segoe UI", 10)
            ).pack(expand=True)
            
            # Diff cell
            diff_frame = tk.Frame(row_frame, bg=row_bg, width=60)
            diff_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
            diff_frame.pack_propagate(False)
            
            tk.Label(
                diff_frame,
                text=str(int(diff_val)),
                bg=row_bg,
                fg=self.theme["text"] if self.theme else "#333333",
                font=("Segoe UI", 10)
            ).pack(expand=True)
            
            # Probability cell with progress bar
            prob_frame = tk.Frame(row_frame, bg=row_bg, width=80)
            prob_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
            prob_frame.pack_propagate(False)
            
            # Canvas for progress bar
            prob_canvas = tk.Canvas(
                prob_frame, 
                bg=row_bg, 
                height=20, 
                width=70,
                bd=0,
                highlightthickness=0
            )
            prob_canvas.pack(expand=True)
            
            # Background bar
            bar_bg = self.theme["chart_grid"] if self.theme else "#DDDDDD"
            prob_canvas.create_roundrectangle(
                0, 5, 70, 15,
                radius=5,
                fill=bar_bg,
                outline=""
            )
            
            # Progress bar (width based on probability)
            bar_width = max(5, int(70 * prob_val))  # Min width 5px
            prob_canvas.create_roundrectangle(
                0, 5, bar_width, 15,
                radius=5,
                fill=color,
                outline=""
            )
            
            # Probability text
            prob_canvas.create_text(
                35, 10,
                text=prob_str,
                fill="white" if bar_width > 35 else self.theme["text"] if self.theme else "#333333",
                font=("Segoe UI", 9, "bold")
            )
            
            # Preference cell
            pref_frame = tk.Frame(row_frame, bg=row_bg, width=60)
            pref_frame.pack(side=tk.LEFT, fill=tk.Y)
            pref_frame.pack_propagate(False)
            
            # Draw stars based on preference
            pref_canvas = tk.Canvas(
                pref_frame,
                bg=row_bg,
                height=20,
                width=60,
                bd=0,
                highlightthickness=0
            )
            pref_canvas.pack(expand=True)
            
            # Draw stars for preference
            star_color = self.theme["warning"] if self.theme else "#FFCC00"
            star_size = 12
            for i in range(pref):
                x = 10 + i * (star_size + 5)
                y = 10
                self._draw_star(pref_canvas, x, y, star_size, star_color)
    
    def _draw_star(self, canvas, x, y, size, color):
        """Draw a star shape on the canvas"""
        points = []
        for i in range(5):
            # Outer points
            angle = math.pi/2 + i * 2*math.pi/5
            points.append(x + size * math.cos(angle))
            points.append(y - size * math.sin(angle))
            
            # Inner points
            angle += math.pi/5
            points.append(x + (size/2) * math.cos(angle))
            points.append(y - (size/2) * math.sin(angle))
        
        canvas.create_polygon(points, fill=color, outline="")
    
    def _adjust_color_brightness(self, hex_color, amount):
        """Adjust the brightness of a hex color"""
        # Convert hex to rgb
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Adjust brightness
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        # Convert back to hex
        return f'#{int(r):02x}{int(g):02x}{int(b):02x}'
    
    def set_player_colors(self, colors):
        """
        Set player colors
        
        Args:
            colors: Dict of {player: color}
        """
        self.player_colors = colors.copy()
        
        # Update display if data exists
        if self.current_data:
            probs = {p: prob for p, _, _, prob, _ in self.current_data}
            player_mmrs = {p: mmr for p, mmr, _, _, _ in self.current_data}
            
            # Find the ideal_mmr
            if len(self.current_data) > 0:
                # Use smallest diff to find ideal_mmr
                _, mmr, diff, _, _ = min(self.current_data, key=lambda x: x[2])
                ideal_mmr = mmr if diff == 0 else mmr - diff  # This might be wrong, but best we can do
                
                # Get role_prefs
                role_prefs = {p: pref for p, _, _, _, pref in self.current_data}
                
                # Update
                self.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)
    
    def on_theme_changed(self, theme):
        """
        Handle theme changes
        
        Args:
            theme: New theme dict
        """
        self.theme = theme
        
        # Update UI colors
        bg_color = theme["panel_bg"]
        text_color = theme["text"]
        accent_color = theme["accent"]
        
        # Update frame colors
        self.frame.configure(bg=bg_color)
        self.canvas.configure(bg=bg_color)
        self.rows_frame.configure(bg=bg_color)
        
        # Update header
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.canvas:
                widget.configure(bg=bg_color)
                
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=theme["header_bg"], fg=text_color)
                    elif isinstance(child, tk.Canvas):
                        child.configure(bg=bg_color)
                        # Update canvas elements (would need object IDs)
        
        # Re-draw the data with new theme
        if self.current_data:
            probs = {p: prob for p, _, _, prob, _ in self.current_data}
            player_mmrs = {p: mmr for p, mmr, _, _, _ in self.current_data}
            
            # Find the ideal_mmr
            if len(self.current_data) > 0:
                # Use smallest diff to find ideal_mmr
                _, mmr, diff, _, _ = min(self.current_data, key=lambda x: x[2])
                ideal_mmr = mmr if diff == 0 else mmr - diff
                
                # Get role_prefs
                role_prefs = {p: pref for p, _, _, _, pref in self.current_data}
                
                # Update
                self.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)


# Add roundrectangle method to Canvas if not already defined
def _create_roundrectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return self.create_polygon(points, **kwargs, smooth=True)

if not hasattr(tk.Canvas, 'create_roundrectangle'):
    tk.Canvas.create_roundrectangle = _create_roundrectangle
