"""
PMhelper Edu — Dashboard Tab.
Project health summary with expandable mini-chart cards.
Click any card to view fullscreen; press Esc or click X to return.
"""

import tkinter as tk
from tkinter import ttk

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.evm_calculations_edu import compute_all_kpis, get_rag

# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import PLOTLY_AVAILABLE as _PLT_AVAIL
    _PLOTLY_EMBED = WEBVIEW2_AVAILABLE and _PLT_AVAIL
except ImportError:
    _PLOTLY_EMBED = False

# RAG badge colours
_RAG_COLOURS = {
    "green": "#2ecc71",
    "amber": "#f39c12",
    "red": "#e74c3c",
    "grey": "#95a5a6",
}

# The 6 headline KPIs for the dashboard strip
_DASHBOARD_KPIS = [
    ("cpi", "CPI"),
    ("spi", "SPI"),
    ("cv", "CV"),
    ("sv", "SV"),
    ("pc", "% Complete"),
    ("eac1", "EAC\u2081"),
]


class DashboardTabEdu:
    """Project health summary dashboard with expandable chart cards."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self._mode = "UG"
        self.frame = ttk.Frame(parent)
        self._build_ui()

    # ================================================================
    #  UI Construction
    # ================================================================

    def _build_ui(self):
        # Title + refresh
        hdr = ttk.Frame(self.frame)
        hdr.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(hdr, text="Project Health Dashboard",
                  font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Button(hdr, text="\U0001f504 Refresh",
                   command=self._refresh).pack(side=tk.RIGHT)

        # ── KPI Strip ──
        kpi_lf = ttk.LabelFrame(self.frame, text="Key Performance Indicators",
                                padding=5)
        kpi_lf.pack(fill=tk.X, padx=10, pady=5)

        self._kpi_cards = {}
        for idx, (key, label) in enumerate(_DASHBOARD_KPIS):
            card = ttk.Frame(kpi_lf, relief="groove", borderwidth=1)
            card.grid(row=0, column=idx, padx=4, pady=4, sticky="nsew")
            ttk.Label(card, text=label,
                      font=("Arial", 9, "bold")).pack(pady=(4, 0))
            val_lbl = ttk.Label(card, text="\u2014",
                                font=("Arial", 16, "bold"))
            val_lbl.pack(pady=2)
            badge = tk.Label(card, text="  ", width=6,
                             bg=_RAG_COLOURS["grey"], fg="white",
                             font=("Arial", 8, "bold"))
            badge.pack(pady=(0, 4))
            self._kpi_cards[key] = {"value": val_lbl, "badge": badge}
        for c in range(len(_DASHBOARD_KPIS)):
            kpi_lf.columnconfigure(c, weight=1)

        # ── Scrollable card grid ──
        canvas_outer = ttk.Frame(self.frame)
        canvas_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._dash_canvas = tk.Canvas(canvas_outer, highlightthickness=0)
        vsb = ttk.Scrollbar(canvas_outer, orient=tk.VERTICAL,
                            command=self._dash_canvas.yview)
        self._dash_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._dash_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._grid_frame = ttk.Frame(self._dash_canvas)
        self._dash_canvas.create_window((0, 0), window=self._grid_frame,
                                        anchor="nw")
        self._grid_frame.bind("<Configure>",
                              lambda e: self._dash_canvas.configure(
                                  scrollregion=self._dash_canvas.bbox("all")))
        self._dash_canvas.bind("<MouseWheel>",
                               lambda e: self._dash_canvas.yview_scroll(
                                   int(-1 * (e.delta / 120)), "units"))

        self._build_cards()

        # ── Info bar ──
        self._info_lbl = ttk.Label(self.frame, text="", foreground="grey",
                                   font=("Arial", 9, "italic"))
        self._info_lbl.pack(fill=tk.X, padx=10, pady=(0, 5))

    # ----------------------------------------------------------------
    #  Card infrastructure
    # ----------------------------------------------------------------

    def _build_cards(self):
        grid = self._grid_frame
        for c in range(3):
            grid.columnconfigure(c, weight=1, uniform="card")

        self._scurve_card = self._make_card(
            grid,
            0,
            0,
            "\U0001f4c8 S-Curve",
            self._draw_mini_scurve,
            self._expand_scurve)
        self._risk_card = self._make_card(
            grid,
            0,
            1,
            "\U0001f6e1 Risk Summary",
            self._draw_mini_risk,
            self._expand_risk)
        self._schedule_card = self._make_card(
            grid,
            0,
            2,
            "\U0001f4cb Schedule Summary",
            self._draw_mini_schedule,
            self._expand_schedule)
        self._swot_card = self._make_card(
            grid,
            1,
            0,
            "\U0001f532 SWOT Analysis",
            self._draw_mini_swot,
            self._expand_swot)
        self._pestel_card = self._make_card(
            grid,
            1,
            1,
            "\U0001f30d PESTEL Analysis",
            self._draw_mini_pestel,
            self._expand_pestel)
        self._mc_card = self._make_card(
            grid,
            1,
            2,
            "\U0001f3b2 Monte Carlo",
            self._draw_mini_mc,
            self._expand_mc)
        self._wbs_card = self._make_card(
            grid,
            2,
            0,
            "\U0001f5c2 WBS Overview",
            self._draw_mini_wbs,
            self._expand_wbs)

    def _make_card(self, parent, row, col, title, draw_fn, expand_fn):
        outer = ttk.Frame(parent, relief="groove", borderwidth=2)
        outer.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        title_bar = ttk.Frame(outer)
        title_bar.pack(fill=tk.X, padx=4, pady=(4, 0))
        ttk.Label(title_bar, text=title,
                  font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Button(title_bar, text="\u26f6", width=3,
                   command=expand_fn).pack(side=tk.RIGHT)

        content = ttk.Frame(outer, height=200)
        content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        content.pack_propagate(False)

        for widget in (outer, content):
            widget.bind("<Button-1>", lambda e, fn=expand_fn: fn())

        return {"frame": content, "outer": outer,
                "draw": draw_fn, "expand": expand_fn}

    def _expand_to_fullscreen(self, title, build_fn):
        win = tk.Toplevel(self.frame)
        win.title(title)
        try:
            win.state("zoomed")
        except tk.TclError:
            win.geometry("1200x800")
        win.grab_set()

        top = ttk.Frame(win)
        top.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(top, text=title,
                  font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(
            top,
            text="\u2715 Close",
            command=win.destroy).pack(
            side=tk.RIGHT)

        body = ttk.Frame(win)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        build_fn(body)

        win.bind("<Escape>", lambda e: win.destroy())

    # ================================================================
    #  Mini-chart draw functions
    # ================================================================

    def _draw_mini_scurve(self):
        frame = self._scurve_card["frame"]
        for w in frame.winfo_children():
            w.destroy()
        proj = self.state.evm_project
        if not HAS_MATPLOTLIB or proj is None or not proj.periods:
            ttk.Label(frame, text="No period data available",
                      foreground="grey").pack(expand=True)
            return
        fig = Figure(figsize=(3.5, 1.8), dpi=80)
        ax = fig.add_subplot(111)
        periods = proj.periods
        x = list(range(len(periods)))
        ax.plot(x, [p.pv_cumulative for p in periods], "g--", lw=1, label="PV")
        ax.plot(x, [p.ev_cumulative for p in periods], "b-", lw=1, label="EV")
        ax.plot(x, [p.ac_cumulative for p in periods], "r-", lw=1, label="AC")
        ax.legend(fontsize=6, loc="upper left")
        ax.tick_params(labelsize=6)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, frame)
        c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        c.draw()

    def _draw_mini_risk(self):
        frame = self._risk_card["frame"]
        for w in frame.winfo_children():
            w.destroy()
        reg = self.state.risk_register
        if reg is None or not reg.risks:
            ttk.Label(frame, text="No risks registered",
                      foreground="grey").pack(expand=True)
            return
        sym = "$"
        if self.state.evm_project:
            sym = self.state.evm_project.currency_symbol
        exposure = reg.total_exposure()
        contingency = reg.contingency_reserve()
        flagged = len(reg.flag_high_exposure())
        lines = [
            f"Total Risks: {len(reg.risks)}",
            f"Total Exposure: {sym}{exposure:,.2f}",
            f"Contingency: {sym}{contingency:,.2f}",
            f"High-Exposure: {flagged}",
        ]
        from collections import Counter
        cats = Counter(r.category.value for r in reg.risks)
        for cat, cnt in sorted(cats.items()):
            lines.append(f"  {cat}: {cnt}")
        for line in lines:
            fg = "red" if "High-Exposure" in line and flagged > 0 else ""
            ttk.Label(
                frame,
                text=line,
                font=(
                    "Arial",
                    9),
                foreground=fg if fg else "").pack(
                anchor="w",
                padx=4,
                pady=1)

    def _draw_mini_schedule(self):
        frame = self._schedule_card["frame"]
        for w in frame.winfo_children():
            w.destroy()
        rd = self.state.results_data
        if not rd:
            ttk.Label(
                frame,
                text="No analysis results yet\n(Run CPM/PERT first)",
                foreground="grey").pack(
                expand=True)
            return
        dur = rd.get("project_duration", "?")
        n_acts = len(rd.get("activities", []))
        n_crit = len(rd.get("critical_activities", set()))
        lines = [
            f"Project Duration: {dur}",
            f"Activities: {n_acts}",
            f"Critical: {n_crit}",
        ]
        if "expected_duration" in rd:
            lines.append(f"Expected: {rd['expected_duration']:.2f}")
            lines.append(f"Std Dev: {rd.get('standard_deviation', 0):.2f}")
        cp = rd.get("critical_path", [])
        if cp:
            path_str = " \u2192 ".join(str(n) for n in cp)
            if len(path_str) > 50:
                path_str = path_str[:47] + "\u2026"
            lines.append(f"CP: {path_str}")
        for line in lines:
            ttk.Label(frame, text=line, font=("Arial", 9)).pack(
                anchor="w", padx=4, pady=1)

    def _draw_mini_swot(self):
        frame = self._swot_card["frame"]
        for w in frame.winfo_children():
            w.destroy()
        swot = self.state.swot_analysis
        if swot is None:
            ttk.Label(frame, text="No SWOT analysis",
                      foreground="grey").pack(expand=True)
            return
        for name, items, colour in [
            ("Strengths", swot.strengths, "#22c55e"),
            ("Weaknesses", swot.weaknesses, "#ef4444"),
            ("Opportunities", swot.opportunities, "#3b82f6"),
            ("Threats", swot.threats, "#f59e0b"),
        ]:
            tk.Label(frame, text=f"\u25a0 {name}: {len(items)}",
                     fg=colour, font=("Arial", 10, "bold"),
                     anchor="w").pack(side=tk.TOP, anchor="w", padx=4, pady=2)

    def _draw_mini_pestel(self):
        frame = self._pestel_card["frame"]
        for w in frame.winfo_children():
            w.destroy()
        pestel = self.state.pestel_analysis
        if pestel is None or not pestel.factors:
            ttk.Label(frame, text="No PESTEL analysis",
                      foreground="grey").pack(expand=True)
            return
        from collections import Counter
        cats = Counter(f.category.value for f in pestel.factors)
        for cat in ["Political", "Economic", "Social",
                    "Technological", "Environmental", "Legal"]:
            cnt = cats.get(cat, 0)
            ttk.Label(frame, text=f"  {cat}: {cnt}",
                      font=("Arial", 9)).pack(anchor="w", padx=4, pady=1)
        total_exp = sum(f.impact * f.probability for f in pestel.factors)
        ttk.Label(frame, text=f"\nExposure: {total_exp:.1f}",
                  font=("Arial", 9, "bold")).pack(anchor="w", padx=4)

    def _draw_mini_mc(self):
        frame = self._mc_card["frame"]
        for w in frame.winfo_children():
            w.destroy()
        mc = self.state.mc_results
        if mc is None:
            ttk.Label(frame, text="No MC simulation yet",
                      foreground="grey").pack(expand=True)
            return
        ttk.Label(frame, text="\u2713 Simulation Complete",
                  font=("Arial", 9, "bold"),
                  foreground="green").pack(anchor="w", padx=4, pady=(2, 4))
        for line in [
            f"Trials: {mc.n_trials:,}",
            f"P50: {mc.p50_duration:.1f}",
            f"P80: {mc.p80_duration:.1f}",
            f"P90: {mc.p90_duration:.1f}",
            f"P(Cost\u2264BAC): {mc.p_cost_within_bac:.1%}",
        ]:
            ttk.Label(frame, text=line, font=("Arial", 9)).pack(
                anchor="w", padx=4, pady=1)

    def _draw_mini_wbs(self):
        frame = self._wbs_card["frame"]
        for w in frame.winfo_children():
            w.destroy()
        wbs = self.state.wbs_tree
        if wbs is None or wbs.root is None:
            ttk.Label(frame, text="No WBS defined",
                      foreground="grey").pack(expand=True)
            return

        def count_depth(node, depth=0, counts=None):
            if counts is None:
                counts = {}
            counts[depth] = counts.get(depth, 0) + 1
            for ch in node.children:
                count_depth(ch, depth + 1, counts)
            return counts
        counts = count_depth(wbs.root)
        total = sum(counts.values())
        for line in [f"Root: {wbs.root.name}",
                     f"Elements: {total}"] + [f"  Level {d}: {cnt}" for d,
                                              cnt in sorted(counts.items())]:
            ttk.Label(frame, text=line, font=("Arial", 9)).pack(
                anchor="w", padx=4, pady=1)

    # ================================================================
    #  Fullscreen expand functions
    # ================================================================

    def _expand_scurve(self):
        self._expand_to_fullscreen("S-Curve Overview", self._build_full_scurve)

    def _build_full_scurve(self, parent):
        proj = self.state.evm_project
        if not HAS_MATPLOTLIB or proj is None or not proj.periods:
            ttk.Label(parent, text="No period data available.",
                      font=("Arial", 14)).pack(expand=True)
            return
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        periods = proj.periods
        x = list(range(len(periods)))
        ax.plot(x, [p.pv_cumulative for p in periods], "g--", lw=2, label="PV")
        ax.plot(x, [p.ev_cumulative for p in periods], "b-", lw=2, label="EV")
        ax.plot(x, [p.ac_cumulative for p in periods], "r-", lw=2, label="AC")
        ax.set_xlabel("Period", fontsize=12)
        ax.set_ylabel("Cumulative Value", fontsize=12)
        ax.set_title("S-Curve (PV / EV / AC)", fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, parent)
        c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        c.draw()

    def _expand_risk(self):
        self._expand_to_fullscreen("Risk Summary", self._build_full_risk)

    def _build_full_risk(self, parent):
        reg = self.state.risk_register
        if reg is None or not reg.risks:
            ttk.Label(parent, text="No risks registered.",
                      font=("Arial", 14)).pack(expand=True)
            return
        sym = "$"
        if self.state.evm_project:
            sym = self.state.evm_project.currency_symbol

        summary_f = ttk.LabelFrame(parent, text="Summary", padding=10)
        summary_f.pack(fill=tk.X, padx=5, pady=5)
        exposure = reg.total_exposure()
        contingency = reg.contingency_reserve()
        flagged = reg.flag_high_exposure()
        for text in [
            f"Total Risks: {len(reg.risks)}",
            f"Total Exposure: {sym}{exposure:,.2f}",
            f"Contingency Reserve: {sym}{contingency:,.2f}",
            f"High-Exposure Risks: {len(flagged)}",
        ]:
            ttk.Label(summary_f, text=text, font=("Arial", 12)).pack(
                anchor="w", pady=2)

        from pmhelper.gui.widgets.sortable_treeview import SortableTreeview
        cols = ["id", "name", "category", "probability", "impact",
                "exposure", "score", "rank"]
        headings = ["ID", "Name", "Category", "Probability", "Impact",
                    "Exposure", "Score", "Rank"]
        tree = SortableTreeview(parent, columns=cols, headings=headings,
                                show_filter=True, show_export=True, height=20)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        reg.recompute_exposures()
        for r in reg.risks_by_score():
            tree.insert((
                r.id, r.name, r.category.value,
                f"{r.probability:.2f}", f"{sym}{r.impact:,.2f}",
                f"{sym}{r.exposure:,.2f}", f"{r.risk_score:.0f}",
                getattr(r, 'rank', ''),
            ))

    def _expand_schedule(self):
        self._expand_to_fullscreen(
            "Schedule Analysis",
            self._build_full_schedule)

    def _build_full_schedule(self, parent):
        rd = self.state.results_data
        if not rd:
            ttk.Label(parent, text="No analysis results.",
                      font=("Arial", 14)).pack(expand=True)
            return
        summary_f = ttk.LabelFrame(parent, text="Project Summary", padding=10)
        summary_f.pack(fill=tk.X, padx=5, pady=5)
        for text in [
            f"Project Duration: {rd.get('project_duration', '?')}",
            f"Activities: {len(rd.get('activities', []))}",
            f"Critical: {len(rd.get('critical_activities', set()))}",
        ]:
            ttk.Label(summary_f, text=text, font=("Arial", 12)).pack(
                anchor="w", pady=2)
        if "expected_duration" in rd:
            ttk.Label(summary_f,
                      text=f"Expected Duration: {rd['expected_duration']:.2f}",
                      font=("Arial", 12)).pack(anchor="w", pady=2)

        from pmhelper.gui.widgets.sortable_treeview import SortableTreeview
        activities = rd.get("activities", [])
        if activities and "optimistic" in activities[0]:
            cols = [
                "id",
                "name",
                "optimistic",
                "most_likely",
                "pessimistic",
                "expected",
                "variance",
                "ES",
                "EF",
                "LS",
                "LF",
                "float",
                "critical"]
            headings = ["ID", "Name", "O", "M", "P", "Exp", "Var",
                        "ES", "EF", "LS", "LF", "Float", "Critical"]
        else:
            cols = [
                "id",
                "name",
                "duration",
                "ES",
                "EF",
                "LS",
                "LF",
                "float",
                "critical"]
            headings = [
                "ID",
                "Name",
                "Dur",
                "ES",
                "EF",
                "LS",
                "LF",
                "Float",
                "Critical"]
        tree = SortableTreeview(parent, columns=cols, headings=headings,
                                show_filter=True, show_export=True, height=25)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        crit_set = rd.get("critical_activities", set())
        tree.tag_configure(
            "critical",
            background="#fee2e2",
            foreground="#b91c1c")
        for act in activities:
            vals = []
            for c in cols:
                v = act.get(c, "")
                if isinstance(v, float):
                    v = f"{v:.2f}"
                elif isinstance(v, bool):
                    v = "Yes" if v else "No"
                vals.append(v)
            tag = ("critical",) if act.get(
                "id") in crit_set or act.get("critical") else ()
            tree.insert(vals, tags=tag)

    def _expand_swot(self):
        self._expand_to_fullscreen("SWOT Analysis", self._build_full_swot)

    def _build_full_swot(self, parent):
        swot = self.state.swot_analysis
        if swot is None:
            ttk.Label(parent, text="No SWOT analysis.",
                      font=("Arial", 14)).pack(expand=True)
            return
        grid = ttk.Frame(parent)
        grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        grid.rowconfigure(0, weight=1)
        grid.rowconfigure(1, weight=1)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)
        for r, c, name, items in [
            (0, 0, "Strengths", swot.strengths),
            (0, 1, "Weaknesses", swot.weaknesses),
            (1, 0, "Opportunities", swot.opportunities),
            (1, 1, "Threats", swot.threats),
        ]:
            lf = ttk.LabelFrame(grid, text=f"{name} ({len(items)})")
            lf.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            txt = tk.Text(lf, wrap=tk.WORD, font=("Arial", 11), height=10)
            txt.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            for item in items:
                factor_text = item.text if hasattr(item, "text") else str(item)
                txt.insert(tk.END, f"\u2022 {factor_text}\n")
            txt.config(state=tk.DISABLED)

    def _expand_pestel(self):
        self._expand_to_fullscreen("PESTEL Analysis", self._build_full_pestel)

    def _build_full_pestel(self, parent):
        pestel = self.state.pestel_analysis
        if pestel is None or not pestel.factors:
            ttk.Label(parent, text="No PESTEL analysis.",
                      font=("Arial", 14)).pack(expand=True)
            return
        body = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True)
        from pmhelper.gui.widgets.sortable_treeview import SortableTreeview
        cols = ["category", "description", "impact", "probability", "exposure"]
        headings = [
            "Category",
            "Description",
            "Impact",
            "Probability",
            "Exposure"]
        tree = SortableTreeview(body, columns=cols, headings=headings,
                                show_filter=True, height=20)
        body.add(tree, weight=2)
        for f in pestel.factors:
            tree.insert(
                (f.category.value, f.description, str(
                    f.impact), str(
                    f.probability), f"{
                    f.impact * f.probability:.1f}"))
        if HAS_MATPLOTLIB:
            chart_f = ttk.Frame(body)
            body.add(chart_f, weight=1)
            self._build_pestel_radar(chart_f, pestel)

    def _build_pestel_radar(self, parent, pestel):
        from collections import Counter
        cats = Counter(f.category.value for f in pestel.factors)
        cat_order = ["Political", "Economic", "Social",
                     "Technological", "Environmental", "Legal"]
        values = [cats.get(c, 0) for c in cat_order]
        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111, polar=True)
        angles = np.linspace(
            0,
            2 * np.pi,
            len(cat_order),
            endpoint=False).tolist()
        values_plot = values + [values[0]]
        angles += angles[:1]
        ax.fill(angles, values_plot, alpha=0.25, color="#3b82f6")
        ax.plot(angles, values_plot, "o-", color="#3b82f6", lw=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(cat_order, fontsize=9)
        ax.set_title("PESTEL Factor Distribution", fontsize=12, pad=20)
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, parent)
        c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        c.draw()

    def _expand_mc(self):
        self._expand_to_fullscreen("Monte Carlo Summary", self._build_full_mc)

    def _build_full_mc(self, parent):
        mc = self.state.mc_results
        if mc is None:
            ttk.Label(parent, text="No MC simulation results.",
                      font=("Arial", 14)).pack(expand=True)
            return
        summary_f = ttk.LabelFrame(
            parent, text="Simulation Results", padding=10)
        summary_f.pack(fill=tk.X, padx=5, pady=5)
        for text in [
            f"Trials: {mc.n_trials:,}",
            f"P50 Duration: {mc.p50_duration:.1f}",
            f"P80 Duration: {mc.p80_duration:.1f}",
            f"P90 Duration: {mc.p90_duration:.1f}",
            f"P(Cost \u2264 BAC): {mc.p_cost_within_bac:.1%}",
        ]:
            ttk.Label(summary_f, text=text, font=("Arial", 12)).pack(
                anchor="w", pady=2)
        if HAS_MATPLOTLIB and hasattr(
                mc, "duration_samples") and mc.duration_samples is not None:
            chart_f = ttk.LabelFrame(parent, text="Duration Distribution")
            chart_f.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            fig = Figure(figsize=(10, 5), dpi=100)
            ax = fig.add_subplot(111)
            ax.hist(mc.duration_samples, bins=50, color="#3b82f6", alpha=0.7,
                    edgecolor="white")
            ax.axvline(mc.p50_duration, color="green", lw=2,
                       ls="--", label=f"P50={mc.p50_duration:.1f}")
            ax.axvline(mc.p80_duration, color="orange", lw=2,
                       ls="--", label=f"P80={mc.p80_duration:.1f}")
            ax.axvline(mc.p90_duration, color="red", lw=2,
                       ls="--", label=f"P90={mc.p90_duration:.1f}")
            ax.legend(fontsize=10)
            ax.set_xlabel("Duration", fontsize=12)
            ax.set_ylabel("Frequency", fontsize=12)
            ax.set_title("Duration Distribution", fontsize=14)
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            c = FigureCanvasTkAgg(fig, chart_f)
            c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            c.draw()

    def _expand_wbs(self):
        self._expand_to_fullscreen("WBS Overview", self._build_full_wbs)

    def _build_full_wbs(self, parent):
        wbs = self.state.wbs_tree
        if wbs is None or wbs.root is None:
            ttk.Label(parent, text="No WBS defined.",
                      font=("Arial", 14)).pack(expand=True)
            return
        tree = ttk.Treeview(parent, columns=("name", "dur", "cost", "status"),
                            show="tree headings")
        tree.heading("#0", text="WBS")
        tree.heading("name", text="Name")
        tree.heading("dur", text="Duration")
        tree.heading("cost", text="Cost")
        tree.heading("status", text="Status")
        tree.column("#0", width=120)
        tree.column("name", width=200)
        tree.column("dur", width=80, anchor=tk.E)
        tree.column("cost", width=100, anchor=tk.E)
        tree.column("status", width=100, anchor=tk.CENTER)
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        from pmhelper.gui.widgets.sortable_treeview import enhance_treeview
        enhance_treeview(tree)

        def _insert_node(parent_iid, node):
            iid = tree.insert(
                parent_iid, tk.END, text=node.wbs_code or "", values=(
                    node.name, getattr(
                        node, "duration", ""), getattr(
                        node, "cost", ""), getattr(
                        node, "status", "").name if hasattr(
                        getattr(
                            node, "status", None), "name") else str(
                                getattr(
                                    node, "status", ""))))
            for ch in node.children:
                _insert_node(iid, ch)
        _insert_node("", wbs.root)

    # ================================================================
    #  Refresh / public interface
    # ================================================================

    def _refresh(self):
        self._update_kpi_strip()
        self._draw_mini_scurve()
        self._draw_mini_risk()
        self._draw_mini_schedule()
        self._draw_mini_swot()
        self._draw_mini_pestel()
        self._draw_mini_mc()
        self._draw_mini_wbs()
        self._update_info_bar()

    def _update_kpi_strip(self):
        proj = self.state.evm_project
        if proj is None:
            for card in self._kpi_cards.values():
                card["value"].config(text="\u2014")
                card["badge"].config(bg=_RAG_COLOURS["grey"], text="  ")
            return

        kpis = compute_all_kpis(proj, primary_eac=1)
        bac = kpis.get("bac", 0)
        sym = proj.currency_symbol

        for key, card in self._kpi_cards.items():
            val = kpis.get(key)
            if val is None:
                display = "N/A"
            elif key in ("pc",):
                display = f"{val:.1f}%"
            elif key in ("cpi", "spi"):
                display = f"{val:.3f}"
            else:
                display = f"{sym}{val:,.2f}"

            card["value"].config(text=display)
            rag = get_rag(key, val, bac)
            colour = _RAG_COLOURS.get(rag, _RAG_COLOURS["grey"])
            card["badge"].config(bg=colour, text=rag.upper())

    def _update_info_bar(self):
        proj = self.state.evm_project
        if proj is None:
            self._info_lbl.config(text="No project loaded.")
            return

        n_tasks = len(proj.tasks)
        n_periods = len(proj.periods)
        name = proj.project_name
        mode = self._mode
        self._info_lbl.config(
            text=f"{name}  |  {n_tasks} tasks  |  {n_periods} periods  |  "
            f"Mode: {mode}")

    # ================================================================
    #  Tab interface
    # ================================================================

    def set_mode(self, mode: str):
        self._mode = mode

    def on_tab_selected(self):
        self._refresh()

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        return []
