"""
PMhelper Edu — EVM Dashboard Tab.
Sub-tab A: KPI Cards with RAG badges + step-by-step walkthrough.
Sub-tab B: EV S-Curve (Matplotlib).
"""

import tkinter as tk
from tkinter import ttk
import hashlib
import json

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.evm_calculations_edu import (
    compute_all_kpis, get_rag, get_kpi_walkthrough, RAG_DEFAULTS,
)
from pmhelper.core.step_generators_edu import evm_steps
from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow


# RAG badge colours
_RAG_COLOURS = {
    "green": "#2ecc71",
    "amber": "#f39c12",
    "red":   "#e74c3c",
    "grey":  "#95a5a6",
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


class EVMTabEdu:
    """EVM Dashboard with KPI cards and S-Curve chart."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self._mode = "UG"
        self._last_calc_hash = None
        self._kpis = {}

        self.frame = ttk.Frame(parent)

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

        # Scrollable card grid
        canvas = tk.Canvas(self._kpi_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self._kpi_frame, orient=tk.VERTICAL,
                                   command=canvas.yview)
        self._card_container = ttk.Frame(canvas)

        self._card_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._card_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Build card widgets
        self._cards = {}
        for idx, kpi_name in enumerate(_KPI_CARD_ORDER):
            row, col = divmod(idx, 4)
            card = self._create_card(self._card_container, kpi_name)
            card["frame"].grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            self._cards[kpi_name] = card

        for c in range(4):
            self._card_container.columnconfigure(c, weight=1)

        # Step-by-step walkthrough panel
        walk_lf = ttk.LabelFrame(self._kpi_frame, text="Step-by-Step Walkthrough",
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
                      text="Matplotlib not available — S-Curve disabled.").pack(
                          expand=True)
            return

        self._fig = Figure(figsize=(8, 4.5), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._canvas_widget = FigureCanvasTkAgg(self._fig, self._curve_frame)
        self._canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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

    def _update_scurve(self):
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
        current_hash = self._compute_data_hash()
        if self._last_calc_hash is None:
            # First visit — auto-calculate
            self._recalculate()
        elif current_hash != self._last_calc_hash:
            self._stale_bar.config(
                text="⚠ Input data has changed since last calculation. "
                     "Click Recalculate to update.")
