"""
PMhelper Edu — Input Tab.
Copy of input_tab.py with EVM data entry panel added below the CPM/PERT table.
The original input_tab.py is NEVER touched.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from pmhelper.utils.file_handlers import FileHandler
from pmhelper.core.evm_models_edu import EVMTask, EVMPeriod, EVMProject, PVSpread, compute_pv_schedule


class InputTabEdu:
    """Input tab for activity data entry + EVM data entry panel."""

    def __init__(self, parent, state, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self.current_mode = None
        self._mode = "UG"  # UG or PG

        self.frame = ttk.Frame(parent)

        # Main paned window: top = CPM/PERT, bottom = EVM
        self.paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ---- Top section: CPM/PERT task table (from original input_tab) ----
        self.top_frame = ttk.Frame(self.paned)
        self.paned.add(self.top_frame, weight=1)

        self._create_button_frame()
        self.mode_label = ttk.Label(self.top_frame, text="Mode: None",
                                    font=("Arial", 10, "bold"))
        self.mode_label.pack(anchor="w", pady=(0, 5))

        self.tree_frame = ttk.Frame(self.top_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        self.setup_deterministic_tree()

        # ---- Bottom section: EVM data entry panel ----
        self.bottom_frame = ttk.Frame(self.paned)
        self.paned.add(self.bottom_frame, weight=1)
        self._create_evm_panel()

        # Initialize EVM project in state if not set
        if self.state.evm_project is None:
            self.state.evm_project = EVMProject()

    # ================================================================
    #  CPM / PERT section (copied from original input_tab.py)
    # ================================================================

    def _create_button_frame(self):
        """Create the button frame with all control buttons."""
        button_frame = ttk.Frame(self.top_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="Load CPM Data",
                   command=self.load_deterministic_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Load PERT Data",
                   command=self.load_probabilistic_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Auto-Detect CSV",
                   command=self.load_csv_auto_detect).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Add Row",
                   command=self.add_row).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Row",
                   command=self.delete_row).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All",
                   command=self.clear_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Load Sample CPM",
                   command=self.load_sample_cpm).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Load Sample PERT",
                   command=self.load_sample_pert).pack(side=tk.LEFT, padx=(0, 5))

        # Separator + Analyze button
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=8, pady=2)
        self._analyze_btn = ttk.Button(
            button_frame, text="\u25b6 Analyze",
            command=self._run_analysis)
        self._analyze_btn.pack(side=tk.LEFT, padx=(0, 5))

    def setup_deterministic_tree(self):
        self.clear_tree_frame()
        columns = ("ID", "Activity", "Duration", "Predecessors", "Min Duration",
                   "Crash Cost", "Resource Demand", "Normal Cost")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns,
                                 show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50, minwidth=50)
            elif col in ("Duration", "Min Duration", "Resource Demand"):
                self.tree.column(col, width=80, minwidth=70)
            elif col in ("Crash Cost", "Normal Cost"):
                self.tree.column(col, width=100, minwidth=80)
            elif col == "Predecessors":
                self.tree.column(col, width=120, minwidth=100)
            else:
                self.tree.column(col, width=150, minwidth=120)
        v_sb = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind('<Double-1>', self.edit_item)
        self.current_mode = 'deterministic'

    def setup_probabilistic_tree(self):
        self.clear_tree_frame()
        columns = ("ID", "Activity", "Optimistic", "Most Likely", "Pessimistic",
                   "Predecessors", "Min Duration", "Crash Cost", "Resource Demand",
                   "Normal Cost")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns,
                                 show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50, minwidth=50)
            elif col in ("Optimistic", "Most Likely", "Pessimistic",
                         "Min Duration", "Resource Demand"):
                self.tree.column(col, width=80, minwidth=70)
            elif col in ("Crash Cost", "Normal Cost"):
                self.tree.column(col, width=100, minwidth=80)
            elif col == "Predecessors":
                self.tree.column(col, width=120, minwidth=100)
            else:
                self.tree.column(col, width=150, minwidth=120)
        v_sb = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind('<Double-1>', self.edit_item)
        self.current_mode = 'probabilistic'

    def clear_tree_frame(self):
        for widget in self.tree_frame.winfo_children():
            widget.destroy()

    def auto_detect_mode(self, csv_headers):
        headers_lower = [h.lower().strip() for h in csv_headers]
        pert_indicators = ['optimistic', 'pessimistic', 'most_likely']
        if any(ind in headers_lower for ind in pert_indicators):
            return 'probabilistic'
        return 'deterministic'

    def validate_file_format(self, filename, expected_mode):
        try:
            if filename.lower().endswith('.xlsx'):
                import pandas as pd
                df = pd.read_excel(filename, nrows=0)
                headers = df.columns.tolist()
            else:
                with open(filename, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])
            if not headers:
                return True
            return self.auto_detect_mode(headers) == expected_mode
        except Exception:
            return True

    def load_deterministic_data(self):
        filename = filedialog.askopenfilename(
            title="Load CPM Data",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"),
                       ("All files", "*.*")])
        if filename:
            self.clear_all_without_confirmation()
            if self.validate_file_format(filename, 'deterministic'):
                self.load_file(filename, 'deterministic')
            else:
                messagebox.showerror("Invalid Data Format",
                    "This file appears to contain PERT data.\n"
                    "Use 'Load PERT Data' instead.")

    def load_probabilistic_data(self):
        filename = filedialog.askopenfilename(
            title="Load PERT Data",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"),
                       ("All files", "*.*")])
        if filename:
            self.clear_all_without_confirmation()
            if self.validate_file_format(filename, 'probabilistic'):
                self.load_file(filename, 'probabilistic')
            else:
                messagebox.showerror("Invalid Data Format",
                    "This file appears to contain CPM data.\n"
                    "Use 'Load CPM Data' instead.")

    def load_csv_auto_detect(self):
        filename = filedialog.askopenfilename(
            title="Select CSV file (Auto-detect mode)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not filename:
            return
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if not headers:
                    messagebox.showerror("Error", "CSV file appears to be empty.")
                    return
                detected_mode = self.auto_detect_mode(headers)
                self.clear_all_without_confirmation()
                if detected_mode == 'probabilistic':
                    self.setup_probabilistic_tree()
                else:
                    self.setup_deterministic_tree()
                activities_data = []
                f.seek(0)
                reader = csv.DictReader(f)
                for row in reader:
                    if detected_mode == 'probabilistic':
                        activity_dict = {
                            'id': row.get('id', ''),
                            'activity': row.get('activity', ''),
                            'optimistic': row.get('optimistic', ''),
                            'most_likely': row.get('most_likely', ''),
                            'pessimistic': row.get('pessimistic', ''),
                            'predecessors': row.get('predecessors', ''),
                            'min_duration': row.get('min_duration', ''),
                            'crash_cost': row.get('crash_cost', ''),
                            'resource_demand': row.get('resource_demand', ''),
                            'normal_cost': row.get('normal_cost', ''),
                        }
                    else:
                        activity_dict = {
                            'id': row.get('id', ''),
                            'activity': row.get('activity', ''),
                            'duration': row.get('duration', ''),
                            'predecessors': row.get('predecessors', ''),
                            'min_duration': row.get('min_duration', ''),
                            'crash_cost': row.get('crash_cost', ''),
                            'resource_demand': row.get('resource_demand', ''),
                            'normal_cost': row.get('normal_cost', ''),
                        }
                    activities_data.append(activity_dict)
                self.populate_tree(activities_data)
                self.mode_label.config(
                    text=f"Mode: {detected_mode.title()} (Auto-detected)")
                messagebox.showinfo("Success",
                    f"Loaded {len(activities_data)} activities ({detected_mode} mode)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def load_file(self, filename, mode):
        try:
            if filename.lower().endswith('.xlsx'):
                activities_data = FileHandler.load_excel(filename)
            else:
                activities_data = FileHandler.load_csv(filename)
            if mode == 'deterministic':
                if mode != self.current_mode:
                    self.setup_deterministic_tree()
                self.mode_label.config(text="Mode: CPM (Deterministic)")
            elif mode == 'probabilistic':
                if mode != self.current_mode:
                    self.setup_probabilistic_tree()
                self.mode_label.config(text="Mode: PERT (Probabilistic)")
            self.populate_tree(activities_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def populate_tree(self, activities_data):
        for activity in activities_data:
            if self.current_mode == 'deterministic':
                values = (
                    activity.get('id', ''), activity.get('activity', ''),
                    activity.get('duration', ''), activity.get('predecessors', ''),
                    activity.get('min_duration', ''), activity.get('crash_cost', ''),
                    activity.get('resource_demand', ''), activity.get('normal_cost', ''))
            else:
                values = (
                    activity.get('id', ''), activity.get('activity', ''),
                    activity.get('optimistic', ''), activity.get('most_likely', ''),
                    activity.get('pessimistic', ''), activity.get('predecessors', ''),
                    activity.get('min_duration', ''), activity.get('crash_cost', ''),
                    activity.get('resource_demand', ''), activity.get('normal_cost', ''))
            self.tree.insert("", tk.END, values=values)

    def add_row(self):
        if self.current_mode == 'deterministic':
            self.tree.insert("", tk.END, values=("",) * 8)
        else:
            self.tree.insert("", tk.END, values=("",) * 10)

    def delete_row(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a row to delete.")
            return
        for item in sel:
            self.tree.delete(item)

    def clear_all(self):
        if messagebox.askyesno("Clear All", "Clear all data?"):
            self.clear_all_without_confirmation()

    def clear_all_without_confirmation(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def edit_item(self, event):
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        column = self.tree.identify_column(event.x)
        if not column:
            return
        col_index = int(column.replace('#', '')) - 1
        current_values = list(self.tree.item(item, 'values'))
        current_value = current_values[col_index] if col_index < len(current_values) else ""

        self._edit_entry = tk.Entry(self.tree)
        self._edit_entry.insert(0, current_value)
        bbox = self.tree.bbox(item, column)
        if bbox:
            self._edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            self._edit_entry.focus()
            self._edit_entry.select_range(0, tk.END)
            self._edit_entry.bind('<Return>',
                                  lambda e: self._save_edit(item, col_index))
            self._edit_entry.bind('<Escape>', lambda e: self._cancel_edit())
            self._edit_entry.bind('<FocusOut>',
                                  lambda e: self._save_edit(item, col_index))

    def _save_edit(self, item, col_index):
        if hasattr(self, '_edit_entry'):
            new_value = self._edit_entry.get()
            vals = list(self.tree.item(item, 'values'))
            while len(vals) <= col_index:
                vals.append('')
            vals[col_index] = new_value
            self.tree.item(item, values=vals)
            self._cancel_edit()

    def _cancel_edit(self):
        if hasattr(self, '_edit_entry'):
            self._edit_entry.destroy()
            delattr(self, '_edit_entry')

    def load_sample_cpm(self):
        sample_data = FileHandler.get_sample_cpm_data()
        if self.current_mode != 'deterministic':
            self.setup_deterministic_tree()
        self.mode_label.config(text="Mode: CPM (Deterministic)")
        self.populate_tree(sample_data)

    def load_sample_pert(self):
        self.clear_tree_frame()
        self.setup_probabilistic_tree()
        sample_data = FileHandler.get_sample_pert_data()
        self.populate_tree(sample_data)
        self.mode_label.config(text="Mode: PERT (Probabilistic)")

    def get_activities_data(self):
        """Get activities data from the treeview."""
        activities_data = []
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if not values or not values[0].strip():
                continue
            if self.current_mode == 'deterministic':
                activity_dict = {
                    'id': values[0] if len(values) > 0 else '',
                    'activity': values[1] if len(values) > 1 else '',
                    'duration': values[2] if len(values) > 2 else '',
                    'predecessors': values[3] if len(values) > 3 else '',
                    'min_duration': values[4] if len(values) > 4 else '',
                    'crash_cost': values[5] if len(values) > 5 else '',
                    'resource_demand': values[6] if len(values) > 6 else '',
                    'normal_cost': values[7] if len(values) > 7 else '',
                }
            else:
                activity_dict = {
                    'id': values[0] if len(values) > 0 else '',
                    'activity': values[1] if len(values) > 1 else '',
                    'optimistic': values[2] if len(values) > 2 else '',
                    'most_likely': values[3] if len(values) > 3 else '',
                    'pessimistic': values[4] if len(values) > 4 else '',
                    'predecessors': values[5] if len(values) > 5 else '',
                    'min_duration': values[6] if len(values) > 6 else '',
                    'crash_cost': values[7] if len(values) > 7 else '',
                    'resource_demand': values[8] if len(values) > 8 else '',
                    'normal_cost': values[9] if len(values) > 9 else '',
                }
            activities_data.append(activity_dict)
        return activities_data

    # ================================================================
    #  EVM Data Entry Panel  (Phase 1 addition)
    # ================================================================

    def _create_evm_panel(self):
        """Create the EVM data entry panel below the CPM/PERT table."""
        # Outer labelled frame
        evm_frame = ttk.LabelFrame(self.bottom_frame, text="EVM Data Entry",
                                    padding=5)
        evm_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ---- BAC Input ----
        bac_frame = ttk.LabelFrame(evm_frame, text="Budget at Completion (BAC)",
                                    padding=5)
        bac_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        bac_row = ttk.Frame(bac_frame)
        bac_row.pack(fill=tk.X)

        ttk.Label(bac_row, text="BAC:").pack(side=tk.LEFT, padx=(0, 5))

        self._bac_var = tk.StringVar(value="0.0")
        self._bac_entry = ttk.Entry(bac_row, textvariable=self._bac_var, width=15)
        self._bac_entry.pack(side=tk.LEFT, padx=(0, 10))
        self._bac_entry.bind('<Return>', lambda e: self._on_bac_changed())
        self._bac_entry.bind('<FocusOut>', lambda e: self._on_bac_changed())

        self._bac_auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bac_row, text="Auto-compute from task budgets",
                        variable=self._bac_auto_var,
                        command=self._on_bac_auto_toggle).pack(side=tk.LEFT)

        self._bac_warning = ttk.Label(bac_frame, text="", foreground="orange")
        self._bac_warning.pack(anchor="w", pady=(2, 0))

        # ---- Sub-section A: EVM Task Budgets & Progress ----
        task_lf = ttk.LabelFrame(evm_frame, text="Task Budgets & Progress",
                                  padding=5)
        task_lf.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        task_btn_row = ttk.Frame(task_lf)
        task_btn_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(task_btn_row, text="Sync from CPM Tasks",
                   command=self._sync_from_cpm).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_btn_row, text="Add EVM Task",
                   command=self._add_evm_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_btn_row, text="Delete EVM Task",
                   command=self._delete_evm_task).pack(side=tk.LEFT, padx=(0, 5))

        evm_task_cols = ("Task ID", "Name", "Budget ($)", "% Complete",
                         "Planned Start", "Planned Finish", "PV Spread")
        self.evm_task_tree = ttk.Treeview(task_lf, columns=evm_task_cols,
                                           show='headings', height=6)
        for col in evm_task_cols:
            self.evm_task_tree.heading(col, text=col)
            if col == "Task ID":
                self.evm_task_tree.column(col, width=70, minwidth=60)
            elif col == "Name":
                self.evm_task_tree.column(col, width=140, minwidth=100)
            elif col in ("Budget ($)", "% Complete", "Planned Start",
                         "Planned Finish"):
                self.evm_task_tree.column(col, width=90, minwidth=70)
            else:
                self.evm_task_tree.column(col, width=80, minwidth=60)

        evm_task_sb = ttk.Scrollbar(task_lf, orient=tk.VERTICAL,
                                     command=self.evm_task_tree.yview)
        self.evm_task_tree.configure(yscrollcommand=evm_task_sb.set)
        self.evm_task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        evm_task_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.evm_task_tree.bind('<Double-1>', self._edit_evm_task_item)

        # ---- Sub-section B: Period PV / EV / AC Table ----
        period_lf = ttk.LabelFrame(evm_frame, text="Period Data (PV / EV / AC)",
                                    padding=5)
        period_lf.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        period_btn_row = ttk.Frame(period_lf)
        period_btn_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(period_btn_row, text="Add Period",
                   command=self._add_period).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(period_btn_row, text="Remove Period",
                   command=self._remove_period).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(period_btn_row, text="Compute PV from Tasks",
                   command=self._compute_pv_from_tasks).pack(side=tk.LEFT, padx=(0, 5))

        period_cols = ("#", "Label", "Cumul. PV ($)", "Cumul. EV ($)",
                       "Cumul. AC ($)", "EV Source")
        self.period_tree = ttk.Treeview(period_lf, columns=period_cols,
                                         show='headings', height=6)
        for col in period_cols:
            self.period_tree.heading(col, text=col)
            if col == "#":
                self.period_tree.column(col, width=40, minwidth=30)
            elif col == "Label":
                self.period_tree.column(col, width=100, minwidth=80)
            elif col == "EV Source":
                self.period_tree.column(col, width=80, minwidth=60)
            else:
                self.period_tree.column(col, width=100, minwidth=80)

        period_sb = ttk.Scrollbar(period_lf, orient=tk.VERTICAL,
                                   command=self.period_tree.yview)
        self.period_tree.configure(yscrollcommand=period_sb.set)
        self.period_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        period_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.period_tree.bind('<Double-1>', self._edit_period_item)

        # EV discrepancy warning
        self._ev_warning = ttk.Label(evm_frame, text="", foreground="orange")
        self._ev_warning.pack(anchor="w", padx=5, pady=(0, 5))

    # ---- BAC logic ----

    def _on_bac_auto_toggle(self):
        proj = self.state.evm_project
        if proj is None:
            return
        proj.bac_auto_compute = self._bac_auto_var.get()
        if proj.bac_auto_compute:
            proj.recompute_bac()
            self._bac_var.set(f"{proj.bac:.2f}")
            self._bac_entry.config(state="readonly")
        else:
            self._bac_entry.config(state="normal")
        self._check_bac_warning()
        self.state.mark_dirty()

    def _on_bac_changed(self):
        proj = self.state.evm_project
        if proj is None or proj.bac_auto_compute:
            return
        try:
            val = float(self._bac_var.get())
            if val < 0:
                messagebox.showwarning("Invalid BAC", "BAC must be >= 0")
                return
            proj.bac = val
            self._check_bac_warning()
            self.state.mark_dirty()
        except ValueError:
            messagebox.showwarning("Invalid BAC", "Please enter a valid number.")

    def _check_bac_warning(self):
        proj = self.state.evm_project
        if proj is None:
            self._bac_warning.config(text="")
            return
        task_total = sum(t.budget for t in proj.tasks)
        if abs(proj.bac - task_total) > 0.01:
            sym = proj.currency_symbol
            self._bac_warning.config(
                text=f"\u26a0 BAC ({sym}{proj.bac:,.2f}) \u2260 sum of task "
                     f"budgets ({sym}{task_total:,.2f}). Adjust task budgets or BAC.")
        else:
            self._bac_warning.config(text="")

    # ---- EVM Task Table ----

    def _sync_from_cpm(self):
        """Copy task IDs and names from the CPM table into the EVM table.

        If CPM analysis has been run, also pulls ES/EF as planned start/finish
        and sets cpm_task_id for Gantt integration.
        """
        cpm_rows = self.get_activities_data()
        if not cpm_rows:
            messagebox.showinfo("Sync", "No CPM tasks to sync.")
            return
        proj = self.state.evm_project
        if proj is None:
            proj = EVMProject()
            self.state.evm_project = proj

        # Get analysis results if available (for ES/EF)
        analysis_activities = {}
        if self.main_window and hasattr(self.main_window, 'results_data'):
            rd = self.main_window.results_data
            if rd and 'activities' in rd:
                for act in rd['activities']:
                    analysis_activities[act.get('id', '')] = act

        existing_ids = {t.task_id: t for t in proj.tasks}
        new_count = 0
        updated_count = 0

        for row in cpm_rows:
            tid = row.get('id', '').strip()
            name = row.get('activity', '').strip()
            if not tid:
                continue

            # Get ES/EF from analysis results if available
            cpm_act = analysis_activities.get(tid, {})
            es = int(cpm_act.get('ES', 0)) if cpm_act else 0
            ef = int(cpm_act.get('EF', 0)) if cpm_act else 0

            if tid in existing_ids:
                existing_ids[tid].name = name
                existing_ids[tid].cpm_task_id = tid
                # Update planned start/finish from CPM if analysis was run
                if cpm_act:
                    existing_ids[tid].planned_start = es
                    existing_ids[tid].planned_finish = ef
                updated_count += 1
            else:
                proj.tasks.append(EVMTask(
                    task_id=tid, name=name, budget=0.0,
                    planned_start=es, planned_finish=ef,
                    cpm_task_id=tid))
                new_count += 1

        # Flag deleted CPM tasks
        cpm_ids = {r.get('id', '').strip() for r in cpm_rows if r.get('id', '')}
        for t in proj.tasks:
            if t.task_id not in cpm_ids and not t.name.endswith("(CPM task deleted)"):
                t.name = f"{t.name} \u26a0 (CPM task deleted)"

        has_analysis = bool(analysis_activities)
        sync_msg = (
            f"Sync will add {new_count} new and update {updated_count} "
            f"existing tasks.\nBudgets and % Complete are preserved."
        )
        if has_analysis:
            sync_msg += "\n\nPlanned Start/Finish will be updated from CPM results (ES/EF)."

        if messagebox.askyesno("Sync from CPM",
                               f"{sync_msg}\n\nContinue?"):
            self._refresh_evm_task_tree()
            proj.recompute_bac()
            self._bac_var.set(f"{proj.bac:.2f}")
            self._check_bac_warning()
            self.state.mark_dirty()
        else:
            # Undo changes — reload from pre-sync state
            # (simple approach: just refresh from current state)
            pass

    def _add_evm_task(self):
        proj = self.state.evm_project
        if proj is None:
            proj = EVMProject()
            self.state.evm_project = proj

        # Generate next ID
        existing_ids = {t.task_id for t in proj.tasks}
        idx = len(proj.tasks) + 1
        while f"T{idx}" in existing_ids:
            idx += 1
        new_id = f"T{idx}"

        proj.tasks.append(EVMTask(
            task_id=new_id, name=f"Task {idx}", budget=0.0,
            planned_start=0, planned_finish=0))
        self._refresh_evm_task_tree()
        proj.recompute_bac()
        self._bac_var.set(f"{proj.bac:.2f}")
        self._check_bac_warning()
        self.state.mark_dirty()

    def _delete_evm_task(self):
        sel = self.evm_task_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an EVM task to delete.")
            return
        proj = self.state.evm_project
        if proj is None:
            return
        for item in sel:
            vals = self.evm_task_tree.item(item, 'values')
            tid = vals[0] if vals else ""
            proj.tasks = [t for t in proj.tasks if t.task_id != tid]
        self._refresh_evm_task_tree()
        proj.recompute_bac()
        self._bac_var.set(f"{proj.bac:.2f}")
        self._check_bac_warning()
        self.state.mark_dirty()

    def _refresh_evm_task_tree(self):
        """Rebuild the EVM task treeview from state."""
        for item in self.evm_task_tree.get_children():
            self.evm_task_tree.delete(item)
        proj = self.state.evm_project
        if proj is None:
            return
        for t in proj.tasks:
            self.evm_task_tree.insert("", tk.END, values=(
                t.task_id, t.name, f"{t.budget:.2f}", f"{t.pct_complete:.1f}",
                t.planned_start, t.planned_finish, t.pv_spread.value))

    def _edit_evm_task_item(self, event):
        """Handle double-click editing in the EVM task tree."""
        item = self.evm_task_tree.selection()[0] if self.evm_task_tree.selection() else None
        if not item:
            return
        column = self.evm_task_tree.identify_column(event.x)
        if not column:
            return
        col_index = int(column.replace('#', '')) - 1
        # Columns: 0=ID(readonly), 1=Name(readonly), 2=Budget, 3=%Complete,
        #          4=PlannedStart, 5=PlannedFinish, 6=PVSpread
        if col_index < 2:
            return  # ID and Name are read-only

        current_values = list(self.evm_task_tree.item(item, 'values'))
        current_value = current_values[col_index] if col_index < len(current_values) else ""

        entry = tk.Entry(self.evm_task_tree)
        entry.insert(0, current_value)
        bbox = self.evm_task_tree.bbox(item, column)
        if bbox:
            entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            entry.focus()
            entry.select_range(0, tk.END)

            def save(e=None):
                new_val = entry.get()
                tid = current_values[0]
                proj = self.state.evm_project
                task = next((t for t in proj.tasks if t.task_id == tid), None)
                if task:
                    try:
                        if col_index == 2:  # Budget
                            task.budget = float(new_val)
                        elif col_index == 3:  # % Complete
                            task.pct_complete = float(new_val)
                        elif col_index == 4:  # Planned Start
                            task.planned_start = int(new_val)
                        elif col_index == 5:  # Planned Finish
                            task.planned_finish = int(new_val)
                        elif col_index == 6:  # PV Spread
                            task.pv_spread = PVSpread(new_val.lower())
                        task.validate()
                        proj.recompute_bac()
                        self._bac_var.set(f"{proj.bac:.2f}")
                        self._check_bac_warning()
                        self._check_ev_discrepancy()
                        self.state.mark_dirty()
                    except (ValueError, KeyError) as ex:
                        messagebox.showwarning("Invalid Value", str(ex))
                self._refresh_evm_task_tree()
                entry.destroy()

            def cancel(e=None):
                entry.destroy()

            entry.bind('<Return>', save)
            entry.bind('<Escape>', cancel)
            entry.bind('<FocusOut>', save)

    # ---- Period Table ----

    def _add_period(self):
        proj = self.state.evm_project
        if proj is None:
            proj = EVMProject()
            self.state.evm_project = proj
        idx = len(proj.periods)
        proj.periods.append(EVMPeriod(index=idx, label=f"Period {idx + 1}"))
        self._refresh_period_tree()
        self.state.mark_dirty()

    def _remove_period(self):
        sel = self.period_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select a period to remove.")
            return
        proj = self.state.evm_project
        if proj is None:
            return
        indices_to_remove = set()
        for item in sel:
            vals = self.period_tree.item(item, 'values')
            try:
                indices_to_remove.add(int(vals[0]))
            except (IndexError, ValueError):
                pass
        proj.periods = [p for p in proj.periods if p.index not in indices_to_remove]
        # Re-index
        for i, p in enumerate(proj.periods):
            p.index = i
        self._refresh_period_tree()
        self.state.mark_dirty()

    def _compute_pv_from_tasks(self):
        """Compute PV schedule from task data and fill the PV column."""
        proj = self.state.evm_project
        if proj is None or not proj.tasks:
            messagebox.showinfo("Compute PV", "No EVM tasks defined.")
            return
        if not proj.periods:
            messagebox.showinfo("Compute PV",
                "No periods defined. Add periods first.")
            return

        cumulative_pv = compute_pv_schedule(proj.tasks, len(proj.periods))
        for i, p in enumerate(proj.periods):
            if i < len(cumulative_pv):
                p.pv_cumulative = cumulative_pv[i]
        self._refresh_period_tree()
        self._check_ev_discrepancy()
        self.state.mark_dirty()
        messagebox.showinfo("Compute PV",
            f"PV schedule computed from {len(proj.tasks)} tasks across "
            f"{len(proj.periods)} periods.")

    def _refresh_period_tree(self):
        """Rebuild the period treeview from state."""
        for item in self.period_tree.get_children():
            self.period_tree.delete(item)
        proj = self.state.evm_project
        if proj is None:
            return
        for p in proj.periods:
            self.period_tree.insert("", tk.END, values=(
                p.index, p.label,
                f"{p.pv_cumulative:.2f}", f"{p.ev_cumulative:.2f}",
                f"{p.ac_cumulative:.2f}", p.ev_source))

    def _edit_period_item(self, event):
        """Handle double-click editing in the period tree."""
        item = self.period_tree.selection()[0] if self.period_tree.selection() else None
        if not item:
            return
        column = self.period_tree.identify_column(event.x)
        if not column:
            return
        col_index = int(column.replace('#', '')) - 1
        # Columns: 0=#(readonly), 1=Label, 2=PV, 3=EV, 4=AC, 5=Source(readonly)
        if col_index == 0 or col_index == 5:
            return

        current_values = list(self.period_tree.item(item, 'values'))
        current_value = current_values[col_index] if col_index < len(current_values) else ""

        entry = tk.Entry(self.period_tree)
        entry.insert(0, current_value)
        bbox = self.period_tree.bbox(item, column)
        if bbox:
            entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            entry.focus()
            entry.select_range(0, tk.END)

            def save(e=None):
                new_val = entry.get()
                period_idx = int(current_values[0])
                proj = self.state.evm_project
                period = next((p for p in proj.periods if p.index == period_idx), None)
                if period:
                    try:
                        if col_index == 1:  # Label
                            period.label = new_val
                        elif col_index == 2:  # PV
                            period.pv_cumulative = float(new_val)
                        elif col_index == 3:  # EV
                            period.ev_cumulative = float(new_val)
                            period.ev_source = "manual"
                        elif col_index == 4:  # AC
                            period.ac_cumulative = float(new_val)
                        self._check_ev_discrepancy()
                        self.state.mark_dirty()
                    except ValueError as ex:
                        messagebox.showwarning("Invalid Value", str(ex))
                self._refresh_period_tree()
                entry.destroy()

            def cancel(e=None):
                entry.destroy()

            entry.bind('<Return>', save)
            entry.bind('<Escape>', cancel)
            entry.bind('<FocusOut>', save)

    def _check_ev_discrepancy(self):
        """Show warning if period EV differs from task-level EV."""
        proj = self.state.evm_project
        if proj is None:
            self._ev_warning.config(text="")
            return
        disc = proj.ev_discrepancy()
        if disc > 0.01:
            sym = proj.currency_symbol
            self._ev_warning.config(
                text=f"\u26a0 Period EV ({sym}{proj.current_ev():,.2f}) differs from "
                     f"task-level EV ({sym}{proj.task_ev():,.2f}). "
                     f"Check % completes or edit period EV manually.")
        else:
            self._ev_warning.config(text="")

    # ---- Refresh from state ----

    def _refresh_from_state(self):
        """Refresh all EVM displays from the shared state."""
        proj = self.state.evm_project
        if proj is None:
            return
        self._bac_var.set(f"{proj.bac:.2f}")
        self._bac_auto_var.set(proj.bac_auto_compute)
        if proj.bac_auto_compute:
            self._bac_entry.config(state="readonly")
        else:
            self._bac_entry.config(state="normal")
        self._refresh_evm_task_tree()
        self._refresh_period_tree()
        self._check_bac_warning()
        self._check_ev_discrepancy()

    # ---- Tab interface methods ----

    def set_mode(self, mode: str):
        """Show/hide PG-only columns (e.g. PV Spread)."""
        self._mode = mode
        if mode == "UG":
            self.evm_task_tree.column("PV Spread", width=0, minwidth=0, stretch=False)
        else:
            self.evm_task_tree.column("PV Spread", width=80, minwidth=60, stretch=True)

    def _run_analysis(self):
        """Trigger CPM/PERT analysis via the main window."""
        if self.main_window and hasattr(self.main_window, 'analyze_project'):
            self.main_window.analyze_project()
        else:
            messagebox.showinfo(
                "Analysis",
                "Analysis is not available in this context.\n"
                "Please launch the app via the main entry point.")

    def on_tab_selected(self):
        """Refresh display from state when tab becomes active."""
        self._refresh_from_state()
