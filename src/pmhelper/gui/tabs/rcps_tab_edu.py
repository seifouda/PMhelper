"""PMhelper Edu — RCPS (Resources) Tab.
Histogram sub-tab: Cost-per-period and Resource usage charts.
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


class RCPSTabEdu:
    """Resources tab with cost/resource histogram sub-tab."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)

        # Inner notebook
        self._notebook = ttk.Notebook(self.frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sub-tab: Histograms
        self._hist_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._hist_frame, text="Histograms")
        self._build_histogram_tab()

    def _build_histogram_tab(self):
        toolbar = ttk.Frame(self._hist_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))
        ttk.Button(toolbar, text="Refresh", command=self._draw_histograms).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export PNG",
                   command=lambda: self._export("png")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export PDF",
                   command=lambda: self._export("pdf")).pack(side=tk.LEFT, padx=2)

        if not HAS_MATPLOTLIB:
            ttk.Label(self._hist_frame,
                      text="Matplotlib not installed — histograms unavailable.").pack(
                expand=True)
            return

        # Matplotlib figure with 2 subplots
        self._fig = Figure(figsize=(8, 6), dpi=100)
        self._ax_cost = self._fig.add_subplot(211)
        self._ax_resource = self._fig.add_subplot(212)
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._hist_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _draw_histograms(self):
        if not HAS_MATPLOTLIB:
            return

        proj = self.state.evm_project
        periods = proj.periods

        # --- Cost-per-Period chart ---
        ax = self._ax_cost
        ax.clear()
        if not periods:
            ax.text(0.5, 0.5, "No period data.\nAdd periods in the Input tab.",
                    ha="center", va="center", fontsize=11, color="grey",
                    transform=ax.transAxes)
        else:
            labels = [p.label for p in periods]
            # Compute per-period AC deltas
            ac_deltas = [periods[0].ac_cumulative]
            for i in range(1, len(periods)):
                ac_deltas.append(periods[i].ac_cumulative - periods[i - 1].ac_cumulative)
            # Compute per-period PV deltas
            pv_deltas = [periods[0].pv_cumulative]
            for i in range(1, len(periods)):
                pv_deltas.append(periods[i].pv_cumulative - periods[i - 1].pv_cumulative)

            x = np.arange(len(labels))
            width = 0.35
            ax.bar(x - width / 2, pv_deltas, width, label="PV per period",
                   color="#2ecc71", alpha=0.8)
            ax.bar(x + width / 2, ac_deltas, width, label="AC per period",
                   color="#e74c3c", alpha=0.8)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontsize=8, rotation=45, ha="right")
            ax.set_ylabel("Cost ($)")
            ax.set_title("Cost per Period", fontsize=10, fontweight="bold")
            ax.legend(fontsize=8)

        # --- Resource Usage chart ---
        ax2 = self._ax_resource
        ax2.clear()
        ax2.text(0.5, 0.5,
                 "Resource usage data requires RCPS analysis.\n"
                 "Run RCPS analysis first.",
                 ha="center", va="center", fontsize=11, color="grey",
                 transform=ax2.transAxes)
        ax2.set_title("Resource Usage", fontsize=10, fontweight="bold")

        self._fig.tight_layout()
        self._canvas.draw()

    def _export(self, fmt):
        from tkinter import filedialog
        ext = f".{fmt}"
        filepath = filedialog.asksaveasfilename(
            title=f"Export Histograms as {fmt.upper()}",
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} files", f"*{ext}"), ("All files", "*.*")])
        if filepath:
            self._fig.savefig(filepath, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Export", f"Saved to {filepath}")

    def set_mode(self, mode: str):
        """PG-only tab."""
        self._mode = mode

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB and hasattr(self, "_fig"):
            figs.append(("resource_histograms", self._fig))
        return figs

    def on_tab_selected(self):
        """Refresh histograms."""
        self._draw_histograms()
