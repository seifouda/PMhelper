#!/usr/bin/env python3
"""
RCPS Tab Module

Displays resource-constrained project scheduling (RCPS) results and resource utilization charts.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class RCPSTab:
    """RCPS tab for displaying resource-constrained schedule and resource charts"""
    def __init__(self, notebook, main_window):
        self.notebook = notebook
        self.main_window = main_window
        self.results_data = None
        self.analysis_mode = None
        self.figure = None
        self.canvas = None
        self.create_tab()

    def create_tab(self):
        self.rcps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rcps_frame, text="RCPS Schedule")
        self.create_control_frame()
        self.tables_frame = ttk.Frame(self.rcps_frame)
        self.tables_frame.pack(fill=tk.BOTH, expand=True)

    def create_control_frame(self):
        control_frame = ttk.Frame(self.rcps_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(control_frame, text="Resource Limit:").pack(side=tk.LEFT, padx=5)
        self.resource_limit_var = tk.IntVar(value=5)
        ttk.Entry(control_frame, textvariable=self.resource_limit_var, width=5).pack(side=tk.LEFT)

        # Priority Rule Dropdown
        ttk.Label(control_frame, text="Priority Rule:").pack(side=tk.LEFT, padx=(20, 5))
        self.priority_rule_var = tk.StringVar(value='minimum_slack')
        priority_options = ['minimum_slack', 'shortest_duration', 'earliest_start']
        self.priority_rule_menu = ttk.Combobox(control_frame, textvariable=self.priority_rule_var, values=priority_options, state='readonly', width=18)
        self.priority_rule_menu.pack(side=tk.LEFT)

        ttk.Button(control_frame, text="Run RCPS", command=self.run_rcps).pack(side=tk.LEFT, padx=10)

    # Chart area removed

    def run_rcps(self):
        try:
            resource_limit = self.resource_limit_var.get()
            priority_rule = self.priority_rule_var.get()
            df_gantt = self.main_window.current_data
            import pandas as pd
            if df_gantt is None or not isinstance(df_gantt, pd.DataFrame) or df_gantt.empty:
                messagebox.showerror("RCPS Error", "No project data available. Please run CPM or PERT analysis before running RCPS scheduling.")
                return
            # Validate resource limit against max resource demand
            if 'resource' in df_gantt.columns:
                try:
                    max_resource = pd.to_numeric(df_gantt['resource'], errors='coerce').max()
                except Exception:
                    max_resource = None
                if max_resource is not None and resource_limit < max_resource:
                    messagebox.showwarning(
                        "Resource Limit Too Low",
                        f"Resource limit cannot be less than the maximum resource assigned to a single activity (max: {max_resource})."
                    )
                    return
            # Select analyzer based on analysis mode
            analysis_mode = getattr(self.main_window, 'analysis_mode', None)
            # --- DEBUG: Print input DataFrame for RCPS tab (especially for PERT data) ---
            print("\n[DEBUG] RCPS Tab Input DataFrame (first 10 rows):")
            print(df_gantt.head(10))
            print("[DEBUG] Columns:", list(df_gantt.columns))
            print("[DEBUG] Dtypes:\n", df_gantt.dtypes)
            print("[DEBUG] Analysis mode:", analysis_mode)
            print("[DEBUG] Priority rule:", priority_rule)
            # --- END DEBUG ---
            if analysis_mode == 'probabilistic':
                analyzer = self.main_window.pert_analyzer
            else:
                analyzer = self.main_window.cpm_analyzer
            # Generate CPM and RCPS tables using the correct analyzer
            cpm_table, _, _ = analyzer.build_cpm_schedule_table(df_gantt, resource_limit)
            rcps_table, _, _ = analyzer.rcps_heuristic_schedule_table(df_gantt, resource_limit, priority_rule=priority_rule)
            # Fill timeline columns with resource usage for both CPM and PERT using the same analyzed Gantt DataFrame
            timeline_cols = [col for col in cpm_table.columns if isinstance(col, int)]
            # CPM Table: fill timeline cells with resource usage for scheduled periods
            for idx, row in cpm_table.iterrows():
                if row['id'] in ['RA', 'RS']:
                    continue
                try:
                    es = int(row['early_start'])
                    dur = int(row['duration'])
                    res = int(row['resource'])
                    for t in timeline_cols:
                        if es < t <= es + dur:
                            cpm_table.at[idx, t] = res
                    # Do not clear timeline cells outside scheduled periods
                except Exception:
                    pass
            # RCPS Table: fill timeline cells with resource usage for scheduled periods
            for idx, row in rcps_table.iterrows():
                if row['id'] in ['RA', 'RS']:
                    continue
                try:
                    # Use actual_start if available, else early_start
                    start = int(row['actual_start']) if 'actual_start' in row and row['actual_start'] != '' else int(row['early_start'])
                    dur = int(row['duration'])
                    res = int(row['resource'])
                    for t in timeline_cols:
                        if start < t <= start + dur:
                            rcps_table.at[idx, t] = res
                    # Do not clear timeline cells outside scheduled periods
                except Exception:
                    pass
            # Clear previous tables
            for widget in self.tables_frame.winfo_children():
                widget.destroy()
            # Align CPM table columns to RCPS columns, but remove 'actual_start' (AS) from CPM table
            rcps_columns = list(rcps_table.columns)
            cpm_columns = [col for col in rcps_columns if col != 'actual_start']
            cpm_table_aligned = cpm_table.reindex(columns=cpm_columns, fill_value='')
            # Display both tables stacked vertically
            self.display_schedule_table(self.tables_frame, cpm_table_aligned, "Initial CPM-based Plan", 0, row=0)
            self.display_schedule_table(self.tables_frame, rcps_table, "Resource-Constrained Schedule (RCPS)", 0, row=1)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            messagebox.showerror("RCPS Error", str(e))

    def display_schedule_table(self, parent, table, label, col, row=0):
        # Display a schedule table in the parent frame with a label
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        label_widget = ttk.Label(frame, text=label, font=("Arial", 12, "bold"))
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 2))
        # Use tksheet for true cell borders
        from tksheet import Sheet
        pretty_names = {
            'id': 'ID',
            'duration': 'D',
            'resource': 'R',
            'early_start': 'ES',
            'late_finish': 'LF',
            'float': 'F',
            'actual_start': 'AS',
        }
        display_columns = list(table.columns)
        display_headers = [pretty_names.get(col, str(col)) for col in display_columns]

        # Identify timeline columns (integer column names)
        timeline_cols = [col for col in display_columns if isinstance(col, int)]

        # Special handling for CPM table: replace 'S' with resource usage in timeline columns
        is_cpm = label.lower().startswith("initial cpm")

        # --- Highlighting logic adapted from plot_schedule_tables (matplotlib) ---
        # For RCPS table, need to know scheduled/delayed activities
        scheduled_activities = set()
        delayed_activities = set()
        if not is_cpm:
            for _, row in table.iterrows():
                if row['id'] not in ['RA', 'RS']:
                    if 'actual_start' in row and 'early_start' in row and row['actual_start'] == row['early_start']:
                        scheduled_activities.add(row['id'])
                    else:
                        delayed_activities.add(row['id'])

        # Prepare data and cell_colors
        data = []
        cell_colors = []
        # --- Precompute heatmap for RS row ---
        rs_row_idx = None
        rs_row_values = []
        for idx, row in enumerate(table.iterrows()):
            row_obj = row[1]
            if row_obj['id'] == 'RS':
                rs_row_idx = idx
                # Only collect timeline column values (numeric)
                for col in display_columns:
                    if col in timeline_cols:
                        val = row_obj[col]
                        try:
                            rs_row_values.append(float(val))
                        except Exception:
                            rs_row_values.append(None)
                break
        # Compute min/max for heatmap
        rs_numeric = [v for v in rs_row_values if v is not None]
        rs_min = min(rs_numeric) if rs_numeric else 0
        rs_max = max(rs_numeric) if rs_numeric else 1
        def interpolate_color(val, vmin, vmax):
            # Colors: light yellow #fff9c4 to dark orange #ff9800
            if val is None or vmax == vmin:
                return '#fff9c4'
            ratio = (val - vmin) / (vmax - vmin) if vmax > vmin else 0
            # Interpolate RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            def rgb_to_hex(rgb):
                return '#{:02x}{:02x}{:02x}'.format(*rgb)
            light = hex_to_rgb('fff9c4')
            dark = hex_to_rgb('ff9800')
            rgb = tuple(int(light[i] + (dark[i] - light[i]) * ratio) for i in range(3))
            return rgb_to_hex(rgb)

        for row_idx, row in enumerate(table.iterrows()):
            row_obj = row[1]
            row_data = []
            row_colors = []
            is_resource_row = row_obj['id'] in ['RA', 'RS']
            for col_idx, col in enumerate(display_columns):
                val = row_obj[col]
                # For any table with timeline columns and 'resource', replace 'S' with resource usage
                cell_val = str(val) if val != '' else ''
                is_cpm_or_pert = (col in timeline_cols and 'resource' in row_obj)
                if is_cpm_or_pert and str(val) == 'S':
                    resource_val = row_obj['resource'] if 'resource' in row_obj else ''
                    cell_val = str(resource_val)
                row_data.append(cell_val)

                # --- Cell coloring logic ---
                # Resource rows (RA, RS): all cells white except RS heatmap
                if is_resource_row:
                    if row_obj['id'] == 'RS' and col in timeline_cols:
                        try:
                            idx_in_timeline = timeline_cols.index(col)
                            v = rs_row_values[idx_in_timeline] if idx_in_timeline < len(rs_row_values) else None
                            row_colors.append(interpolate_color(v, rs_min, rs_max))
                        except Exception:
                            row_colors.append('white')
                    else:
                        row_colors.append('white')
                # Critical activity row: first column (not resource rows), in both CPM and RCPS
                elif col == display_columns[0] and ('float' in row_obj and row_obj['float'] == 0 and row_obj['id'] not in ['RA', 'RS']):
                    row_colors.append('#c0392b')
                # Highlight AS > ES in RCPS table only
                elif not is_cpm and col == 'actual_start' and 'early_start' in row_obj and 'actual_start' in row_obj:
                    try:
                        as_val = int(row_obj['actual_start'])
                        es_val = int(row_obj['early_start'])
                        if as_val > es_val:
                            row_colors.append('#ffd580')  # yellow
                        else:
                            row_colors.append('white')
                    except Exception:
                        row_colors.append('white')
                # CPM Table
                elif is_cpm:
                    # Timeline columns
                    if col in timeline_cols:
                        if str(val) == 'S' or (str(cell_val).isdigit() and int(cell_val) > 0):
                            row_colors.append('#b6fcb6')
                        else:
                            row_colors.append('white')
                    else:
                        row_colors.append('white')
                # RCPS Table
                else:
                    # Timeline columns
                    if col in timeline_cols:
                        if row_obj['id'] == 'RS':
                            # Already handled above
                            row_colors.append('white')
                        elif str(cell_val).isdigit() and int(cell_val) > 0:
                            if row_obj['id'] in delayed_activities:
                                row_colors.append('#ffd580')
                            elif row_obj['id'] in scheduled_activities:
                                row_colors.append('#b6fcb6')
                            else:
                                row_colors.append('white')
                        else:
                            row_colors.append('white')
                    else:
                        row_colors.append('white')
            data.append(row_data)
            cell_colors.append(row_colors)

        sheet = Sheet(frame,
                      data=data,
                      headers=display_headers,
                      show_x_scrollbar=False,  # No horizontal scrollbar
                      show_y_scrollbar=True,
                      show_row_index=False,
                      outline_thickness=1)
        # Apply per-cell background colors using tksheet's highlight_cells
        try:
            for r, row_colors in enumerate(cell_colors):
                for c, color in enumerate(row_colors):
                    sheet.highlight_cells(row=r, column=c, bg=color, fg='black', redraw=False)
            sheet.redraw()
        except Exception:
            pass
        # Hide x scrollbar if method exists (for newer tksheet)
        if hasattr(sheet, 'hide'):
            try:
                sheet.hide("x_scrollbar")
            except Exception:
                pass
        # Enable only vertical navigation and editing, no horizontal scroll or left/right arrow
        sheet.enable_bindings((
            "single_select", "row_select", "column_select", "right_click_popup_menu", "rc_select", "copy", "cut", "paste", "delete", "undo", "edit_cell"
        ))
        # Disable left/right arrow and horizontal scroll if method exists
        if hasattr(sheet, 'disable_bindings'):
            try:
                sheet.disable_bindings(("left_arrow", "right_arrow", "horizontal_scroll"))
            except Exception:
                pass
        sheet.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # --- Dynamic column width adjustment: always fill frame, no horizontal scroll ---
        def adjust_column_widths(event=None):
            frame.update_idletasks()
            frame_width = frame.winfo_width() or 1000  # fallback if not yet rendered
            num_cols = len(display_columns)
            min_col_width = 1
            if num_cols == 0:
                return
            # Always distribute the width exactly, with minimal col width = 1
            col_width = int(frame_width / num_cols)
            widths = [col_width] * num_cols
            # Distribute any leftover pixels to the last column
            total_width = sum(widths)
            if total_width < frame_width:
                widths[-1] += frame_width - total_width
            # If too many columns, all will be 1px
            sheet.set_column_widths(widths)

        # Bind to frame resize events for live adjustment
        frame.bind("<Configure>", adjust_column_widths)
        # Initial adjustment after rendering
        frame.after(100, adjust_column_widths)
        # Set gridline color and thickness for all cells
        sheet.set_options(grid_color="#888", thickness=1)

    # Chart plotting removed

