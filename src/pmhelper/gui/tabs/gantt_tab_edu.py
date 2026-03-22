"""PMhelper Edu — Gantt Chart Tab with Tracking Gantt.
Baseline bars, % complete shading, status colouring.
Predecessor arrows, today-line, project start date, enhanced visuals.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from pmhelper.core.step_generators_edu import cpm_forward_steps, cpm_backward_steps
from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
from pmhelper.gui.widgets.scrollable_mpl_frame import ScrollableMatplotlibFrame

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

        # Control frame row 1: chart options
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))

        options_frame = ttk.LabelFrame(
            control_frame,
            text="Professional Gantt Chart Options",
            padding="5")
        options_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        self._baseline_btn = ttk.Button(options_frame, text="Set Baseline",
                                        command=self._toggle_baseline)
        self._baseline_btn.pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(options_frame, text="Tracking Gantt",
                        variable=self._tracking_mode,
                        command=self._draw_gantt).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(options_frame, text="Show Predecessor Arrows",
                        variable=self._show_arrows,
                        command=self._draw_gantt).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(options_frame, text="Show Today Line",
                        variable=self._show_today,
                        command=self._draw_gantt).pack(side=tk.LEFT, padx=4)

        # Date settings frame
        date_frame = ttk.LabelFrame(
            control_frame, text="Project Dates", padding="5")
        date_frame.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(date_frame, text="Start Date:").pack(side=tk.LEFT, padx=(0, 5))
        self._start_date_var = tk.StringVar(value="")
        self._start_date_entry = ttk.Entry(date_frame, textvariable=self._start_date_var, width=12)
        self._start_date_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(date_frame, text="Update",
                   command=self._draw_gantt).pack(side=tk.LEFT, padx=5)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Save Chart",
                   command=lambda: self._export("png")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Data",
                   command=self._export_data).pack(side=tk.LEFT, padx=5)

        # Toolbar row 2: CPM Worked Solution buttons
        toolbar2 = ttk.Frame(self.frame)
        toolbar2.pack(fill=tk.X, padx=5, pady=(2, 2))
        ttk.Button(toolbar2, text="Refresh", command=self._draw_gantt).pack(
            side=tk.LEFT, padx=2)

        # CPM Worked Solution buttons (UG only)
        self._cpm_fwd_btn = ttk.Button(
            toolbar2, text="\U0001f4dd Forward Pass",
            command=self._show_cpm_forward)
        self._cpm_fwd_btn.pack(side=tk.RIGHT, padx=2)
        self._cpm_bwd_btn = ttk.Button(
            toolbar2, text="\U0001f4dd Backward Pass",
            command=self._show_cpm_backward)
        self._cpm_bwd_btn.pack(side=tk.RIGHT, padx=2)

        # Chart — scrollable professional Gantt
        self._scroll_frame = ScrollableMatplotlibFrame(
            self.frame, figsize=(14, 8), dpi=100, toolbar=True)
        self._scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._fig = self._scroll_frame.figure
        self._ax = self._fig.add_subplot(111)
        self._canvas = self._scroll_frame.canvas
        self._toolbar = self._scroll_frame.toolbar

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

        # Adaptive margins: shrink left margin for wider figures
        n_acts = len(self._results_data.get('activities', [])) if self._results_data else 0
        left_margin = 0.22 if n_acts <= 50 else max(0.06, min(0.22, 3.0 / max(1, self._fig.get_figwidth())))
        self._fig.subplots_adjust(left=left_margin, right=0.96, top=0.95, bottom=0.06)
        self._canvas.draw()

    def _draw_cpm_gantt(self, ax, tracking):
        """Draw Gantt chart from CPM/PERT analysis results (professional style)."""
        activities = self._results_data['activities']
        if not activities:
            ax.text(0.5, 0.5, "No activities in analysis results.",
                    ha="center", va="center", fontsize=12, color="grey",
                    transform=ax.transAxes)
            return

        import numpy as np

        # Adaptive figure sizing for large projects
        n = len(activities)
        max_lf = max(float(a.get('LF', 0)) for a in activities) if activities else 10

        # Always fit to viewport so the full chart is visible on screen.
        self._scroll_frame.fit_to_viewport()

        bar_height = 0.6
        label_fs = 10 if n <= 50 else (8 if n <= 200 else 6)
        critical_activities = self._results_data.get(
            'critical_activities', [])
        critical_color = 'red'
        normal_color = 'lightblue'
        slack_color = 'lightgrey'

        # Build name→y-index map for arrows
        id_to_y = {}
        id_to_ef = {}
        y_pos = np.arange(len(activities))[::-1]
        activity_labels = []

        for i, act in enumerate(activities):
            y = y_pos[i]
            act_id = act.get('id', '')
            es = float(act.get('ES', 0))
            ef = float(act.get('EF', 0))
            lf = float(act.get('LF', 0))
            duration = ef - es
            if duration <= 0:
                duration = 0.5
            is_critical = act.get('critical', False)
            float_time = max(0, lf - ef)

            id_to_y[act_id] = y
            id_to_ef[act_id] = ef
            activity_labels.append(act_id)

            # Main bar (critical=red, normal=lightblue) — professional style
            bar_color = critical_color if is_critical else normal_color
            ax.barh(y, duration, left=es, height=bar_height,
                    color=bar_color, alpha=0.7, edgecolor='black',
                    linewidth=0.8, zorder=2)

            # Float/slack bar (dashed edge, full height) — matching original
            if not is_critical and float_time > 0:
                ax.barh(y, float_time, left=ef, height=bar_height,
                        color=slack_color, alpha=0.5,
                        edgecolor='gray', linewidth=0.5,
                        linestyle='--', zorder=1)

            # Activity ID centered ON bar — matching original
            bar_center_x = es + duration / 2
            ax.text(bar_center_x, y, act_id,
                    ha='center', va='center', fontsize=label_fs,
                    fontweight='bold', zorder=4)

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
            # Parse project start date from UI
            try:
                project_start = datetime.strptime(
                    self._start_date_var.get(), "%Y-%m-%d")
            except Exception:
                project_start = datetime.now()
            today = datetime.now()
            today_position = (today - project_start).days
            if today_position < 0:
                today_position = 0
            max_lf = max(float(a.get('LF', 0)) for a in activities) if activities else 0
            if today_position > max_lf:
                today_position = max_lf
            ax.axvline(x=today_position, color='green', linestyle='-',
                       linewidth=2, alpha=0.8, zorder=5)

        # Professional grid
        ax.set_axisbelow(True)
        ax.grid(True, axis='x', alpha=0.3)
        for y_val in range(len(activities)):
            ax.axhline(y=y_val, color='#ecf0f1', linewidth=0.5, zorder=0)

        # Alternating row background (edu enhancement)
        for i in range(len(activities)):
            if i % 2 == 0:
                ax.axhspan(i - 0.5, i + 0.5, color='#f8f9fa', zorder=0, alpha=0.5)

        # Y-axis: activity IDs (matching original professional style)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(activity_labels, fontsize=label_fs, fontweight='bold')
        ax.set_xlabel('Time Units', fontsize=12, fontweight='bold', color='darkgreen')
        ax.set_ylabel('Activities', fontsize=12, fontweight='bold', color='darkgreen')
        title = "Project Gantt Chart"
        if tracking:
            title += " + Tracking"
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        # Set proper axis limits
        if activities:
            max_lf = max(float(a.get('LF', 0)) for a in activities)
            ax.set_xlim(-0.5, max_lf + 0.5)
            ax.set_ylim(-0.5, len(activities) - 0.5)

        # Legend — matching original style
        legend_elements = [
            mpatches.Patch(color='red', alpha=0.7, label='Critical Activities'),
            mpatches.Patch(color='lightblue', alpha=0.7, label='Non-Critical Activities'),
            mpatches.Patch(color='lightgrey', alpha=0.5, label='Available Slack/Float'),
        ]
        if tracking:
            legend_elements.append(
                mpatches.Patch(color=_COLOURS["progress"],
                               alpha=0.7, label='Progress'))
        if self._show_today.get():
            import matplotlib.lines as mlines
            legend_elements.append(
                mlines.Line2D([0], [0], color='green',
                              linewidth=2, label='Today'))
        ax.legend(handles=legend_elements, loc='lower left')

    def _draw_predecessor_arrows(self, ax, activities, id_to_y, id_to_ef, bar_height):
        """Draw dependency arrows from predecessor EF to successor ES (professional style)."""
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
                    # Offset slightly from bar edges for clarity
                    from_x = x_pred_ef + 0.1
                    to_x = es - 0.1
                    if abs(to_x - from_x) > 0.1 or abs(y_succ - y_pred) > 0.1:
                        ax.annotate(
                            '', xy=(to_x, y_succ),
                            xytext=(from_x, y_pred),
                            arrowprops=dict(
                                arrowstyle='->', color='#2F4F4F',
                                connectionstyle='arc3,rad=0.1',
                                lw=2, alpha=0.7),
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
            self._fig.savefig(filepath, dpi=300, bbox_inches="tight",
                              facecolor='white', edgecolor='none')
            messagebox.showinfo("Export", f"Saved to {filepath}")

    def _export_data(self):
        """Export schedule data to CSV or Excel from graph nodes."""
        if not self._results_data or not self._results_data.get('graph'):
            messagebox.showwarning("Warning",
                                   "No schedule data. Run analysis first.")
            return
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            title="Export Schedule Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"),
                       ("Excel files", "*.xlsx"),
                       ("All files", "*.*")])
        if not filepath:
            return
        try:
            G = self._results_data['graph']
            critical_set = set(self._results_data.get('critical_activities', []))
            # Parse project start date
            try:
                project_start = datetime.strptime(
                    self._start_date_var.get(), "%Y-%m-%d")
            except Exception:
                project_start = datetime.now()

            rows = []
            for node in G.nodes():
                if node in ('START', 'END'):
                    continue
                nd = G.nodes[node]
                es = nd.get('earliest_start', nd.get('ES', 0))
                ef = nd.get('earliest_finish', nd.get('EF', 0))
                ls = nd.get('latest_start', nd.get('LS', 0))
                lf = nd.get('latest_finish', nd.get('LF', 0))
                tf = nd.get('float', nd.get('total_float', 0))
                dur = nd.get('expected_duration', nd.get('duration', 0))
                start_date = project_start + timedelta(days=int(es))
                finish_date = project_start + timedelta(days=int(ef))
                preds = list(G.predecessors(node))
                preds_str = ', '.join(str(p) for p in preds if p != 'START')
                rows.append({
                    'Activity_ID': node,
                    'Activity_Name': nd.get('activity', node),
                    'Duration': dur,
                    'Start_Date': start_date.strftime('%Y-%m-%d'),
                    'Finish_Date': finish_date.strftime('%Y-%m-%d'),
                    'Earliest_Start': es,
                    'Earliest_Finish': ef,
                    'Latest_Start': ls,
                    'Latest_Finish': lf,
                    'Total_Float': tf,
                    'Critical': 'Yes' if node in critical_set else 'No',
                    'Predecessors': preds_str,
                })
            import pandas as pd
            df = pd.DataFrame(rows)
            if filepath.lower().endswith('.xlsx'):
                df.to_excel(filepath, index=False, sheet_name='Project_Schedule')
            else:
                df.to_csv(filepath, index=False)
            messagebox.showinfo("Export", f"Schedule data exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    # ----------------------------------------------------------------
    # Public interface
    # ----------------------------------------------------------------

    def set_mode(self, mode: str):
        """Show/hide tracking controls based on mode."""
        self._mode = mode
        # Show CPM worked-solution buttons only in UG mode
        for btn in (self._cpm_fwd_btn, self._cpm_bwd_btn):
            if hasattr(self, '_cpm_fwd_btn'):
                if mode.upper() == "UG":
                    btn.pack(side=tk.RIGHT, padx=2)
                else:
                    btn.pack_forget()

    def _show_cpm_forward(self):
        """Open CPM forward-pass worked solution."""
        rd = self._results_data
        if not rd or not rd.get("graph"):
            messagebox.showinfo("No data",
                                "Run CPM/PERT analysis first.",
                                parent=self.frame)
            return
        steps = cpm_forward_steps(rd)
        WorkedSolutionWindow(self.frame, "CPM Forward Pass — Worked Solution", steps)

    def _show_cpm_backward(self):
        """Open CPM backward-pass worked solution."""
        rd = self._results_data
        if not rd or not rd.get("graph"):
            messagebox.showinfo("No data",
                                "Run CPM/PERT analysis first.",
                                parent=self.frame)
            return
        steps = cpm_backward_steps(rd)
        WorkedSolutionWindow(self.frame, "CPM Backward Pass — Worked Solution", steps)

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB and hasattr(self, "_fig"):
            figs.append(("gantt", self._fig))
        return figs

    def on_tab_selected(self):
        """Refresh chart when tab is selected."""
        self._draw_gantt()
