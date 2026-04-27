"""PMhelper Edu — Probability Tab.
PERT Analysis sub-tab with completion probability, risk metrics,
distribution / cumulative / sensitivity charts.
Monte Carlo sub-tab with duration & cost histograms,
probabilistic critical path table.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from pmhelper.gui.widgets.sortable_treeview import enhance_treeview

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from scipy.stats import norm
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from pmhelper.core.monte_carlo_edu import (
    MCInputs, MCResults, MonteCarloRunner,
)
from pmhelper.core.step_generators_edu import pert_steps
from pmhelper.core.ztable_loader import load_ztable, lookup_forward, lookup_reverse
from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
from pmhelper.gui.widgets.ztable_widget import ZScoreTableWidget
from pmhelper.utils.calculations import ProbabilityCalculations

# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame, WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import (
        plotly_pert_distribution, plotly_pert_cumulative, plotly_sensitivity,
        plotly_mc_results, PLOTLY_AVAILABLE as _PLT_AVAIL,
    )
    _PLOTLY_EMBED = WEBVIEW2_AVAILABLE and _PLT_AVAIL
except ImportError:
    _PLOTLY_EMBED = False


class ProbabilityTabEdu:
    """Probability tab with PERT Analysis + Monte Carlo simulation sub-tabs."""

    def __init__(self, parent, state, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        self._render_mode_var = tk.StringVar(value="matplotlib")

        # Inner notebook
        self._notebook = ttk.Notebook(self.frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sub-tab 1: PERT Analysis (first tab)
        self._pert_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._pert_frame, text="PERT Analysis")
        self._build_pert_tab()

        # Sub-tab 2: Monte Carlo
        self._mc_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._mc_frame, text="Monte Carlo")
        self._build_mc_tab()

        # Sub-tab 3: Z-Score Table
        self._ztab_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._ztab_frame, text="Z-Score Table")
        self._build_ztable_tab()

    def _build_pert_tab(self):
        """Build the PERT Analysis sub-tab UI."""
        # Main paned window: left panel (controls) + right panel (charts)
        pane = ttk.PanedWindow(self._pert_frame, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ---- LEFT PANEL: statistics + calculator ----
        left = ttk.Frame(pane)
        pane.add(left, weight=1)

        # Statistics summary
        stats_lf = ttk.LabelFrame(left, text="Project Statistics")
        stats_lf.pack(fill=tk.X, padx=4, pady=(4, 2))

        stat_labels = [
            ("Expected Duration:", "_lbl_exp_dur"),
            ("Variance:", "_lbl_variance"),
            ("Std Deviation:", "_lbl_std_dev"),
        ]
        for text, attr in stat_labels:
            row = ttk.Frame(stats_lf)
            row.pack(fill=tk.X, padx=4, pady=1)
            ttk.Label(row, text=text, width=18, anchor=tk.W).pack(side=tk.LEFT)
            var = tk.StringVar(value="—")
            ttk.Label(row, textvariable=var, foreground="#2c3e50",
                      font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT)
            setattr(self, attr, var)

        # Completion probability calculator
        calc_lf = ttk.LabelFrame(
            left, text="Completion Probability Calculator")
        calc_lf.pack(fill=tk.X, padx=4, pady=4)

        # Target duration → probability
        r1 = ttk.Frame(calc_lf)
        r1.pack(fill=tk.X, padx=4, pady=2)
        ttk.Label(r1, text="Target Duration:").pack(side=tk.LEFT)
        self._target_dur_var = tk.DoubleVar(value=0)
        ttk.Entry(
            r1,
            textvariable=self._target_dur_var,
            width=8).pack(
            side=tk.LEFT,
            padx=4)
        ttk.Button(
            r1,
            text="P(T≤d)",
            command=self._calc_prob_from_dur).pack(
            side=tk.LEFT,
            padx=2)
        self._prob_result_var = tk.StringVar(value="")
        ttk.Label(r1, textvariable=self._prob_result_var, foreground="#27ae60",
                  font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=4)

        # Target probability → duration
        r2 = ttk.Frame(calc_lf)
        r2.pack(fill=tk.X, padx=4, pady=2)
        ttk.Label(r2, text="Target Probability:").pack(side=tk.LEFT)
        self._target_prob_var = tk.DoubleVar(value=0.9)
        ttk.Entry(
            r2,
            textvariable=self._target_prob_var,
            width=8).pack(
            side=tk.LEFT,
            padx=4)
        ttk.Button(
            r2,
            text="d(P)",
            command=self._calc_dur_from_prob).pack(
            side=tk.LEFT,
            padx=2)
        self._dur_result_var = tk.StringVar(value="")
        ttk.Label(r2, textvariable=self._dur_result_var, foreground="#2980b9",
                  font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=4)

        # Flag: only show expected line / shading after student clicks
        # Calculate
        self._prob_calc_performed = False

        # Reactive chart updates when target values change (9C.7)
        self._target_dur_var.trace_add(
            'write', lambda *_: self._safe_redraw_pert())
        self._target_prob_var.trace_add(
            'write', lambda *_: self._safe_redraw_pert())

        # Common scenarios
        scen_lf = ttk.LabelFrame(left, text="Common Scenarios")
        scen_lf.pack(fill=tk.X, padx=4, pady=4)

        scenarios = [
            ("P50 (50%):", "_lbl_p50"),
            ("P80 (80%):", "_lbl_p80"),
            ("P90 (90%):", "_lbl_p90"),
            ("P95 (95%):", "_lbl_p95"),
        ]
        for text, attr in scenarios:
            row = ttk.Frame(scen_lf)
            row.pack(fill=tk.X, padx=4, pady=1)
            ttk.Label(row, text=text, width=14, anchor=tk.W).pack(side=tk.LEFT)
            var = tk.StringVar(value="—")
            ttk.Label(
                row,
                textvariable=var,
                foreground="#8e44ad").pack(
                side=tk.LEFT)
            setattr(self, attr, var)

        # Risk analysis
        risk_lf = ttk.LabelFrame(left, text="Risk Analysis")
        risk_lf.pack(fill=tk.X, padx=4, pady=(4, 2))

        risk_labels = [
            ("Coef. of Variation:", "_lbl_cov"),
            ("P(on time):", "_lbl_p_ontime"),
            ("P(≤10% late):", "_lbl_p_10_late"),
            ("P(≤20% late):", "_lbl_p_20_late"),
        ]
        for text, attr in risk_labels:
            row = ttk.Frame(risk_lf)
            row.pack(fill=tk.X, padx=4, pady=1)
            ttk.Label(row, text=text, width=18, anchor=tk.W).pack(side=tk.LEFT)
            var = tk.StringVar(value="—")
            ttk.Label(row, textvariable=var).pack(side=tk.LEFT)
            setattr(self, attr, var)

        # Worked Solution button (UG only)
        self._pert_worked_btn = ttk.Button(
            left, text="📝 Show Worked Solution",
            command=self._show_pert_worked_solution)
        self._pert_worked_btn.pack(fill=tk.X, padx=4, pady=(6, 4))

        # ---- RIGHT PANEL: charts ----
        right = ttk.Frame(pane)
        pane.add(right, weight=2)

        # Chart type selector
        chart_bar = ttk.Frame(right)
        chart_bar.pack(fill=tk.X, padx=4, pady=(4, 2))
        ttk.Label(chart_bar, text="Chart:").pack(side=tk.LEFT, padx=(0, 4))
        self._pert_chart_var = tk.StringVar(value="Distribution")
        chart_combo = ttk.Combobox(
            chart_bar,
            textvariable=self._pert_chart_var,
            values=[
                "Distribution",
                "Cumulative",
                "Sensitivity"],
            state="readonly",
            width=14)
        chart_combo.pack(side=tk.LEFT, padx=2)
        chart_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self._draw_pert_chart())
        ttk.Button(
            chart_bar,
            text="Export PNG",
            command=lambda: self._export_pert_fig("png")).pack(
            side=tk.RIGHT,
            padx=2)
        ttk.Button(
            chart_bar,
            text="\U0001f50d Open Interactive",
            command=self._open_pert_interactive).pack(
            side=tk.RIGHT,
            padx=4)

        # Renderer toggle
        if _PLOTLY_EMBED:
            rf = ttk.LabelFrame(chart_bar, text="Renderer", padding="3")
            rf.pack(side=tk.LEFT, padx=(10, 0))
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

        if not HAS_MATPLOTLIB or not HAS_SCIPY:
            msg = "Matplotlib + SciPy required for PERT charts."
            ttk.Label(right, text=msg).pack(expand=True)
            return

        self._mpl_pert_frame = ttk.Frame(right)
        self._mpl_pert_frame.pack(fill=tk.BOTH, expand=True)
        self._pert_fig = Figure(figsize=(6, 4), dpi=100)
        self._pert_ax = self._pert_fig.add_subplot(111)
        self._pert_canvas = FigureCanvasTkAgg(
            self._pert_fig, master=self._mpl_pert_frame)
        self._pert_canvas.get_tk_widget().pack(
            fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Plotly PERT frame (hidden)
        self._plotly_pert_frame = None
        if _PLOTLY_EMBED:
            self._plotly_pert_frame = PlotlyChartFrame(right)

    # ----------------------------------------------------------------
    # PERT Analysis logic
    # ----------------------------------------------------------------

    def _get_pert_params(self):
        """Extract expected duration, std deviation from analysis results."""
        if not self.main_window or not self.main_window.results_data:
            return None, None
        rd = self.main_window.results_data
        exp = rd.get('expected_duration', rd.get('project_duration', 0))
        std = rd.get('standard_deviation', 0)
        return float(exp), float(std)

    def _update_pert_stats(self):
        """Update all PERT statistics labels from analysis results."""
        exp, std = self._get_pert_params()
        if exp is None or exp <= 0:
            for attr in ('_lbl_exp_dur', '_lbl_variance', '_lbl_std_dev',
                         '_lbl_p50', '_lbl_p80', '_lbl_p90',
                         '_lbl_p95', '_lbl_cov', '_lbl_p_ontime',
                         '_lbl_p_10_late', '_lbl_p_20_late'):
                getattr(self, attr).set("—")
            return

        rd = self.main_window.results_data
        var = rd.get('project_variance', std ** 2)

        self._lbl_exp_dur.set(f"{exp:.2f}")
        self._lbl_variance.set(f"{var:.3f}")
        self._lbl_std_dev.set(f"{std:.3f}")

        # Do NOT pre-fill target duration; student must enter it
        # self._target_dur_var.set(round(exp, 1))

        # Common scenarios
        if std > 0:
            for prob, attr in [(0.5, '_lbl_p50'), (0.8, '_lbl_p80'),
                               (0.9, '_lbl_p90'), (0.95, '_lbl_p95')]:
                dur = ProbabilityCalculations.calculate_duration_for_probability(
                    prob, exp, std)
                getattr(self, attr).set(f"{dur:.2f} periods")
        else:
            for attr in ('_lbl_p50', '_lbl_p80', '_lbl_p90', '_lbl_p95'):
                getattr(self, attr).set(f"{exp:.2f} periods")

        # Risk analysis
        metrics = ProbabilityCalculations.calculate_risk_metrics(exp, std)
        self._lbl_cov.set(f"{metrics['coefficient_of_variation']:.3f}")
        self._lbl_p_ontime.set(f"{metrics['probability_on_time']:.1%}")
        self._lbl_p_10_late.set(
            f"{metrics['probability_10_percent_late']:.1%}")
        self._lbl_p_20_late.set(
            f"{metrics['probability_20_percent_late']:.1%}")

    def _calc_prob_from_dur(self):
        """Calculate P(T ≤ d) for the entered target duration."""
        exp, std = self._get_pert_params()
        if exp is None or exp <= 0:
            self._prob_result_var.set("Run PERT analysis first")
            return
        target = self._target_dur_var.get()
        prob = ProbabilityCalculations.calculate_completion_probability(
            target, exp, std)
        self._prob_result_var.set(f"→ {prob:.2%}")
        self._prob_calc_performed = True
        self._safe_redraw_pert()

    def _calc_dur_from_prob(self):
        """Calculate duration for the entered target probability."""
        exp, std = self._get_pert_params()
        if exp is None or exp <= 0:
            self._dur_result_var.set("Run PERT analysis first")
            return
        prob = self._target_prob_var.get()
        if not (0 < prob < 1):
            self._dur_result_var.set("(0 < p < 1)")
            return
        dur = ProbabilityCalculations.calculate_duration_for_probability(
            prob, exp, std)
        self._dur_result_var.set(f"→ {dur:.2f} periods")
        # Set the target duration to the calculated value and mark as
        # calculated
        self._target_dur_var.set(round(dur, 1))
        self._prob_calc_performed = True
        self._safe_redraw_pert()

    def _draw_pert_chart(self):
        """Draw the selected PERT chart type."""
        if self._render_mode_var.get() == "plotly" and getattr(
                self, '_plotly_pert_frame', None):
            self._update_plotly_pert()
            return
        if not HAS_MATPLOTLIB or not HAS_SCIPY:
            return
        if not hasattr(self, '_pert_ax'):
            return

        chart_type = self._pert_chart_var.get()
        ax = self._pert_ax
        ax.clear()

        exp, std = self._get_pert_params()
        if exp is None or exp <= 0 or std is None:
            ax.text(
                0.5,
                0.5,
                "Run PERT analysis first\n(switch to PG mode, add probabilistic data,\nthen click ▶ Analyze).",
                ha='center',
                va='center',
                fontsize=11,
                color='grey',
                transform=ax.transAxes)
            self._pert_fig.tight_layout()
            self._pert_canvas.draw()
            return

        if std <= 0:
            std = 0.001  # avoid div-by-zero

        if chart_type == "Distribution":
            self._draw_distribution(ax, exp, std)
        elif chart_type == "Cumulative":
            self._draw_cumulative(ax, exp, std)
        elif chart_type == "Sensitivity":
            self._draw_sensitivity(ax, exp, std)

        self._pert_fig.tight_layout()
        self._pert_canvas.draw()

    def _safe_redraw_pert(self):
        """Redraw PERT chart reactively, guarding against non-numeric states."""
        if not hasattr(self, '_pert_fig') or self._pert_fig is None:
            return
        try:
            self._draw_pert_chart()
        except Exception:
            pass

    def _draw_distribution(self, ax, exp, std):
        """Normal distribution PDF with shaded regions."""
        x = np.linspace(exp - 4 * std, exp + 4 * std, 300)
        y = norm.pdf(x, exp, std)
        ax.plot(x, y, color='#2c3e50', linewidth=2)
        ax.fill_between(x, y, alpha=0.15, color='#3498db')

        # Only show shading + expected line after student clicks Calculate
        if getattr(self, '_prob_calc_performed', False):
            target = self._target_dur_var.get()
            if target > 0:
                mask = x <= target
                ax.fill_between(
                    x[mask],
                    y[mask],
                    alpha=0.35,
                    color='#27ae60',
                    label=f'P(T≤{
                        target:.1f})={
                        norm.cdf(
                            (target - exp) / std):.1%}')

            # Mark expected duration
            ax.axvline(exp, color='#e74c3c', linewidth=1.5, linestyle='--',
                       label=f'Expected={exp:.1f}')

        ax.set_xlabel("Duration")
        ax.set_ylabel("Probability Density")
        ax.set_title(
            "Duration Distribution (Normal)",
            fontsize=10,
            fontweight='bold')
        ax.legend(fontsize=8, loc='upper right')

    def _draw_cumulative(self, ax, exp, std):
        """Cumulative distribution (S-curve)."""
        x = np.linspace(exp - 4 * std, exp + 4 * std, 300)
        y = norm.cdf(x, exp, std)
        ax.plot(x, y, color='#2980b9', linewidth=2)

        # Mark common percentiles
        for p, color, ls in [(0.5, '#27ae60', '--'), (0.8, '#f39c12', '-.'),
                             (0.9, '#e74c3c', ':'), (0.95, '#8e44ad', ':')]:
            d = ProbabilityCalculations.calculate_duration_for_probability(
                p, exp, std)
            ax.axhline(p, color=color, alpha=0.4, linewidth=0.8, linestyle=ls)
            ax.axvline(d, color=color, alpha=0.4, linewidth=0.8, linestyle=ls)
            ax.plot(d, p, 'o', color=color, markersize=5)
            ax.annotate(f'P{int(p * 100)}={d:.1f}', xy=(d, p),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=7, color=color)

        # Mark target duration line on CDF only after Calculate is clicked
        # (9C.7)
        if getattr(self, '_prob_calc_performed', False):
            try:
                target = self._target_dur_var.get()
                if target > 0 and (exp - 4 * std) <= target <= (exp + 4 * std):
                    p_target = norm.cdf(target, exp, std)
                    ax.axvline(
                        target,
                        color='#e74c3c',
                        linestyle='--',
                        linewidth=1.5,
                        alpha=0.8)
                    ax.plot(
                        target,
                        p_target,
                        's',
                        color='#e74c3c',
                        markersize=6,
                        zorder=5)
                    ax.annotate(f'd={target:.1f}\nP={p_target:.1%}',
                                xy=(target, p_target), xytext=(8, -15),
                                textcoords='offset points', fontsize=7, color='#e74c3c',
                                fontweight='bold')
            except (tk.TclError, ValueError):
                pass

        ax.set_xlabel("Duration")
        ax.set_ylabel("Cumulative Probability")
        ax.set_title(
            "Cumulative Distribution (S-Curve)",
            fontsize=10,
            fontweight='bold')
        ax.set_ylim(-0.02, 1.05)
        ax.grid(True, alpha=0.3)

    def _draw_sensitivity(self, ax, exp, std):
        """Sensitivity analysis — show how activity variances contribute."""
        if not self.main_window or not self.main_window.results_data:
            return
        rd = self.main_window.results_data
        activities = rd.get('activities', [])

        # Only activities with variance (PERT mode)
        act_vars = []
        for act in activities:
            v = act.get('variance', 0)
            if v > 0 and act.get('critical', False):
                act_vars.append((act.get('name', act.get('id', '?')), v))

        if not act_vars:
            # Fall back: show all activities with variance
            for act in activities:
                v = act.get('variance', 0)
                if v > 0:
                    act_vars.append((act.get('name', act.get('id', '?')), v))

        if not act_vars:
            ax.text(
                0.5,
                0.5,
                "No activity variances available.\nRun PERT analysis first.",
                ha='center',
                va='center',
                fontsize=11,
                color='grey',
                transform=ax.transAxes)
            return

        # Sort by variance descending
        act_vars.sort(key=lambda x: x[1], reverse=True)
        total_var = sum(v for _, v in act_vars)
        names = [n[:15] for n, _ in act_vars]
        pcts = [(v / total_var * 100) if total_var >
                0 else 0 for _, v in act_vars]

        bars = ax.barh(
            range(
                len(names)),
            pcts,
            color='#e67e22',
            edgecolor='white')
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=8)
        ax.set_xlabel("Contribution to Total Variance (%)")
        ax.set_title("Variance Sensitivity (Critical Path Activities)",
                     fontsize=10, fontweight='bold')
        ax.invert_yaxis()

        # Add percentage labels
        for bar, pct in zip(bars, pcts):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                    f'{pct:.1f}%', va='center', fontsize=8)

    def _export_pert_fig(self, fmt):
        """Export the PERT chart."""
        if not hasattr(self, '_pert_fig'):
            return
        from tkinter import filedialog
        ext = f".{fmt}"
        filepath = filedialog.asksaveasfilename(
            title=f"Export PERT chart as {fmt.upper()}",
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} files", f"*{ext}"), ("All files", "*.*")])
        if filepath:
            self._pert_fig.savefig(filepath, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Export", f"Saved to {filepath}")

    def update_from_analysis(self, results_data, analysis_mode):
        """Update PERT sub-tab with new analysis results."""
        self._update_pert_stats()
        self._draw_pert_chart()
        self._update_ztable_auto()

    # ----------------------------------------------------------------
    # Z-Score Table sub-tab
    # ----------------------------------------------------------------

    def _build_ztable_tab(self):
        """Build the Z-Score Table sub-tab."""

        pane = ttk.PanedWindow(self._ztab_frame, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._zt_pane = pane  # kept for sash reset

        # ── LEFT PANEL: inputs + bell curve ──
        left = ttk.Frame(pane)
        pane.add(left, weight=3)

        # Formula display
        formula_lf = ttk.LabelFrame(left, text="Z-Score Formula")
        formula_lf.pack(fill=tk.X, padx=4, pady=(4, 2))
        self._zt_formula_var = tk.StringVar(value="Z = (d − μ) / σ")
        ttk.Label(formula_lf, textvariable=self._zt_formula_var,
                  font=("Consolas", 11), foreground="#2c3e50").pack(
                      padx=6, pady=4)
        self._zt_substitution_var = tk.StringVar(value="")
        ttk.Label(formula_lf, textvariable=self._zt_substitution_var,
                  font=("Consolas", 9), foreground="#7f8c8d").pack(
                      padx=6, pady=(0, 4))

        # Forward lookup: Z → P
        fwd_lf = ttk.LabelFrame(left, text="Forward Lookup: Z → P(Z)")
        fwd_lf.pack(fill=tk.X, padx=4, pady=4)

        r1 = ttk.Frame(fwd_lf)
        r1.pack(fill=tk.X, padx=4, pady=3)
        ttk.Label(r1, text="Z =").pack(side=tk.LEFT)
        self._zt_z_var = tk.StringVar(value="")
        ttk.Entry(r1, textvariable=self._zt_z_var, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(r1, text="Find P(Z)",
                   command=self._zt_forward_lookup).pack(side=tk.LEFT, padx=2)
        self._zt_fwd_result_var = tk.StringVar(value="")
        ttk.Label(r1, textvariable=self._zt_fwd_result_var,
                  foreground="#27ae60",
                  font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=6)

        # Reverse lookup: P → Z
        rev_lf = ttk.LabelFrame(left, text="Reverse Lookup: P → Z")
        rev_lf.pack(fill=tk.X, padx=4, pady=4)

        r2 = ttk.Frame(rev_lf)
        r2.pack(fill=tk.X, padx=4, pady=3)
        ttk.Label(r2, text="P =").pack(side=tk.LEFT)
        self._zt_p_var = tk.StringVar(value="")
        ttk.Entry(r2, textvariable=self._zt_p_var, width=8).pack(
            side=tk.LEFT, padx=4)
        ttk.Button(r2, text="Find Z",
                   command=self._zt_reverse_lookup).pack(side=tk.LEFT, padx=2)
        self._zt_rev_result_var = tk.StringVar(value="")
        ttk.Label(r2, textvariable=self._zt_rev_result_var,
                  foreground="#2980b9",
                  font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=6)

        # Bell curve diagram (matplotlib)
        if HAS_MATPLOTLIB and HAS_SCIPY:
            chart_lf = ttk.LabelFrame(
                left, text="Standard Normal Distribution")
            chart_lf.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            self._zt_fig = Figure(figsize=(5.5, 5.5), dpi=90)
            self._zt_ax = self._zt_fig.add_subplot(111)
            self._zt_canvas = FigureCanvasTkAgg(self._zt_fig, master=chart_lf)
            self._zt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            self._draw_zt_bell()

        # ── RIGHT PANEL: Z-score table grid ──
        right = ttk.Frame(pane)
        pane.add(right, weight=2)

        # Set initial sash to 60 : 40 left/right split
        self._ztab_frame.after(
            150, lambda p=pane: p.sashpos(
                0, int(
                    p.winfo_width() * 0.60)))

        # Load the CSV
        self._zt_table = None
        self._zt_widget = None
        csv_path = self._find_ztable_csv()
        if csv_path:
            try:
                self._zt_table = load_ztable(csv_path)
                self._zt_widget = ZScoreTableWidget(right, self._zt_table)
                self._zt_widget.pack(fill=tk.BOTH, expand=True)
            except Exception as exc:
                ttk.Label(right,
                          text=f"Error loading Z-table: {exc}").pack(
                              expand=True)
        else:
            ttk.Label(
                right,
                text="ztable.csv not found.\nPlace it in the project root.").pack(
                expand=True)

    def _find_ztable_csv(self) -> str | None:
        """Locate ztable.csv — check project root and package directory."""
        import os
        candidates = []
        # Project root (next to pyproject.toml)
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        for up in range(5):
            candidate = os.path.join(pkg_dir, "ztable.csv")
            if os.path.isfile(candidate):
                return candidate
            pkg_dir = os.path.dirname(pkg_dir)
        # Fallback: CWD
        cwd = os.path.join(os.getcwd(), "ztable.csv")
        if os.path.isfile(cwd):
            return cwd
        return None

    def _zt_forward_lookup(self):
        """Handle Z → P(Z) button click."""
        if self._zt_table is None:
            return
        raw = self._zt_z_var.get().strip()
        try:
            z = float(raw)
        except ValueError:
            self._zt_fwd_result_var.set("Enter a number")
            self._zt_z_var.set("")
            return
        result = lookup_forward(self._zt_table, z)
        if result is None:
            self._zt_fwd_result_var.set(
                f"Z={
                    z:.2f} outside range [{
                    self._zt_table.z_min:.1f}, {
                    self._zt_table.z_max:.2f}]")
            self._zt_z_var.set("")
            return
        self._zt_fwd_result_var.set(
            f"→ P(Z≤{
                result.z_value:.2f}) = {
                result.probability:.4f}")
        if self._zt_widget:
            self._zt_widget.highlight_forward(result)
        self._draw_zt_bell(z=result.z_value)

    def _zt_reverse_lookup(self):
        """Handle P → Z button click."""
        if self._zt_table is None:
            return
        raw = self._zt_p_var.get().strip()
        try:
            p = float(raw)
        except ValueError:
            self._zt_rev_result_var.set("Enter a number")
            self._zt_p_var.set("")
            return
        if not (0 < p < 1):
            self._zt_rev_result_var.set("P must be between 0 and 1")
            self._zt_p_var.set("")
            return
        result = lookup_reverse(self._zt_table, p)
        if result is None:
            self._zt_rev_result_var.set("Not found")
            return
        approx = "" if result.is_exact else " ≈"
        self._zt_rev_result_var.set(
            f"→ Z{approx} {result.z_value:.2f}  (P={result.probability:.4f})")
        if self._zt_widget:
            self._zt_widget.highlight_reverse(result)
        self._draw_zt_bell(z=result.z_value)

    def _draw_zt_bell(self, z: float | None = None):
        """Draw the standard normal bell curve, optionally shading up to *z*."""
        if not HAS_MATPLOTLIB or not HAS_SCIPY:
            return
        if not hasattr(self, '_zt_ax'):
            return
        ax = self._zt_ax
        ax.clear()
        x = np.linspace(-4, 4, 300)
        y = norm.pdf(x, 0, 1)
        ax.plot(x, y, color='#2c3e50', linewidth=1.5)
        ax.fill_between(x, y, alpha=0.08, color='#3498db')

        if z is not None:
            mask = x <= z
            ax.fill_between(x[mask], y[mask], alpha=0.35, color='#27ae60')
            ax.axvline(z, color='#e74c3c', linewidth=1.2, linestyle='--')
            prob = norm.cdf(z)
            ax.set_title(
                f"P(Z ≤ {
                    z:.2f}) = {
                    prob:.4f}",
                fontsize=8,
                fontweight='bold')
        else:
            ax.set_title("Standard Normal Distribution", fontsize=8)

        ax.set_xlabel("Z", fontsize=7)
        ax.set_ylabel("f(z)", fontsize=7)
        ax.tick_params(labelsize=6)
        self._zt_fig.tight_layout(pad=0.5)
        self._zt_canvas.draw()

    def _update_ztable_auto(self):
        """Auto-compute Z from PERT results and highlight in the Z-table."""
        if self._zt_table is None or self._zt_widget is None:
            return
        exp, std = self._get_pert_params()
        if exp is None or exp <= 0 or std is None or std <= 0:
            return
        try:
            target = self._target_dur_var.get()
        except (tk.TclError, ValueError):
            return
        if target <= 0:
            return
        z = (target - exp) / std
        result = lookup_forward(self._zt_table, z)
        if result is None:
            return
        self._zt_fwd_result_var.set(
            f"→ P(Z≤{
                result.z_value:.2f}) = {
                result.probability:.4f}")
        self._zt_z_var.set(f"{result.z_value:.2f}")
        self._zt_substitution_var.set(
            f"Z = ({target:.2f} − {exp:.2f}) / {std:.4f} = {result.z_value:.4f}")
        self._zt_widget.highlight_forward(result)
        self._draw_zt_bell(z=result.z_value)

    # ----------------------------------------------------------------
    # Monte Carlo sub-tab
    # ----------------------------------------------------------------

    def _build_mc_tab(self):
        # Controls
        ctrl = ttk.Frame(self._mc_frame)
        ctrl.pack(fill=tk.X, padx=5, pady=(5, 2))

        ttk.Label(ctrl, text="Trials (N):").pack(side=tk.LEFT, padx=(0, 4))
        self._n_var = tk.IntVar(value=5000)
        self._n_spin = ttk.Spinbox(ctrl, from_=500, to=50000, increment=500,
                                   textvariable=self._n_var, width=8)
        self._n_spin.pack(side=tk.LEFT, padx=(0, 8))

        self._run_btn = ttk.Button(ctrl, text="Run Simulation",
                                   command=self._run_mc)
        self._run_btn.pack(side=tk.LEFT, padx=2)

        self._cancel_btn = ttk.Button(ctrl, text="Cancel",
                                      command=self._cancel_mc,
                                      state="disabled")
        self._cancel_btn.pack(side=tk.LEFT, padx=2)

        self._progress = ttk.Progressbar(ctrl, mode="determinate",
                                         maximum=100, length=200)
        self._progress.pack(side=tk.LEFT, padx=8)

        self._status_var = tk.StringVar(value="Ready")
        ttk.Label(
            ctrl,
            textvariable=self._status_var).pack(
            side=tk.LEFT,
            padx=4)

        if not HAS_MATPLOTLIB:
            ttk.Label(
                self._mc_frame,
                text="Matplotlib not installed — charts unavailable.").pack(
                expand=True)
            return

        # Results area (scrollable-ish via paned)
        pane = ttk.PanedWindow(self._mc_frame, orient=tk.VERTICAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Duration histogram
        dur_frame = ttk.LabelFrame(pane, text="Duration Distribution")
        pane.add(dur_frame, weight=1)
        self._mpl_dur_frame = ttk.Frame(dur_frame)
        self._mpl_dur_frame.pack(fill=tk.BOTH, expand=True)
        self._dur_fig = Figure(figsize=(6, 3), dpi=100)
        self._dur_ax = self._dur_fig.add_subplot(111)
        self._dur_canvas = FigureCanvasTkAgg(
            self._dur_fig, master=self._mpl_dur_frame)
        self._dur_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Cost histogram
        cost_frame = ttk.LabelFrame(pane, text="Cost Distribution")
        pane.add(cost_frame, weight=1)
        self._mpl_cost_frame = ttk.Frame(cost_frame)
        self._mpl_cost_frame.pack(fill=tk.BOTH, expand=True)
        self._cost_fig = Figure(figsize=(6, 3), dpi=100)
        self._cost_ax = self._cost_fig.add_subplot(111)
        self._cost_canvas = FigureCanvasTkAgg(
            self._cost_fig, master=self._mpl_cost_frame)
        self._cost_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Plotly MC frame (hidden)
        self._plotly_mc_frame = None
        if _PLOTLY_EMBED:
            self._plotly_mc_frame = PlotlyChartFrame(pane)

        # CP frequency table
        cp_frame = ttk.LabelFrame(pane, text="Probabilistic Critical Path")
        pane.add(cp_frame, weight=1)
        cols = ("task", "frequency")
        self._cp_tree = ttk.Treeview(cp_frame, columns=cols, show="headings",
                                     height=6)
        self._cp_tree.heading("task", text="Task")
        self._cp_tree.heading("frequency", text="CP Frequency (%)")
        self._cp_tree.column("task", width=200)
        self._cp_tree.column("frequency", width=120, anchor=tk.E)
        self._cp_tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        enhance_treeview(self._cp_tree)

        # Export buttons
        export_bar = ttk.Frame(self._mc_frame)
        export_bar.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(
            export_bar,
            text="Export Duration PNG",
            command=lambda: self._export_fig(
                self._dur_fig,
                "duration",
                "png")).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            export_bar,
            text="Export Cost PNG",
            command=lambda: self._export_fig(
                self._cost_fig,
                "cost",
                "png")).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            export_bar,
            text="\U0001f50d Open Interactive",
            command=self._open_mc_interactive).pack(
            side=tk.LEFT,
            padx=6)

    def _run_mc(self):
        """Run Monte Carlo simulation."""
        proj = self.state.evm_project
        # Build activity list from EVM tasks (fallback if no CPM activities)
        activities = []
        for t in proj.tasks:
            act = {
                "id": t.task_id,
                "predecessors": [],
                "duration": max(1, t.planned_finish - t.planned_start),
            }
            activities.append(act)

        if not activities:
            messagebox.showinfo("Monte Carlo",
                                "No tasks found. Add tasks in the Input tab.")
            return

        inputs = MCInputs(
            cpm_activities=activities,
            evm_tasks=proj.tasks,
            risks=self.state.risk_register.risks if self.state.risk_register else [],
            bac=proj.bac,
            n_trials=self._n_var.get(),
        )

        self._run_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._status_var.set("Running...")
        self._progress["value"] = 0

        root = self.main_window.root if self.main_window else None
        self._mc_runner = MonteCarloRunner(root=root)

        def on_progress(pct):
            self._progress["value"] = pct * 100

        def on_complete(results: MCResults):
            self.state.mc_results = results
            self._run_btn.configure(state="normal")
            self._cancel_btn.configure(state="disabled")
            self._status_var.set(
                f"Done — P50={results.p50_duration:.1f}, "
                f"P80={results.p80_duration:.1f}, "
                f"P90={results.p90_duration:.1f}")
            self._progress["value"] = 100
            self._draw_results(results)

        def on_error(exc: Exception):
            self._run_btn.configure(state="normal")
            self._cancel_btn.configure(state="disabled")
            self._progress["value"] = 0
            if "cancelled" in str(exc).lower():
                self._status_var.set("Cancelled")
            else:
                self._status_var.set(f"Error: {exc}")
                messagebox.showerror("Monte Carlo Error", str(exc))

        self._mc_runner.run_async(inputs, on_progress, on_complete, on_error)

    def _cancel_mc(self):
        """Cancel a running Monte Carlo simulation."""
        runner = getattr(self, '_mc_runner', None)
        if runner is not None:
            runner.cancel()

    def _draw_results(self, results: MCResults):
        """Draw histograms and populate CP table."""
        if self._render_mode_var.get() == "plotly" and getattr(
                self, '_plotly_mc_frame', None):
            self._update_plotly_mc(results)
            self._fill_cp_tree(results)
            return
        if not HAS_MATPLOTLIB:
            return

        # Duration histogram
        ax = self._dur_ax
        ax.clear()
        ax.hist(results.durations, bins=40, color="#3498db", edgecolor="white",
                alpha=0.8, density=True)
        for pval, label, color in [
            (results.p50_duration, "P50", "#2ecc71"),
            (results.p80_duration, "P80", "#f39c12"),
            (results.p90_duration, "P90", "#e74c3c"),
        ]:
            ax.axvline(pval, color=color, linewidth=2, linestyle="--",
                       label=f"{label}={pval:.1f}")
        ax.set_xlabel("Project Duration")
        ax.set_ylabel("Density")
        ax.set_title("Duration Distribution", fontsize=10, fontweight="bold")
        ax.legend(fontsize=8)
        self._dur_fig.tight_layout()
        self._dur_canvas.draw()

        # Cost histogram
        ax = self._cost_ax
        ax.clear()
        ax.hist(results.costs, bins=40, color="#e67e22", edgecolor="white",
                alpha=0.8, density=True)
        bac = self.state.evm_project.bac if self.state.evm_project else 0
        if bac > 0:
            ax.axvline(bac, color="#e74c3c", linewidth=2, linestyle="-",
                       label=f"BAC=${bac:,.0f}")
            ax.annotate(
                f"P(cost \u2264 BAC) = {results.p_cost_within_bac:.1%}",
                xy=(bac, 0), xytext=(bac * 1.02, ax.get_ylim()[1] * 0.8),
                fontsize=9, color="#e74c3c",
                arrowprops=dict(arrowstyle="->", color="#e74c3c"))
        ax.set_xlabel("Total Cost ($)")
        ax.set_ylabel("Density")
        ax.set_title("Cost Distribution", fontsize=10, fontweight="bold")
        ax.legend(fontsize=8)
        self._cost_fig.tight_layout()
        self._cost_canvas.draw()

        # CP frequency table
        self._cp_tree.delete(*self._cp_tree.get_children())
        sorted_cp = sorted(results.cp_frequencies.items(),
                           key=lambda x: x[1], reverse=True)
        for task_id, freq in sorted_cp:
            if freq > 0:
                self._cp_tree.insert("", tk.END, values=(
                    task_id, f"{freq * 100:.1f}%"))

    def _export_fig(self, fig, name, fmt):
        from tkinter import filedialog
        ext = f".{fmt}"
        filepath = filedialog.asksaveasfilename(
            title=f"Export {name} chart",
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} files", f"*{ext}"), ("All files", "*.*")])
        if filepath:
            fig.savefig(filepath, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Export", f"Saved to {filepath}")

    def set_mode(self, mode: str):
        """PG-only tab."""
        self._mode = mode
        # Show worked-solution button only in UG mode
        if hasattr(self, "_pert_worked_btn"):
            if mode.upper() == "UG":
                self._pert_worked_btn.pack(fill=tk.X, padx=4, pady=(6, 4))
            else:
                self._pert_worked_btn.pack_forget()

    def _show_pert_worked_solution(self):
        """Open a Worked Solution window for PERT calculations."""
        if not self.main_window or not self.main_window.results_data:
            messagebox.showinfo("No data",
                                "Run PERT analysis first (Analyze button).",
                                parent=self.frame)
            return
        rd = self.main_window.results_data
        if not rd.get("expected_duration"):
            messagebox.showinfo(
                "No PERT data",
                "PERT data not available. Use probabilistic mode.",
                parent=self.frame)
            return
        target = None
        try:
            target = self._target_dur_var.get()
            if target <= 0:
                target = None
        except (tk.TclError, ValueError):
            target = None
        steps = pert_steps(rd, target_duration=target)
        WorkedSolutionWindow(self.frame, "PERT — Worked Solution", steps)

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB:
            if hasattr(self, "_pert_fig"):
                figs.append(("pert_analysis", self._pert_fig))
            if hasattr(self, "_dur_fig"):
                figs.append(("mc_duration", self._dur_fig))
            if hasattr(self, "_cost_fig"):
                figs.append(("mc_cost", self._cost_fig))
        return figs

    def on_tab_selected(self):
        """Check for cached MC results and refresh PERT stats."""
        # Refresh PERT tab
        self._update_pert_stats()
        self._draw_pert_chart()
        # Refresh MC tab
        if self.state.mc_results and HAS_MATPLOTLIB:
            self._draw_results(self.state.mc_results)

    def _open_pert_interactive(self):
        exp, std = self._get_pert_params()
        if exp is None or std is None or exp <= 0 or std <= 0:
            messagebox.showinfo("Interactive", "Run PERT analysis first.")
            return
        target, probability = None, None
        if getattr(self, '_prob_calc_performed', False):
            try:
                t = self._target_dur_var.get()
                if t > 0:
                    target = t
            except Exception:
                pass
            try:
                p = self._target_prob_var.get()
                if 0 < p < 1:
                    probability = p
            except Exception:
                pass
            if target is not None and probability is None:
                probability = norm.cdf(target, exp, std)
            elif probability is not None and target is None:
                target = norm.ppf(probability, exp, std)
        from pmhelper.utils.interactive_charts import open_chart_in_browser
        fig = plotly_pert_distribution(exp, std, target, probability)
        open_chart_in_browser(fig, "PERT Distribution")

    def _open_mc_interactive(self):
        results = self.state.mc_results
        if not results:
            messagebox.showinfo("Interactive", "Run Monte Carlo first.")
            return
        from pmhelper.utils.interactive_charts import open_chart_in_browser
        fig = plotly_mc_results(results)
        open_chart_in_browser(fig, "Monte Carlo Results")

    # ── Plotly embedded renderer ──────────────────────────────────

    def _switch_renderer(self):
        mode = self._render_mode_var.get()
        # PERT charts
        if mode == "plotly" and getattr(self, '_plotly_pert_frame', None):
            if hasattr(self, '_mpl_pert_frame'):
                self._mpl_pert_frame.pack_forget()
            self._plotly_pert_frame.pack(
                fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            if getattr(self, '_plotly_pert_frame', None):
                self._plotly_pert_frame.pack_forget()
            if hasattr(self, '_mpl_pert_frame'):
                self._mpl_pert_frame.pack(fill=tk.BOTH, expand=True)
        # MC charts
        if mode == "plotly" and getattr(self, '_plotly_mc_frame', None):
            if hasattr(self, '_mpl_dur_frame'):
                self._mpl_dur_frame.pack_forget()
            if hasattr(self, '_mpl_cost_frame'):
                self._mpl_cost_frame.pack_forget()
            self._plotly_mc_frame.pack(
                fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            if getattr(self, '_plotly_mc_frame', None):
                self._plotly_mc_frame.pack_forget()
            if hasattr(self, '_mpl_dur_frame'):
                self._mpl_dur_frame.pack(fill=tk.BOTH, expand=True)
            if hasattr(self, '_mpl_cost_frame'):
                self._mpl_cost_frame.pack(fill=tk.BOTH, expand=True)
        self._draw_pert_chart()
        if self.state.mc_results:
            self._draw_results(self.state.mc_results)

    def _update_plotly_pert(self):
        if not getattr(self, '_plotly_pert_frame', None):
            return
        exp, std = self._get_pert_params()
        if exp is None or exp <= 0 or std is None or std <= 0:
            return
        chart_type = self._pert_chart_var.get()

        # Only pass target after the student clicks Calculate (same guard
        # as the matplotlib Distribution/Cumulative charts — 9C.7).
        target = None
        probability = None
        if getattr(self, '_prob_calc_performed', False):
            try:
                t = self._target_dur_var.get()
                if t > 0:
                    target = t
            except (tk.TclError, ValueError, AttributeError):
                pass
            try:
                p = self._target_prob_var.get()
                if 0 < p < 1:
                    probability = p
            except (tk.TclError, ValueError, AttributeError):
                pass
            # Derive whichever value is missing from the other
            if target is not None and probability is None:
                probability = norm.cdf(target, exp, std)
            elif probability is not None and target is None:
                target = norm.ppf(probability, exp, std)

        try:
            if chart_type == "Cumulative":
                fig = plotly_pert_cumulative(exp, std, target, probability)
            elif chart_type == "Sensitivity":
                rd = self.main_window.results_data if self.main_window else {}
                acts = rd.get("activities", [])
                fig = plotly_sensitivity(acts)
            else:
                fig = plotly_pert_distribution(exp, std, target, probability)
            if fig:
                self._plotly_pert_frame.update_chart(fig)
        except Exception as e:
            self._plotly_pert_frame.load_html(
                f"<html><body><pre>Error: {e}</pre></body></html>")

    def _update_plotly_mc(self, results):
        if not getattr(self, '_plotly_mc_frame', None):
            return
        try:
            fig = plotly_mc_results(results)
            if fig:
                self._plotly_mc_frame.update_chart(fig)
        except Exception as e:
            self._plotly_mc_frame.load_html(
                f"<html><body><pre>Error: {e}</pre></body></html>")

    def _fill_cp_tree(self, results):
        self._cp_tree.delete(*self._cp_tree.get_children())
        sorted_cp = sorted(results.cp_frequencies.items(),
                           key=lambda x: x[1], reverse=True)
        for task_id, freq in sorted_cp:
            if freq > 0:
                self._cp_tree.insert("", tk.END, values=(
                    task_id, f"{freq * 100:.1f}%"))
