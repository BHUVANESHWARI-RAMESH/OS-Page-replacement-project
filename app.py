"""
Page Replacement Algorithm Simulator
------------------------------------
A modern dashboard-style desktop application built with Tkinter and Matplotlib
that simulates and compares FIFO, LRU and Optimal page replacement algorithms.

Run with:  python main.py
Requires:  matplotlib  (pip install matplotlib)
"""

import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ---------------------------------------------------------------------------
# THEME / COLORS
# ---------------------------------------------------------------------------
BG_DARK       = "#0f172a"   # main background  (slate-900)
BG_PANEL      = "#1e293b"   # panel background (slate-800)
BG_CARD       = "#273449"   # card background
ACCENT        = "#3b82f6"   # blue-500
ACCENT_DARK   = "#2563eb"
HIT_COLOR     = "#22c55e"   # green-500
FAULT_COLOR   = "#ef4444"   # red-500
REPLACED_COL  = "#facc15"   # yellow-400
CURRENT_COL   = "#60a5fa"   # blue-400
TEXT_LIGHT    = "#f1f5f9"
TEXT_MUTED    = "#94a3b8"
BORDER        = "#334155"


# ===========================================================================
# ALGORITHM IMPLEMENTATIONS
# ===========================================================================

def fifo(pages, capacity):
    """First-In-First-Out page replacement.
    Returns list of step dicts and (faults, hits)."""
    frames, queue, steps, faults, hits = [], [], [], 0, 0
    for i, page in enumerate(pages):
        replaced, explanation = "-", ""
        if page in frames:
            hits += 1
            result = "Hit"
            explanation = f"Page {page} found in frames -> Hit"
        else:
            faults += 1
            result = "Fault"
            if len(frames) < capacity:
                frames.append(page)
                explanation = f"Page {page} loaded into empty frame (Fault)"
            else:
                replaced = queue.pop(0)
                idx = frames.index(replaced)
                frames[idx] = page
                explanation = f"Page {page} caused fault, replaced Page {replaced} using FIFO"
            queue.append(page)
        steps.append({
            "step": i + 1,
            "page": page,
            "frames": list(frames),
            "result": result,
            "replaced": replaced,
            "explanation": explanation,
        })
    return steps, faults, hits


def lru(pages, capacity):
    """Least Recently Used replacement."""
    frames, recent, steps, faults, hits = [], [], [], 0, 0
    for i, page in enumerate(pages):
        replaced, explanation = "-", ""
        if page in frames:
            hits += 1
            result = "Hit"
            recent.remove(page)
            recent.append(page)
            explanation = f"Page {page} found -> Hit (marked most recent)"
        else:
            faults += 1
            result = "Fault"
            if len(frames) < capacity:
                frames.append(page)
                explanation = f"Page {page} loaded into empty frame (Fault)"
            else:
                replaced = recent.pop(0)
                idx = frames.index(replaced)
                frames[idx] = page
                explanation = f"Page {page} caused fault, replaced LRU page {replaced}"
            recent.append(page)
        steps.append({
            "step": i + 1,
            "page": page,
            "frames": list(frames),
            "result": result,
            "replaced": replaced,
            "explanation": explanation,
        })
    return steps, faults, hits


def optimal(pages, capacity):
    """Belady's Optimal page replacement."""
    frames, steps, faults, hits = [], [], 0, 0
    for i, page in enumerate(pages):
        replaced, explanation = "-", ""
        if page in frames:
            hits += 1
            result = "Hit"
            explanation = f"Page {page} found -> Hit"
        else:
            faults += 1
            result = "Fault"
            if len(frames) < capacity:
                frames.append(page)
                explanation = f"Page {page} loaded into empty frame (Fault)"
            else:
                # find the page used farthest in the future
                future = pages[i + 1:]
                farthest_idx, victim = -1, None
                for f in frames:
                    if f not in future:
                        victim = f
                        break
                    else:
                        idx = future.index(f)
                        if idx > farthest_idx:
                            farthest_idx, victim = idx, f
                replaced = victim
                idx = frames.index(victim)
                frames[idx] = page
                explanation = f"Page {page} replaced Page {victim} (used farthest in future)"
        steps.append({
            "step": i + 1,
            "page": page,
            "frames": list(frames),
            "result": result,
            "replaced": replaced,
            "explanation": explanation,
        })
    return steps, faults, hits


ALGOS = {"FIFO": fifo, "LRU": lru, "Optimal": optimal}


# ===========================================================================
# MAIN APPLICATION
# ===========================================================================
class PageReplacementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Page Replacement Algorithm Simulator")
        self.geometry("1400x860")
        self.minsize(1200, 760)
        self.configure(bg=BG_DARK)

        self.steps = []
        self.current_step = 0
        self.animation_running = False
        self.last_results = {}        # algorithm -> (steps, faults, hits)

        self._setup_styles()
        self._build_header()
        self._build_body()
        self._build_footer()

    # -----------------------------------------------------------------------
    # STYLES
    # -----------------------------------------------------------------------
    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=BG_DARK)
        style.configure("Panel.TFrame", background=BG_PANEL)
        style.configure("Card.TFrame", background=BG_CARD)

        style.configure("TLabel", background=BG_PANEL, foreground=TEXT_LIGHT,
                        font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=BG_CARD, foreground=TEXT_LIGHT)
        style.configure("Header.TLabel", background=BG_DARK, foreground=TEXT_LIGHT,
                        font=("Segoe UI", 18, "bold"))
        style.configure("SubHeader.TLabel", background=BG_DARK, foreground=TEXT_MUTED,
                        font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=BG_PANEL, foreground=ACCENT,
                        font=("Segoe UI", 11, "bold"))
        style.configure("Muted.TLabel", background=BG_PANEL, foreground=TEXT_MUTED,
                        font=("Segoe UI", 9))

        style.configure("TEntry", fieldbackground=BG_CARD, foreground=TEXT_LIGHT,
                        insertcolor=TEXT_LIGHT, bordercolor=BORDER)
        style.configure("TRadiobutton", background=BG_PANEL, foreground=TEXT_LIGHT,
                        font=("Segoe UI", 10))
        style.map("TRadiobutton", background=[("active", BG_PANEL)])

        style.configure("TCheckbutton", background=BG_PANEL, foreground=TEXT_LIGHT)
        style.map("TCheckbutton", background=[("active", BG_PANEL)])

        style.configure("Accent.TButton", background=ACCENT, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=8, borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)])

        style.configure("Ghost.TButton", background=BG_CARD, foreground=TEXT_LIGHT,
                        font=("Segoe UI", 10), padding=8, borderwidth=0)
        style.map("Ghost.TButton",
                  background=[("active", BORDER), ("pressed", BORDER)])

        # Treeview
        style.configure("Treeview",
                        background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TEXT_LIGHT, bordercolor=BORDER,
                        rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background=BG_PANEL, foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", ACCENT_DARK)])

        style.configure("TScale", background=BG_PANEL)

    # -----------------------------------------------------------------------
    # HEADER
    # -----------------------------------------------------------------------
    def _build_header(self):
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=20, pady=(16, 8))

        title = ttk.Label(header, text="Page Replacement Algorithm Simulator",
                          style="Header.TLabel")
        title.pack(side="left")

        sub = ttk.Label(header,
                        text="FIFO  •  LRU  •  Optimal     |     Operating Systems Mini-Project",
                        style="SubHeader.TLabel")
        sub.pack(side="right", pady=(8, 0))

    # -----------------------------------------------------------------------
    # BODY
    # -----------------------------------------------------------------------
    def _build_body(self):
        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True, padx=20, pady=8)

        body.columnconfigure(0, weight=0, minsize=300)
        body.columnconfigure(1, weight=3)
        body.columnconfigure(2, weight=2, minsize=380)
        body.rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_center_panel(body)
        self._build_right_panel(body)

    # ---------------- LEFT PANEL ----------------
    def _build_left_panel(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(panel, text="INPUT", style="Section.TLabel").pack(anchor="w")
        ttk.Label(panel, text="Configure your simulation",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 12))

        # Frame count
        ttk.Label(panel, text="Number of Frames").pack(anchor="w", pady=(6, 4))
        self.frames_var = tk.StringVar(value="3")
        ttk.Entry(panel, textvariable=self.frames_var).pack(fill="x")

        # Reference string
        ttk.Label(panel, text="Page Reference String").pack(anchor="w", pady=(12, 4))
        ttk.Label(panel, text="comma-separated, e.g.  7,0,1,2,0,3,0,4",
                  style="Muted.TLabel").pack(anchor="w")
        self.refstr_var = tk.StringVar(value="7,0,1,2,0,3,0,4,2,3,0,3,2")
        ttk.Entry(panel, textvariable=self.refstr_var).pack(fill="x", pady=(4, 0))

        # Algorithm
        ttk.Label(panel, text="Algorithm").pack(anchor="w", pady=(14, 4))
        self.algo_var = tk.StringVar(value="FIFO")
        for name in ("FIFO", "LRU", "Optimal"):
            ttk.Radiobutton(panel, text=name, value=name,
                            variable=self.algo_var).pack(anchor="w")

        # Animation controls
        ttk.Label(panel, text="Animation", style="Section.TLabel").pack(
            anchor="w", pady=(20, 4))
        self.anim_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, text="Enable step animation",
                        variable=self.anim_var).pack(anchor="w")

        ttk.Label(panel, text="Speed (ms per step)").pack(anchor="w", pady=(6, 0))
        self.speed_var = tk.IntVar(value=600)
        ttk.Scale(panel, from_=100, to=1500, variable=self.speed_var,
                  orient="horizontal").pack(fill="x")

        # Buttons
        ttk.Button(panel, text="Run Simulation", style="Accent.TButton",
                   command=self.run_simulation).pack(fill="x", pady=(20, 6))
        ttk.Button(panel, text="Compare All Algorithms", style="Accent.TButton",
                   command=self.compare_all).pack(fill="x", pady=6)
        ttk.Button(panel, text="Reset / Clear", style="Ghost.TButton",
                   command=self.reset_all).pack(fill="x", pady=6)

        ttk.Separator(panel).pack(fill="x", pady=12)

        # Color legend
        ttk.Label(panel, text="LEGEND", style="Section.TLabel").pack(anchor="w")
        for color, label in [(HIT_COLOR, "Hit"), (FAULT_COLOR, "Fault"),
                             (REPLACED_COL, "Replaced Page"),
                             (CURRENT_COL, "Current Page")]:
            row = ttk.Frame(panel, style="Panel.TFrame")
            row.pack(anchor="w", pady=2, fill="x")
            tk.Label(row, bg=color, width=2, height=1).pack(side="left", padx=(0, 8))
            ttk.Label(row, text=label).pack(side="left")

        # Export buttons
        ttk.Label(panel, text="EXPORT", style="Section.TLabel").pack(
            anchor="w", pady=(16, 6))
        ttk.Button(panel, text="Export as CSV", style="Ghost.TButton",
                   command=self.export_csv).pack(fill="x", pady=3)
        ttk.Button(panel, text="Export as Text", style="Ghost.TButton",
                   command=self.export_txt).pack(fill="x", pady=3)

    # ---------------- CENTER PANEL ----------------
    def _build_center_panel(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        panel.grid(row=0, column=1, sticky="nsew", padx=5)
        panel.rowconfigure(2, weight=1)
        panel.columnconfigure(0, weight=1)

        ttk.Label(panel, text="STEP-BY-STEP SIMULATION",
                  style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(panel, text="Each row is one access in the reference string",
                  style="Muted.TLabel").grid(row=0, column=0, sticky="e")

        # Frame visualization
        frame_vis = ttk.Frame(panel, style="Card.TFrame", padding=12)
        frame_vis.grid(row=1, column=0, sticky="ew", pady=(10, 10))
        ttk.Label(frame_vis, text="Memory Frames",
                  style="Card.TLabel",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.frame_box_container = tk.Frame(frame_vis, bg=BG_CARD)
        self.frame_box_container.pack(fill="x", pady=(8, 0))
        self._render_frame_boxes([], int(self.frames_var.get() or 3))

        # Steps table
        cols = ("step", "page", "f1", "f2", "f3", "result", "replaced", "explanation")
        self.tree = ttk.Treeview(panel, columns=cols, show="headings", height=12)
        headings = ["Step", "Current Page", "Frame 1", "Frame 2", "Frame 3",
                    "Result", "Replaced", "Explanation"]
        widths = [50, 90, 70, 70, 70, 70, 80, 360]
        for c, h, w in zip(cols, headings, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center" if c != "explanation" else "w")

        self.tree.tag_configure("hit", background="#14532d", foreground="white")
        self.tree.tag_configure("fault", background="#7f1d1d", foreground="white")

        vsb = ttk.Scrollbar(panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=2, column=0, sticky="nsew")
        vsb.grid(row=2, column=1, sticky="ns")

        # Explanation panel
        exp_card = ttk.Frame(panel, style="Card.TFrame", padding=12)
        exp_card.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Label(exp_card, text="Explanation", style="Card.TLabel",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.explain_var = tk.StringVar(
            value="Run a simulation to see step-by-step explanations.")
        tk.Label(exp_card, textvariable=self.explain_var, bg=BG_CARD,
                 fg=TEXT_LIGHT, wraplength=700, justify="left",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))

    # ---------------- RIGHT PANEL ----------------
    def _build_right_panel(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(3, weight=1)

        # Summary
        ttk.Label(panel, text="SUMMARY", style="Section.TLabel").grid(
            row=0, column=0, sticky="w")

        sum_card = ttk.Frame(panel, style="Card.TFrame", padding=12)
        sum_card.grid(row=1, column=0, sticky="ew", pady=(6, 12))
        sum_cols = ("algo", "faults", "hitratio")
        self.sum_tree = ttk.Treeview(sum_card, columns=sum_cols,
                                     show="headings", height=4)
        for c, h, w in zip(sum_cols, ("Algorithm", "Page Faults", "Hit Ratio"),
                           (110, 100, 100)):
            self.sum_tree.heading(c, text=h)
            self.sum_tree.column(c, width=w, anchor="center")
        self.sum_tree.pack(fill="x")
        self.sum_tree.tag_configure("best", background="#166534", foreground="white",
                                    font=("Segoe UI", 10, "bold"))

        # Best algorithm highlight
        self.best_var = tk.StringVar(value="Best Algorithm: —")
        self.best_label = tk.Label(panel, textvariable=self.best_var,
                                   bg=ACCENT, fg="white",
                                   font=("Segoe UI", 11, "bold"),
                                   pady=8)
        self.best_label.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        # Performance graph
        ttk.Label(panel, text="PERFORMANCE", style="Section.TLabel").grid(
            row=3, column=0, sticky="nw")
        graph_card = ttk.Frame(panel, style="Card.TFrame", padding=8)
        graph_card.grid(row=4, column=0, sticky="nsew")
        panel.rowconfigure(4, weight=1)

        self.fig = Figure(figsize=(4, 3), dpi=90, facecolor=BG_CARD)
        self.ax = self.fig.add_subplot(111)
        self._style_axes()
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _style_axes(self):
        self.ax.set_facecolor(BG_CARD)
        for s in self.ax.spines.values():
            s.set_color(BORDER)
        self.ax.tick_params(colors=TEXT_LIGHT)
        self.ax.yaxis.label.set_color(TEXT_LIGHT)
        self.ax.xaxis.label.set_color(TEXT_LIGHT)
        self.ax.title.set_color(TEXT_LIGHT)

    # ---------------- FOOTER ----------------
    def _build_footer(self):
        panel = ttk.Frame(self, style="Panel.TFrame", padding=12)
        panel.pack(fill="x", padx=20, pady=(8, 16))

        ttk.Label(panel, text="COMPARISON (H = Hit, F = Fault)",
                  style="Section.TLabel").pack(anchor="w")
        ttk.Label(panel,
                  text="Side-by-side hit/fault per access for all three algorithms",
                  style="Muted.TLabel").pack(anchor="w", pady=(0, 6))

        cmp_holder = ttk.Frame(panel, style="Card.TFrame", padding=8)
        cmp_holder.pack(fill="x")
        self.cmp_tree = ttk.Treeview(cmp_holder, show="headings", height=5)
        self.cmp_tree.pack(fill="x")

    # =======================================================================
    # ACTIONS
    # =======================================================================
    def _parse_inputs(self):
        try:
            cap = int(self.frames_var.get())
            if cap <= 0 or cap > 10:
                raise ValueError("Frames must be between 1 and 10.")
        except ValueError as e:
            messagebox.showerror("Invalid input",
                                 f"Number of Frames: {e}")
            return None, None
        try:
            raw = self.refstr_var.get().replace(" ", "")
            pages = [int(x) for x in raw.split(",") if x != ""]
            if not pages:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input",
                                 "Reference string must be comma-separated integers.")
            return None, None
        return pages, cap

    def run_simulation(self):
        pages, cap = self._parse_inputs()
        if pages is None:
            return

        algo_name = self.algo_var.get()
        steps, faults, hits = ALGOS[algo_name](pages, cap)
        self.steps = steps
        self.last_results[algo_name] = (steps, faults, hits)

        self._rebuild_table_columns(cap)
        self._populate_summary_single(algo_name, faults, hits, len(pages))

        # Clear table and animate / fill
        for row in self.tree.get_children():
            self.tree.delete(row)

        if self.anim_var.get():
            self._animate_steps(0, cap)
        else:
            for s in steps:
                self._insert_step_row(s, cap)
            if steps:
                self._render_frame_boxes(steps[-1]["frames"], cap)
                self.explain_var.set(steps[-1]["explanation"])

    def _animate_steps(self, idx, cap):
        if idx >= len(self.steps):
            return
        s = self.steps[idx]
        self._insert_step_row(s, cap)
        self._render_frame_boxes(s["frames"], cap, current=s["page"],
                                 replaced=s["replaced"])
        self.explain_var.set(f"Step {s['step']}: {s['explanation']}")
        delay = self.speed_var.get()
        self.after(delay, lambda: self._animate_steps(idx + 1, cap))

    def _rebuild_table_columns(self, cap):
        # Adjust frame columns based on capacity
        cols = ["step", "page"] + [f"f{i+1}" for i in range(cap)] + \
               ["result", "replaced", "explanation"]
        self.tree.configure(columns=cols)
        headings = ["Step", "Current Page"] + [f"Frame {i+1}" for i in range(cap)] + \
                   ["Result", "Replaced", "Explanation"]
        widths = [50, 90] + [70] * cap + [70, 80, 320]
        anchors = ["center", "center"] + ["center"] * cap + ["center", "center", "w"]
        for c, h, w, a in zip(cols, headings, widths, anchors):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor=a)

    def _insert_step_row(self, s, cap):
        frames_padded = list(s["frames"]) + ["-"] * (cap - len(s["frames"]))
        values = [s["step"], s["page"]] + frames_padded + \
                 [s["result"], s["replaced"], s["explanation"]]
        tag = "hit" if s["result"] == "Hit" else "fault"
        self.tree.insert("", "end", values=values, tags=(tag,))
        self.tree.see(self.tree.get_children()[-1])

    def _render_frame_boxes(self, frames, capacity, current=None, replaced=None):
        for w in self.frame_box_container.winfo_children():
            w.destroy()
        if current is not None:
            tk.Label(self.frame_box_container, text=f"Page {current}",
                     bg=CURRENT_COL, fg="black", padx=14, pady=10,
                     font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 18))

        for i in range(capacity):
            val = frames[i] if i < len(frames) else "-"
            color = BG_PANEL
            fg = TEXT_LIGHT
            if val != "-" and replaced != "-" and val == current:
                color = HIT_COLOR
            elif replaced != "-" and val == current:
                color = REPLACED_COL
                fg = "black"
            box = tk.Frame(self.frame_box_container, bg=color,
                           highlightthickness=2, highlightbackground=BORDER)
            box.pack(side="left", padx=6)
            tk.Label(box, text=f"Frame {i+1}", bg=color, fg=TEXT_MUTED,
                     font=("Segoe UI", 8)).pack(padx=18, pady=(8, 0))
            tk.Label(box, text=str(val), bg=color, fg=fg,
                     font=("Segoe UI", 16, "bold")).pack(padx=18, pady=(0, 8))

    # ---------------- SUMMARY / GRAPH ----------------
    def _populate_summary_single(self, algo, faults, hits, total):
        for r in self.sum_tree.get_children():
            self.sum_tree.delete(r)
        ratio = hits / total if total else 0
        self.sum_tree.insert("", "end",
                             values=(algo, faults, f"{ratio:.2%}"))
        self.best_var.set(f"Best Algorithm: {algo}  (only one run)")
        self.best_label.configure(bg=ACCENT)

        # graph
        self.ax.clear()
        self._style_axes()
        self.ax.bar([algo], [faults], color=ACCENT)
        self.ax.set_title("Page Faults", color=TEXT_LIGHT)
        self.ax.set_ylabel("Faults")
        self.canvas.draw()

    def compare_all(self):
        pages, cap = self._parse_inputs()
        if pages is None:
            return

        results = {}
        for name, fn in ALGOS.items():
            steps, faults, hits = fn(pages, cap)
            results[name] = (steps, faults, hits)
        self.last_results = results

        # Summary table
        for r in self.sum_tree.get_children():
            self.sum_tree.delete(r)
        total = len(pages)
        best_name, best_faults = None, float("inf")
        for name, (_, faults, hits) in results.items():
            ratio = hits / total if total else 0
            tag = ()
            self.sum_tree.insert("", "end",
                                 values=(name, faults, f"{ratio:.2%}"),
                                 tags=tag)
            if faults < best_faults:
                best_faults, best_name = faults, name

        # Highlight best row
        for iid in self.sum_tree.get_children():
            vals = self.sum_tree.item(iid, "values")
            if vals[0] == best_name:
                self.sum_tree.item(iid, tags=("best",))
        self.best_var.set(f"Best Algorithm: {best_name}  ({best_faults} faults)")
        self.best_label.configure(bg=HIT_COLOR)

        # Graph
        self.ax.clear()
        self._style_axes()
        names = list(results.keys())
        faults_list = [results[n][1] for n in names]
        bar_colors = [HIT_COLOR if n == best_name else ACCENT for n in names]
        bars = self.ax.bar(names, faults_list, color=bar_colors)
        self.ax.set_title("Page Faults Comparison", color=TEXT_LIGHT)
        self.ax.set_ylabel("Faults")
        for b, v in zip(bars, faults_list):
            self.ax.text(b.get_x() + b.get_width() / 2, v + 0.05, str(v),
                         ha="center", color=TEXT_LIGHT)
        self.canvas.draw()

        # Comparison footer table
        self._populate_comparison_table(pages, results)

        # Single-algo simulation table also runs the currently selected algo
        self.steps = results[self.algo_var.get()][0]
        self._rebuild_table_columns(cap)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in self.steps:
            self._insert_step_row(s, cap)
        if self.steps:
            self._render_frame_boxes(self.steps[-1]["frames"], cap)
            self.explain_var.set(
                f"Showing {self.algo_var.get()} steps. Compare totals on the right.")

    def _populate_comparison_table(self, pages, results):
        cols = ["algo"] + [f"p{i+1}" for i in range(len(pages))] + ["faults"]
        headings = ["Algorithm"] + [str(p) for p in pages] + ["Total Faults"]
        widths = [90] + [38] * len(pages) + [100]
        self.cmp_tree.configure(columns=cols)
        for c, h, w in zip(cols, headings, widths):
            self.cmp_tree.heading(c, text=h)
            self.cmp_tree.column(c, width=w, anchor="center")
        for r in self.cmp_tree.get_children():
            self.cmp_tree.delete(r)
        self.cmp_tree.tag_configure("hit", background="#14532d", foreground="white")
        self.cmp_tree.tag_configure("fault", background="#7f1d1d", foreground="white")

        for name, (steps, faults, _hits) in results.items():
            row = [name] + ["H" if s["result"] == "Hit" else "F" for s in steps] + [faults]
            self.cmp_tree.insert("", "end", values=row)

    # ---------------- RESET / EXPORT ----------------
    def reset_all(self):
        self.frames_var.set("3")
        self.refstr_var.set("")
        self.algo_var.set("FIFO")
        for r in self.tree.get_children():
            self.tree.delete(r)
        for r in self.sum_tree.get_children():
            self.sum_tree.delete(r)
        for r in self.cmp_tree.get_children():
            self.cmp_tree.delete(r)
        self.steps = []
        self.last_results = {}
        self.explain_var.set("Cleared. Enter inputs and run a simulation.")
        self.best_var.set("Best Algorithm: —")
        self.best_label.configure(bg=ACCENT)
        self.ax.clear()
        self._style_axes()
        self.canvas.draw()
        self._render_frame_boxes([], int(self.frames_var.get() or 3))

    def export_csv(self):
        if not self.steps:
            messagebox.showinfo("Nothing to export",
                                "Run a simulation first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Step", "Page", "Frames", "Result", "Replaced", "Explanation"])
            for s in self.steps:
                w.writerow([s["step"], s["page"], " ".join(map(str, s["frames"])),
                            s["result"], s["replaced"], s["explanation"]])
        messagebox.showinfo("Exported", f"Saved to {path}")

    def export_txt(self):
        if not self.steps:
            messagebox.showinfo("Nothing to export",
                                "Run a simulation first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("Page Replacement Simulation Results\n")
            f.write("=" * 60 + "\n\n")
            for s in self.steps:
                f.write(f"Step {s['step']:>3} | Page {s['page']} | "
                        f"Frames: {s['frames']} | {s['result']} | "
                        f"Replaced: {s['replaced']}\n   -> {s['explanation']}\n")
            if self.last_results:
                f.write("\nSummary\n" + "-" * 60 + "\n")
                for name, (_, faults, hits) in self.last_results.items():
                    total = faults + hits
                    ratio = hits / total if total else 0
                    f.write(f"{name:<8} faults={faults}  hits={hits}  "
                            f"hit_ratio={ratio:.2%}\n")
        messagebox.showinfo("Exported", f"Saved to {path}")


# ===========================================================================
if __name__ == "__main__":
    app = PageReplacementApp()
    app.mainloop()
