# draft_wheel/gui/draft_gui.py

import tkinter as tk
from tkinter import ttk
import random
import os
import math
from PIL import Image, ImageTk

# import the chart classes
from  gui.charts import MMRBucketChartView, RoleDistributionChartView


class DraftGUI:
    def __init__(self, master, config: dict, logic):
        self.master = master
        self.config = config
        self.logic = logic

        ui = self.config.get("ui_settings", {})
        self.scale_width = ui.get("wheel_size", 700)
        self.scale_height=200
        self.text_font_size= ui.get("text_font_size", 10)
        self.text_font_type= ui.get("text_font_type","Arial")

        style=ttk.Style()
        style.configure("Treeview",
                        font=(self.text_font_type, self.text_font_size, "bold"),
                        rowheight=28)
        style.configure("Treeview.Heading",
                        font=(self.text_font_type, self.text_font_size+1, "bold"))
        style.configure("Normal.TButton",
                        font=(self.text_font_type, 11, "bold"),
                        padding=8,
                        foreground="black")

        self.friction_var = tk.DoubleVar(value=0.99)

        # Layout
        self.left_frame= tk.Frame(master)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.right_frame= tk.Frame(master, bd=2, relief=tk.GROOVE)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.teams_canvas= tk.Canvas(self.right_frame, bg="#F0F0F0")
        self.teams_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.teams_scrollbar= ttk.Scrollbar(self.right_frame, orient="vertical",
                                            command=self.teams_canvas.yview)
        self.teams_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.teams_canvas.configure(yscrollcommand=self.teams_scrollbar.set)

        self.teams_inner_frame= tk.Frame(self.teams_canvas, bg="#F0F0F0")
        self.teams_canvas.create_window((0,0), window=self.teams_inner_frame, anchor="nw")
        def _on_teams_configure(event):
            self.teams_canvas.configure(scrollregion=self.teams_canvas.bbox("all"))
        self.teams_inner_frame.bind("<Configure>", _on_teams_configure)

        self.center_frame= tk.Frame(master, bg="#EEEEEE")
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # top => scale+probabilities+ friction
        self.top_center_frame= tk.Frame(self.center_frame, bg="#DDDDDD")
        self.top_center_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # # # next => MMR bucket chart
        # # self.mmr_bucket_ch        # next => MMR bucket chart
        # self.mmr_bucket_chart_frame= tk.Frame(self.center_frame, bg="#EEEEEE")
        # self.mmr_bucket_chart_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # # next => role chart
        # self.role_chart_frame= tk.Frame(self.center_frame, bg="#EEEEEE")
        # self.role_chart_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # bottom => banner
        self.bottom_banner_frame= tk.Frame(self.center_frame, bg="#CCCCCC")
        self.bottom_banner_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Build role list (left)
        self.role_frames={}
        for r in self.logic.players_by_role:
            f= tk.Frame(self.left_frame, bd=2, relief=tk.RIDGE)
            f.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lbl= tk.Label(f, text=r.upper(), font=(self.text_font_type,9,"bold"))
            lbl.pack(side=tk.TOP)
            lb= tk.Listbox(f, height=8)
            lb.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.role_frames[r]= lb

        # top controls
        self.top_controls_frame_1= tk.Frame(self.top_center_frame, bg="#DDDDDD")
        self.top_controls_frame_1.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.top_controls_frame_2= tk.Frame(self.top_center_frame, bg="#DDDDDD")
        self.top_controls_frame_2.pack(side=tk.TOP, fill=tk.X, pady=2)

        # row1
        tk.Label(self.top_controls_frame_1, text="Select Team:", bg="#DDDDDD").pack(side=tk.LEFT, padx=5)
        self.team_var= tk.StringVar()
        self.team_combo= ttk.Combobox(self.top_controls_frame_1, textvariable=self.team_var,
                                      font=(self.text_font_type,11))
        self.team_combo.pack(side=tk.LEFT, padx=5)

        self.btn_new_team= ttk.Button(self.top_controls_frame_1, text="New Team",style="Normal.TButton",
                                      command=self.create_team_popup)
        self.btn_new_team.pack(side=tk.LEFT, padx=5)

        self.btn_add_captain= ttk.Button(self.top_controls_frame_1, text="Add Captain",style="Normal.TButton",
                                         command=self.add_captain_popup)
        self.btn_add_captain.pack(side=tk.LEFT, padx=5)

        tk.Label(self.top_controls_frame_1, text="Select Role:", bg="#DDDDDD").pack(side=tk.LEFT, padx=5)
        self.role_var= tk.StringVar()
        roles_list= list(self.logic.players_by_role.keys())
        self.role_combo= ttk.Combobox(self.top_controls_frame_1, textvariable=self.role_var,
                                      font=(self.text_font_type,11),
                                      values=roles_list)
        self.role_combo.pack(side=tk.LEFT, padx=5)

        # row2
        self.btn_preview= ttk.Button(self.top_controls_frame_2, text="Preview", style="Normal.TButton",
                                     command=self.preview_slices)
        self.btn_preview.pack(side=tk.LEFT, padx=5)

        self.btn_spin= ttk.Button(self.top_controls_frame_2, text="Spin", style="Normal.TButton",
                                  command=self.spin_clicked)
        self.btn_spin.pack(side=tk.LEFT, padx=5)

        self.btn_undo= ttk.Button(self.top_controls_frame_2, text="Undo", style="Normal.TButton",
                                  command=self.undo_pick)
        self.btn_undo.pack(side=tk.LEFT, padx=5)

        self.btn_save= ttk.Button(self.top_controls_frame_2, text="Save", style="Normal.TButton",
                                  command=self.save_draft)
        self.btn_save.pack(side=tk.LEFT, padx=5)

        self.btn_load= ttk.Button(self.top_controls_frame_2, text="Load", style="Normal.TButton",
                                  command=self.load_draft)
        self.btn_load.pack(side=tk.LEFT, padx=5)

        self.randomness_label_var= tk.StringVar(value="Randomness: N/A")
        self.randomness_label= tk.Label(self.top_controls_frame_2, textvariable=self.randomness_label_var,bg="#DDDDDD")
        self.randomness_label.pack(side=tk.LEFT, padx=10)

        tk.Label(self.top_controls_frame_2, text="Friction:", bg="#DDDDDD").pack(side=tk.LEFT, padx=5)
        self.friction_spin= tk.Spinbox(self.top_controls_frame_2, from_=0.80,to=0.999,increment=0.001,
                                       textvariable=self.friction_var, width=5)
        self.friction_spin.pack(side=tk.LEFT, padx=5)

        # scale+prob
        self.scale_prob_frame= tk.Frame(self.top_center_frame, bg="#EEEEEE")
        self.scale_prob_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.scale_canvas= tk.Canvas(self.scale_prob_frame, width=self.scale_width,
                                     height=self.scale_height, bg="white")
        self.scale_canvas.pack(side=tk.LEFT, padx=10, pady=5)


        # # [NEW CODE] - Add a canvas for the sigmoid/ratio curve
        # self.sigmoid_canvas = tk.Canvas(self.scale_prob_frame, width=300, height=200, bg="white")
        # self.sigmoid_canvas.pack(side=tk.LEFT, padx=10, pady=5)

        # [NEW CODE] - A label to show the pool vs. drafted MMR averages
        self.stats_label_var = tk.StringVar(value="Pool Avg: ?, Drafted Avg: ?")
        self.stats_label = tk.Label(self.top_center_frame, textvariable=self.stats_label_var,
                                    bg="#DDDDDD", font=(self.text_font_type, 10, "bold"))
        self.stats_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)

        self.prob_frame = tk.Frame(self.scale_prob_frame, bg="#EEEEEE")
        self.prob_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        tk.Label(self.prob_frame, text="Probabilities", bg="#EEEEEE",
                 font=(self.text_font_type, 10, "bold")).pack(anchor="w")

        # [MODIFIED CODE] - Add columns for MMR and Diff
        self.prob_tree = ttk.Treeview(self.prob_frame, columns=("player", "mmr", "diff", "prob"),
                                      show="headings", height=10)
        self.prob_tree.heading("player", text="Player")
        self.prob_tree.heading("mmr", text="MMR")
        self.prob_tree.heading("diff", text="Diff")
        self.prob_tree.heading("prob", text="Probability")

        self.prob_tree.column("player", width=120)
        self.prob_tree.column("mmr", width=60)
        self.prob_tree.column("diff", width=60)
        self.prob_tree.column("prob", width=80)
        self.prob_tree.pack(fill=tk.BOTH, expand=False)

        text_font=(self.text_font_type, self.text_font_size,"bold")




        # 1) Main container for all bottom charts
        self.bottom_charts_frame = tk.Frame(self.center_frame, bg="#EEEEEE")
        self.bottom_charts_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 2) A left panel to stack MMR & Role charts
        self.charts_left_panel = tk.Frame(self.bottom_charts_frame, bg="#EEEEEE")
        self.charts_left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 3) A right panel for the Sigmoid chart
        self.sigmoid_chart_frame = tk.Frame(self.bottom_charts_frame, bg="#EEEEEE")
        self.sigmoid_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 4) Inside the left panel, we create two frames for each chart:
        #    a) MMR bucket chart frame (TOP)
        #    b) Role distribution chart frame (BOTTOM)

        # a) MMR bucket chart frame
        self.mmr_bucket_chart_frame = tk.Frame(self.charts_left_panel, bg="#EEEEEE")
        self.mmr_bucket_chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # b) Role distribution chart frame
        self.role_chart_frame = tk.Frame(self.charts_left_panel, bg="#EEEEEE")
        self.role_chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # 5) Create the actual chart objects in those frames
        ui = self.config.get("ui_settings", {})
        self.mmr_chart = MMRBucketChartView(
            self.mmr_bucket_chart_frame,
            width=ui.get("mmr_chart_width", 600),
            height=ui.get("mmr_chart_height", 150),
            text_font=(self.text_font_type, self.text_font_size, "bold")
        )
        self.role_chart = RoleDistributionChartView(
            self.role_chart_frame,
            width=ui.get("role_chart_width", 600),
            height=ui.get("role_chart_height", 180),
            text_font=(self.text_font_type, self.text_font_size, "bold")
        )

        # 6) The Sigmoid canvas (centered)
        self.sigmoid_canvas = tk.Canvas(
            self.sigmoid_chart_frame,
            width=300,
            height=200,
            bg="white"
        )
        self.sigmoid_canvas.pack(side=tk.LEFT, anchor="sw", fill=tk.BOTH, expand=True, padx=15, pady=20)



        # banner
        banner_path="banner.png"
        if os.path.exists(banner_path):
            try:
                self.banner_img= ImageTk.PhotoImage(Image.open(banner_path))
                tk.Label(self.bottom_banner_frame, image=self.banner_img).pack()
            except Exception as e:
                print(f"[WARNING] Could not load banner: {e}")
                tk.Label(self.bottom_banner_frame, text="(Banner error)",bg="#CCCCCC").pack()
        else:
            tk.Label(self.bottom_banner_frame, text="(No banner found)",bg="#CCCCCC").pack()

        # internal
        self.scale_segments=[]
        self.pointer_x=0.0
        self.pointer_vel=0.0
        self.bouncing=False
        self.pick_team=None
        self.pick_role=None
        self.player_colors={}

        self.refresh_all()

    # REFRESH
    def refresh_all(self):
        self.refresh_teams_combo()
        self.refresh_roles_listboxes()
        self.refresh_teams_display()
        self.draw_mmr_bucket_chart()
        self.draw_role_chart()

    def refresh_teams_combo(self):
        teams=list(self.logic.get_teams_data().keys())
        self.team_combo["values"]=teams

    def refresh_roles_listboxes(self):
        p_by_role=self.logic.get_players_by_role()
        for r, lb in self.role_frames.items():
            lb.delete(0, tk.END)
            if r in p_by_role:
                for player in p_by_role[r]:
                    mmr=self.logic.all_players[player]["mmr"]
                    lb.insert(tk.END, f"{player} (MMR {mmr})")

    def refresh_teams_display(self):
        for w in self.teams_inner_frame.winfo_children():
            w.destroy()

        all_teams= self.logic.get_teams_data()
        idx=0
        role_to_num=self.logic.role_to_number

        for tid, tinfo in all_teams.items():
            team_bg= self._team_color(idx)
            team_card= tk.Frame(self.teams_inner_frame, bd=2, relief=tk.RAISED, bg=team_bg)
            # let user click => sets that team
            team_card.bind("<Button-1>", lambda e,team_id=tid: self.on_team_box_clicked(team_id))

            # If you want 2 columns => use .grid(...) instead of .pack(...)
            team_card.pack(side=tk.TOP, fill=tk.X, anchor="nw", pady=5, padx=5)

            tk.Label(team_card, text=f"Team: {tid}",
                     bg=team_bg, font=(self.text_font_type,12,"bold")).pack(side=tk.TOP, anchor=tk.W)

            avg_mmr_int=int(tinfo["average_mmr"]) if tinfo["players"] else 0
            tk.Label(team_card, text=f"Average MMR: {avg_mmr_int}",
                     bg=team_bg).pack(side=tk.TOP, anchor=tk.W)

            count= len(tinfo["players"])
            tk.Label(team_card, text=f"Players Count: {count}",
                     bg=team_bg).pack(side=tk.TOP, anchor=tk.W)

            plist_frame= tk.Frame(team_card, bg=team_bg)
            plist_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

            for (pname, role) in tinfo["players"]:
                if role=="(Captain)":
                    line=f"(Captain) {pname}"
                else:
                    role_str= role_to_num.get(role,"?")
                    line=f"{role_str} {pname}"
                lbl=tk.Label(plist_frame, text=line, bg=team_bg,
                             font=(self.text_font_type, self.text_font_size,"normal"))
                lbl.pack(side=tk.TOP, anchor=tk.W)

            idx+=1

    def on_team_box_clicked(self, team_id:str):
        self.team_var.set(team_id)

    # CHARTS
    def draw_mmr_bucket_chart(self):
        stats=self.logic.get_mmr_bucket_stats()
        self.mmr_chart.draw(stats)

    def draw_role_chart(self):
        stats=self.logic.get_role_distribution_stats()
        self.role_chart.draw(stats)

    # PREVIEW / SPIN
    def preview_slices(self):
        team_id=self.team_var.get()
        self.team_id = team_id
        role=self.role_var.get()
        if team_id not in self.logic.get_teams_data():
            return

        # If empty
        if role in self.logic.players_by_role and not self.logic.players_by_role[role]:
            fallback_role=self.ask_for_fallback_role(role)
            if not fallback_role:
                return
            actual_role= fallback_role
        else:
            actual_role= role

        base_random= self._get_base_randomness(team_id)
        self.randomness_label_var.set(f"Randomness: {base_random:.2f}")


        # [NEW CODE] - Gather 'ideal_mmr' for display
        ideal_mmr = self.logic.get_ideal_mmr_for_pick(team_id, actual_role)

        # [NEW CODE] - Show pool vs drafted MMR averages
        pool_avg = self.logic.get_pool_average_mmr()
        drafted_avg = self.logic.get_drafted_average_mmr()
        self.stats_label_var.set(f"Pool Avg: {int(pool_avg)}  |  Drafted Avg: {int(drafted_avg)}")

        # Calculate probabilities
        probs = self.logic.compute_probabilities(team_id, actual_role)
        if not probs:
            self.scale_canvas.delete("all")
            self.sigmoid_canvas.delete("all")  # clear the sigmoid canvas as well
            for item in self.prob_tree.get_children():
                self.prob_tree.delete(item)
            return

        # Clear old items
        for item in self.prob_tree.get_children():
            self.prob_tree.delete(item)
        self.player_colors.clear()
        self.scale_segments = []

        # 1) Build data (player, mmr, diff, prob) and sort by MMR
        data_list = []
        for p, prob_val in probs.items():
            pm = self.logic.all_players[p]["mmr"]
            diff_val = abs(pm - ideal_mmr)
            data_list.append((p, pm, diff_val, prob_val))
        # Sort by MMR ascending (change to descending if you prefer)
        data_list.sort(key=lambda x: x[1])

        # 2) Populate the Treeview in sorted order
        idx = 0
        total_prob = sum(x[3] for x in data_list)
        current_angle = 0.0  # used for the scale drawing
        for (p, pm, diff_val, prob_val) in data_list:
            prob_pct = prob_val * 100.0
            prob_str = f"{prob_pct:.1f}%"

            # color
            color = self._team_color(idx)
            self.player_colors[p] = color

            # Insert row into tree
            style_name = f"ColorStyle_{idx}"
            s = ttk.Style()
            s.configure(style_name, background=color,
                        font=(self.text_font_type, self.text_font_size, "bold"))

            row_id = self.prob_tree.insert("", "end", values=(p, int(pm), int(diff_val), prob_str))
            self.prob_tree.item(row_id, tags=(style_name,))
            self.prob_tree.tag_configure(style_name, background=color)

            idx += 1

        # 3) Build scale segments (like before) for the main wheel canvas
        segs = self.build_segments(probs)
        self.scale_segments = segs
        self.draw_scale(segs)

        # 4) Draw the sigmoid/ratio curve on self.sigmoid_canvas
        self.draw_sigmoid_curve(self.sigmoid_canvas, data_list, ideal_mmr)

    def draw_sigmoid_curve(self, canvas, data_list, ideal_mmr):
        """
        [NEW CODE]
        Draw a basic logistic-like curve from ratio=0 to ratio=some max,
        and then plot each player's (ratio, weight) point in matching color.

        data_list: list of (playerName, mmr, diff, prob)
        """
        canvas.delete("all")

        # If you have a known logistic function, you can replicate it here.
        # For example, if midpoint=0.1, slope=5.0, then we do:
        midpoint = self.config["logistic_settings"].get("midpoint", 0.1)
        slope = self.config["logistic_settings"].get("slope", 5.0)

        # Canvas dimensions
        w = int(canvas["width"])
        h = int(canvas["height"])

        # We'll sample ratio from 0..(some max) in small steps
        # Let's find max ratio from the data. Or pick 2.0 if large.
        max_ratio = 0.0
        for (_, pm, diff_val, _) in data_list:
            if ideal_mmr > 0:
                r = diff_val / ideal_mmr
                if r > max_ratio:
                    max_ratio = r
        if max_ratio < 0.2:
            max_ratio = 0.2  # minimal range
        margin_ratio = 0.1 * max_ratio
        max_ratio += margin_ratio

        def logistic_fn(ratio):
            return 1.0 / (1.0 + math.exp(slope * (ratio - midpoint)))

        # Draw X and Y axes
        x_axis_pad = 40
        y_axis_pad = 20
        canvas.create_line(x_axis_pad, h-y_axis_pad, w-10, h-y_axis_pad, fill="black")  # X axis
        canvas.create_line(x_axis_pad, h-y_axis_pad, x_axis_pad, 10, fill="black")      # Y axis

        # We'll map ratio in [0..max_ratio] to X in [x_axis_pad..(w-50)]
        # We'll map logistic in [0..1] to Y in [h-y_axis_pad..someTop]
        def to_canvas_coords(ratio, val):
            # ratio => X
            x_min = x_axis_pad
            x_max = w - 50
            ratio_frac = ratio / max_ratio
            cx = x_min + (x_max - x_min) * ratio_frac

            # logistic => Y ( invert so 1.0 is near the top )
            y_min = 10
            y_max = h - y_axis_pad
            # val is in [0..1], so we flip
            cy = y_max - (y_max - y_min) * val
            return (cx, cy)

        # Plot the curve
        prev_x, prev_y = None, None
        steps = 100
        for i in range(steps+1):
            r = (max_ratio / steps) * i
            val = logistic_fn(r)
            cx, cy = to_canvas_coords(r, val)
            if i > 0:
                canvas.create_line(prev_x, prev_y, cx, cy, fill="blue")
            prev_x, prev_y = cx, cy

        # Plot the data points
        for (p, pm, diff_val, prob_val) in data_list:
            if ideal_mmr <= 0:
                continue
            ratio = diff_val / ideal_mmr
            lw = logistic_fn(ratio)

            (cx, cy) = to_canvas_coords(ratio, lw)
            radius = 4
            color = self.player_colors.get(p, "red")
            canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=color)

            # Optionally label them
            canvas.create_text(cx, cy - 10, text=p, fill=color, font=(self.text_font_type, 8, "bold"))

    def build_segments(self, probs_dict):
        """
        Same logic you had before for building the slices for the wheel.
        This returns a list of (player, startAngle, endAngle in degrees * 100).
        """
        segs = []
        acc = 0.0
        for p, val in probs_dict.items():
            deg = val*100.0
            segs.append((p, acc, acc+deg))
            acc += deg
        return segs

        probs= self.logic.compute_probabilities(team_id, actual_role)
        if not probs:
            self.scale_canvas.delete("all")
            for item in self.prob_tree.get_children():
                self.prob_tree.delete(item)
            return

        for item in self.prob_tree.get_children():
            self.prob_tree.delete(item)
        self.player_colors.clear()

        segs= self.build_segments(probs)
        self.scale_segments=segs
        self.draw_scale(segs)

        idx=0
        for (p, start, end) in segs:
            color=self._team_color(idx)
            self.player_colors[p]= color
            prob_fraction= (end-start)/100.0
            prob_str=f"{prob_fraction*100:.1f}%"

            style_name=f"ColorStyle_{idx}"
            s=ttk.Style()
            s.configure(style_name, background=color,
                        font=(self.text_font_type,self.text_font_size,"bold"))
            row_id=self.prob_tree.insert("", "end", values=(p, prob_str))
            self.prob_tree.item(row_id, tags=(style_name,))
            self.prob_tree.tag_configure(style_name, background=color)

            idx+=1

    def ask_for_fallback_role(self, original_role:str):
        popup=tk.Toplevel(self.master)
        popup.title("Empty Role Pool")
        tk.Label(popup, text=f"No players left for role: {original_role}. Select fallback:").pack(pady=5)
        fallback_var=tk.StringVar()
        fallback_combo=ttk.Combobox(popup, textvariable=fallback_var,
                                    values=list(self.logic.players_by_role.keys()))
        fallback_combo.pack(pady=5)

        choice=[None]
        def confirm():
            chosen=fallback_var.get()
            if chosen and chosen in self.logic.players_by_role:
                choice[0]= chosen
            popup.destroy()

        def cancel():
            popup.destroy()

        ttk.Button(popup, text="OK", command=confirm).pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Button(popup, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=20, pady=10)

        popup.wait_window()
        return choice[0]

    def spin_clicked(self):
        team_id=self.team_var.get()
        role=self.role_var.get()
        if team_id not in self.logic.get_teams_data():
            return

        if role in self.logic.players_by_role and not self.logic.players_by_role[role]:
            fallback_role=self.ask_for_fallback_role(role)
            if not fallback_role:
                return
            actual_role_to_spin=fallback_role
        else:
            actual_role_to_spin= role

        base_random= self._get_base_randomness(team_id)
        self.randomness_label_var.set(f"Randomness: {base_random:.2f}")

        probs= self.logic.compute_probabilities(team_id, actual_role_to_spin)
        if not probs:
            return

        segs= self.build_segments(probs)
        if not segs:
            return

        self.scale_segments=segs
        self.pick_team= team_id
        # we assign them to the original role, even if we fallback
        self.pick_role= role

        self.pointer_x= random.uniform(0,100)
        self.pointer_vel= random.uniform(-5,5)
        if abs(self.pointer_vel)<1:
            self.pointer_vel=5 if self.pointer_vel>=0 else -5

        self.bouncing=True
        self.update_bounce()

    def update_bounce(self):
        if not self.bouncing:
            return
        friction=self.friction_var.get()
        self.pointer_x+= self.pointer_vel
        if self.pointer_x<0:
            self.pointer_x= abs(self.pointer_x)
            self.pointer_vel= -self.pointer_vel
        elif self.pointer_x>100:
            excess= self.pointer_x-100
            self.pointer_x= 100- excess
            self.pointer_vel= -self.pointer_vel

        self.pointer_vel*= friction
        self.draw_scale(self.scale_segments)
        self.draw_pointer()

        if abs(self.pointer_vel)<0.2:
            self.bouncing=False
            chosen= self.logic.pick_player_from_position(
                self.pick_team, self.pick_role, self.pointer_x, self.scale_segments
            )
            self.scale_canvas.delete("all")
            self.draw_scale([])
            self.refresh_all()
            if chosen:
                w=int(self.scale_width/2)
                h=int(self.scale_height/2)
                chosen_color= self.player_colors.get(chosen,"red")
                text_id= self.scale_canvas.create_text(
                    w,h,
                    text=chosen,
                    fill="black",
                    font=(self.text_font_type, self.text_font_size+6,"bold"),
                    anchor="center"
                )
                bbox=self.scale_canvas.bbox(text_id)
                if bbox:
                    rect_id=self.scale_canvas.create_rectangle(bbox, fill=chosen_color, outline="")
                    self.scale_canvas.tag_raise(text_id, rect_id)
            return
        else:
            self.master.after(20, self.update_bounce)

    def build_segments(self, probs:dict):
        segs=[]
        current=0.0
        for p,val in probs.items():
            width= val*100.0
            segs.append((p, current, current+width))
            current+= width
        return segs

    def draw_scale(self, segs):
        self.scale_canvas.delete("all")
        w=self.scale_width
        h=self.scale_height
        self.scale_canvas.create_rectangle(0,0, w,h, outline="black", width=2, fill="white")
        for idx, (p,start,end) in enumerate(segs):
            x1=(start/100)* w
            x2=(end/100)* w
            color=self._team_color(idx)
            self.player_colors[p]= color
            self.scale_canvas.create_rectangle(x1,0,x2,h, fill=color, outline="")

            cx=(x1+x2)/2
            cy=h/2
            self.scale_canvas.create_text(cx,cy,
                                          text=p,
                                          font=(self.text_font_type,self.text_font_size,"bold"),
                                          fill="black",
                                          angle=90)

    def draw_pointer(self):
        w=self.scale_width
        h=self.scale_height
        px=(self.pointer_x/100)* w
        self.scale_canvas.create_line(px,0,px,h, width=4, fill="red")

    # UNDO / SAVE / LOAD
    def undo_pick(self):
        undone=self.logic.undo_last_pick()
        if undone:
            print(f"[UNDO] Removed {undone} from team.")
        self.refresh_all()

    def save_draft(self):
        self.logic.save_state("data/draft_remaining.csv", "data/draft_teams.csv")
        print("[GUI] Saved state.")

    def load_draft(self):
        self.logic.load_state("data/draft_remaining.csv", "data/draft_teams.csv")
        print("[GUI] Loaded state.")
        self.refresh_all()
        for item in self.prob_tree.get_children():
            self.prob_tree.delete(item)
        self.scale_canvas.delete("all")

    # CAPTAIN
    def add_captain_popup(self):
        team_id=self.team_var.get()
        if not team_id:
            return
        popup=tk.Toplevel(self.master)
        popup.title(f"Add Captain to {team_id}")

        tk.Label(popup, text="Captain Name:").pack(pady=5)
        name_var=tk.StringVar()
        e_name=tk.Entry(popup, textvariable=name_var)
        e_name.pack(pady=5)

        tk.Label(popup, text="Captain MMR:").pack(pady=5)
        mmr_var=tk.StringVar()
        e_mmr=tk.Entry(popup, textvariable=mmr_var)
        e_mmr.pack(pady=5)

        def confirm():
            cname= name_var.get().strip()
            if not cname:
                popup.destroy()
                return
            try:
                cmmr=int(mmr_var.get())
            except:
                cmmr=0
            self.logic.add_captain_to_team(team_id,cname,cmmr)
            self.refresh_all()
            popup.destroy()
        ttk.Button(popup, text="Confirm", command=confirm).pack(pady=10)

    def create_team_popup(self):
        popup=tk.Toplevel(self.master)
        popup.title("Create New Team")
        tk.Label(popup, text="Team Name:").pack(side=tk.TOP, pady=5)
        name_var=tk.StringVar()
        entry=tk.Entry(popup, textvariable=name_var)
        entry.pack(side=tk.TOP, pady=5)
        def confirm():
            tname=name_var.get().strip()
            if tname:
                self.logic.register_team(tname)
                self.refresh_all()
            popup.destroy()
        ttk.Button(popup, text="Confirm",style="Normal.TButton", command=confirm).pack(side=tk.TOP, pady=10)

    # # UTILS
    def _get_base_randomness(self, team_id:str)->float:
        teams_data=self.logic.get_teams_data()
        if team_id not in teams_data:
            return 0.0
        n=len(teams_data[team_id]["players"])
        return self.logic.randomness_levels.get(n,0.30)

    # def _te# _color(self, idx=0):
    #     random.seed(idx)
    #     r=random.randint(100,255)
    #     g=random.randint(100,255)
    #     b=random.randint(100,255)
    #     return f"#{r:02x}{g:02x}{b:02x}"


    def _team_color(self, idx: int):
        # Your existing logic for color generation or cycling
        base_colors = ["#FFD700","#ADFF2F","#40E0D0","#FF69B4","#FF7F50","#9ACD32","#9370DB","#FFB6C1"]
        return base_colors[idx % len(base_colors)]
