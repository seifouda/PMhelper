"""PMhelper Edu — Gantt Chart Tab with Tracking Gantt.
Baseline bars, % complete shading, status colouring.
Predecessor arrows, today-line, project start date, enhanced visuals.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.patches as mpatches
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# Colour scheme
_COLOURS = {
    "current": "#3498db",
    "baseline": "#bdc3c7",
    "progress": "#2ecc71",
    "behind_amber": "#f39c12",
    "behind_red": "#e74c3c",
}


def _evm_to_gantt_coords(evm_task, cpm_results=None):
    """Translate EVMTask period indices to Gantt x-coordinates.

    If cpm_results contains a matching task (by cpm_task_id), use its ES/EF.
    Otherwise fall back to EVMTask.planned_start / planned_finish.
    """
    if cpm_results and evm_task.cpm_task_id:
        for item in cpm_results:
            cpm_id = item.get("id") or item.get("task_id")
            if cpm_id == evm_task.cpm_task_id:
                return float(item.get("ES", evm_task.planned_start)), \
                       float(item.get("EF", evm_task.planned_finish))
    return float(evm_task.planned_start), float(evm_task.planned_finish)


class GanttTabEdu:
    """Gantt Chart with Tracking Gantt mode."""

    def __init__(self, parent, state, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        self._tracking_mode = tk.BooleanVar(value=False)
        self._show_arrows = tk.BooleanVar(value=True)
        self._show_today = tk.BooleanVar(value=False)
        self._results_data = None
        self._analysis_mode = None

        if not HAS_MATPLOTLIB:
            ttk.Label(self.frame,
                      text="Matplotlib not installed — Gantt chart unavailable.").pack(
                expand=True)
            return

        # Toolbar row 1: existing buttons
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))
        self._baseline_btn = ttk.Button(toolbar, text="Set Baseline",
                                        command=self._toggle_baseline)
        self._baseline_btn.pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(toolbar, text="Tracking Gantt",
                        variable=self._tracking_mode,
                        command=self._draw_gantt).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(toolbar, text="Arrows",
                        variable=self._show_arrows,
                        command=self._draw_gantt).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(toolbar, text="Today Line",
                        variable=self._show_today,
                        command=self._draw_gantt).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Refresh", command=self._draw_gantt).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export PNG",
                   command=lambda: self._export("png")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export PDF",
                   command=lambda: self._export("pdf")).pack(side=tk.LEFT, padx=2)

        # Toolbar row 2: project start date
        toolbar2 = ttk.Frame(self.frame)
        toolbar2.pack(fill=tk.X, padx=5, pady=(2, 2))
        ttk.Label(toolbar2, text="Project Start:").pack(side=tk.LEFT, padx=(0, 4))
        self._start_date_var = tk.StringVar(value="")
        self._start_date_entry = ttk.Entry(toolbar2, textvariable=self._start_date_var, width=12)
        self._start_date_entry.pack(side=tk.LEFT, padx=(0, 4))
        ttk.Label(toolbar2, text="(YYYY-MM-DD)", foreground="grey").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar2, text="Apply Dates", command=self._draw_gantt).pack(side=tk.LEFT, padx=2)

        # Chart
        self._fig = Figure(figsize=(8, 5), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(self._fig, master=self.frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._baseline_set = False

    # ----------------------------------------------------------------
    # Baseline management
    # ----------------------------------------------------------------

    def _toggle_baseline(self):
        tasks = self.state.evm_project.tasks
        if not tasks:
            messagebox.showinfo("Baseline", "No EVM tasks to set baseline for.")
            return
        if not self._baseline_set:
            for t in tasks:
                t.baseline_start = t.planned_start
                t.baseline_finish = t.planned_finish
            self._baseline_set = True
            self._baseline_btn.configure(text="Reset Baseline")
            messagebox.showinfo("Baseline",
                                f"Baseline set for {len(tasks)} tasks.\n"
                                f"Use 'Reset Baseline' to undo.")
        else:
            if messagebox.askyesno("Reset Baseline",
                                  "Clear baseline data for all tasks?"):
                for t in tasks:
                    t.baseline_start = None
                    t.baseline_finish = None
                self._baseline_set = False
                self._baseline_btn.configure(text="Set Baseline")
        self.state.mark_dirty()
        self._draw_gantt()

    # ----------------------------------------------------------------
    # Gantt drawing
    # ----------------------------------------------------------------

    def _draw_gantt(self):
        if not HAS_MATPLOTLIB:
            return
        ax = self._ax
        ax.clear()

        tracking = self._tracking_mode.get()

        # If CPM analysis results are available, draw CPM-based Gantt
        if self._results_data and 'activities' in self._results_data:
            self._draw_cpm_gantt(ax, tracking)
        else:
            # Fall back to EVM task data
            self._draw_evm_gantt(ax, tracking)

        self._fig.subplots_adjust(left=0.22, right=0.96, top=0.92, bottom=0.12)
        self._canvas.draw()

    def _draw_cpm_gantt(self, ax, tracking):
        """Draw Gantt chart from CPM/PERT analysis results."""
        activities = self._results_data['activities']
        if not activities:
            ax.text(0.5, 0.5, "No activities in analysis results.",
                    ha="center", va="center", fontsize=12, color="grey",
                    transform=ax.transAxes)
            return

        bar_height = 0.4
        critical_activities = self._results_data.get(
            'critical_activities', [])

        # Build name→y-index map for arrows
        id_to_y = {}
        id_to_ef = {}

        for i, act in enumerate(activities):
            y = len(activities) - 1 - i
            act_id = act.get('id', '')
            es = float(act.get('ES', 0))
            ef = float(act.get('EF', 0))
            lf = float(act.get('LF', 0))
            duration = ef - es
            if duration <= 0:
                duration = 0.5
            is_critical = act.get('critical', False)

            id_to_y[act_id] = y
            id_to_ef[act_id] = ef

            # Main bar (critical=red, normal=steelblue)
            colour = '#e74c3c' if is_critical else '#3498db'
            ax.barh(y, duration, left=es, height=bar_height,
                    color=colour, edgecolor='white',
                    linewidth=0.5, zorder=2)

            # Float/slack bar (grey, from EF to LF)
            slack = lf - ef
            if slack > 0:
                ax.barh(y, slack, left=ef, height=bar_height * 0.6,
                        color='#bdc3c7', edgecolor='white',
                        linewidth=0.5, alpha=0.5, zorder=1)

            # Duration label inside bar
            if duration >= 1.5:
                ax.text(es + duration / 2, y, f"{duration:.0f}",
                        ha='center', va='center', fontsize=7,
                        color='white', fontweight='bold', zorder=4)

            # Tracking overlay: match CPM activity to EVM task
            if tracking:
                evm_task = self._find_evm_task(act_id)
                if evm_task and evm_task.pct_complete > 0:
                    progress_dur = duration * evm_task.pct_complete / 100.0
                    ax.barh(y, progress_dur, left=es,
                            height=bar_height,
                            color=_COLOURS["progress"],
                            edgecolor='none', zorder=3, alpha=0.7)

        # Predecessor arrows
        if self._show_arrows.get():
            self._draw_predecessor_arrows(ax, activities, id_to_y, id_to_ef, bar_height)

        # Today line
        if self._show_today.get():
            project_duration = self._results_data.get('project_duration', 0)
            if project_duration > 0:
                # Use EVM current period as "today", fallback to 40% of project
                current_period = 0
                if self.state.evm_project and self.state.evm_project.periods:
                    current_period = len(self.state.evm_project.periods)
                if current_period <= 0:
                    current_period = project_duration * 0.4
                ax.axvline(current_period, color='#9b59b6', linewidth=2,
                           linestyle='-.', zorder=5, alpha=0.8)
                ax.text(current_period, len(activities) - 0.3,
                        f" Today (t={current_period})",
                        fontsize=7, color='#9b59b6', va='bottom')

        # Horizontal grid lines
        ax.set_axisbelow(True)
        ax.xaxis.grid(True, linestyle='--', alpha=0.3)
        for y_pos in range(len(activities)):
            ax.axhline(y=y_pos, color='#ecf0f1', linewidth=0.5, zorder=0)

        # Alternating row background
        for i in range(len(activities)):
            if i % 2 == 0:
                ax.axhspan(i - 0.5, i + 0.5, color='#f8f9fa', zorder=0, alpha=0.5)

        # Labels and formatting
        task_names = []
        for a in activities:
            name = a.get('name', a.get('id', ''))
            # Truncate long names
            if len(str(name)) > 20:
                name = str(name)[:18] + '…'
            task_names.append(name)
        y_ticks = list(range(len(activities) - 1, -1, -1))
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(task_names, fontsize=8)
        ax.set_xlabel("Time (periods)", fontsize=10)
        title = "Gantt Chart (CPM Analysis)"
        if tracking:
            title += " + Tracking"
        ax.set_title(title, fontsize=11, fontweight="bold")

        # Legend
        patches = [
            mpatches.Patch(color='#e74c3c', label='Critical'),
            mpatches.Patch(color='#3498db', label='Non-critical'),
            mpatches.Patch(color='#bdc3c7', alpha=0.5, label='Float/Slack'),
        ]
        if tracking:
            patches.append(
                mpatches.Patch(color=_COLOURS["progress"],
                               alpha=0.7, label='Progress'))
        if self._show_today.get():
            import matplotlib.lines as mlines
            patches.append(mlines.Line2D([], [], color='#9b59b6',
                                          linestyle='-.', label='Today'))
        ax.legend(handles=patches, loc='lower right', fontsize=7)

    def _draw_predecessor_arrows(self, ax, activities, id_to_y, id_to_ef, bar_height):
        """Draw dependency arrows from predecessor EF to successor ES."""
        for act in activities:
            act_id = act.get('id', '')
            es = float(act.get('ES', 0))
            preds_str = act.get('predecessors', '')
            if not preds_str or act_id not in id_to_y:
                continue
            # Parse predecessors (comma-separated)
            preds = [p.strip() for p in str(preds_str).split(',') if p.strip()]
            y_succ = id_to_y[act_id]
            for pred_id in preds:
                if pred_id in id_to_y and pred_id in id_to_ef:
                    y_pred = id_to_y[pred_id]
                    x_pred_ef = id_to_ef[pred_id]
                    ax.annotate(
                        '', xy=(es, y_succ),
                        xytext=(x_pred_ef, y_pred),
                        arrowprops=dict(
                            arrowstyle='->', color='#7f8c8d',
                            connectionstyle='arc3,rad=0.15',
                            linewidth=1.0, alpha=0.6),
                        zorder=1)

    def _draw_evm_gantt(self, ax, tracking):
        """Draw Gantt chart from EVM task data (no CPM results)."""
        tasks = self.state.evm_project.tasks
        if not tasks:
            ax.text(0.5, 0.5,
                    "No data to display.\n"
                    "Load activities and click \u25b6 Analyze,\n"
                    "or add EVM tasks in the Input tab.",
                    ha="center", va="center", fontsize=12, color="grey",
                    transform=ax.transAxes)
            self._canvas.draw()
            return

        bar_height = 0.4

        for i, task in enumerate(tasks):
            y = len(tasks) - 1 - i
            start = float(task.planned_start)
            finish = float(task.planned_finish)
            duration = finish - start
            if duration <= 0:
                duration = 0.5

            # Baseline bar (behind)
            if tracking and task.baseline_start is not None \
                    and task.baseline_finish is not None:
                bs = float(task.baseline_start)
                bf = float(task.baseline_finish)
                ax.barh(y, bf - bs, left=bs, height=bar_height * 1.4,
                        color=_COLOURS["baseline"], edgecolor="#999",
                        linewidth=0.5, alpha=0.5, zorder=1)

            # Current plan bar
            ax.barh(y, duration, left=start, height=bar_height,
                    color=_COLOURS["current"], edgecolor="white",
                    linewidth=0.5, zorder=2)

            # Progress fill
            if tracking and task.pct_complete > 0:
                progress_dur = duration * task.pct_complete / 100.0
                if task.baseline_finish is not None:
                    slip = finish - task.baseline_finish
                    if slip <= 0:
                        colour = _COLOURS["progress"]
                    elif slip <= 1:
                        colour = _COLOURS["behind_amber"]
                    else:
                        colour = _COLOURS["behind_red"]
                else:
                    colour = _COLOURS["progress"]
                ax.barh(y, progress_dur, left=start, height=bar_height,
                        color=colour, edgecolor="none", zorder=3)

        # Labels
        task_names = [t.name for t in tasks]
        y_ticks = list(range(len(tasks) - 1, -1, -1))
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(task_names, fontsize=8)
        ax.set_xlabel("Period", fontsize=10)
        title = "Tracking Gantt" if tracking else "Gantt Chart"
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.invert_yaxis()

        if tracking:
            patches = [
                mpatches.Patch(color=_COLOURS["baseline"], label="Baseline"),
                mpatches.Patch(color=_COLOURS["current"], label="Current Plan"),
                mpatches.Patch(color=_COLOURS["progress"], label="On Schedule"),
                mpatches.Patch(color=_COLOURS["behind_amber"],
                               label="Slight Delay"),
                mpatches.Patch(color=_COLOURS["behind_red"],
                               label="Significant Delay"),
            ]
            ax.legend(handles=patches, loc="lower right", fontsize=7)

    def _find_evm_task(self, activity_id):
        """Find matching EVM task by cpm_task_id or task_id."""
        if not activity_id:
            return None
        for t in self.state.evm_project.tasks:
            if t.cpm_task_id == activity_id or t.task_id == activity_id:
                return t
        return None

    def update_from_analysis(self, results_data, analysis_mode):
        """Update Gantt with CPM/PERT analysis results."""
        self._results_data = results_data
        self._analysis_mode = analysis_mode
        self._draw_gantt()

    def _export(self, fmt):
        from tkinter import filedialog
        ext = f".{fmt}"
        filepath = filedialog.asksaveasfilename(
            title=f"Export Gantt as {fmt.upper()}",
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} files", f"*{ext}"), ("All files", "*.*")])
        if filepath:
            self._fig.savefig(filepath, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Export", f"Saved to {filepath}")

    # ----------------------------------------------------------------
    # Public interface
    # ----------------------------------------------------------------

    def set_mode(self, mode: str):
        """Show/hide tracking controls based on mode."""
        self._mode = mode

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB and hasattr(self, "_fig"):
            figs.append(("gantt", self._fig))
        return figs

    def on_tab_selected(self):
        """Refresh chart when tab is selected."""
        self._draw_gantt()
