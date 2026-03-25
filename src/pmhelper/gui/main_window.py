#!/usr/bin/env python3
"""
Main Window Module

Contains the main application window and overall GUI structure for PMHelper.
Manages the main interface, tab navigation, and overall application state.
"""

from .tabs.rcps_crashing_tab import RCPSCrashingTab
from .tabs.crashing_tab import CrashingTab
from .tabs.rcps_tab import RCPSTab
from .tabs.probability_tab import ProbabilityTab
from .tabs.gantt_tab import GanttTab
from .tabs.pert_diagram_tab import PertDiagramTab
from .tabs.network_tab import NetworkTab
from .tabs.results_tab import ResultsTab
from .tabs.input_tab import InputTab
from .tabs.dpci_tab import DPCITab
from .tabs.charter_tab import CharterTab
from .tabs.charter_manager import CharterManager
from .tabs.selection_tab import SelectionTab
from .tabs.risk_tab import RiskAnalysisTab
from .tabs.optimization_tab import OptimizationTab

# Server mode components (import with try/except for compatibility)
try:
    from .tabs.server_tab import ServerTab
    SERVER_MODE_AVAILABLE = True
except ImportError as e:
    ServerTab = None
    SERVER_MODE_AVAILABLE = False
    print(f"Server mode not available: {e}")
from pmhelper.utils.file_handlers import FileHandler
from pmhelper.core.cpm_analyzer import CPMAnalyzer
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import math
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# Handle optional PERT analyzer import
try:
    from pmhelper.core.pert_analyzer import PERTAnalyzer
    PERT_AVAILABLE = True
except ImportError:
    PERTAnalyzer = None
    PERT_AVAILABLE = False


class MainWindow:
    """Main desktop application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("PMHelper - Project Management Analysis Tool")
        self.root.geometry("1400x900")

        # Initialize analyzers
        self.cpm_analyzer = CPMAnalyzer()
        if PERT_AVAILABLE:
            self.pert_analyzer = PERTAnalyzer()
        else:
            self.pert_analyzer = None

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

        # Setup cleanup handler for server resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        file_menu.add_command(
            label="Load CPM Data...",
            command=self.load_cpm_data)
        file_menu.add_command(
            label="Load PERT Data...",
            command=self.load_pert_data)
        file_menu.add_separator()
        file_menu.add_command(
            label="Save Results...",
            command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(
            label="Run CPM Analysis",
            command=self.run_cpm_analysis)
        analysis_menu.add_command(
            label="Run PERT Analysis",
            command=self.run_pert_analysis)
        analysis_menu.add_separator()
        analysis_menu.add_command(
            label="Project Crashing",
            command=self.show_crashing_tab)
        analysis_menu.add_command(
            label="Resource Scheduling",
            command=self.show_rcps_tab)
        analysis_menu.add_command(
            label="RCPS Crashing",
            command=self.show_rcps_crashing_tab)
        analysis_menu.add_separator()
        analysis_menu.add_command(
            label="Cost Optimization",
            command=self.show_optimization_tab)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(
            label="Generate Sample CPM Data",
            command=self.generate_sample_cpm)
        tools_menu.add_command(
            label="Generate Sample PERT Data",
            command=self.generate_sample_pert)

        # Server menu (if available)
        if SERVER_MODE_AVAILABLE:
            server_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Server", menu=server_menu)
            server_menu.add_command(
                label="Go to Server Tab",
                command=self.show_server_tab)
            server_menu.add_separator()
            server_menu.add_command(
                label="Start Server",
                command=self.start_server)
            server_menu.add_command(
                label="Stop Server", 
                command=self.stop_server)
            server_menu.add_separator()
            server_menu.add_command(
                label="Open API Documentation",
                command=self.open_api_docs)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(
            label="Complete User Guide",
            command=self.show_user_guide)
        help_menu.add_separator()

        # Tab-specific help submenu
        tab_help_menu = tk.Menu(help_menu, tearoff=0)
        help_menu.add_cascade(label="Tab Help", menu=tab_help_menu)
        tab_help_menu.add_command(
            label="Input Tab Help",
            command=self.show_input_tab_help)
        tab_help_menu.add_command(
            label="Results Tab Help",
            command=self.show_results_tab_help)
        tab_help_menu.add_command(
            label="Network Tab Help",
            command=self.show_network_tab_help)
        tab_help_menu.add_command(
            label="Gantt Tab Help",
            command=self.show_gantt_tab_help)
        tab_help_menu.add_command(
            label="Probability Tab Help",
            command=self.show_probability_tab_help)
        tab_help_menu.add_command(
            label="RCPS Tab Help",
            command=self.show_rcps_tab_help)
        tab_help_menu.add_command(
            label="Crashing Tab Help",
            command=self.show_crashing_tab_help)
        tab_help_menu.add_command(
            label="RCPS Crashing Tab Help",
            command=self.show_rcps_crashing_tab_help)

        help_menu.add_separator()
        help_menu.add_command(label="About PMHelper", command=self.show_about)

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

        # PRODUCTION FIX: Always create and show RCPS tab in correct order
        self.crashing_tab = CrashingTab(self.notebook, self)
        self.notebook.add(self.crashing_tab, text="Crashing")

        # RCPS tab - always visible between Crashing and RCPS Crashing
        self.rcps_tab = RCPSTab(self.notebook, self)
        self.notebook.add(self.rcps_tab.rcps_frame,
                          text="RCPS")  # Add the frame, not the object

        # Add RCPS Crashing tab
        self.rcps_crashing_tab = RCPSCrashingTab(self.notebook, self)
        self.notebook.add(self.rcps_crashing_tab, text="RCPS Crashing")

        # Add Project Charter tab
        self.charter_tab = CharterTab(self.notebook, self)
        self.notebook.add(self.charter_tab, text="Project Charter")
        

        # Add Charter Manager tab
        self.charter_manager = CharterManager(
            self.notebook,
            on_open_callback=self._open_charter_from_manager,
            on_duplicate_callback=self._open_charter_from_manager
        )
        self.notebook.add(self.charter_manager, text="Charter Manager")

        # Add DPCI Assessment tab
        self.dpci_tab = DPCITab(self.notebook)
        self.notebook.add(self.dpci_tab, text="DPCI Assessment")

        # Add Project Selection tab
        self.selection_tab = SelectionTab(self.notebook, self)

        # Add Risk Analysis tab
        self.risk_tab = RiskAnalysisTab(self.notebook, self)

        # Add Cost Optimization tab
        self.optimization_tab = OptimizationTab(self.notebook, self.cpm_analyzer)
        self.notebook.add(self.optimization_tab, text="Cost Optimization")

        # Add Server tab (if available)
        if SERVER_MODE_AVAILABLE:
            try:
                self.server_tab = ServerTab(self.notebook, self)
            except Exception as e:
                print(f"Warning: Failed to create Server tab: {e}")
                self.server_tab = None
        else:
            self.server_tab = None

        # Setup tab references for data sharing
        self.setup_tab_references()

        # CRITICAL FIX 3: Add tab communication event handling
        self.setup_tab_communication()

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def setup_tab_references(self):
        """Setup cross-references between tabs for data sharing"""
        # PRODUCTION FIX: Since RCPS tab is now always created, establish the
        # links immediately
        if hasattr(self, 'rcps_tab') and hasattr(self, 'rcps_crashing_tab'):
            self.rcps_crashing_tab.set_rcps_tab_reference(self.rcps_tab)
            self.rcps_tab.rcps_crashing_tab = self.rcps_crashing_tab

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

            # If Gantt Chart tab is selected and we have analysis results,
            # ensure chart is displayed
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
                if not hasattr(
                        self.gantt_tab,
                        'results_data') or not self.gantt_tab.results_data:
                    # print("DEBUG: Sending analysis results to Gantt tab")
                    self.gantt_tab.update_data(
                        self.results_data, getattr(
                            self, 'analysis_mode', 'deterministic'))

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
        result = messagebox.askyesno(
            "New Project", "This will clear all current data. Continue?")
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
                title="Load CPM Data", filetypes=[
                    ("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")])
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
                title="Load PERT Data", filetypes=[
                    ("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")])
            if filename:
                self.input_tab.load_file(filename, 'probabilistic')
                self.set_status(f"Loaded PERT data from {filename}")
                # Automatically run PERT analysis after loading data
                self.set_analysis_mode('probabilistic')
                self.run_pert_analysis()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to load PERT data: {
                    str(e)}")

    def save_results(self):
        """Save analysis results to file"""
        if not self.current_analyzer or not hasattr(
                self.current_analyzer, 'G') or not self.current_analyzer.G:
            messagebox.showwarning(
                "Warning", "No analysis results to save. Please run analysis first.")
            return

        try:
            self.results_tab.save_results()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")

    def run_cpm_analysis(self):
        """Run CPM analysis"""
        if self.analysis_mode != 'deterministic':
            messagebox.showwarning(
                "Warning", "Please load CPM data first or switch to deterministic mode.")
            return

        self.analyze_project()

    def run_pert_analysis(self):
        """Run PERT analysis"""
        if self.analysis_mode != 'probabilistic':
            messagebox.showwarning(
                "Warning", "Please load PERT data first or switch to probabilistic mode.")
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
                messagebox.showwarning(
                    "Warning", "Please enter some activities to analyze.")
                return

            if not self.current_analyzer:
                messagebox.showwarning(
                    "Warning", "Please select an analysis mode (CPM or PERT).")
                return

            # [DEBUG] Check analysis mode and data
            print(f"\n[DEBUG_ANALYZE] [MAIN WINDOW] ANALYSIS DEBUG")
            print(f"   Analysis mode: {self.analysis_mode}")
            print(f"   Current analyzer: {type(self.current_analyzer)}")
            print(f"   Activities data count: {len(activities_data)}")
            print(
                f"   Sample activity data: {
                    activities_data[0] if activities_data else 'None'}")

            self.set_status("Running analysis...")

            # Perform analysis
            G, critical_paths, critical_activities = self.current_analyzer.analyze(
                activities_data)

            # [DEBUG] Check analysis results
            print(f"\n[DEBUG_COST] [ANALYSIS RESULTS] COST DATA CHECK")
            print(f"   Graph created: {G is not None}")
            if G:
                print(f"   Graph nodes: {list(G.nodes())}")
                for node_id, node_data in G.nodes(data=True):
                    if node_id not in ['START', 'END']:
                        crash_cost = node_data.get('crash_cost', 'MISSING')
                        normal_cost = node_data.get('normal_cost', 'MISSING')
                        print(
                            f"   {node_id}: crash_cost={crash_cost}, normal_cost={normal_cost}")

            # [DEBUG] Check analyzer state after analysis
            print(f"\n[DEBUG_DATA] [ANALYZER STATE] AFTER ANALYSIS")
            if hasattr(self.current_analyzer, 'activities'):
                print(
                    f"   Analyzer has activities: {len(self.current_analyzer.activities)}")
                # Show first 3
                for activity in self.current_analyzer.activities[:3]:
                    print(f"   Activity: {activity}")
            else:
                print(f"   Analyzer has NO activities attribute")

            if hasattr(self.current_analyzer, 'G'):
                print(
                    f"   Analyzer has graph G: {
                        self.current_analyzer.G is not None}")
            else:
                print(f"   Analyzer has NO graph G")

            # Store analyzer references for RCPS/Crashing
            if self.analysis_mode == 'probabilistic':
                self.pert_analyzer = self.current_analyzer
                print(
                    f"   [DEBUG_SUCCESS] PERT analyzer stored in main window")
            else:
                self.cmp_analyzer = self.current_analyzer
                print(f"   [DEBUG_SUCCESS] CPM analyzer stored in main window")

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
                activity_id = activity_data.get(
                    'id', activity_data.get('Activity', ''))

                # Get node data from graph if available
                node_data = G.nodes.get(activity_id, {}) if G else {}

                # Standardize predecessor IDs: split, strip, and rejoin
                raw_preds = activity_data.get(
                    'predecessors', activity_data.get(
                        'Predecessors', ''))
                if isinstance(raw_preds, str):
                    preds_clean = ','.join(
                        [p.strip() for p in raw_preds.split(',') if p.strip()])
                else:
                    preds_clean = ''
                activity_display = {
                    'id': activity_id,
                    'name': activity_data.get('activity', activity_data.get('name', activity_data.get('Activity', activity_id))),
                    'duration': activity_data.get('duration', activity_data.get('Duration', 0)),
                    # FIXED: Use correct field names
                    'ES': node_data.get('ES', 0),
                    # FIXED: Use correct field names
                    'EF': node_data.get('EF', 0),
                    # FIXED: Use correct field names
                    'LS': node_data.get('LS', 0),
                    # FIXED: Use correct field names
                    'LF': node_data.get('LF', 0),
                    'float': node_data.get('float', 0),
                    'critical': activity_id in critical_activities,
                    'predecessors': preds_clean,
                    # Ensure resource column for RCPS
                    'resource': activity_data.get('resource', activity_data.get('resource_demand', 1)),
                }

                # Add PERT-specific data if in probabilistic mode
                if self.analysis_mode == 'probabilistic':
                    opt = activity_data.get(
                        'optimistic', activity_data.get(
                            'Optimistic', 0))
                    most = activity_data.get(
                        'most_likely', activity_data.get(
                            'Most_Likely', 0))
                    pess = activity_data.get(
                        'pessimistic', activity_data.get(
                            'Pessimistic', 0))
                    expected_time = (
                        float(opt) + 4 * float(most) + float(pess)) / 6
                    variance = ((float(pess) - float(opt)) / 6) ** 2

                    activity_display.update({
                        'optimistic': opt,
                        'most_likely': most,
                        'pessimistic': pess,
                        'expected_duration': expected_time,  # Keep precise for any legacy needs
                        # Integer expected duration for display
                        'expected': math.ceil(expected_time),
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
                # For PERT/RCPS, set duration to ceil(expected_duration) if
                # available
                if self.analysis_mode == 'probabilistic' and 'expected_duration' in df_gantt.columns:
                    df_gantt['duration'] = np.ceil(
                        df_gantt['expected_duration']).astype(int)
                # Ensure all required columns are present and filled
                required_cols = [
                    'id',
                    'early_start',
                    'duration',
                    'resource',
                    'late_finish',
                    'float']
                for col in required_cols:
                    if col not in df_gantt.columns:
                        df_gantt[col] = 0 if col != 'id' else ''
                # Fill NaN or empty values with defaults
                df_gantt['id'] = df_gantt['id'].replace('', pd.NA).fillna('X')
                df_gantt['early_start'] = pd.to_numeric(
                    df_gantt['early_start'], errors='coerce').fillna(0).astype(int)
                df_gantt['duration'] = pd.to_numeric(
                    df_gantt['duration'], errors='coerce').fillna(1).astype(int)
                df_gantt['resource'] = pd.to_numeric(
                    df_gantt['resource'], errors='coerce').fillna(1).astype(int)
                df_gantt['late_finish'] = pd.to_numeric(
                    df_gantt['late_finish'], errors='coerce').fillna(0).astype(int)
                df_gantt['float'] = pd.to_numeric(
                    df_gantt['float'], errors='coerce').fillna(0).astype(int)
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
                # Calculate precise expected duration from critical path using
                # statistical values
                precise_expected_duration = 0
                if critical_path:
                    for activity_id in critical_path:
                        if activity_id not in ['START', 'END']:
                            # Find the original activity data to get precise
                            # expected_time
                            for activity_data in activities_data:
                                if activity_data.get('id') == activity_id:
                                    # Calculate precise expected time using
                                    # PERT formula
                                    opt = float(
                                        activity_data.get(
                                            'optimistic', 0))
                                    most = float(
                                        activity_data.get(
                                            'most_likely', 0))
                                    pess = float(
                                        activity_data.get(
                                            'pessimistic', 0))
                                    precise_expected_duration += (
                                        opt + 4 * most + pess) / 6
                                    break

                # Get PERT statistics from the analyzer
                project_variance = self.current_analyzer.project_variance
                # Already rounded to 3 decimals
                standard_deviation = self.current_analyzer.project_std

                self.results_data.update({
                    'expected_duration': precise_expected_duration,  # Use precise statistical value
                    'project_variance': project_variance,
                    'standard_deviation': standard_deviation
                })

            # Update results in all tabs
            self.results_tab.update_results(
                self.results_data, self.analysis_mode)
            self.network_tab.update_network(
                self.results_data, self.analysis_mode)
            self.pert_diagram_tab.update_network(
                self.results_data, self.analysis_mode)

            # CRITICAL FIX 1: Automatic Gantt chart update after analysis
            self.update_gantt_chart_after_analysis(self.results_data)

            # Update probability tab if in PERT mode
            if self.analysis_mode == 'probabilistic':
                try:
                    self.probability_tab.update_analysis(self.results_data)
                except Exception as e:
                    print(f"WARNING: Failed to update ProbabilityTab: {e}")
                    # Continue execution - don't let probability tab errors
                    # crash analysis

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
        messagebox.showinfo(
            "Info", "Crashing tab not found. Please check integration.")

    def show_rcps_tab(self):
        """Switch to the RCPS tab (now always visible)"""
        # PRODUCTION FIX: RCPS tab is now always visible, just switch to it
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'RCPS':
                self.notebook.select(i)
                return

        # Fallback (should not be needed since tab is always visible)
        messagebox.showinfo(
            "Info", "RCPS tab not found. Please check integration.")

    def show_rcps_crashing_tab(self):
        """Show the RCPS crashing tab"""
        # PRODUCTION FIX: Since RCPS tab is now always created, no need to
        # check or create it

        # Switch to the RCPS Crashing tab
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'RCPS Crashing':
                self.notebook.select(i)
                return

        # If not found, show info
        messagebox.showinfo(
            "Info", "RCPS Crashing tab not found. Please check integration.")
    
    def show_optimization_tab(self):
        """Show the Cost Optimization tab"""
        # Switch to the Cost Optimization tab
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'Cost Optimization':
                self.notebook.select(i)
                # Update analyzer if CPM has been run
                if hasattr(self, 'optimization_tab') and self.current_analyzer:
                    self.optimization_tab.set_analyzer(self.current_analyzer)
                return
        
        # If not found, show info
        messagebox.showinfo(
            "Info", "Cost Optimization tab not found. Please check integration.")

    def show_server_tab(self):
        """Show the Server tab"""
        if not SERVER_MODE_AVAILABLE or not hasattr(self, 'server_tab') or not self.server_tab:
            messagebox.showwarning("Server Mode", "Server mode is not available in this installation.")
            return
        
        # Switch to the Server tab
        for i in range(self.notebook.index('end')):
            if self.notebook.tab(i, 'text') == 'Server':
                self.notebook.select(i)
                return
    
    def start_server(self):
        """Start the PMHelper server"""
        if not SERVER_MODE_AVAILABLE or not hasattr(self, 'server_tab') or not self.server_tab:
            messagebox.showwarning("Server Mode", "Server mode is not available in this installation.")
            return
        
        try:
            self.server_tab.control_panel.start_server()
        except Exception as e:
            messagebox.showerror("Server Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self):
        """Stop the PMHelper server"""
        if not SERVER_MODE_AVAILABLE or not hasattr(self, 'server_tab') or not self.server_tab:
            messagebox.showwarning("Server Mode", "Server mode is not available in this installation.")
            return
        
        try:
            self.server_tab.control_panel.stop_server()
        except Exception as e:
            messagebox.showerror("Server Error", f"Failed to stop server: {str(e)}")
    
    def open_api_docs(self):
        """Open API documentation in browser"""
        if not SERVER_MODE_AVAILABLE or not hasattr(self, 'server_tab') or not self.server_tab:
            messagebox.showwarning("Server Mode", "Server mode is not available in this installation.")
            return
        
        if not self.server_tab.is_server_running():
            messagebox.showinfo("Server Not Running", "Please start the server first to access the API documentation.")
            return
        
        try:
            import webbrowser
            webbrowser.open(f"{self.server_tab.get_server_url()}/docs")
        except Exception as e:
            messagebox.showerror("Browser Error", f"Failed to open API documentation: {str(e)}")

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
                messagebox.showinfo(
                    "Success", f"Sample CPM data saved to {filename}")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save sample data: {
                    str(e)}")

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
                    FileHandler.save_excel(
                        sample_data, filename, 'Sample_PERT')
                else:
                    FileHandler.save_csv(sample_data, filename)
                messagebox.showinfo(
                    "Success", f"Sample PERT data saved to {filename}")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save sample data: {
                    str(e)}")

    def show_user_guide(self):
        """Show comprehensive user guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("PMHelper - Complete User Guide")
        guide_window.geometry("900x700")
        guide_window.resizable(True, True)

        # Create scrollable text widget
        frame = ttk.Frame(guide_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 11))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        guide_text = """PMHelper - Complete User Guide

═══════════════════════════════════════════════════════════════════════

OVERVIEW
PMHelper is a comprehensive project management analysis tool supporting multiple methodologies:
• Critical Path Method (CPM) - Deterministic analysis
• Program Evaluation and Review Technique (PERT) - Probabilistic analysis
• Resource-Constrained Project Scheduling (RCPS)
• Project Crashing optimization
• Network diagrams and Gantt charts

═══════════════════════════════════════════════════════════════════════

QUICK START GUIDE

1. DATA INPUT
   • Use the Input tab to enter project activities
   • Each activity needs: ID, Name, Duration, Predecessors
   • For PERT analysis, add optimistic/pessimistic durations
   • Import from CSV files via File menu

2. ANALYSIS MODES
   • CPM (Deterministic): Uses fixed durations
   • PERT (Probabilistic): Uses three-point estimates

3. BASIC WORKFLOW
   • Enter or load activity data
   • Click "Run CPM Analysis" or "Run PERT Analysis"
   • View results in Results tab
   • Check Network tab for visual diagram
   • Use Gantt tab for timeline visualization

═══════════════════════════════════════════════════════════════════════

TAB-SPECIFIC HELP

For detailed help on any specific tab, use the Help buttons in each tab or:
• Help Menu → Input Tab Help
• Help Menu → Results Tab Help
• Help Menu → Network Tab Help
• Help Menu → Gantt Tab Help
• Help Menu → Probability Tab Help
• Help Menu → RCPS Tab Help
• Help Menu → Crashing Tab Help

═══════════════════════════════════════════════════════════════════════

ADVANCED FEATURES

PROJECT CRASHING
• Reduces project duration by spending additional resources
• Define crash costs and crash durations for activities
• Algorithm finds optimal crashing strategy

RESOURCE-CONSTRAINED PROJECT SCHEDULING (RCPS)
• Schedules projects with limited resources
• Define resource requirements and availability
• Uses priority rules for resource allocation

PROBABILITY ANALYSIS (PERT)
• Calculate probability of meeting deadlines
• Statistical analysis of project completion times

═══════════════════════════════════════════════════════════════════════

FILE OPERATIONS

IMPORT/EXPORT
• Supported formats: CSV files
• Use File menu for import/export operations
• Export analysis results and charts

DATA FORMAT REQUIREMENTS
• Activity ID: Unique identifier
• Activity Name: Descriptive name
• Duration: Time units (days, weeks, etc.)
• Predecessors: Comma-separated list of predecessor IDs
• Resources (for RCPS): Resource type and quantity

FUTURE DEPLOYMENTS
The following features are planned for future releases:
• Excel (.xlsx, .xls) import/export support
• Monte Carlo simulation for risk analysis

═══════════════════════════════════════════════════════════════════════

TROUBLESHOOTING

COMMON ISSUES
• Circular dependencies: Check predecessor relationships
• Missing predecessors: Ensure all referenced activities exist
• Data format errors: Verify CSV format matches requirements
• Analysis failures: Check for complete activity data

GETTING HELP
• Use Help buttons in individual tabs for specific guidance
• Check About dialog for version and feature information
• Refer to this guide for comprehensive instructions

═══════════════════════════════════════════════════════════════════════"""

        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)

        # Add close button
        close_btn = ttk.Button(
            guide_window,
            text="Close",
            command=guide_window.destroy)
        close_btn.pack(pady=10)

        # Center the window
        guide_window.transient(self.root)
        guide_window.grab_set()

    def show_input_tab_help(self):
        """Show Input tab specific help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Input Tab - Help")
        help_window.geometry("700x500")

        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = """INPUT TAB - DETAILED HELP

═══════════════════════════════════════════════════════════════════════

PURPOSE
The Input tab is where you define your project activities and their relationships.

ACTIVITY FIELDS

1. ACTIVITY ID
   • Unique identifier for each activity (e.g., A, B, C or 1, 2, 3)
   • Use consistent naming convention
   • Cannot be empty or duplicate

2. ACTIVITY NAME
   • Descriptive name for the activity
   • Helps identify activities in reports and charts
   • Can contain spaces and special characters

3. DURATION
   • Time required to complete the activity
   • Use consistent time units (days, weeks, months)
   • Must be positive number
   • For PERT: This becomes the "most likely" duration

4. PREDECESSORS
   • Activities that must complete before this activity starts
   • Enter as comma-separated list (e.g., "A,B,C")
   • Leave blank for activities with no predecessors
   • Must reference existing activity IDs

5. PERT-SPECIFIC FIELDS (for probabilistic analysis)
   • Optimistic Duration: Best-case scenario time
   • Pessimistic Duration: Worst-case scenario time
   • Most Likely Duration: Normal expected time

6. RESOURCE FIELDS (for RCPS analysis)
   • Resource Type: Name of required resource (e.g., "Workers", "Equipment")
   • Resource Quantity: Number of resource units needed

═══════════════════════════════════════════════════════════════════════

HOW TO USE

ADDING ACTIVITIES
1. Click "Add Activity" button
2. Fill in all required fields in the form
3. Click "Save Activity" to add to the table
4. Repeat for each project activity

EDITING ACTIVITIES
1. Select activity row in the table
2. Click "Edit Selected" button
3. Modify fields in the form
4. Click "Update Activity" to save changes

DELETING ACTIVITIES
1. Select activity row in the table
2. Click "Delete Selected" button
3. Confirm deletion when prompted

IMPORTING DATA
• Use File → Import Data to load from CSV files
• Ensure your file matches the expected format
• Sample data is loaded automatically when application starts

LOAD SAMPLE DATA FUNCTION
The "Load Sample Data" button provides predefined project examples:
• Sample CPM Project: A simple construction project with 7 activities
• Sample PERT Project: A software development project with uncertainty estimates
• These examples help you understand the data format and test analysis features
• Sample data is automatically loaded when you first open the application

FUTURE DEPLOYMENTS
The following features are planned for future releases:
• Excel (.xlsx, .xls) import capabilities
• Advanced data validation tools
• Template projects for different industries

═══════════════════════════════════════════════════════════════════════

TIPS & BEST PRACTICES

• Start with a simple project structure
• Use descriptive activity names
• Double-check predecessor relationships
• Ensure all predecessors are defined before referencing them
• Use consistent time units throughout the project
• Test with sample data first before entering complex projects

═══════════════════════════════════════════════════════════════════════"""

        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)

        help_window.transient(self.root)

    def show_results_tab_help(self):
        """Show Results tab specific help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Results Tab - Help")
        help_window.geometry("700x500")

        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = """RESULTS TAB - DETAILED HELP

═══════════════════════════════════════════════════════════════════════

PURPOSE
The Results tab displays the calculated analysis results for your project.

ANALYSIS RESULTS

PROJECT SUMMARY
• Total Project Duration: Overall time to complete the project
• Critical Path: Sequence of activities that determines project duration
• Number of Critical Activities: Count of activities on critical path

ACTIVITY SCHEDULE TABLE
Columns explained:

1. ACTIVITY ID & NAME
   • Unique identifier and descriptive name

2. DURATION
   • Time required to complete the activity

3. EARLIEST START (ES)
   • Earliest time the activity can begin
   • Based on predecessor completion times

4. EARLIEST FINISH (EF)
   • Earliest time the activity can complete
   • Calculated as ES + Duration

5. LATEST START (LS)
   • Latest time activity can start without delaying project
   • Critical for identifying schedule flexibility

6. LATEST FINISH (LF)
   • Latest time activity can finish without delaying project

7. TOTAL FLOAT (SLACK)
   • Amount of time activity can be delayed without affecting project
   • Zero float = Critical activity
   • Positive float = Non-critical activity

8. CRITICAL
   • Yes/No indicator if activity is on critical path
   • Critical activities have zero total float

═══════════════════════════════════════════════════════════════════════

INTERPRETING RESULTS

CRITICAL PATH ANALYSIS
• Critical activities must be closely monitored
• Any delay in critical activities delays the entire project
• Focus resources on critical activities for schedule compression

FLOAT ANALYSIS
• Activities with float provide scheduling flexibility
• Use float activities as buffers for resource allocation
• Float can be used to level resources or manage risks

PERT-SPECIFIC RESULTS (when applicable)
• Expected Duration: Weighted average of optimistic, most likely, pessimistic
• Variance: Measure of uncertainty in activity duration
• Standard Deviation: Square root of variance

═══════════════════════════════════════════════════════════════════════

USING THE RESULTS

PROJECT MANAGEMENT
1. Identify critical activities for priority focus
2. Use float information for resource optimization
3. Monitor early/late start dates for scheduling
4. Plan contingencies for high-variance activities (PERT)

SCHEDULE OPTIMIZATION
• Activities with float can be delayed if needed
• Critical activities need precise scheduling
• Use results to create detailed project timeline

EXPORT OPTIONS
• Export results table to CSV files
• Print results for documentation
• Save analysis for future reference

FUTURE DEPLOYMENTS
The following features are planned for future releases:
• Excel export capabilities
• Advanced reporting templates
• Real-time progress tracking integration
• Custom report generation
• Dashboard views with key metrics

═══════════════════════════════════════════════════════════════════════"""

        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)

        help_window.transient(self.root)

    def show_network_tab_help(self):
        """Show Network tab specific help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Network Tab - Help")
        help_window.geometry("700x500")

        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = """NETWORK TAB - DETAILED HELP

═══════════════════════════════════════════════════════════════════════

PURPOSE
The Network tab displays a visual network diagram showing activity relationships and the critical path.

NETWORK DIAGRAM ELEMENTS

NODES (ACTIVITIES)
• Circles represent project activities
• Node color indicates critical path status:
  - Red: Critical activities (zero float)
  - Blue: Non-critical activities (positive float)
• Node labels show activity ID and name

ARROWS (DEPENDENCIES)
• Lines connect predecessor to successor activities
• Arrow direction shows dependency flow
• Critical path arrows may be highlighted differently

NODE INFORMATION
Each node typically displays:
• Activity ID
• Activity Name
• Duration
• Early Start (ES) / Early Finish (EF)
• Late Start (LS) / Late Finish (LF)

═══════════════════════════════════════════════════════════════════════

READING THE DIAGRAM

CRITICAL PATH IDENTIFICATION
• Critical activities form an unbroken chain from start to finish
• These activities have zero total float
• Critical path determines minimum project duration

DEPENDENCY RELATIONSHIPS
• Follow arrows to see activity sequence requirements
• Parallel activities can be performed simultaneously
• Convergence points show where multiple activities must complete

SCHEDULE ANALYSIS
• Use early/late times to understand scheduling flexibility
• Identify potential bottlenecks and resource conflicts
• Plan activity sequences and resource allocation

═══════════════════════════════════════════════════════════════════════

USING THE NETWORK DIAGRAM

PROJECT PLANNING
• Visualize project workflow and dependencies
• Identify parallel work opportunities
• Plan resource allocation and team assignments

SCHEDULE MANAGEMENT
• Monitor critical activities closely
• Use non-critical activities for schedule buffering
• Plan alternative paths in case of delays

COMMUNICATION
• Share visual representation with stakeholders
• Explain project logic and critical activities
• Document project structure for team understanding

DIAGRAM CONTROLS
• Zoom in/out for better visibility
• Pan to navigate large diagrams
• Export diagram for documentation
• Print for offline reference

═══════════════════════════════════════════════════════════════════════

TROUBLESHOOTING

COMMON ISSUES
• Overlapping nodes: Zoom out or resize window
• Missing connections: Check predecessor data in Input tab
• Layout problems: Regenerate diagram after data changes
• Critical path not visible: Verify analysis was run successfully

FUTURE DEPLOYMENTS
The following features are planned for future releases:
• Interactive node editing and manipulation
• Advanced layout algorithms for complex networks
• Custom node shapes and styling options
• Enhanced export formats and print options
• Real-time updates during project execution

═══════════════════════════════════════════════════════════════════════"""

        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)

        help_window.transient(self.root)

    def show_gantt_tab_help(self):
        """Show Gantt tab specific help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Gantt Tab - Help")
        help_window.geometry("700x500")

        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = """GANTT TAB - DETAILED HELP

═══════════════════════════════════════════════════════════════════════

PURPOSE
The Gantt tab displays a timeline view of your project schedule showing when activities occur and their durations.

GANTT CHART ELEMENTS

TIMELINE BARS
• Horizontal bars represent activity durations
• Bar position shows when activity occurs
• Bar length represents activity duration
• Color coding indicates activity status:
  - Red: Critical activities
  - Blue: Non-critical activities
  - Green: Completed activities (if tracking progress)

TIME SCALE
• X-axis shows project timeline (days, weeks, months)
• Scale adjusts based on project duration
• Grid lines help read exact dates/times

ACTIVITY LIST
• Y-axis lists all project activities
• Activities sorted by start time or ID
• Activity names displayed on left side

DEPENDENCIES
• Lines or arrows may show predecessor relationships
• Helps visualize activity sequence requirements

═══════════════════════════════════════════════════════════════════════

READING THE GANTT CHART

SCHEDULE INFORMATION
• Activity start and finish times clearly visible
• Project duration shown across full timeline
• Overlapping bars indicate parallel activities
• Gaps show waiting time or float

CRITICAL PATH VISUALIZATION
• Critical activities form continuous chain
• No gaps between critical activities
• Critical path determines project end date

RESOURCE PLANNING
• Overlapping activities need resource consideration
• Identify peak resource demand periods
• Plan resource leveling for efficient allocation

═══════════════════════════════════════════════════════════════════════

USING THE GANTT CHART

PROJECT SCHEDULING
• Create detailed project timeline
• Assign start dates to activities
• Plan milestone dates and deadlines
• Communicate schedule to team members

PROGRESS TRACKING
• Update activity completion status
• Compare actual vs. planned progress
• Identify schedule deviations early
• Replan remaining activities as needed

RESOURCE MANAGEMENT
• Identify resource conflicts from overlapping activities
• Plan equipment and personnel allocation
• Schedule resource-dependent activities
• Balance workload across project duration

STAKEHOLDER COMMUNICATION
• Visual timeline easy for non-technical audiences
• Show project milestones and deliverables
• Demonstrate project progress and status
• Explain schedule impacts of changes

═══════════════════════════════════════════════════════════════════════

CHART CONTROLS

NAVIGATION
• Zoom in/out for different time scales
• Pan left/right to navigate timeline
• Scroll up/down for large activity lists

EXPORT OPTIONS
• Save chart as image file
• Print for documentation
• Export to PDF for sharing
• Include in project reports

CUSTOMIZATION
• Adjust time scale (days, weeks, months)
• Filter activities by status or type
• Show/hide dependency lines
• Modify color schemes

FUTURE DEPLOYMENTS
The following features are planned for future releases:
• Interactive activity editing directly on the chart
• Progress tracking with percentage completion
• Resource allocation visualization
• Baseline comparison capabilities
• Advanced filtering and grouping options

═══════════════════════════════════════════════════════════════════════"""

        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)

        help_window.transient(self.root)

    def show_probability_tab_help(self):
        """Show Probability tab specific help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Probability Tab - Help")
        help_window.geometry("700x500")

        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = """PROBABILITY TAB - DETAILED HELP

═══════════════════════════════════════════════════════════════════════

PURPOSE
The Probability tab provides statistical analysis for PERT projects, including probability calculations for project completion times.

PROBABILITY ANALYSIS FEATURES

TARGET DATE PROBABILITY
• Calculate probability of completing project by specific date
• Enter target completion date
• Get percentage probability of meeting deadline
• Based on project duration distribution

CONFIDENCE INTERVALS
• Show range of likely completion times
• 90%, 95%, 99% confidence levels
• Helps establish realistic project deadlines
• Accounts for uncertainty in activity durations

STATISTICAL CALCULATIONS
• Uses analytical PERT formulas for probability calculations
• Based on normal distribution approximation
• Calculates expected times and variances for the critical path
• Provides quick and reliable probability estimates

═══════════════════════════════════════════════════════════════════════

STATISTICAL MEASURES

PROJECT DURATION STATISTICS
• Expected Duration: Mean completion time using PERT formula
• Standard Deviation: Measure of project duration variability
• Variance: Square of standard deviation
• Critical Path Analysis: Focus on activities affecting project duration

DISTRIBUTION ANALYSIS
• Normal distribution curve showing project completion probability
• Probability density function visualization
• Percentile calculations for different confidence levels
• Statistical summary of project timing uncertainty

RISK ANALYSIS
• Probability of schedule overrun beyond target dates
• Expected completion time ranges
• Critical path uncertainty analysis
• Activity variance contribution to project risk

═══════════════════════════════════════════════════════════════════════

HOW TO USE

SETTING UP ANALYSIS
1. Ensure PERT analysis has been run first
2. Activities must have optimistic, most likely, and pessimistic durations
3. Enter target completion date for probability calculation
4. View the calculated probability and statistical measures

INTERPRETING RESULTS
• Higher probability = more likely to meet deadline
• Larger standard deviation = higher uncertainty in project timing
• Use confidence intervals to establish realistic deadline ranges
• Critical path variance shows which activities contribute most to uncertainty

RISK MANAGEMENT
• Use probability calculations for contingency planning
• Focus on critical path activities with high variance
• Plan buffers based on confidence intervals
• Set realistic expectations with stakeholders

═══════════════════════════════════════════════════════════════════════

ANALYTICAL APPROACH

PERT FORMULAS
• Expected Time = (Optimistic + 4×Most Likely + Pessimistic) / 6
• Activity Variance = ((Pessimistic - Optimistic) / 6)²
• Project Variance = Sum of critical path activity variances
• Standard Deviation = Square root of project variance

PROBABILITY CALCULATIONS
• Uses normal distribution approximation for project completion
• Calculates Z-score for target dates
• Converts Z-scores to probability percentages
• Provides confidence intervals for different probability levels

ASSUMPTIONS
• Activity durations follow beta distribution
• Central Limit Theorem applies to project duration
• Activities are independent (no correlations)
• Focus on critical path for project duration analysis

FUTURE DEPLOYMENTS
The following features are planned for future releases:
• Monte Carlo simulation for enhanced accuracy
• Correlation analysis between activities
• Advanced risk modeling capabilities
• Sensitivity analysis for individual activities

═══════════════════════════════════════════════════════════════════════

PRACTICAL APPLICATIONS

PROJECT PLANNING
• Set realistic deadlines based on probability analysis
• Plan contingencies for low-probability scenarios
• Communicate uncertainty to stakeholders
• Justify schedule buffers with statistical evidence

RISK MANAGEMENT
• Identify high-risk activities needing attention
• Quantify schedule risk for project portfolio
• Plan mitigation strategies for critical uncertainties
• Monitor variance reduction during project execution

CONTRACT NEGOTIATIONS
• Support deadline negotiations with probability data
• Justify contract terms based on risk analysis
• Set performance incentives aligned with probabilities
• Document assumptions for scope change discussions

═══════════════════════════════════════════════════════════════════════"""

        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)

        help_window.transient(self.root)

    def show_rcps_tab_help(self):
        """Show RCPS tab specific help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("RCPS Tab - Help")
        help_window.geometry("700x500")

        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = """RCPS TAB - DETAILED HELP
Resource-Constrained Project Scheduling

═══════════════════════════════════════════════════════════════════════

PURPOSE
The RCPS tab handles project scheduling when resources are limited, unlike standard CPM which assumes unlimited resources.

KEY CONCEPTS

RESOURCE CONSTRAINTS
• Limited availability of personnel, equipment, materials
• Activities compete for same resources
• Resource conflicts cause schedule delays beyond critical path
• Requires priority-based scheduling decisions

RESOURCE LEVELING vs. RESOURCE-CONSTRAINED SCHEDULING
• Leveling: Smooth resource usage within float
• Constrained: Hard limits on resource availability
• RCPS uses constrained approach with priority rules

PRIORITY RULES
• Earliest Start Time (EST): Schedule activities by early start
• Shortest Processing Time (SPT): Prioritize shorter activities
• Latest Start Time (LST): Priority to activities with latest start
• Resource Requirements: Consider resource intensity

═══════════════════════════════════════════════════════════════════════

SETTING UP RCPS ANALYSIS

RESOURCE DEFINITION
1. Define resource types (e.g., "Engineers", "Equipment A")
2. Set resource availability for each type
3. Specify availability by time period if needed
4. Consider resource calendars and non-working time

ACTIVITY RESOURCE REQUIREMENTS
• Each activity specifies required resource types
• Quantity of each resource type needed
• Duration activity needs resources
• Resource requirements must be realistic

SCHEDULING PARAMETERS
• Choose priority rule for conflict resolution
• Set resource availability levels
• Define scheduling horizon
• Select optimization objectives

═══════════════════════════════════════════════════════════════════════

RCPS ALGORITHM PROCESS

SCHEDULING STEPS
1. Start with earliest possible start times (CPM)
2. Identify resource conflicts at each time period
3. Apply priority rule to resolve conflicts
4. Delay conflicted activities to next feasible time
5. Update dependent activity start times
6. Repeat until schedule is resource-feasible

CONFLICT RESOLUTION
• When demand exceeds supply, prioritize activities
• Higher priority activities get resources first
• Lower priority activities delayed until resources available
• May cause project duration extension beyond CPM

═══════════════════════════════════════════════════════════════════════

INTERPRETING RCPS RESULTS

SCHEDULE CHANGES
• Compare RCPS schedule to original CPM schedule
• Identify activities delayed due to resource constraints
• New critical path may emerge (resource-critical)
• Project duration typically increases

RESOURCE UTILIZATION
• Resource usage charts show utilization over time
• Identify periods of resource over/under-utilization
• Spot resource bottlenecks and idle periods
• Plan resource acquisition or reallocation

PERFORMANCE METRICS
• Project duration extension due to resources
• Resource utilization efficiency percentages
• Number of resource conflicts resolved
• Critical resource types causing most delays

═══════════════════════════════════════════════════════════════════════

OPTIMIZATION STRATEGIES

RESOURCE ALLOCATION
• Add resources to bottleneck resource types
• Redistribute resources between activities
• Consider resource substitution possibilities
• Plan resource procurement timing

ACTIVITY MODIFICATION
• Split activities to reduce resource peaks
• Change activity sequences if possible
• Consider overtime or alternative methods
• Outsource resource-intensive activities

SCHEDULE OPTIMIZATION
• Try different priority rules
• Combine multiple scheduling objectives
• Consider multi-project resource sharing
• Plan buffer resources for uncertainty

═══════════════════════════════════════════════════════════════════════

PRACTICAL APPLICATIONS

PROJECT PLANNING
• Realistic schedules considering resource limits
• Resource procurement planning
• Team size and composition decisions
• Equipment rental and purchase timing

RESOURCE MANAGEMENT
• Workforce planning and hiring decisions
• Equipment utilization optimization
• Multi-project resource allocation
• Resource capacity planning

WHAT-IF ANALYSIS
• Test different resource availability scenarios
• Evaluate impact of resource changes
• Compare alternative project approaches
• Assess resource investment decisions

═══════════════════════════════════════════════════════════════════════"""

        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)

        help_window.transient(self.root)

    def show_crashing_tab_help(self):
        """Show Crashing tab specific help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Crashing Tab - Help")
        help_window.geometry("800x600")

        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = """CRASHING TAB - DETAILED HELP
Project Crashing and Time-Cost Optimization (CPM/PERT Based)

═══════════════════════════════════════════════════════════════════════

PURPOSE
The Crashing tab helps you reduce the theoretical project duration by spending additional money on activities that can be accelerated, assuming unlimited resources. This is a CPM/PERT-based analysis and does not consider resource constraints.

NORMAL COST CALCULATION (STEP-BY-STEP)
• For each time step in the project schedule:
    – Identify all activities active during that step (where ES < current_time <= EF)
    – For each active activity, add its normal_cost to the step normal cost
    – Accumulate step normal costs over the entire project duration to get the total normal cost

Example:
    If three activities are active at time t, and their normal costs are 100, 150, and 200, then step normal cost = 450. This is repeated for each time step and summed for the total normal cost.

CRASH COST CALCULATION
• Only critical activities (float = 0) are considered for crashing
• Activities are ranked by cost-effectiveness (cost slope: (Crash Cost - Normal Cost) / (Normal Duration - Crash Duration))
• The algorithm crashes the most cost-effective critical activity in 1-unit increments
• Each crash decision adds to the total crash cost

BUDGET VALIDATION
• Before each crash, the system projects the total cost (normal cost + crash cost)
• Validates against user-defined limits: max_budget, max_crash_cost, max_normal_cost
• Prevents budget overruns by checking before committing to a crash

CRASHING ALGORITHM (CPM-BASED)
1. Start with the theoretical CPM schedule (no resource constraints)
2. Identify critical path activities (float = 0)
3. Calculate cost slopes for all crashable critical activities
4. Crash the activity with the lowest cost slope first
5. Recalculate CPM after each crash
6. Repeat until the target duration is reached or no further crashing is possible

KEY CONCEPTS
• Project Crashing: Shortening project duration by reducing activity durations, trading off time for cost
• Normal vs. Crash Parameters:
    – Normal Duration: Standard time to complete activity
    – Crash Duration: Minimum possible time with maximum resources
    – Normal Cost: Standard cost for normal duration
    – Crash Cost: Total cost when activity is fully crashed
• Cost Slope: Cost per unit time saved; lower slope means more cost-effective to crash

LIMITATIONS
• Results assume unlimited resources
• May not be practically achievable in real projects
• Does not consider resource conflicts or resource availability

WHEN TO USE THE CRASHING TAB
• For theoretical minimum project duration
• When resources are not a constraint
• For quick cost estimates for schedule acceleration
• For feasibility studies and scenario comparisons

PRACTICAL APPLICATIONS
• Theoretical feasibility analysis
• Upper bound estimates for schedule compression
• Cost benchmarking for project proposals
• Comparative analysis between project alternatives

═══════════════════════════════════════════════════════════════════════"""

        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)

        help_window.transient(self.root)

    def show_rcps_crashing_tab_help(self):
        """Show RCPS Crashing tab specific help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("RCPS Crashing Tab - Help")
        help_window.geometry("800x600")

        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        help_text = (
            "RCPS CRASHING TAB - DETAILED HELP\n"
            "Resource-Constrained Project Schedule Crashing\n"
            "\n"
            "================================================================\n"
            "\n"
            "PURPOSE\n"
            "The RCPS Crashing tab helps you reduce project duration while respecting resource constraints, providing realistic and implementable crashing strategies. This approach is designed to be resource-aware and only allows crashing when resources are available.\n"
            "\n"
            "[NOTE] Resource awareness is not fully implemented in the current version. Crashing decisions do not yet validate actual resource availability. Full resource-aware crashing will be available in future development releases.\n"
            "\n"
            "NORMAL COST CALCULATION (STEP-BY-STEP)\n"
            "- For each time step in the RCPS schedule:\n"
            "    * Identify all activities active during that step (where ES < current_time <= EF)\n"
            "    * For each active activity, add its normal_cost to the step normal cost\n"
            "    * Accumulate step normal costs over the entire project duration to get the total normal cost\n"
            "- The calculation uses the actual RCPS schedule, reflecting real resource limitations.\n"
            "\n"
            "CRASH COST CALCULATION\n"
            "- Only activities that are critical (float = 0) and crashable (duration > min_duration) are considered\n")
        text_widget.insert(tk.END, help_text)
        more_help = (
            "- Each potential crash is validated against resource availability at the crash time\n"
            "- Only resource-feasible crashes are applied\n"
            "- Crash cost = crash_cost_per_unit * crash_amount for each valid crash\n"
            "\n"
            "BUDGET AND RESOURCE VALIDATION\n"
            "- Before each crash, the system checks:\n"
            "    * Resource availability at the crash time\n"
            "    * That the crash does not exceed resource capacity\n"
            "    * That the crash does not conflict with other activities\n"
            "    * That the projected total cost does not exceed max_budget\n"
            "\n"
            "RCPS CRASHING ALGORITHM\n"
            "1. Start with the RCPS-constrained network graph\n"
            "2. Identify critical activities (float = 0) in the RCPS schedule\n"
            "3. Filter for crashable activities (duration > min_duration)\n"
            "4. Validate each crash for resource feasibility\n"
            "5. Apply the most cost-effective, resource-feasible crash\n"
            "6. Update the schedule minimally, preserving RCPS timing\n"
            "7. Repeat until the target duration is reached or no further crashing is possible\n"
            "\n"
            "KEY CONCEPTS\n"
            "- Resource constraints: Only crashes that respect resource limits are allowed\n"
            "- Realistic schedule: All results are implementable in practice\n"
            "- Cost calculation: Includes resource acquisition/overtime costs\n"
            "\n"
            "LIMITATIONS\n"
            "- Results are bounded by resource availability\n"
            "- May achieve less time reduction than theoretical CPM crashing\n"
            "- Higher costs may result from resource constraints\n"
            "- Some activities may not be crashable due to lack of resources\n"
            "\n"
            "WHEN TO USE THE RCPS CRASHING TAB\n"
            "- When resources are limited (personnel, equipment, facilities)\n")
        text_widget.insert(tk.END, more_help)
        final_help = (
            "- For realistic, implementable schedule acceleration plans\n"
            "- For final project planning and execution decisions\n"
            "\n"
            "PRACTICAL APPLICATIONS\n"
            "- Direct applicability to project execution\n"
            "- Resource allocation requirements are clearly defined\n"
            "- Timeline considers resource constraint impacts\n"
            "- Crash sequence respects resource availability\n"
            "\n"
            "================================================================\n")
        text_widget.insert(tk.END, final_help)
        text_widget.config(state=tk.DISABLED)
        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)
        help_window.transient(self.root)

    def show_about(self):
        """Show comprehensive about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About PMHelper")
        about_window.geometry("600x500")
        about_window.resizable(False, False)

        # Create scrollable content
        main_frame = ttk.Frame(about_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(
            header_frame, text="PMHelper", font=(
                "Arial", 16, "bold"))
        title_label.pack()

        version_label = ttk.Label(
            header_frame,
            text="Project Management Analysis Tool v1.0.0",
            font=(
                "Arial",
                10))
        version_label.pack()

        # Create scrollable text area
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(
            text_frame, wrap=tk.WORD, font=(
                "Arial", 9), height=20)
        scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        about_text = """OVERVIEW
PMHelper is an educational project management analysis tool designed to help students plan and design projects while learning core project management methodologies.

CORE METHODOLOGIES
• Critical Path Method (CPM) - Deterministic project analysis
• Program Evaluation and Review Technique (PERT) - Probabilistic analysis with uncertainty
• Resource-Constrained Project Scheduling (RCPS) - Scheduling with limited resources
• Project Crashing - Time-cost optimization for schedule acceleration

ANALYSIS FEATURES
✓ Critical path identification and analysis
✓ Activity scheduling with early/late start and finish times
✓ Total float and free float calculations
✓ Network diagram visualization
✓ Gantt chart timeline representation
✓ Probability analysis for PERT projects
✓ Resource utilization optimization
✓ Project crashing and time-cost trade-offs

VISUALIZATION TOOLS
✓ Interactive network diagrams showing dependencies
✓ Professional Gantt charts with critical path highlighting
✓ Probability distribution charts and histograms
✓ Resource utilization graphs
✓ Statistical analysis charts

DATA MANAGEMENT
✓ Manual data entry with validation
✓ CSV import/export
✓ Sample data sets for learning and testing
✓ Data validation and error checking
✓ Comprehensive results export

ADVANCED CAPABILITIES
✓ What-if scenario analysis
✓ Resource leveling and optimization
✓ Schedule compression strategies
✓ Statistical project analysis

FUTURE DEPLOYMENTS
The following features are planned for future releases:
• Monte Carlo simulation for risk analysis
• Cost-time curve analysis
• Excel import/export capabilities
• Multi-project analysis support
• Risk and uncertainty modeling

USER INTERFACE
✓ Modern tabbed interface for easy navigation
✓ Context-sensitive help for each feature
✓ Comprehensive user guide and documentation
✓ Export capabilities for reports and charts
✓ Professional results formatting

TECHNICAL SPECIFICATIONS
• Built with Python and Tkinter for cross-platform compatibility
• Uses advanced algorithms for optimization and analysis
• Supports projects of varying complexity and size
• Integrated mathematical libraries for statistical analysis
• Professional-grade calculations and validations

IDEAL FOR
• Project managers planning and controlling projects
• Engineers analyzing complex project networks
• Students learning project management methodologies
• Consultants performing project analysis and optimization
• Organizations requiring professional project scheduling tools

VERSION HISTORY
v1.0.0 - Complete implementation with all core features
• Full CPM and PERT analysis capabilities
• RCPS and crashing optimization
• Comprehensive visualization tools
• Professional user interface

SUPPORT & DOCUMENTATION
• Comprehensive help system built into application
• Detailed user guides for each feature
• Sample projects for learning
• Export capabilities for documentation

© 2024 PMHelper Development Team
All rights reserved.

PMHelper is designed to meet professional project management analysis needs while remaining accessible for educational use."""

        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)

        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=about_window.destroy)
        close_btn.pack()

        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()

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
        except BaseException:
            print("✗ Fix 1: Error checking automatic chart display")

        # Test Fix 2: Data integration
        try:
            if hasattr(
                    self,
                    'gantt_tab') and hasattr(
                    self.gantt_tab,
                    'update_data'):
                print("✓ Fix 2: Enhanced data integration method exists")
                results['fix2'] = True
            else:
                print("✗ Fix 2: Missing enhanced data integration")
        except BaseException:
            print("✗ Fix 2: Error checking data integration")

        # Test Fix 3: Tab communication
        try:
            if hasattr(self, 'on_tab_selected'):
                print("✓ Fix 3: Tab communication event handler exists")
                results['fix3'] = True
            else:
                print("✗ Fix 3: Missing tab communication handler")
        except BaseException:
            print("✗ Fix 3: Error checking tab communication")

        # Summary
        passed = sum(results.values())
        total = len(results)

        print(
            f"\nIntegration Test Results: {passed}/{total} fixes implemented")

        if passed == total:
            print("[DEBUG_SUCCESS] ALL INTEGRATION FIXES READY FOR TESTING!")
        else:
            print("[DEBUG_ERROR] Some fixes missing - implementation incomplete")

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
            
            # Refresh charter manager when tab is selected
            elif "Charter Manager" in tab_text:
                self.charter_manager.refresh()
        except Exception as e:
            print(f"ERROR: Tab change handler failed: {e}")
            self.set_status("Ready")
    
    def _open_charter_from_manager(self, filepath: str):
        """Open a charter from the manager in the charter tab.
        
        Args:
            filepath: Path to the charter file to open
        """
        try:
            # Switch to charter tab
            for i in range(self.notebook.index("end")):
                if self.notebook.tab(i, "text") == "Project Charter":
                    self.notebook.select(i)
                    break
            
            # Load the charter in the charter tab
            self.charter_tab.load_charter_from_file(filepath)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open charter: {str(e)}")
    
    def on_closing(self):
        """Handle application closing with proper cleanup."""
        try:
            # Cleanup server resources if available
            if SERVER_MODE_AVAILABLE and hasattr(self, 'server_tab') and self.server_tab:
                self.server_tab.cleanup()
                
            # Close the application
            self.root.destroy()
            
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
            self.root.destroy()


def main():
    """Main entry point for the GUI application"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


# Export alias for common import patterns
PMHelperGUI = MainWindow

if __name__ == '__main__':
    main()
