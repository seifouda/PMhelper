"""PMhelper Edu — RCPS (Resources) Tab.
RCPS Schedule sub-tab: resource-constrained scheduling with comparison table + Gantt.
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

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class RCPSTabEdu:
    """Resources tab with RCPS Schedule + cost/resource histogram sub-tabs."""

    def __init__(self, parent, state, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self.frame = ttk.Frame(parent)

        # Compatibility attributes for RCPS Crashing bidirectional link
        self._rcps_crashing_tab = None
        self._rcps_analyzer = None
        self._rcps_table_data = None
        self._resource_limit = 5

        # Inner notebook
        self._notebook = ttk.Notebook(self.frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sub-tab 1: RCPS Schedule (first tab)
        self._sched_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._sched_frame, text="RCPS Schedule")
        self._build_schedule_tab()

        # Sub-tab 2: Histograms
        self._hist_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._hist_frame, text="Histograms")
        self._build_histogram_tab()

    # ================================================================
    #  RCPS Schedule sub-tab
    # ================================================================

    def _build_schedule_tab(self):
        """Build the RCPS scheduling UI with controls, comparison table, and Gantt."""
        # Controls bar
        ctrl = ttk.Frame(self._sched_frame)
        ctrl.pack(fill=tk.X, padx=5, pady=(5, 2))

        ttk.Label(ctrl, text="Resource Limit:").pack(side=tk.LEFT, padx=(0, 4))
        self._res_limit_var = tk.IntVar(value=5)
        ttk.Spinbox(ctrl, from_=1, to=100, increment=1,
                    textvariable=self._res_limit_var, width=5).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(ctrl, text="Priority Rule:").pack(side=tk.LEFT, padx=(0, 4))
        self._priority_var = tk.StringVar(value="minimum_slack")
        ttk.Combobox(ctrl, textvariable=self._priority_var,
                     values=["minimum_slack", "shortest_duration", "earliest_start"],
                     state="readonly", width=18).pack(side=tk.LEFT, padx=(0, 8))

        self._run_btn = ttk.Button(ctrl, text="▶ Run RCPS",
                                    command=self._run_rcps)
        self._run_btn.pack(side=tk.LEFT, padx=2)

        self._status_var = tk.StringVar(value="Ready — run CPM/PERT analysis first")
        ttk.Label(ctrl, textvariable=self._status_var,
                  foreground="grey").pack(side=tk.LEFT, padx=8)

        # Results area — paned: top=table, bottom=Gantt
        pane = ttk.PanedWindow(self._sched_frame, orient=tk.VERTICAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Comparison table
        table_frame = ttk.LabelFrame(pane, text="CPM vs RCPS Comparison")
        pane.add(table_frame, weight=1)

        cols = ("Activity", "Duration", "Resource",
                "CPM ES", "CPM EF", "CPM Float",
                "RCPS ES", "RCPS EF", "RCPS Float", "Delay")
        self._cmp_tree = ttk.Treeview(table_frame, columns=cols,
                                       show="headings", height=8)
        for c in cols:
            self._cmp_tree.heading(c, text=c)
            w = 70 if c != "Activity" else 100
            self._cmp_tree.column(c, width=w, anchor=tk.CENTER)
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                             command=self._cmp_tree.yview)
        self._cmp_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._cmp_tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Comparison Gantt chart
        gantt_frame = ttk.LabelFrame(pane, text="CPM vs RCPS Gantt")
        pane.add(gantt_frame, weight=1)

        if not HAS_MATPLOTLIB:
            ttk.Label(gantt_frame,
                      text="Matplotlib not installed — chart unavailable.").pack(expand=True)
        else:
            self._sched_fig = Figure(figsize=(8, 4), dpi=100)
            self._sched_ax = self._sched_fig.add_subplot(111)
            self._sched_canvas = FigureCanvasTkAgg(self._sched_fig, master=gantt_frame)
            self._sched_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Export bar
        exp_bar = ttk.Frame(self._sched_frame)
        exp_bar.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(exp_bar, text="Export Gantt PNG",
                   command=lambda: self._export_sched("png")).pack(side=tk.LEFT, padx=2)
        ttk.Button(exp_bar, text="Export Gantt PDF",
                   command=lambda: self._export_sched("pdf")).pack(side=tk.LEFT, padx=2)

    def _run_rcps(self):
        """Run RCPS scheduling and populate comparison table + Gantt."""
        if not self.main_window:
            messagebox.showinfo("RCPS", "Main window reference not available.")
            return
        if not self.main_window.current_data is not None:
            pass  # current_data could be a DataFrame
        if self.main_window.current_data is None:
            messagebox.showinfo("RCPS",
                                "No analysis data. Run ▶ Analyze first.")
            return
        if not HAS_PANDAS:
            messagebox.showerror("RCPS", "pandas is required for RCPS scheduling.")
            return

        df = self.main_window.current_data
        resource_limit = self._res_limit_var.get()
        priority_rule = self._priority_var.get()
        self._resource_limit = resource_limit

        # Validate resource limit
        if 'resource_demand' in df.columns:
            try:
                max_res = pd.to_numeric(df['resource_demand'], errors='coerce').max()
                if max_res is not None and resource_limit < max_res:
                    messagebox.showwarning(
                        "Resource Limit",
                        f"Resource limit ({resource_limit}) is less than the maximum "
                        f"per-activity resource demand ({max_res:.0f}).\n"
                        "Some activities may be infeasible.")
            except Exception:
                pass

        # Select analyzer
        analysis_mode = getattr(self.main_window, 'analysis_mode', 'deterministic')
        if analysis_mode == 'probabilistic' and self.main_window.pert_analyzer:
            analyzer = self.main_window.pert_analyzer
        else:
            analyzer = self.main_window.cpm_analyzer

        if analyzer is None:
            messagebox.showerror("RCPS", "No analyzer available. Run analysis first.")
            return

        self._status_var.set("Running RCPS...")
        self._run_btn.configure(state="disabled")

        try:
            cpm_table, _, _ = analyzer.build_cpm_schedule_table(df, resource_limit)
            rcps_table, _, _ = analyzer.rcps_heuristic_schedule_table(
                df, resource_limit, priority_rule=priority_rule)
        except Exception as exc:
            self._run_btn.configure(state="normal")
            self._status_var.set(f"Error: {exc}")
            messagebox.showerror("RCPS Error", str(exc))
            return

        # Store for downstream (crashing etc.)
        self._rcps_analyzer = analyzer
        self._rcps_table_data = rcps_table

        self._run_btn.configure(state="normal")

        # ---- Populate comparison table ----
        self._cmp_tree.delete(*self._cmp_tree.get_children())

        # Build lookup from CPM table
        cpm_lookup = {}
        for _, row in cpm_table.iterrows():
            aid = row.get('id', '')
            if aid and aid not in ('RA', 'RS'):
                cpm_lookup[aid] = row

        rcps_duration = 0
        cpm_duration = 0
        for _, row in rcps_table.iterrows():
            aid = row.get('id', '')
            if not aid or aid in ('RA', 'RS'):
                continue
            dur = row.get('duration', 0)
            res = row.get('resource_demand', row.get('resource', 0))
            rcps_es = row.get('actual_start', row.get('early_start', 0))
            rcps_ef = rcps_es + dur if dur else 0
            rcps_float = row.get('float', 0)

            cpm_row = cpm_lookup.get(aid, {})
            cpm_es = cpm_row.get('early_start', 0) if isinstance(cpm_row, dict) else getattr(cpm_row, 'get', lambda k, d=0: d)('early_start', 0)
            cpm_ef = cpm_row.get('early_finish', cpm_es + dur) if isinstance(cpm_row, dict) else getattr(cpm_row, 'get', lambda k, d=0: d)('early_finish', 0)
            cpm_flt = cpm_row.get('float', 0) if isinstance(cpm_row, dict) else getattr(cpm_row, 'get', lambda k, d=0: d)('float', 0)

            # For pandas Series
            if hasattr(cpm_row, 'get'):
                cpm_es = cpm_row.get('early_start', 0)
                cpm_ef = cpm_row.get('early_finish', cpm_es + dur)
                cpm_flt = cpm_row.get('float', 0)

            delay = max(0, rcps_es - cpm_es) if cpm_es else 0

            self._cmp_tree.insert("", tk.END, values=(
                aid, dur, res,
                cpm_es, cpm_ef, cpm_flt,
                rcps_es, rcps_ef, rcps_float, delay))

            rcps_duration = max(rcps_duration, rcps_ef)
            cpm_duration = max(cpm_duration, cpm_ef)

        self._status_var.set(
            f"Done — CPM Duration: {cpm_duration:.0f}, "
            f"RCPS Duration: {rcps_duration:.0f}, "
            f"Resource Limit: {resource_limit}")

        # ---- Draw comparison Gantt ----
        if HAS_MATPLOTLIB and hasattr(self, '_sched_ax'):
            self._draw_comparison_gantt(cpm_table, rcps_table, resource_limit)

    def _draw_comparison_gantt(self, cpm_table, rcps_table, resource_limit):
        """Draw side-by-side CPM vs RCPS Gantt chart."""
        import matplotlib.patches as mpatches

        ax = self._sched_ax
        ax.clear()

        # Collect activity IDs from RCPS table (skip RA/RS rows)
        activities = []
        for _, row in rcps_table.iterrows():
            aid = row.get('id', '')
            if aid and aid not in ('RA', 'RS'):
                activities.append(aid)

        if not activities:
            ax.text(0.5, 0.5, "No activities to display.",
                    ha='center', va='center', fontsize=11, color='grey',
                    transform=ax.transAxes)
            self._sched_fig.tight_layout()
            self._sched_canvas.draw()
            return

        # Build lookups
        cpm_lookup = {}
        for _, row in cpm_table.iterrows():
            aid = row.get('id', '')
            if aid and aid not in ('RA', 'RS'):
                cpm_lookup[aid] = row

        rcps_lookup = {}
        for _, row in rcps_table.iterrows():
            aid = row.get('id', '')
            if aid and aid not in ('RA', 'RS'):
                rcps_lookup[aid] = row

        bar_h = 0.35
        n = len(activities)

        for i, aid in enumerate(activities):
            y = n - 1 - i
            dur = 0

            # CPM bar (upper half)
            if aid in cpm_lookup:
                r = cpm_lookup[aid]
                es = r.get('early_start', 0)
                dur = r.get('duration', 0)
                ax.barh(y + bar_h / 2, dur, left=es, height=bar_h,
                        color='#3498db', edgecolor='white', linewidth=0.5,
                        alpha=0.7, zorder=2)

            # RCPS bar (lower half)
            if aid in rcps_lookup:
                r = rcps_lookup[aid]
                rcps_es = r.get('actual_start', r.get('early_start', 0))
                dur = r.get('duration', dur)
                ax.barh(y - bar_h / 2, dur, left=rcps_es, height=bar_h,
                        color='#e67e22', edgecolor='white', linewidth=0.5,
                        alpha=0.7, zorder=2)

        # Resource limit line (informational)
        ax.set_yticks(range(n))
        ax.set_yticklabels(list(reversed(activities)), fontsize=8)
        ax.set_xlabel("Time (periods)")
        ax.set_title(f"CPM vs RCPS (Resource Limit = {resource_limit})",
                     fontsize=10, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()

        patches = [
            mpatches.Patch(color='#3498db', alpha=0.7, label='CPM Schedule'),
            mpatches.Patch(color='#e67e22', alpha=0.7, label='RCPS Schedule'),
        ]
        ax.legend(handles=patches, loc='lower right', fontsize=8)

        self._sched_fig.tight_layout()
        self._sched_canvas.draw()

    def _export_sched(self, fmt):
        """Export the RCPS comparison Gantt."""
        if not hasattr(self, '_sched_fig'):
            return
        from tkinter import filedialog
        ext = f".{fmt}"
        filepath = filedialog.asksaveasfilename(
            title=f"Export RCPS Gantt as {fmt.upper()}",
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} files", f"*{ext}"), ("All files", "*.*")])
        if filepath:
            self._sched_fig.savefig(filepath, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Export", f"Saved to {filepath}")

    # ================================================================
    #  Histograms sub-tab
    # ================================================================

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
        if proj is None:
            return
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
        if HAS_MATPLOTLIB:
            if hasattr(self, "_sched_fig"):
                figs.append(("rcps_schedule", self._sched_fig))
            if hasattr(self, "_fig"):
                figs.append(("resource_histograms", self._fig))
        return figs

    def on_tab_selected(self):
        """Refresh histograms."""
        self._draw_histograms()

    # ----------------------------------------------------------------
    # RCPS Crashing compatibility stubs
    # ----------------------------------------------------------------

    def set_rcps_crashing_tab(self, rcps_crashing_tab):
        """Set reference to RCPS Crashing tab (bidirectional link)."""
        self._rcps_crashing_tab = rcps_crashing_tab

    def get_rcps_analyzer(self):
        """Return the current RCPS analyzer (if any)."""
        return self._rcps_analyzer

    def get_resource_limit(self):
        """Return the current resource limit."""
        return self._resource_limit

    def get_rcps_table_data(self):
        """Return the current RCPS table data for crashing analysis."""
        return self._rcps_table_data
