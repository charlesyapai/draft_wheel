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
        self.scale_canvas.create_rectangle(0, 0, w, h, outline="black", width=2, fill="white")
        
        for idx, (p, start, end) in enumerate(segs):
            x1 = (start/100) * w
            x2 = (end/100) * w
            color = self.player_colors.get(p, self._get_color(idx))
            self.player_colors[p] = color
            self.scale_canvas.create_rectangle(x1, 0, x2, h, fill=color, outline="")

            cx = (x1+x2)/2
            cy = h/2
            if (x2-x1) > 20:  # Only show text if segment is wide enough
                self.scale_canvas.create_text(cx, cy,
                                          text=p,
                                          font=(self.ui_config["text_font_type"], 
                                                self.ui_config["text_font_size"], "bold"),
                                          fill="black",
                                          angle=90)
    
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
    
    def build_segments(self, probs):
        """
        Build segments for wheel based on probabilities
        
        Args:
            probs: Dict of {player: probability}
            
        Returns:
            list: List of (player, start_percent, end_percent) tuples
        """
        segs = []
        current = 0.0
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
        self.scale_canvas.create_line(px, 0, px, h, width=4, 
                                    fill=self.ui_config["pointer_color"])
    
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
        w = int(self.scale_canvas.winfo_width()/2)
        h = int(self.scale_canvas.winfo_height()/2)
        display_color = color if color else self.player_colors.get(player_name, "red")
        
        text_id = self.scale_canvas.create_text(
            w, h,
            text=player_name,
            fill="black",
            font=(self.ui_config["text_font_type"], 
                 self.ui_config["text_font_size"]+6, "bold"),
            anchor="center"
        )
        
        bbox = self.scale_canvas.bbox(text_id)
        if bbox:
            rect_id = self.scale_canvas.create_rectangle(bbox, 
                                                       fill=display_color, 
                                                       outline="")
            self.scale_canvas.tag_raise(text_id, rect_id) 