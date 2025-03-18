#!/usr/bin/env python3
# example_usage.py
"""
Example usage of the modular Draft GUI
"""

import tkinter as tk
import json
import os

# Import the new modular DraftGUI
from gui.new_draft_gui import DraftGUI

# Mock draft logic class for example purposes
class DraftLogic:
    def __init__(self):
        # Example data structure for players
        self.all_players = {
            "Player1": {"mmr": 3000, "roles": [("carry", 1), ("mid", 2)]},
            "Player2": {"mmr": 3500, "roles": [("mid", 1), ("offlane", 2)]},
            "Player3": {"mmr": 2800, "roles": [("offlane", 1), ("soft_support", 2)]},
            "Player4": {"mmr": 2500, "roles": [("soft_support", 1), ("hard_support", 2)]},
            "Player5": {"mmr": 2200, "roles": [("hard_support", 1), ("carry", 3)]}
        }
        
        # Organize players by role
        self.players_by_role = {
            "carry": ["Player1"],
            "mid": ["Player2"],
            "offlane": ["Player3"],
            "soft_support": ["Player4"],
            "hard_support": ["Player5"]
        }
        
        # Team data
        self.teams = {
            "Team A": {"players": [], "average_mmr": 0},
            "Team B": {"players": [], "average_mmr": 0}
        }
        
        # Randomness settings
        self.randomness_levels = {0: 0.5, 1: 0.4, 2: 0.3, 3: 0.2, 4: 0.1}
    
    # Mock methods for the required functionality
    def get_teams_data(self):
        return self.teams
    
    def get_players_by_role(self):
        return self.players_by_role
        
    def compute_probabilities(self, team_id, role):
        # Return simple probabilities
        if role not in self.players_by_role or not self.players_by_role[role]:
            return {}
            
        players = self.players_by_role[role]
        total = len(players)
        if total == 0:
            return {}
            
        # Equal probabilities for demo
        probs = {p: 1.0/total for p in players}
        return probs
    
    def get_ideal_mmr_for_pick(self, team_id, role):
        # Return average mmr of the team as the ideal
        if team_id in self.teams:
            return 3000  # Example value
        return 0
    
    def get_pool_average_mmr(self):
        if not self.all_players:
            return 0
        total_mmr = sum(p["mmr"] for p in self.all_players.values())
        return total_mmr / len(self.all_players)
    
    def get_drafted_average_mmr(self):
        # Example calculation
        drafted_count = 0
        total_mmr = 0
        
        for team_data in self.teams.values():
            for player, _ in team_data["players"]:
                if player in self.all_players:
                    total_mmr += self.all_players[player]["mmr"]
                    drafted_count += 1
        
        return total_mmr / drafted_count if drafted_count > 0 else 0
    
    def get_mmr_bucket_stats(self):
        # Example MMR bucket data
        return {
            "0k-2k": {"total": 1, "roles": {"carry": 0, "mid": 0, "offlane": 0, "soft_support": 0, "hard_support": 1}},
            "2k-4k": {"total": 4, "roles": {"carry": 1, "mid": 1, "offlane": 1, "soft_support": 1, "hard_support": 0}},
            "4k-6k": {"total": 0, "roles": {"carry": 0, "mid": 0, "offlane": 0, "soft_support": 0, "hard_support": 0}},
            "6k+": {"total": 0, "roles": {"carry": 0, "mid": 0, "offlane": 0, "soft_support": 0, "hard_support": 0}}
        }
    
    def get_role_distribution_stats(self):
        # Example role distribution data
        return {r: len(p) for r, p in self.players_by_role.items()}
    
    def pick_player_from_position(self, team_id, role, position, segments):
        # Find the segment containing the position
        for player, start, end in segments:
            if start <= position <= end:
                # Add player to team
                if team_id in self.teams and player in self.all_players:
                    self.teams[team_id]["players"].append((player, role))
                    # Remove from available pool
                    if role in self.players_by_role and player in self.players_by_role[role]:
                        self.players_by_role[role].remove(player)
                    return player
        return None
    
    def undo_last_pick(self):
        # Simple example implementation
        for team_id, team_data in self.teams.items():
            if team_data["players"]:
                player, role = team_data["players"].pop()
                if player in self.all_players:
                    if role not in self.players_by_role:
                        self.players_by_role[role] = []
                    self.players_by_role[role].append(player)
                return player
        return None
    
    def register_team(self, team_name):
        if team_name not in self.teams:
            self.teams[team_name] = {"players": [], "average_mmr": 0}
    
    def add_captain_to_team(self, team_id, captain_name, captain_mmr):
        if team_id in self.teams:
            # Create player if not exists
            if captain_name not in self.all_players:
                self.all_players[captain_name] = {
                    "mmr": captain_mmr,
                    "roles": [("carry", 1), ("mid", 1), ("offlane", 1), 
                              ("soft_support", 1), ("hard_support", 1)]
                }
            # Add as captain
            self.teams[team_id]["players"].append((captain_name, "(Captain)"))
    
    def save_state(self, players_file, teams_file):
        # Mock implementation - would save to files in a real implementation
        print(f"[MOCK] Saving state to {players_file} and {teams_file}")
    
    def load_state(self, players_file, teams_file):
        # Mock implementation - would load from files in a real implementation
        print(f"[MOCK] Loading state from {players_file} and {teams_file}")

# Main function to run the application
def main():
    # Create a simple configuration
    config = {
        "ui_settings": {
            # Override default colors
            "main_bg_color": "#F0F0F0",
            "button_fg_color": "#0066CC",
            "button_select_color": "#FFD700"
        }
    }
    
    # Create the UI config file path
    ui_config_path = "ui_config.json"
    
    # Create example UI config file if doesn't exist
    if not os.path.exists(ui_config_path):
        from gui.config import DEFAULT_UI_CONFIG
        with open(ui_config_path, 'w') as f:
            json.dump(DEFAULT_UI_CONFIG, f, indent=2)
        
        # Point to the config file
        config["ui_config_file"] = ui_config_path
    
    # Create the draft logic
    draft_logic = DraftLogic()
    
    # Create the Tkinter root window
    root = tk.Tk()
    root.title("Draft Tool Example")
    
    # Create and initialize the GUI
    draft_gui = DraftGUI(root, config, draft_logic)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main() 