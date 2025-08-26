#!/usr/bin/env python3
"""
RCPS Tab Module

Displays resource-constrained project scheduling (RCPS) results and resource utilization charts.
This module provides GUI components for v            # Display hybrid layout with tables and Gantt charts
            print("[DEBUG] Using HYBRID LAYOUT with tables + Gantt charts")
            self.display_hybrid_schedule_view(self.tables_frame, cmp_table_aligned, rcps_table, df_gantt)
            
            # Store data for fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')alizing resource-constrained project schedules,
comparing CPM/PERT theoretical schedules with realistic resource-limited schedules.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import sys
from pathlib import Path

# Add project root to path for imports
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
        self.cmp_table_data = None
        self.rcps_table_data = None
        self.gantt_data = None
        self.create_tab()

    def create_tab(self):
        """Create the RCPS tab and its components"""
        self.rcps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rcps_frame, text="RCPS Schedule")
        self.create_control_frame()
        self.tables_frame = ttk.Frame(self.rcps_frame)
        self.tables_frame.pack(fill=tk.BOTH, expand=True)

    def create_control_frame(self):
        """Create the control panel with resource limit and priority rule settings"""
        control_frame = ttk.Frame(self.rcps_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Resource limit control
        ttk.Label(control_frame, text="Resource Limit:").pack(side=tk.LEFT, padx=5)
        self.resource_limit_var = tk.IntVar(value=5)
        ttk.Entry(control_frame, textvariable=self.resource_limit_var, width=5).pack(side=tk.LEFT)

        # Priority Rule Dropdown
        ttk.Label(control_frame, text="Priority Rule:").pack(side=tk.LEFT, padx=(20, 5))
        self.priority_rule_var = tk.StringVar(value='minimum_slack')
        priority_options = ['minimum_slack', 'shortest_duration', 'earliest_start']
        self.priority_rule_menu = ttk.Combobox(
            control_frame, 
            textvariable=self.priority_rule_var, 
            values=priority_options, 
            state='readonly', 
            width=18
        )
        self.priority_rule_menu.pack(side=tk.LEFT)

        # Run RCPS button
        ttk.Button(control_frame, text="Run RCPS", command=self.run_rcps).pack(side=tk.LEFT, padx=10)
        
        # Fullscreen Comparison button
        self.fullscreen_btn = ttk.Button(control_frame, text="Fullscreen Comparison", 
                                       command=self.open_fullscreen_comparison, state='disabled')
        self.fullscreen_btn.pack(side=tk.LEFT, padx=10)

    def validate_rcps_inputs(self, df_gantt, resource_limit, priority_rule):
        """
        Comprehensive input validation for RCPS analysis
        
        Args:
            df_gantt: Project data DataFrame
            resource_limit: Maximum available resources
            priority_rule: Scheduling priority rule
            
        Raises:
            ValueError: If any input is invalid
        """
        errors = []
        
        # Data validation
        if df_gantt is None:
            errors.append("No project data available. Please run CPM or PERT analysis first.")
        elif df_gantt.empty:
            errors.append("Project data is empty. Please load valid project data.")
        else:
            # Check required columns
            required_columns = ['id', 'duration', 'resource', 'early_start', 'late_finish', 'float']
            missing_columns = [col for col in required_columns if col not in df_gantt.columns]
            if missing_columns:
                errors.append(f"Missing required data columns: {', '.join(missing_columns)}")
            
            # Check for valid data types
            try:
                pd.to_numeric(df_gantt['duration'], errors='coerce')
                pd.to_numeric(df_gantt['resource'], errors='coerce')
            except Exception:
                errors.append("Invalid data types in duration or resource columns")
        
        # Resource validation  
        if not isinstance(resource_limit, (int, float)) or resource_limit <= 0:
            errors.append("Resource limit must be a positive number")
        elif df_gantt is not None and 'resource' in df_gantt.columns:
            try:
                max_resource = pd.to_numeric(df_gantt['resource'], errors='coerce').max()
                if not pd.isna(max_resource) and resource_limit < max_resource:
                    errors.append(f"Resource limit ({resource_limit}) cannot be less than maximum single activity resource requirement ({max_resource})")
            except Exception:
                pass  # Skip validation if resource column has issues
                
        # Priority rule validation
        valid_rules = ['minimum_slack', 'shortest_duration', 'earliest_start']
        if priority_rule not in valid_rules:
            errors.append(f"Invalid priority rule '{priority_rule}'. Valid options: {', '.join(valid_rules)}")
        
        if errors:
            raise ValueError("\\n".join(errors))

    def run_rcps(self):
        """Execute RCPS analysis with comprehensive error handling"""
        try:
            # Get input parameters
            resource_limit = self.resource_limit_var.get()
            priority_rule = self.priority_rule_var.get()
            df_gantt = self.main_window.current_data
            
            # Validate inputs
            self.validate_rcps_inputs(df_gantt, resource_limit, priority_rule)
            
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
            
            print(f"[DEBUG] RCPS Analysis starting - Mode: {analysis_mode}, Resource Limit: {resource_limit}, Priority: {priority_rule}")
            
            if analysis_mode == 'probabilistic':
                analyzer = self.main_window.pert_analyzer
            else:
                analyzer = self.main_window.cpm_analyzer
            
            if analyzer is None:
                raise ValueError("Analysis engine not available. Please run CPM or PERT analysis first.")
            
            # Generate CPM and RCPS tables using the correct analyzer
            cpm_table, _, _ = analyzer.build_cpm_schedule_table(df_gantt, resource_limit)
            rcps_table, _, _ = analyzer.rcps_heuristic_schedule_table(df_gantt, resource_limit, priority_rule=priority_rule)
            
            # Fill timeline columns with resource usage for both CPM and RCPS
            timeline_cols = [col for col in cpm_table.columns if isinstance(col, int)]
            
            # CPM Table: fill timeline cells with resource usage for scheduled periods
            self._fill_timeline_data(cpm_table, timeline_cols, is_rcps=False)
            
            # RCPS Table: fill timeline cells with resource usage for scheduled periods
            self._fill_timeline_data(rcps_table, timeline_cols, is_rcps=True)
            
            # Clear previous content
            for widget in self.tables_frame.winfo_children():
                widget.destroy()
            
            # Align CPM table columns to RCPS columns, but remove 'actual_start' (AS) from CPM table
            rcps_columns = list(rcps_table.columns)
            cpm_columns = [col for col in rcps_columns if col != 'actual_start']
            cpm_table_aligned = cpm_table.reindex(columns=cpm_columns, fill_value='')
            
            # Display hybrid layout with tables and Gantt charts
            print("[DEBUG] Using HYBRID LAYOUT with tables + Gantt charts")
            self.display_hybrid_schedule_view(self.tables_frame, cpm_table_aligned, rcps_table, df_gantt)
            
            # Store data for fullscreen comparison and enable button
            self.cmp_table_data = cpm_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
        except ValueError as ve:
            # User input errors - show user-friendly message
            messagebox.showerror("Input Error", str(ve))
            
        except Exception as e:
            # Unexpected system errors
            import traceback
            import logging
            
            # Log detailed error for debugging
            logging.error(f"RCPS Analysis Error: {str(e)}", exc_info=True)
            print(f"RCPS Error Details:\\n{traceback.format_exc()}")
            
            # Show user-friendly error message
            messagebox.showerror("Analysis Error", 
                f"RCPS analysis encountered an unexpected error.\\n\\n"
                f"Error: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}\\n\\n"
                f"Please check your project data and try again.")

    def _fill_timeline_data(self, table, timeline_cols, is_rcps=False):
        """Helper method to fill timeline columns with resource usage data"""
        for idx, row in table.iterrows():
            if row['id'] in ['RA', 'RS']:
                continue
            try:
                if is_rcps and 'actual_start' in row and row['actual_start'] != '':
                    start = int(row['actual_start'])
                else:
                    start = int(row['early_start'])
                    
                dur = int(row['duration'])
                res = int(row['resource'])
                
                for t in timeline_cols:
                    if start < t <= start + dur:
                        table.at[idx, t] = res
            except Exception:
                # Skip problematic rows rather than failing entirely
                continue

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
        self.display_gantt_chart(main_frame, cpm_table, "CPM Timeline", col=1, row=0, is_cmp=True)
        self.display_gantt_chart(main_frame, rcps_table, "RCPS Timeline", col=1, row=1, is_cmp=False)

    def create_compact_table(self, table):
        """Create a compact version of the table without timeline columns"""
        # Keep only non-timeline columns (non-integer column names)
        compact_columns = [col for col in table.columns if not isinstance(col, int)]
        return table[compact_columns].copy()

    def display_compact_table_fixed_width(self, parent, table, label, col, row=0):
        """Display a compact table with fixed width based on content"""
        # Calculate optimal fixed width for compact table
        num_cols = len(table.columns)
        
        # Determine column width based on table type
        is_cmp = label.lower().startswith("initial cmp")
        if is_cmp:
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
        try:
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
            
        except ImportError:
            # Fallback to basic display if tksheet not available
            ttk.Label(frame, text="Table display requires tksheet package").grid(row=1, column=0)

    def display_gantt_chart(self, parent, table, label, col, row, is_cmp=False):
        """Display Gantt chart for the schedule"""
        # Create frame for this chart
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Add label
        label_widget = ttk.Label(frame, text=label, font=("Arial", 11, "bold"))
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 4), dpi=80)
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
                    if is_cmp:
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
        
        # Apply tight layout for optimal space usage
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def open_fullscreen_comparison(self):
        """Open a fullscreen window with stacked Gantt charts for comparison"""
        if self.cmp_table_data is None or self.rcps_table_data is None:
            messagebox.showwarning("No Data", "Please run RCPS analysis first to generate comparison data.")
            return
        
        # Get the actual tkinter root window
        root_widget = self.rcps_frame
        while root_widget.master:
            root_widget = root_widget.master
        
        # Create fullscreen window
        fullscreen_window = FullscreenComparisonWindow(
            root_widget, 
            self.cmp_table_data, 
            self.rcps_table_data, 
            self.gantt_data
        )


class FullscreenComparisonWindow:
    """Fullscreen window for comparing CPM and RCPS Gantt charts side by side"""
    
    def __init__(self, parent, cmp_table, rcps_table, gantt_data):
        self.parent = parent
        self.cmp_table = cmp_table
        self.rcps_table = rcps_table
        self.gantt_data = gantt_data
        
        # Create the fullscreen window
        self.window = tk.Toplevel(parent)
        self.window.title("RCPS Gantt Chart Comparison - Fullscreen")
        self.window.state('zoomed')  # Maximize window on Windows
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        # Create the comparison interface
        self.create_comparison_interface()
        
        # Focus the window
        self.window.focus_force()
        self.window.lift()
    
    def create_comparison_interface(self):
        """Create the main comparison interface with stacked Gantt charts"""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="CPM vs RCPS Schedule Comparison", 
                              font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Close button
        close_btn = ttk.Button(title_frame, text="Close", command=self.close_window)
        close_btn.pack(side=tk.RIGHT)
        
        # Create stacked charts container
        charts_frame = ttk.Frame(main_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for two rows (CPM on top, RCPS on bottom)
        charts_frame.grid_rowconfigure(0, weight=1)  # CPM chart
        charts_frame.grid_rowconfigure(1, weight=1)  # RCPS chart
        charts_frame.grid_columnconfigure(0, weight=1)  # Single column
        
        # Create the two Gantt charts
        self.create_fullscreen_gantt_chart(charts_frame, self.cmp_table, 
                                         "CPM Timeline (Theoretical)", row=0, is_cmp=True)
        self.create_fullscreen_gantt_chart(charts_frame, self.rcps_table, 
                                         "RCPS Timeline (Resource-Constrained)", row=1, is_cmp=False)
    
    def create_fullscreen_gantt_chart(self, parent, table, title, row, is_cmp=False):
        """Create a large Gantt chart optimized for fullscreen viewing"""
        # Create frame for this chart
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="nsew", padx=5, pady=5)
        
        # Chart title
        title_label = tk.Label(frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create matplotlib figure with larger size for fullscreen
        fig = Figure(figsize=(16, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        # Adjust subplot parameters for better space utilization
        fig.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.1)
        
        # Filter out resource rows
        activities = table[~table['id'].isin(['RA', 'RS'])].copy()
        
        if activities.empty:
            ax.text(0.5, 0.5, 'No activities to display', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
        else:
            # Get timeline columns and max time
            timeline_cols = [col for col in table.columns if isinstance(col, int)]
            max_time = max(timeline_cols) if timeline_cols else 10
            
            # Prepare Gantt data
            y_pos = range(len(activities))
            activity_labels = activities['id'].tolist()
            
            # Calculate bar height based on number of activities for better visibility
            bar_height = min(0.8, 10 / len(activities)) if len(activities) > 10 else 0.8
            
            # Plot bars for each activity
            for i, (_, activity) in enumerate(activities.iterrows()):
                try:
                    if is_cmp:
                        start = int(activity['early_start'])
                        duration = int(activity['duration'])
                        # Enhanced color coding for CPM
                        if activity['float'] == 0:
                            color = '#FF6B6B'  # Red for critical path
                            alpha = 0.9
                        else:
                            color = '#4ECDC4'  # Teal for non-critical
                            alpha = 0.7
                    else:
                        # RCPS: use actual_start if available
                        start = int(activity['actual_start']) if 'actual_start' in activity and activity['actual_start'] != '' else int(activity['early_start'])
                        duration = int(activity['duration'])
                        
                        # Enhanced color coding for RCPS with delay indicators
                        if 'actual_start' in activity and 'early_start' in activity:
                            try:
                                early_start = int(activity['early_start'])
                                actual_start = int(activity['actual_start'])
                                delay = actual_start - early_start
                                
                                if delay > 0:
                                    # Color intensity based on delay amount
                                    if delay >= 3:
                                        color = '#FF4757'  # Bright red for significant delay
                                        alpha = 0.9
                                    elif delay >= 1:
                                        color = '#FFA726'  # Orange for moderate delay
                                        alpha = 0.8
                                    else:
                                        color = '#FFD93D'  # Yellow for minor delay
                                        alpha = 0.7
                                else:
                                    color = '#6BCF7F'  # Green for on-time
                                    alpha = 0.8
                            except:
                                color = '#74B9FF'  # Blue default
                                alpha = 0.7
                        else:
                            color = '#74B9FF'  # Blue default
                            alpha = 0.7
                    
                    # Draw the bar
                    bar = ax.barh(i, duration, left=start, height=bar_height, 
                                color=color, alpha=alpha, edgecolor='black', linewidth=1)
                    
                    # Add activity ID and duration text on the bar
                    text_x = start + duration/2
                    text_y = i
                    
                    # Activity ID (bold)
                    ax.text(text_x, text_y + 0.1, activity['id'], ha='center', va='center', 
                           fontsize=10, fontweight='bold', color='black')
                    
                    # Duration (smaller text below ID)
                    ax.text(text_x, text_y - 0.1, f"({duration})", ha='center', va='center', 
                           fontsize=8, color='black')
                    
                    # Add delay indicator for RCPS
                    if not is_cmp and 'actual_start' in activity and 'early_start' in activity:
                        try:
                            delay = int(activity['actual_start']) - int(activity['early_start'])
                            if delay > 0:
                                ax.text(start - 0.5, i, f"+{delay}", ha='right', va='center', 
                                       fontsize=8, color='red', fontweight='bold')
                        except:
                            pass
                    
                except Exception as e:
                    print(f"Error plotting activity {activity['id']}: {e}")
                    continue
            
            # Customize the chart with better formatting
            ax.set_yticks(y_pos)
            ax.set_yticklabels(activity_labels, fontsize=10)
            ax.set_xlabel('Time (Days)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Activities', fontsize=12, fontweight='bold')
            ax.set_xlim(0, max_time + 1)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.invert_yaxis()  # Activities from top to bottom
            
            # Add title to the subplot
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
            
            # Add legend for color coding
            if is_cmp:
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='#FF6B6B', alpha=0.9, label='Critical Path'),
                    Patch(facecolor='#4ECDC4', alpha=0.7, label='Non-Critical')
                ]
                ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
            else:
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='#6BCF7F', alpha=0.8, label='On Time'),
                    Patch(facecolor='#FFD93D', alpha=0.7, label='Minor Delay'),
                    Patch(facecolor='#FFA726', alpha=0.8, label='Moderate Delay'),
                    Patch(facecolor='#FF4757', alpha=0.9, label='Significant Delay')
                ]
                ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        # Apply tight layout for optimal space usage
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar for zooming and panning
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
    
    def close_window(self):
        """Close the fullscreen window"""
        self.window.destroy()
