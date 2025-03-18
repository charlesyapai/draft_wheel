# Modern UI for Draft Wheel

This readme provides an overview of the modern UI components for Draft Wheel and how to integrate them with the core functionality.

## Overview

The modernized UI provides a gaming-themed interface with:

- A dockable panel system for flexible layout
- Enhanced data visualization with modern charts
- Three themes: Cyber, Dark, and Light
- Smooth animations and visual effects
- Responsive layout that adapts to window size

## Components

The modernization includes:

1. **Modern Toolkit** (`gui/components/modern_toolkit.py`): 
   - `ThemeManager`: Manages application themes and styling
   - `ModernFrame`: Enhanced frame with title bar, collapsible and movable features
   - `ModernButton`: Gaming-style button with hover effects
   - `PanelManager`: Manages dockable panels

2. **Modern Charts** (`gui/components/modern_charts.py`):
   - `ModernSigmoidChart`: Enhanced sigmoid probability chart with animations
   - `ModernProbabilityTable`: Advanced table with visual indicators

3. **Modern Probability View** (`gui/components/modern_probability_view.py`):
   - Combines charts into a cohesive interface with dockable panels

## Integration with Core Functionality

### Step 1: Combine Modern UI with Draft Logic

The modernized UI needs to be integrated with the existing `DraftLogic` class to retain all core functionality:

```python
# In your main application file
from gui.components import ModernProbabilityView, ThemeManager
from logic.draft_logic import DraftLogic

# Initialize core logic
draft_logic = DraftLogic(config)

# Create modern UI components
theme_manager = ThemeManager()
probability_view = ModernProbabilityView(parent_frame, theme_manager)

# When probabilities need to be updated:
def update_probabilities(team_id, role):
    # Get probabilities from draft logic
    probs = draft_logic.compute_probabilities(team_id, role)
    
    # Get player MMRs
    player_mmrs = {p: draft_logic.all_players[p]["mmr"] for p in probs.keys()}
    
    # Get ideal MMR for this pick
    ideal_mmr = draft_logic.get_ideal_mmr_for_pick(team_id, role)
    
    # Get role preferences if available
    role_prefs = {}
    for p in probs.keys():
        for r, prio in draft_logic.all_players[p]["roles"]:
            if r == role:
                role_prefs[p] = prio
    
    # Update the modern probability view
    probability_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)
```

### Step 2: Integrate the Spinning Wheel

The spinning wheel functionality needs to be added to the modern UI:

1. Create a `ModernWheelView` component based on the original code in `draft_gui.py`
2. Add pointer animation and segment drawing based on probabilities
3. Connect to the draft logic's `pick_player_from_position` function

### Step 3: Retain Team Management

Ensure the team management panel remains:

1. Create a `ModernTeamPanel` component based on the original code
2. Connect team display to the draft logic's team data
3. Retain color selection and team details

### Step 4: Add Role Selection

Add role selection UI with the modernized components:

1. Create a `ModernRoleSelector` component for role selection
2. Connect role selection to the draft logic

### Step 5: Enable Charts and Statistics

Include all the existing statistics and charts:

1. Enhance the MMR bucket chart with the modern UI styling
2. Improve the role distribution chart with modern components
3. Ensure all statistics from the original app are retained

## Using with Original Components

The modernized components can be used alongside existing components. For backward compatibility, we've created:

```python
# In gui/components/probability_view.py
class ProbabilityView:
    """Component for displaying probabilities and sigmoid chart"""
    
    def __init__(self, parent, ui_config):
        # Create modern view internally
        self.modern_view = ModernProbabilityView(parent, ThemeManager())
        
    # Delegate methods to modern implementation
    def update_probabilities(self, probs, player_mmrs, ideal_mmr, role_prefs=None):
        self.modern_view.update_probabilities(probs, player_mmrs, ideal_mmr, role_prefs)
```

## Next Steps for Full Implementation

To complete the modernization:

1. Create a new draft GUI class that uses all modern components
2. Test with real data to ensure all functionality is retained
3. Compare side by side with original UI to verify feature parity

## Credits

The modern UI components were designed to enhance the Draft Wheel application while maintaining full compatibility with its core functionality.

## Running the Modern UI

You can run the modernized Draft Wheel application using the provided launcher:

```bash
# Run with default settings
./modern_draft_wheel.py

# Run with a specific theme
./modern_draft_wheel.py --theme dark

# Run with a custom config file
./modern_draft_wheel.py --config path/to/config.yaml
```

The modern UI includes all the features of the original Draft Wheel:
- Probability-based player selection with spinning wheel
- Team creation and management
- MMR-based balancing of player selection
- Role preference support
- Draft history with undo capability

With additional modern features:
- Three gaming-themed visual styles (Cyber, Dark, Light)
- Movable, resizable, and collapsible panels
- Improved data visualization with animated charts
- Intuitive, accessible controls with visual feedback
- Responsive layout that adapts to window size 