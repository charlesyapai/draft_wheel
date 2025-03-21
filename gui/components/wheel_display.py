"""
Wheel Display Component
Handles the scale and probability visualization
"""
import tkinter as tk
import random

class WheelDisplay:
    """Wheel display for visualizing probabilities and spinning animation"""
    
    def __init__(self, parent, ui_config):
        """
        Initialize the wheel display
        
        Args:
            parent: Parent widget
            ui_config: UI configuration dict
        """
        self.parent = parent
        self.ui_config = ui_config
        self.wheel_size = ui_config["wheel_size"]
        self.wheel_height = ui_config["wheel_height"]
        
        # Use configurable font settings with defaults if not provided
        self.wheel_font_type = ui_config.get("wheel_font_type", ui_config["text_font_type"])
        self.wheel_font_size = ui_config.get("wheel_font_size", ui_config["text_font_size"])
        
        # Create the canvas for the scale display
        self.scale_canvas = tk.Canvas(parent, bg=ui_config["canvas_bg_color"])
        self.scale_canvas.pack(fill=tk.BOTH, expand=True, 
                              padx=ui_config["frame_padding"], 
                              pady=ui_config["padding"])
        
        # Set up animation variables
        self.scale_segments = []
        self.pointer_x = 0.0
        self.pointer_vel = 0.0
        self.bouncing = False
        self.friction = tk.DoubleVar(value=0.99)
        self.player_colors = {}
        
        # Bind resize events
        self.scale_canvas.bind("<Configure>", self._on_scale_canvas_resize)
        
    def _on_scale_canvas_resize(self, event):
        """Handle scale canvas resize"""
        self.wheel_size = event.width
        self.wheel_height = event.height
        if self.scale_segments:
            self.draw_scale(self.scale_segments)
            
    def draw_scale(self, segs):
        """
        Draw the scale with player segments
        
        Args:
            segs: List of (player, start_percent, end_percent) tuples
        """
        self.scale_canvas.delete("all")
        w = self.wheel_size
        h = self.wheel_height
        
        # Create a modern dark background with subtle gradient
        self.scale_canvas.create_rectangle(0, 0, w, h, outline="#141414", width=3, fill="#222222")
        
        # Add a subtle pattern to background
        for i in range(0, w, 20):
            self.scale_canvas.create_line(i, 0, i, h, fill="#2a2a2a", width=1)
        
        # Create a border with gaming aesthetic
        border_width = 3
        self.scale_canvas.create_line(0, 0, w, 0, fill="#444444", width=border_width)
        self.scale_canvas.create_line(0, h, w, h, fill="#444444", width=border_width)
        self.scale_canvas.create_line(0, 0, 0, h, fill="#444444", width=border_width)
        self.scale_canvas.create_line(w, 0, w, h, fill="#444444", width=border_width)
        
        # Add corner accents for gaming look
        corner_size = 15
        self.scale_canvas.create_line(0, 0, corner_size, 0, fill="#00aaff", width=border_width)
        self.scale_canvas.create_line(0, 0, 0, corner_size, fill="#00aaff", width=border_width)
        self.scale_canvas.create_line(w, 0, w-corner_size, 0, fill="#00aaff", width=border_width)
        self.scale_canvas.create_line(w, 0, w, corner_size, fill="#00aaff", width=border_width)
        self.scale_canvas.create_line(0, h, corner_size, h, fill="#00aaff", width=border_width)
        self.scale_canvas.create_line(0, h, 0, h-corner_size, fill="#00aaff", width=border_width)
        self.scale_canvas.create_line(w, h, w-corner_size, h, fill="#00aaff", width=border_width)
        self.scale_canvas.create_line(w, h, w, h-corner_size, fill="#00aaff", width=border_width)
        
        for idx, (p, start, end) in enumerate(segs):
            x1 = (start/100) * w
            x2 = (end/100) * w
            color = self.player_colors.get(p, self._get_color(idx))
            self.player_colors[p] = color
            
            # Create a gradient effect for each segment
            gradient_steps = 20
            segment_height = h / gradient_steps
            for step in range(gradient_steps):
                # Calculate gradient color - darker at top, brighter at bottom
                brightness_factor = 0.7 + (step / gradient_steps) * 0.5
                r, g, b = self._hex_to_rgb(color)
                gradient_color = self._rgb_to_hex(
                    min(255, int(r * brightness_factor)),
                    min(255, int(g * brightness_factor)),
                    min(255, int(b * brightness_factor))
                )
                
                # Draw gradient rectangle
                y1 = step * segment_height
                y2 = (step + 1) * segment_height
                self.scale_canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill=gradient_color, 
                    outline="",
                )
            
            # Add a subtle glow effect
            glow_color = self._create_lighter_color(color, 0.3)
            self.scale_canvas.create_rectangle(
                x1, 0, x2, h,
                outline=glow_color,
                width=2,
                fill=""
            )

            # Add player name with better visibility
            cx = (x1+x2)/2
            cy = h/2
            if (x2-x1) > 20:  # Only show text if segment is wide enough
                # Get font settings from config, with fallbacks
                font_type = self.wheel_font_type
                font_size = self.wheel_font_size
                
                # Create text with multiple outlines for better visibility
                # This approach avoids the black rectangle issue while keeping rotation
                outline_offsets = [
                    (-1, -1), (0, -1), (1, -1),
                    (-1, 0),           (1, 0),
                    (-1, 1),  (0, 1),  (1, 1)
                ]
                
                # Create text outline first (black outline)
                for dx, dy in outline_offsets:
                    self.scale_canvas.create_text(
                        cx+dx, cy+dy,
                        text=p,
                        font=(font_type, font_size, "bold"),
                        fill="#000000",
                        angle=90  # Add rotation back
                    )
                
                # Create main text on top
                self.scale_canvas.create_text(
                    cx, cy,
                    text=p,
                    font=(font_type, font_size, "bold"),
                    fill="#ffffff",
                    angle=90  # Add rotation back
                )
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, r, g, b):
        """Convert RGB to hex color"""
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _create_lighter_color(self, hex_color, factor=0.2):
        """Create a lighter version of the color"""
        r, g, b = self._hex_to_rgb(hex_color)
        return self._rgb_to_hex(
            min(255, int(r + (255 - r) * factor)),
            min(255, int(g + (255 - g) * factor)),
            min(255, int(b + (255 - b) * factor))
        )
    
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
    
    def clear(self):
        """Clear the wheel display"""
        self.scale_canvas.delete("all")
        self.scale_segments = []
        self.player_colors = {}
    
    def build_segments(self, probs, player_colors=None):
        """
        Build segments for wheel based on probabilities
        
        Args:
            probs: Dict of {player: probability}
            player_colors: Dict of {player: color} (optional)
            
        Returns:
            list: List of (player, start_percent, end_percent) tuples
        """
        segs = []
        current = 0.0
        
        # Update player colors if provided
        if player_colors:
            self.player_colors = player_colors.copy()
            
        for p, val in probs.items():
            width = val * 100.0
            segs.append((p, current, current+width))
            current += width
        
        self.scale_segments = segs
        return segs
    
    def draw_pointer(self):
        """Draw the pointer on wheel during spin"""
        w = self.scale_canvas.winfo_width()
        h = self.scale_canvas.winfo_height()
        px = (self.pointer_x/100) * w
        
        # Draw glowing effect behind pointer - using solid colors
        glow_width = 8
        glow_colors = ["#99ddff", "#66ccff", "#33bbff"]  # Increasingly brighter blue
        for i, color in enumerate(glow_colors):
            width = glow_width - i*2
            self.scale_canvas.create_line(
                px, 0, px, h, 
                width=width+4, 
                fill=color
            )
        
        # Draw pointer with modern style
        pointer_width = 4
        pointer_color = "#00aaff"
        self.scale_canvas.create_line(
            px, 0, px, h, 
            width=pointer_width, 
            fill=pointer_color
        )
        
        # Draw pointer head (triangle)
        arrow_size = 12
        self.scale_canvas.create_polygon(
            px-arrow_size, 0,
            px+arrow_size, 0,
            px, arrow_size*1.5,
            fill=pointer_color,
            outline="#ffffff",
            width=1
        )
        
        # Draw pointer base
        self.scale_canvas.create_rectangle(
            px-arrow_size, h-arrow_size*1.5,
            px+arrow_size, h,
            fill=pointer_color,
            outline="#ffffff",
            width=1
        )
    
    def spin(self, callback_on_finish=None):
        """
        Start spinning animation
        
        Args:
            callback_on_finish: Callback when spin completes with x_position
        """
        if not self.scale_segments:
            return False
            
        self.pointer_x = random.uniform(0, 100)
        self.pointer_vel = random.uniform(-5, 5)
        if abs(self.pointer_vel) < 1:
            self.pointer_vel = 5 if self.pointer_vel >= 0 else -5

        self.bouncing = True
        self._callback_on_finish = callback_on_finish
        self._update_bounce()
        return True
    
    def _update_bounce(self):
        """Update pointer animation during spin"""
        if not self.bouncing:
            return
            
        friction = self.friction.get()
        self.pointer_x += self.pointer_vel
        
        if self.pointer_x < 0:
            self.pointer_x = abs(self.pointer_x)
            self.pointer_vel = -self.pointer_vel
        elif self.pointer_x > 100:
            excess = self.pointer_x - 100
            self.pointer_x = 100 - excess
            self.pointer_vel = -self.pointer_vel

        self.pointer_vel *= friction
        self.draw_scale(self.scale_segments)
        self.draw_pointer()

        if abs(self.pointer_vel) < 0.2:
            self.bouncing = False
            if self._callback_on_finish:
                self._callback_on_finish(self.pointer_x)
        else:
            self.parent.after(20, self._update_bounce)
    
    def display_winner(self, player_name, color=None):
        """
        Display the winner after spin completes
        
        Args:
            player_name: Name of the winning player
            color: Color to use for highlight (or None to use player's color)
        """
        self.scale_canvas.delete("all")
        w = int(self.scale_canvas.winfo_width())
        h = int(self.scale_canvas.winfo_height())
        display_color = color if color else self.player_colors.get(player_name, "red")
        
        # Create a background with gaming aesthetic
        self.scale_canvas.create_rectangle(0, 0, w, h, fill="#222222", outline="#444444", width=3)
        
        # Add diagonal lines for a tech/gaming look
        for i in range(-h, w+h, 40):
            self.scale_canvas.create_line(i, 0, i+h, h, fill="#333333", width=1)
        
        # Create glowing border
        border_width = 3
        glow_colors = ["#66ccff", "#33aaff", "#0088cc"]  # Solid colors instead of transparent
        for i, glow_color in enumerate(glow_colors):
            padding = (i+1) * 3
            self.scale_canvas.create_rectangle(
                padding, padding, 
                w-padding, h-padding, 
                outline=glow_color, 
                width=border_width
            )
        
        # Create a highlight box for the player name
        box_width = min(w * 0.8, 400)
        box_height = min(h * 0.6, 100)
        box_x = w/2 - box_width/2
        box_y = h/2 - box_height/2
        
        # Draw the background box with gradient
        gradient_steps = 20
        step_height = box_height / gradient_steps
        r, g, b = self._hex_to_rgb(display_color)
        
        for step in range(gradient_steps):
            # Calculate gradient color - darker at edges, brighter in center
            center_factor = 1 - abs(step - gradient_steps/2) / (gradient_steps/2)
            brightness = 0.3 + center_factor * 0.7
            
            gradient_color = self._rgb_to_hex(
                min(255, int(r * brightness)),
                min(255, int(g * brightness)),
                min(255, int(b * brightness))
            )
            
            y1 = box_y + step * step_height
            y2 = box_y + (step + 1) * step_height
            
            self.scale_canvas.create_rectangle(
                box_x, y1, box_x + box_width, y2,
                fill=gradient_color,
                outline=""
            )
        
        # Draw border for the box
        self.scale_canvas.create_rectangle(
            box_x, box_y, box_x + box_width, box_y + box_height,
            fill="",
            outline="#ffffff",
            width=2
        )
        
        # Draw corner accents
        corner_size = 15
        corners = [
            (box_x, box_y, box_x + corner_size, box_y, box_x, box_y + corner_size),
            (box_x + box_width, box_y, box_x + box_width - corner_size, box_y, box_x + box_width, box_y + corner_size),
            (box_x, box_y + box_height, box_x + corner_size, box_y + box_height, box_x, box_y + box_height - corner_size),
            (box_x + box_width, box_y + box_height, box_x + box_width - corner_size, box_y + box_height, box_x + box_width, box_y + box_height - corner_size)
        ]
        
        for x1, y1, x2, y2, x3, y3 in corners:
            self.scale_canvas.create_line(x1, y1, x2, y2, fill="#00aaff", width=3)
            self.scale_canvas.create_line(x1, y1, x3, y3, fill="#00aaff", width=3)
        
        # Create winner text with shadow for better visibility (no rotation used to avoid black box)
        text_id = self.scale_canvas.create_text(
            w/2+2, h/2+2,
            text=player_name,
            fill="#000000",
            font=(self.wheel_font_type, 
                self.wheel_font_size+6, "bold"),
            anchor="center"
        )
        
        self.scale_canvas.create_text(
            w/2, h/2,
            text=player_name,
            fill="#ffffff",
            font=(self.wheel_font_type, 
                self.wheel_font_size+6, "bold"),
            anchor="center"
        )
        
        # Add "WINNER" text
        self.scale_canvas.create_text(
            w/2, box_y - 20,
            text="WINNER",
            fill="#00aaff",
            font=(self.wheel_font_type, 
                self.wheel_font_size+4, "bold"),
            anchor="center"
        ) 