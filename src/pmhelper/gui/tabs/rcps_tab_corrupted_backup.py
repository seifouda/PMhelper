#!/usr/bin/env python3
"""
RCPS Tab Module

Displays resource-constrained project scheduling (RCPS) results and resource            # Clear             # Cl            #                 except Exception:
                    pass
            # Clear previous content
            for widget in self.tables_frame.winfo_children():
                widget.destroy()
            
            # Align CPM table columns to RCPS columns, but remove 'actual_start' (AS) from CPM table
            rcps_columns = list(rcps_table.columns)
            cmp_columns = [col for col in rcps_columns if col != 'actual_start']
            cpm_table_aligned = cpm_table.reindex(columns=cmp_columns, fill_value='')
            
            # NEW HYBRID LAYOUT: Tables + Gantt Charts side by side
            print("[DEBUG] Using NEW HYBRID LAYOUT with tables + Gantt charts")
            self.display_hybrid_schedule_view(self.tables_frame, cpm_table_aligned, rcps_table, df_gantt)
            
            # COMMENTED OUT: Original table-only display
            # # Display both tables stacked vertically
            # self.display_schedule_table(self.tables_frame, cpm_table_aligned, "Initial CPM-based Plan", 0, row=0)
            # self.display_schedule_table(self.tables_frame, rcps_table, "Resource-Constrained Schedule (RCPS)", 0, row=1)
        except Exception as e:s content
            for widget in self.tables_frame.winfo_children():
                widget.destroy()
            
            # Align CPM table columns to RCPS columns, but remove 'actual_start' (AS) from CPM table
            rcps_columns = list(rcps_table.columns)
            cmp_columns = [col for col in rcps_columns if col != 'actual_start']
            cpm_table_aligned = cpm_table.reindex(columns=cmp_columns, fill_value='')
            
            # NEW HYBRID LAYOUT: Tables + Gantt Charts side by side
            print("[DEBUG] Using NEW HYBRID LAYOUT with tables + Gantt charts")
            self.display_hybrid_schedule_view(self.tables_frame, cpm_table_aligned, rcps_table, df_gantt)
            
            # COMMENTED OUT: Original table-only display
            # # Display both tables stacked vertically
            # self.display_schedule_table(self.tables_frame, cpm_table_aligned, "Initial CPM-based Plan", 0, row=0)
            # self.display_schedule_table(self.tables_frame, rcps_table, "Resource-Constrained Schedule (RCPS)", 0, row=1)us content
            for widget in self.tables_frame.winfo_children():
                widget.destroy()
            
            # Align CPM table columns to RCPS columns, but remove 'actual_start' (AS) from CPM table
            rcps_columns = list(rcps_table.columns)
            cmp_columns = [col for col in rcps_columns if col != 'actual_start']
            cpm_table_aligned = cpm_table.reindex(columns=cmp_columns, fill_value='')
            
            # NEW HYBRID LAYOUT: Tables + Gantt Charts side by side
            print("[DEBUG] Using NEW HYBRID LAYOUT with tables + Gantt charts")
            self.display_hybrid_schedule_view(self.tables_frame, cpm_table_aligned, rcps_table, df_gantt)
            
            # COMMENTED OUT: Original table-only display
            # # Display both tables stacked vertically
            # self.display_schedule_table(self.tables_frame, cpm_table_aligned, "Initial CPM-based Plan", 0, row=0)
            # self.display_schedule_table(self.tables_frame, rcps_table, "Resource-Constrained Schedule (RCPS)", 0, row=1)  # Align CPM table columns to RCPS columns, but remove 'actual_start' (AS) from CPM table
            rcps_columns = list(rcps_table.columns)
            cmp_columns = [col for col in rcps_columns if col != 'actual_start']
            cpm_table_aligned = cpm_table.reindex(columns=cmp_columns, fill_value='')ious content
            for widget in self.tables_frame.winfo_children():
                widget.destroy()
            
            # Align CPM table columns to RCPS columns, but remove 'actual_start' (AS) from CPM table
            rcps_columns = lis        # Create compact tables (without timeline columns to save space)
        cpm_compact = self.create_compact_table(cpm_table)
        rcps_compact = self.create_compact_table(rcps_table)cps_table.columns)
            cpm_columns = [col for col in rcps_columns if col != 'actual_start']
            cpm_table_aligned = cmp_table.reindex(columns=cpm_columns, fill_value='')
            
            # NEW HYBRID LAYOUT: Tables + Gantt Charts side by side
            self.display_hybrid_schedule_view(self.tables_frame, cpm_table_aligned, rcps_table, df_gantt)
            
            # COMMENTED OUT: Original table-only display
            # # Display both tables stacked vertically
            # self.display_schedule_table(self.tables_frame, cpm_table_aligned, "Initial CPM-based Plan", 0, row=0)
            # self.display_schedule_table(self.tables_frame, rcps_table, "Resource-Constrained Schedule (RCPS)", 0, row=1)on charts.
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
            # NEW HYBRID LAYOUT: Tables + Gantt Charts side by side  
            print("[DEBUG] Using NEW HYBRID LAYOUT with tables + Gantt charts")
            self.display_hybrid_schedule_view(self.tables_frame, cpm_table_aligned, rcps_table, df_gantt)
            
            # COMMENTED OUT: Original table-only display
            # # Display both tables stacked vertically
            # self.display_schedule_table(self.tables_frame, cpm_table_aligned, "Initial CPM-based Plan", 0, row=0)
            # self.display_schedule_table(self.tables_frame, rcps_table, "Resource-Constrained Schedule (RCPS)", 0, row=1)
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
        # Disable all horizontal navigation and scrolling
        if hasattr(sheet, 'disable_bindings'):
            try:
                sheet.disable_bindings(("left_arrow", "right_arrow", "horizontal_scroll"))
            except Exception:
                pass
        # Do NOT enable any horizontal movement bindings
        sheet.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # --- Dynamic column width adjustment: always fill frame, no horizontal scroll ---
        def adjust_column_widths(event=None):
            frame.update_idletasks()
            frame_width = frame.winfo_width() or 1000  # fallback if not yet rendered
            min_col_width = 1  # Minimum width is 1 pixel
            # Identify timeline columns (integer column names)
            timeline_cols = [col for col in display_columns if isinstance(col, int)]
            n_timeline = len(timeline_cols)
            # Table type detection
            is_cpm = label.lower().startswith("initial cpm")
            if is_cpm:
                fixed_col_count = 6
                # CPM fixed width is based on RCPS: 7*45=315px, so each CPM col is 315//6=52px
                fixed_col_width = 41
                fixed_total_width = fixed_col_count * fixed_col_width
            else:
                fixed_col_count = 7
                fixed_col_width = 35
                fixed_total_width = fixed_col_count * fixed_col_width
            num_cols = len(display_columns)
            if num_cols == 0:
                return
            # Build widths: fixed for first N, rest for timeline
            widths = []
            for i, col in enumerate(display_columns):
                if (is_cpm and i < 6) or (not is_cpm and i < 7):
                    widths.append(fixed_col_width)
                else:
                    # Timeline columns: handled below
                    break
            n_fixed = len(widths)
            n_timeline = num_cols - n_fixed
            timeline_widths = []
            if n_timeline > 0:
                timeline_total_width = max(frame_width - fixed_total_width, n_timeline * min_col_width)
                timeline_col_width = int(timeline_total_width / n_timeline)
                timeline_widths = [max(min_col_width, timeline_col_width)] * n_timeline
                # Distribute any leftover pixels to the last timeline column
                total_width = fixed_total_width + sum(timeline_widths)
                if total_width < frame_width:
                    timeline_widths[-1] += frame_width - total_width
            widths.extend(timeline_widths)
            sheet.set_column_widths(widths)

        # Bind to frame resize events for live adjustment
        frame.bind("<Configure>", adjust_column_widths)
        # Initial adjustment after rendering
        frame.after(100, adjust_column_widths)
        # Set gridline color and thickness for all cells
        sheet.set_options(grid_color="#888", thickness=1)

    def display_hybrid_schedule_view(self, parent, cpm_table, rcps_table, df_gantt):
        """
        Display tables on the left and Gantt charts on the right.
        Layout: 
        [CPM Table]    [CPM Gantt]
        [RCPS Table]   [RCPS Gantt]
        """
        # Create main container with 2 columns (left: tables, right: gantt charts)
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid weights for content-based table sizing
        main_frame.grid_rowconfigure(0, weight=1)  # CPM row
        main_frame.grid_rowconfigure(1, weight=1)  # RCPS row
        main_frame.grid_columnconfigure(0, weight=0)  # Tables column - fixed size based on content
        main_frame.grid_columnconfigure(1, weight=1)  # Gantt column - fills remaining space
        
        # Create compact tables (without timeline columns to save space)
        cpm_compact = self.create_compact_table(cpm_table)
        rcps_compact = self.create_compact_table(rcps_table)
        
        # Left side: Compact tables with fixed width
        self.display_compact_table_fixed_width(main_frame, cpm_compact, "Initial CPM-based Plan", col=0, row=0)
        self.display_compact_table_fixed_width(main_frame, rcps_compact, "Resource-Constrained Schedule (RCPS)", col=0, row=1)
        
        # Right side: Gantt charts
        self.display_gantt_chart(main_frame, cpm_table, "CPM Timeline", col=1, row=0, is_cpm=True)
        self.display_gantt_chart(main_frame, rcps_table, "RCPS Timeline", col=1, row=1, is_cpm=False)

    def create_compact_table(self, table):
        """Create a compact version of the table without timeline columns"""
        import pandas as pd
        # Keep only non-timeline columns (non-integer column names)
        compact_columns = [col for col in table.columns if not isinstance(col, int)]
        return table[compact_columns].copy()

    def display_compact_table_fixed_width(self, parent, table, label, col, row=0):
        """Display a compact table with fixed width based on content"""
        # Calculate optimal fixed width for compact table
        num_cols = len(table.columns)
        
        # Determine column width based on table type
        is_cpm = label.lower().startswith("initial cpm")
        if is_cpm:
            # CPM has 6 columns (no AS column)
            col_width = 42  # Slightly larger for readability
            total_width = 6 * col_width + 20  # 272px + padding
        else:
            # RCPS has 7 columns (includes AS column)
            col_width = 38  # Balanced size
            total_width = 7 * col_width + 20  # 286px + padding
        
        # Create frame with fixed width
        frame = ttk.Frame(parent, width=total_width)
        frame.grid(row=row, column=col, sticky="ns", padx=5, pady=5)  # Only stretch vertically
        frame.grid_propagate(False)  # Prevent frame from shrinking to content
        
        # Add label
        label_widget = ttk.Label(frame, text=label, font=("Arial", 11, "bold"))
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Use tksheet for the table
        from tksheet import Sheet
        
        pretty_names = {
            'id': 'ID', 'duration': 'Dur', 'resource': 'Res',
            'early_start': 'ES', 'late_finish': 'LF', 'float': 'Float',
            'actual_start': 'AS'
        }
        
        display_columns = list(table.columns)
        display_headers = [pretty_names.get(col, str(col)) for col in display_columns]
        
        # Prepare data and colors
        data = []
        cell_colors = []
        
        for row_idx, row in enumerate(table.iterrows()):
            row_obj = row[1]
            row_data = [str(row_obj[col]) if row_obj[col] != '' else '' for col in display_columns]
            data.append(row_data)
            
            # Color coding for compact table
            row_colors = []
            for col_idx, col in enumerate(display_columns):
                if col == 'id' and row_obj['id'] not in ['RA', 'RS'] and 'float' in row_obj and row_obj['float'] == 0:
                    row_colors.append('#ffcccb')  # Light red for critical activities
                elif col == 'actual_start' and 'early_start' in row_obj and 'actual_start' in row_obj:
                    try:
                        if int(row_obj['actual_start']) > int(row_obj['early_start']):
                            row_colors.append('#ffd580')  # Yellow for delays
                        else:
                            row_colors.append('white')
                    except:
                        row_colors.append('white')
                else:
                    row_colors.append('white')
            cell_colors.append(row_colors)
        
        # Create sheet
        sheet = Sheet(frame, data=data, headers=display_headers,
                     show_x_scrollbar=False, show_y_scrollbar=True,
                     show_row_index=False, outline_thickness=1)
        
        # Apply colors
        try:
            for r, row_colors in enumerate(cell_colors):
                for c, color in enumerate(row_colors):
                    sheet.highlight_cells(row=r, column=c, bg=color, fg='black', redraw=False)
            sheet.redraw()
        except:
            pass
        
        sheet.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Set fixed column widths
        widths = [col_width] * len(display_columns)
        sheet.set_column_widths(widths)

    def display_compact_schedule_table(self, parent, table, label, col, row=0):
        """Display a compact schedule table without timeline columns"""
        # Create frame for this table
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Add label
        label_widget = ttk.Label(frame, text=label, font=("Arial", 11, "bold"))
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Use tksheet for the table
        from tksheet import Sheet
        
        pretty_names = {
            'id': 'ID', 'duration': 'Dur', 'resource': 'Res',
            'early_start': 'ES', 'late_finish': 'LF', 'float': 'Float',
            'actual_start': 'AS'
        }
        
        display_columns = list(table.columns)
        display_headers = [pretty_names.get(col, str(col)) for col in display_columns]
        
        # Prepare data and colors
        data = []
        cell_colors = []
        
        for row_idx, row in enumerate(table.iterrows()):
            row_obj = row[1]
            row_data = [str(row_obj[col]) if row_obj[col] != '' else '' for col in display_columns]
            data.append(row_data)
            
            # Color coding for compact table
            row_colors = []
            for col_idx, col in enumerate(display_columns):
                if col == 'id' and row_obj['id'] not in ['RA', 'RS'] and 'float' in row_obj and row_obj['float'] == 0:
                    row_colors.append('#ffcccb')  # Light red for critical activities
                elif col == 'actual_start' and 'early_start' in row_obj and 'actual_start' in row_obj:
                    try:
                        if int(row_obj['actual_start']) > int(row_obj['early_start']):
                            row_colors.append('#ffd580')  # Yellow for delays
                        else:
                            row_colors.append('white')
                    except:
                        row_colors.append('white')
                else:
                    row_colors.append('white')
            cell_colors.append(row_colors)
        
        # Create sheet
        sheet = Sheet(frame, data=data, headers=display_headers,
                     show_x_scrollbar=False, show_y_scrollbar=True,
                     show_row_index=False, outline_thickness=1)
        
        # Apply colors
        try:
            for r, row_colors in enumerate(cell_colors):
                for c, color in enumerate(row_colors):
                    sheet.highlight_cells(row=r, column=c, bg=color, fg='black', redraw=False)
            sheet.redraw()
        except:
            pass
        
        sheet.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Add automatic column width adjustment for compact tables
        def adjust_compact_column_widths(event=None):
            frame.update_idletasks()
            frame_width = frame.winfo_width() or 300  # fallback for small tables
            
            num_cols = len(display_columns)
            if num_cols == 0:
                return
                
            # For compact tables, distribute width equally with minimum sizes
            min_col_width = 25  # Very minimum readable width
            max_col_width = 70  # Maximum to prevent oversized columns
            
            # Calculate optimal width per column
            available_width = max(frame_width - 20, num_cols * min_col_width)  # 20px padding
            ideal_col_width = available_width // num_cols
            col_width = max(min_col_width, min(ideal_col_width, max_col_width))
            
            # Set all columns to the same width
            widths = [col_width] * num_cols
            sheet.set_column_widths(widths)

        # Bind to frame resize events for live adjustment
        frame.bind("<Configure>", adjust_compact_column_widths)
        # Initial adjustment after rendering
        frame.after(100, adjust_compact_column_widths)

    def display_gantt_chart(self, parent, table, label, col, row, is_cpm=False):
        """Display Gantt chart for the schedule"""
        # Create frame for this chart
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Add label
        label_widget = ttk.Label(frame, text=label, font=("Arial", 11, "bold"))
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Create matplotlib figure with larger size for better fit
        # Increased width from 8 to 12 to better utilize the chart field space
        fig = Figure(figsize=(12, 4), dpi=80)
        ax = fig.add_subplot(111)
        
        # Adjust subplot parameters for better space utilization
        fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
        
        # Filter out resource rows
        activities = table[~table['id'].isin(['RA', 'RS'])].copy()
        
        if activities.empty:
            ax.text(0.5, 0.5, 'No activities to display', ha='center', va='center', transform=ax.transAxes)
        else:
            # Get timeline columns and max time
            timeline_cols = [col for col in table.columns if isinstance(col, int)]
            max_time = max(timeline_cols) if timeline_cols else 10
            
            # Prepare Gantt data
            y_pos = range(len(activities))
            activity_labels = activities['id'].tolist()
            
            # Plot bars for each activity
            for i, (_, activity) in enumerate(activities.iterrows()):
                try:
                    if is_cpm:
                        start = int(activity['early_start'])
                        duration = int(activity['duration'])
                        color = '#90EE90' if activity['float'] == 0 else '#ADD8E6'  # Green for critical, blue for non-critical
                    else:
                        # RCPS: use actual_start if available
                        start = int(activity['actual_start']) if 'actual_start' in activity and activity['actual_start'] != '' else int(activity['early_start'])
                        duration = int(activity['duration'])
                        
                        # Color coding for RCPS
                        if 'actual_start' in activity and 'early_start' in activity:
                            try:
                                if int(activity['actual_start']) > int(activity['early_start']):
                                    color = '#FFD700'  # Gold for delayed
                                else:
                                    color = '#90EE90'  # Green for on-time
                            except:
                                color = '#ADD8E6'  # Blue default
                        else:
                            color = '#ADD8E6'
                    
                    ax.barh(i, duration, left=start, height=0.6, color=color, alpha=0.8, edgecolor='black')
                    
                    # Add activity ID on the bar
                    ax.text(start + duration/2, i, activity['id'], ha='center', va='center', fontsize=8, fontweight='bold')
                    
                except Exception as e:
                    print(f"Error plotting activity {activity['id']}: {e}")
                    continue
            
            # Customize the chart
            ax.set_yticks(y_pos)
            ax.set_yticklabels(activity_labels)
            ax.set_xlabel('Time')
            ax.set_xlim(0, max_time)
            ax.grid(True, alpha=0.3)
            ax.invert_yaxis()  # Activities from top to bottom
            
            # Add resource utilization if available
            if 'RS' in table['id'].values:
                rs_row = table[table['id'] == 'RS'].iloc[0]
                resource_usage = []
                time_points = []
                for col in timeline_cols:
                    if col in rs_row and rs_row[col] != '':
                        try:
                            resource_usage.append(float(rs_row[col]))
                            time_points.append(col)
                        except:
                            pass
                
                if resource_usage:
                    # Create secondary y-axis for resource usage
                    ax2 = ax.twinx()
                    ax2.plot(time_points, resource_usage, 'r--', linewidth=2, alpha=0.7, label='Resource Usage')
                    ax2.set_ylabel('Resource Usage', color='red')
                    ax2.tick_params(axis='y', labelcolor='red')
        
        # Apply tight layout for optimal space usage
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    # COMMENTED OUT: Original display_schedule_table method preserved below
    # def display_schedule_table(self, parent, table, label, col, row=0):

