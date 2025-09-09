#!/usr/bin/env python3
"""
RCPS Tab Module

Displays resource-constrained project scheduling (RCPS) results and resource utilization charts.
This module provides GUI componen            # Display hybrid layout with tables and Gantt charts
            print("[DEBUG] Using HYBRID LAYOUT with tables + Gantt charts")
            self.display_hybrid_schedule_view(self.tables_frame, cpm_table_aligned, rcps_table, df_gantt)
            
#!/usr/bin/env python3
"""
RCPS Tab Module

Displays resource-constrained project scheduling (RCPS) results and resource utilization charts.
This module provides GUI components for visualizing resource-constrained project schedules,
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

    def prepare_crashing_dataframe(self):
        """
        Creates a DataFrame optimized for RCPS crashing analysis by combining:
        - RCPS schedule data (with actual_start times)
        - Original crashing attributes from input data (min_duration, crash_cost, normal_cost)
        
        Returns:
            DataFrame with all attributes needed for resource-aware crashing
        """
        if not hasattr(self, 'rcps_table_data') or self.rcps_table_data is None:
            print("[DEBUG] RCPS data not available. Run RCPS analysis first.")
            return None
            
        # Start with RCPS results (which has actual start times)
        crashing_df = self.rcps_table_data.copy()
        
        # Filter out resource rows
        crashing_df = crashing_df[~crashing_df['id'].isin(['RA', 'RS'])].copy()
        
        # Add indicator column to track that we're using RCPS data
        crashing_df['is_rcps_based'] = True
        
        # Map necessary attributes for crashing
        if 'actual_start' in crashing_df.columns:
            # Replace early_start with actual_start for crashing (critical for resource-aware crashing)
            crashing_df['original_early_start'] = crashing_df['early_start']
            crashing_df['early_start'] = crashing_df['actual_start']
            
            # Calculate early_finish based on new early_start
            crashing_df['early_finish'] = crashing_df.apply(
                lambda row: row['early_start'] + row['duration'], axis=1
            )
        
        # Get original input data where crashing attributes might exist
        input_data = None
        
        # Try to get input data from the input tab
        if hasattr(self.main_window, 'input_tab') and self.main_window.input_tab:
            try:
                activities_data = self.main_window.input_tab.get_activities_data()
                if activities_data:
                    input_data = pd.DataFrame(activities_data)
                    print(f"[DEBUG] Retrieved input data from input tab: {len(input_data)} activities")
            except Exception as e:
                print(f"[DEBUG] Could not get input data from input tab: {e}")
        
        # Fallback: try main_window.input_data if it exists
        if input_data is None:
            input_data = getattr(self.main_window, 'input_data', None)
            if input_data is not None:
                print(f"[DEBUG] Using fallback input_data from main_window")
        
        # Merge crashing attributes from original data if they exist
        if input_data is not None and isinstance(input_data, pd.DataFrame) and 'id' in input_data.columns:
            # Identify crashing columns in the input data
            crashing_cols = ['id']  # Always include ID for merging
            for col in ['min_duration', 'crash_cost', 'normal_cost']:
                if col in input_data.columns:
                    crashing_cols.append(col)
                    
            if len(crashing_cols) > 1:  # If we found at least one crashing attribute
                # Merge only the crashing attributes
                crashing_df = pd.merge(
                    crashing_df,
                    input_data[crashing_cols],
                    on='id',
                    how='left'
                )
                print(f"[DEBUG] Merged crashing attributes from input data: {crashing_cols[1:]}")
        
        # Ensure all required crashing attributes exist with sensible defaults
        required_crashing_attrs = {
            'min_duration': 1,  # Default to 1 time unit minimum
            'crash_cost': 100,  # Default crash cost per time unit
            'normal_cost': 50   # Default normal cost per time unit
        }
        
        for attr, default_value in required_crashing_attrs.items():
            if attr not in crashing_df.columns:
                # Column doesn't exist, create it with default values
                crashing_df[attr] = default_value
                print(f"[DEBUG] Added missing crashing attribute '{attr}' with default value {default_value}")
            else:
                # Column exists - check for null/empty values and fill only those
                # Convert to numeric first, handling non-numeric values
                crashing_df[attr] = pd.to_numeric(crashing_df[attr], errors='coerce')
                null_count = crashing_df[attr].isnull().sum()
                if null_count > 0:
                    crashing_df[attr] = crashing_df[attr].fillna(default_value)
                    print(f"[DEBUG] Filled {null_count} null values in '{attr}' with default value {default_value}")
        
        print(f"[DEBUG] Prepared RCPS crashing DataFrame with {len(crashing_df)} activities")
        return crashing_df

    def get_resource_limit(self):
        """Return the current resource limit setting"""
        return self.resource_limit_var.get()

    def get_rcps_analyzer_for_crashing(self):
        """
        Create an analyzer object compatible with the project crashing core.
        This analyzer uses RCPS-adjusted times instead of pure CPM times.
        
        Returns:
            analyzer object with 'G' or 'graph' attribute containing the RCPS network graph
        """
        if not hasattr(self, 'rcps_network_graph') or self.rcps_network_graph is None:
            print("[ERROR] No RCPS network graph available. Run RCPS analysis first.")
            return None
            
        if not hasattr(self, 'rcps_analyzer') or self.rcps_analyzer is None:
            print("[ERROR] No RCPS analyzer available. Run RCPS analysis first.")
            return None
        
        # Create a wrapper object that mimics the original analyzer but with RCPS data
        class RCPSAnalyzerWrapper:
            def __init__(self, rcps_graph, original_analyzer):
                self.G = rcps_graph  # Use RCPS-adjusted graph
                self.graph = rcps_graph  # Fallback attribute name
                # Copy other attributes from original analyzer
                if hasattr(original_analyzer, 'network_builder'):
                    self.network_builder = original_analyzer.network_builder
                if hasattr(original_analyzer, 'activities'):
                    self.activities = original_analyzer.activities
        
        rcps_analyzer_wrapper = RCPSAnalyzerWrapper(self.rcps_network_graph, self.rcps_analyzer)
        
        print(f"[DEBUG] Created RCPS analyzer wrapper with graph containing {len(self.rcps_network_graph.nodes())} nodes")
        print(f"[DEBUG] RCPS analyzer wrapper ready for crashing core")
        
        return rcps_analyzer_wrapper

    def set_rcps_crashing_tab(self, tab_instance):
        """Set reference to RCPS Crashing tab for data sharing"""
        self.rcps_crashing_tab = tab_instance
        print("[DEBUG] RCPS tab linked to RCPS Crashing tab")

    def _build_rcps_network_graph(self, rcps_table, df_gantt, analyzer):
        """Convert RCPS table back to a NetworkX graph with fully recalculated scheduling attributes based on actual_start."""
        import networkx as nx
        
        print(f"[DEBUG] Starting network graph build with {len(rcps_table)} activities")
        G = nx.DiGraph()
        
        # 1. Add nodes with base data (duration, actual_start)
        for _, row in rcps_table.iterrows():
            if row['id'] not in ['RA', 'RS']:
                actual_start = row['actual_start'] if 'actual_start' in row and row['actual_start'] != '' else row['early_start']
                G.add_node(row['id'], 
                           duration=row['duration'],
                           actual_start=actual_start,
                           original_late_finish=row['late_finish'],
                           original_float=row['float'])
        
        print(f"[DEBUG] Added {len(G.nodes())} nodes to graph")

        # 2. Add edges from the original analyzer graph
        if hasattr(analyzer, 'G') and analyzer.G is not None:
            for u, v in analyzer.G.edges():
                if u in G.nodes() and v in G.nodes():
                    G.add_edge(u, v)
            print(f"[DEBUG] Added {len(G.edges())} edges to graph")
        else:
            print("[DEBUG] No analyzer graph available for edges")
        
        # 3. Forward Pass: Recalculate ES and EF based on actual_start
        for node in G.nodes():
            G.nodes[node]['ES'] = G.nodes[node]['actual_start']
            G.nodes[node]['EF'] = G.nodes[node]['ES'] + G.nodes[node]['duration']
            
        rcps_project_duration = max(nx.get_node_attributes(G, 'EF').values()) if G.nodes() else 0
        print(f"[DEBUG] RCPS Project Duration: {rcps_project_duration}")

        # 4. Backward Pass: Recalculate LF and LS
        for node in G.nodes():
            if not list(G.successors(node)):  # Sink nodes
                G.nodes[node]['LF'] = rcps_project_duration
            else:
                G.nodes[node]['LF'] = float('inf')

        # Iterate in reverse topological order
        try:
            for node in reversed(list(nx.topological_sort(G))):
                # For non-sink nodes, LF is min(LS of successors)
                if list(G.successors(node)):
                    min_succ_ls = min([G.nodes[succ]['LF'] - G.nodes[succ]['duration'] for succ in G.successors(node)])
                    G.nodes[node]['LF'] = min_succ_ls
                
                # Calculate LS
                G.nodes[node]['LS'] = G.nodes[node]['LF'] - G.nodes[node]['duration']
        except nx.NetworkXUnfeasible:
            print("[ERROR] Graph has cycles, cannot perform topological sort for backward pass.")
            # Fallback for cyclic graphs
            for node in G.nodes():
                G.nodes[node]['LF'] = rcps_project_duration
                G.nodes[node]['LS'] = G.nodes[node]['LF'] - G.nodes[node]['duration']

        # 5. Recalculate Float
        for node in G.nodes():
            G.nodes[node]['float'] = G.nodes[node]['LS'] - G.nodes[node]['ES']

        # 6. Add crashing attributes
        crashing_df = self.prepare_crashing_dataframe()
        if crashing_df is not None:
            print("[DEBUG] Adding crashing attributes from prepared DataFrame")
            for _, row in crashing_df.iterrows():
                if row['id'] in G.nodes():
                    node_id = row['id']
                    # Add crashing attributes
                    if 'min_duration' in row and pd.notna(row['min_duration']):
                        G.nodes[node_id]['min_duration'] = row['min_duration']
                    if 'crash_cost' in row and pd.notna(row['crash_cost']):
                        G.nodes[node_id]['crash_cost'] = row['crash_cost']
                    if 'normal_cost' in row and pd.notna(row['normal_cost']):
                        G.nodes[node_id]['normal_cost'] = row['normal_cost']
                    if 'resource' in row and pd.notna(row['resource']):
                        G.nodes[node_id]['resource'] = row['resource']
        
        # Ensure all nodes have required crashing attributes with sensible defaults
        required_attrs = {
            'min_duration': 1,
            'crash_cost': 100,
            'normal_cost': 50
        }
        
        for node_id in G.nodes():
            if node_id not in ['START', 'END', 'RA', 'RS']:
                for attr, default_value in required_attrs.items():
                    if attr not in G.nodes[node_id] or pd.isna(G.nodes[node_id][attr]):
                        G.nodes[node_id][attr] = default_value
        
        print(f"[DEBUG] Built RCPS network graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
        return G
