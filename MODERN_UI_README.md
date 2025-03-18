# Modern UI Components for Draft Wheel

This document explains the modern UI enhancements added to the Draft Wheel application.

## Overview

The Draft Wheel UI has been modernized with a gaming-themed design system that includes:

1. **Flexible, Movable Panels** - Components can be moved, resized, collapsed, and toggled
2. **Theme System** - Multiple themes with cyberpunk and gaming aesthetics
3. **Enhanced Charts** - Modern data visualizations with animations and sleek design
4. **Responsive Layout** - UI adapts to different window sizes

## Using the Modern UI

### Testing the UI

To test the modern UI components, run:

```bash
python test_modern_ui.py
```

This will launch a test application showing the modern probability view with random data.

### Theme Switching

The UI supports three built-in themes:

- **Cyber** - Neon blue/green on a dark background (default)
- **Dark** - Modern dark mode with blue accent
- **Light** - Light mode for high contrast environments

You can switch themes using the theme buttons in the test application, or programmatically:

```python
# Create a theme manager and set the theme
theme_manager = ThemeManager("cyber")  # or "dark" or "light"

# To change the theme later:
theme_manager.set_theme("dark")
```

### Movable Panels

Panels can be:

1. **Moved** - Drag the title bar to move a panel
2. **Collapsed** - Click the arrow in the title bar to collapse/expand
3. **Repositioned** - Move between left, center, and right areas
4. **Toggled** - Hide/show panels as needed

### Integration with Existing Code

The modernized UI maintains backward compatibility. The original `ProbabilityView` class 
now delegates to the new `ModernProbabilityView` class, so no changes are required for existing code.

## Component Reference

### ModernProbabilityView

Main component that displays probability data with a movable panel system.

```python
from gui.components import ModernProbabilityView, ThemeManager

# Create a theme manager
theme_manager = ThemeManager("cyber")

# Create the modern view
modern_view = ModernProbabilityView(parent_widget, theme_manager)

# Update with data
modern_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)
```

### ThemeManager

Manages application themes and provides colors to components.

```python
from gui.components import ThemeManager

# Create with initial theme
theme_manager = ThemeManager("cyber")  # or "dark" or "light"

# Get theme colors
colors = theme_manager.get_theme()
print(colors["accent"])  # Access a specific color

# Change theme
theme_manager.set_theme("dark")

# Listen for theme changes
def on_theme_changed(new_theme):
    print(f"Theme changed to: {new_theme['name']}")

theme_manager.register_listener(on_theme_changed)
```

### ModernFrame

Enhanced frame with title bar, collapsible support, and move capability.

```python
from gui.components import ModernFrame, ThemeManager

theme_manager = ThemeManager()
frame = ModernFrame(
    parent_widget, 
    theme_manager=theme_manager,
    title="My Panel",  # Optional title bar
    collapsible=True,  # Can be collapsed with title bar button
    movable=True,      # Can be dragged by title bar
    border_effect=True # Show border effect
)
```

### ModernButton

Modern button with hover effects and theme support.

```python
from gui.components import ModernButton, ThemeManager

theme_manager = ThemeManager()
button = ModernButton(
    parent_widget,
    text="Click me",
    command=lambda: print("Clicked!"),
    theme_manager=theme_manager,
    size="medium"  # "small", "medium", or "large"
)
```

## Customization

### Adding New Themes

You can create custom themes by adding entries to the `THEMES` dictionary in `ThemeManager`:

```python
ThemeManager.THEMES["my_theme"] = {
    "name": "My Custom Theme",
    "main_bg": "#000000",
    "panel_bg": "#111111",
    # ... other colors ...
}
```

Or by adding theme overrides to the `THEME_OVERRIDES` dictionary in `config.py`.

### Configuration Options

The modern UI respects the configuration in `gui/config.py`, which includes:

- Font settings
- Color scheme
- Animation settings
- Layout dimensions

## Technical Details

The modernization uses pure Tkinter for compatibility, with the following enhancements:

1. Custom canvas-based widgets for modern effects
2. Animation system for smooth transitions
3. Theme system with observer pattern for updates
4. Panel manager for dockable UI components 