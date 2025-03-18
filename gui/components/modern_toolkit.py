"""
Modern UI Toolkit
A collection of enhanced widgets and UI components for a gaming-themed interface
"""
import tkinter as tk
from typing import Dict, List, Callable

class ThemeManager:
    """Manages application themes and styling"""
    
    # Theme definitions
    THEMES = {
        "dark": {
            "name": "Cyber Dark",
            "main_bg": "#121212",
            "panel_bg": "#1E1E1E",
            "control_bg": "#252525",
            "header_bg": "#202020",
            "accent": "#0077FF",
            "accent_2": "#00CCFF", 
            "accent_hover": "#3399FF",
            "text": "#FFFFFF",
            "text_secondary": "#BBBBBB",
            "text_disabled": "#666666",
            "border": "#333333",
            "success": "#00CC66",
            "warning": "#FFBB00",
            "error": "#FF3333",
            "chart_bg": "#252525",
            "chart_grid": "#333333",
            "chart_text": "#BBBBBB",
            "team_colors": [
                "#FF5500", "#00AAFF", "#FFCC00", "#FF00AA", 
                "#00DDAA", "#AA66FF", "#FF3366", "#66BBFF"
            ],
            "app_bg": "#1E1E1E"
        },
        "light": {
            "name": "Cyber Light",
            "main_bg": "#F0F0F0",
            "panel_bg": "#FFFFFF",
            "control_bg": "#F5F5F5",
            "header_bg": "#E0E0E0",
            "accent": "#0077FF",
            "accent_2": "#00AADD",
            "accent_hover": "#3399FF",
            "text": "#111111",
            "text_secondary": "#555555",
            "text_disabled": "#999999",
            "border": "#CCCCCC",
            "success": "#00BB66",
            "warning": "#FFAA00",
            "error": "#EE3333",
            "chart_bg": "#FFFFFF",
            "chart_grid": "#DDDDDD",
            "chart_text": "#555555",
            "team_colors": [
                "#FF5500", "#0088CC", "#FFAA00", "#CC0088", 
                "#00AA88", "#8844DD", "#DD2244", "#4499DD"
            ],
            "app_bg": "#F5F5F5"
        },
        "cyber": {
            "name": "Neon Cyber",
            "main_bg": "#050510",
            "panel_bg": "#0A0A1A",
            "control_bg": "#101025",
            "header_bg": "#0D0D20",
            "accent": "#00FFAA",
            "accent_2": "#00DDFF",
            "accent_hover": "#44FFBB",
            "text": "#EEEEFF",
            "text_secondary": "#AAAACC",
            "text_disabled": "#555577",
            "border": "#222244",
            "success": "#00FF88",
            "warning": "#FFDD00",
            "error": "#FF2266",
            "chart_bg": "#101025",
            "chart_grid": "#222244",
            "chart_text": "#AAAACC",
            "team_colors": [
                "#FF00AA", "#00FFCC", "#FFDD00", "#00AAFF", 
                "#FF5500", "#AA00FF", "#00FF66", "#FF2288"
            ],
            "app_bg": "#0A1929"
        }
    }
    
    def __init__(self, initial_theme="dark"):
        """Initialize the theme manager"""
        self.current_theme = initial_theme
        self.callbacks = []
        
    def get_theme(self) -> Dict:
        """Get the current theme colors and settings"""
        return self.THEMES[self.current_theme].copy()
    
    def set_theme(self, theme_name: str):
        """Set the current theme and notify listeners"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self._notify_theme_changed()
            
    def register_listener(self, callback: Callable):
        """Register a callback to be notified when theme changes"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            
    def unregister_listener(self, callback: Callable):
        """Remove a callback from the listener list"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            
    def _notify_theme_changed(self):
        """Notify all listeners that the theme has changed"""
        for callback in self.callbacks:
            callback(self.get_theme())
            
    def generate_gradient_colors(self, start_color: str, end_color: str, steps: int) -> List[str]:
        """Generate a gradient between two colors"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return f'#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}'
        
        start_rgb = hex_to_rgb(start_color)
        end_rgb = hex_to_rgb(end_color)
        
        result = []
        for step in range(steps):
            factor = step / (steps - 1)
            r = start_rgb[0] + factor * (end_rgb[0] - start_rgb[0])
            g = start_rgb[1] + factor * (end_rgb[1] - start_rgb[1])
            b = start_rgb[2] + factor * (end_rgb[2] - start_rgb[2])
            result.append(rgb_to_hex((r, g, b)))
            
        return result


class ModernFrame(tk.Frame):
    """A modern, gaming-themed frame with title bar and customizable controls"""
    
    def __init__(self, parent, title="", theme_manager=None, 
                 collapsible=False, movable=False, 
                 width=None, height=None):
        """
        Initialize a modern frame with gaming-style visuals
        
        Args:
            parent: Parent widget
            title: Title for the frame
            theme_manager: ThemeManager instance
            collapsible: Whether the frame is collapsible
            movable: Whether the frame is movable
            width: Optional width override
            height: Optional height override
        """
        self.theme_manager = theme_manager or ThemeManager()
        self.theme = self.theme_manager.get_theme()
        
        # Set frame properties
        bg_color = self.theme["panel_bg"]
        
        # Initialize frame
        tk.Frame.__init__(
            self, parent, 
            bg=bg_color, 
            highlightbackground=self.theme["accent"],
            highlightthickness=1
        )
        
        # Set dimensions if provided
        if width:
            self.configure(width=width)
        if height:
            self.configure(height=height)
        
        # Store properties
        self.title_text = title
        self.is_collapsible = collapsible
        self.is_movable = movable
        self.collapsed = False
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Create title bar
        self._create_title_bar()
        
        # Create content frame
        self.content_frame = tk.Frame(self, bg=bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))
        
        # Register for theme changes
        self.theme_manager.register_listener(self._on_theme_changed)
        
    def _create_title_bar(self):
        """Create the title bar with controls"""
        # Title bar frame
        bar_height = 30
        title_bar_bg = self.theme["header_bg"]
        title_bar_fg = self.theme["text"]
        
        self.title_bar = tk.Frame(
            self, 
            bg=title_bar_bg, 
            height=bar_height
        )
        self.title_bar.pack(fill=tk.X, padx=1, pady=(1, 0))
        
        # Make sure title bar maintains its height
        self.title_bar.pack_propagate(False)
        
        # Title label
        title_font = ("Segoe UI", 10, "bold")
        self.title_label = tk.Label(
            self.title_bar,
            text=self.title_text,
            bg=title_bar_bg,
            fg=title_bar_fg,
            font=title_font
        )
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Make title bar draggable if movable
        if self.is_movable:
            self.title_bar.bind("<Button-1>", self._on_drag_start)
            self.title_bar.bind("<B1-Motion>", self._on_drag_motion)
            self.title_label.bind("<Button-1>", self._on_drag_start)
            self.title_label.bind("<B1-Motion>", self._on_drag_motion)
        
        # Add collapse button if collapsible
        if self.is_collapsible:
            # Add padding frame
            padding = tk.Frame(self.title_bar, bg=title_bar_bg, width=10)
            padding.pack(side=tk.RIGHT)
            
            # Create collapse button
            btn_size = 16
            self.collapse_btn = tk.Canvas(
                self.title_bar,
                width=btn_size,
                height=btn_size,
                bg=title_bar_bg,
                highlightthickness=0
            )
            self.collapse_btn.pack(side=tk.RIGHT, padx=5, pady=(bar_height-btn_size)//2)
            
            # Draw collapse arrow
            self.draw_collapse_button()
            
            # Bind click event
            self.collapse_btn.bind("<Button-1>", self._toggle_collapse)
    
    def draw_collapse_button(self):
        """Draw the collapse/expand button"""
        self.collapse_btn.delete("all")
        
        # Get button size
        btn_size = self.collapse_btn.winfo_reqwidth()
        
        # Draw circle background
        bg_color = self.theme.get("accent", "#0077FF")
        self.collapse_btn.create_oval(
            1, 1, btn_size-1, btn_size-1,
            fill=bg_color, outline=""
        )
        
        # Draw arrow (down when expanded, right when collapsed)
        arrow_color = "white"
        if self.collapsed:
            # Right-facing arrow (collapsed)
            points = [
                btn_size//3, btn_size//4,
                btn_size//3, 3*btn_size//4,
                2*btn_size//3, btn_size//2
            ]
        else:
            # Down-facing arrow (expanded)
            points = [
                btn_size//4, btn_size//3,
                3*btn_size//4, btn_size//3,
                btn_size//2, 2*btn_size//3
            ]
            
        self.collapse_btn.create_polygon(
            points, fill=arrow_color, outline=""
        )
    
    def _toggle_collapse(self, event=None):
        """Toggle frame between collapsed and expanded states"""
        if self.collapsed:
            # Expand
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))
            if hasattr(self, "title_bar"):
                # Find the collapse button and update its appearance
                self.draw_collapse_button()
            self.collapsed = False
        else:
            # Collapse
            self.content_frame.pack_forget()
            if hasattr(self, "title_bar"):
                # Find the collapse button and update its appearance
                self.draw_collapse_button()
            self.collapsed = True
            
    def _on_drag_start(self, event):
        """Start moving the frame"""
        if not self.is_movable:
            return
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def _on_drag_motion(self, event):
        """Handle frame movement"""
        if not self.is_movable:
            return
        x = self.winfo_x() - self._drag_start_x + event.x
        y = self.winfo_y() - self._drag_start_y + event.y
        self.place(x=x, y=y)
        
    def _on_drag_stop(self, event):
        """Stop moving the frame"""
        if not self.is_movable:
            return
        
    def _on_theme_changed(self, theme):
        """Handle theme changes"""
        self.theme = theme
        bg_color = theme["panel_bg"]
        self.configure(bg=bg_color)
        self.content_frame.configure(bg=bg_color)
        
        if hasattr(self, "title_bar"):
            self.title_bar.configure(bg=theme["header_bg"])
            self.title_label.configure(bg=theme["header_bg"], fg=theme["text"])
            
            # Update collapse button if present
            if self.is_collapsible and hasattr(self, "collapse_btn"):
                self.collapse_btn.configure(bg=theme["header_bg"])
                self.draw_collapse_button()
        
        # Update border color
        self.configure(highlightbackground=theme["accent"])


class ModernButton(tk.Canvas):
    """A modern, gaming-style button with hover effects"""
    
    def __init__(self, parent, text="Button", command=None, 
                theme_manager=None, width=None, height=None,
                size="medium", active=True):
        """
        Initialize a modern button with gaming-style visuals
        
        Args:
            parent: Parent widget
            text: Button text
            command: Callback function
            theme_manager: ThemeManager instance
            width: Optional width override
            height: Optional height override
            size: Button size ("small", "medium", "large")
            active: Whether button is initially active
        """
        self.theme_manager = theme_manager or ThemeManager()
        self.theme = self.theme_manager.get_theme()
        
        # Store properties
        self.text = text
        self.command = command
        self.active = active
        self.hovered = False
        self.highlighted = False
        
        # Font configuration
        # Check for font settings in theme manager
        self.font_config = self.theme.get("fonts", {}).get("buttons", {})
        
        # Set size based on preset
        if size == "small":
            btn_width = width or 100
            btn_height = height or 28
            self.font_size = self.font_config.get("small", 9)
            self.font_family = self.font_config.get("family", "Segoe UI")
        elif size == "large":
            btn_width = width or 150
            btn_height = height or 40
            self.font_size = self.font_config.get("large", 12)
            self.font_family = self.font_config.get("family", "Segoe UI")
        else:  # medium
            btn_width = width or 120
            btn_height = height or 36
            self.font_size = self.font_config.get("medium", 10)
            self.font_family = self.font_config.get("family", "Segoe UI")
        
        # Initialize canvas with proper parent
        tk.Canvas.__init__(
            self,
            parent,
            width=btn_width,
            height=btn_height,
            bg=parent["bg"],
            highlightthickness=0
        )
        
        # Create button shape
        self._draw_button()
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        
        # Register for theme changes
        self.theme_manager.register_listener(self._on_theme_changed)

    def set_highlighted(self, highlighted=True):
        """Set whether the button should be highlighted as selected"""
        if self.highlighted != highlighted:
            self.highlighted = highlighted
            self._draw_button()
            
    def _draw_button(self):
        """Draw the button with current state"""
        # Clear canvas
        self.delete("all")
        
        # Get dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Adjust if dimensions are not available yet
        if width <= 1:
            width = self.winfo_reqwidth()
        if height <= 1:
            height = self.winfo_reqheight()
        
        # Get colors based on state
        if not self.active:
            bg_color = self.theme.get("control_bg", "#CCCCCC")
            text_color = self.theme.get("text_disabled", "#888888")
        elif self.highlighted:
            bg_color = self.theme.get("success", "#00AA00")
            text_color = "white"
        elif self.hovered:
            bg_color = self.theme.get("accent_hover", "#3399FF")
            text_color = "white"
        else:
            bg_color = self.theme.get("accent", "#0077FF")
            text_color = "white"
        
        # Create rounded rectangle for button
        corner_radius = min(height // 2, 10)
        
        # Add roundrectangle method to Canvas if not present
        if not hasattr(tk.Canvas, 'create_roundrectangle'):
            tk.Canvas.create_roundrectangle = _create_roundrectangle
            
        self.create_roundrectangle(
            2, 2, width-2, height-2,
            radius=corner_radius,
            fill=bg_color,
            outline=""
        )
        
        # Add glow effect when hovered or highlighted and active
        if (self.hovered or self.highlighted) and self.active:
            self.create_roundrectangle(
                4, 4, width-4, height-4,
                radius=corner_radius-2,
                fill="",
                outline="white",
                width=1
            )
        
        # Button text
        font_weight = "bold"
        self.create_text(
            width//2, height//2,
            text=self.text,
            fill=text_color,
            font=(self.font_family, self.font_size, font_weight)
        )

    def _on_enter(self, event):
        """Handle mouse enter event"""
        if not self.active:
            return
            
        self.hovered = True
        self._draw_button()
        
    def _on_leave(self, event):
        """Handle mouse leave event"""
        if not self.active:
            return
            
        self.hovered = False
        self._draw_button()
        
    def _on_click(self, event):
        """Handle mouse click event"""
        if not self.active:
            return
            
        self.command()
        
    def _on_theme_changed(self, theme):
        """Handle theme changes"""
        self.theme = theme
        self._draw_button()

    def set_state(self, state):
        """Set button state (normal, disabled)"""
        if state not in ("normal", "disabled"):
            return
            
        active = (state == "normal")
        if self.active != active:
            self.active = active
            self._draw_button()


# Add missing roundrectangle method to Canvas
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

# Add method to Canvas class
tk.Canvas.create_roundrectangle = _create_roundrectangle


class ModernChart:
    """Base class for modern charts with animation support"""
    
    def __init__(self, canvas, theme_manager=None):
        """
        Initialize chart base class
        
        Args:
            canvas: Canvas widget to draw on
            theme_manager: ThemeManager instance
        """
        self.canvas = canvas
        self.theme_manager = theme_manager
        self.theme = theme_manager.get_theme() if theme_manager else None
        
        # Animation settings
        self.animation_speed = 300  # ms
        self.animation_active = False
        self.animation_frames = 20
        
        # Register for theme changes
        if theme_manager:
            theme_manager.register_listener(self.on_theme_changed)
    
    def clear(self):
        """Clear the chart canvas"""
        self.canvas.delete("all")
        
    def on_theme_changed(self, theme):
        """Handle theme changes"""
        self.theme = theme
        self.redraw()
        
    def redraw(self):
        """Redraw the chart with current data"""
        pass
    
    def animate(self, from_values, to_values, callback):
        """
        Animate transition between values
        
        Args:
            from_values: Starting values
            to_values: Ending values
            callback: Function to call with interpolated values
        """
        if self.animation_active:
            return
            
        self.animation_active = True
        self.animation_current_frame = 0
        self.animation_from = from_values
        self.animation_to = to_values
        self.animation_callback = callback
        
        self._animate_step()
        
    def _animate_step(self):
        """Perform one step of animation"""
        if not self.animation_active:
            return
            
        progress = self.animation_current_frame / self.animation_frames
        
        # Calculate interpolated values
        interpolated = []
        for i in range(len(self.animation_from)):
            from_val = self.animation_from[i]
            to_val = self.animation_to[i]
            current = from_val + (to_val - from_val) * progress
            interpolated.append(current)
            
        # Call callback with interpolated values
        self.animation_callback(interpolated)
        
        # Next frame or finish
        self.animation_current_frame += 1
        if self.animation_current_frame <= self.animation_frames:
            self.canvas.after(int(self.animation_speed / self.animation_frames), self._animate_step)
        else:
            self.animation_active = False
            
    def _draw_grid(self, x_min, y_min, x_max, y_max, x_steps, y_steps):
        """
        Draw a grid on the chart
        
        Args:
            x_min, y_min: Lower bounds of grid area
            x_max, y_max: Upper bounds of grid area
            x_steps, y_steps: Number of grid lines
        """
        grid_color = self.theme["chart_grid"] if self.theme else "#DDDDDD"
        
        # Draw horizontal grid lines
        for i in range(y_steps + 1):
            y = y_min + (y_max - y_min) * (i / y_steps)
            self.canvas.create_line(
                x_min, y, x_max, y,
                fill=grid_color, width=1, dash=(4, 4)
            )
            
        # Draw vertical grid lines
        for i in range(x_steps + 1):
            x = x_min + (x_max - x_min) * (i / x_steps)
            self.canvas.create_line(
                x, y_min, x, y_max,
                fill=grid_color, width=1, dash=(4, 4)
            )


# Panel Manager for dockable/movable panels
class PanelManager:
    """Manages dockable panels in the application"""
    
    def __init__(self):
        """Initialize the panel manager"""
        self.panels = {}
        self.visible_panels = set()
    
    def register_panel(self, panel_id, panel_widget):
        """
        Register a panel with the manager
        
        Args:
            panel_id: Unique identifier for the panel
            panel_widget: The panel widget
        """
        self.panels[panel_id] = panel_widget
        self.visible_panels.add(panel_id)
    
    def get_panel(self, panel_id):
        """
        Get a panel by its ID
        
        Args:
            panel_id: Panel identifier
            
        Returns:
            Panel widget or None if not found
        """
        return self.panels.get(panel_id)
    
    def toggle_panel(self, panel_id):
        """
        Toggle panel visibility
        
        Args:
            panel_id: Panel identifier
        """
        panel = self.get_panel(panel_id)
        if not panel:
            return
            
        if panel_id in self.visible_panels:
            panel.place_forget()
            self.visible_panels.remove(panel_id)
        else:
            # Restore panel (will use last place coordinates)
            panel.place(panel.place_info())
            self.visible_panels.add(panel_id)
    
    def show_panel(self, panel_id):
        """
        Show a panel
        
        Args:
            panel_id: Panel identifier
        """
        panel = self.get_panel(panel_id)
        if not panel or panel_id in self.visible_panels:
            return
            
        panel.place(panel.place_info())
        self.visible_panels.add(panel_id)
    
    def hide_panel(self, panel_id):
        """
        Hide a panel
        
        Args:
            panel_id: Panel identifier
        """
        panel = self.get_panel(panel_id)
        if not panel or panel_id not in self.visible_panels:
            return
            
        panel.place_forget()
        self.visible_panels.remove(panel_id)
