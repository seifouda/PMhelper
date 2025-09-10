#!/usr/bin/env python3
"""
RCPS Tab Module

Displays resource-constrained project scheduling (RCPS) results and resource utilization charts.
This module provides GUI components for v            # Displa                                  # Store data for f            # Store            # Store            # S            # Displ                     # PRODUCTION CHANGE: Use large tables layout instead of hybrid
            print("[DEBUG] Using LARGE TABLES LAYOUT with full timeline data")
            self.display_large_tables_view(self.tables_frame, cmp_table_aligned, rcps_table, df_gantt)
            
            # COMMENTED FOR FUTURE USE: Hybrid layout with small tables + Gantt charts
            # print("[DEBUG] Using HYBRID LAYOUT with tables + Gantt charts")
            # self.display_hybrid_schedule_view(self.tables_frame, cmp_table_aligned, rcps_table, df_gantt)
            
            # Store data for fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # Build and store network graph for RCPS Crashing feature
            print("[DEBUG STORAGE] Building network graph for RCPS Crashing...")
            self.rcps_network_graph = self._build_rcps_network_graph(df_gantt)
            self.rcps_analyzer = analyzer
            print(f"[DEBUG STORAGE] Network graph built: {self.rcps_network_graph is not None}")
            print(f"[DEBUG STORAGE] Analyzer stored: {self.rcps_analyzer is not None}")
            
        except ValueError as ve:data for fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # CRITICAL: Build and store network graph for RCPS Crashing
            print("[DEBUG STORAGE] Building and storing network graph for RCPS Crashing...")
            self.rcps_network_graph = self._build_rcps_network_graph(df_gantt, analyzer)
            self.rcps_analyzer = analyzer
            print(f"[DEBUG STORAGE] Network graph stored: {self.rcps_network_graph is not None}")
            print(f"[DEBUG STORAGE] Analyzer stored: {self.rcps_analyzer is not None}")
            
        except ValueError as ve:
            # Display large tables layout with full timeline data
            print("[DEBUG] Using LARGE TABLES LAYOUT with full timeline data")
            self.display_large_tables_view(self.tables_frame, cmp_table_aligned, rcps_table, df_gantt)
            
            # Store data for fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # CRITICAL: Build and store network graph for RCPS Crashing
            print("[DEBUG STORAGE] Building and storing network graph for RCPS Crashing...")
            self.rcps_network_graph = self._build_rcps_network_graph(df_gantt, analyzer)
            self.rcps_analyzer = analyzer
            print(f"[DEBUG STORAGE] Network graph stored: {self.rcps_network_graph is not None}")
            print(f"[DEBUG STORAGE] Analyzer stored: {self.rcps_analyzer is not None}") for fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # Convert RCPS table back to NetworkX graph for RCPS Crashing
            print(f"[DEBUG] About to store RCPS network graph and analyzer")
            try:
                self.rcps_network_graph = self._build_rcps_network_graph(rcps_table, df_gantt, analyzer)
                self.rcps_analyzer = analyzer
                print(f"[DEBUG] RCPS network graph stored: {type(self.rcps_network_graph)}")
                print(f"[DEBUG] RCPS analyzer stored: {type(self.rcps_analyzer)}")
                print(f"[DEBUG] RCPS network graph and analyzer stored for RCPS Crashing")
            except Exception as e:
                print(f"[DEBUG] Error storing RCPS data: {e}")
                import traceback
                traceback.print_exc()
            
        except ValueError as ve:or fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # Convert RCPS table back to NetworkX graph for RCPS Crashing
            print(f"[DEBUG] About to store RCPS network graph and analyzer")
            try:
                self.rcps_network_graph = self._build_rcps_network_graph(rcps_table, df_gantt, analyzer)
                self.rcps_analyzer = analyzer
                print(f"[DEBUG] RCPS network graph stored: {type(self.rcps_network_graph)}")
                print(f"[DEBUG] RCPS analyzer stored: {type(self.rcps_analyzer)}")
                print(f"[DEBUG] RCPS network graph and analyzer stored for RCPS Crashing")
            except Exception as e:
                print(f"[DEBUG] Error storing RCPS data: {e}")
                import traceback
                traceback.print_exc()
            
        except ValueError as ve:or fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # Convert RCPS table back to NetworkX graph for RCPS Crashing
            print(f"[DEBUG] About to store RCPS network graph and analyzer")
            try:
                self.rcps_network_graph = self._build_rcps_network_graph(rcps_table, df_gantt, analyzer)
                self.rcps_analyzer = analyzer
                print(f"[DEBUG] RCPS network graph stored: {type(self.rcps_network_graph)}")
                print(f"[DEBUG] RCPS analyzer stored: {type(self.rcps_analyzer)}")
                print(f"[DEBUG] RCPS network graph and analyzer stored for RCPS Crashing")
            except Exception as e:
                print(f"[DEBUG] Error storing RCPS data: {e}")
                import traceback
                traceback.print_exc()
            
        except ValueError as ve:en comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # Convert RCPS table back to NetworkX graph for RCPS Crashing
            print(f"[DEBUG] About to store RCPS network graph and analyzer")
            try:
                self.rcps_network_graph = self._build_rcps_network_graph(rcps_table, df_gantt, analyzer)
                self.rcps_analyzer = analyzer
                print(f"[DEBUG] RCPS network graph stored: {type(self.rcps_network_graph)}")
                print(f"[DEBUG] RCPS analyzer stored: {type(self.rcps_analyzer)}")
                print(f"[DEBUG] RCPS network graph and analyzer stored for RCPS Crashing")
            except Exception as e:
                print(f"[DEBUG] Error storing RCPS data: {e}")
                import traceback
                traceback.print_exc()
            
        except ValueError as ve:e data for fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # Convert RCPS table back to NetworkX graph for RCPS Crashing
            self.rcps_network_graph = self._build_rcps_network_graph(rcps_table, df_gantt, analyzer)
            self.rcps_analyzer = analyzer
            print(f"[DEBUG] RCPS network graph and analyzer stored for RCPS Crashing")
            
        except ValueError as ve:e data for fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # Convert RCPS table back to NetworkX graph for RCPS Crashing
            self.rcps_network_graph = self._build_rcps_network_graph(rcps_table, df_gantt, analyzer)
            self.rcps_analyzer = analyzer
            print(f"[DEBUG] RCPS network graph and analyzer stored for RCPS Crashing")
            
        except ValueError as ve:
            # Display large tables layout with full timeline data
            print("[DEBUG] Using LARGE TABLES LAYOUT with full timeline data")
            self.display_large_tables_view(self.tables_frame, cmp_table_aligned, rcps_table, df_gantt)
            
            # Store data for fullscreen comparison and enable button
            self.cmp_table_data = cmp_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            
            # Convert RCPS table back to NetworkX graph for RCPS Crashing
            self.rcps_network_graph = self._build_rcps_network_graph(rcps_table, df_gantt, analyzer)
            self.rcps_analyzer = analyzeralizing resource-constrained project schedules,
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
from src.pmhelper.core.rcps_analyzer import RCPSAnalyzer

# Import tksheet for advanced table display
try:
    from tksheet import Sheet
    TKSHEET_AVAILABLE = True
except ImportError:
    TKSHEET_AVAILABLE = False
    print("Warning: tksheet not available - using basic table display")

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
        # Add storage for RCPS network data
        self.rcps_network_graph = None
        self.rcps_analyzer = None
        self.rcps_crashing_tab = None  # Reference to RCPS Crashing tab
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
        print("[DEBUG] run_rcps method called - starting execution")
        try:
            # Get input parameters
            resource_limit = self.resource_limit_var.get()
            priority_rule = self.priority_rule_var.get()
            df_gantt = self.main_window.current_data
            print(f"[DEBUG] Got inputs: resource_limit={resource_limit}, priority_rule={priority_rule}, df_gantt shape={df_gantt.shape if df_gantt is not None else 'None'}")
            
            # Validate inputs
            print("[DEBUG] About to validate inputs")
            try:
                self.validate_rcps_inputs(df_gantt, resource_limit, priority_rule)
                print("[DEBUG] Input validation completed")
            except Exception as e:
                print(f"[DEBUG] Input validation failed: {e}")
                raise
            
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
                    print("[DEBUG] Resource limit too low - returning early")
                    return
            
            print("[DEBUG] Resource limit validation passed")
            
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
            
            # Display large tables layout with full timeline data
            print("[DEBUG] Using LARGE TABLES LAYOUT with full timeline data")
            self.display_large_tables_view(self.tables_frame, cpm_table_aligned, rcps_table, df_gantt)
            
            # Store data for fullscreen comparison and enable button
            self.cmp_table_data = cpm_table_aligned
            self.rcps_table_data = rcps_table
            self.gantt_data = df_gantt
            self.fullscreen_btn.config(state='normal')
            

            # Build and store network graph for RCPS Crashing feature
            # CRITICAL FIX: Use actual_start as ES for resource-aware crashing
            import networkx as nx
            G = nx.DiGraph()
            
            # Add nodes with RCPS-specific attributes
            for _, row in rcps_table.iterrows():
                if row['id'] not in ['RA', 'RS']:  # Skip resource rows
                    # FIXED: Use actual_start as ES for crashing logic (resource-constrained schedule)
                    actual_start = row['actual_start'] if 'actual_start' in row and row['actual_start'] != '' else row['early_start']
                    duration = row['duration']
                    early_finish = actual_start + duration
                    
                    node_attrs = {
                        'duration': duration,
                        'early_start': actual_start,  # ES is now actual_start from RCPS
                        'late_finish': row['late_finish'],
                        'float': row['float'],
                        'EF': early_finish,           # EF based on actual_start (resource-constrained)
                        'ES': actual_start            # For crashing, ES is actual_start (resource-aware)
                    }
                    
                    # Add resource information if available
                    if 'resource' in row:
                        node_attrs['resource'] = row['resource']
                    
                    # Store actual_start explicitly for debugging and verification
                    node_attrs['actual_start'] = actual_start
                    
                    # Add crash cost information if available in original data
                    if hasattr(analyzer, 'activities'):
                        for activity in analyzer.activities:
                            if activity.get('id') == row['id']:
                                if 'crash_cost' in activity:
                                    node_attrs['crash_cost'] = activity['crash_cost']
                                if 'min_duration' in activity:
                                    node_attrs['min_duration'] = activity['min_duration']
                                break
                    
                    G.add_node(row['id'], **node_attrs)
            
            # Rebuild edges from original project dependencies
            if hasattr(analyzer, 'G') and analyzer.G is not None:
                # Copy edges from original analyzer graph
                for u, v in analyzer.G.edges():
                    if u in G.nodes() and v in G.nodes():
                        G.add_edge(u, v)
            elif hasattr(analyzer, 'activities'):
                # Build edges from activities data
                for activity in analyzer.activities:
                    activity_id = activity.get('id')
                    predecessors = activity.get('predecessors', [])
                    if activity_id in G.nodes():
                        for pred in predecessors:
                            if pred in G.nodes():
                                G.add_edge(pred, activity_id)
            
            self.rcps_network_graph = G
            
            # Create RCPSAnalyzer with proper NetworkX graph
            self.rcps_analyzer = RCPSAnalyzer(G, resource_limit, analyzer)
            
            # Ensure graph has all required node attributes for crashing
            self._ensure_crashing_attributes(G)
            
            # DEBUG: Verify that ES values use actual_start (resource-constrained)
            print(f"[DEBUG VERIFICATION] RCPS Network Graph built with {len(G.nodes())} nodes")
            for node_id, attrs in G.nodes(data=True):
                if 'actual_start' in attrs and 'ES' in attrs:
                    print(f"[DEBUG] Node {node_id}: ES={attrs['ES']}, actual_start={attrs['actual_start']}, early_start={attrs.get('early_start', 'N/A')}")
                    if attrs['ES'] != attrs['actual_start']:
                        print(f"[WARNING] Node {node_id}: ES != actual_start! This will cause incorrect crashing analysis.")
            print("[DEBUG] RCPS network graph stored for RCPS Crashing - using actual_start as ES")
        
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

    def display_large_tables_view(self, parent, cmp_table, rcps_table, df_gantt):
        """
        Display large tables with full timeline data (Production Layout)
        Layout: 
        [CPM Table - Full]
        [RCPS Table - Full]
        """
        # Use the parent frame directly - no additional container needed
        parent.grid_rowconfigure(0, weight=1)  # CPM table
        parent.grid_rowconfigure(1, weight=1)  # RCPS table
        parent.grid_columnconfigure(0, weight=1)  # Single column for tables
        
        # Display large tables with full timeline data
        self.display_schedule_table(parent, cmp_table, "Initial CPM-based Plan", col=0, row=0)
        self.display_schedule_table(parent, rcps_table, "Resource-Constrained Schedule (RCPS)", col=0, row=1)

    def display_schedule_table(self, parent, table, label, col, row=0):
        """Display a schedule table with advanced formatting and timeline visualization"""
        # Display a schedule table in the parent frame with a label
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        label_widget = ttk.Label(frame, text=label, font=("Arial", 12, "bold"))
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        # Use tksheet for true cell borders if available
        if not TKSHEET_AVAILABLE:
            # Fallback to basic display
            self.display_basic_table(frame, table, label)
            return
            
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
        is_cmp = label.lower().startswith("initial cmp")

        # --- Highlighting logic adapted from plot_schedule_tables (matplotlib) ---
        # For RCPS table, need to know scheduled/delayed activities
        scheduled_activities = set()
        delayed_activities = set()
        if not is_cmp:
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
                is_cmp_or_pert = (col in timeline_cols and 'resource' in row_obj)
                if is_cmp_or_pert and str(val) == 'S':
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
                elif not is_cmp and col == 'actual_start' and 'early_start' in row_obj and 'actual_start' in row_obj:
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
                elif is_cmp:
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
            is_cmp = label.lower().startswith("initial cmp")
            if is_cmp:
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
                if (is_cmp and i < 6) or (not is_cmp and i < 7):
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

    # ========================================================================
    # COMMENTED FOR FUTURE USE: Hybrid Layout Methods (Small Tables + Gantt Charts)
    # ========================================================================
    #
    # def display_hybrid_schedule_view(self, parent, cmp_table, rcps_table, df_gantt):
    #     '''
    #     Display tables on the left and Gantt charts on the right.
    #     Layout: 
    #     [CPM Table]    [CPM Gantt]
    #     [RCPS Table]   [RCPS Gantt]
    #     '''
        # Create main container with 2 columns (left: tables, right: gantt charts)
        # main_frame = ttk.Frame(parent)
        # main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid weights for content-based table sizing
        # main_frame.grid_rowconfigure(0, weight=1)  # CPM row
        # main_frame.grid_rowconfigure(1, weight=1)  # RCPS row
        # main_frame.grid_columnconfigure(0, weight=0)  # Tables column - fixed size based on content
        # main_frame.grid_columnconfigure(1, weight=1)  # Gantt column - fills remaining space
        
        # Create compact tables (without timeline columns to save space)
        # cpm_compact = self.create_compact_table(cpm_table)
        # rcps_compact = self.create_compact_table(rcps_table)
        
        # Left side: Compact tables with fixed width
        # self.display_compact_table_fixed_width(main_frame, cpm_compact, "Initial CPM-based Plan", col=0, row=0)
        # self.display_compact_table_fixed_width(main_frame, rcps_compact, "Resource-Constrained Schedule (RCPS)", col=0, row=1)
        
        # Right side: Gantt charts
        # self.display_gantt_chart(main_frame, cpm_table, "CPM Timeline", col=1, row=0, is_cmp=True)
        # self.display_gantt_chart(main_frame, rcps_table, "RCPS Timeline", col=1, row=1, is_cmp=False)

    def create_compact_table(self, table):
        '''Create a compact version of the table without timeline columns'''
        # Keep only non-timeline columns (non-integer column names)
        compact_columns = [col for col in table.columns if not isinstance(col, int)]
        return table[compact_columns].copy()

    def display_compact_table_fixed_width(self, parent, table, label, col, row=0):
        '''Display a compact table with fixed width based on content'''
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
        
        # Use tksheet for the table if available
        if not TKSHEET_AVAILABLE:
            # Fallback to basic display
            self.display_basic_table(frame, table, label)
            return
            
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

    def display_basic_table(self, frame, table, label):
        """Fallback basic table display when tksheet is not available"""
        # Create a simple text widget for displaying table data
        text_widget = tk.Text(frame, wrap=tk.NONE, font=("Courier", 10))
        text_widget.grid(row=1, column=0, sticky="nsew")
        
        # Format table as text
        table_str = table.to_string(index=False)
        text_widget.insert(tk.END, table_str)
        text_widget.config(state=tk.DISABLED)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        v_scrollbar.grid(row=1, column=1, sticky="ns")
        text_widget.config(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        h_scrollbar.grid(row=2, column=0, sticky="ew")
        text_widget.config(xscrollcommand=h_scrollbar.set)
        
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

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

    # ========================================================================
    # END OF COMMENTED HYBRID LAYOUT METHODS  
    # ========================================================================

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

    def get_rcps_analyzer(self):
        """Return the current RCPS analyzer"""
        return getattr(self, 'rcps_analyzer', None)
    
    def get_resource_limit(self):
        """Return the current resource limit from RCPS tab"""
        return self.resource_limit_var.get()
    
    def get_rcps_table_data(self):
        """Return the current RCPS table data for crashing analysis"""
        print(f"🔍 [RCPS TAB] get_rcps_table_data called")
        
        # Check if we have RCPS table data
        if hasattr(self, 'rcps_table_data') and self.rcps_table_data is not None:
            table = self.rcps_table_data
            print(f"   📊 RCPS table found: {type(table)} with {len(table)} rows")
            print(f"   📊 RCPS table columns: {list(table.columns)}")
            
            # Show all activities in the RCPS table
            print(f"   📋 RCPS table activities:")
            for idx, row in table.iterrows():
                activity_id = row.get('id', f'ROW_{idx}')
                duration = row.get('duration', 'N/A')
                early_start = row.get('early_start', 'N/A')
                actual_start = row.get('actual_start', 'N/A')
                print(f"      {idx}: {activity_id} | Duration={duration} | ES={early_start} | AS={actual_start}")
            
            return table
        else:
            print(f"   ❌ No RCPS table data available")
            return None
    
    def get_cmp_table_data(self):
        """Return the current CMP table data for comparison"""
        return getattr(self, 'cmp_table_data', None)
    
    def get_gantt_data(self):
        """Return the current Gantt data"""
        return getattr(self, 'gantt_data', None)
    
    def set_rcps_crashing_tab(self, rcps_crashing_tab):
        """Set reference to RCPS Crashing tab"""
        self.rcps_crashing_tab = rcps_crashing_tab
    
    def _ensure_crashing_attributes(self, graph):
        """Ensure NetworkX graph has all attributes required for crashing"""
        for node_id, node_data in graph.nodes(data=True):
            if node_id not in ['RA', 'RS']:
                # Set default values if missing
                if 'crash_cost' not in node_data:
                    node_data['crash_cost'] = 100  # Default crash cost
                if 'normal_cost' not in node_data:
                    node_data['normal_cost'] = 50   # Default normal cost
                if 'min_duration' not in node_data:
                    node_data['min_duration'] = max(1, node_data.get('duration', 0) // 2)


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

    def _build_rcps_network_graph(self, rcps_table, df_gantt, analyzer):
        """Convert RCPS table back to NetworkX graph with actual start times"""
        import networkx as nx
        
        print("\n🔧 [RCPS NETWORK BUILDER] Starting network graph construction...")
        print("=" * 70)
        
        # Debug input parameters
        print(f"📊 INPUT DATA ANALYSIS:")
        print(f"   rcps_table type: {type(rcps_table)}")
        print(f"   rcps_table shape: {rcps_table.shape if hasattr(rcps_table, 'shape') else 'N/A'}")
        print(f"   df_gantt type: {type(df_gantt)}")
        print(f"   analyzer type: {type(analyzer)}")
        
        # Show all rows in RCPS table
        print(f"\n📋 ALL ROWS IN RCPS TABLE:")
        for idx, row in rcps_table.iterrows():
            row_id = row.get('id', f'ROW_{idx}')
            duration = row.get('duration', 'N/A')
            early_start = row.get('early_start', 'N/A')
            actual_start = row.get('actual_start', 'N/A')
            print(f"   Row {idx}: ID='{row_id}' | Duration={duration} | ES={early_start} | AS={actual_start}")
        
        G = nx.DiGraph()
        nodes_added = []
        nodes_skipped = []
        
        # Add nodes with RCPS-specific attributes
        print(f"\n🏗️  NODE CONSTRUCTION PROCESS:")
        for idx, row in rcps_table.iterrows():
            row_id = row.get('id', f'ROW_{idx}')
            
            if row_id in ['RA', 'RS']:  # Skip resource rows
                nodes_skipped.append((row_id, "Resource row"))
                print(f"   ⏭️  SKIPPED: {row_id} (Resource row)")
                continue
                
            # This is where we might lose A and B - let's see what happens
            print(f"   🔨 PROCESSING: {row_id}")
            
            node_attrs = {
                'duration': row.get('duration', 0),
                'early_start': row.get('early_start', 0),
                'late_finish': row.get('late_finish', 0),
                'float': row.get('float', 0)
            }
            
            # Add resource information if available
            if 'resource' in row:
                node_attrs['resource'] = row['resource']
            
            # Add actual start time from RCPS if available
            if 'actual_start' in row:
                node_attrs['actual_start'] = row['actual_start']
            else:
                node_attrs['actual_start'] = row.get('early_start', 0)
            
            # Add crash cost information if available in original data
            if hasattr(analyzer, 'activities') and analyzer.activities:
                for activity in analyzer.activities:
                    if activity.get('id') == row_id:
                        if 'crash_cost' in activity:
                            node_attrs['crash_cost'] = activity['crash_cost']
                        if 'min_duration' in activity:
                            node_attrs['min_duration'] = activity['min_duration']
                        break
            
            G.add_node(row_id, **node_attrs)
            nodes_added.append(row_id)
            print(f"      ✅ ADDED: {row_id} with attributes: {node_attrs}")
        
        print(f"\n📈 NODE SUMMARY:")
        print(f"   ✅ Nodes added: {nodes_added}")
        print(f"   ⏭️  Nodes skipped: {nodes_skipped}")
        print(f"   📊 Total nodes in graph: {len(G.nodes())}")
        
        # Rebuild edges from original project dependencies
        edges_added = []
        print(f"\n🔗 EDGE CONSTRUCTION PROCESS:")
        
        if hasattr(analyzer, 'G') and analyzer.G is not None:
            print(f"   📊 Using analyzer's graph for edges...")
            print(f"   📊 Original graph has {len(analyzer.G.nodes())} nodes and {len(analyzer.G.edges())} edges")
            print(f"   📊 Original graph nodes: {list(analyzer.G.nodes())}")
            
            # Copy edges from original analyzer graph
            for u, v in analyzer.G.edges():
                if u in G.nodes() and v in G.nodes():
                    G.add_edge(u, v)
                    edges_added.append((u, v))
                    print(f"      ✅ EDGE ADDED: {u} → {v}")
                else:
                    print(f"      ⏭️  EDGE SKIPPED: {u} → {v} (missing nodes: u_exists={u in G.nodes()}, v_exists={v in G.nodes()})")
                    
        elif hasattr(analyzer, 'activities') and analyzer.activities:
            print(f"   📊 Using activities data for edges...")
            print(f"   📊 Activities count: {len(analyzer.activities)}")
            
            # Build edges from activities data
            for activity in analyzer.activities:
                activity_id = activity.get('id')
                predecessors = activity.get('predecessors', [])
                print(f"   🔍 Activity {activity_id}: predecessors = {predecessors}")
                
                if activity_id in G.nodes():
                    for pred in predecessors:
                        if pred in G.nodes():
                            G.add_edge(pred, activity_id)
                            edges_added.append((pred, activity_id))
                            print(f"      ✅ EDGE ADDED: {pred} → {activity_id}")
                        else:
                            print(f"      ⏭️  EDGE SKIPPED: {pred} → {activity_id} (predecessor {pred} not in graph)")
                else:
                    print(f"      ⏭️  ACTIVITY SKIPPED: {activity_id} (not in graph nodes)")
        else:
            print(f"   ❌ No edge source available!")
            
        print(f"\n🔗 EDGE SUMMARY:")
        print(f"   ✅ Edges added: {edges_added}")
        print(f"   📊 Total edges in graph: {len(G.edges())}")
        
        # Final graph analysis
        print(f"\n🎯 FINAL GRAPH ANALYSIS:")
        print(f"   📊 Final nodes: {list(G.nodes())}")
        print(f"   📊 Final edges: {list(G.edges())}")
        
        # Specifically look for A and B
        print(f"\n🔍 MISSING ACTIVITIES INVESTIGATION:")
        has_A = 'A' in G.nodes()
        has_B = 'B' in G.nodes()
        print(f"   Activity A in graph: {has_A}")
        print(f"   Activity B in graph: {has_B}")
        
        if not has_A:
            print(f"   🚨 ACTIVITY A MISSING - checking original data...")
            if hasattr(analyzer, 'activities'):
                a_in_activities = any(act.get('id') == 'A' for act in analyzer.activities)
                print(f"      A in analyzer.activities: {a_in_activities}")
            a_in_rcps_table = 'A' in rcps_table['id'].values if 'id' in rcps_table.columns else False
            print(f"      A in rcps_table: {a_in_rcps_table}")
            
        if not has_B:
            print(f"   🚨 ACTIVITY B MISSING - checking original data...")
            if hasattr(analyzer, 'activities'):
                b_in_activities = any(act.get('id') == 'B' for act in analyzer.activities)
                print(f"      B in analyzer.activities: {b_in_activities}")
            b_in_rcps_table = 'B' in rcps_table['id'].values if 'id' in rcps_table.columns else False
            print(f"      B in rcps_table: {b_in_rcps_table}")
        
        print(f"\n✅ [RCPS NETWORK BUILDER] Built RCPS network graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
        print("=" * 70)
        return G
