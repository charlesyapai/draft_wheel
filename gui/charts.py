# draft_wheel/gui/charts.py

import tkinter as tk

class MMRBucketChartView:
    """
    A separate chart class for MMR bucket distribution.
    """
    def __init__(self, parent, width=600, height=150, bg="#FFFFFF", text_font=("Arial",10,"bold")):
        self.width = width
        self.height = height
        self.bg = bg
        self.text_font = text_font

        self.canvas = tk.Canvas(parent, width=width, height=height, bg=bg)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=5)

    def draw(self, stats: dict):
        """
        stats => from logic.get_mmr_bucket_stats().
        """
        self.canvas.delete("all")
        if not stats:
            return

        # gather total counts
        all_counts=[]
        for bucket_key, d in stats.items():
            total = d["core_only"]+ d["support_only"]+ d["mixed"]
            all_counts.append(total)
        max_count = max(all_counts) if all_counts else 1

        bar_width=40
        gap=10
        left_margin=50
        base_line= self.height-30
        scale_factor= (self.height-50)/max_count

        c_core="#88C0D0"
        c_support="#A3BE8C"
        c_mixed="#EBCB8B"

        # draw bars
        buckets_list = list(stats.keys())
        for i, bucket_key in enumerate(buckets_list):
            x_start= left_margin + i*(3*bar_width+ gap)
            bdata= stats[bucket_key]

            # core
            h_core= bdata["core_only"]* scale_factor
            self.canvas.create_rectangle(
                x_start, base_line - h_core,
                x_start+bar_width, base_line,
                fill=c_core, outline="black"
            )
            self.canvas.create_text(
                x_start+ bar_width/2, base_line - h_core-10,
                text=str(bdata["core_only"]),
                font=self.text_font
            )

            # support
            x_supp= x_start+ bar_width
            h_supp= bdata["support_only"]*scale_factor
            self.canvas.create_rectangle(
                x_supp, base_line - h_supp,
                x_supp+bar_width, base_line,
                fill=c_support, outline="black"
            )
            self.canvas.create_text(
                x_supp+ bar_width/2, base_line - h_supp -10,
                text=str(bdata["support_only"]),
                font=self.text_font
            )

            # mixed
            x_mixed= x_supp+ bar_width
            h_mixed= bdata["mixed"]* scale_factor
            self.canvas.create_rectangle(
                x_mixed, base_line - h_mixed,
                x_mixed+bar_width, base_line,
                fill=c_mixed, outline="black"
            )
            self.canvas.create_text(
                x_mixed+ bar_width/2, base_line - h_mixed-10,
                text=str(bdata["mixed"]),
                font=self.text_font
            )

            # label
            self.canvas.create_text(
                x_start+1.5*bar_width, base_line+15,
                text=bucket_key,
                font=(self.text_font[0], self.text_font[1], "bold")
            )

        # title
        self.canvas.create_text(
            self.width//2, 15,
            text="MMR Bucket Distribution",
            font=(self.text_font[0], self.text_font[1]+1, "bold"),
            fill="black"
        )

        # You can add a legend if you want.

class RoleDistributionChartView:
    """
    A separate chart class for role distribution (count + avg MMR).
    """
    def __init__(self, parent, width=600, height=180, bg="#FFFFFF", text_font=("Arial",10,"bold")):
        self.width= width
        self.height=height
        self.bg=bg
        self.text_font=text_font

        self.canvas= tk.Canvas(parent, width=width, height=height, bg=bg)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=5)

    def draw(self, stats:dict):
        """
        stats => from logic.get_role_distribution_stats(), e.g.:
          { "carry": (count, avgMMR), "mid": (count, avgMMR), ... }
        """
        self.canvas.delete("all")
        if not stats:
            return

        roles_list = list(stats.keys())
        counts=[]
        mmrs=[]
        for r in roles_list:
            c, avg= stats[r]
            counts.append(c)
            mmrs.append(avg)
        max_count= max(counts) if counts else 1
        max_mmr= max(mmrs) if mmrs else 1

        base_line= self.height-30
        bar_width=20
        group_width=75
        left_margin=40
        gap=20
        scale_count= (self.height-50)/max_count
        scale_mmr= (self.height-50)/max_mmr

        color_count="#5E81AC"
        color_mmr="#BF616A"

        for i, rname in enumerate(roles_list):
            c, avg= stats[rname]
            x_start= left_margin + i*(group_width+ gap)

            # bar for count
            h_count= c* scale_count
            self.canvas.create_rectangle(
                x_start, base_line-h_count,
                x_start+bar_width, base_line,
                fill=color_count, outline="black"
            )
            self.canvas.create_text(
                x_start+bar_width/2, base_line-h_count-10,
                text=str(c),
                font=self.text_font
            )

            # bar for avg MMR
            x_mmr= x_start+bar_width
            h_mmr= avg*scale_mmr
            self.canvas.create_rectangle(
                x_mmr, base_line -h_mmr,
                x_mmr+bar_width, base_line,
                fill=color_mmr, outline="black"
            )
            self.canvas.create_text(
                x_mmr+bar_width/2, base_line-h_mmr-10,
                text=str(int(avg)),
                font=self.text_font
            )

            # label
            self.canvas.create_text(
                x_start+ bar_width, base_line+15,
                text=rname,
                font=(self.text_font[0], self.text_font[1]+1, "bold")
            )

        # title
        self.canvas.create_text(
            self.width//2, 20,
            text="Role Distribution",
            font=(self.text_font[0], self.text_font[1]+2, "bold"),
            fill="black"
        )
        # optional legend, etc.
