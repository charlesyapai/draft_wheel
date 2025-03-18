"""
Modern Wheel Component
A modernized, animated wheel for the Draft Wheel application
"""
import random

class ModernWheel:
    """A modern animated wheel component for the draft process"""
    
    def __init__(self, canvas, theme_manager=None, friction=0.99):
        """
        Initialize the modern wheel
        
        Args:
            canvas: Canvas widget to draw on
            theme_manager: ThemeManager instance for theming
            friction: Friction coefficient for animation (0-1)
        """
        self.canvas = canvas
        self.theme_manager = theme_manager
        self.theme = theme_manager.get_theme() if theme_manager else None
        
        # Wheel state
        self.segments = []  # [(player_name, start_pct, end_pct), ...]
        self.pointer_x = 0.0
        self.pointer_vel = 0.0
        self.bouncing = False
        self.friction = friction
        
        # Callback when spin ends
        self.on_spin_complete = None
        
        # Animation frame reference
        self.animation_frame = None
        
        # Colors for segments
        self.player_colors = {}
        
        # Register for theme changes
        if theme_manager:
            theme_manager.register_listener(self.on_theme_changed)
        
        # Bind resize event
        self.canvas.bind("<Configure>", self._on_resize)
    
    def _on_resize(self, event):
        """Handle canvas resize"""
        if self.segments:
            self.draw_wheel(self.segments)
    
    def on_theme_changed(self, theme):
        """Handle theme changes"""
        self.theme = theme
        if self.segments:
            self.draw_wheel(self.segments)
    
    def draw_wheel(self, segments):
        """
        Draw the wheel segments
        
        Args:
            segments: List of (player_name, start_pct, end_pct) tuples
        """
        self.canvas.delete("wheel")
        if not segments:
            return
        
        self.segments = segments
        
        # Get dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # If canvas is too small, skip drawing
        if width < 50 or height < 50:
            return
        
        # Get colors from theme
        bg_color = self.theme["panel_bg"] if self.theme else "#F0F0F0"
        text_color = self.theme["text"] if self.theme else "#333333"
        accent_color = self.theme["accent"] if self.theme else "#0077FF"
        
        # Draw segments
        segment_height = height * 0.7
        y_offset = (height - segment_height) / 2
        
        for player, start_pct, end_pct in segments:
            # Calculate segment position
            x1 = width * (start_pct / 100.0)
            x2 = width * (end_pct / 100.0)
            y1 = y_offset
            y2 = y_offset + segment_height
            
            # Get color for player
            color = self.player_colors.get(player, accent_color)
            
            # Draw segment
            segment_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline="white",
                width=1,
                tags=("wheel", f"segment_{player}")
            )
            
            # Calculate segment width
            seg_width = x2 - x1
            
            # Only show text if segment is wide enough
            if seg_width > 40:
                # Create text label
                self.canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=player,
                    fill="white",
                    font=("Segoe UI", 9, "bold"),
                    tags=("wheel", f"text_{player}"),
                    anchor="center"
                )
        
        # Draw probability scale indicators
        for i in range(0, 101, 10):
            x = width * (i / 100.0)
            
            # Draw tick
            self.canvas.create_line(
                x, y_offset - 5, x, y_offset,
                fill=text_color,
                width=1,
                tags=("wheel", "ticks")
            )
            
            # Add label for 0, 50, 100
            if i in (0, 50, 100):
                self.canvas.create_text(
                    x, y_offset - 15,
                    text=f"{i}%",
                    fill=text_color,
                    font=("Segoe UI", 8),
                    tags=("wheel", "labels")
                )
        
        # Draw pointer if wheel is spinning
        if self.bouncing:
            self.draw_pointer()
    
    def draw_pointer(self):
        """Draw the spinning pointer"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Calculate pointer position
        px = width * (self.pointer_x / 100.0)
        
        # Remove old pointer
        self.canvas.delete("pointer")
        
        # Get pointer color from theme
        pointer_color = self.theme["warning"] if self.theme else "#FF5500"
        
        # Draw pointer line
        self.canvas.create_line(
            px, 0, px, height,
            width=3,
            fill=pointer_color,
            tags=("wheel", "pointer")
        )
        
        # Add glow effect
        glow_width = 7
        for i in range(1, 4):
            alpha = 0.3 - (i * 0.1)
            glow_color = self._create_alpha_color(pointer_color, alpha)
            self.canvas.create_line(
                px - i, 0, px - i, height,
                width=glow_width,
                fill=glow_color,
                tags=("wheel", "pointer", "glow")
            )
            self.canvas.create_line(
                px + i, 0, px + i, height,
                width=glow_width,
                fill=glow_color,
                tags=("wheel", "pointer", "glow")
            )
        
        # Ensure pointer is on top
        self.canvas.tag_raise("pointer", "wheel")
    
    def _create_alpha_color(self, hex_color, alpha):
        """Create a color with alpha (simulated for tkinter)"""
        # For tkinter we'll just blend with background
        if not hex_color.startswith('#'):
            return hex_color
            
        # Parse hex color
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Get background color
        bg_color = self.theme["panel_bg"] if self.theme else "#F0F0F0"
        bg_color = bg_color.lstrip('#')
        bg_r = int(bg_color[0:2], 16)
        bg_g = int(bg_color[2:4], 16)
        bg_b = int(bg_color[4:6], 16)
        
        # Blend
        blend_r = int(r * alpha + bg_r * (1 - alpha))
        blend_g = int(g * alpha + bg_g * (1 - alpha))
        blend_b = int(b * alpha + bg_b * (1 - alpha))
        
        return f'#{blend_r:02x}{blend_g:02x}{blend_b:02x}'
    
    def set_player_colors(self, colors):
        """
        Set player colors for wheel segments
        
        Args:
            colors: Dict of {player: color}
        """
        self.player_colors = colors.copy()
        
        # Redraw wheel if already displayed
        if self.segments:
            self.draw_wheel(self.segments)
    
    def clear(self):
        """Clear the wheel"""
        self.canvas.delete("all")
        self.segments = []
        
        # Cancel any running animations
        if self.animation_frame:
            self.canvas.after_cancel(self.animation_frame)
            self.animation_frame = None
        
        self.bouncing = False
    
    def spin(self, segments, on_complete=None):
        """
        Spin the wheel
        
        Args:
            segments: List of (player_name, start_pct, end_pct) tuples
            on_complete: Callback function when spin ends, receives selected player
        """
        if not segments:
            return
        
        # Store segments and callback
        self.segments = segments
        self.on_spin_complete = on_complete
        
        # Initialize pointer
        self.pointer_x = random.uniform(0, 100)
        self.pointer_vel = random.uniform(-5, 5)
        
        # Ensure some minimum velocity
        if abs(self.pointer_vel) < 1:
            self.pointer_vel = 5 if self.pointer_vel >= 0 else -5
            
        # Start animation
        self.bouncing = True
        self.draw_wheel(segments)
        self.update_animation()
    
    def update_animation(self):
        """Update animation frame"""
        if not self.bouncing:
            return
            
        # Update pointer position
        self.pointer_x += self.pointer_vel
        
        # Bounce off edges
        if self.pointer_x < 0:
            self.pointer_x = abs(self.pointer_x)
            self.pointer_vel = -self.pointer_vel
        elif self.pointer_x > 100:
            excess = self.pointer_x - 100
            self.pointer_x = 100 - excess
            self.pointer_vel = -self.pointer_vel
        
        # Apply friction
        self.pointer_vel *= self.friction
        
        # Redraw
        self.draw_pointer()
        
        # Check if animation is complete
        if abs(self.pointer_vel) < 0.2:
            self.bouncing = False
            self._finish_spin()
            return
        
        # Schedule next frame
        self.animation_frame = self.canvas.after(20, self.update_animation)
    
    def _finish_spin(self):
        """Handle end of spin animation"""
        # Find which segment contains the pointer
        selected_player = None
        for player, start_pct, end_pct in self.segments:
            if start_pct <= self.pointer_x < end_pct:
                selected_player = player
                break
        
        # Display selected player with highlight
        self.canvas.delete("wheel")
        
        # Get dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if selected_player:
            # Highlight selected player in center of wheel
            color = self.player_colors.get(selected_player, self.theme["accent"])
            
            # Create centered highlight box
            cx = width / 2
            cy = height / 2
            box_width = min(width * 0.7, 300)
            box_height = min(height * 0.5, 80)
            
            # Add background glow
            glow_padding = 10
            self.canvas.create_rectangle(
                cx - box_width/2 - glow_padding, 
                cy - box_height/2 - glow_padding,
                cx + box_width/2 + glow_padding, 
                cy + box_height/2 + glow_padding,
                fill=self._create_alpha_color(color, 0.3),
                outline="",
                tags="result"
            )
            
            # Add selection box
            self.canvas.create_rectangle(
                cx - box_width/2, cy - box_height/2,
                cx + box_width/2, cy + box_height/2,
                fill=color,
                outline="white",
                width=2,
                tags="result"
            )
            
            # Add player name
            self.canvas.create_text(
                cx, cy,
                text=selected_player,
                fill="white",
                font=("Segoe UI", 14, "bold"),
                tags="result"
            )
        
        # Call completion callback
        if self.on_spin_complete:
            self.on_spin_complete(selected_player)
    
    def set_friction(self, friction):
        """
        Set the friction value for animation
        
        Args:
            friction: Friction coefficient (0-1)
        """
        self.friction = max(0, min(0.999, friction))
    
    def build_segments(self, probabilities):
        """
        Build wheel segments based on probabilities
        
        Args:
            probabilities: Dict of {player: probability}
            
        Returns:
            List of (player, start_pct, end_pct) tuples
        """
        segments = []
        current = 0.0
        
        for player, prob in probabilities.items():
            width = prob * 100.0
            segments.append((player, current, current + width))
            current += width
            
        return segments 