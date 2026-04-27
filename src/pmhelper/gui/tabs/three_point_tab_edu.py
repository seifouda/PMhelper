"""
PMhelper Edu — Three-Point Estimates Tab (V2 Phase 2).

Full educational calculator for PERT-Beta and Triangular three-point
estimation.  Features:

* **Standalone input grid** — editable rows for Activity ID / Name / O / M / P
* **Load from Project** — pulls PERT activities from the active ``.pmproj``
* **Formula selector** — PERT-Beta ``(O+4M+P)/6`` vs Triangular ``(O+M+P)/3``
* **Results table** — tₑ, σ², σ per activity; project totals in a footer row;
  critical-path activities highlighted in red
* **Line chart** — 4 series (O, M, P, Expected) per activity on the same axes
* **Worked Solution** — pops a :class:`WorkedSolutionWindow` with 5 steps
* **Try It Yourself** — student fills in Expected (tₑ); "Check" validates
  against computed values (tolerance ±0.01)
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

try:
    from scipy.stats import norm
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame, WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import plotly_three_point, PLOTLY_AVAILABLE as _PLT_AVAIL
    _PLOTLY_EMBED = WEBVIEW2_AVAILABLE and _PLT_AVAIL
except ImportError:
    _PLOTLY_EMBED = False


class ThreePointTabEdu:
    """Three-Point Estimates educational tab."""

    # Column config for the input grid
    _INPUT_COLS: List[Tuple[str, str, int]] = [
        ("act_id", "Act ID", 8),
        ("name", "Activity Name", 22),
        ("o", "Optimistic (O)", 13),
        ("m", "Most Likely (M)", 13),
        ("p", "Pessimistic (P)", 13),
    ]

    def __init__(self, parent, state, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self._mode = "UG"
        self._current_result = None
        self._critical_path_ids: List[str] = []
        self._render_mode_var = tk.StringVar(value="matplotlib")

        # Root frame (added to parent notebook by main_window_edu)
        self.frame = ttk.Frame(parent)

        self._build_ui()

    # ════════════════════════════════════════════════════════════════
    #  UI construction
    # ════════════════════════════════════════════════════════════════

    def _build_ui(self):
        # ── Toolbar ─────────────────────────────────────────────
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=6, pady=(5, 2))

        ttk.Button(
            toolbar, text="📂 Load Demo",
            command=self._load_demo,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            toolbar, text="📂 Load from Project",
            command=self._load_from_project,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(toolbar, text="Formula:").pack(side=tk.LEFT, padx=(0, 3))
        self._formula_var = tk.StringVar(value="PERT")
        ttk.Radiobutton(
            toolbar, text="PERT  (O+4M+P)/6",
            variable=self._formula_var, value="PERT",
        ).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Radiobutton(
            toolbar, text="Triangular  (O+M+P)/3",
            variable=self._formula_var, value="Triangular",
        ).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Button(
            toolbar, text="▶ Calculate",
            command=self._calculate,
        ).pack(side=tk.LEFT, padx=(0, 8))

        self._try_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            toolbar, text="🎓 Try It Yourself",
            variable=self._try_var,
            command=self._toggle_practice,
        ).pack(side=tk.RIGHT)

        # ── Scrollable container (replaces outer PanedWindow) ──────
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

        def _on_inner_configure(e):
            self._tiy_canvas.configure(
                scrollregion=self._tiy_canvas.bbox('all'))

        def _on_canvas_configure(e):
            self._tiy_canvas.itemconfig(self._tiy_win, width=e.width)
        self._inner_frame.bind('<Configure>', _on_inner_configure)
        self._tiy_canvas.bind('<Configure>', _on_canvas_configure)
        self._tiy_canvas.bind_all('<MouseWheel>', lambda e: self._tiy_canvas.yview_scroll(
            int(-1 * (e.delta / 120)), 'units'))

        # _content_frame inside scrollable inner
        self._content_frame = ttk.Frame(self._inner_frame)
        self._content_frame.pack(fill=tk.BOTH, expand=True)

        # ── Main paned area (B4): vertical outer split ────────────────
        self._paned = ttk.PanedWindow(self._content_frame, orient=tk.VERTICAL)
        self._paned.pack(fill=tk.BOTH, expand=True)

        # Top pane: horizontal split — input (left) | results (right)
        _top_row = ttk.Frame(self._paned)
        self._paned.add(_top_row, weight=1)
        _top_horiz = ttk.PanedWindow(_top_row, orient=tk.HORIZONTAL)
        _top_horiz.pack(fill=tk.BOTH, expand=True)

        input_lf = ttk.LabelFrame(
            _top_horiz, text="Input Activities — O / M / P")
        _top_horiz.add(input_lf, weight=2)
        self._build_input_panel(input_lf)

        results_lf = ttk.LabelFrame(_top_horiz, text="Results")
        _top_horiz.add(results_lf, weight=1)
        self._build_results_table(results_lf)

        # Bottom pane: full-width line chart (B4)
        chart_lf = ttk.LabelFrame(self._paned, text="Line Chart")
        self._paned.add(chart_lf, weight=2)
        self._build_chart(chart_lf)

        # ── Educational bar ──────────────────────────────────────
        edu_bar = ttk.Frame(self._content_frame)
        edu_bar.pack(fill=tk.X, pady=(2, 2))
        ttk.Button(
            edu_bar, text="📖 Show Worked Solution",
            command=self._show_worked_solution,
        ).pack(side=tk.LEFT)

        # ── Z-Score Table section (collapsible) ─────────────────
        self._build_ztable_section()

        # ── Cost Estimation section (collapsible) ───────────────
        self._build_cost_estimation_section()

        # ── Practice frame (hidden — shown below content when TIY enabled) ──
        self._practice_frame = ttk.LabelFrame(
            self._inner_frame, text="🎓 Try It Yourself — Enter Your tₑ")
        self._build_practice_panel()

    # ── Input panel ─────────────────────────────────────────────────

    def _build_input_panel(self, parent: ttk.Frame):
        # Column headers
        hdr = ttk.Frame(parent)
        hdr.pack(fill=tk.X, padx=4, pady=(4, 0))
        for _, label, width in self._INPUT_COLS:
            ttk.Label(hdr, text=label, width=width, anchor=tk.CENTER,
                      relief="groove").pack(side=tk.LEFT, padx=1)
        ttk.Label(
            hdr, text="", width=3).pack(
            side=tk.LEFT)  # spacer for remove btn

        # Scrollable rows area
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 0))

        self._input_canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        vsb = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL,
                            command=self._input_canvas.yview)
        self._input_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._input_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._rows_frame = ttk.Frame(self._input_canvas)
        self._rows_win = self._input_canvas.create_window(
            (0, 0), window=self._rows_frame, anchor=tk.NW)

        self._rows_frame.bind("<Configure>", self._on_rows_resize)
        self._input_canvas.bind("<Configure>", self._on_canvas_resize)

        # Storage: list of (id_var, name_var, o_var, m_var, p_var, row_frame)
        self._input_rows: List[Tuple] = []

        # Seed with 5 blank rows
        for _ in range(5):
            self._add_input_row()

        # Buttons bar
        btn_bar = ttk.Frame(parent)
        btn_bar.pack(fill=tk.X, padx=4, pady=(2, 4))
        ttk.Button(btn_bar, text="+ Add Row",
                   command=self._add_input_row).pack(side=tk.LEFT)
        ttk.Button(btn_bar, text="Clear All",
                   command=self._clear_input_rows).pack(side=tk.LEFT, padx=4)

    def _on_rows_resize(self, event):
        self._input_canvas.configure(
            scrollregion=self._input_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self._input_canvas.itemconfig(self._rows_win, width=event.width)

    def _add_input_row(
            self,
            id_val="",
            name_val="",
            o_val="",
            m_val="",
            p_val=""):
        row_frame = ttk.Frame(self._rows_frame)
        row_frame.pack(fill=tk.X, pady=1)

        vars_: List[tk.StringVar] = []
        init_vals = [str(id_val), str(name_val),
                     str(o_val), str(m_val), str(p_val)]
        widths = [col[2] for col in self._INPUT_COLS]
        for val, w in zip(init_vals, widths):
            v = tk.StringVar(value=val)
            ttk.Entry(row_frame, textvariable=v, width=w).pack(
                side=tk.LEFT, padx=1)
            vars_.append(v)

        row_tuple = tuple(vars_) + (row_frame,)
        self._input_rows.append(row_tuple)

        def _remove(rf=row_frame, rt=row_tuple):
            if rt in self._input_rows:
                self._input_rows.remove(rt)
            rf.destroy()
            self._on_rows_resize(None)

        ttk.Button(row_frame, text="−", width=2,
                   command=_remove).pack(side=tk.LEFT, padx=1)

    def _clear_input_rows(self):
        for w in self._rows_frame.winfo_children():
            w.destroy()
        self._input_rows.clear()
        for _ in range(5):
            self._add_input_row()

    def _get_input_data(self) -> List[dict]:
        """Parse all valid input rows into activity dicts."""
        activities = []
        for row in self._input_rows:
            id_val = row[0].get().strip()
            if not id_val:
                continue
            try:
                o = float(row[2].get())
                m = float(row[3].get())
                p = float(row[4].get())
            except ValueError:
                continue
            activities.append({
                "id": id_val,
                "name": row[1].get().strip() or id_val,
                "optimistic": o,
                "most_likely": m,
                "pessimistic": p,
            })
        return activities

    # ── Results table ─────────────────────────────────────────────────

    def _build_results_table(self, parent: ttk.Frame):
        cols = ("id", "name", "o", "m", "p", "te", "var", "sd")
        headings = {
            "id": "ID", "name": "Name",
            "o": "O", "m": "M", "p": "P",
            "te": "Expected (tₑ)", "var": "Variance (σ²)", "sd": "Std Dev (σ)",
        }
        widths = {"id": 50, "name": 120, "o": 45, "m": 45, "p": 45,
                  "te": 100, "var": 100, "sd": 80}

        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(parent, orient=tk.HORIZONTAL)
        self._results_tree = ttk.Treeview(
            parent, columns=cols, show="headings",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self._results_tree.yview)
        hsb.config(command=self._results_tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._results_tree.pack(fill=tk.BOTH, expand=True)

        for c in cols:
            self._results_tree.heading(c, text=headings[c])
            self._results_tree.column(c, width=widths[c], anchor=tk.CENTER,
                                      minwidth=40)

        # Tag for critical path (light red background)
        self._results_tree.tag_configure("critical", background="#fee2e2",
                                         foreground="#b91c1c")
        enhance_treeview(self._results_tree)

    def _build_chart(self, parent: ttk.Frame):
        if not HAS_MATPLOTLIB:
            ttk.Label(
                parent,
                text="matplotlib not available — install it for chart view",
                foreground="grey").pack(
                expand=True)
            self._fig = None
            self._ax = None
            self._chart_canvas = None
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

        self._mpl_chart_frame = ttk.Frame(parent)
        self._mpl_chart_frame.pack(fill=tk.BOTH, expand=True)
        self._fig = Figure(figsize=(5, 3), dpi=90)
        self._ax = self._fig.add_subplot(111)
        self._chart_canvas = FigureCanvasTkAgg(
            self._fig, master=self._mpl_chart_frame)
        self._chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._ax.set_title("Three-Point Estimates")
        self._ax.set_xlabel("Activity")
        self._ax.set_ylabel("Duration")
        self._fig.tight_layout()
        self._chart_canvas.draw()

        # Plotly frame (hidden)
        self._plotly_frame = None
        if _PLOTLY_EMBED:
            self._plotly_frame = PlotlyChartFrame(parent)

    # ── Practice panel ────────────────────────────────────────────────

    def _build_practice_panel(self):
        inner = ttk.Frame(self._practice_frame)
        inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        ttk.Label(
            inner,
            text="Calculate Expected (tₑ) for each activity using the selected formula, "
            "enter your answers below, then click 'Check'.",
            foreground="navy",
            wraplength=700,
        ).pack(
            anchor=tk.W,
            pady=(
                0,
                4))

        # Formula reminder
        self._formula_hint = ttk.Label(inner, text="", foreground="grey",
                                       font=("TkDefaultFont", 9, "italic"))
        self._formula_hint.pack(anchor=tk.W, pady=(0, 6))

        # Activity rows: {activity_id: StringVar}
        self._answer_vars: dict = {}
        self._answer_frame = ttk.Frame(inner)
        self._answer_frame.pack(fill=tk.BOTH, expand=True)

        # Feedback text
        self._prac_feedback = tk.StringVar(value="")
        ttk.Label(inner, textvariable=self._prac_feedback,
                  foreground="teal").pack(anchor=tk.W, pady=(6, 0))

        # Check buttons
        btn_row = ttk.Frame(inner)
        btn_row.pack(anchor=tk.W, pady=(4, 0))
        ttk.Button(btn_row, text="✓ Check My Answers",
                   command=self._check_answers).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Show All Answers",
                   command=self._reveal_all).pack(side=tk.LEFT)

        # Correct answers cache: {activity_id: float}
        self._correct_answers: dict = {}

    def _populate_practice(self, result):
        """Build one label+entry+feedback row per activity."""
        # Clear previous
        for w in self._answer_frame.winfo_children():
            w.destroy()
        self._answer_vars.clear()
        self._correct_answers.clear()

        # Formula reminder
        if result.formula == "PERT":
            self._formula_hint.config(text="Formula:  tₑ = (O + 4M + P) / 6")
        else:
            self._formula_hint.config(text="Formula:  tₑ = (O + M + P) / 3")

        # Header row
        hdr = ttk.Frame(self._answer_frame)
        hdr.pack(fill=tk.X)
        for txt, w in [("ID", 8), ("Name", 22), ("O", 7), ("M", 7), ("P", 7),
                       ("Your tₑ", 10), ("Status", 18)]:
            ttk.Label(hdr, text=txt, width=w, anchor=tk.CENTER,
                      relief="groove").pack(side=tk.LEFT, padx=1)

        for act in result.activities:
            row = ttk.Frame(self._answer_frame)
            row.pack(fill=tk.X, pady=1)

            for txt, w in [
                (act.activity_id, 8),
                (act.name, 22),
                (f"{act.optimistic:.2f}", 7),
                (f"{act.most_likely:.2f}", 7),
                (f"{act.pessimistic:.2f}", 7),
            ]:
                ttk.Label(row, text=txt, width=w, anchor=tk.CENTER).pack(
                    side=tk.LEFT, padx=1)

            ans_var = tk.StringVar()
            self._answer_vars[act.activity_id] = ans_var
            ttk.Entry(row, textvariable=ans_var, width=10).pack(
                side=tk.LEFT, padx=1)

            status_var = tk.StringVar()
            ttk.Label(row, textvariable=status_var, width=18,
                      anchor=tk.W).pack(side=tk.LEFT, padx=1)
            ans_var._status_var = status_var  # stash reference

            self._correct_answers[act.activity_id] = act.expected

        self._prac_feedback.set("")

    def _check_answers(self):
        """Validate all student answers against computed tₑ."""
        if not self._correct_answers:
            messagebox.showinfo("Check", "Run Calculate first.")
            return

        n_correct = 0
        n_total = len(self._correct_answers)
        for aid, var in self._answer_vars.items():
            correct = self._correct_answers[aid]
            status_var: tk.StringVar = var._status_var
            try:
                student = float(var.get())
            except ValueError:
                status_var.set("⚠ Not a number")
                continue

            if abs(student - correct) <= 0.01:
                status_var.set("✓ Correct")
                n_correct += 1
            else:
                status_var.set(f"✗  Answer: {correct:.4f}")

        self._prac_feedback.set(
            f"{n_correct}/{n_total} correct — well done! 🎉"
            if n_correct == n_total
            else f"{n_correct}/{n_total} correct — keep trying!"
        )

    def _reveal_all(self):
        """Reveal all correct answers."""
        for aid, var in self._answer_vars.items():
            correct = self._correct_answers.get(aid)
            if correct is None:
                continue
            var.set(f"{correct:.4f}")
            var._status_var.set("✓ Revealed")
        self._prac_feedback.set("All answers revealed.")

    # ════════════════════════════════════════════════════════════════
    #  Actions: Load, Calculate, Worked Solution
    # ════════════════════════════════════════════════════════════════

    def _load_demo(self):
        """Load demo data from three_point_demo.json."""
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "data",
            "demos",
            "v2",
            "three_point_demo.json")
        demo_path = os.path.normpath(demo_path)

        if not os.path.exists(demo_path):
            here = os.path.dirname(os.path.abspath(__file__))
            for _ in range(6):
                candidate = os.path.join(
                    here, "data", "demos", "v2", "three_point_demo.json")
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

        data = demo.get("data", {})
        activities = data.get("activities", [])
        if not activities:
            messagebox.showinfo("Load Demo", "No activities in demo file.")
            return

        # Set formula from demo
        formula = data.get("formula", "PERT")
        self._formula_var.set(formula)

        # Set critical path IDs
        self._critical_path_ids = data.get("critical_path_ids", [])

        # Populate input grid
        for w in self._rows_frame.winfo_children():
            w.destroy()
        self._input_rows.clear()
        for act in activities:
            self._add_input_row(
                act.get("id", ""),
                act.get("name", ""),
                act.get("optimistic", 0),
                act.get("most_likely", 0),
                act.get("pessimistic", 0))
        self._on_rows_resize(None)

        messagebox.showinfo(
            "Load Demo",
            f"Loaded {len(activities)} demo activities.\n"
            "Click ▶ Calculate to see results.")

    def _load_from_project(self):
        """Pull PERT activities from the active project."""
        if self.main_window is None:
            messagebox.showinfo("Load from Project",
                                "No project window connected.")
            return

        activities = []
        if hasattr(self.main_window, "_input_tab_edu"):
            raw = self.main_window._input_tab_edu.get_activities_data()
            for act in raw:
                try:
                    o = float(act.get("optimistic", ""))
                    m = float(act.get("most_likely", ""))
                    p = float(act.get("pessimistic", ""))
                except (TypeError, ValueError):
                    continue
                activities.append({
                    "id": str(act.get("id", "")),
                    "name": (act.get("activity") or act.get("name")
                             or act.get("id", "")),
                    "optimistic": o,
                    "most_likely": m,
                    "pessimistic": p,
                })

        if not activities:
            messagebox.showinfo(
                "Load from Project", "No PERT activities found.\n\n"
                "Switch the Input Activities tab to PERT / probabilistic mode, "
                "enter Optimistic, Most Likely and Pessimistic values, then try again.")
            return

        # Grab critical path IDs from last analysis
        self._critical_path_ids = []
        if hasattr(
                self.main_window,
                "results_data") and self.main_window.results_data:
            cp = self.main_window.results_data.get(
                "critical_activities", set())
            self._critical_path_ids = [
                str(a) for a in cp if a not in ("START", "END")]

        # Populate input grid
        for w in self._rows_frame.winfo_children():
            w.destroy()
        self._input_rows.clear()
        for act in activities:
            self._add_input_row(
                act["id"], act["name"],
                act["optimistic"], act["most_likely"], act["pessimistic"])
        self._on_rows_resize(None)

        messagebox.showinfo(
            "Load from Project",
            f"Loaded {len(activities)} PERT activities from project.")

    def _calculate(self):
        """Run the computation and refresh results + chart."""
        from pmhelper.core.three_point_engine import ThreePointEngine

        activities = self._get_input_data()
        if not activities:
            messagebox.showwarning(
                "Calculate",
                "No valid activities to calculate.\n"
                "Please fill in Activity ID and numeric O / M / P values.")
            return

        formula = self._formula_var.get()
        result = ThreePointEngine.calculate(
            activities,
            formula=formula,
            critical_path_ids=self._critical_path_ids or None,
        )
        self._current_result = result

        self._update_results_table(result)
        if HAS_MATPLOTLIB and self._chart_canvas is not None:
            self._update_chart(result)
        if self._try_var.get():
            self._populate_practice(result)
        self._zt_update_from_result()

    # ────────────────────────────────────────────────────────────────
    #  Z-Score Table expandable section
    # ────────────────────────────────────────────────────────────────

    def _build_ztable_section(self):
        """Add a collapsible Z-table section below the output panel."""

        self._zt_expanded = tk.BooleanVar(value=False)
        self._zt_outer = ttk.Frame(self._content_frame)
        self._zt_outer.pack(fill=tk.X, pady=(0, 2))

        # Toggle header
        hdr = ttk.Frame(self._zt_outer)
        hdr.pack(fill=tk.X)
        self._zt_arrow = ttk.Label(hdr, text="▶", width=2)
        self._zt_arrow.pack(side=tk.LEFT)
        lbl = ttk.Label(hdr, text="Z-Score Table Lookup",
                        font=("TkDefaultFont", 9, "bold"), cursor="hand2")
        lbl.pack(side=tk.LEFT, padx=4)
        for w in (self._zt_arrow, lbl, hdr):
            w.bind("<Button-1>", lambda e: self._zt_toggle())

        # Content (hidden initially)
        self._zt_content = ttk.Frame(self._zt_outer)

        # Target duration + compute Z row
        calc_row = ttk.Frame(self._zt_content)
        calc_row.pack(fill=tk.X, padx=4, pady=3)
        ttk.Label(calc_row, text="Target Duration:").pack(side=tk.LEFT)
        self._zt_target_var = tk.StringVar(value="")
        ttk.Entry(calc_row, textvariable=self._zt_target_var, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(calc_row, text="Compute Z & Lookup",
                   command=self._zt_compute).pack(side=tk.LEFT, padx=2)
        self._zt_result_var = tk.StringVar(value="")
        ttk.Label(calc_row, textvariable=self._zt_result_var,
                  foreground="#27ae60",
                  font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=6)

        # Formula line
        self._zt_formula_var = tk.StringVar(value="")
        ttk.Label(self._zt_content, textvariable=self._zt_formula_var,
                  font=("Consolas", 9), foreground="#7f8c8d").pack(
                      fill=tk.X, padx=4, pady=(0, 2))

        # Z-table widget
        self._zt_table = None
        self._zt_widget = None
        csv_path = self._zt_find_csv()
        if csv_path:
            try:
                from pmhelper.core.ztable_loader import load_ztable
                self._zt_table = load_ztable(csv_path)
                from pmhelper.gui.widgets.ztable_widget import ZScoreTableWidget
                widget_frame = ttk.Frame(self._zt_content, height=200)
                widget_frame.pack(fill=tk.BOTH, padx=4, pady=2)
                widget_frame.pack_propagate(False)
                self._zt_widget = ZScoreTableWidget(
                    widget_frame, self._zt_table)
                self._zt_widget.pack(fill=tk.BOTH, expand=True)
            except Exception:
                pass

    def _zt_find_csv(self) -> str | None:
        import os
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        for _ in range(5):
            cand = os.path.join(pkg_dir, "ztable.csv")
            if os.path.isfile(cand):
                return cand
            pkg_dir = os.path.dirname(pkg_dir)
        cwd = os.path.join(os.getcwd(), "ztable.csv")
        return cwd if os.path.isfile(cwd) else None

    def _zt_toggle(self):
        if self._zt_expanded.get():
            self._zt_content.pack_forget()
            self._zt_arrow.configure(text="▶")
            self._zt_expanded.set(False)
        else:
            self._zt_content.pack(fill=tk.BOTH, padx=0, pady=2)
            self._zt_arrow.configure(text="▼")
            self._zt_expanded.set(True)

    def _zt_compute(self):
        """Compute Z from target duration and project totals, then look up."""
        if self._zt_table is None or self._current_result is None:
            self._zt_result_var.set(
                "Calculate first" if self._current_result is None else "Z-table not loaded")
            return
        raw = self._zt_target_var.get().strip()
        try:
            target = float(raw)
        except ValueError:
            self._zt_result_var.set("Enter a number")
            return
        exp = self._current_result.project_expected
        std = self._current_result.project_std_dev
        if std <= 0:
            self._zt_result_var.set("σ = 0, cannot compute Z")
            return
        z = (target - exp) / std
        from pmhelper.core.ztable_loader import lookup_forward
        result = lookup_forward(self._zt_table, z)
        if result is None:
            self._zt_result_var.set(
                f"Z = {z:.4f} — outside table range")
            self._zt_formula_var.set(
                f"Z = ({target:.2f} − {exp:.4f}) / {std:.4f} = {z:.4f}")
            return
        self._zt_result_var.set(
            f"Z = {z:.4f}  →  P(T≤{target:.2f}) = {result.probability:.4f}")
        self._zt_formula_var.set(
            f"Z = ({target:.2f} − {exp:.4f}) / {std:.4f} = {z:.4f}")
        if self._zt_widget:
            self._zt_widget.highlight_forward(result)

    def _zt_update_from_result(self):
        """Auto-expand and update Z-section when Calculate runs."""
        if self._zt_table is None or self._current_result is None:
            return
        raw = self._zt_target_var.get().strip()
        if raw:
            self._zt_compute()

    def _update_results_table(self, result):
        """Refresh the results Treeview."""
        self._results_tree.delete(*self._results_tree.get_children())

        for act in result.activities:
            tag = ("critical",) if act.is_critical else ()
            self._results_tree.insert("", tk.END, tags=tag, values=(
                act.activity_id,
                act.name,
                f"{act.optimistic:.2f}",
                f"{act.most_likely:.2f}",
                f"{act.pessimistic:.2f}",
                f"{act.expected:.4f}",
                f"{act.variance:.4f}",
                f"{act.std_dev:.4f}",
            ))

        # Footer row: project totals
        self._results_tree.insert("", tk.END, tags=("critical",), values=(
            "TOTAL", "Project (Critical Path)",
            "", "", "",
            f"{result.project_expected:.4f}",
            f"{result.project_variance:.4f}",
            f"{result.project_std_dev:.4f}",
        ))

    def _update_chart(self, result):
        """Redraw the four-series line chart."""
        if self._render_mode_var.get() == "plotly" and getattr(self, '_plotly_frame', None):
            self._update_plotly_chart(result)
            return
        self._ax.clear()

        acts = result.activities
        if not acts:
            self._chart_canvas.draw()
            return

        labels = [a.activity_id for a in acts]
        x = list(range(len(labels)))
        o_vals = [a.optimistic for a in acts]
        m_vals = [a.most_likely for a in acts]
        p_vals = [a.pessimistic for a in acts]
        te_vals = [a.expected for a in acts]

        self._ax.plot(
            x,
            o_vals,
            "b--o",
            label="Optimistic (O)",
            alpha=0.75,
            markersize=5)
        self._ax.plot(
            x,
            m_vals,
            "g-o",
            label="Most Likely (M)",
            alpha=0.75,
            markersize=5)
        self._ax.plot(
            x,
            p_vals,
            "r--o",
            label="Pessimistic (P)",
            alpha=0.75,
            markersize=5)
        self._ax.plot(
            x,
            te_vals,
            "k-s",
            label="Expected (tₑ)",
            linewidth=2,
            markersize=6)

        # Shade critical path columns
        for i, act in enumerate(acts):
            if act.is_critical:
                self._ax.axvspan(i - 0.35, i + 0.35, alpha=0.08, color="red")

        self._ax.set_xticks(x)
        self._ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        formula_label = result.formula
        self._ax.set_title(
            f"Three-Point Estimates — {formula_label}",
            fontsize=10)
        self._ax.set_xlabel("Activity", fontsize=9)
        self._ax.set_ylabel("Duration", fontsize=9)
        self._ax.legend(loc="upper left", fontsize=7)
        self._ax.grid(True, alpha=0.3, linestyle="--")
        self._fig.tight_layout()
        self._chart_canvas.draw()

    def _show_worked_solution(self):
        """Open the step-by-step worked solution pop-up."""
        if self._current_result is None:
            messagebox.showinfo(
                "Worked Solution",
                "Please click ▶ Calculate first.")
            return

        from pmhelper.core.three_point_step_generator import three_point_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow

        steps = three_point_steps(self._current_result)
        WorkedSolutionWindow(
            self.frame,
            "Three-Point Estimates — Worked Solution",
            steps,
        )

    # ── Try It Yourself toggle ────────────────────────────────────────

    def _toggle_practice(self):
        if self._try_var.get():
            self._practice_frame.pack(fill=tk.X, padx=4, pady=4)
            if self._current_result is not None:
                self._populate_practice(self._current_result)
            # Scroll down so TIY panel is visible
            self._inner_frame.update_idletasks()
            self._tiy_canvas.yview_moveto(1.0)
        else:
            self._practice_frame.pack_forget()

    # ── Public interface (called by main_window_edu) ────────────────

    # ════════════════════════════════════════════════════════════════
    #  Cost Estimation Based on Probability
    # ════════════════════════════════════════════════════════════════

    def _build_cost_estimation_section(self):
        """Collapsible cost estimation panel using PERT probability data."""
        self._ce_expanded = tk.BooleanVar(value=False)
        self._ce_outer = ttk.Frame(self._content_frame)
        self._ce_outer.pack(fill=tk.X, pady=(0, 2))

        # Toggle header
        hdr = ttk.Frame(self._ce_outer)
        hdr.pack(fill=tk.X)
        self._ce_arrow = ttk.Label(hdr, text="▶", width=2)
        self._ce_arrow.pack(side=tk.LEFT)
        lbl = ttk.Label(hdr, text="💰 Cost Estimation Based on Probability",
                        font=("TkDefaultFont", 9, "bold"), cursor="hand2")
        lbl.pack(side=tk.LEFT, padx=4)
        for w in (self._ce_arrow, lbl, hdr):
            w.bind("<Button-1>", lambda e: self._ce_toggle())

        # Content (hidden initially)
        self._ce_content = ttk.Frame(self._ce_outer)

        # Input row
        input_row = ttk.Frame(self._ce_content)
        input_row.pack(fill=tk.X, padx=4, pady=3)

        ttk.Label(input_row, text="Daily Cost Rate:").pack(side=tk.LEFT)
        self._ce_rate_var = tk.StringVar(value="1000")
        ttk.Entry(input_row, textvariable=self._ce_rate_var, width=10).pack(
            side=tk.LEFT, padx=(4, 12))

        ttk.Label(input_row, text="Target Duration:").pack(side=tk.LEFT)
        self._ce_target_var = tk.StringVar(value="")
        ttk.Entry(input_row, textvariable=self._ce_target_var, width=8).pack(
            side=tk.LEFT, padx=(4, 12))

        ttk.Button(input_row, text="▶ Compute Costs",
                   command=self._ce_compute).pack(side=tk.LEFT, padx=2)

        # Summary result
        self._ce_summary_var = tk.StringVar(value="")
        ttk.Label(self._ce_content, textvariable=self._ce_summary_var,
                  font=("Consolas", 9), foreground="#2c3e50").pack(
                      fill=tk.X, padx=4, pady=(2, 0))

        # Results table: probability levels vs cost
        table_frame = ttk.Frame(self._ce_content)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        cols = ("prob", "duration", "extra_days", "contingency", "total_cost")
        self._ce_tree = ttk.Treeview(table_frame, columns=cols,
                                     show="headings", height=8)
        for cid, heading, w in [
            ("prob", "Probability", 90),
            ("duration", "Duration", 90),
            ("extra_days", "Extra Days", 90),
            ("contingency", "Contingency", 110),
            ("total_cost", "Total Cost", 120),
        ]:
            self._ce_tree.heading(cid, text=heading)
            self._ce_tree.column(cid, width=w, anchor=tk.CENTER)
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                            command=self._ce_tree.yview)
        self._ce_tree.configure(yscrollcommand=vsb.set)
        self._ce_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        enhance_treeview(self._ce_tree)

        # Chart placeholder
        self._ce_chart_frame = ttk.Frame(self._ce_content, height=200)
        self._ce_chart_frame.pack(fill=tk.BOTH, padx=4, pady=(0, 4))
        self._ce_chart_frame.pack_propagate(False)

    def _ce_toggle(self):
        if self._ce_expanded.get():
            self._ce_content.pack_forget()
            self._ce_arrow.configure(text="▶")
            self._ce_expanded.set(False)
        else:
            self._ce_content.pack(fill=tk.BOTH, padx=0, pady=2)
            self._ce_arrow.configure(text="▼")
            self._ce_expanded.set(True)

    def _ce_compute(self):
        """Compute cost estimates at various probability levels."""
        if not HAS_SCIPY:
            messagebox.showwarning(
                "Cost Estimation",
                "scipy is required for probability calculations.")
            return
        result = self._current_result
        if result is None:
            messagebox.showwarning("Cost Estimation",
                                   "Please run Calculate first.")
            return

        try:
            daily_rate = float(self._ce_rate_var.get())
        except ValueError:
            messagebox.showwarning("Cost Estimation",
                                   "Enter a valid Daily Cost Rate.")
            return

        # Project expected duration and std dev from PERT result
        project_te = result.project_expected
        project_var = result.project_variance
        project_sd = result.project_std_dev if result.project_std_dev > 0 else (
            project_var ** 0.5 if project_var > 0 else 0)

        if project_te <= 0 or project_sd <= 0:
            messagebox.showwarning(
                "Cost Estimation",
                "Need valid project expected duration and variance.\n"
                "Ensure critical path is identified.")
            return

        # Target duration probability
        target_str = self._ce_target_var.get().strip()
        target_info = ""
        if target_str:
            try:
                target_dur = float(target_str)
                z = (target_dur - project_te) / project_sd
                prob = norm.cdf(z)
                extra = max(0, target_dur - project_te)
                cost = extra * daily_rate
                target_info = (
                    f"Target={
                        target_dur:.1f}  |  Z={
                        z:.3f}  |  " f"P(T≤{
                        target_dur:.0f})={
                        prob:.2%}  |  " f"Extra days={
                        extra:.1f}  |  Contingency={
                            daily_rate *
                        extra:,.2f}")
            except ValueError:
                pass

        base_cost = project_te * daily_rate
        summary = f"Expected Duration={
            project_te:.2f}  |  σ={
            project_sd:.2f}  |  Base Cost={
            base_cost:,.2f}"
        if target_info:
            summary += f"\n{target_info}"
        self._ce_summary_var.set(summary)

        # Populate table with probability levels
        self._ce_tree.delete(*self._ce_tree.get_children())
        prob_levels = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99]
        rows = []
        for p in prob_levels:
            z = norm.ppf(p)
            dur = project_te + z * project_sd
            extra = max(0, dur - project_te)
            contingency = extra * daily_rate
            total = base_cost + contingency
            rows.append((p, dur, extra, contingency, total))
            self._ce_tree.insert("", tk.END, values=(
                f"{p:.0%}", f"{dur:.2f}", f"{extra:.2f}",
                f"{contingency:,.2f}", f"{total:,.2f}",
            ))

        # Draw cost vs probability chart
        if HAS_MATPLOTLIB:
            self._ce_draw_chart(
                rows,
                base_cost,
                daily_rate,
                project_te,
                project_sd)

    def _ce_draw_chart(
            self,
            rows,
            base_cost,
            daily_rate,
            project_te,
            project_sd):
        for w in self._ce_chart_frame.winfo_children():
            w.destroy()
        fig = Figure(figsize=(5, 2), dpi=90)
        ax = fig.add_subplot(111)
        probs = [r[0] * 100 for r in rows]
        totals = [r[4] for r in rows]
        contingencies = [r[3] for r in rows]

        ax.bar(probs, [base_cost] * len(probs), width=4,
               color="#93c5fd", label="Base Cost")
        ax.bar(probs, contingencies, width=4, bottom=[base_cost] * len(probs),
               color="#f97316", label="Contingency")
        ax.set_xlabel("Probability (%)", fontsize=8)
        ax.set_ylabel("Cost", fontsize=8)
        ax.set_title("Total Cost at Confidence Levels", fontsize=9)
        ax.legend(fontsize=7, loc="upper left")
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, self._ce_chart_frame)
        c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        c.draw()

    def set_mode(self, mode: str):
        self._mode = mode.upper()

    def on_tab_selected(self):
        """Called when this tab gains focus — no-op unless auto-refresh needed."""

    def get_figures(self) -> list:
        """Return matplotlib figures for chart export."""
        if self._fig is not None:
            return [self._fig]
        return []

    # ── Plotly embedded renderer ──────────────────────────────────────

    def _switch_renderer(self):
        mode = self._render_mode_var.get()
        if mode == "plotly" and getattr(self, '_plotly_frame', None):
            self._mpl_chart_frame.pack_forget()
            self._plotly_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            if getattr(self, '_plotly_frame', None):
                self._plotly_frame.pack_forget()
            self._mpl_chart_frame.pack(fill=tk.BOTH, expand=True)
        if self._current_result:
            self._update_chart(self._current_result)

    def _update_plotly_chart(self, result):
        if not self._plotly_frame:
            return
        try:
            fig = plotly_three_point(result)
            if fig:
                self._plotly_frame.update_chart(fig)
        except Exception as e:
            self._plotly_frame.load_html(
                f"<html><body style='font-family:sans-serif;padding:40px'>"
                f"<h3>Error</h3><pre>{e}</pre></body></html>")
