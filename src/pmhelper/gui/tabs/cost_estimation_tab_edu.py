"""
PMhelper Edu — Cost Estimation Tab (V2 Phase 5).

A method-selector tab in the Cost group containing 7 cost estimation
techniques.  Selecting a method from the left panel shows the
corresponding input form on the right.

Methods
-------
1. Top-Down (Analogous)
2. Bottom-Up
3. Work Element
4. Power Sizing / Cost-Capacity Index
5. Unit / Factor
6. Cost-Capacity Index (alias for Power Sizing — same panel)
7. Learning Curves

Each method panel provides:
* Standalone input fields / tables
* "Calculate" button
* "Load from Project" (where applicable)
* "Load Demo" button
* Results display (treeview + formula)
* "📖 Worked Solution" → WorkedSolutionWindow
* "🎓 Try It Yourself" toggle → student fills answer, validates

Comparison panel shows side-by-side cost estimates once ≥ 2 methods
have been calculated.
"""

from __future__ import annotations

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Tuple

from pmhelper.gui.widgets.sortable_treeview import enhance_treeview

from pmhelper.core.cost_estimation import (
    AdjustmentFactor, AnalogousEstimator,
    WorkPackage, BottomUpEstimator,
    WorkElement, WorkElementEstimator,
    PowerSizingEstimator,
    UnitFactorItem, UnitFactorEstimator,
    LearningCurveEstimator,
    CostEstimateResult, METHOD_LABELS,
)

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame, WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import plotly_learning_curve, PLOTLY_AVAILABLE as _PLT_AVAIL
    _PLOTLY_EMBED = WEBVIEW2_AVAILABLE and _PLT_AVAIL
except ImportError:
    _PLOTLY_EMBED = False

_DEMO_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "data", "demos", "v2", "cost_estimation_demo.json",
))

if not os.path.exists(_DEMO_PATH):
    _here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        _candidate = os.path.join(
            _here,
            "data",
            "demos",
            "v2",
            "cost_estimation_demo.json")
        if os.path.exists(_candidate):
            _DEMO_PATH = _candidate
            break
        _here = os.path.dirname(_here)


# ════════════════════════════════════════════════════════════════════
#  Outer tab container
# ════════════════════════════════════════════════════════════════════

class CostEstimationTabEdu:
    """Cost Estimation tab — method selector + 7 input panels."""

    _METHOD_KEYS = [
        "analogous", "bottom_up", "work_element",
        "power_sizing", "unit_factor", "cost_capacity", "learning_curve",
    ]

    def __init__(self, parent, state, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self._mode = "UG"
        self._results: Dict[str, CostEstimateResult] = {}

        self.frame = ttk.Frame(parent)
        self._build_ui()

    # ── Public interface ─────────────────────────────────────────

    def set_mode(self, mode: str):
        self._mode = mode.upper()
        for panel in getattr(self, "_panels", {}).values():
            panel.set_mode(self._mode)

    def on_tab_selected(self):
        pass

    def get_figures(self) -> list:
        return []

    # ── UI Construction ──────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self.frame)
        top.pack(fill=tk.X, padx=6, pady=(5, 2))
        ttk.Label(top, text="Cost Estimation Techniques",
                  font=("TkDefaultFont", 11, "bold")).pack(side=tk.LEFT)

        # B5: method Combobox (replaces left-panel Listbox)
        ttk.Separator(
            top,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=10,
            fill=tk.Y)
        ttk.Label(top, text="Method:").pack(side=tk.LEFT)
        self._method_combo = ttk.Combobox(top, values=METHOD_LABELS,
                                          state="readonly", width=30)
        self._method_combo.current(0)
        self._method_combo.pack(side=tk.LEFT, padx=(4, 0))
        self._method_combo.bind("<<ComboboxSelected>>", self._on_method_select)

        # B5: Compare button — disabled until ≥2 methods calculated
        self._compare_btn = ttk.Button(top, text="⚖ Compare Methods",
                                       command=self._show_comparison,
                                       state="disabled")
        self._compare_btn.pack(side=tk.RIGHT)
        ttk.Button(top, text="📖 Theory Overview",
                   command=self._show_theory).pack(side=tk.RIGHT, padx=(0, 6))

        # Main area: full-width method panels (no left sidebar)
        right_frame = ttk.Frame(self.frame)
        right_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        self._panels: Dict[str, _MethodPanel] = {
            "analogous": _AnalogousPanel(right_frame, self),
            "bottom_up": _BottomUpPanel(right_frame, self),
            "work_element": _WorkElementPanel(right_frame, self),
            "power_sizing": _PowerSizingPanel(right_frame, self, label="Power Sizing"),
            "unit_factor": _UnitFactorPanel(right_frame, self),
            "cost_capacity": _PowerSizingPanel(right_frame, self, label="Cost-Capacity Index"),
            "learning_curve": _LearningCurvePanel(right_frame, self),
        }
        for panel in self._panels.values():
            panel.frame.place(relwidth=1, relheight=1)

        self._active_key = "analogous"
        self._show_panel("analogous")

    def _on_method_select(self, event=None):
        sel = self._method_combo.current()
        if sel < 0:
            return
        key = self._METHOD_KEYS[sel]
        self._active_key = key
        self._show_panel(key)

    # ── WBS → Cost Estimation link (11.9) ────────────────────────

    def load_bottom_up_from_wbs(self, items) -> None:
        """Populate Bottom-Up from WBS leaf ``(name, cost)`` pairs and show it."""
        self._panels["bottom_up"].load_work_packages(items)
        self._active_key = "bottom_up"
        self._method_combo.current(self._METHOD_KEYS.index("bottom_up"))
        self._show_panel("bottom_up")

    def _show_panel(self, key: str):
        for k, panel in self._panels.items():
            panel.frame.lower()
        self._panels[key].frame.lift()

    # ── Theory worked solution ────────────────────────────────────

    def _show_theory(self):
        from pmhelper.core.cost_estimation_step_generator import (
            cost_estimation_theory_steps)
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        WorkedSolutionWindow(
            self.frame,
            "Cost Estimation — Theory & Overview",
            cost_estimation_theory_steps(),
        )

    # ── Comparison panel ─────────────────────────────────────────

    def _show_comparison(self):
        if len(self._results) < 1:
            messagebox.showinfo(
                "Compare Methods",
                "Calculate at least one method first.")
            return
        _ComparisonWindow(self.frame, self._results)

    # ── Called by each panel when a result is ready ───────────────

    def record_result(self, key: str, result: CostEstimateResult):
        self._results[key] = result
        self._update_compare_btn_state()

    def _update_compare_btn_state(self):
        """Enable Compare button only when ≥2 methods have results (B5)."""
        state = "normal" if len(self._results) >= 2 else "disabled"
        self._compare_btn.configure(state=state)


# ════════════════════════════════════════════════════════════════════
#  Base method panel
# ════════════════════════════════════════════════════════════════════

class _MethodPanel:
    """Abstract base for the 7 method panels."""

    def __init__(self, parent: tk.Widget, owner: CostEstimationTabEdu,
                 title: str, method_key: str):
        self.parent = parent
        self.owner = owner
        self.method_key = method_key
        self._try_mode = False
        self._worked_btn = None

        self.frame = ttk.Frame(parent)
        lf = ttk.LabelFrame(self.frame, text=title)
        lf.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Toolbar
        tb = ttk.Frame(lf)
        tb.pack(fill=tk.X, padx=4, pady=(4, 2))
        self._build_toolbar(tb)

        # Scrollable content area
        _scroll_outer = ttk.Frame(lf)
        _scroll_outer.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        _vsb = ttk.Scrollbar(_scroll_outer, orient=tk.VERTICAL)
        _vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tiy_canvas = tk.Canvas(_scroll_outer, yscrollcommand=_vsb.set,
                                     highlightthickness=0)
        self._tiy_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        _vsb.config(command=self._tiy_canvas.yview)
        self._inner_content = ttk.Frame(self._tiy_canvas)
        _tiy_win = self._tiy_canvas.create_window(
            (0, 0), window=self._inner_content, anchor='nw')
        self._inner_content.bind(
            '<Configure>', lambda e: self._tiy_canvas.configure(
                scrollregion=self._tiy_canvas.bbox('all')))
        self._tiy_canvas.bind(
            '<Configure>',
            lambda e: self._tiy_canvas.itemconfig(
                _tiy_win,
                width=e.width))
        _scroll_outer.bind('<Enter>', lambda e: self._tiy_canvas.bind_all(
            '<MouseWheel>', lambda ev: self._tiy_canvas.yview_scroll(int(-1 * (ev.delta / 120)), 'units')))
        _scroll_outer.bind(
            '<Leave>',
            lambda e: self._tiy_canvas.unbind_all('<MouseWheel>'))
        content = self._inner_content
        self._build_content(content)

    def _build_toolbar(self, parent: ttk.Frame):
        ttk.Button(parent, text="▶ Calculate",
                   command=self._calculate).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            parent,
            text="📂 Load Demo",
            command=self._load_demo_data).pack(
            side=tk.LEFT,
            padx=(
                0,
                6))
        self._worked_btn = ttk.Button(
            parent,
            text="📊 Show All Calculations",
            command=self._show_worked_solution)
        self._worked_btn.pack(side=tk.LEFT, padx=(0, 6))
        self._try_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="🎓 Try It Yourself",
                        variable=self._try_var,
                        command=self._toggle_practice).pack(side=tk.RIGHT)

    def set_mode(self, mode: str):
        """Show the all-calculations button only in UG mode."""
        if self._worked_btn is None:
            return
        if mode.upper() == "UG":
            self._worked_btn.pack(side=tk.LEFT, padx=(0, 6))
        else:
            self._worked_btn.pack_forget()

    def _build_content(self, parent: ttk.Frame):
        """Subclass implements input + results."""
        raise NotImplementedError

    def _calculate(self):
        raise NotImplementedError

    def _show_worked_solution(self):
        raise NotImplementedError

    def _load_demo_data(self):
        raise NotImplementedError

    # ── Practice helpers ─────────────────────────────────────────

    def _toggle_practice(self):
        self._try_mode = self._try_var.get()
        self._on_toggle_practice(self._try_mode)
        if self._try_mode and hasattr(self, '_tiy_canvas'):
            self._inner_content.update_idletasks()
            self._tiy_canvas.yview_moveto(1.0)

    def _on_toggle_practice(self, active: bool):
        pass  # override in subclass if needed

    # ── Results display helper ────────────────────────────────────

    def _show_result_in_tree(
            self,
            tree: ttk.Treeview,
            result: CostEstimateResult):
        tree.delete(*tree.get_children())
        for label, val in result.breakdown:
            if isinstance(val, float):
                tree.insert("", tk.END, values=(label, f"{val:,.4f}"))
            else:
                tree.insert("", tk.END, values=(label, str(val)))

    def _build_result_tree(self, parent: ttk.Frame) -> ttk.Treeview:
        """Standard 2-column treeview for breakdown results."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=("item", "value"),
                            show="headings", height=8)
        tree.heading("item", text="Item")
        tree.heading("value", text="Value")
        tree.column("item", width=240, anchor=tk.W)
        tree.column("value", width=140, anchor=tk.E)
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        enhance_treeview(tree)
        return tree

    def _build_summary_bar(self, parent: ttk.Frame):
        f = ttk.Frame(parent)
        f.pack(fill=tk.X, pady=(4, 0))
        self._summary_var = tk.StringVar()
        self._interp_var = tk.StringVar()
        ttk.Label(f, textvariable=self._summary_var,
                  font=("TkDefaultFont", 10, "bold"),
                  foreground="#1d4ed8").pack(anchor=tk.W)
        ttk.Label(f, textvariable=self._interp_var,
                  foreground="grey", wraplength=600).pack(anchor=tk.W)

    def _update_summary(self, result: CostEstimateResult):
        if hasattr(self, "_summary_var"):
            self._summary_var.set(
                f"Estimated Cost: {result.total_cost:,.2f}")
        if hasattr(self, "_interp_var"):
            self._interp_var.set(result.interpretation)
        self.owner.record_result(self.method_key, result)

    def _load_demo_section(self, section_key: str) -> Optional[dict]:
        """Load a specific section from the cost estimation demo file."""
        if not os.path.exists(_DEMO_PATH):
            messagebox.showerror("Load Demo",
                                 f"Demo file not found:\n{_DEMO_PATH}")
            return None
        with open(_DEMO_PATH, encoding="utf-8") as fh:
            demo = json.load(fh)
        return demo.get(section_key)

    def _show_practice_result(self, ok: bool, msg: str):
        color = "#15803d" if ok else "#b91c1c"
        icon = "✓" if ok else "✗"
        if hasattr(self, "_prac_result_var"):
            self._prac_result_var.set(f"{icon} {msg}")
            if hasattr(self, "_prac_lbl"):
                self._prac_lbl.config(foreground=color)


# ════════════════════════════════════════════════════════════════════
#  Panel 1 — Analogous (Top-Down)
# ════════════════════════════════════════════════════════════════════

class _AnalogousPanel(_MethodPanel):
    def __init__(self, parent, owner):
        super().__init__(parent, owner,
                         title="Top-Down (Analogous) Estimation",
                         method_key="analogous")

    def _build_content(self, parent: ttk.Frame):
        # Inputs
        inp = ttk.LabelFrame(parent, text="Inputs")
        inp.pack(fill=tk.X, pady=(0, 6))

        row = ttk.Frame(inp)
        row.pack(fill=tk.X, padx=4, pady=2)
        ttk.Label(row, text="Reference Project Cost:", width=26,
                  anchor=tk.W).pack(side=tk.LEFT)
        self._ref_cost_var = tk.StringVar(value="100000")
        ttk.Entry(row, textvariable=self._ref_cost_var, width=14).pack(
            side=tk.LEFT)

        # Factors table
        ftable_lf = ttk.LabelFrame(
            inp, text="Adjustment Factors  (name | multiplier)")
        ftable_lf.pack(fill=tk.X, padx=4, pady=4)
        self._factors_frame = ttk.Frame(ftable_lf)
        self._factors_frame.pack(fill=tk.X, padx=2, pady=2)
        self._factor_rows: List[Tuple[tk.StringVar, tk.StringVar]] = []
        ttk.Button(inp, text="+ Add Factor",
                   command=self._add_factor_row).pack(
            anchor=tk.W, padx=4, pady=(0, 4))

        # Results
        res_lf = ttk.LabelFrame(parent, text="Results")
        res_lf.pack(fill=tk.BOTH, expand=True)
        self._tree = self._build_result_tree(res_lf)
        self._build_summary_bar(res_lf)
        self._build_practice_frame(parent)

    def _add_factor_row(self, name: str = "", factor: str = "1.0"):
        row = ttk.Frame(self._factors_frame)
        row.pack(fill=tk.X, pady=1)
        nv = tk.StringVar(value=name)
        fv = tk.StringVar(value=factor)
        self._factor_rows.append((nv, fv))
        ttk.Entry(
            row,
            textvariable=nv,
            width=20).pack(
            side=tk.LEFT,
            padx=(
                0,
                4))
        ttk.Entry(
            row,
            textvariable=fv,
            width=10).pack(
            side=tk.LEFT,
            padx=(
                0,
                4))
        ttk.Button(
            row, text="−", width=2, command=lambda r=row, t=(
                nv, fv): self._remove_factor(
                r, t)).pack(
            side=tk.LEFT)

    def _remove_factor(self, row_widget, row_tuple):
        row_widget.destroy()
        if row_tuple in self._factor_rows:
            self._factor_rows.remove(row_tuple)

    def _calculate(self):
        try:
            ref = float(self._ref_cost_var.get())
        except ValueError:
            messagebox.showerror(
                "Input Error",
                "Reference cost must be a number.")
            return
        factors = []
        for nv, fv in self._factor_rows:
            name = nv.get().strip() or "Factor"
            try:
                f = float(fv.get())
            except ValueError:
                messagebox.showerror("Input Error",
                                     f"Invalid factor value for '{name}'.")
                return
            factors.append(AdjustmentFactor(name=name, factor=f))

        result = AnalogousEstimator().estimate(ref, factors)
        self._last_result = (result, ref, factors)
        self._show_result_in_tree(self._tree, result)
        self._update_summary(result)

    def _show_worked_solution(self):
        from pmhelper.core.cost_estimation_step_generator import analogous_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        if not hasattr(self, "_last_result"):
            self._calculate()
            if not hasattr(self, "_last_result"):
                return
        result, ref, factors = self._last_result
        WorkedSolutionWindow(
            self.frame,
            "Top-Down (Analogous) — Worked Solution",
            analogous_steps(
                result,
                ref,
                factors))

    def _load_demo_data(self):
        data = self._load_demo_section("analogous")
        if not data:
            return
        self._ref_cost_var.set(str(data.get("reference_cost", 100000)))
        for row in list(self._factors_frame.winfo_children()):
            row.destroy()
        self._factor_rows.clear()
        for f in data.get("factors", []):
            self._add_factor_row(f.get("name", ""), str(f.get("factor", 1.0)))
        self._calculate()

    def _build_practice_frame(self, parent: ttk.Frame):
        self._prac_frame = ttk.LabelFrame(parent, text="🎓 Try It Yourself")
        f = ttk.Frame(self._prac_frame)
        f.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(f, text="What is the estimated cost?  C_new =",
                  foreground="navy").pack(side=tk.LEFT)
        self._prac_answer = tk.StringVar()
        ttk.Entry(f, textvariable=self._prac_answer, width=14).pack(
            side=tk.LEFT, padx=(4, 4))
        ttk.Button(f, text="✓ Check", command=self._check_practice).pack(
            side=tk.LEFT)
        self._prac_result_var = tk.StringVar()
        self._prac_lbl = ttk.Label(self._prac_frame,
                                   textvariable=self._prac_result_var)
        self._prac_lbl.pack(anchor=tk.W, padx=6)

    def _on_toggle_practice(self, active: bool):
        if active:
            self._prac_frame.pack(fill=tk.X, padx=4, pady=(2, 4))
        else:
            self._prac_frame.pack_forget()

    def _check_practice(self):
        if not hasattr(self, "_last_result"):
            messagebox.showinfo("Try It Yourself", "Calculate first.")
            return
        try:
            answer = float(self._prac_answer.get())
        except ValueError:
            messagebox.showerror("Input", "Enter a numeric answer.")
            return
        expected = self._last_result[0].total_cost
        ok = abs(answer - expected) / max(abs(expected), 1) < 0.01
        self._show_practice_result(
            ok,
            f"Correct! C_new = {
                expected:,.2f}" if ok else f"Not quite. Expected {
                expected:,.2f}, you entered {
                answer:,.2f}",
        )


# ════════════════════════════════════════════════════════════════════
#  Panel 2 — Bottom-Up
# ════════════════════════════════════════════════════════════════════

class _BottomUpPanel(_MethodPanel):
    def __init__(self, parent, owner):
        super().__init__(parent, owner,
                         title="Bottom-Up Estimation",
                         method_key="bottom_up")

    def _build_content(self, parent: ttk.Frame):
        hdr = ttk.Frame(parent)
        hdr.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(
            hdr,
            text="Work Package",
            width=20).grid(
            row=0,
            column=0,
            padx=2)
        ttk.Label(hdr, text="Labour $", width=10).grid(row=0, column=1, padx=2)
        ttk.Label(
            hdr,
            text="Material $",
            width=10).grid(
            row=0,
            column=2,
            padx=2)
        ttk.Label(
            hdr,
            text="Equipment $",
            width=10).grid(
            row=0,
            column=3,
            padx=2)
        ttk.Label(
            hdr,
            text="Overhead %",
            width=10).grid(
            row=0,
            column=4,
            padx=2)

        self._wp_scroll = ttk.Frame(parent)
        self._wp_scroll.pack(fill=tk.X)
        self._wp_rows: List[Tuple] = []
        ttk.Button(parent, text="+ Add Work Package",
                   command=self._add_wp_row).pack(anchor=tk.W, pady=2)
        ttk.Button(parent, text="📂 Load from Project",
                   command=self._load_from_project).pack(anchor=tk.W, pady=2)

        res_lf = ttk.LabelFrame(parent, text="Results")
        res_lf.pack(fill=tk.BOTH, expand=True)
        self._tree = self._build_result_tree(res_lf)
        self._build_summary_bar(res_lf)
        self._build_practice_frame(parent)

        # Seed 3 rows
        for name, l, m, e, o in [
            ("Design", "5000", "0", "0", "10"),
            ("Development", "15000", "2000", "0", "10"),
            ("Testing", "4000", "0", "500", "10"),
        ]:
            self._add_wp_row(name, l, m, e, o)

    def load_work_packages(self, items):
        """Replace all rows with ``(name, cost)`` pairs (WBS → Bottom-Up).

        The WBS already carries a per-leaf total, so the cost lands in
        Labour and overhead is zeroed — adding the default 10% on top
        would silently inflate a figure the user already reconciled.
        """
        for child in self._wp_scroll.winfo_children():
            child.destroy()
        self._wp_rows = []
        for name, cost in items:
            self._add_wp_row(name, f"{float(cost):g}", "0", "0", "0")
        if not self._wp_rows:
            self._add_wp_row()

    def _add_wp_row(self, name="", labour="0", material="0",
                    equipment="0", overhead="10"):
        row = ttk.Frame(self._wp_scroll)
        row.pack(fill=tk.X, pady=1)
        nv = tk.StringVar(value=name)
        lv = tk.StringVar(value=labour)
        mv = tk.StringVar(value=material)
        ev = tk.StringVar(value=equipment)
        ov = tk.StringVar(value=overhead)
        self._wp_rows.append((nv, lv, mv, ev, ov))
        ttk.Entry(row, textvariable=nv, width=18).pack(side=tk.LEFT, padx=1)
        ttk.Entry(row, textvariable=lv, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Entry(row, textvariable=mv, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Entry(row, textvariable=ev, width=10).pack(side=tk.LEFT, padx=1)
        ttk.Entry(row, textvariable=ov, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(
            row, text="−", width=2, command=lambda r=row, t=(
                nv, lv, mv, ev, ov): self._remove_wp(
                r, t)).pack(
            side=tk.LEFT, padx=1)

    def _remove_wp(self, row_widget, row_tuple):
        row_widget.destroy()
        if row_tuple in self._wp_rows:
            self._wp_rows.remove(row_tuple)

    def _load_from_project(self):
        if self.owner.main_window is None:
            return
        state = self.owner.state
        wbs = getattr(state, "wbs_tree", None)
        if wbs is None:
            messagebox.showinfo(
                "Load from Project", "No WBS data found. Build a WBS first.")
            return
        # Clear and re-populate from WBS nodes
        for w in self._wp_scroll.winfo_children():
            w.destroy()
        self._wp_rows.clear()
        nodes = getattr(wbs, "nodes", [])
        for node in nodes:
            if not node.get("children"):  # leaf nodes
                self._add_wp_row(
                    node.get("name", ""),
                    str(node.get("labour_cost", 0)),
                    str(node.get("material_cost", 0)),
                    str(node.get("equipment_cost", 0)),
                    str(node.get("overhead_pct", 10)),
                )
        if not self._wp_rows:
            messagebox.showinfo("Load from Project",
                                "No WBS leaf nodes found.")

    def _calculate(self):
        wps = []
        for nv, lv, mv, ev, ov in self._wp_rows:
            try:
                wps.append(WorkPackage(
                    name=nv.get().strip() or "WP",
                    labour_cost=float(lv.get()),
                    material_cost=float(mv.get()),
                    equipment_cost=float(ev.get()),
                    overhead_pct=float(ov.get()),
                ))
            except ValueError:
                messagebox.showerror("Input Error",
                                     f"Invalid number in row '{nv.get()}'.")
                return
        result = BottomUpEstimator().estimate(wps)
        self._last_result = (result, wps)
        self._show_result_in_tree(self._tree, result)
        self._update_summary(result)

    def _show_worked_solution(self):
        from pmhelper.core.cost_estimation_step_generator import bottom_up_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        if not hasattr(self, "_last_result"):
            self._calculate()
            if not hasattr(self, "_last_result"):
                return
        result, wps = self._last_result
        WorkedSolutionWindow(self.frame, "Bottom-Up — Worked Solution",
                             bottom_up_steps(result, wps))

    def _load_demo_data(self):
        data = self._load_demo_section("bottom_up")
        if not data:
            return
        for w in self._wp_scroll.winfo_children():
            w.destroy()
        self._wp_rows.clear()
        for wp in data.get("work_packages", []):
            self._add_wp_row(
                wp.get("name", "WP"),
                str(wp.get("labour_cost", 0)),
                str(wp.get("material_cost", 0)),
                str(wp.get("equipment_cost", 0)),
                str(wp.get("overhead_pct", 10)),
            )
        self._calculate()

    def _build_practice_frame(self, parent):
        self._prac_frame = ttk.LabelFrame(parent, text="🎓 Try It Yourself")
        f = ttk.Frame(self._prac_frame)
        f.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(f, text="What is the total bottom-up estimate?  C_total =",
                  foreground="navy").pack(side=tk.LEFT)
        self._prac_answer = tk.StringVar()
        ttk.Entry(f, textvariable=self._prac_answer, width=14).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(f, text="✓ Check", command=self._check_practice).pack(
            side=tk.LEFT)
        self._prac_result_var = tk.StringVar()
        self._prac_lbl = ttk.Label(self._prac_frame,
                                   textvariable=self._prac_result_var)
        self._prac_lbl.pack(anchor=tk.W, padx=6)

    def _on_toggle_practice(self, active):
        if active:
            self._prac_frame.pack(fill=tk.X, padx=4, pady=(2, 4))
        else:
            self._prac_frame.pack_forget()

    def _check_practice(self):
        if not hasattr(self, "_last_result"):
            messagebox.showinfo("Try It Yourself", "Calculate first.")
            return
        try:
            answer = float(self._prac_answer.get())
        except ValueError:
            return
        expected = self._last_result[0].total_cost
        ok = abs(answer - expected) / max(abs(expected), 1) < 0.01
        self._show_practice_result(
            ok,
            f"Correct! C_total = {expected:,.2f}" if ok
            else f"Expected {expected:,.2f}, you entered {answer:,.2f}",
        )


# ════════════════════════════════════════════════════════════════════
#  Panel 3 — Work Element
# ════════════════════════════════════════════════════════════════════

class _WorkElementPanel(_MethodPanel):
    def __init__(self, parent, owner):
        super().__init__(parent, owner,
                         title="Work Element (Template) Estimation",
                         method_key="work_element")

    def _build_content(self, parent: ttk.Frame):
        hdr = ttk.Frame(parent)
        hdr.pack(fill=tk.X, pady=(0, 2))
        for col, (text, w) in enumerate([
            ("Element", 18), ("Hours", 8), ("Rate $/hr", 8),
            ("Material $", 10), ("Equipment $", 10)
        ]):
            ttk.Label(hdr, text=text, width=w).grid(row=0, column=col, padx=2)

        self._el_scroll = ttk.Frame(parent)
        self._el_scroll.pack(fill=tk.X)
        self._el_rows: List[Tuple] = []
        ttk.Button(parent, text="+ Add Element",
                   command=self._add_el_row).pack(anchor=tk.W, pady=2)

        res_lf = ttk.LabelFrame(parent, text="Results")
        res_lf.pack(fill=tk.BOTH, expand=True)
        self._tree = self._build_result_tree(res_lf)
        self._build_summary_bar(res_lf)
        self._build_practice_frame(parent)

        for name, h, r, m, e in [
            ("Foundation", "80", "45", "3000", "1500"),
            ("Framing", "120", "45", "8000", "2000"),
            ("Electrical", "60", "60", "2500", "500"),
        ]:
            self._add_el_row(name, h, r, m, e)

    def _add_el_row(self, name="", hours="0", rate="0",
                    material="0", equipment="0"):
        row = ttk.Frame(self._el_scroll)
        row.pack(fill=tk.X, pady=1)
        nv = tk.StringVar(value=name)
        hv = tk.StringVar(value=hours)
        rv = tk.StringVar(value=rate)
        mv = tk.StringVar(value=material)
        ev = tk.StringVar(value=equipment)
        self._el_rows.append((nv, hv, rv, mv, ev))
        for sv, w in [(nv, 16), (hv, 8), (rv, 8), (mv, 10), (ev, 10)]:
            ttk.Entry(row, textvariable=sv, width=w).pack(side=tk.LEFT, padx=1)
        ttk.Button(
            row, text="−", width=2, command=lambda r=row, t=(
                nv, hv, rv, mv, ev): self._remove_el(
                r, t)).pack(
            side=tk.LEFT)

    def _remove_el(self, row_widget, row_tuple):
        row_widget.destroy()
        if row_tuple in self._el_rows:
            self._el_rows.remove(row_tuple)

    def _calculate(self):
        els = []
        for nv, hv, rv, mv, ev in self._el_rows:
            try:
                els.append(WorkElement(
                    name=nv.get().strip() or "Element",
                    hours=float(hv.get()),
                    hourly_rate=float(rv.get()),
                    material_cost=float(mv.get()),
                    equipment_cost=float(ev.get()),
                ))
            except ValueError:
                messagebox.showerror("Input Error",
                                     f"Invalid number in row '{nv.get()}'.")
                return
        result = WorkElementEstimator().estimate(els)
        self._last_result = (result, els)
        self._show_result_in_tree(self._tree, result)
        self._update_summary(result)

    def _show_worked_solution(self):
        from pmhelper.core.cost_estimation_step_generator import work_element_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        if not hasattr(self, "_last_result"):
            self._calculate()
            if not hasattr(self, "_last_result"):
                return
        result, els = self._last_result
        WorkedSolutionWindow(self.frame, "Work Element — Worked Solution",
                             work_element_steps(result, els))

    def _load_demo_data(self):
        data = self._load_demo_section("work_element")
        if not data:
            return
        for w in self._el_scroll.winfo_children():
            w.destroy()
        self._el_rows.clear()
        for el in data.get("elements", []):
            self._add_el_row(
                el.get("name", ""),
                str(el.get("hours", 0)),
                str(el.get("hourly_rate", 0)),
                str(el.get("material_cost", 0)),
                str(el.get("equipment_cost", 0)),
            )
        self._calculate()

    def _build_practice_frame(self, parent):
        self._prac_frame = ttk.LabelFrame(parent, text="🎓 Try It Yourself")
        f = ttk.Frame(self._prac_frame)
        f.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(f, text="Total cost estimate =",
                  foreground="navy").pack(side=tk.LEFT)
        self._prac_answer = tk.StringVar()
        ttk.Entry(f, textvariable=self._prac_answer, width=14).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(f, text="✓ Check", command=self._check_practice).pack(
            side=tk.LEFT)
        self._prac_result_var = tk.StringVar()
        self._prac_lbl = ttk.Label(self._prac_frame,
                                   textvariable=self._prac_result_var)
        self._prac_lbl.pack(anchor=tk.W, padx=6)

    def _on_toggle_practice(self, active):
        if active:
            self._prac_frame.pack(fill=tk.X, padx=4, pady=(2, 4))
        else:
            self._prac_frame.pack_forget()

    def _check_practice(self):
        if not hasattr(self, "_last_result"):
            messagebox.showinfo("Try It Yourself", "Calculate first.")
            return
        try:
            answer = float(self._prac_answer.get())
        except ValueError:
            return
        expected = self._last_result[0].total_cost
        ok = abs(answer - expected) / max(abs(expected), 1) < 0.01
        self._show_practice_result(
            ok,
            f"Correct! = {expected:,.2f}" if ok
            else f"Expected {expected:,.2f}, you entered {answer:,.2f}",
        )


# ════════════════════════════════════════════════════════════════════
#  Panel 4 & 6 — Power Sizing / Cost-Capacity Index
# ════════════════════════════════════════════════════════════════════

class _PowerSizingPanel(_MethodPanel):
    def __init__(self, parent, owner, label: str = "Power Sizing"):
        key = "power_sizing" if label == "Power Sizing" else "cost_capacity"
        super().__init__(parent, owner, title=f"{label} Estimation",
                         method_key=key)

    def _build_content(self, parent: ttk.Frame):
        inp = ttk.LabelFrame(parent, text="Inputs")
        inp.pack(fill=tk.X, pady=(0, 6))

        fields = [
            ("Reference Cost (C_ref):", "ref_cost_var", "500000"),
            ("Reference Capacity (S_ref):", "ref_cap_var", "100"),
            ("New Capacity (S_new):", "new_cap_var", "150"),
            ("Sizing Exponent (x):", "exp_var", "0.6"),
        ]
        for label_text, attr, default in fields:
            row = ttk.Frame(inp)
            row.pack(fill=tk.X, padx=4, pady=2)
            ttk.Label(row, text=label_text, width=28, anchor=tk.W).pack(
                side=tk.LEFT)
            v = tk.StringVar(value=default)
            setattr(self, f"_{attr}", v)
            ttk.Entry(row, textvariable=v, width=14).pack(side=tk.LEFT)

        res_lf = ttk.LabelFrame(parent, text="Results")
        res_lf.pack(fill=tk.BOTH, expand=True)
        self._tree = self._build_result_tree(res_lf)
        self._build_summary_bar(res_lf)
        self._build_practice_frame(parent)

    def _calculate(self):
        try:
            ref_c = float(self._ref_cost_var.get())
            ref_s = float(self._ref_cap_var.get())
            new_s = float(self._new_cap_var.get())
            exp = float(self._exp_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "All fields must be numbers.")
            return
        try:
            result = PowerSizingEstimator().estimate(ref_c, ref_s, new_s, exp)
        except ValueError as exc:
            messagebox.showerror("Calculation Error", str(exc))
            return
        self._last_result = (result, ref_c, ref_s, new_s, exp)
        self._show_result_in_tree(self._tree, result)
        self._update_summary(result)

    def _show_worked_solution(self):
        from pmhelper.core.cost_estimation_step_generator import power_sizing_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        if not hasattr(self, "_last_result"):
            self._calculate()
            if not hasattr(self, "_last_result"):
                return
        result, rc, rs, ns, exp = self._last_result
        WorkedSolutionWindow(self.frame, "Power Sizing — Worked Solution",
                             power_sizing_steps(result, rc, rs, ns, exp))

    def _load_demo_data(self):
        data = self._load_demo_section("power_sizing")
        if not data:
            return
        self._ref_cost_var.set(str(data.get("reference_cost", 500000)))
        self._ref_cap_var.set(str(data.get("reference_capacity", 100)))
        self._new_cap_var.set(str(data.get("new_capacity", 150)))
        self._exp_var.set(str(data.get("exponent", 0.6)))
        self._calculate()

    def _build_practice_frame(self, parent):
        self._prac_frame = ttk.LabelFrame(parent, text="🎓 Try It Yourself")
        f = ttk.Frame(self._prac_frame)
        f.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(f, text="Estimated Cost C_new =",
                  foreground="navy").pack(side=tk.LEFT)
        self._prac_answer = tk.StringVar()
        ttk.Entry(f, textvariable=self._prac_answer, width=14).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(f, text="✓ Check", command=self._check_practice).pack(
            side=tk.LEFT)
        self._prac_result_var = tk.StringVar()
        self._prac_lbl = ttk.Label(self._prac_frame,
                                   textvariable=self._prac_result_var)
        self._prac_lbl.pack(anchor=tk.W, padx=6)

    def _on_toggle_practice(self, active):
        if active:
            self._prac_frame.pack(fill=tk.X, padx=4, pady=(2, 4))
        else:
            self._prac_frame.pack_forget()

    def _check_practice(self):
        if not hasattr(self, "_last_result"):
            messagebox.showinfo("Try It Yourself", "Calculate first.")
            return
        try:
            answer = float(self._prac_answer.get())
        except ValueError:
            return
        expected = self._last_result[0].total_cost
        ok = abs(answer - expected) / max(abs(expected), 1) < 0.01
        self._show_practice_result(
            ok,
            f"Correct! C_new = {expected:,.2f}" if ok
            else f"Expected {expected:,.2f}, you entered {answer:,.2f}",
        )


# ════════════════════════════════════════════════════════════════════
#  Panel 5 — Unit / Factor
# ════════════════════════════════════════════════════════════════════

class _UnitFactorPanel(_MethodPanel):
    def __init__(self, parent, owner):
        super().__init__(parent, owner,
                         title="Unit / Factor Estimation",
                         method_key="unit_factor")

    def _build_content(self, parent: ttk.Frame):
        hdr = ttk.Frame(parent)
        hdr.pack(fill=tk.X, pady=(0, 2))
        for col, (text, w) in enumerate([
            ("Item", 18), ("Unit Cost $", 10), ("Quantity", 10), ("Factor", 8)
        ]):
            ttk.Label(hdr, text=text, width=w).grid(row=0, column=col, padx=2)

        self._item_scroll = ttk.Frame(parent)
        self._item_scroll.pack(fill=tk.X)
        self._item_rows: List[Tuple] = []
        ttk.Button(parent, text="+ Add Item",
                   command=self._add_item_row).pack(anchor=tk.W, pady=2)

        res_lf = ttk.LabelFrame(parent, text="Results")
        res_lf.pack(fill=tk.BOTH, expand=True)
        self._tree = self._build_result_tree(res_lf)
        self._build_summary_bar(res_lf)
        self._build_practice_frame(parent)

        for name, uc, qty, fac in [
            ("Concrete (m³)", "120", "250", "1.05"),
            ("Steel reinforcement (ton)", "800", "30", "1.10"),
            ("Labour (days)", "350", "180", "1.0"),
        ]:
            self._add_item_row(name, uc, qty, fac)

    def _add_item_row(self, name="", unit_cost="0", qty="1", factor="1.0"):
        row = ttk.Frame(self._item_scroll)
        row.pack(fill=tk.X, pady=1)
        nv = tk.StringVar(value=name)
        uv = tk.StringVar(value=unit_cost)
        qv = tk.StringVar(value=qty)
        fv = tk.StringVar(value=factor)
        self._item_rows.append((nv, uv, qv, fv))
        for sv, w in [(nv, 16), (uv, 10), (qv, 10), (fv, 8)]:
            ttk.Entry(row, textvariable=sv, width=w).pack(side=tk.LEFT, padx=1)
        ttk.Button(
            row, text="−", width=2, command=lambda r=row, t=(
                nv, uv, qv, fv): self._remove_item(
                r, t)).pack(
            side=tk.LEFT)

    def _remove_item(self, row_widget, row_tuple):
        row_widget.destroy()
        if row_tuple in self._item_rows:
            self._item_rows.remove(row_tuple)

    def _calculate(self):
        items = []
        for nv, uv, qv, fv in self._item_rows:
            try:
                items.append(UnitFactorItem(
                    name=nv.get().strip() or "Item",
                    unit_cost=float(uv.get()),
                    quantity=float(qv.get()),
                    factor=float(fv.get()),
                ))
            except ValueError:
                messagebox.showerror("Input Error",
                                     f"Invalid number in row '{nv.get()}'.")
                return
        result = UnitFactorEstimator().estimate(items)
        self._last_result = (result, items)
        self._show_result_in_tree(self._tree, result)
        self._update_summary(result)

    def _show_worked_solution(self):
        from pmhelper.core.cost_estimation_step_generator import unit_factor_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        if not hasattr(self, "_last_result"):
            self._calculate()
            if not hasattr(self, "_last_result"):
                return
        result, items = self._last_result
        WorkedSolutionWindow(self.frame, "Unit/Factor — Worked Solution",
                             unit_factor_steps(result, items))

    def _load_demo_data(self):
        data = self._load_demo_section("unit_factor")
        if not data:
            return
        for w in self._item_scroll.winfo_children():
            w.destroy()
        self._item_rows.clear()
        for item in data.get("items", []):
            self._add_item_row(
                item.get("name", ""),
                str(item.get("unit_cost", 0)),
                str(item.get("quantity", 1)),
                str(item.get("factor", 1.0)),
            )
        self._calculate()

    def _build_practice_frame(self, parent):
        self._prac_frame = ttk.LabelFrame(parent, text="🎓 Try It Yourself")
        f = ttk.Frame(self._prac_frame)
        f.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(f, text="C_total =",
                  foreground="navy").pack(side=tk.LEFT)
        self._prac_answer = tk.StringVar()
        ttk.Entry(f, textvariable=self._prac_answer, width=14).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(f, text="✓ Check", command=self._check_practice).pack(
            side=tk.LEFT)
        self._prac_result_var = tk.StringVar()
        self._prac_lbl = ttk.Label(self._prac_frame,
                                   textvariable=self._prac_result_var)
        self._prac_lbl.pack(anchor=tk.W, padx=6)

    def _on_toggle_practice(self, active):
        if active:
            self._prac_frame.pack(fill=tk.X, padx=4, pady=(2, 4))
        else:
            self._prac_frame.pack_forget()

    def _check_practice(self):
        if not hasattr(self, "_last_result"):
            messagebox.showinfo("Try It Yourself", "Calculate first.")
            return
        try:
            answer = float(self._prac_answer.get())
        except ValueError:
            return
        expected = self._last_result[0].total_cost
        ok = abs(answer - expected) / max(abs(expected), 1) < 0.01
        self._show_practice_result(
            ok,
            f"Correct! = {expected:,.2f}" if ok
            else f"Expected {expected:,.2f}, you entered {answer:,.2f}",
        )


# ════════════════════════════════════════════════════════════════════
#  Panel 7 — Learning Curves
# ════════════════════════════════════════════════════════════════════

class _LearningCurvePanel(_MethodPanel):
    def __init__(self, parent, owner):
        super().__init__(parent, owner,
                         title="Learning Curve Estimation",
                         method_key="learning_curve")

    def _build_content(self, parent: ttk.Frame):
        inp = ttk.LabelFrame(parent, text="Inputs")
        inp.pack(fill=tk.X, pady=(0, 6))

        fields = [
            ("First Unit Cost (T₁):", "t1_var", "1000"),
            ("Learning Rate (e.g. 0.80):", "rate_var", "0.80"),
            ("Target Unit Number (N):", "n_var", "10"),
        ]
        for label_text, attr, default in fields:
            row = ttk.Frame(inp)
            row.pack(fill=tk.X, padx=4, pady=2)
            ttk.Label(row, text=label_text, width=30, anchor=tk.W).pack(
                side=tk.LEFT)
            v = tk.StringVar(value=default)
            setattr(self, f"_{attr}", v)
            ttk.Entry(row, textvariable=v, width=14).pack(side=tk.LEFT)

        ttk.Label(
            inp,
            text="Learning rate: 0.80 = 80% curve (common in manufacturing)",
            foreground="grey",
            font=(
                "TkDefaultFont",
                8,
                "italic")).pack(
            anchor=tk.W,
            padx=4,
            pady=(
                0,
                4))

        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Results breakdown
        res_lf = ttk.LabelFrame(paned, text="Results")
        paned.add(res_lf, weight=2)
        self._tree = self._build_result_tree(res_lf)
        self._build_summary_bar(res_lf)

        # Learning curve chart
        if HAS_MATPLOTLIB:
            chart_lf = ttk.LabelFrame(paned, text="Learning Curve Chart")
            paned.add(chart_lf, weight=3)

            self._render_mode_var = tk.StringVar(value="matplotlib")
            if _PLOTLY_EMBED:
                ctrl = ttk.Frame(chart_lf)
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

            self._mpl_chart_frame = ttk.Frame(chart_lf)
            self._mpl_chart_frame.pack(fill=tk.BOTH, expand=True)
            self._fig = Figure(figsize=(4, 3), dpi=80)
            self._ax = self._fig.add_subplot(111)
            self._canvas = FigureCanvasTkAgg(
                self._fig, master=self._mpl_chart_frame)
            self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self._plotly_frame = None
            if _PLOTLY_EMBED:
                self._plotly_frame = PlotlyChartFrame(chart_lf)

        self._build_practice_frame(parent)

    def _calculate(self):
        try:
            t1 = float(self._t1_var.get())
            rate = float(self._rate_var.get())
            n = int(float(self._n_var.get()))
        except ValueError:
            messagebox.showerror("Input Error", "All fields must be numbers.")
            return
        try:
            result = LearningCurveEstimator().estimate(t1, rate, n,
                                                       build_curve=True)
        except ValueError as exc:
            messagebox.showerror("Calculation Error", str(exc))
            return
        self._last_result = (result, t1, rate, n)
        self._show_result_in_tree(self._tree, result)
        self._update_summary(result)
        if HAS_MATPLOTLIB:
            self._draw_chart(result, t1)

    def _draw_chart(self, result: CostEstimateResult, t1: float):
        if getattr(
                self,
                '_render_mode_var',
                None) and self._render_mode_var.get() == "plotly" and getattr(
                self,
                '_plotly_frame',
                None):
            self._update_plotly_lc(result, t1)
            return
        self._ax.clear()
        curve = result.extra.get("curve", [])
        if not curve:
            return
        ns = [pt["n"] for pt in curve]
        uts = [pt["unit_time"] for pt in curve]
        avgs = [pt["cum_avg"] for pt in curve]
        self._ax.plot(
            ns,
            uts,
            "b-o",
            markersize=3,
            label="Unit Cost",
            linewidth=1.5)
        self._ax.plot(
            ns,
            avgs,
            "r--s",
            markersize=3,
            label="Cumul. Avg",
            linewidth=1.2)
        self._ax.axhline(t1, color="grey", linestyle=":", linewidth=1,
                         label=f"T₁={t1}")
        self._ax.set_xlabel("Unit Number")
        self._ax.set_ylabel("Cost / Time")
        self._ax.set_title("Learning Curve")
        self._ax.legend(fontsize=8)
        self._ax.grid(True, alpha=0.3)
        self._fig.tight_layout()
        self._canvas.draw()

    def _show_worked_solution(self):
        from pmhelper.core.cost_estimation_step_generator import learning_curve_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        if not hasattr(self, "_last_result"):
            self._calculate()
            if not hasattr(self, "_last_result"):
                return
        result, t1, rate, n = self._last_result
        WorkedSolutionWindow(self.frame, "Learning Curves — Worked Solution",
                             learning_curve_steps(result, t1, rate, n))

    def _load_demo_data(self):
        data = self._load_demo_section("learning_curve")
        if not data:
            return
        self._t1_var.set(str(data.get("first_unit_cost", 1000)))
        self._rate_var.set(str(data.get("learning_rate", 0.80)))
        self._n_var.set(str(data.get("target_unit", 10)))
        self._calculate()

    def _build_practice_frame(self, parent):
        self._prac_frame = ttk.LabelFrame(parent, text="🎓 Try It Yourself")
        f = ttk.Frame(self._prac_frame)
        f.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(f, text="Cost of unit N  T_N =",
                  foreground="navy").pack(side=tk.LEFT)
        self._prac_answer = tk.StringVar()
        ttk.Entry(f, textvariable=self._prac_answer, width=14).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(f, text="✓ Check", command=self._check_practice).pack(
            side=tk.LEFT)

        f2 = ttk.Frame(self._prac_frame)
        f2.pack(fill=tk.X, padx=6, pady=2)
        ttk.Label(f2, text="Cumulative Total =",
                  foreground="navy").pack(side=tk.LEFT)
        self._prac_cum_answer = tk.StringVar()
        ttk.Entry(f2, textvariable=self._prac_cum_answer, width=14).pack(
            side=tk.LEFT, padx=4)

        self._prac_result_var = tk.StringVar()
        self._prac_lbl = ttk.Label(self._prac_frame,
                                   textvariable=self._prac_result_var)
        self._prac_lbl.pack(anchor=tk.W, padx=6)

    def _on_toggle_practice(self, active):
        if active:
            self._prac_frame.pack(fill=tk.X, padx=4, pady=(2, 4))
        else:
            self._prac_frame.pack_forget()

    def _check_practice(self):
        if not hasattr(self, "_last_result"):
            messagebox.showinfo("Try It Yourself", "Calculate first.")
            return
        result, t1, rate, n = self._last_result
        try:
            tn_ans = float(self._prac_answer.get())
        except ValueError:
            return
        expected_tn = result.total_cost
        tol = max(abs(expected_tn) * 0.01, 0.001)
        ok = abs(tn_ans - expected_tn) <= tol
        msg = (
            f"T_{n} = {
                expected_tn:,.4f}  ({
                '✓ Correct' if ok else '✗ Incorrect'})\n" f"Cumulative = {
                result.extra.get(
                    'cumulative_total',
                    0):,.4f}")
        self._show_practice_result(ok, msg)

    def _switch_renderer(self):
        mode = self._render_mode_var.get()
        if mode == "plotly" and getattr(self, '_plotly_frame', None):
            self._mpl_chart_frame.pack_forget()
            self._plotly_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            if getattr(self, '_plotly_frame', None):
                self._plotly_frame.pack_forget()
            self._mpl_chart_frame.pack(fill=tk.BOTH, expand=True)
        if hasattr(self, '_last_result'):
            result, t1, rate, n = self._last_result
            self._draw_chart(result, t1)

    def _update_plotly_lc(self, result, t1):
        if not self._plotly_frame:
            return
        try:
            curve = result.extra.get("curve", [])
            fig = plotly_learning_curve(curve, t1)
            if fig:
                self._plotly_frame.update_chart(fig)
        except Exception as e:
            self._plotly_frame.load_html(
                f"<html><body><pre>Error: {e}</pre></body></html>")


# ════════════════════════════════════════════════════════════════════
#  Comparison window
# ════════════════════════════════════════════════════════════════════

class _ComparisonWindow:
    """Pop-up window showing all calculated estimates side by side."""

    _LABEL_MAP = {
        "analogous": "Top-Down",
        "bottom_up": "Bottom-Up",
        "work_element": "Work Element",
        "power_sizing": "Power Sizing",
        "unit_factor": "Unit/Factor",
        "cost_capacity": "Cost-Capacity",
        "learning_curve": "Learning Curves",
    }

    def __init__(self, parent: tk.Widget,
                 results: Dict[str, CostEstimateResult]):
        win = tk.Toplevel(parent)
        win.title("Cost Estimation — Method Comparison")
        win.geometry("900x500")
        win.grab_set()

        ttk.Label(win, text="Method Comparison",
                  font=("TkDefaultFont", 12, "bold")).pack(pady=8)

        # Horizontal layout: table on left, chart on right
        body = ttk.PanedWindow(win, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Left: table
        left = ttk.Frame(body)
        body.add(left, weight=1)

        tree = ttk.Treeview(left, columns=("method", "cost", "interp"),
                            show="headings", height=10)
        tree.heading("method", text="Method")
        tree.heading("cost", text="Estimated Cost")
        tree.heading("interp", text="Notes")
        tree.column("method", width=120, anchor=tk.W)
        tree.column("cost", width=110, anchor=tk.E)
        tree.column("interp", width=200, anchor=tk.W)
        vsb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        enhance_treeview(tree)

        for key, res in results.items():
            label = self._LABEL_MAP.get(key, key)
            tree.insert("", tk.END, values=(
                label, f"{res.total_cost:,.2f}", res.interpretation[:60]))

        # Right: chart
        if HAS_MATPLOTLIB and results:
            right = ttk.Frame(body)
            body.add(right, weight=1)

            fig = Figure(figsize=(5, 4), dpi=90)
            ax = fig.add_subplot(111)
            labels = [self._LABEL_MAP.get(k, k) for k in results]
            costs = [r.total_cost for r in results.values()]
            colors = ["#3b82f6", "#10b981", "#f59e0b",
                      "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6"]
            ax.bar(labels, costs, color=colors[:len(labels)])
            ax.set_ylabel("Estimated Cost")
            ax.set_title("Cost Estimates by Method")
            for tick in ax.get_xticklabels():
                tick.set_rotation(25)
                tick.set_fontsize(8)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=right)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=6)
