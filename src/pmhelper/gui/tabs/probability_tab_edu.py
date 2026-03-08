"""PMhelper Edu — Probability Tab.
Monte Carlo sub-tab with duration & cost histograms,
probabilistic critical path table.
"""

import tkinter as tk
from tkinter import ttk, messagebox

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.monte_carlo_edu import (
    MCInputs, MCResults, MonteCarloRunner, run_simulation,
)


class ProbabilityTabEdu:
    """Probability tab with Monte Carlo simulation sub-tab."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)

        # Inner notebook
        self._notebook = ttk.Notebook(self.frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sub-tab: Monte Carlo
        self._mc_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._mc_frame, text="Monte Carlo")
        self._build_mc_tab()

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

        self._progress = ttk.Progressbar(ctrl, mode="determinate",
                                         maximum=100, length=200)
        self._progress.pack(side=tk.LEFT, padx=8)

        self._status_var = tk.StringVar(value="Ready")
        ttk.Label(ctrl, textvariable=self._status_var).pack(side=tk.LEFT, padx=4)

        if not HAS_MATPLOTLIB:
            ttk.Label(self._mc_frame,
                      text="Matplotlib not installed — charts unavailable.").pack(
                expand=True)
            return

        # Results area (scrollable-ish via paned)
        pane = ttk.PanedWindow(self._mc_frame, orient=tk.VERTICAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Duration histogram
        dur_frame = ttk.LabelFrame(pane, text="Duration Distribution")
        pane.add(dur_frame, weight=1)
        self._dur_fig = Figure(figsize=(6, 3), dpi=100)
        self._dur_ax = self._dur_fig.add_subplot(111)
        self._dur_canvas = FigureCanvasTkAgg(self._dur_fig, master=dur_frame)
        self._dur_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Cost histogram
        cost_frame = ttk.LabelFrame(pane, text="Cost Distribution")
        pane.add(cost_frame, weight=1)
        self._cost_fig = Figure(figsize=(6, 3), dpi=100)
        self._cost_ax = self._cost_fig.add_subplot(111)
        self._cost_canvas = FigureCanvasTkAgg(self._cost_fig, master=cost_frame)
        self._cost_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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

        # Export buttons
        export_bar = ttk.Frame(self._mc_frame)
        export_bar.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(export_bar, text="Export Duration PNG",
                   command=lambda: self._export_fig(self._dur_fig, "duration", "png")).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(export_bar, text="Export Cost PNG",
                   command=lambda: self._export_fig(self._cost_fig, "cost", "png")).pack(
            side=tk.LEFT, padx=2)

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
            messagebox.showinfo("Monte Carlo", "No tasks found. Add tasks in the Input tab.")
            return

        inputs = MCInputs(
            cpm_activities=activities,
            evm_tasks=proj.tasks,
            risks=self.state.risk_register.risks if self.state.risk_register else [],
            bac=proj.bac,
            n_trials=self._n_var.get(),
        )

        self._run_btn.configure(state="disabled")
        self._status_var.set("Running...")
        self._progress["value"] = 0

        def on_progress(pct):
            self._progress["value"] = pct * 100

        def on_complete(results: MCResults):
            self.state.mc_results = results
            self._run_btn.configure(state="normal")
            self._status_var.set(
                f"Done — P50={results.p50_duration:.1f}, "
                f"P80={results.p80_duration:.1f}, "
                f"P90={results.p90_duration:.1f}")
            self._progress["value"] = 100
            self._draw_results(results)

        def on_error(exc: Exception):
            self._run_btn.configure(state="normal")
            self._status_var.set(f"Error: {exc}")
            self._progress["value"] = 0
            messagebox.showerror("Monte Carlo Error", str(exc))

        # Run synchronously (threading via MonteCarloRunner needs root)
        try:
            result = run_simulation(inputs, on_progress)
            on_complete(result)
        except Exception as e:
            on_error(e)

    def _draw_results(self, results: MCResults):
        """Draw histograms and populate CP table."""
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
        bac = self.state.evm_project.bac
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

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB:
            if hasattr(self, "_dur_fig"):
                figs.append(("mc_duration", self._dur_fig))
            if hasattr(self, "_cost_fig"):
                figs.append(("mc_cost", self._cost_fig))
        return figs

    def on_tab_selected(self):
        """Check for cached MC results."""
        if self.state.mc_results and HAS_MATPLOTLIB:
            self._draw_results(self.state.mc_results)
