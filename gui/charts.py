# draft_wheel/gui/charts.py

import tkinter as tk
class MMRBucketChartView:
    """
    A separate chart class for MMR bucket distribution with improved visuals.
    Now categorizes players based on their first two prioritized roles.
    """
    def __init__(self, parent, width=500, height=180, bg="#1E2130", text_font=("Arial",9,"bold")):
        self.width = width
        self.height = height
        self.bg = bg
        self.text_font = text_font
        self.parent = parent

        self.canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=1, highlightbackground="#3D4663")
        self.canvas.pack(side=tk.BOTTOM, padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Bind to configure event for resizing
        self.canvas.bind("<Configure>", self._on_resize)
        
        self.bucket_ranges = {
            "0k-2k": (0, 2000),
            "2k-4k": (2001, 4000),
            "4k-6k": (4001, 6000),
            "6k-8k": (6001, 8000),
            "8k-10k": (8001, 10000),
            ">10k": (10001, 99999)
        }
        
        # Store the current data for redrawing on resize
        self.current_stats = None
        self.current_all_players = None
        self.current_logic = None

    def _on_resize(self, event):
        """Handle window resize event"""
        # Update dimensions
        self.width = event.width
        self.height = event.height
        
        # Redraw with current data if available
        if self.current_stats:
            self.draw(self.current_stats, self.current_all_players, self.current_logic)

    def draw(self, stats: dict, all_players=None, logic=None):
        # Store current data for resize events
        self.current_stats = stats
        self.current_all_players = all_players
        self.current_logic = logic
        
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

        # Calculate bar dimensions based on current canvas size
        total_buckets = len(recategorized_stats)
        bar_width = min(25, (self.width - 100) / (total_buckets * 3.5))  # Dynamic bar width
        gap = min(15, (self.width - 100) / (total_buckets * 6))  # Dynamic gap
        left_margin = self.width * 0.1  # 10% of width
        base_line = self.height - (self.height * 0.3)  # 30% from bottom
        scale_factor = (self.height - (self.height * 0.45)) / max_count if max_count > 0 else 1

        # Vibrant gamer colors with gradients
        c_core = "#4F9AFF"  # Bright blue
        c_support = "#5CFF5C"  # Bright green
        c_mixed = "#FFC857"  # Bright gold

        # Draw subtle grid lines
        grid_spacing = (base_line - self.height * 0.1) / 4  # 4 grid lines
        for i in range(5):  # 5 lines including baseline
            y = base_line - (i * grid_spacing)
            self.canvas.create_line(
                left_margin - 5, y, self.width - (self.width * 0.1), y, 
                fill="#3D4663", width=1, dash=(2, 4)
            )

        buckets_list = list(recategorized_stats.keys())
        for i, bucket_key in enumerate(buckets_list):
            x_start = left_margin + i * (3 * bar_width + gap)
            bdata = recategorized_stats[bucket_key]

            # core
            h_core = bdata["core_only"] * scale_factor
            if h_core > 0:
                # Create gradient effect with two rectangles
                self.canvas.create_rectangle(
                    x_start, base_line - h_core,
                    x_start + bar_width, base_line,
                    fill=c_core, outline="#000000", width=1
                )
                self.canvas.create_rectangle(
                    x_start + 2, base_line - h_core + 2,
                    x_start + bar_width - 2, base_line,
                    fill="#2D78DC", outline=""  # Darker shade for 3D effect
                )
                # Add count text
                self.canvas.create_text(
                    x_start + bar_width / 2, base_line - h_core - 10,
                    text=str(bdata["core_only"]), font=self.text_font, fill="#FFFFFF"
                )

            # support
            x_supp = x_start + bar_width
            h_supp = bdata["support_only"] * scale_factor
            if h_supp > 0:
                self.canvas.create_rectangle(
                    x_supp, base_line - h_supp,
                    x_supp + bar_width, base_line,
                    fill=c_support, outline="#000000", width=1
                )
                self.canvas.create_rectangle(
                    x_supp + 2, base_line - h_supp + 2,
                    x_supp + bar_width - 2, base_line,
                    fill="#2CC62C", outline=""  # Darker shade for 3D effect
                )
                self.canvas.create_text(
                    x_supp + bar_width / 2, base_line - h_supp - 10,
                    text=str(bdata["support_only"]), font=self.text_font, fill="#FFFFFF"
                )

            # mixed
            x_mixed = x_supp + bar_width
            h_mixed = bdata["mixed"] * scale_factor
            if h_mixed > 0:
                self.canvas.create_rectangle(
                    x_mixed, base_line - h_mixed,
                    x_mixed + bar_width, base_line,
                    fill=c_mixed, outline="#000000", width=1
                )
                self.canvas.create_rectangle(
                    x_mixed + 2, base_line - h_mixed + 2,
                    x_mixed + bar_width - 2, base_line,
                    fill="#DCA632", outline=""  # Darker shade for 3D effect
                )
                self.canvas.create_text(
                    x_mixed + bar_width / 2, base_line - h_mixed - 10,
                    text=str(bdata["mixed"]), font=self.text_font, fill="#FFFFFF"
                )

            # label - with slight glow effect
            self.canvas.create_text(
                x_start + 1.5 * bar_width, base_line + 15, text=bucket_key,
                font=(self.text_font[0], self.text_font[1], "bold"), fill="#FFFFFF"
            )

        # Draw legend with more spacing and clearer separation from chart
        legend_y = self.height - (self.height * 0.11)  # 11% from bottom
        legend_spacing = self.width / 4
        
        # Core legend
        legend_x = legend_spacing
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_core, outline="#000000", width=1
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Core", anchor="w", 
            font=self.text_font, fill="#FFFFFF"
        )
        
        # Support legend
        legend_x = legend_spacing * 2
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_support, outline="#000000", width=1
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Support", anchor="w", 
            font=self.text_font, fill="#FFFFFF"
        )
        
        # Mixed legend
        legend_x = legend_spacing * 3
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_mixed, outline="#000000", width=1
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Mixed", anchor="w", 
            font=self.text_font, fill="#FFFFFF"
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

        # Calculate bar dimensions based on current canvas size
        total_buckets = len(stats)
        bar_width = min(25, (self.width - 100) / (total_buckets * 3.5))  # Dynamic bar width
        gap = min(15, (self.width - 100) / (total_buckets * 6))  # Dynamic gap
        left_margin = self.width * 0.1  # 10% of width
        base_line = self.height - (self.height * 0.3)  # 30% from bottom
        scale_factor = (self.height - (self.height * 0.45)) / max_count if max_count > 0 else 1

        c_core = "#4F9AFF"  # Bright blue
        c_support = "#5CFF5C"  # Bright green
        c_mixed = "#FFC857"  # Bright gold

        # Draw subtle grid lines
        grid_spacing = (base_line - self.height * 0.1) / 4  # 4 grid lines
        for i in range(5):  # 5 lines including baseline
            y = base_line - (i * grid_spacing)
            self.canvas.create_line(
                left_margin - 5, y, self.width - (self.width * 0.1), y, 
                fill="#3D4663", width=1, dash=(2, 4)
            )

        buckets_list = list(stats.keys())
        for i, bucket_key in enumerate(buckets_list):
            x_start = left_margin + i * (3 * bar_width + gap)
            bdata = stats[bucket_key]

            # core
            h_core = bdata["core_only"] * scale_factor
            if h_core > 0:
                # Create gradient effect with two rectangles
                self.canvas.create_rectangle(
                    x_start, base_line - h_core,
                    x_start + bar_width, base_line,
                    fill=c_core, outline="#000000", width=1
                )
                self.canvas.create_rectangle(
                    x_start + 2, base_line - h_core + 2,
                    x_start + bar_width - 2, base_line,
                    fill="#2D78DC", outline=""  # Darker shade for 3D effect
                )
                self.canvas.create_text(
                    x_start + bar_width / 2, base_line - h_core - 10,
                    text=str(bdata["core_only"]), font=self.text_font, fill="#FFFFFF"
                )

            # support
            x_supp = x_start + bar_width
            h_supp = bdata["support_only"] * scale_factor
            if h_supp > 0:
                self.canvas.create_rectangle(
                    x_supp, base_line - h_supp,
                    x_supp + bar_width, base_line,
                    fill=c_support, outline="#000000", width=1
                )
                self.canvas.create_rectangle(
                    x_supp + 2, base_line - h_supp + 2,
                    x_supp + bar_width - 2, base_line,
                    fill="#2CC62C", outline=""  # Darker shade for 3D effect
                )
                self.canvas.create_text(
                    x_supp + bar_width / 2, base_line - h_supp - 10,
                    text=str(bdata["support_only"]), font=self.text_font, fill="#FFFFFF"
                )

            # mixed
            x_mixed = x_supp + bar_width
            h_mixed = bdata["mixed"] * scale_factor
            if h_mixed > 0:
                self.canvas.create_rectangle(
                    x_mixed, base_line - h_mixed,
                    x_mixed + bar_width, base_line,
                    fill=c_mixed, outline="#000000", width=1
                )
                self.canvas.create_rectangle(
                    x_mixed + 2, base_line - h_mixed + 2,
                    x_mixed + bar_width - 2, base_line,
                    fill="#DCA632", outline=""  # Darker shade for 3D effect
                )
                self.canvas.create_text(
                    x_mixed + bar_width / 2, base_line - h_mixed - 10,
                    text=str(bdata["mixed"]), font=self.text_font, fill="#FFFFFF"
                )

            # label
            self.canvas.create_text(
                x_start + 1.5 * bar_width, base_line + 15, text=bucket_key,
                font=(self.text_font[0], self.text_font[1], "bold"), fill="#FFFFFF"
            )

        # Draw legend with more spacing and clearer separation from chart
        legend_y = self.height - (self.height * 0.11)  # 11% from bottom
        legend_spacing = self.width / 4
        
        # Core legend
        legend_x = legend_spacing
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_core, outline="#000000", width=1
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Core", anchor="w", 
            font=self.text_font, fill="#FFFFFF"
        )
        
        # Support legend
        legend_x = legend_spacing * 2
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_support, outline="#000000", width=1
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Support", anchor="w", 
            font=self.text_font, fill="#FFFFFF"
        )
        
        # Mixed legend
        legend_x = legend_spacing * 3
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=c_mixed, outline="#000000", width=1
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Mixed", anchor="w", 
            font=self.text_font, fill="#FFFFFF"
        )


class RoleDistributionChartView:
    """
    A separate chart class for role distribution (count + avg MMR + priority breakdown).
    Shows how many players put each role at 1st, 2nd, and 3rd priority.
    """
    def __init__(self, parent, width=600, height=220, bg="#1E2130", text_font=("Arial",9,"bold")):
        self.width = width
        self.height = height
        self.bg = bg
        self.text_font = text_font
        self.parent = parent

        self.canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=1, highlightbackground="#3D4663")
        self.canvas.pack(side=tk.BOTTOM, padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Bind to configure event for resizing
        self.canvas.bind("<Configure>", self._on_resize)
        
        # Store the current data for redrawing on resize
        self.current_stats = None
        self.current_logic = None

    def _on_resize(self, event):
        """Handle window resize event"""
        # Update dimensions
        self.width = event.width
        self.height = event.height
        
        # Redraw with current data if available
        if self.current_stats:
            self.draw(self.current_stats, self.current_logic)

    def draw(self, stats: dict, logic=None):
        """
        stats => from logic.get_role_distribution_stats(), e.g.:
          { "carry": (count, avgMMR), "mid": (count, avgMMR), ... }
        
        Now also shows priority breakdown per role.
        """
        # Store current data for resize events
        self.current_stats = stats
        self.current_logic = logic
        
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

        # Calculate dimensions based on current canvas size
        base_line = self.height - (self.height * 0.27)  # 27% from bottom
        total_roles = len(roles_list)
        
        # Adjust bar_width and group_width based on canvas width
        bar_width = max(12, min(18, (self.width - 100) / (total_roles * 7)))  # Dynamic sizing
        group_width = max(bar_width * 6, min(120, (self.width - 100) / total_roles * 0.85))  # Dynamic group width
        
        left_margin = self.width * 0.08  # 8% of width
        gap = max(5, min(25, (self.width - left_margin - (group_width * total_roles)) / total_roles))
        
        scale_count = (self.height - (self.height * 0.45)) / max_count if max_count > 0 else 1
        scale_mmr = (self.height - (self.height * 0.45)) / max_mmr if max_mmr > 0 else 1
        scale_priority = (self.height - (self.height * 0.45)) / max_priority_count if max_priority_count > 0 else 1

        # Vibrant gamer colors
        color_count = "#3D8CFF"  # Bright blue
        color_mmr = "#FF6B6B"    # Bright red
        priority_colors = {
            1: "#FF9200",  # Orange for 1st priority
            2: "#FFB600",  # Lighter orange for 2nd priority
            3: "#FFDA00"   # Yellow for 3rd priority
        }
        
        # Draw subtle grid lines
        grid_spacing = (base_line - self.height * 0.1) / 4  # 4 grid lines
        for i in range(5):  # 5 lines including baseline
            y = base_line - (i * grid_spacing)
            self.canvas.create_line(
                left_margin - 5, y, self.width - (self.width * 0.08), y, 
                fill="#3D4663", width=1, dash=(2, 4)
            )

        for i, rname in enumerate(roles_list):
            c, avg = stats[rname]
            x_start = left_margin + i * (group_width + gap)

            # bar for count with 3D effect
            h_count = c * scale_count
            if h_count > 0:
                self.canvas.create_rectangle(
                    x_start, base_line - h_count,
                    x_start + bar_width, base_line,
                    fill=color_count, outline="#000000", width=1
                )
                self.canvas.create_rectangle(
                    x_start + 2, base_line - h_count + 2,
                    x_start + bar_width - 2, base_line,
                    fill="#2A6ADB", outline=""  # Darker shade for 3D effect
                )
                self.canvas.create_text(
                    x_start + bar_width / 2, base_line - h_count - 10,
                    text=str(c), fill="#FFFFFF",
                    font=self.text_font
                )

            # bar for avg MMR with 3D effect
            x_mmr = x_start + bar_width
            h_mmr = avg * scale_mmr
            if h_mmr > 0:
                self.canvas.create_rectangle(
                    x_mmr, base_line - h_mmr,
                    x_mmr + bar_width, base_line,
                    fill=color_mmr, outline="#000000", width=1
                )
                self.canvas.create_rectangle(
                    x_mmr + 2, base_line - h_mmr + 2,
                    x_mmr + bar_width - 2, base_line,
                    fill="#D44D4D", outline=""  # Darker shade for 3D effect
                )
                self.canvas.create_text(
                    x_mmr + bar_width / 2, base_line - h_mmr - 10,
                    text=str(int(avg)), fill="#FFFFFF",
                    font=self.text_font
                )
            
            # bars for priorities if we have the data
            if has_priority_data and rname in priority_counts:
                for prio in range(1, 4):
                    prio_count = priority_counts[rname].get(prio, 0)
                    x_prio = x_mmr + bar_width + (prio - 1) * bar_width
                    h_prio = prio_count * scale_priority
                    
                    if h_prio > 0:
                        self.canvas.create_rectangle(
                            x_prio, base_line - h_prio,
                            x_prio + bar_width, base_line,
                            fill=priority_colors[prio], outline="#000000", width=1
                        )
                        # Darker shade for 3D effect
                        darker_colors = {
                            1: "#DB7C00",  # Darker orange
                            2: "#DB9C00",  # Darker light orange
                            3: "#DBB800"   # Darker yellow
                        }
                        self.canvas.create_rectangle(
                            x_prio + 2, base_line - h_prio + 2,
                            x_prio + bar_width - 2, base_line,
                            fill=darker_colors[prio], outline=""
                        )
                        
                        self.canvas.create_text(
                            x_prio + bar_width / 2, base_line - h_prio - 10,
                            text=str(prio_count), fill="#FFFFFF",
                            font=self.text_font
                        )

            # label with glow effect
            self.canvas.create_text(
                x_start + group_width / 2, base_line + 15,
                text=rname, fill="#FFFFFF",
                font=(self.text_font[0], self.text_font[1] + 1, "bold")
            )

        # Draw legend at the bottom with clear separation from chart
        legend_y = self.height - (self.height * 0.11)  # 11% from bottom
        legend_spacing = self.width / 7  # Distribute evenly with room for 5-6 items
        
        # Draw a semi-transparent divider line
        self.canvas.create_line(
            left_margin - 10, base_line + 30, 
            self.width - left_margin + 10, base_line + 30,
            fill="#4D5980", width=1
        )
        
        # Count legend
        legend_x = legend_spacing
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=color_count, outline="#000000", width=1
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Count", anchor="w", 
            font=self.text_font, fill="#FFFFFF"
        )
        
        # MMR legend
        legend_x = legend_spacing * 2
        self.canvas.create_rectangle(
            legend_x - 30, legend_y, 
            legend_x - 15, legend_y + 15, 
            fill=color_mmr, outline="#000000", width=1
        )
        self.canvas.create_text(
            legend_x - 5, legend_y + 7, 
            text="Avg MMR", anchor="w", 
            font=self.text_font, fill="#FFFFFF"
        )
        
        # Priority legends
        if has_priority_data:
            for prio in range(1, 4):
                legend_x = legend_spacing * (2 + prio)
                self.canvas.create_rectangle(
                    legend_x - 30, legend_y, 
                    legend_x - 15, legend_y + 15, 
                    fill=priority_colors[prio], outline="#000000", width=1
                )
                self.canvas.create_text(
                    legend_x - 5, legend_y + 7, 
                    text=f"Prio {prio}", anchor="w", 
                    font=self.text_font, fill="#FFFFFF"
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


# Function to bind Enter key to Spin button in the main application
def bind_enter_to_spin(root, spin_button):
    """
    Binds the Enter key to trigger the Spin button.
    This function should be called after creating the Spin button.
    
    Parameters:
    - root: The root or parent window where the key binding applies
    - spin_button: The button to trigger when Enter is pressed
    """
    def trigger_spin(event):
        # Only trigger if button is enabled
        if str(spin_button['state']) != 'disabled':
            spin_button.invoke()
    
    # Bind Enter key to the trigger_spin function
    root.bind('<Return>', trigger_spin)