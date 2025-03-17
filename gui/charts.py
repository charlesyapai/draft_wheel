# draft_wheel/gui/charts.py

import tkinter as tk
class MMRBucketChartView:
    """
    A separate chart class for MMR bucket distribution with improved visuals.
    Now categorizes players based on their first two prioritized roles.
    """
    def __init__(self, parent, width=500, height=150, bg="#FFFFFF", text_font=("Arial",9,"bold")):
        self.width = width
        self.height = height
        self.bg = bg
        self.text_font = text_font

        self.canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=1, highlightbackground="#CCC")
        self.canvas.pack(side=tk.BOTTOM, padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.bucket_ranges = {
            "0k-2k": (0, 2000),
            "2k-4k": (2001, 4000),
            "4k-6k": (4001, 6000),
            "6k-8k": (6001, 8000),
            "8k-10k": (8001, 10000),
            ">10k": (10001, 99999)
        }

    def draw(self, stats: dict, all_players=None, logic=None):
        self.canvas.delete("all")
        if not stats or not logic or not all_players:
            # Fall back to original drawing if we don't have logic or player data
            self._draw_original(stats)
            return

        # Recalculate player categorization based on first two prioritized roles
        recategorized_stats = self._recategorize_players(stats, all_players, logic)
        
        # background
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.bg, outline="")

        # gather data
        all_counts = []
        for bucket_key, d in recategorized_stats.items():
            total = d["core_only"] + d["support_only"] + d["mixed"]
            all_counts.append(total)
        max_count = max(all_counts) if all_counts else 1

        bar_width = 30  # Reduced from 40
        gap = 8        # Reduced from 10
        left_margin = 40
        base_line = self.height - 45  # Adjusted to make room for bottom legend
        scale_factor = (self.height - 65) / max_count if max_count > 0 else 1

        c_core = "#82AEDC"
        c_support = "#9CD08C"
        c_mixed = "#EDCE88"

        buckets_list = list(recategorized_stats.keys())
        for i, bucket_key in enumerate(buckets_list):
            x_start = left_margin + i * (3 * bar_width + gap)
            bdata = recategorized_stats[bucket_key]

            # core
            h_core = bdata["core_only"] * scale_factor
            self.canvas.create_rectangle(
                x_start, base_line - h_core,
                x_start + bar_width, base_line,
                fill=c_core, outline="black"
            )
            if bdata["core_only"] > 0:
                self.canvas.create_text(
                    x_start + bar_width / 2, base_line - h_core - 10,
                    text=str(bdata["core_only"]), font=self.text_font
                )

            # support
            x_supp = x_start + bar_width
            h_supp = bdata["support_only"] * scale_factor
            self.canvas.create_rectangle(
                x_supp, base_line - h_supp,
                x_supp + bar_width, base_line,
                fill=c_support, outline="black"
            )
            if bdata["support_only"] > 0:
                self.canvas.create_text(
                    x_supp + bar_width / 2, base_line - h_supp - 10,
                    text=str(bdata["support_only"]), font=self.text_font
                )

            # mixed
            x_mixed = x_supp + bar_width
            h_mixed = bdata["mixed"] * scale_factor
            self.canvas.create_rectangle(
                x_mixed, base_line - h_mixed,
                x_mixed + bar_width, base_line,
                fill=c_mixed, outline="black"
            )
            if bdata["mixed"] > 0:
                self.canvas.create_text(
                    x_mixed + bar_width / 2, base_line - h_mixed - 10,
                    text=str(bdata["mixed"]), font=self.text_font
                )

            # label
            self.canvas.create_text(
                x_start + 1.5 * bar_width, base_line + 15, text=bucket_key,
                font=(self.text_font[0], self.text_font[1], "bold")
            )

        # Draw legend at the bottom
        legend_y = self.height - 25
        legend_spacing = self.width / 4
        
        # Core legend
        legend_x = legend_spacing
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_core, outline="black"
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Core", anchor="w", 
            font=self.text_font
        )
        
        # Support legend
        legend_x = legend_spacing * 2
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_support, outline="black"
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Support", anchor="w", 
            font=self.text_font
        )
        
        # Mixed legend
        legend_x = legend_spacing * 3
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_mixed, outline="black"
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Mixed", anchor="w", 
            font=self.text_font
        )
            
    def _recategorize_players(self, stats, all_players, logic):
        """
        Recategorize players based on their first two prioritized roles.
        Core roles: carry, mid, offlane
        Support roles: soft_support, hard_support
        
        Now supports custom bucket ranges that may differ from the original stats keys.
        """
        bucket_ranges = self.bucket_ranges
        
        # Create new stats dictionary based on custom bucket ranges
        new_stats = {}
        for bucket in bucket_ranges.keys():
            new_stats[bucket] = {
                "core_only": 0,
                "support_only": 0,
                "mixed": 0
            }
        
        # Get already drafted players
        drafted_players = set()
        for team_data in logic.teams.values():
            for player, _ in team_data["players"]:
                drafted_players.add(player)
                
        # Define core and support roles
        core_roles = {"carry", "mid", "offlane"}
        support_roles = {"soft_support", "hard_support"}
        
        # Debug info
        print("Categorizing players by MMR buckets...")
        
        # Go through each player and categorize them
        for player_name, player_data in all_players.items():
            # Skip already drafted players
            if player_name in drafted_players:
                continue
                
            mmr = player_data["mmr"]
            roles = player_data["roles"]
            
            # Find the bucket for this player's MMR using explicit ranges
            player_bucket = None
            for bucket, (min_val, max_val) in bucket_ranges.items():
                if min_val <= mmr <= max_val:
                    player_bucket = bucket
                    break
                    
            if not player_bucket:
                print(f"Warning: Player {player_name} with MMR {mmr} doesn't fit any bucket")
                continue  # Skip if no bucket matches
                
            # Look at first two priority roles (if available)
            top_roles = sorted(roles, key=lambda x: x[1])[:2]
            if not top_roles:
                new_stats[player_bucket]["mixed"] += 1
                continue
                
            # Get role types
            role_types = [role_name for role_name, _ in top_roles]
            
            # Categorize based on role types
            is_core = all(role in core_roles for role in role_types)
            is_support = all(role in support_roles for role in role_types)
            
            if is_core:
                new_stats[player_bucket]["core_only"] += 1
                print(f"Player {player_name} (MMR {mmr}) -> {player_bucket} as Core")
            elif is_support:
                new_stats[player_bucket]["support_only"] += 1
                print(f"Player {player_name} (MMR {mmr}) -> {player_bucket} as Support")
            else:
                new_stats[player_bucket]["mixed"] += 1
                print(f"Player {player_name} (MMR {mmr}) -> {player_bucket} as Mixed")
                
        return new_stats
    def _draw_original(self, stats):
        """Fallback to original drawing method if we don't have player data"""
        # background
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.bg, outline="")

        # gather data
        all_counts = []
        for bucket_key, d in stats.items():
            total = d["core_only"] + d["support_only"] + d["mixed"]
            all_counts.append(total)
        max_count = max(all_counts) if all_counts else 1

        bar_width = 30  # Thinner bars
        gap = 8        # Smaller gap
        left_margin = 40
        base_line = self.height - 45  # Adjusted for bottom legend
        scale_factor = (self.height - 65) / max_count if max_count > 0 else 1

        c_core = "#82AEDC"
        c_support = "#9CD08C"
        c_mixed = "#EDCE88"

        buckets_list = list(stats.keys())
        for i, bucket_key in enumerate(buckets_list):
            x_start = left_margin + i * (3 * bar_width + gap)
            bdata = stats[bucket_key]

            # core
            h_core = bdata["core_only"] * scale_factor
            self.canvas.create_rectangle(
                x_start, base_line - h_core,
                x_start + bar_width, base_line,
                fill=c_core, outline="black"
            )
            if bdata["core_only"] > 0:
                self.canvas.create_text(
                    x_start + bar_width / 2, base_line - h_core - 10,
                    text=str(bdata["core_only"]), font=self.text_font
                )

            # support
            x_supp = x_start + bar_width
            h_supp = bdata["support_only"] * scale_factor
            self.canvas.create_rectangle(
                x_supp, base_line - h_supp,
                x_supp + bar_width, base_line,
                fill=c_support, outline="black"
            )
            if bdata["support_only"] > 0:
                self.canvas.create_text(
                    x_supp + bar_width / 2, base_line - h_supp - 10,
                    text=str(bdata["support_only"]), font=self.text_font
                )

            # mixed
            x_mixed = x_supp + bar_width
            h_mixed = bdata["mixed"] * scale_factor
            self.canvas.create_rectangle(
                x_mixed, base_line - h_mixed,
                x_mixed + bar_width, base_line,
                fill=c_mixed, outline="black"
            )
            if bdata["mixed"] > 0:
                self.canvas.create_text(
                    x_mixed + bar_width / 2, base_line - h_mixed - 10,
                    text=str(bdata["mixed"]), font=self.text_font
                )

            # label
            self.canvas.create_text(
                x_start + 1.5 * bar_width, base_line + 15, text=bucket_key,
                font=(self.text_font[0], self.text_font[1], "bold")
            )

        # Draw legend at the bottom
        legend_y = self.height - 25
        legend_spacing = self.width / 4
        
        # Core legend
        legend_x = legend_spacing
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_core, outline="black"
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Core", anchor="w", 
            font=self.text_font
        )
        
        # Support legend
        legend_x = legend_spacing * 2
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_support, outline="black"
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Support", anchor="w", 
            font=self.text_font
        )
        
        # Mixed legend
        legend_x = legend_spacing * 3
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_mixed, outline="black"
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Mixed", anchor="w", 
            font=self.text_font
        )


class RoleDistributionChartView:
    """
    A separate chart class for role distribution (count + avg MMR + priority breakdown).
    Shows how many players put each role at 1st, 2nd, and 3rd priority.
    """
    def __init__(self, parent, width=600, height=180, bg="#FFFFFF", text_font=("Arial",9,"bold")):
        self.width = width
        self.height = height
        self.bg = bg
        self.text_font = text_font

        self.canvas = tk.Canvas(parent, width=width, height=height, bg=bg)
        self.canvas.pack(side=tk.BOTTOM, padx=10, pady=5, fill=tk.BOTH, expand=True)

    def draw(self, stats: dict, logic=None):
        """
        stats => from logic.get_role_distribution_stats(), e.g.:
          { "carry": (count, avgMMR), "mid": (count, avgMMR), ... }
        
        Now also shows priority breakdown per role.
        """
        self.canvas.delete("all")
        if not stats:
            return
            
        # Check if we have the logic object to get priority counts
        has_priority_data = logic is not None
        
        # Calculate priority counts if we have the logic object
        priority_counts = {}
        if has_priority_data:
            priority_counts = self._get_priority_counts(logic)

        roles_list = list(stats.keys())
        counts = []
        mmrs = []
        for r in roles_list:
            c, avg = stats[r]
            counts.append(c)
            mmrs.append(avg)
        max_count = max(counts) if counts else 1
        max_mmr = max(mmrs) if mmrs else 1
        
        # Find max priority count for scaling
        max_priority_count = 1
        if has_priority_data:
            for role in roles_list:
                if role in priority_counts:
                    for prio in range(1, 4):
                        max_priority_count = max(max_priority_count, priority_counts[role].get(prio, 0))

        base_line = self.height - 45  # Adjusted for bottom legend
        bar_width = 15  # Smaller for more bars
        group_width = 120  # Wider to accommodate priority bars
        left_margin = 40
        gap = 20
        scale_count = (self.height - 65) / max_count if max_count > 0 else 1
        scale_mmr = (self.height - 65) / max_mmr if max_mmr > 0 else 1
        scale_priority = (self.height - 65) / max_priority_count if max_priority_count > 0 else 1

        color_count = "#5E81AC"
        color_mmr = "#BF616A"
        priority_colors = {
            1: "#FF9200",  # Orange for 1st priority
            2: "#FFB600",  # Lighter orange for 2nd priority
            3: "#FFDA00"   # Yellow for 3rd priority
        }

        for i, rname in enumerate(roles_list):
            c, avg = stats[rname]
            x_start = left_margin + i * (group_width + gap)

            # bar for count
            h_count = c * scale_count
            self.canvas.create_rectangle(
                x_start, base_line - h_count,
                x_start + bar_width, base_line,
                fill=color_count, outline="black"
            )
            if c > 0:
                self.canvas.create_text(
                    x_start + bar_width / 2, base_line - h_count - 10,
                    text=str(c),
                    font=self.text_font
                )

            # bar for avg MMR
            x_mmr = x_start + bar_width
            h_mmr = avg * scale_mmr
            self.canvas.create_rectangle(
                x_mmr, base_line - h_mmr,
                x_mmr + bar_width, base_line,
                fill=color_mmr, outline="black"
            )
            if avg > 0:
                self.canvas.create_text(
                    x_mmr + bar_width / 2, base_line - h_mmr - 10,
                    text=str(int(avg)),
                    font=self.text_font
                )
            
            # bars for priorities if we have the data
            if has_priority_data and rname in priority_counts:
                for prio in range(1, 4):
                    prio_count = priority_counts[rname].get(prio, 0)
                    x_prio = x_mmr + bar_width + (prio - 1) * bar_width
                    h_prio = prio_count * scale_priority
                    
                    self.canvas.create_rectangle(
                        x_prio, base_line - h_prio,
                        x_prio + bar_width, base_line,
                        fill=priority_colors[prio], outline="black"
                    )
                    
                    if prio_count > 0:
                        self.canvas.create_text(
                            x_prio + bar_width / 2, base_line - h_prio - 10,
                            text=str(prio_count),
                            font=self.text_font
                        )

            # label
            self.canvas.create_text(
                x_start + group_width / 2, base_line + 15,
                text=rname,
                font=(self.text_font[0], self.text_font[1] + 1, "bold")
            )

        # Draw legend at the bottom
        legend_y = self.height - 25
        legend_spacing = self.width / 7  # Distribute evenly with room for 5-6 items
        
        # Count legend
        legend_x = legend_spacing
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=color_count, outline="black"
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Count", anchor="w", 
            font=self.text_font
        )
        
        # MMR legend
        legend_x = legend_spacing * 2
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=color_mmr, outline="black"
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Avg MMR", anchor="w", 
            font=self.text_font
        )
        
        # Priority legends
        if has_priority_data:
            for prio in range(1, 4):
                legend_x = legend_spacing * (2 + prio)
                self.canvas.create_rectangle(
                    legend_x - 30, legend_y, 
                    legend_x - 15, legend_y + 15, 
                    fill=priority_colors[prio], outline="black"
                )
                self.canvas.create_text(
                    legend_x - 5, legend_y + 7, 
                    text=f"Prio {prio}", anchor="w", 
                    font=self.text_font
                )
                
    def _get_priority_counts(self, logic):
        """
        Calculate how many players have each role at priority 1, 2, and 3.
        Returns a nested dictionary: { role: { priority: count } }
        """
        result = {}
        
        # Initialize the dictionary structure
        for role in logic.roles:
            result[role] = {1: 0, 2: 0, 3: 0}
        
        # Get already drafted players
        drafted_players = set()
        for team_data in logic.teams.values():
            for player, _ in team_data["players"]:
                drafted_players.add(player)
        
        # Count priorities for undrafted players
        for player_name, player_data in logic.all_players.items():
            if player_name in drafted_players:
                continue
                
            for role_name, priority in player_data["roles"]:
                if role_name in result and 1 <= priority <= 3:
                    result[role_name][priority] += 1
        
        return result