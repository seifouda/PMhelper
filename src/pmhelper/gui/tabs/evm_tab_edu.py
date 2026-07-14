"""
PMhelper Edu — EVM Dashboard Tab.
Sub-tab A: KPI Cards with RAG badges + step-by-step walkthrough.
Sub-tab B: EV S-Curve (Matplotlib).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import json

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.evm_calculations_edu import (
    compute_all_kpis, get_rag, get_kpi_walkthrough,
)
from pmhelper.core.step_generators_edu import evm_steps
from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow

# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame, WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import plotly_scurve, PLOTLY_AVAILABLE as _PLT_AVAIL
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

# Display order of KPI cards (4 columns)
_KPI_CARD_ORDER = [
    "ev", "pv", "ac", "bac",
    "cv", "sv", "cpi", "spi",
    "pc", "ps", "cr", "tcpi_bac",
    "eac1", "eac2", "eac3", "vac",
]

_KPI_LABELS = {
    "ev": "Earned Value (EV)", "pv": "Planned Value (PV)",
    "ac": "Actual Cost (AC)", "bac": "Budget at Completion (BAC)",
    "cv": "Cost Variance (CV)", "sv": "Schedule Variance (SV)",
    "cpi": "Cost Performance Index (CPI)", "spi": "Schedule Perf. Index (SPI)",
    "pc": "Percent Complete (PC)", "ps": "Percent Spent (PS)",
    "cr": "Critical Ratio (CR)", "tcpi_bac": "TCPI (BAC)",
    "eac1": "EAC₁ (Atypical)", "eac2": "EAC₂ (Typical)",
    "eac3": "EAC₃ (Composite)", "vac": "Variance at Completion",
}

# B7.3: KPI phase groups
_KPI_GROUPS = [
    ("Core Values", ["ev", "pv", "ac", "bac"]),
    ("Variance", ["cv", "sv"]),
    ("Performance Indices", ["cpi", "spi", "cr", "tcpi_bac"]),
    ("Forecasts & Completion", ["pc", "ps", "eac1", "eac2", "eac3", "vac"]),
]


class EVMTabEdu:
    """EVM Dashboard with KPI cards and S-Curve chart."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self._mode = "UG"
        self._last_calc_hash = None
        self._kpis = {}
        self._render_mode_var = tk.StringVar(value="matplotlib")

        self.frame = ttk.Frame(parent)

        # B7.1: Shared toolbar above notebook (status + global Refresh)
        _shared_bar = ttk.Frame(self.frame)
        _shared_bar.pack(fill=tk.X, padx=5, pady=(4, 0))
        self._shared_status_var = tk.StringVar(value="No EVM data loaded")
        ttk.Label(
            _shared_bar,
            textvariable=self._shared_status_var,
            foreground="grey",
            font=(
                "TkDefaultFont",
                9,
                "italic")).pack(
            side=tk.LEFT)
        ttk.Button(_shared_bar, text="\u21ba Refresh",
                   command=self._refresh_all).pack(side=tk.RIGHT)

        # Inner notebook for sub-tabs
        self._notebook = ttk.Notebook(self.frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sub-tab A: KPI Cards
        self._kpi_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._kpi_frame, text="KPI Cards")
        self._build_kpi_panel()

        # Sub-tab B: S-Curve
        self._curve_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._curve_frame, text="EV S-Curve")
        self._build_scurve_panel()

    # ================================================================
    #  KPI Cards Panel
    # ================================================================

    def _build_kpi_panel(self):
        # Stale-data warning bar
        self._stale_bar = ttk.Label(
            self._kpi_frame, text="", foreground="orange",
            font=("Arial", 9, "italic"))
        self._stale_bar.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Controls row
        ctrl = ttk.Frame(self._kpi_frame)
        ctrl.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(ctrl, text="Recalculate",
                   command=self._recalculate).pack(side=tk.LEFT, padx=(0, 10))

        self._evm_worked_btn = ttk.Button(
            ctrl, text="📝 Worked Solution",
            command=self._show_evm_worked_solution)
        self._evm_worked_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(ctrl, text="Primary EAC:").pack(side=tk.LEFT)
        self._eac_var = tk.IntVar(value=1)
        for i in (1, 2, 3):
            ttk.Radiobutton(ctrl, text=f"EAC{i}", variable=self._eac_var,
                            value=i).pack(side=tk.LEFT, padx=2)

        ttk.Button(ctrl, text="Export Excel",
                   command=self._export_excel).pack(side=tk.RIGHT, padx=2)

        # B7.2: Student Input panel (UG mode only, hidden by default)
        self._student_input_frame = ttk.LabelFrame(
            self._kpi_frame, text="🎓 Student Input — Enter EV / PV / AC / BAC manually")
        # Will be shown/hidden by set_mode(); pack now so it stays above cards

        si_inner = ttk.Frame(self._student_input_frame)
        si_inner.pack(fill=tk.X, padx=6, pady=4)
        self._si_vars = {}
        for col, key in enumerate(["ev", "pv", "ac", "bac"]):
            ttk.Label(
                si_inner,
                text=_KPI_LABELS[key].split("(")[0].strip() +
                ":").grid(
                row=0,
                column=col *
                2,
                padx=(
                    8,
                    2),
                pady=2,
                sticky="e")
            v = tk.StringVar(value="0")
            self._si_vars[key] = v
            ttk.Entry(si_inner, textvariable=v, width=10).grid(
                row=0, column=col * 2 + 1, padx=(0, 8), pady=2, sticky="w")
        ttk.Button(si_inner, text="▶ Apply",
                   command=self._apply_student_input).grid(
            row=0, column=8, padx=8, pady=2)

        # Pre-register student frame in pack order (hidden by default, shown by
        # set_mode in UG)
        self._student_input_frame.pack(fill=tk.X, padx=5, pady=(0, 4))
        self._student_input_frame.pack_forget()

        # Scrollable card area (B7.3: grouped by phase)
        canvas = tk.Canvas(self._kpi_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self._kpi_frame, orient=tk.VERTICAL,
                                  command=canvas.yview)
        self._kpi_canvas = canvas  # keep ref for set_mode before= ordering
        self._card_container = ttk.Frame(canvas)

        self._card_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._card_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # B7.3: Build cards inside phase-group LabelFrames
        self._cards = {}
        for group_name, kpi_names in _KPI_GROUPS:
            grp_lf = ttk.LabelFrame(
                self._card_container, text=group_name, padding=4)
            grp_lf.pack(fill=tk.X, padx=4, pady=4)
            for col, kpi_name in enumerate(kpi_names):
                card = self._create_card(grp_lf, kpi_name)
                card["frame"].grid(
                    row=0, column=col, padx=3, pady=3, sticky="nsew")
                grp_lf.columnconfigure(col, weight=1)
                self._cards[kpi_name] = card

        # Step-by-step walkthrough panel
        walk_lf = ttk.LabelFrame(
            self._kpi_frame,
            text="Step-by-Step Walkthrough",
            padding=5)
        walk_lf.pack(fill=tk.X, padx=5, pady=(0, 5))

        self._walk_formula = ttk.Label(walk_lf, text="Click a KPI card above",
                                       font=("Consolas", 10))
        self._walk_formula.pack(anchor="w")
        self._walk_sub = ttk.Label(walk_lf, text="", font=("Consolas", 10))
        self._walk_sub.pack(anchor="w")
        self._walk_result = ttk.Label(walk_lf, text="",
                                      font=("Consolas", 10, "bold"))
        self._walk_result.pack(anchor="w")
        self._walk_interp = ttk.Label(walk_lf, text="", foreground="grey",
                                      font=("Arial", 9, "italic"),
                                      wraplength=600)
        self._walk_interp.pack(anchor="w")

    def _create_card(self, parent, kpi_name):
        """Build a single KPI card widget."""
        lf = ttk.LabelFrame(parent, text=_KPI_LABELS.get(kpi_name, kpi_name),
                            padding=5)

        value_label = ttk.Label(lf, text="—", font=("Arial", 16, "bold"))
        value_label.pack(anchor="w")

        badge = tk.Label(lf, text="  ", width=6, bg=_RAG_COLOURS["grey"],
                         fg="white", font=("Arial", 8, "bold"))
        badge.pack(anchor="w", pady=(2, 0))

        interp_label = ttk.Label(lf, text="", foreground="grey",
                                 font=("Arial", 8), wraplength=180)
        interp_label.pack(anchor="w", pady=(2, 0))

        # Click to show walkthrough
        for widget in (lf, value_label, badge, interp_label):
            widget.bind("<Button-1>",
                        lambda e, k=kpi_name: self._show_walkthrough(k))

        return {
            "frame": lf,
            "value_label": value_label,
            "badge": badge,
            "interp_label": interp_label,
        }

    def _recalculate(self):
        """Compute all KPIs and update the display."""
        proj = self.state.evm_project
        if proj is None:
            return

        primary_eac = self._eac_var.get()
        self._kpis = compute_all_kpis(proj, primary_eac)
        bac = self._kpis.get("bac", 0)
        sym = proj.currency_symbol

        for kpi_name, card in self._cards.items():
            val = self._kpis.get(kpi_name)

            # Format value
            if val is None:
                display = "N/A"
            elif kpi_name in ("pc", "ps"):
                display = f"{val:.1f}%"
            elif kpi_name in ("cpi", "spi", "cr", "tcpi_bac"):
                display = f"{val:.3f}"
            else:
                display = f"{sym}{val:,.2f}"

            card["value_label"].config(text=display)

            # RAG badge
            rag_key = kpi_name
            if kpi_name in ("eac1", "eac2", "eac3"):
                rag_key = kpi_name  # get_rag handles eac*
            rag = get_rag(rag_key, val, bac)
            colour = _RAG_COLOURS.get(rag, _RAG_COLOURS["grey"])
            card["badge"].config(bg=colour, text=rag.upper())

            # Short interpretation
            error_msg = self._kpis.get("errors", {}).get(kpi_name, "")
            if error_msg:
                card["interp_label"].config(text=f"⚠ {error_msg}")
            else:
                card["interp_label"].config(text="")

        # Update stale-data hash
        self._last_calc_hash = self._compute_data_hash()
        self._stale_bar.config(text="")

        # Update S-curve
        self._update_scurve()

    def _show_walkthrough(self, kpi_name):
        """Populate the step-by-step panel for the clicked KPI."""
        if not self._kpis:
            return
        proj = self.state.evm_project
        sym = proj.currency_symbol if proj else "$"
        wt = get_kpi_walkthrough(kpi_name, self._kpis, sym)
        self._walk_formula.config(text=wt["formula"])
        self._walk_sub.config(text=wt["substitution"])
        self._walk_result.config(text=wt["result"])
        self._walk_interp.config(text=wt["interpretation"])

    # ================================================================
    #  S-Curve Panel
    # ================================================================

    def _build_scurve_panel(self):
        if not HAS_MATPLOTLIB:
            ttk.Label(self._curve_frame,
                      text="Matplotlib not available — S-Curve disabled.").pack(expand=True)
            return

        # Renderer toggle
        if _PLOTLY_EMBED:
            ctrl = ttk.Frame(self._curve_frame)
            ctrl.pack(fill=tk.X, padx=5, pady=(5, 0))
            render_frame = ttk.LabelFrame(ctrl, text="Renderer", padding="3")
            render_frame.pack(side=tk.LEFT)
            ttk.Radiobutton(
                render_frame,
                text="Classic",
                value="matplotlib",
                variable=self._render_mode_var,
                command=self._switch_renderer).pack(
                side=tk.LEFT,
                padx=4)
            ttk.Radiobutton(
                render_frame,
                text="\U0001f4ca Plotly",
                value="plotly",
                variable=self._render_mode_var,
                command=self._switch_renderer).pack(
                side=tk.LEFT,
                padx=4)

        # Matplotlib chart
        self._mpl_scurve_frame = ttk.Frame(self._curve_frame)
        self._mpl_scurve_frame.pack(fill=tk.BOTH, expand=True)
        self._fig = Figure(figsize=(8, 4.5), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._canvas_widget = FigureCanvasTkAgg(
            self._fig, self._mpl_scurve_frame)
        self._canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Plotly frame (hidden)
        self._plotly_frame = None
        if _PLOTLY_EMBED:
            self._plotly_frame = PlotlyChartFrame(self._curve_frame)

        # Empty-state label (shown when no data)
        self._scurve_empty = ttk.Label(
            self._curve_frame,
            text="No period data — add periods in the Input tab, then click Recalculate.",
            font=("Arial", 10, "italic"))

        # Export buttons
        btn_row = ttk.Frame(self._curve_frame)
        btn_row.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_row, text="Export PNG",
                   command=lambda: self._export_chart("png")).pack(
                       side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row, text="Export PDF",
                   command=lambda: self._export_chart("pdf")).pack(
                       side=tk.LEFT)
        ttk.Button(
            btn_row,
            text="\U0001f50d Open Interactive",
            command=self._open_scurve_interactive).pack(
            side=tk.LEFT,
            padx=6)

    def _open_scurve_interactive(self):
        proj = self.state.evm_project
        if not proj or not proj.periods:
            messagebox.showinfo("Interactive", "No EVM data available.")
            return
        from pmhelper.utils.interactive_charts import open_chart_in_browser
        fig = plotly_scurve(proj.periods)
        open_chart_in_browser(fig, "EV S-Curve")

    def _update_scurve(self):
        if self._render_mode_var.get() == "plotly" and getattr(self, '_plotly_frame', None):
            self._update_plotly_scurve()
            return
        if not HAS_MATPLOTLIB:
            return

        proj = self.state.evm_project
        if proj is None or not proj.periods:
            self._ax.clear()
            self._ax.set_title("No period data")
            self._canvas_widget.draw()
            return

        self._scurve_empty.pack_forget()

        periods = proj.periods
        x_labels = [p.label or f"P{p.index}" for p in periods]
        x = list(range(len(periods)))
        pv_vals = [p.pv_cumulative for p in periods]
        ev_vals = [p.ev_cumulative for p in periods]
        ac_vals = [p.ac_cumulative for p in periods]

        self._ax.clear()
        self._ax.plot(x, pv_vals, 'g--o', label='PV', markersize=5)
        self._ax.plot(x, ev_vals, 'b-o', label='EV', markersize=5)
        self._ax.plot(x, ac_vals, 'r-o', label='AC', markersize=5)

        # B7.5: EAC forecast lines (dashed, from last actual period to
        # projected end)
        if self._kpis:
            bac = self._kpis.get("bac", 0)
            cpi = self._kpis.get("cpi") or 1.0
            spi = self._kpis.get("spi") or 1.0
            last_x = x[-1]
            # Estimate x_completion based on SPI
            remaining_periods = (
                1 - (ev_vals[-1] / bac)) / spi if bac and spi else 0
            x_end = last_x + max(remaining_periods * len(x), 1)
            for eac_key, label_, colour_ in [
                ("eac1", "EAC₁", "#9b59b6"),
                ("eac2", "EAC₂", "#1abc9c"),
            ]:
                eac_val = self._kpis.get(eac_key)
                if eac_val and eac_val > ac_vals[-1]:
                    self._ax.plot(
                        [last_x, x_end], [ac_vals[-1], eac_val],
                        linestyle=":", linewidth=1.5, color=colour_,
                        label=f"{label_} forecast")
                    self._ax.annotate(
                        f"{label_}={proj.currency_symbol}{eac_val:,.0f}",
                        xy=(x_end, eac_val), fontsize=7, color=colour_)

        # Shaded regions
        for i in range(len(x)):
            if ac_vals[i] > ev_vals[i]:
                self._ax.fill_between(
                    [x[i] - 0.3, x[i] + 0.3],
                    [ev_vals[i], ev_vals[i]],
                    [ac_vals[i], ac_vals[i]],
                    alpha=0.15, color='red')
            elif ev_vals[i] > ac_vals[i]:
                self._ax.fill_between(
                    [x[i] - 0.3, x[i] + 0.3],
                    [ac_vals[i], ac_vals[i]],
                    [ev_vals[i], ev_vals[i]],
                    alpha=0.15, color='green')

        sym = proj.currency_symbol
        self._ax.set_title("Earned Value S-Curve", fontsize=12)
        self._ax.set_xlabel("Period")
        self._ax.set_ylabel(f"Cumulative Value ({sym})")
        self._ax.set_xticks(x)
        self._ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)
        self._ax.legend(loc='upper left')
        self._ax.grid(True, alpha=0.3)
        self._fig.tight_layout()
        self._canvas_widget.draw()

    def _export_chart(self, fmt):
        from tkinter import filedialog
        ext = fmt.lower()
        filepath = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            filetypes=[(f"{ext.upper()} files", f"*.{ext}"), ("All files", "*.*")])
        if filepath:
            self._fig.savefig(filepath, format=ext, dpi=150)

    # ================================================================
    #  Stale-data detection
    # ================================================================

    def _compute_data_hash(self) -> str:
        """Hash the current EVM project data for change detection."""
        proj = self.state.evm_project
        if proj is None:
            return ""
        raw = json.dumps(proj.to_dict(), sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()

    # ================================================================
    #  Tab interface
    # ================================================================

    def set_mode(self, mode: str):
        self._mode = mode
        # Hide EAC3 and TCPI cards in UG mode
        pg_only_kpis = ("eac3", "tcpi_bac")
        for kpi_name in pg_only_kpis:
            if kpi_name in self._cards:
                if mode.upper() == "PG":
                    self._cards[kpi_name]["frame"].grid()
                else:
                    self._cards[kpi_name]["frame"].grid_remove()
        # Show worked-solution button only in UG mode
        if hasattr(self, "_evm_worked_btn"):
            if mode.upper() == "UG":
                self._evm_worked_btn.pack(side=tk.LEFT, padx=(0, 10))
            else:
                self._evm_worked_btn.pack_forget()
        # B7.2: show student input panel only in UG mode
        if hasattr(
                self,
                "_student_input_frame") and hasattr(
                self,
                "_kpi_canvas"):
            if mode.upper() == "UG":
                self._student_input_frame.pack(fill=tk.X, padx=5, pady=(0, 4),
                                               before=self._kpi_canvas)
            else:
                self._student_input_frame.pack_forget()

    # ── B7.2: Student input apply ────────────────────────────────

    def _apply_student_input(self):
        """Build a minimal EVM project from manually entered EV/PV/AC/BAC."""
        from pmhelper.core.evm_models_edu import EVMProject, EVMPeriod
        try:
            ev = float(self._si_vars["ev"].get() or 0)
            pv = float(self._si_vars["pv"].get() or 0)
            ac = float(self._si_vars["ac"].get() or 0)
            bac = float(self._si_vars["bac"].get() or 0)
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror(
                "Student Input",
                "All values must be numbers.",
                parent=self.frame)
            return

        proj = self.state.evm_project
        if proj is None:
            proj = EVMProject()
            self.state.evm_project = proj

        # Inject a single synthetic period so KPI calculations work
        synth = EVMPeriod(label="Manual", pv_cumulative=pv,
                          ev_cumulative=ev, ac_cumulative=ac)
        proj.periods = [synth]
        proj.bac = bac
        self._recalculate()

    # ── B7.1: Global refresh ─────────────────────────────────────

    def _refresh_all(self):
        """Refresh status bar, recalculate KPIs, and redraw S-Curve."""
        self._update_shared_status()
        self._recalculate()

    def _update_shared_status(self):
        """Update the shared status label with current project info."""
        proj = self.state.evm_project
        if proj is None:
            self._shared_status_var.set("No EVM data loaded")
            return
        name = getattr(proj, 'name', '') or "Unnamed project"
        n_per = len(proj.periods) if proj.periods else 0
        n_tsk = len(proj.tasks) if proj.tasks else 0
        self._shared_status_var.set(
            f"Project: {name}  |  Tasks: {n_tsk}  |  Periods: {n_per}")

    def _show_evm_worked_solution(self):
        """Open a Worked Solution window for EVM KPIs."""
        if not self._kpis:
            from tkinter import messagebox
            messagebox.showinfo("No data",
                                "Click Recalculate first.",
                                parent=self.frame)
            return
        proj = self.state.evm_project
        sym = proj.currency_symbol if proj else "$"
        steps = evm_steps(self._kpis, sym)
        WorkedSolutionWindow(self.frame, "EVM — Worked Solution", steps)

    def _export_excel(self):
        """Export KPI table to an Excel file."""
        if not self._kpis:
            from tkinter import messagebox
            messagebox.showinfo("No data", "Click Recalculate first.",
                                parent=self.frame)
            return
        try:
            import openpyxl
        except ImportError:
            from tkinter import messagebox
            messagebox.showwarning(
                "Missing dependency",
                "Install openpyxl to export Excel:\n  pip install openpyxl",
                parent=self.frame)
            return

        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            title="Export KPIs to Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not filepath:
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "EVM KPIs"
        ws.append(["KPI", "Value", "RAG Status"])

        proj = self.state.evm_project
        sym = proj.currency_symbol if proj else "$"
        bac = self._kpis.get("bac", 0)

        for kpi_name in _KPI_CARD_ORDER:
            val = self._kpis.get(kpi_name)
            label = _KPI_LABELS.get(kpi_name, kpi_name)
            if val is None:
                display = "N/A"
            elif kpi_name in ("pc", "ps"):
                display = f"{val:.1f}%"
            elif kpi_name in ("cpi", "spi", "cr", "tcpi_bac"):
                display = f"{val:.3f}"
            else:
                display = f"{sym}{val:,.2f}"
            rag = get_rag(kpi_name, val, bac)
            ws.append([label, display, rag.upper()])

        wb.save(filepath)
        from tkinter import messagebox
        messagebox.showinfo("Exported", f"KPIs exported to:\n{filepath}",
                            parent=self.frame)

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB and hasattr(self, "_fig"):
            figs.append(("s_curve", self._fig))
        return figs

    def on_tab_selected(self):
        """Check for data changes and show stale-data warning or auto-recalculate."""
        self._update_shared_status()
        current_hash = self._compute_data_hash()
        if self._last_calc_hash is None:
            # First visit — auto-calculate
            self._recalculate()
        elif current_hash != self._last_calc_hash:
            self._stale_bar.config(
                text="⚠ Input data has changed since last calculation. "
                     "Click Recalculate to update.")

    # ================================================================
    #  Plotly embedded renderer
    # ================================================================

    def _switch_renderer(self):
        mode = self._render_mode_var.get()
        if mode == "plotly" and self._plotly_frame:
            self._mpl_scurve_frame.pack_forget()
            self._plotly_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            if self._plotly_frame:
                self._plotly_frame.pack_forget()
            self._mpl_scurve_frame.pack(fill=tk.BOTH, expand=True)
        self._update_scurve()

    def _update_plotly_scurve(self):
        if not self._plotly_frame:
            return
        proj = self.state.evm_project
        if proj is None or not proj.periods:
            self._plotly_frame.load_html(
                "<html><body style='font-family:sans-serif;padding:40px'>"
                "<h3>No period data</h3></body></html>")
            return
        try:
            fig = plotly_scurve(proj.periods)
            if fig:
                self._plotly_frame.update_chart(fig)
        except Exception as e:
            self._plotly_frame.load_html(
                f"<html><body style='font-family:sans-serif;padding:40px'>"
                f"<h3>Error</h3><pre>{e}</pre></body></html>")
