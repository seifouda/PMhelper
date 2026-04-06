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

        # Sub-tab 3: Resource Leveling walkthrough
        self._leveling_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._leveling_frame, text="Resource Leveling")
        self._leveling_result = None
        self._leveling_steps: list = []
        self._current_step_idx = 0
        self._build_leveling_tab()

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
        if 'resource' in df.columns:
            try:
                max_res = pd.to_numeric(df['resource'], errors='coerce').max()
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

    # ================================================================
    #  Resource Leveling sub-tab  (sub-tab 3)
    # ================================================================

    def _build_leveling_tab(self):
        """Build the Resource Leveling walkthrough UI."""
        outer = ttk.Frame(self._leveling_frame)
        outer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Controls row ──────────────────────────────────────────────
        ctrl = ttk.LabelFrame(outer, text="Leveling Settings")
        ctrl.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(ctrl, text="Method:").grid(row=0, column=0, padx=6, pady=4, sticky="e")
        self._lev_method_var = tk.StringVar(value="minimum_moment")
        ttk.Combobox(ctrl, textvariable=self._lev_method_var,
                     values=["minimum_moment", "burgess"],
                     state="readonly", width=16).grid(row=0, column=1, padx=4, pady=4, sticky="w")

        ttk.Label(ctrl, text="Mode:").grid(row=0, column=2, padx=(12, 6), pady=4, sticky="e")
        self._lev_mode_var = tk.StringVar(value="smoothing")
        ttk.Combobox(ctrl, textvariable=self._lev_mode_var,
                     values=["smoothing", "constrained"],
                     state="readonly", width=14).grid(row=0, column=3, padx=4, pady=4, sticky="w")

        ttk.Label(ctrl, text="Resource Limit:").grid(row=0, column=4, padx=(12, 6), pady=4, sticky="e")
        self._lev_limit_var = tk.IntVar(value=5)
        ttk.Spinbox(ctrl, from_=1, to=99, increment=1,
                    textvariable=self._lev_limit_var, width=5).grid(row=0, column=5, padx=4, pady=4, sticky="w")

        self._lev_run_btn = ttk.Button(ctrl, text="▶ Run Leveling",
                                       command=self._run_leveling)
        self._lev_run_btn.grid(row=0, column=6, padx=(16, 4), pady=4)

        ttk.Button(ctrl, text="📂 Load Demo",
                   command=self._load_leveling_demo).grid(row=0, column=7, padx=4, pady=4)

        ttk.Button(ctrl, text="📖 Worked Solution",
                   command=self._show_leveling_worked_solution).grid(row=0, column=8, padx=4, pady=4)

        self._lev_status_var = tk.StringVar(value="Ready — load a demo or run analysis first.")
        ttk.Label(ctrl, textvariable=self._lev_status_var,
                  foreground="grey").grid(row=1, column=0, columnspan=9,
                                          padx=6, pady=(0, 4), sticky="w")

        # ── Main paned: chart (top) + walkthrough (bottom) ───────────
        pane = ttk.PanedWindow(outer, orient=tk.VERTICAL)
        pane.pack(fill=tk.BOTH, expand=True)

        # ─ Before / After chart ──────────────────────────────────────
        chart_frm = ttk.LabelFrame(pane, text="Before / After Resource Profile")
        pane.add(chart_frm, weight=2)

        if not HAS_MATPLOTLIB:
            ttk.Label(chart_frm,
                      text="Matplotlib not installed — chart unavailable.").pack(expand=True)
        else:
            self._lev_fig = Figure(figsize=(8, 3), dpi=100)
            self._lev_ax_before = self._lev_fig.add_subplot(121)
            self._lev_ax_after = self._lev_fig.add_subplot(122)
            self._lev_canvas = FigureCanvasTkAgg(self._lev_fig, master=chart_frm)
            self._lev_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            self._lev_fig.text(0.5, 0.5, "Run Leveling to see chart",
                               ha="center", va="center", fontsize=12, color="grey")
            self._lev_canvas.draw()

        # ─ Metrics panel ─────────────────────────────────────────────
        metrics_frm = ttk.LabelFrame(pane, text="Leveling Metrics")
        pane.add(metrics_frm, weight=1)

        metrics_cols = ("Metric", "Before", "After", "Improvement")
        self._metrics_tree = ttk.Treeview(metrics_frm, columns=metrics_cols,
                                          show="headings", height=4)
        for col in metrics_cols:
            self._metrics_tree.heading(col, text=col)
            self._metrics_tree.column(col, width=150, anchor=tk.CENTER)
        self._metrics_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ─ Step walkthrough ──────────────────────────────────────────
        step_frm = ttk.LabelFrame(pane, text="Step-by-Step Walkthrough")
        pane.add(step_frm, weight=2)

        # Step list (left) + description (right)
        step_inner = ttk.Frame(step_frm)
        step_inner.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        list_frm = ttk.Frame(step_inner)
        list_frm.pack(side=tk.LEFT, fill=tk.Y)

        self._step_listbox = tk.Listbox(list_frm, width=36, activestyle="none",
                                        selectmode=tk.SINGLE)
        step_sb = ttk.Scrollbar(list_frm, orient=tk.VERTICAL,
                                command=self._step_listbox.yview)
        self._step_listbox.configure(yscrollcommand=step_sb.set)
        step_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._step_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._step_listbox.bind("<<ListboxSelect>>", self._on_step_select)

        nav_bar = ttk.Frame(list_frm)
        nav_bar.pack(fill=tk.X, pady=2)
        ttk.Button(nav_bar, text="◀ Prev",
                   command=self._prev_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_bar, text="Next ▶",
                   command=self._next_step).pack(side=tk.LEFT, padx=2)

        desc_frm = ttk.Frame(step_inner)
        desc_frm.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self._step_desc = tk.Text(desc_frm, wrap=tk.WORD, height=10,
                                  state="disabled", relief="flat",
                                  background="#f8f8f8", font=("Courier", 9))
        desc_sb = ttk.Scrollbar(desc_frm, orient=tk.VERTICAL,
                                command=self._step_desc.yview)
        self._step_desc.configure(yscrollcommand=desc_sb.set)
        desc_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._step_desc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ─ Try It Yourself panel ─────────────────────────────────────
        try_frm = ttk.LabelFrame(pane, text="Try It Yourself")
        pane.add(try_frm, weight=1)

        try_inner = ttk.Frame(try_frm)
        try_inner.pack(fill=tk.X, padx=6, pady=4)

        ttk.Label(try_inner,
                  text="Manually adjust start times for non-critical activities "
                       "and see whether the moment improves:").pack(anchor="w")

        self._try_table_frame = ttk.Frame(try_frm)
        self._try_table_frame.pack(fill=tk.X, padx=6, pady=2)

        try_btn_bar = ttk.Frame(try_frm)
        try_btn_bar.pack(fill=tk.X, padx=6, pady=(0, 4))
        ttk.Button(try_btn_bar, text="📐 Calculate Moment",
                   command=self._calculate_try_moment).pack(side=tk.LEFT, padx=2)
        ttk.Button(try_btn_bar, text="↺ Reset to Original",
                   command=self._reset_try_schedule).pack(side=tk.LEFT, padx=2)

        self._try_result_var = tk.StringVar(value="")
        ttk.Label(try_btn_bar, textvariable=self._try_result_var,
                  foreground="#2980b9").pack(side=tk.LEFT, padx=8)

        # Storage for Try It widgets
        self._try_spinboxes: dict = {}
        self._try_original: dict = {}

    # ── Internal helpers ─────────────────────────────────────────────

    def _run_leveling(self):
        """Run resource leveling on the current project data."""
        if not self.main_window:
            messagebox.showinfo("Resource Leveling",
                                "Main window reference not available.")
            return
        if self.main_window.current_data is None:
            messagebox.showinfo("Resource Leveling",
                                "No analysis data. Run ▶ Analyze first.")
            return

        analysis_mode = getattr(self.main_window, "analysis_mode", "deterministic")
        if analysis_mode == "probabilistic" and self.main_window.pert_analyzer:
            analyzer = self.main_window.pert_analyzer
        else:
            analyzer = self.main_window.cpm_analyzer

        if analyzer is None:
            messagebox.showerror("Resource Leveling",
                                 "No CPM/PERT analysis available. "
                                 "Run ▶ Analyze first.")
            return

        self._lev_run_btn.configure(state="disabled")
        self._lev_status_var.set("Running…")
        self.frame.update_idletasks()

        try:
            from pmhelper.core.resource_leveling import (
                activities_from_cpm, ResourceLevelingFactory,
            )

            activities = activities_from_cpm(analyzer)
            method = self._lev_method_var.get()
            mode = self._lev_mode_var.get()
            limit = self._lev_limit_var.get() if mode == "constrained" else None

            leveler = ResourceLevelingFactory.create(method, activities, limit)
            result = leveler.level(record_steps=True)

            self._leveling_result = result
            self._refresh_leveling_ui(activities)
            n_steps = len(result.get("steps", []))
            improv = result.get("improvement_pct", 0.0)
            self._lev_status_var.set(
                f"Done — {n_steps} move(s), {improv:.1f}% improvement "
                f"({method.replace('_', ' ').title()}, {mode})"
            )
        except Exception as exc:
            messagebox.showerror("Resource Leveling Error", str(exc))
            self._lev_status_var.set(f"Error: {exc}")
        finally:
            self._lev_run_btn.configure(state="normal")

    def _load_leveling_demo(self):
        """Load the built-in resource leveling demo project."""
        import json, os
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..", "data", "demos", "v2",
            "resource_leveling_demo.json",
        )
        demo_path = os.path.normpath(demo_path)
        if not os.path.exists(demo_path):
            # Try relative to workspace root
            here = os.path.dirname(os.path.abspath(__file__))
            for _ in range(6):
                candidate = os.path.join(here, "data", "demos", "v2",
                                         "resource_leveling_demo.json")
                if os.path.exists(candidate):
                    demo_path = candidate
                    break
                here = os.path.dirname(here)

        if not os.path.exists(demo_path):
            messagebox.showerror("Load Demo",
                                 f"Demo file not found.\nLooked in:\n{demo_path}")
            return

        try:
            with open(demo_path, "r") as f:
                data = json.load(f)

            from pmhelper.core.resource_leveling import (
                Activity, ResourceLevelingFactory,
            )

            activities = []
            for a in data["activities"]:
                activities.append(Activity(
                    id=a["id"],
                    duration=a["duration"],
                    resource_demand=a["resource_demand"],
                    es=a["es"],
                    ef=a["ef"],
                    ls=a["ls"],
                    lf=a["lf"],
                    float=a["float"],
                    predecessors=a.get("predecessors", []),
                    successors=a.get("successors", []),
                ))

            method = self._lev_method_var.get()
            mode = self._lev_mode_var.get()
            limit = data.get("resource_limit") if mode == "constrained" else None

            leveler = ResourceLevelingFactory.create(method, activities, limit)
            result = leveler.level(record_steps=True)

            self._leveling_result = result
            self._refresh_leveling_ui(activities)
            n_steps = len(result.get("steps", []))
            improv = result.get("improvement_pct", 0.0)
            self._lev_status_var.set(
                f"Demo loaded — {n_steps} move(s), {improv:.1f}% improvement "
                f"({method.replace('_', ' ').title()}, {mode})"
            )
        except Exception as exc:
            messagebox.showerror("Load Demo Error", str(exc))

    def _refresh_leveling_ui(self, activities):
        """Refresh chart, metrics, steps, and Try It Yourself after a run."""
        result = self._leveling_result
        if result is None:
            return

        self._draw_leveling_chart(result)
        self._refresh_metrics_table(result)
        self._build_step_walkthrough(result)
        self._build_try_it_panel(activities, result)

    def _draw_leveling_chart(self, result):
        """Draw before/after resource profile histograms."""
        if not HAS_MATPLOTLIB:
            return

        orig_prof = result.get("original_profile")
        lev_prof = result.get("leveled_profile")
        if orig_prof is None or lev_prof is None:
            return

        periods_orig = sorted(orig_prof.profile.keys())
        periods_lev = sorted(lev_prof.profile.keys())

        # ── Before ────────────────────────────────────────────────────
        ax1 = self._lev_ax_before
        ax1.clear()
        ax1.bar(periods_orig,
                [orig_prof.profile[t] for t in periods_orig],
                color="#e74c3c", alpha=0.8, label="Before")
        peak_orig = orig_prof.get_peak_usage()
        ax1.axhline(peak_orig, color="#c0392b", linestyle="--",
                    linewidth=1, label=f"Peak = {peak_orig:.1f}")
        ax1.set_title("Before Leveling", fontsize=9, fontweight="bold")
        ax1.set_xlabel("Period", fontsize=8)
        ax1.set_ylabel("Resources", fontsize=8)
        ax1.legend(fontsize=7)
        ax1.tick_params(labelsize=7)

        # ── After ─────────────────────────────────────────────────────
        ax2 = self._lev_ax_after
        ax2.clear()
        ax2.bar(periods_lev,
                [lev_prof.profile[t] for t in periods_lev],
                color="#2ecc71", alpha=0.8, label="After")
        peak_lev = lev_prof.get_peak_usage()
        ax2.axhline(peak_lev, color="#27ae60", linestyle="--",
                    linewidth=1, label=f"Peak = {peak_lev:.1f}")
        ax2.set_title("After Leveling", fontsize=9, fontweight="bold")
        ax2.set_xlabel("Period", fontsize=8)
        ax2.set_ylabel("Resources", fontsize=8)
        ax2.legend(fontsize=7)
        ax2.tick_params(labelsize=7)

        self._lev_fig.tight_layout()
        self._lev_canvas.draw()

    def _refresh_metrics_table(self, result):
        """Populate the metrics comparison tree."""
        self._metrics_tree.delete(*self._metrics_tree.get_children())

        peak_b = result.get("peak_usage_original", 0.0)
        peak_a = result.get("peak_usage_leveled", 0.0)
        peak_delta = (peak_b - peak_a) / peak_b * 100 if peak_b > 0 else 0.0

        moment_b = result.get("original_moment", result.get("original_cost", 0.0))
        moment_a = result.get("leveled_moment", result.get("leveled_cost", 0.0))
        improv = result.get("improvement_pct", 0.0)

        feasible = result.get("feasible", True)

        rows = [
            ("Peak Usage",
             f"{peak_b:.2f}", f"{peak_a:.2f}",
             f"{peak_delta:.1f}% ↓" if peak_delta > 0 else "—"),
            ("Smoothness Metric",
             f"{moment_b:.2f}", f"{moment_a:.2f}",
             f"{improv:.1f}% ↓" if improv > 0 else "—"),
            ("Feasible?",
             "—", "Yes" if feasible else "No", "—"),
            ("Moves Made",
             "—", str(len(result.get("steps", []))), "—"),
        ]
        for row in rows:
            self._metrics_tree.insert("", tk.END, values=row)

    def _build_step_walkthrough(self, result):
        """Populate the step listbox from recorded LevelingStep objects."""
        self._step_listbox.delete(0, tk.END)
        self._leveling_steps = result.get("steps", [])

        if not self._leveling_steps:
            self._step_listbox.insert(tk.END, "(no moves — already optimal)")
            self._set_step_description(
                "No activity moves were made.\n\n"
                "Either every activity is on the critical path (no float) "
                "or the early-start schedule is already at minimum moment."
            )
            return

        for step in self._leveling_steps:
            label = (f"Move {step.step_number}: {step.activity_id}  "
                     f"day {step.from_start}→{step.to_start}  "
                     f"Δ={step.metric_after - step.metric_before:+.1f}")
            self._step_listbox.insert(tk.END, label)

        self._current_step_idx = 0
        self._step_listbox.selection_set(0)
        self._show_leveling_step(0)

    def _show_leveling_step(self, idx: int):
        """Display step detail in the description pane."""
        if not self._leveling_steps or idx >= len(self._leveling_steps):
            return
        step = self._leveling_steps[idx]
        lines = [
            f"Step {step.step_number} of {len(self._leveling_steps)}",
            f"{'─' * 40}",
            f"Activity : {step.activity_id}",
            f"Moved    : day {step.from_start}  →  day {step.to_start}",
            f"Metric (before): {step.metric_before:.4f}",
            f"Metric (after) : {step.metric_after:.4f}",
            f"Change         : {step.metric_after - step.metric_before:+.4f}",
            "",
            "Reason:",
            f"  {step.reason}",
            "",
            "Resource profile after this move:",
        ]
        if step.profile:
            for t in sorted(step.profile.keys()):
                lines.append(f"  Period {t:3d}: {'█' * int(step.profile[t])}  {step.profile[t]:.1f}")
        self._set_step_description("\n".join(lines))

    def _set_step_description(self, text: str):
        self._step_desc.configure(state="normal")
        self._step_desc.delete("1.0", tk.END)
        self._step_desc.insert(tk.END, text)
        self._step_desc.configure(state="disabled")

    def _on_step_select(self, _event=None):
        sel = self._step_listbox.curselection()
        if sel:
            self._current_step_idx = sel[0]
            self._show_leveling_step(self._current_step_idx)

    def _prev_step(self):
        if self._leveling_steps and self._current_step_idx > 0:
            self._current_step_idx -= 1
            self._step_listbox.selection_clear(0, tk.END)
            self._step_listbox.selection_set(self._current_step_idx)
            self._step_listbox.see(self._current_step_idx)
            self._show_leveling_step(self._current_step_idx)

    def _next_step(self):
        if self._leveling_steps and \
                self._current_step_idx < len(self._leveling_steps) - 1:
            self._current_step_idx += 1
            self._step_listbox.selection_clear(0, tk.END)
            self._step_listbox.selection_set(self._current_step_idx)
            self._step_listbox.see(self._current_step_idx)
            self._show_leveling_step(self._current_step_idx)

    def _build_try_it_panel(self, activities, result):
        """Build editable start-time spinboxes for non-critical activities."""
        for w in self._try_table_frame.winfo_children():
            w.destroy()
        self._try_spinboxes.clear()
        self._try_original.clear()

        original_schedule = result.get("original_schedule", {})
        non_critical = [a for a in activities if getattr(a, "float", 0) > 0]

        if not non_critical:
            ttk.Label(self._try_table_frame,
                      text="All activities are critical — nothing to adjust.").pack()
            return

        hdr = ttk.Frame(self._try_table_frame)
        hdr.pack(fill=tk.X)
        for i, h in enumerate(("Activity", "Float", "ES", "LS",
                                "Res", "Start Time (adjust)")):
            ttk.Label(hdr, text=h, font=("TkDefaultFont", 9, "bold"),
                      width=14, anchor="center").grid(row=0, column=i, padx=2)

        for row_idx, act in enumerate(non_critical, start=1):
            row_f = ttk.Frame(self._try_table_frame)
            row_f.pack(fill=tk.X)
            current_start = original_schedule.get(act.id, act.es)
            self._try_original[act.id] = current_start

            var = tk.IntVar(value=current_start)
            self._try_spinboxes[act.id] = var

            for col_idx, val in enumerate([
                act.id, act.float, act.es, act.ls, act.resource_demand,
            ]):
                ttk.Label(row_f, text=str(val), width=14,
                          anchor="center").grid(row=0, column=col_idx, padx=2)

            ttk.Spinbox(row_f, from_=act.es, to=act.ls, increment=1,
                        textvariable=var, width=8).grid(row=0, column=5, padx=2, pady=1)

        self._try_activities = activities
        self._try_result_var.set("")

    def _calculate_try_moment(self):
        """Calculate moment for the user-edited start times."""
        if not self._leveling_result or not hasattr(self, "_try_activities"):
            messagebox.showinfo("Try It", "Run leveling or load a demo first.")
            return

        try:
            from pmhelper.core.resource_leveling import ResourceProfile

            activities = self._try_activities
            orig_schedule = self._leveling_result.get("original_schedule", {})

            user_schedule = dict(orig_schedule)
            for act_id, var in self._try_spinboxes.items():
                user_schedule[act_id] = var.get()

            user_profile = ResourceProfile(user_schedule, activities)
            user_moment = user_profile.calculate_moment()
            orig_profile = self._leveling_result.get("original_profile")
            orig_moment = self._leveling_result.get(
                "original_moment",
                self._leveling_result.get("original_cost", 0.0),
            )
            user_peak = user_profile.get_peak_usage()
            improv = (orig_moment - user_moment) / orig_moment * 100 if orig_moment > 0 else 0
            sign = "↓" if improv > 0 else ("↑" if improv < 0 else "=")
            self._try_result_var.set(
                f"Moment = {user_moment:.2f}  "
                f"(original = {orig_moment:.2f}, {sign} {abs(improv):.1f}%),  "
                f"Peak = {user_peak:.1f}"
            )
        except Exception as exc:
            self._try_result_var.set(f"Error: {exc}")

    def _reset_try_schedule(self):
        """Reset all spinboxes to the original early-start schedule."""
        for act_id, var in self._try_spinboxes.items():
            var.set(self._try_original.get(act_id, 0))
        self._try_result_var.set("Reset to original schedule.")

    def _show_leveling_worked_solution(self):
        """Open a WorkedSolutionWindow for the last leveling run."""
        if self._leveling_result is None:
            messagebox.showinfo("Worked Solution",
                                "Run leveling or load a demo first.")
            return

        try:
            from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
            from pmhelper.core.leveling_step_generator import (
                leveling_concepts_steps,
                minimum_moment_algorithm_steps,
                burgess_algorithm_steps,
                before_after_comparison_steps,
            )

            method = self._lev_method_var.get()
            if method == "burgess":
                algo_steps = burgess_algorithm_steps(self._leveling_result)
                method_label = "Burgess"
            else:
                algo_steps = minimum_moment_algorithm_steps(self._leveling_result)
                method_label = "Minimum Moment"

            all_steps = (
                leveling_concepts_steps()
                + algo_steps
                + before_after_comparison_steps(self._leveling_result)
            )
            title = f"Resource Leveling — {method_label} Worked Solution"
            WorkedSolutionWindow(self.frame, title, all_steps)
        except Exception as exc:
            messagebox.showerror("Worked Solution Error", str(exc))

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
