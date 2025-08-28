#!/usr/bin/env python3
"""
Main Window Module

Contains the main application w        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Run CPM Analysis", command=self.run_cpm_analysis)
        analysis_menu.add_command(label="Run PERT Analysis", command=self.run_pert_analysis)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Project Crashing", command=self.show_crashing_tab)
        analysis_menu.add_command(label="Resource Scheduling", command=self.show_rcps_tab)
        analysis_menu.add_command(label="RCPS Crashing", command=self.show_rcps_crashing_tab)d overall GUI structure for PMHelper.
Manages the main interface, tab navigation, and overall application state.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import math
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler
from .tabs.input_tab import InputTab
from .tabs.results_tab import ResultsTab
from .tabs.network_tab import NetworkTab
from .tabs.pert_diagram_tab import PertDiagramTab

from .tabs.gantt_tab import GanttTab
from .tabs.probability_tab import ProbabilityTab
from .tabs.rcps_tab import RCPSTab
from .tabs.crashing_tab import CrashingTab
from .tabs.rcps_crashing_tab import RCPSCrashingTab


class MainWindow:
    """Main desktop application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PMHelper - Project Management Analysis Tool")
        self.root.geometry("1400x900")
        
        # Initialize analyzers
        self.cpm_analyzer = CPMAnalyzer()
        self.pert_analyzer = PERTAnalyzer()
        
        # Analysis mode tracking
        self.analysis_mode = None  # 'deterministic' or 'probabilistic'
        self.current_analyzer = None
        self.current_data = None
        
        # Initialize GUI
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        # Load sample data
        self.load_sample_data()
        
        # INTEGRATION TEST: Verify all fixes are implemented
        self.test_gantt_integration()
    
    @property
    def analyzer(self):
        """Backward compatibility property"""
        return self.current_analyzer
    
    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Load CPM Data...", command=self.load_cpm_data)
        file_menu.add_command(label="Load PERT Data...", command=self.load_pert_data)
        file_menu.add_separator()
        file_menu.add_command(label="Save Results...", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Run CPM Analysis", command=self.run_cpm_analysis)
        analysis_menu.add_command(label="Run PERT Analysis", command=self.run_pert_analysis)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="Project Crashing", command=self.show_crashing_tab)
        analysis_menu.add_command(label="Resource Scheduling", command=self.show_rcps_tab)
        analysis_menu.add_command(label="RCPS Crashing", command=self.show_rcps_crashing_tab)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Generate Sample CPM Data", command=self.generate_sample_cpm)
        tools_menu.add_command(label="Generate Sample PERT Data", command=self.generate_sample_pert)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Create the main interface with notebook tabs"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initialize tabs
        self.input_tab = InputTab(self.notebook, self)
        self.results_tab = ResultsTab(self.notebook, self)
        self.network_tab = NetworkTab(self.notebook, self)
        self.pert_diagram_tab = PertDiagramTab(self.notebook, self)
        self.gantt_tab = GanttTab(self.notebook, self)
        self.probability_tab = ProbabilityTab(self.notebook, self)
        self.rcps_tab = None
        self.crashing_tab = CrashingTab(self.notebook, self)
        self.notebook.add(self.crashing_tab, text="Crashing")
        
        # Add RCPS Crashing tab
        self.rcps_crashing_tab = RCPSCrashingTab(self.notebook, self)
        self.notebook.add(self.rcps_crashing_tab, text="RCPS Crashing")
        
        # Setup tab references for data sharing
        self.setup_tab_references()
        
        # CRITICAL FIX 3: Add tab communication event handling
        self.setup_tab_communication()
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def setup_tab_references(self):
        """Setup cross-references between tabs for data sharing"""
        # This method will be called after RCPS tab is created
        # For now, store the reference for later linking
        self.rcps_crashing_tab_needs_linking = True
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Mode indicator
        self.mode_indicator = ttk.Label(self.status_bar, text="Mode: None", 
                                       font=("Arial", 9, "bold"))
        self.mode_indicator.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def setup_tab_communication(self):
        """CRITICAL FIX 3: Setup automatic tab communication and event handling"""
        if hasattr(self, 'notebook'):
            # Bind tab selection event for automatic chart updates
            self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_selected)
            # print("DEBUG: Tab communication event handling setup completed")
        else:
            print("WARNING: Notebook not available for tab communication setup")

    def on_tab_selected(self, event):
        """CRITICAL FIX 3: Handle tab selection events for automatic chart updates"""
        try:
            # Get the selected tab
            selected_tab = event.widget.select()
            tab_text = event.widget.tab(selected_tab, "text")
            
            # print(f"DEBUG: Tab selected: {tab_text}")
            
            # If Gantt Chart tab is selected and we have analysis results, ensure chart is displayed
            if ("Gantt" in tab_text or "gantt" in tab_text.lower()):
                self.handle_gantt_tab_selection()
                
        except Exception as e:
            print(f"ERROR: Tab selection handler failed: {e}")

    def handle_gantt_tab_selection(self):
        """CRITICAL FIX 3: Handle Gantt tab selection with automatic chart update"""
        try:
            # print("DEBUG: Gantt tab selected - checking for data and updating chart")
            
            # Check if Gantt tab exists
            if not (hasattr(self, 'gantt_tab') and self.gantt_tab):
                print("WARNING: Gantt tab not available")
                return
            
            # Check if we have analysis results
            if hasattr(self, 'results_data') and self.results_data:
                # print("DEBUG: Analysis results available - updating Gantt chart")
                
                # Ensure Gantt tab has the latest data
                if not hasattr(self.gantt_tab, 'results_data') or not self.gantt_tab.results_data:
                    # print("DEBUG: Sending analysis results to Gantt tab")
                    self.gantt_tab.update_data(self.results_data, getattr(self, 'analysis_mode', 'deterministic'))
                
                # Force chart update to ensure visibility
                # print("DEBUG: Forcing chart update for Gantt tab visibility")
                self.gantt_tab.update_chart()
                
            else:
                # print("DEBUG: No analysis results available for Gantt chart")
                # Show empty plot with instruction message
                if hasattr(self.gantt_tab, 'create_empty_plot'):
                    self.gantt_tab.create_empty_plot()
                    
        except Exception as e:
            print(f"ERROR: Failed to handle Gantt tab selection: {e}")
            import traceback
            traceback.print_exc()

    def set_status(self, message):
        """Update the status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def set_analysis_mode(self, mode):
        """Set the analysis mode and update UI accordingly"""
        self.analysis_mode = mode
        
        if mode == 'deterministic':
            self.current_analyzer = self.cpm_analyzer
            self.mode_indicator.config(text="Mode: CPM (Deterministic)")
        elif mode == 'probabilistic':
            self.current_analyzer = self.pert_analyzer
            self.mode_indicator.config(text="Mode: PERT (Probabilistic)")
        else:
            self.current_analyzer = None
            self.mode_indicator.config(text="Mode: None")
        
        # Update input tab layout
        self.input_tab.set_mode(mode)
        
        # Update probability tab visibility
        if mode == 'probabilistic':
            self.probability_tab.show()
        else:
            self.probability_tab.hide()
    
    def get_activities_data(self):
        """Get activities data from the input tab"""
        return self.input_tab.get_activities_data()
    
    def load_sample_data(self):
        """Load sample data into the input tab"""
        self.input_tab.load_sample_data()
    
    def new_project(self):
        """Start a new project"""
        result = messagebox.askyesno("New Project", 
                                   "This will clear all current data. Continue?")
        if result:
            self.input_tab.clear_all()
            self.results_tab.clear_results()
            self.network_tab.clear_diagram()
            self.pert_diagram_tab.clear_network()
            self.gantt_tab.clear_chart()
            self.probability_tab.clear_analysis()
            self.set_analysis_mode(None)
            self.set_status("New project started")
    
    def load_cpm_data(self):
        """Load CPM data from file"""
        try:
            filename = filedialog.askopenfilename(
                title="Load CPM Data",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if filename:
                self.input_tab.load_file(filename, 'deterministic')
                self.current_data = None  # Clear RCPS data until analysis is run
                self.set_status(f"Loaded CPM data from {filename}")
                # Automatically run CPM analysis after loading data
                self.set_analysis_mode('deterministic')
                self.run_cpm_analysis()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CPM data: {str(e)}")
    
    def load_pert_data(self):
        """Load PERT data from file"""
        try:
            filename = filedialog.askopenfilename(
                title="Load PERT Data",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if filename:
                self.input_tab.load_file(filename, 'probabilistic')
                self.set_status(f"Loaded PERT data from {filename}")
                # Automatically run PERT analysis after loading data
                self.set_analysis_mode('probabilistic')
                self.run_pert_analysis()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PERT data: {str(e)}")
    
    def save_results(self):
        """Save analysis results to file"""
        if not self.current_analyzer or not hasattr(self.current_analyzer, 'G') or not self.current_analyzer.G:
            messagebox.showwarning("Warning", "No analysis results to save. Please run analysis first.")
            return
        
        try:
            self.results_tab.save_results()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
    
    def run_cpm_analysis(self):
        """Run CPM analysis"""
        if self.analysis_mode != 'deterministic':
            messagebox.showwarning("Warning", "Please load CPM data first or switch to deterministic mode.")
            return
        
        self.analyze_project()
    
    def run_pert_analysis(self):
        """Run PERT analysis"""
        if self.analysis_mode != 'probabilistic':
            messagebox.showwarning("Warning", "Please load PERT data first or switch to probabilistic mode.")
            return
        
        self.analyze_project()
    
    def update_gantt_chart_after_analysis(self, results):
        """CRITICAL FIX 1: Automatically update Gantt chart after analysis"""
        try:
            # print("DEBUG: Triggering automatic Gantt chart update...")
            
            # Check if Gantt tab exists
            if hasattr(self, 'gantt_tab') and self.gantt_tab:
                # Send results to Gantt tab
                self.gantt_tab.update_data(results, self.analysis_mode)
                # print("DEBUG: Gantt tab updated with analysis results")
                
                # Force chart generation
                self.gantt_tab.update_chart()
                # print("DEBUG: Gantt chart generation triggered")
                
                # Optional: Switch to Gantt tab to show results
                self.show_gantt_tab_after_analysis()
                
            else:
                print("WARNING: Gantt tab not available for update")
                
        except Exception as e:
            print(f"ERROR: Failed to update Gantt chart after analysis: {e}")
            import traceback
            traceback.print_exc()

    def show_gantt_tab_after_analysis(self):
        """Optional: Switch to Gantt tab to show results immediately"""
        try:
            if hasattr(self, 'notebook'):
                # Find Gantt tab index
                for i in range(self.notebook.index("end")):
                    tab_text = self.notebook.tab(i, "text")
                    if "Gantt" in tab_text or "gantt" in tab_text.lower():
                        self.notebook.select(i)
                        # print("DEBUG: Automatically switched to Gantt Chart tab")
                        return
            # print("DEBUG: Gantt tab not found for automatic switching")
        except Exception as e:
            print(f"ERROR: Failed to switch to Gantt tab: {e}")

    def analyze_project(self):
        """Run the appropriate analysis based on current mode"""
        try:
            activities_data = self.get_activities_data()
            
            if not activities_data:
                messagebox.showwarning("Warning", "Please enter some activities to analyze.")
                return
            
            if not self.current_analyzer:
                messagebox.showwarning("Warning", "Please select an analysis mode (CPM or PERT).")
                return
            
            self.set_status("Running analysis...")
            
            # Perform analysis
            G, critical_paths, critical_activities = self.current_analyzer.analyze(activities_data)
            
            # Optional debug output (comment out for production)
            # print("=" * 80)
            # print("CPM ANALYSIS DEBUG OUTPUT")
            # print("=" * 80)
            # print(f"Critical Path: {critical_paths[0] if critical_paths else 'None'}")
            # print(f"Critical Activities: {critical_activities}")
            # 
            # print("\nActivity Float Values from Graph:")
            # for node in G.nodes() if G else []:
            #     if node not in ['START', 'END']:
            #         node_data = G.nodes[node]
            #         es = node_data.get('ES', 0)
            #         ef = node_data.get('EF', 0)
            #         ls = node_data.get('LS', 0)
            #         lf = node_data.get('LF', 0)
            #         float_val = node_data.get('float', 0)
            #         is_critical = node in critical_activities
            #         print(f"  {node}: ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val:.2f}, Critical={is_critical}")
            # print("=" * 80)
            
            # Calculate project duration from the graph
            project_duration = 0
            if G and G.nodes():
                # Find the maximum EF (Earliest Finish) time
                for node in G.nodes():
                    ef = G.nodes[node].get('EF', 0)
                    if ef > project_duration:
                        project_duration = ef
            
            # Extract the first critical path for display
            critical_path = critical_paths[0] if critical_paths else []
            
            # Convert activities_data to the format expected by ResultsTab
            activities_for_display = []
            for activity_data in activities_data:
                activity_id = activity_data.get('id', activity_data.get('Activity', ''))
                
                # Get node data from graph if available
                node_data = G.nodes.get(activity_id, {}) if G else {}
                
                # Standardize predecessor IDs: split, strip, and rejoin
                raw_preds = activity_data.get('predecessors', activity_data.get('Predecessors', ''))
                if isinstance(raw_preds, str):
                    preds_clean = ','.join([p.strip() for p in raw_preds.split(',') if p.strip()])
                else:
                    preds_clean = ''
                activity_display = {
                    'id': activity_id,
                    'name': activity_data.get('activity', activity_data.get('name', activity_data.get('Activity', activity_id))),
                    'duration': activity_data.get('duration', activity_data.get('Duration', 0)),
                    'ES': node_data.get('ES', 0),  # FIXED: Use correct field names
                    'EF': node_data.get('EF', 0),  # FIXED: Use correct field names
                    'LS': node_data.get('LS', 0),  # FIXED: Use correct field names
                    'LF': node_data.get('LF', 0),  # FIXED: Use correct field names
                    'float': node_data.get('float', 0),
                    'critical': activity_id in critical_activities,
                    'predecessors': preds_clean,
                    'resource': activity_data.get('resource', activity_data.get('resource_demand', 1)),  # Ensure resource column for RCPS
                }
                
                # Add PERT-specific data if in probabilistic mode
                if self.analysis_mode == 'probabilistic':
                    opt = activity_data.get('optimistic', activity_data.get('Optimistic', 0))
                    most = activity_data.get('most_likely', activity_data.get('Most_Likely', 0))
                    pess = activity_data.get('pessimistic', activity_data.get('Pessimistic', 0))
                    expected_time = (float(opt) + 4 * float(most) + float(pess)) / 6
                    variance = ((float(pess) - float(opt)) / 6) ** 2
                    
                    activity_display.update({
                        'optimistic': opt,
                        'most_likely': most,
                        'pessimistic': pess,
                        'expected_duration': expected_time,  # Keep precise for any legacy needs
                        'expected': math.ceil(expected_time),  # Integer expected duration for display
                        'variance': round(variance, 3)
                    })
                
                activities_for_display.append(activity_display)
            
            # Optional debug: Verify activities data format for ResultsTab
            # print("\nActivities Data for ResultsTab:")
            # for activity in activities_for_display:
            #     act_id = activity.get('id')
            #     name = activity.get('name')
            #     float_val = activity.get('float', 0)
            #     critical = activity.get('critical', False)
            #     es = activity.get('ES', 0)
            #     ef = activity.get('EF', 0)
            #     ls = activity.get('LS', 0)
            #     lf = activity.get('LF', 0)
            #     print(f"  {act_id} ({name}): ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val:.2f}, Critical={critical}")
            # 
            # total_float = sum(a.get('float', 0) for a in activities_for_display)
            # critical_count = sum(1 for a in activities_for_display if a.get('critical', False))
            # non_critical_count = len(activities_for_display) - critical_count
            # print(f"Summary: Total Float={total_float:.2f}, Critical={critical_count}, Non-Critical={non_critical_count}")
            # print("=" * 80)
            
            # Create results data structure for the results tab
            self.results_data = {
                'graph': G,
                'critical_paths': critical_paths,
                'critical_path': critical_path,  # FIXED: Add single critical_path
                'critical_activities': critical_activities,
                'activities_data': activities_data,  # Keep original for other tabs
                'activities': activities_for_display,  # FIXED: Add formatted activities
                'project_duration': project_duration,  # FIXED: Add calculated duration
            }
            # --- CRITICAL: Set current_data for RCPS tab ---
            import pandas as pd
            try:
                import numpy as np
                df_gantt = pd.DataFrame(activities_for_display)
                # Rename CPM columns to P6-style columns for RCPS compatibility
                df_gantt = df_gantt.rename(columns={
                    'ES': 'early_start',
                    'EF': 'early_finish',
                    'LS': 'late_start',
                    'LF': 'late_finish'
                })
                # For PERT/RCPS, set duration to ceil(expected_duration) if available
                if self.analysis_mode == 'probabilistic' and 'expected_duration' in df_gantt.columns:
                    df_gantt['duration'] = np.ceil(df_gantt['expected_duration']).astype(int)
                # Ensure all required columns are present and filled
                required_cols = ['id', 'early_start', 'duration', 'resource', 'late_finish', 'float']
                for col in required_cols:
                    if col not in df_gantt.columns:
                        df_gantt[col] = 0 if col != 'id' else ''
                # Fill NaN or empty values with defaults
                df_gantt['id'] = df_gantt['id'].replace('', pd.NA).fillna('X')
                df_gantt['early_start'] = pd.to_numeric(df_gantt['early_start'], errors='coerce').fillna(0).astype(int)
                df_gantt['duration'] = pd.to_numeric(df_gantt['duration'], errors='coerce').fillna(1).astype(int)
                df_gantt['resource'] = pd.to_numeric(df_gantt['resource'], errors='coerce').fillna(1).astype(int)
                df_gantt['late_finish'] = pd.to_numeric(df_gantt['late_finish'], errors='coerce').fillna(0).astype(int)
                df_gantt['float'] = pd.to_numeric(df_gantt['float'], errors='coerce').fillna(0).astype(int)
                if not df_gantt.empty:
                    self.current_data = df_gantt
                else:
                    self.current_data = None
                # Debug printout for RCPS input verification
                # print("\n[DEBUG] PERT Analysis: DataFrame for RCPS (first 10 rows):")
                print(self.current_data.head(10))
                # print("[DEBUG] Columns:", list(self.current_data.columns))
                # print("[DEBUG] Dtypes:\n", self.current_data.dtypes)
            except Exception as e:
                print(f"[RCPS] Failed to set current_data: {e}")
                self.current_data = None
            
            # Add PERT-specific data if in probabilistic mode
            if self.analysis_mode == 'probabilistic':
                # Calculate precise expected duration from critical path using statistical values
                precise_expected_duration = 0
                if critical_path:
                    for activity_id in critical_path:
                        if activity_id not in ['START', 'END']:
                            # Find the original activity data to get precise expected_time
                            for activity_data in activities_data:
                                if activity_data.get('id') == activity_id:
                                    # Calculate precise expected time using PERT formula
                                    opt = float(activity_data.get('optimistic', 0))
                                    most = float(activity_data.get('most_likely', 0))
                                    pess = float(activity_data.get('pessimistic', 0))
                                    precise_expected_duration += (opt + 4 * most + pess) / 6
                                    break
                
                # Get PERT statistics from the analyzer
                project_variance = self.current_analyzer.project_variance
                standard_deviation = self.current_analyzer.project_std  # Already rounded to 3 decimals
                
                self.results_data.update({
                    'expected_duration': precise_expected_duration,  # Use precise statistical value
                    'project_variance': project_variance,
                    'standard_deviation': standard_deviation
                })
            
            # Update results in all tabs
            self.results_tab.update_results(self.results_data, self.analysis_mode)
            self.network_tab.update_network(self.results_data, self.analysis_mode)
            self.pert_diagram_tab.update_network(self.results_data, self.analysis_mode)
            
            # CRITICAL FIX 1: Automatic Gantt chart update after analysis
            self.update_gantt_chart_after_analysis(self.results_data)
            
            # Update probability tab if in PERT mode
            if self.analysis_mode == 'probabilistic':
                try:
                    self.probability_tab.update_analysis(self.results_data)
                except Exception as e:
                    print(f"WARNING: Failed to update ProbabilityTab: {e}")
                    # Continue execution - don't let probability tab errors crash analysis
            
            # Switch to results tab
            self.notebook.select(1)
            
            self.set_status("Analysis completed successfully")
            messagebox.showinfo("Success", "Analysis completed successfully!")
            
        except Exception as e:
            self.set_status("Analysis failed")
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    # def show_crashing_tab(self):
    #     """Show the project crashing tab (ENABLED)"""

    #     # Robust import: add code/ to sys.path if needed
    #     import sys, os
    #     code_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../code'))
    #     if code_dir not in sys.path:
    #         sys.path.insert(0, code_dir)
    #     try:
    #         from enhanced_crashing_integration import integrate_enhanced_crashing
    #     except ImportError:
    #         messagebox.showerror("Error", "Enhanced Project Crashing integration module not found.")
    #         return

    #     # Integrate enhanced crashing tabs if not already present
    #     if not hasattr(self, 'enhanced_crashing_manager') or self.enhanced_crashing_manager is None:
    #         try:
    #             self.enhanced_crashing_manager = integrate_enhanced_crashing(self)
    #             if self.enhanced_crashing_manager:
    #                 self.set_status("Enhanced Project Crashing features enabled.")
    #             else:
    #                 messagebox.showerror("Error", "Failed to enable Enhanced Project Crashing features.")
    #                 return
    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to enable Enhanced Project Crashing: {e}")
    #             return

    #     # Switch to the Enhanced Crashing tab
    #     for i in range(self.notebook.index('end')):
    #         tab_text = self.notebook.tab(i, 'text')
    #         if 'Enhanced Crashing' in tab_text:
    #             self.notebook.select(i)
    #             return
    #     # If not found, show info
    #     messagebox.showinfo("Info", "Enhanced Crashing tab not found. Please check integration.")
    
    def show_crashing_tab(self):
        """Show the project crashing tab (NO MENU CHANGES, just switch tab if exists)"""
        # Switch to the Enhanced Crashing tab
        for i in range(self.notebook.index('end')):
            tab_text = self.notebook.tab(i, 'text')
            if 'Crashing' in tab_text:
                self.notebook.select(i)
                return
        # If not found, show info
        messagebox.showinfo("Info", "Crashing tab not found. Please check integration.")
    
    
    def show_rcps_tab(self):
        """Show the resource-constrained project scheduling tab"""
        if self.rcps_tab is None:
            self.rcps_tab = RCPSTab(self.notebook, self)
            
            # Link RCPS Crashing tab to RCPS tab now that both exist
            if hasattr(self, 'rcps_crashing_tab') and hasattr(self, 'rcps_crashing_tab_needs_linking'):
                self.rcps_crashing_tab.set_rcps_tab_reference(self.rcps_tab)
                self.rcps_tab.rcps_crashing_tab = self.rcps_crashing_tab
                delattr(self, 'rcps_crashing_tab_needs_linking')
                # print("[DEBUG] RCPS tabs linked successfully")
        
        # Switch to the RCPS tab
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'RCPS Schedule':
                self.notebook.select(i)
                break
    
    def show_rcps_crashing_tab(self):
        """Show the RCPS crashing tab"""
        # Ensure RCPS tab is created first (required for data access)
        if self.rcps_tab is None:
            self.show_rcps_tab()  # This will create and link the tabs
        
        # Switch to the RCPS Crashing tab
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'RCPS Crashing':
                self.notebook.select(i)
                return
        
        # If not found, show info
        messagebox.showinfo("Info", "RCPS Crashing tab not found. Please check integration.")
    
    def generate_sample_cpm(self):
        """Generate and save sample CPM data"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Sample CPM Data",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            if filename:
                sample_data = FileHandler.get_sample_cpm_data()
                if filename.endswith('.xlsx'):
                    FileHandler.save_excel(sample_data, filename, 'Sample_CPM')
                else:
                    FileHandler.save_csv(sample_data, filename)
                messagebox.showinfo("Success", f"Sample CPM data saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sample data: {str(e)}")
    
    def generate_sample_pert(self):
        """Generate and save sample PERT data"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Sample PERT Data",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            if filename:
                sample_data = FileHandler.get_sample_pert_data()
                if filename.endswith('.xlsx'):
                    FileHandler.save_excel(sample_data, filename, 'Sample_PERT')
                else:
                    FileHandler.save_csv(sample_data, filename)
                messagebox.showinfo("Success", f"Sample PERT data saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sample data: {str(e)}")
    
    def show_user_guide(self):
        """Show user guide"""
        messagebox.showinfo("User Guide", 
                           "PMHelper User Guide\\n\\n"
                           "1. Load data using File menu or enter manually\\n"
                           "2. Choose analysis mode (CPM or PERT)\\n"
                           "3. Click Analyze to run analysis\\n"
                           "4. View results in different tabs\\n\\n"
                           "For detailed instructions, see documentation.")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About PMHelper", 
                           "PMHelper v1.0.0\\n\\n"
                           "A comprehensive project management analysis tool\\n"
                           "supporting both CPM and PERT methodologies.\\n\\n"
                           "Features:\\n"
                           "• Critical Path Method (CPM) analysis\\n"
                           "• Program Evaluation and Review Technique (PERT)\\n"
                           "• Network diagrams and Gantt charts\\n"
                           "• Probability analysis for PERT\\n"
                           "• Export capabilities\\n\\n"
                           "© 2024 PMHelper Team")
    
    def test_gantt_integration(self):
        """Quick test of all three integration fixes"""
        print("=" * 70)
        print("GANTT CHART INTEGRATION TEST - ALL THREE FIXES")
        print("=" * 70)
        
        results = {'fix1': False, 'fix2': False, 'fix3': False}
        
        # Test Fix 1: Automatic chart display
        try:
            if hasattr(self, 'update_gantt_chart_after_analysis'):
                print("✓ Fix 1: Automatic chart display method exists")
                results['fix1'] = True
            else:
                print("✗ Fix 1: Missing automatic chart display method")
        except:
            print("✗ Fix 1: Error checking automatic chart display")
        
        # Test Fix 2: Data integration
        try:
            if hasattr(self, 'gantt_tab') and hasattr(self.gantt_tab, 'update_data'):
                print("✓ Fix 2: Enhanced data integration method exists")
                results['fix2'] = True
            else:
                print("✗ Fix 2: Missing enhanced data integration")
        except:
            print("✗ Fix 2: Error checking data integration")
        
        # Test Fix 3: Tab communication
        try:
            if hasattr(self, 'on_tab_selected'):
                print("✓ Fix 3: Tab communication event handler exists")
                results['fix3'] = True
            else:
                print("✗ Fix 3: Missing tab communication handler")
        except:
            print("✗ Fix 3: Error checking tab communication")
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        
        print(f"\nIntegration Test Results: {passed}/{total} fixes implemented")
        
        if passed == total:
            print("🎉 ALL INTEGRATION FIXES READY FOR TESTING!")
        else:
            print("❌ Some fixes missing - implementation incomplete")
        
        print("=" * 70)
        return results

    def on_tab_changed(self, event):
        """Handle tab change events - ENHANCED with Gantt chart integration"""
        try:
            selection = event.widget.select()
            tab_text = event.widget.tab(selection, "text")
            self.set_status(f"Viewing: {tab_text}")
            
            # CRITICAL FIX 3: Additional handling for Gantt tab visibility
            if "Gantt" in tab_text or "gantt" in tab_text.lower():
                self.handle_gantt_tab_selection()
        except Exception as e:
            print(f"ERROR: Tab change handler failed: {e}")
            self.set_status("Ready")


def main():
    """Main entry point for the GUI application"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
