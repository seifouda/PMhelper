"""
PMhelper Edu — Financial Analysis Tab (V2 Phase 3).

Two inner sub-tabs:

1. **Financial Calculators** (Phase 3A)
   * Inputs: initial investment, discount rate, cash-flow table (up to N periods)
   * Six metric checkboxes: Payback, Discounted Payback, ROI, NPV, IRR, PI
   * Results table: Metric / Value / Interpretation
   * Cumulative Cash-Flow bar chart (simple + discounted)
   * Worked Solution pop-up
   * Try It Yourself: student enters Payback & NPV, validated with ±0.01 tolerance

2. **Factor Scoring** (Phase 3B)
   * Criteria editor (name + weight column, shown for Weighted model)
   * Projects editor (project name per row)
   * Score matrix grid (auto-sized)
   * Model radio buttons: 0-1 / Factor / Weighted
   * Results Treeview + bar chart
   * Worked Solution pop-up
   * Try It Yourself: student enters total scores per project
"""

from __future__ import annotations

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple

from pmhelper.gui.widgets.sortable_treeview import enhance_treeview

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame, WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import (
        plotly_financial_cf,
        plotly_factor_scoring,
        PLOTLY_AVAILABLE as _PLT_AVAIL,
    )
    _PLOTLY_EMBED = WEBVIEW2_AVAILABLE and _PLT_AVAIL
except ImportError:
    _PLOTLY_EMBED = False


class FinancialTabEdu:
    """Outer tab container — owns two inner sub-tabs."""

    def __init__(self, parent, state, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self._mode = "UG"

        self.frame = ttk.Frame(parent)
        self._nb = ttk.Notebook(self.frame)
        self._nb.pack(fill=tk.BOTH, expand=True)

        self._fin = _FinancialCalcSubTab(self._nb, state)
        self._fs = _FactorScoringSubTab(self._nb, state)

        self._nb.add(self._fin.frame, text="Financial Calculators")
        self._nb.add(self._fs.frame, text="Factor Scoring")

    # ── Public interface ─────────────────────────────────────────

    def set_mode(self, mode: str):
        self._mode = mode.upper()
        for sub in (self._fin, self._fs):
            sub.set_mode(self._mode)

    def on_tab_selected(self):
        pass

    def get_figures(self) -> list:
        figs = []
        figs.extend(self._fin.get_figures())
        figs.extend(self._fs.get_figures())
        return figs


# ════════════════════════════════════════════════════════════════════
#  Sub-tab 1 — Financial Calculators
# ════════════════════════════════════════════════════════════════════

class _FinancialCalcSubTab:
    """Financial Calculators inner sub-tab."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self._result = None
        self._inputs = None
        self._worked_btn = None
        self._render_mode_var = tk.StringVar(value="matplotlib")

        self.frame = ttk.Frame(parent)
        self._build_ui()

    # ── Construction ─────────────────────────────────────────────

    def _build_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=6, pady=(5, 2))

        ttk.Button(toolbar, text="📂 Load Demo",
                   command=self._load_demo).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="▶ Calculate",
                   command=self._calculate).pack(side=tk.LEFT, padx=(0, 8))

        self._try_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            toolbar, text="🎓 Try It Yourself",
            variable=self._try_var, command=self._toggle_practice,
        ).pack(side=tk.RIGHT)

        # Scrollable container
        _scroll_outer = ttk.Frame(self.frame)
        _scroll_outer.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)
        _vsb = ttk.Scrollbar(_scroll_outer, orient=tk.VERTICAL)
        _vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tiy_canvas = tk.Canvas(_scroll_outer, yscrollcommand=_vsb.set,
                                     highlightthickness=0)
        self._tiy_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        _vsb.config(command=self._tiy_canvas.yview)
        self._inner_frame = ttk.Frame(self._tiy_canvas)
        self._tiy_win = self._tiy_canvas.create_window(
            (0, 0), window=self._inner_frame, anchor='nw')
        self._inner_frame.bind('<Configure>',
                               lambda e: self._tiy_canvas.configure(
                                   scrollregion=self._tiy_canvas.bbox('all')))
        self._tiy_canvas.bind(
            '<Configure>',
            lambda e: self._tiy_canvas.itemconfig(
                self._tiy_win,
                width=e.width))
        self._tiy_canvas.bind_all('<MouseWheel>', lambda e: self._tiy_canvas.yview_scroll(
            int(-1 * (e.delta / 120)), 'units'))

        content_frame = ttk.Frame(self._inner_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        pane = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        # Left: inputs + metric checkboxes
        left_frame = ttk.Frame(pane)
        pane.add(left_frame, weight=1)
        self._build_left_panel(left_frame)

        # Right: results + chart (vertical)
        right_pane = ttk.PanedWindow(pane, orient=tk.VERTICAL)
        pane.add(right_pane, weight=2)
        self._build_right_panel(right_pane)

        # Bottom: edu bar
        edu_bar = ttk.Frame(content_frame)
        edu_bar.pack(fill=tk.X, pady=(2, 2))
        self._worked_btn = ttk.Button(edu_bar, text="📊 Show All Calculations",
                                      command=self._show_worked_solution)
        self._worked_btn.pack(side=tk.LEFT)

        # Practice frame (below content, hidden initially)
        self._practice_frame = ttk.LabelFrame(
            self._inner_frame, text="🎓 Try It Yourself")
        self._build_practice_panel()

    # ── Left panel ───────────────────────────────────────────────

    def _build_left_panel(self, parent: ttk.Frame):
        # ── Investment & Rate ──
        params_lf = ttk.LabelFrame(parent, text="Project Parameters")
        params_lf.pack(fill=tk.X, padx=4, pady=(4, 2))

        _grid_lbl_entry(params_lf, "Initial Investment ($):", 0)
        self._inv_var = tk.StringVar(value="100000")
        ttk.Entry(params_lf, textvariable=self._inv_var, width=14).grid(
            row=0, column=1, sticky=tk.W, padx=4, pady=2)

        _grid_lbl_entry(params_lf, "Discount Rate (%):", 1)
        self._rate_var = tk.StringVar(value="10")
        ttk.Entry(params_lf, textvariable=self._rate_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=4, pady=2)

        # ── Cash Flows ──
        cf_lf = ttk.LabelFrame(parent, text="Annual Cash Flows (t=1, 2, …)")
        cf_lf.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        # Scrollable CF rows
        cf_canvas = tk.Canvas(cf_lf, highlightthickness=0)
        cf_vsb = ttk.Scrollbar(cf_lf, orient=tk.VERTICAL,
                               command=cf_canvas.yview)
        cf_canvas.configure(yscrollcommand=cf_vsb.set)
        cf_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        cf_canvas.pack(fill=tk.BOTH, expand=True)

        self._cf_inner = ttk.Frame(cf_canvas)
        self._cf_win = cf_canvas.create_window(
            (0, 0), window=self._cf_inner, anchor=tk.NW)
        self._cf_inner.bind(
            "<Configure>",
            lambda e: cf_canvas.configure(
                scrollregion=cf_canvas.bbox("all")))
        cf_canvas.bind(
            "<Configure>",
            lambda e: cf_canvas.itemconfig(self._cf_win, width=e.width))

        # Header
        hdr = ttk.Frame(self._cf_inner)
        hdr.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(hdr, text="Period", width=7, anchor=tk.CENTER,
                  relief="groove").pack(side=tk.LEFT, padx=1)
        ttk.Label(hdr, text="Cash Flow ($)", width=16, anchor=tk.CENTER,
                  relief="groove").pack(side=tk.LEFT, padx=1)

        self._cf_rows: List[Tuple[int, tk.StringVar]] = []

        # Seed 5 rows
        for _ in range(5):
            self._add_cf_row()

        cf_btn = ttk.Frame(cf_lf)
        cf_btn.pack(fill=tk.X, padx=4, pady=2)
        ttk.Button(cf_btn, text="+ Add Period",
                   command=self._add_cf_row).pack(side=tk.LEFT)
        ttk.Button(cf_btn, text="Clear",
                   command=self._clear_cf).pack(side=tk.LEFT, padx=4)

        # ── Metrics ──
        metrics_lf = ttk.LabelFrame(parent, text="Metrics to Calculate")
        metrics_lf.pack(fill=tk.X, padx=4, pady=2)

        metrics = [
            ("payback", "Payback Period"),
            ("disc_pb", "Discounted Payback"),
            ("roi", "ROI (%)"),
            ("npv", "NPV ($)"),
            ("irr", "IRR (%)"),
            ("pi", "Profitability Index"),
        ]
        self._metric_vars: dict = {}
        for col, (key, label) in enumerate(metrics):
            v = tk.BooleanVar(value=True)
            self._metric_vars[key] = v
            r, c = divmod(col, 3)
            ttk.Checkbutton(metrics_lf, text=label,
                            variable=v).grid(row=r, column=c, sticky=tk.W,
                                             padx=6, pady=2)

    def _add_cf_row(self, value=""):
        period = len(self._cf_rows) + 1
        row_frame = ttk.Frame(self._cf_inner)
        row_frame.pack(fill=tk.X, pady=1)
        ttk.Label(row_frame, text=str(period), width=7,
                  anchor=tk.CENTER).pack(side=tk.LEFT, padx=1)
        v = tk.StringVar(value=str(value))
        ttk.Entry(row_frame, textvariable=v, width=16).pack(
            side=tk.LEFT, padx=1)

        def _remove(rf=row_frame, tup=(period, v)):
            if tup in self._cf_rows:
                self._cf_rows.remove(tup)
            rf.destroy()
            self._renumber_cf()

        ttk.Button(row_frame, text="−", width=2,
                   command=_remove).pack(side=tk.LEFT, padx=1)
        self._cf_rows.append((period, v))

    def _renumber_cf(self):
        new_rows = []
        for i, (_, v) in enumerate(self._cf_rows):
            new_rows.append((i + 1, v))
        self._cf_rows = new_rows

    def _clear_cf(self):
        for w in self._cf_inner.winfo_children()[1:]:  # keep header
            w.destroy()
        self._cf_rows.clear()
        for _ in range(5):
            self._add_cf_row()

    def _get_inputs(self):
        """Parse UI into FinancialInputs; raises ValueError on bad input."""
        from pmhelper.core.financial_calcs import FinancialInputs
        inv = float(self._inv_var.get())
        rate = float(self._rate_var.get()) / 100.0
        cfs = []
        for _, v in self._cf_rows:
            raw = v.get().strip()
            if raw:
                cfs.append(float(raw))
        if not cfs:
            raise ValueError("No cash flows entered.")
        return FinancialInputs(
            initial_investment=inv,
            cash_flows=cfs,
            discount_rate=rate,
        )

    # ── Right panel ──────────────────────────────────────────────

    def _build_right_panel(self, pane: ttk.PanedWindow):
        # Results table
        results_lf = ttk.LabelFrame(pane, text="Results")
        pane.add(results_lf, weight=1)
        self._build_results_table(results_lf)

        # Chart
        chart_lf = ttk.LabelFrame(pane, text="Cumulative Cash-Flow Chart")
        pane.add(chart_lf, weight=2)
        self._build_chart(chart_lf)

    def _build_results_table(self, parent: ttk.Frame):
        cols = ("metric", "value", "interpretation")
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(parent, orient=tk.HORIZONTAL)
        self._results_tree = ttk.Treeview(
            parent, columns=cols, show="headings",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=8)
        vsb.config(command=self._results_tree.yview)
        hsb.config(command=self._results_tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._results_tree.pack(fill=tk.BOTH, expand=True)

        self._results_tree.heading("metric", text="Metric")
        self._results_tree.heading("value", text="Value")
        self._results_tree.heading("interpretation", text="Interpretation")
        self._results_tree.column("metric", width=180, minwidth=120)
        self._results_tree.column("value", width=120, minwidth=80,
                                  anchor=tk.E)
        self._results_tree.column("interpretation", width=300, minwidth=160)

        self._results_tree.tag_configure("positive", foreground="#15803d")
        self._results_tree.tag_configure("negative", foreground="#b91c1c")
        enhance_treeview(self._results_tree)

    def _build_chart(self, parent: ttk.Frame):
        if not HAS_MATPLOTLIB:
            ttk.Label(parent,
                      text="matplotlib not available",
                      foreground="grey").pack(expand=True)
            self._fig = None
            self._ax = None
            self._canvas = None
            return

        # Renderer toggle
        if _PLOTLY_EMBED:
            ctrl = ttk.Frame(parent)
            ctrl.pack(fill=tk.X, padx=5, pady=(2, 0))
            rf = ttk.LabelFrame(ctrl, text="Renderer", padding="3")
            rf.pack(side=tk.LEFT)
            ttk.Radiobutton(
                rf,
                text="Classic",
                value="matplotlib",
                variable=self._render_mode_var,
                command=self._switch_renderer).pack(
                side=tk.LEFT,
                padx=4)
            ttk.Radiobutton(
                rf,
                text="\U0001f4ca Plotly",
                value="plotly",
                variable=self._render_mode_var,
                command=self._switch_renderer).pack(
                side=tk.LEFT,
                padx=4)

        ttk.Button(
            parent,
            text="\U0001f50d Open Interactive",
            command=self._open_cf_interactive).pack(
            anchor=tk.W,
            padx=5,
            pady=(
                2,
                0))

        self._mpl_chart_frame = ttk.Frame(parent)
        self._mpl_chart_frame.pack(fill=tk.BOTH, expand=True)
        self._fig = Figure(figsize=(5, 3), dpi=90)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(
            self._fig, master=self._mpl_chart_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._ax.set_title("Cumulative Cash Flows", fontsize=10)
        self._fig.tight_layout()
        self._canvas.draw()

        # Plotly frame (hidden)
        self._plotly_frame = None
        if _PLOTLY_EMBED:
            self._plotly_frame = PlotlyChartFrame(parent)

    # ── Practice panel ────────────────────────────────────────────

    def _build_practice_panel(self):
        inner = ttk.Frame(self._practice_frame)
        inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        ttk.Label(
            inner,
            text=(
                "Calculate the Payback Period and NPV for this project.\n"
                "Enter your answers below and click 'Check'."
            ),
            foreground="navy", wraplength=700,
        ).pack(anchor=tk.W, pady=(0, 4))

        form = ttk.Frame(inner)
        form.pack(anchor=tk.W)
        ttk.Label(form, text="Your Payback Period (periods):").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 6), pady=2)
        self._prac_pb_var = tk.StringVar()
        ttk.Entry(form, textvariable=self._prac_pb_var, width=12).grid(
            row=0, column=1, sticky=tk.W)
        self._prac_pb_status = tk.StringVar()
        ttk.Label(form, textvariable=self._prac_pb_status,
                  width=20).grid(row=0, column=2, sticky=tk.W, padx=4)

        ttk.Label(form, text="Your NPV ($):").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 6), pady=2)
        self._prac_npv_var = tk.StringVar()
        ttk.Entry(form, textvariable=self._prac_npv_var, width=12).grid(
            row=1, column=1, sticky=tk.W)
        self._prac_npv_status = tk.StringVar()
        ttk.Label(form, textvariable=self._prac_npv_status,
                  width=20).grid(row=1, column=2, sticky=tk.W, padx=4)

        self._prac_feedback = tk.StringVar()
        ttk.Label(inner, textvariable=self._prac_feedback,
                  foreground="teal").pack(anchor=tk.W, pady=(6, 0))

        btn_row = ttk.Frame(inner)
        btn_row.pack(anchor=tk.W, pady=(4, 0))
        ttk.Button(btn_row, text="✓ Check",
                   command=self._check_answers).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Show Answers",
                   command=self._reveal_answers).pack(side=tk.LEFT)

    # ── Actions ──────────────────────────────────────────────────

    def _load_demo(self):
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "data",
            "demos",
            "v2",
            "financial_demo.json")
        demo_path = os.path.normpath(demo_path)

        if not os.path.exists(demo_path):
            # Fallback: walk up from __file__ looking for data/demos/v2/
            here = os.path.dirname(os.path.abspath(__file__))
            for _ in range(6):
                candidate = os.path.join(
                    here, "data", "demos", "v2", "financial_demo.json")
                if os.path.exists(candidate):
                    demo_path = candidate
                    break
                here = os.path.dirname(here)

        if not os.path.exists(demo_path):
            messagebox.showerror(
                "Load Demo",
                f"Demo file not found:\n{demo_path}")
            return

        with open(demo_path, encoding="utf-8") as fh:
            demo = json.load(fh)

        scenarios = demo.get("data", {}).get("scenarios", [])
        if not scenarios:
            messagebox.showinfo("Load Demo", "No scenarios in demo file.")
            return

        # If multiple scenarios, pick the first one
        sc = scenarios[0]
        self._inv_var.set(str(sc.get("initial_investment", 100000)))
        self._rate_var.set(str(sc.get("discount_rate_pct", 10)))

        cfs = sc.get("cash_flows", [])
        for w in list(self._cf_inner.winfo_children())[1:]:
            w.destroy()
        self._cf_rows.clear()
        for cf in cfs:
            self._add_cf_row(value=cf)

        messagebox.showinfo(
            "Load Demo",
            f"Loaded scenario: {sc.get('name', 'Demo')}\n\n"
            f"{sc.get('description', '')}")

    def _calculate(self):
        from pmhelper.core.financial_calcs import FinancialCalcs
        try:
            inputs = self._get_inputs()
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            return

        result = FinancialCalcs.calculate(inputs)
        self._result = result
        self._inputs = inputs
        self._update_results(inputs, result)
        if HAS_MATPLOTLIB and self._canvas is not None:
            self._update_chart(inputs, result)
        if self._try_var.get():
            self._prac_pb_var.set("")
            self._prac_npv_var.set("")
            self._prac_pb_status.set("")
            self._prac_npv_status.set("")
            self._prac_feedback.set("")

    def _update_results(self, inputs, result):
        self._results_tree.delete(*self._results_tree.get_children())

        rate_pct = inputs.discount_rate * 100
        interps = result.interpretation

        rows = [
            (
                "Payback Period",
                f"{result.payback_period:.2f} periods"
                if result.payback_period is not None else "Not recovered",
                interps.get("payback", ""),
                result.payback_period is not None,
            ),
            (
                f"Discounted Payback ({rate_pct:.1f}%)",
                f"{result.discounted_payback:.2f} periods"
                if result.discounted_payback is not None else "Not recovered",
                interps.get("discounted_payback", ""),
                result.discounted_payback is not None,
            ),
            (
                "ROI",
                f"{result.roi:.2f}%",
                interps.get("roi", ""),
                result.roi >= 0,
            ),
            (
                "NPV",
                f"${result.npv:,.2f}",
                interps.get("npv", ""),
                result.npv >= 0,
            ),
            (
                "IRR",
                f"{result.irr:.2f}%"
                if result.irr is not None else "N/A",
                interps.get("irr", ""),
                result.irr is not None and result.irr >= inputs.discount_rate * 100,
            ),
            (
                "Profitability Index",
                f"{result.profitability_index:.4f}",
                interps.get("pi", ""),
                result.profitability_index >= 1.0,
            ),
        ]

        metric_map = {
            "Payback Period": "payback",
            "ROI": "roi",
            "NPV": "npv",
            "IRR": "irr",
            "Profitability Index": "pi",
        }

        for metric, value, interp, is_pos in rows:
            key = next(
                (k for k in self._metric_vars if metric.lower().startswith(
                    k.replace(
                        "_pb",
                        "").replace(
                        "disc_",
                        "disc"))),
                None)
            # Always show all calculated rows for now (checkboxes filter later)
            tag = "positive" if is_pos else "negative"
            self._results_tree.insert("", tk.END, tags=(tag,),
                                      values=(metric, value, interp))

    def _update_chart(self, inputs, result):
        if self._render_mode_var.get() == "plotly" and getattr(self, '_plotly_frame', None):
            self._update_plotly_cf(inputs, result)
            return
        self._ax.clear()
        dets = result.payback_details
        if not dets:
            self._canvas.draw()
            return

        periods = [d.period for d in dets]
        cum = [d.cumulative for d in dets]
        dcum = [d.discounted_cumulative for d in dets]
        inv = inputs.initial_investment

        width = 0.35
        x = list(range(len(periods)))

        self._ax.bar([p - width / 2 for p in x], cum, width,
                     label="Cumulative CF", color="#3b82f6", alpha=0.8)
        self._ax.bar([p + width / 2 for p in x], dcum, width,
                     label="Discounted Cumul. CF", color="#8b5cf6", alpha=0.8)
        self._ax.axhline(inv, color="red", linewidth=1.5,
                         linestyle="--", label=f"Investment = {inv:,.0f}")
        self._ax.axhline(0, color="black", linewidth=0.8, alpha=0.4)

        self._ax.set_xticks(x)
        self._ax.set_xticklabels([f"t={p}" for p in periods],
                                 fontsize=7, rotation=45, ha="right")
        self._ax.set_title("Cumulative Cash Flows vs. Initial Investment",
                           fontsize=10)
        self._ax.set_xlabel("Period", fontsize=8)
        self._ax.set_ylabel("Amount ($)", fontsize=8)
        self._ax.legend(fontsize=7)
        self._ax.grid(True, alpha=0.3, linestyle="--")
        self._fig.tight_layout()
        self._canvas.draw()

    def _show_worked_solution(self):
        if self._result is None:
            messagebox.showinfo("Worked Solution",
                                "Click ▶ Calculate first.")
            return
        from pmhelper.core.financial_step_generator import financial_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        steps = financial_steps(self._inputs, self._result)
        WorkedSolutionWindow(
            self.frame,
            "Financial Analysis — Worked Solution",
            steps,
        )

    # ── Practice ─────────────────────────────────────────────────

    def _toggle_practice(self):
        if self._try_var.get():
            self._practice_frame.pack(fill=tk.X, padx=4, pady=4)
            self._inner_frame.update_idletasks()
            self._tiy_canvas.yview_moveto(1.0)
        else:
            self._practice_frame.pack_forget()

    def _check_answers(self):
        if self._result is None:
            messagebox.showinfo("Check", "Run Calculate first.")
            return
        n_ok = 0
        n_total = 0

        pb_str = self._prac_pb_var.get().strip()
        npv_str = self._prac_npv_var.get().strip()

        if self._result.payback_period is not None:
            n_total += 1
            try:
                pb_student = float(pb_str)
                if abs(pb_student - self._result.payback_period) <= 0.01:
                    self._prac_pb_status.set("✓ Correct")
                    n_ok += 1
                else:
                    self._prac_pb_status.set(
                        f"✗ {self._result.payback_period:.4f}")
            except ValueError:
                self._prac_pb_status.set("⚠ Not a number")

        n_total += 1
        try:
            npv_student = float(npv_str)
            if abs(npv_student - self._result.npv) <= 0.1:
                self._prac_npv_status.set("✓ Correct")
                n_ok += 1
            else:
                self._prac_npv_status.set(f"✗ {self._result.npv:,.2f}")
        except ValueError:
            self._prac_npv_status.set("⚠ Not a number")

        self._prac_feedback.set(
            f"{n_ok}/{n_total} correct — well done! 🎉"
            if n_ok == n_total else f"{n_ok}/{n_total} correct — keep trying!")

    def _reveal_answers(self):
        if self._result is None:
            return
        pb = self._result.payback_period
        self._prac_pb_var.set(f"{pb:.4f}" if pb is not None else "N/A")
        self._prac_npv_var.set(f"{self._result.npv:.4f}")
        self._prac_pb_status.set("✓ Revealed")
        self._prac_npv_status.set("✓ Revealed")
        self._prac_feedback.set("Answers revealed.")

    def set_mode(self, mode: str):
        """Show the all-calculations button only in UG mode."""
        if self._worked_btn is None:
            return
        if mode.upper() == "UG":
            self._worked_btn.pack(side=tk.LEFT)
        else:
            self._worked_btn.pack_forget()

    def get_figures(self) -> list:
        if HAS_MATPLOTLIB and self._fig is not None:
            return [self._fig]
        return []

    def _open_cf_interactive(self):
        if self._result is None or self._inputs is None:
            messagebox.showinfo("Interactive", "Run calculation first.")
            return
        from pmhelper.utils.interactive_charts import open_chart_in_browser
        fig = plotly_financial_cf(
            self._result.payback_details,
            self._inputs.initial_investment)
        open_chart_in_browser(fig, "Cash Flow Chart")

    def _switch_renderer(self):
        mode = self._render_mode_var.get()
        if mode == "plotly" and getattr(self, '_plotly_frame', None):
            self._mpl_chart_frame.pack_forget()
            self._plotly_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            if getattr(self, '_plotly_frame', None):
                self._plotly_frame.pack_forget()
            self._mpl_chart_frame.pack(fill=tk.BOTH, expand=True)
        if self._result and self._inputs:
            self._update_chart(self._inputs, self._result)

    def _update_plotly_cf(self, inputs, result):
        if not self._plotly_frame:
            return
        try:
            fig = plotly_financial_cf(
                result.payback_details,
                inputs.initial_investment)
            if fig:
                self._plotly_frame.update_chart(fig)
        except Exception as e:
            self._plotly_frame.load_html(
                f"<html><body style='font-family:sans-serif;padding:40px'>"
                f"<h3>Error</h3><pre>{e}</pre></body></html>")


# ════════════════════════════════════════════════════════════════════
#  Sub-tab 2 — Factor Scoring
# ════════════════════════════════════════════════════════════════════

class _FactorScoringSubTab:
    """Factor Scoring inner sub-tab."""

    _DEFAULT_CRITERIA = [
        "Strategic fit",
        "Risk",
        "Cost",
        "Schedule",
        "Quality"]
    _DEFAULT_PROJECTS = ["Project A", "Project B", "Project C"]
    _MODELS = ["0-1", "Factor", "Weighted"]

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self._result = None
        self._worked_btn = None
        self._render_mode_var = tk.StringVar(value="matplotlib")

        self.frame = ttk.Frame(parent)
        self._build_ui()

    # ── Construction ─────────────────────────────────────────────

    def _build_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=6, pady=(5, 2))

        ttk.Button(toolbar, text="📂 Load Demo",
                   command=self._load_demo).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="▶ Calculate",
                   command=self._calculate).pack(side=tk.LEFT, padx=(0, 8))

        self._try_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            toolbar, text="🎓 Try It Yourself",
            variable=self._try_var, command=self._toggle_practice,
        ).pack(side=tk.RIGHT)

        # Model selector
        model_lf = ttk.LabelFrame(self.frame, text="Scoring Model")
        model_lf.pack(fill=tk.X, padx=6, pady=(0, 2))
        self._model_var = tk.StringVar(value="Weighted")
        for m in self._MODELS:
            ttk.Radiobutton(
                model_lf, text=m, value=m,
                variable=self._model_var,
                command=self._on_model_change,
            ).pack(side=tk.LEFT, padx=8, pady=4)

        # Scrollable container
        _scroll_outer = ttk.Frame(self.frame)
        _scroll_outer.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)
        _vsb2 = ttk.Scrollbar(_scroll_outer, orient=tk.VERTICAL)
        _vsb2.pack(side=tk.RIGHT, fill=tk.Y)
        self._tiy_canvas = tk.Canvas(_scroll_outer, yscrollcommand=_vsb2.set,
                                     highlightthickness=0)
        self._tiy_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        _vsb2.config(command=self._tiy_canvas.yview)
        self._inner_frame = ttk.Frame(self._tiy_canvas)
        self._tiy_win = self._tiy_canvas.create_window(
            (0, 0), window=self._inner_frame, anchor='nw')
        self._inner_frame.bind('<Configure>',
                               lambda e: self._tiy_canvas.configure(
                                   scrollregion=self._tiy_canvas.bbox('all')))
        self._tiy_canvas.bind(
            '<Configure>',
            lambda e: self._tiy_canvas.itemconfig(
                self._tiy_win,
                width=e.width))
        self._tiy_canvas.bind_all('<MouseWheel>', lambda e: self._tiy_canvas.yview_scroll(
            int(-1 * (e.delta / 120)), 'units'))

        content_frame = ttk.Frame(self._inner_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Main horizontal pane
        pane = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        # Left: criterion + project editors
        left = ttk.Frame(pane)
        pane.add(left, weight=1)
        self._build_left(left)

        # Middle: score matrix
        matrix_lf = ttk.LabelFrame(pane, text="Score Matrix")
        pane.add(matrix_lf, weight=2)
        self._build_matrix(matrix_lf)

        # Right: results
        right = ttk.Frame(pane)
        pane.add(right, weight=2)
        self._build_right(right)

        # Edu bar
        edu_bar = ttk.Frame(content_frame)
        edu_bar.pack(fill=tk.X, pady=(2, 2))
        self._worked_btn = ttk.Button(edu_bar, text="📊 Show All Calculations",
                                      command=self._show_worked_solution)
        self._worked_btn.pack(side=tk.LEFT)

        # Practice frame
        self._practice_frame = ttk.LabelFrame(
            self._inner_frame, text="🎓 Try It Yourself")
        self._build_practice_panel()

        # Seed defaults
        self._seed_defaults()

    # ── Criteria editor ──────────────────────────────────────────

    def _build_left(self, parent: ttk.Frame):
        # Criteria
        crit_lf = ttk.LabelFrame(parent, text="Criteria")
        crit_lf.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 2))

        # Header
        hdr = ttk.Frame(crit_lf)
        hdr.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(hdr, text="Name", width=16, anchor=tk.CENTER,
                  relief="groove").pack(side=tk.LEFT, padx=1)
        self._weight_hdr = ttk.Label(
            hdr, text="Weight", width=7, anchor=tk.CENTER, relief="groove")
        self._weight_hdr.pack(side=tk.LEFT, padx=1)

        # Scrollable criteria rows
        crit_canvas = tk.Canvas(crit_lf, highlightthickness=0, height=160)
        crit_vsb = ttk.Scrollbar(crit_lf, orient=tk.VERTICAL,
                                 command=crit_canvas.yview)
        crit_canvas.configure(yscrollcommand=crit_vsb.set)
        crit_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        crit_canvas.pack(fill=tk.BOTH, expand=True)

        self._crit_inner = ttk.Frame(crit_canvas)
        crit_win = crit_canvas.create_window(
            (0, 0), window=self._crit_inner, anchor=tk.NW)
        self._crit_inner.bind(
            "<Configure>",
            lambda e: crit_canvas.configure(
                scrollregion=crit_canvas.bbox("all")))
        crit_canvas.bind(
            "<Configure>",
            lambda e: crit_canvas.itemconfig(crit_win, width=e.width))

        # (name_var, weight_var, row_frame)
        self._crit_rows: List[Tuple] = []

        crit_btn = ttk.Frame(crit_lf)
        crit_btn.pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(crit_btn, text="+ Criterion",
                   command=lambda: self._add_criterion()).pack(side=tk.LEFT)
        ttk.Button(crit_btn, text="Rebuild Grid",
                   command=self._rebuild_matrix).pack(side=tk.LEFT, padx=4)

        # Projects
        proj_lf = ttk.LabelFrame(parent, text="Projects")
        proj_lf.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 2))

        # Header
        phdr = ttk.Frame(proj_lf)
        phdr.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(phdr, text="Project Name", width=20, anchor=tk.CENTER,
                  relief="groove").pack(side=tk.LEFT, padx=1)

        proj_canvas = tk.Canvas(proj_lf, highlightthickness=0, height=120)
        proj_vsb = ttk.Scrollbar(proj_lf, orient=tk.VERTICAL,
                                 command=proj_canvas.yview)
        proj_canvas.configure(yscrollcommand=proj_vsb.set)
        proj_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        proj_canvas.pack(fill=tk.BOTH, expand=True)

        self._proj_inner = ttk.Frame(proj_canvas)
        proj_win = proj_canvas.create_window(
            (0, 0), window=self._proj_inner, anchor=tk.NW)
        self._proj_inner.bind(
            "<Configure>",
            lambda e: proj_canvas.configure(
                scrollregion=proj_canvas.bbox("all")))
        proj_canvas.bind(
            "<Configure>",
            lambda e: proj_canvas.itemconfig(proj_win, width=e.width))

        self._proj_rows: List[tk.StringVar] = []

        proj_btn = ttk.Frame(proj_lf)
        proj_btn.pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(proj_btn, text="+ Project",
                   command=lambda: self._add_project()).pack(side=tk.LEFT)

    def _add_criterion(self, name="", weight="1.0"):
        row = ttk.Frame(self._crit_inner)
        row.pack(fill=tk.X, pady=1)

        nv = tk.StringVar(value=name)
        ttk.Entry(row, textvariable=nv, width=16).pack(side=tk.LEFT, padx=1)
        wv = tk.StringVar(value=str(weight))
        w_entry = ttk.Entry(row, textvariable=wv, width=7)
        w_entry.pack(side=tk.LEFT, padx=1)

        tup = (nv, wv, row, w_entry)
        self._crit_rows.append(tup)

        def _remove(rf=row, t=tup):
            if t in self._crit_rows:
                self._crit_rows.remove(t)
            rf.destroy()

        ttk.Button(row, text="−", width=2,
                   command=_remove).pack(side=tk.LEFT, padx=1)

        self._refresh_weight_visibility()

    def _add_project(self, name=""):
        row = ttk.Frame(self._proj_inner)
        row.pack(fill=tk.X, pady=1)
        v = tk.StringVar(value=name)
        ttk.Entry(row, textvariable=v, width=20).pack(side=tk.LEFT, padx=1)
        self._proj_rows.append(v)

        def _remove(rf=row, sv=v):
            if sv in self._proj_rows:
                self._proj_rows.remove(sv)
            rf.destroy()

        ttk.Button(row, text="−", width=2,
                   command=_remove).pack(side=tk.LEFT, padx=1)

    def _refresh_weight_visibility(self):
        weighted = self._model_var.get() == "Weighted"
        for _, _, _, w_entry in self._crit_rows:
            if weighted:
                w_entry.pack(side=tk.LEFT, padx=1)
            else:
                pass  # entries always present; header visibility controls appearance
        # Toggle weight column header
        if weighted:
            self._weight_hdr.config(foreground="black")
        else:
            self._weight_hdr.config(foreground="grey")

    def _on_model_change(self):
        self._refresh_weight_visibility()

    # ── Score matrix ──────────────────────────────────────────────

    def _build_matrix(self, parent: ttk.Frame):
        self._matrix_parent = parent
        self._matrix_canvas = tk.Canvas(parent, highlightthickness=0)
        mvsb = ttk.Scrollbar(parent, orient=tk.VERTICAL,
                             command=self._matrix_canvas.yview)
        mhsb = ttk.Scrollbar(parent, orient=tk.HORIZONTAL,
                             command=self._matrix_canvas.xview)
        self._matrix_canvas.configure(yscrollcommand=mvsb.set,
                                      xscrollcommand=mhsb.set)
        mvsb.pack(side=tk.RIGHT, fill=tk.Y)
        mhsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._matrix_canvas.pack(fill=tk.BOTH, expand=True)

        self._matrix_inner = ttk.Frame(self._matrix_canvas)
        self._matrix_win = self._matrix_canvas.create_window(
            (0, 0), window=self._matrix_inner, anchor=tk.NW)
        self._matrix_inner.bind(
            "<Configure>",
            lambda e: self._matrix_canvas.configure(
                scrollregion=self._matrix_canvas.bbox("all")))

        # (row, col) → StringVar
        self._score_vars: dict = {}

    def _rebuild_matrix(self):
        """Destroy and recreate the score matrix from current criteria + projects."""
        for w in self._matrix_inner.winfo_children():
            w.destroy()
        self._score_vars.clear()

        crits = [nv.get().strip()
                 for nv, *_ in self._crit_rows if nv.get().strip()]
        projs = [v.get().strip() for v in self._proj_rows if v.get().strip()]

        if not crits or not projs:
            ttk.Label(self._matrix_inner,
                      text="Add criteria and projects first.",
                      foreground="grey").grid(row=0, column=0, padx=6, pady=6)
            return

        # Header row (criteria names)
        ttk.Label(self._matrix_inner, text="", width=14,
                  relief="groove").grid(row=0, column=0, padx=1, pady=1)
        for c_idx, cname in enumerate(crits):
            ttk.Label(self._matrix_inner, text=cname, width=12,
                      anchor=tk.CENTER, relief="groove").grid(
                          row=0, column=c_idx + 1, padx=1, pady=1)

        model = self._model_var.get()
        hint = " (0 or 1)" if model == "0-1" else " (1–5)" if model == "Factor" else ""

        # Data rows (projects)
        for r_idx, pname in enumerate(projs):
            ttk.Label(self._matrix_inner, text=pname + hint, width=14,
                      anchor=tk.W, relief="groove").grid(
                          row=r_idx + 1, column=0, padx=1, pady=1)
            for c_idx in range(len(crits)):
                v = tk.StringVar(value="1" if model == "0-1" else "3")
                self._score_vars[(r_idx, c_idx)] = v
                ttk.Entry(self._matrix_inner, textvariable=v, width=6).grid(
                    row=r_idx + 1, column=c_idx + 1, padx=1, pady=1)

    # ── Right panel ──────────────────────────────────────────────

    def _build_right(self, parent: ttk.Frame):
        results_lf = ttk.LabelFrame(parent, text="Ranking Results")
        results_lf.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 2))

        cols = ("rank", "project", "total")
        vsb = ttk.Scrollbar(results_lf, orient=tk.VERTICAL)
        self._results_tree = ttk.Treeview(
            results_lf, columns=cols, show="headings",
            yscrollcommand=vsb.set, height=8)
        vsb.config(command=self._results_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._results_tree.pack(fill=tk.BOTH, expand=True)

        self._results_tree.heading("rank", text="#")
        self._results_tree.heading("project", text="Project")
        self._results_tree.heading("total", text="Total Score")
        self._results_tree.column("rank", width=40, anchor=tk.CENTER)
        self._results_tree.column("project", width=140)
        self._results_tree.column("total", width=90, anchor=tk.E)

        self._results_tree.tag_configure("winner", background="#dcfce7",
                                         foreground="#15803d")
        enhance_treeview(self._results_tree)

        # Chart
        chart_lf = ttk.LabelFrame(parent, text="Score Comparison")
        chart_lf.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 2))
        self._build_fs_chart(chart_lf)

    def _build_fs_chart(self, parent: ttk.Frame):
        if not HAS_MATPLOTLIB:
            ttk.Label(parent, text="matplotlib not available",
                      foreground="grey").pack(expand=True)
            self._fig = None
            self._ax = None
            self._canvas = None
            return

        # Renderer toggle
        if _PLOTLY_EMBED:
            ctrl = ttk.Frame(parent)
            ctrl.pack(fill=tk.X, padx=5, pady=(2, 0))
            rf = ttk.LabelFrame(ctrl, text="Renderer", padding="3")
            rf.pack(side=tk.LEFT)
            ttk.Radiobutton(
                rf,
                text="Classic",
                value="matplotlib",
                variable=self._render_mode_var,
                command=self._switch_renderer).pack(
                side=tk.LEFT,
                padx=4)
            ttk.Radiobutton(
                rf,
                text="\U0001f4ca Plotly",
                value="plotly",
                variable=self._render_mode_var,
                command=self._switch_renderer).pack(
                side=tk.LEFT,
                padx=4)

        ttk.Button(
            parent,
            text="\U0001f50d Open Interactive",
            command=self._open_scoring_interactive).pack(
            anchor=tk.W,
            padx=5,
            pady=(
                2,
                0))

        self._mpl_chart_frame = ttk.Frame(parent)
        self._mpl_chart_frame.pack(fill=tk.BOTH, expand=True)
        self._fig = Figure(figsize=(4, 3), dpi=90)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(
            self._fig, master=self._mpl_chart_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._ax.set_title("Project Scores", fontsize=10)
        self._fig.tight_layout()
        self._canvas.draw()

        # Plotly frame (hidden)
        self._plotly_frame = None
        if _PLOTLY_EMBED:
            self._plotly_frame = PlotlyChartFrame(parent)

    # ── Practice panel ────────────────────────────────────────────

    def _build_practice_panel(self):
        inner = ttk.Frame(self._practice_frame)
        inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        ttk.Label(
            inner,
            text="Calculate each project's total score using the selected model. "
            "Enter your answers, then click 'Check'.",
            foreground="navy",
            wraplength=700,
        ).pack(
            anchor=tk.W,
            pady=(
                0,
                4))

        self._prac_form = ttk.Frame(inner)
        self._prac_form.pack(anchor=tk.W)
        self._prac_answer_vars: dict = {}   # project_name → StringVar
        self._prac_status_vars: dict = {}
        self._prac_correct: dict = {}

        self._prac_feedback = tk.StringVar()
        ttk.Label(inner, textvariable=self._prac_feedback,
                  foreground="teal").pack(anchor=tk.W, pady=(6, 0))

        btn_row = ttk.Frame(inner)
        btn_row.pack(anchor=tk.W, pady=(4, 0))
        ttk.Button(btn_row, text="✓ Check",
                   command=self._check_answers).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Show Answers",
                   command=self._reveal_answers).pack(side=tk.LEFT)

    def _populate_practice(self):
        for w in self._prac_form.winfo_children():
            w.destroy()
        self._prac_answer_vars.clear()
        self._prac_status_vars.clear()
        self._prac_correct.clear()

        if self._result is None:
            return

        for ps in sorted(self._result.projects, key=lambda p: p.rank):
            row = ttk.Frame(self._prac_form)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=ps.project_name, width=20).pack(
                side=tk.LEFT, padx=(0, 4))
            av = tk.StringVar()
            ttk.Entry(row, textvariable=av, width=10).pack(side=tk.LEFT)
            sv = tk.StringVar()
            ttk.Label(row, textvariable=sv, width=20).pack(
                side=tk.LEFT, padx=4)
            self._prac_answer_vars[ps.project_name] = av
            self._prac_status_vars[ps.project_name] = sv
            self._prac_correct[ps.project_name] = ps.total

        self._prac_feedback.set("")

    # ── Actions ──────────────────────────────────────────────────

    def _seed_defaults(self):
        for c in self._DEFAULT_CRITERIA:
            self._add_criterion(name=c)
        for p in self._DEFAULT_PROJECTS:
            self._add_project(name=p)

    def _load_demo(self):
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..", "data", "demos", "v2",
            "factor_scoring_demo.json")
        demo_path = os.path.normpath(demo_path)

        if not os.path.exists(demo_path):
            # Fallback: walk up from __file__ looking for data/demos/v2/
            here = os.path.dirname(os.path.abspath(__file__))
            for _ in range(6):
                candidate = os.path.join(
                    here, "data", "demos", "v2", "factor_scoring_demo.json")
                if os.path.exists(candidate):
                    demo_path = candidate
                    break
                here = os.path.dirname(here)

        if not os.path.exists(demo_path):
            messagebox.showerror("Load Demo",
                                 f"Demo file not found:\n{demo_path}")
            return

        with open(demo_path, encoding="utf-8") as fh:
            demo = json.load(fh)

        # Try model-specific demo from demos array first
        current_model = self._model_var.get()
        data = None
        for entry in demo.get("demos", []):
            if entry.get("model") == current_model:
                data = entry.get("data", {})
                break
        if data is None:
            data = demo.get("data", {})
        crits = data.get("criteria", [])
        projs = data.get("projects", [])

        # Rebuild criteria
        for w in self._crit_inner.winfo_children():
            w.destroy()
        self._crit_rows.clear()
        for c in crits:
            self._add_criterion(
                name=c.get("name", ""),
                weight=str(c.get("weight", 1.0)))

        # Rebuild projects
        for w in self._proj_inner.winfo_children():
            w.destroy()
        self._proj_rows.clear()
        for p in projs:
            self._add_project(name=p.get("name", ""))

        # Set model
        model = data.get("model", "Weighted")
        if model in self._MODELS:
            self._model_var.set(model)

        # Rebuild + fill matrix
        self._rebuild_matrix()
        score_matrix = data.get("score_matrix", [])
        for r_idx, row_scores in enumerate(score_matrix):
            for c_idx, score in enumerate(row_scores):
                if (r_idx, c_idx) in self._score_vars:
                    self._score_vars[(r_idx, c_idx)].set(str(score))

        messagebox.showinfo(
            "Load Demo",
            f"Loaded: {demo.get('name', 'Demo')}\n\n"
            f"{demo.get('description', '')}")

    def _collect_inputs(self):
        """Parse editors into lists for the engine. Raises ValueError."""
        from pmhelper.core.factor_scoring import ScoringCriterion

        crit_data = [
            (nv.get().strip(), wv.get().strip())
            for nv, wv, *_ in self._crit_rows
            if nv.get().strip()
        ]
        if not crit_data:
            raise ValueError("No criteria defined.")

        proj_names = [v.get().strip()
                      for v in self._proj_rows if v.get().strip()]
        if not proj_names:
            raise ValueError("No projects defined.")

        n_c = len(crit_data)
        n_p = len(proj_names)
        if len(self._score_vars) < n_p * n_c:
            raise ValueError(
                "Score matrix not built. Click 'Rebuild Grid' first.")

        criteria = []
        for cname, wstr in crit_data:
            try:
                w = float(wstr) if wstr else 1.0
            except ValueError:
                w = 1.0
            criteria.append(ScoringCriterion(name=cname, weight=w))

        score_matrix = []
        for r in range(n_p):
            row = []
            for c in range(n_c):
                try:
                    row.append(
                        float(
                            self._score_vars.get(
                                (r, c), tk.StringVar(
                                    value="0")).get()))
                except ValueError:
                    row.append(0.0)
            score_matrix.append(row)

        model = self._model_var.get()
        return criteria, proj_names, score_matrix, model

    def _calculate(self):
        from pmhelper.core.factor_scoring import FactorScoringEngine
        try:
            criteria, proj_names, score_matrix, model = self._collect_inputs()
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            return

        result = FactorScoringEngine.calculate(
            criteria, proj_names, score_matrix, model)
        self._result = result
        self._update_results(result)
        if HAS_MATPLOTLIB and self._canvas is not None:
            self._update_chart(result)
        if self._try_var.get():
            self._populate_practice()

    def _update_results(self, result):
        self._results_tree.delete(*self._results_tree.get_children())
        for ps in sorted(result.projects, key=lambda p: p.rank):
            tag = ("winner",) if ps.rank == 1 else ()
            self._results_tree.insert("", tk.END, tags=tag, values=(
                ps.rank, ps.project_name, f"{ps.total:.4f}"))

    def _update_chart(self, result):
        if self._render_mode_var.get() == "plotly" and getattr(self, '_plotly_frame', None):
            self._update_plotly_fs(result)
            return
        self._ax.clear()
        projs = sorted(result.projects, key=lambda p: p.rank)
        names = [ps.project_name for ps in projs]
        totals = [ps.total for ps in projs]
        colors = ["#16a34a" if ps.rank == 1 else "#6b7280" for ps in projs]

        x = list(range(len(names)))
        self._ax.bar(x, totals, color=colors, alpha=0.85)
        self._ax.set_xticks(x)
        self._ax.set_xticklabels(names, rotation=30, ha="right", fontsize=7)
        self._ax.set_title(
            f"Project Scores — {
                result.model} Model",
            fontsize=10)
        self._ax.set_ylabel("Total Score", fontsize=8)
        self._ax.grid(True, axis="y", alpha=0.3, linestyle="--")
        self._fig.tight_layout()
        self._canvas.draw()

    def _show_worked_solution(self):
        if self._result is None:
            messagebox.showinfo("Worked Solution",
                                "Click ▶ Calculate first.")
            return
        from pmhelper.core.factor_scoring_step_generator import factor_scoring_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        steps = factor_scoring_steps(self._result)
        WorkedSolutionWindow(
            self.frame,
            f"Factor Scoring ({self._result.model}) — Worked Solution",
            steps,
        )

    def _toggle_practice(self):
        if self._try_var.get():
            self._practice_frame.pack(fill=tk.X, padx=4, pady=4)
            if self._result is not None:
                self._populate_practice()
            self._inner_frame.update_idletasks()
            self._tiy_canvas.yview_moveto(1.0)
        else:
            self._practice_frame.pack_forget()

    def _check_answers(self):
        if not self._prac_correct:
            messagebox.showinfo("Check", "Run Calculate first.")
            return
        n_ok = 0
        n_total = len(self._prac_correct)
        for pname, correct in self._prac_correct.items():
            sv = self._prac_status_vars[pname]
            try:
                student = float(self._prac_answer_vars[pname].get())
                if abs(student - correct) <= 0.01:
                    sv.set("✓ Correct")
                    n_ok += 1
                else:
                    sv.set(f"✗ {correct:.4f}")
            except ValueError:
                sv.set("⚠ Not a number")
        self._prac_feedback.set(
            f"{n_ok}/{n_total} correct — well done! 🎉"
            if n_ok == n_total
            else f"{n_ok}/{n_total} correct — keep trying!")

    def _reveal_answers(self):
        for pname, correct in self._prac_correct.items():
            self._prac_answer_vars[pname].set(f"{correct:.4f}")
            self._prac_status_vars[pname].set("✓ Revealed")
        self._prac_feedback.set("Answers revealed.")

    def set_mode(self, mode: str):
        """Show the all-calculations button only in UG mode."""
        if self._worked_btn is None:
            return
        if mode.upper() == "UG":
            self._worked_btn.pack(side=tk.LEFT)
        else:
            self._worked_btn.pack_forget()

    def get_figures(self) -> list:
        if HAS_MATPLOTLIB and self._fig is not None:
            return [self._fig]
        return []

    def _open_scoring_interactive(self):
        if self._result is None:
            messagebox.showinfo("Interactive", "Run scoring first.")
            return
        from pmhelper.utils.interactive_charts import open_chart_in_browser
        fig = plotly_factor_scoring(self._result)
        open_chart_in_browser(fig, "Factor Scoring")

    def _switch_renderer(self):
        mode = self._render_mode_var.get()
        if mode == "plotly" and getattr(self, '_plotly_frame', None):
            self._mpl_chart_frame.pack_forget()
            self._plotly_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            if getattr(self, '_plotly_frame', None):
                self._plotly_frame.pack_forget()
            self._mpl_chart_frame.pack(fill=tk.BOTH, expand=True)
        if self._result:
            self._update_chart(self._result)

    def _update_plotly_fs(self, result):
        if not self._plotly_frame:
            return
        try:
            fig = plotly_factor_scoring(result)
            if fig:
                self._plotly_frame.update_chart(fig)
        except Exception as e:
            self._plotly_frame.load_html(
                f"<html><body style='font-family:sans-serif;padding:40px'>"
                f"<h3>Error</h3><pre>{e}</pre></body></html>")


# ── Tiny helper ───────────────────────────────────────────────────────

def _grid_lbl_entry(parent, text: str, row: int):
    ttk.Label(parent, text=text).grid(
        row=row, column=0, sticky=tk.W, padx=(6, 2), pady=2)
