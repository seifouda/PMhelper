"""
PMhelper Edu — Dashboard Tab.
Project health summary: KPI strip, mini S-curve, risk summary, MC summary (PG).
"""

import tkinter as tk
from tkinter import ttk

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.evm_calculations_edu import compute_all_kpis, get_rag

# RAG badge colours
_RAG_COLOURS = {
    "green": "#2ecc71",
    "amber": "#f39c12",
    "red":   "#e74c3c",
    "grey":  "#95a5a6",
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
    """Project health summary dashboard."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self._mode = "UG"
        self.frame = ttk.Frame(parent)

        self._build_ui()

    # ================================================================
    #  UI construction
    # ================================================================

    def _build_ui(self):
        # Title
        title_lbl = ttk.Label(
            self.frame, text="Project Health Dashboard",
            font=("Arial", 14, "bold"))
        title_lbl.pack(pady=(10, 5))

        # Refresh button
        ttk.Button(self.frame, text="Refresh Dashboard",
                   command=self._refresh).pack(pady=(0, 5))

        # ---- KPI Strip ----
        kpi_lf = ttk.LabelFrame(self.frame, text="Key Performance Indicators",
                                 padding=5)
        kpi_lf.pack(fill=tk.X, padx=10, pady=5)

        self._kpi_cards = {}
        for idx, (key, label) in enumerate(_DASHBOARD_KPIS):
            card_frame = ttk.Frame(kpi_lf, relief="groove", borderwidth=1)
            card_frame.grid(row=0, column=idx, padx=4, pady=4, sticky="nsew")

            ttk.Label(card_frame, text=label,
                      font=("Arial", 9, "bold")).pack(pady=(4, 0))

            val_lbl = ttk.Label(card_frame, text="\u2014",
                                font=("Arial", 16, "bold"))
            val_lbl.pack(pady=2)

            badge = tk.Label(card_frame, text="  ", width=6,
                             bg=_RAG_COLOURS["grey"], fg="white",
                             font=("Arial", 8, "bold"))
            badge.pack(pady=(0, 4))

            self._kpi_cards[key] = {"value": val_lbl, "badge": badge}

        for c in range(len(_DASHBOARD_KPIS)):
            kpi_lf.columnconfigure(c, weight=1)

        # ---- Middle row: S-Curve + Risk Summary ----
        mid_frame = ttk.Frame(self.frame)
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Mini S-Curve (left)
        curve_lf = ttk.LabelFrame(mid_frame, text="S-Curve Overview",
                                    padding=5)
        curve_lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self._build_mini_scurve(curve_lf)

        # Risk summary (right)
        risk_lf = ttk.LabelFrame(mid_frame, text="Risk Summary", padding=5)
        risk_lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self._build_risk_summary(risk_lf)

        # ---- MC Summary (PG only) ----
        self._mc_lf = ttk.LabelFrame(self.frame,
                                      text="Monte Carlo Summary (PG)",
                                      padding=5)
        self._mc_lf.pack(fill=tk.X, padx=10, pady=5)
        self._build_mc_summary(self._mc_lf)

        # ---- Project info bar ----
        self._info_lbl = ttk.Label(
            self.frame, text="", foreground="grey",
            font=("Arial", 9, "italic"))
        self._info_lbl.pack(fill=tk.X, padx=10, pady=(0, 5))

    # ----------------------------------------------------------------
    #  Mini S-Curve
    # ----------------------------------------------------------------

    def _build_mini_scurve(self, parent):
        if not HAS_MATPLOTLIB:
            ttk.Label(parent,
                      text="Matplotlib not available.").pack(expand=True)
            return

        self._sc_fig = Figure(figsize=(4, 2.8), dpi=90)
        self._sc_ax = self._sc_fig.add_subplot(111)
        self._sc_canvas = FigureCanvasTkAgg(self._sc_fig, parent)
        self._sc_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self._sc_empty = ttk.Label(parent, text="No period data yet")

    def _update_mini_scurve(self):
        if not HAS_MATPLOTLIB:
            return

        proj = self.state.evm_project
        if proj is None or not proj.periods:
            self._sc_ax.clear()
            self._sc_ax.text(0.5, 0.5, "No period data",
                             ha="center", va="center", fontsize=10,
                             color="grey", transform=self._sc_ax.transAxes)
            self._sc_canvas.draw()
            return

        self._sc_empty.pack_forget()
        periods = proj.periods
        x = list(range(len(periods)))
        pv = [p.pv_cumulative for p in periods]
        ev = [p.ev_cumulative for p in periods]
        ac = [p.ac_cumulative for p in periods]

        ax = self._sc_ax
        ax.clear()
        ax.plot(x, pv, "g--", label="PV", linewidth=1.2)
        ax.plot(x, ev, "b-", label="EV", linewidth=1.2)
        ax.plot(x, ac, "r-", label="AC", linewidth=1.2)
        ax.legend(fontsize=7, loc="upper left")
        ax.set_title("S-Curve", fontsize=9)
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.3)
        self._sc_fig.tight_layout()
        self._sc_canvas.draw()

    # ----------------------------------------------------------------
    #  Risk Summary
    # ----------------------------------------------------------------

    def _build_risk_summary(self, parent):
        self._risk_total_lbl = ttk.Label(parent, text="Total Risks: 0",
                                          font=("Arial", 10))
        self._risk_total_lbl.pack(anchor="w", pady=2)

        self._risk_exposure_lbl = ttk.Label(parent,
                                             text="Total Exposure: $0.00",
                                             font=("Arial", 10))
        self._risk_exposure_lbl.pack(anchor="w", pady=2)

        self._risk_contingency_lbl = ttk.Label(parent,
                                                text="Contingency Reserve: $0.00",
                                                font=("Arial", 10))
        self._risk_contingency_lbl.pack(anchor="w", pady=2)

        self._risk_flagged_lbl = ttk.Label(parent,
                                            text="High-Exposure Risks: 0",
                                            font=("Arial", 10),
                                            foreground="black")
        self._risk_flagged_lbl.pack(anchor="w", pady=2)

        # Category breakdown
        self._risk_cat_text = tk.Text(parent, height=5, width=30,
                                       state=tk.DISABLED,
                                       font=("Consolas", 9))
        self._risk_cat_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    def _update_risk_summary(self):
        reg = self.state.risk_register
        sym = "$"
        if self.state.evm_project:
            sym = self.state.evm_project.currency_symbol

        if reg is None or not reg.risks:
            self._risk_total_lbl.config(text="Total Risks: 0")
            self._risk_exposure_lbl.config(text=f"Total Exposure: {sym}0.00")
            self._risk_contingency_lbl.config(
                text=f"Contingency Reserve: {sym}0.00")
            self._risk_flagged_lbl.config(text="High-Exposure Risks: 0",
                                           foreground="black")
            self._risk_cat_text.config(state=tk.NORMAL)
            self._risk_cat_text.delete("1.0", tk.END)
            self._risk_cat_text.insert("1.0", "No risks registered.")
            self._risk_cat_text.config(state=tk.DISABLED)
            return

        total = len(reg.risks)
        exposure = reg.total_exposure()
        contingency = reg.contingency_reserve()
        flagged = reg.flag_high_exposure()

        self._risk_total_lbl.config(text=f"Total Risks: {total}")
        self._risk_exposure_lbl.config(
            text=f"Total Exposure: {sym}{exposure:,.2f}")
        self._risk_contingency_lbl.config(
            text=f"Contingency Reserve: {sym}{contingency:,.2f}")

        flag_colour = "red" if len(flagged) > 0 else "black"
        self._risk_flagged_lbl.config(
            text=f"High-Exposure Risks: {len(flagged)}",
            foreground=flag_colour)

        # Category breakdown
        from collections import Counter
        cat_counts = Counter(r.category.value for r in reg.risks)
        lines = [f"  {cat}: {cnt}" for cat, cnt in
                 sorted(cat_counts.items())]
        self._risk_cat_text.config(state=tk.NORMAL)
        self._risk_cat_text.delete("1.0", tk.END)
        self._risk_cat_text.insert("1.0", "By Category:\n" + "\n".join(lines))
        self._risk_cat_text.config(state=tk.DISABLED)

    # ----------------------------------------------------------------
    #  Monte Carlo Summary (PG only)
    # ----------------------------------------------------------------

    def _build_mc_summary(self, parent):
        self._mc_labels = {}
        for key, text in [
            ("status", "Status: No simulation run yet"),
            ("n_trials", "Trials: -"),
            ("p50", "P50 Duration: -"),
            ("p80", "P80 Duration: -"),
            ("p90", "P90 Duration: -"),
            ("p_bac", "P(Cost \u2264 BAC): -"),
        ]:
            lbl = ttk.Label(parent, text=text, font=("Arial", 10))
            lbl.pack(anchor="w", pady=1)
            self._mc_labels[key] = lbl

    def _update_mc_summary(self):
        mc = self.state.mc_results
        if mc is None:
            self._mc_labels["status"].config(
                text="Status: No simulation run yet", foreground="grey")
            for k in ("n_trials", "p50", "p80", "p90", "p_bac"):
                self._mc_labels[k].config(text=f"{k}: -")
            return

        self._mc_labels["status"].config(
            text="Status: Simulation complete", foreground="green")
        self._mc_labels["n_trials"].config(
            text=f"Trials: {mc.n_trials:,}")
        self._mc_labels["p50"].config(
            text=f"P50 Duration: {mc.p50_duration:.1f}")
        self._mc_labels["p80"].config(
            text=f"P80 Duration: {mc.p80_duration:.1f}")
        self._mc_labels["p90"].config(
            text=f"P90 Duration: {mc.p90_duration:.1f}")
        self._mc_labels["p_bac"].config(
            text=f"P(Cost \u2264 BAC): {mc.p_cost_within_bac:.1%}")

    # ================================================================
    #  Refresh / public interface
    # ================================================================

    def _refresh(self):
        """Recalculate and update all dashboard panels."""
        self._update_kpi_strip()
        self._update_mini_scurve()
        self._update_risk_summary()
        self._update_mc_summary()
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
        # Show/hide MC summary (PG only)
        if mode.upper() == "PG":
            self._mc_lf.pack(fill=tk.X, padx=10, pady=5)
        else:
            self._mc_lf.pack_forget()

    def on_tab_selected(self):
        self._refresh()

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB and hasattr(self, "_sc_fig"):
            figs.append(("mini_scurve", self._sc_fig))
        return figs
