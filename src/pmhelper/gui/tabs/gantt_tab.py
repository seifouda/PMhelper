#!/usr/bin/env python3
"""
Professional Gantt Tab Module

Displays professional project Gantt charts with advanced features:
- Always-on critical path highlighting
- Predecessor arrows showing dependencies
- Professional styling matching cmp_app.py
- Grid options and today line
- Removed float toggles for cleaner interface
"""

from pmhelper.utils.visualizations import GanttChartVisualizer
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class GanttTab:
    """Gantt chart tab for displaying project timeline"""

    def __init__(self, notebook, main_window):
        self.notebook = notebook
        self.main_window = main_window
        self.results_data = None
        self.analysis_mode = None
        self.figure = None
        self.canvas = None

        self.create_tab()

    def create_tab(self):
        """Create the Gantt tab"""
        self.gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gantt_frame, text="Gantt Chart")

        if not MATPLOTLIB_AVAILABLE:
            self.create_no_matplotlib_message()
            return

        # Create control frame
        self.create_control_frame()

        # Create matplotlib figure and canvas
        self.create_plot_area()

    def create_no_matplotlib_message(self):
        """Create message when matplotlib is not available"""
        message_frame = ttk.Frame(self.gantt_frame)
        message_frame.pack(fill=tk.BOTH, expand=True)

        message_label = ttk.Label(
            message_frame,
            text="Gantt charts require matplotlib.\nPlease install matplotlib to view Gantt charts.",
            font=(
                "Arial",
                12),
            justify=tk.CENTER)
        message_label.pack(expand=True)

        install_button = ttk.Button(
            message_frame,
            text="Install matplotlib",
            command=self.install_matplotlib
        )
        install_button.pack(pady=10)

    def install_matplotlib(self):
        """Attempt to install matplotlib"""
        try:
            import subprocess
            import sys

            result = messagebox.askyesno(
                "Install matplotlib",
                "This will install matplotlib using pip. Continue?"
            )

            if result:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "matplotlib"])
                messagebox.showinfo(
                    "Success",
                    "matplotlib installed successfully. Please restart the application.")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to install matplotlib: {
                    str(e)}")

    def create_control_frame(self):
        """Create control buttons and options frame"""
        control_frame = ttk.Frame(self.gantt_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))

        # Chart options - Professional features matching cmp_app.py
        options_frame = ttk.LabelFrame(
            control_frame,
            text="Professional Gantt Chart Options",
            padding="5")
        options_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Professional display options (critical path is always on, float
        # removed)
        self.show_predecessors_var = tk.BooleanVar(value=True)
        self.show_today_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(options_frame, text="Show Predecessor Arrows",
                        variable=self.show_predecessors_var,
                        command=self.update_chart).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Show Today Line",
                        variable=self.show_today_var,
                        command=self.update_chart).pack(side=tk.LEFT, padx=5)

        # Date settings frame
        date_frame = ttk.LabelFrame(
            control_frame, text="Project Dates", padding="5")
        date_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(
            date_frame,
            text="Start Date:").pack(
            side=tk.LEFT,
            padx=(
                0,
                5))
        self.start_date_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d"))
        start_date_entry = ttk.Entry(
            date_frame, textvariable=self.start_date_var, width=12)
        start_date_entry.pack(side=tk.LEFT, padx=(0, 10))
        start_date_entry.bind('<Return>', lambda e: self.update_chart())

        ttk.Button(date_frame, text="Update",
                   command=self.update_chart).pack(side=tk.LEFT, padx=5)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(button_frame, text="Save Chart",
                   command=self.save_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame,
            text="Export Data",
            command=self.export_schedule_data).pack(
            side=tk.LEFT,
            padx=5)
        ttk.Button(
            button_frame,
            text="? Help",
            command=self.main_window.show_gantt_tab_help).pack(
            side=tk.LEFT,
            padx=5)

    def create_plot_area(self):
        """Create matplotlib plot area WITHOUT navigation toolbar - FIXED"""
        try:
            # Create matplotlib figure with proper error handling
            self.figure = Figure(figsize=(14, 8), dpi=100)
            self.figure.patch.set_facecolor('white')

            # Create canvas frame
            canvas_frame = ttk.Frame(self.gantt_frame)
            canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Create and configure canvas
            self.canvas = FigureCanvasTkAgg(self.figure, canvas_frame)
            self.canvas.draw()

            # Pack canvas widget properly
            canvas_widget = self.canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)

            # REMOVED: Navigation toolbar (this was causing issues)
            # No toolbar creation - cleaner interface

            # Initialize with empty plot and verify it works
            self.create_empty_plot()

            print("DEBUG: Canvas created successfully without toolbar")

        except Exception as e:
            print(f"ERROR: Failed to create plot area: {e}")
            import traceback
            traceback.print_exc()

            # Create error display
            error_frame = ttk.Frame(self.gantt_frame)
            error_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            error_label = ttk.Label(
                error_frame, text=f"Chart display error: {e}")
            error_label.pack(expand=True)

    def create_empty_plot(self):
        """Create empty plot when no data available - FIXED"""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            ax.text(
                0.5,
                0.5,
                'No Project Data Available\n\nRun analysis to generate Gantt chart',
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                fontsize=14,
                color='gray')

            ax.set_title(
                'Gantt Chart - No Data',
                fontsize=16,
                fontweight='bold')
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 5)
            ax.axis('off')

            self.canvas.draw()
            print("DEBUG: Empty plot created successfully")

        except Exception as e:
            print(f"ERROR: Failed to create empty plot: {e}")
        self.canvas.draw()

    # def update_gantt(self, results_data, analysis_mode):
    #     """Update the Gantt chart with new data"""
    #     self.results_data = results_data
    #     self.analysis_mode = analysis_mode

    #     if not MATPLOTLIB_AVAILABLE:
    #         return

    #     if not results_data:
    #         self.create_empty_plot()
    #         return

    #     self.update_chart()

    def update_data(self, results_data, analysis_mode):
        """CRITICAL FIX 2: Enhanced data integration with comprehensive validation"""
        try:
            print("DEBUG: Gantt tab receiving analysis results...")
            print(f"DEBUG: Analysis mode: {analysis_mode}")

            # ENHANCED: Comprehensive data validation
            if not results_data:
                print("ERROR: No results data provided to Gantt tab")
                self.create_empty_plot()
                return False

            # Validate required data structure
            required_keys = ['graph']
            for key in required_keys:
                if key not in results_data:
                    print(f"ERROR: Missing required data key: {key}")
                    self.create_error_chart(
                        f"Invalid data format: missing {key}")
                    return False

            G = results_data.get('graph')
            critical_activities = results_data.get('critical_activities', [])

            print(
                f"DEBUG: Received graph with {
                    len(
                        G.nodes()) if G else 0} nodes, {
                    len(critical_activities)} critical")

            # ENHANCED: Validate graph data structure
            if not G or not G.nodes():
                print("WARNING: No graph nodes in results data")
                self.create_empty_plot()
                return False

            # Validate each node has required fields
            required_node_fields = ['duration']
            for node in G.nodes():
                if node not in ['START', 'END']:
                    node_data = G.nodes[node]
                    for field in required_node_fields:
                        if field not in node_data:
                            print(
                                f"ERROR: Node {node} missing required field: {field}")
                            self.create_error_chart(
                                f"Invalid node data: missing {field}")
                            return False

            # Store validated data
            self.results_data = results_data
            self.analysis_mode = analysis_mode

            print("DEBUG: Data validation passed, triggering chart generation...")

            # CRITICAL: Automatically generate chart when valid data is
            # received
            success = self.update_chart()

            if success:
                print("DEBUG: Gantt tab data integration completed successfully")
                return True
            else:
                print("ERROR: Chart generation failed after data integration")
                return False

        except Exception as e:
            error_msg = f"Gantt tab data integration failed: {e}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()

            # Show error in chart area
            self.create_error_chart(error_msg)
            return False

    def update_gantt(self, results_data, analysis_mode):
        """Update the gantt chart with new results data using professional features"""
        try:
            print(
                f"DEBUG: Updating professional Gantt chart with mode: {analysis_mode}")

            if not results_data:
                print("DEBUG: No results data for professional Gantt chart")
                self.create_empty_chart()
                return

            # Extract data from results - get the NetworkX graph for
            # professional chart
            G = results_data.get('graph')
            critical_activities = results_data.get('critical_activities', [])
            project_duration = results_data.get('project_duration', None)

            print(f"DEBUG: Professional Gantt data:")
            print(f"  Graph nodes: {len(G.nodes()) if G else 0}")
            print(f"  Critical activities: {critical_activities}")
            print(f"  Project duration: {project_duration}")

            if not G:
                print("DEBUG: No graph data for professional Gantt chart")
                self.create_empty_chart()
                return

            # Call the professional update chart method
            self.update_chart(G, critical_activities, project_duration)

        except Exception as e:
            print(f"Failed to update professional gantt chart: {e}")
            import traceback
            traceback.print_exc()
            self.create_error_chart(str(e))

    def setup_ui(self):
        """Setup the gantt tab UI"""
        # Create a frame for controls
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', padx=10, pady=5)

        # Add refresh button
        refresh_btn = ttk.Button(control_frame, text="Refresh Gantt Chart",
                                 command=self.refresh_gantt)
        refresh_btn.pack(side='left', padx=5)

        # Create matplotlib figure
        self.figure = plt.figure(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, self.gantt_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Initial empty chart
        self.create_empty_chart()

    def create_empty_chart(self):
        """Create an empty gantt chart"""
        try:
            # Clean up previous chart
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.get_tk_widget().destroy()

            if hasattr(self, 'figure'):
                plt.close(self.figure)

            # Create new figure
            self.figure = plt.figure(figsize=(12, 8))
            ax = self.figure.add_subplot(111)

            ax.text(
                0.5,
                0.5,
                'No Gantt chart data available\nRun analysis to generate chart',
                ha='center',
                va='center',
                fontsize=12,
                transform=ax.transAxes)
            ax.set_title('Gantt Chart - No Data', fontsize=14)
            ax.axis('off')

            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.figure, self.gantt_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            print(f"Error creating empty chart: {e}")

    def create_error_chart(self, error_message):
        """Create an error message chart"""
        try:
            # Clean up previous chart
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.get_tk_widget().destroy()

            if hasattr(self, 'figure'):
                plt.close(self.figure)

            # Create new figure
            self.figure = plt.figure(figsize=(12, 8))
            ax = self.figure.add_subplot(111)

            ax.text(0.5, 0.5, f'Error creating Gantt chart:\n{error_message}',
                    ha='center', va='center', fontsize=12, color='red',
                    transform=ax.transAxes)
            ax.set_title('Gantt Chart Error', fontsize=14)
            ax.axis('off')

            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.figure, self.gantt_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            print(f"Error creating error chart: {e}")

    def refresh_gantt(self):
        """Refresh the professional gantt chart with current data"""
        try:
            # Get current results from main window
            if hasattr(self.main_window, 'last_analysis_results'):
                self.update_gantt(self.main_window.last_analysis_results,
                                  self.main_window.analysis_mode)
            else:
                # Try to refresh with stored data
                self.update_chart()
        except Exception as e:
            print(f"Error refreshing professional gantt: {e}")
            self.create_empty_chart()

    def create_error_chart(self, error_message):
        """Create error display in chart area"""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            ax.text(0.5, 0.5, f'Chart Error\n\n{error_message}',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='red')

            ax.set_title('Gantt Chart - Error', fontsize=14, color='red')
            ax.axis('off')

            self.canvas.draw()

        except Exception as e:
            print(f"ERROR: Failed to create error chart: {e}")

    def clear_chart(self):
        """Clear the current gantt chart"""
        try:
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

            if hasattr(self, 'figure'):
                plt.close(self.figure)
                self.figure = None

            self.create_empty_chart()

        except Exception as e:
            print(f"Error clearing chart: {e}")

    def update_chart(
            self,
            G=None,
            critical_activities=None,
            project_duration=None):
        """CRITICAL FIX 2: Enhanced chart update with better error handling"""
        try:
            print("DEBUG: Gantt chart update triggered")

            # Verify data availability
            if not hasattr(self, 'results_data') or not self.results_data:
                if G is None:
                    print("DEBUG: No results data available - showing empty chart")
                    self.create_empty_plot()
                    return False

            # Use provided parameters or fall back to stored data
            if G is None and self.results_data:
                G = self.results_data.get('graph')
            if critical_activities is None and self.results_data:
                critical_activities = self.results_data.get(
                    'critical_activities', [])
            if project_duration is None and self.results_data:
                project_duration = self.results_data.get('project_duration')

            # Store the data for future updates
            if G is not None:
                self.last_graph = G
            if critical_activities is not None:
                self.last_critical_activities = critical_activities
            if project_duration is not None:
                self.last_project_duration = project_duration

            print(f"DEBUG: Processing chart update with:")
            print(f"  Graph nodes: {len(G.nodes()) if G else 0}")
            print(
                f"  Critical activities: {
                    len(critical_activities) if critical_activities else 0}")
            print(f"  Project duration: {project_duration}")

            if not G:
                print("DEBUG: No graph data - showing empty chart")
                self.create_empty_plot()
                return False

            # ENHANCED: Build graph with better error handling
            if G and G.number_of_nodes() > 0:
                print("DEBUG: Graph built successfully, generating professional chart")
                success = self.generate_professional_gantt_chart(
                    G, critical_activities or [])

                if success:
                    print("DEBUG: Professional Gantt chart generated successfully")
                    return True
                else:
                    print("ERROR: Chart generation failed")
                    self.create_error_chart("Chart generation failed")
                    return False
            else:
                print("ERROR: Failed to build graph from activities")
                self.create_error_chart(
                    "Failed to build project network graph")
                return False

        except Exception as e:
            error_msg = f"Chart generation failed: {e}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            self.create_error_chart(error_msg)
            return False

    def build_activities_from_graph(self, G):
        """Build activities list from NetworkX graph data"""
        try:
            import networkx as nx

            activities = []

            # Add nodes for each activity
            for node in G.nodes():
                if node not in ['START', 'END']:  # Skip dummy nodes
                    node_data = G.nodes[node]
                    activities.append({
                        'id': node,
                        'name': node_data.get('activity', node),
                        'duration': node_data.get('duration', 0),
                        'earliest_start': node_data.get('earliest_start', 0),
                        'earliest_finish': node_data.get('earliest_finish', 0),
                        'latest_start': node_data.get('latest_start', 0),
                        'latest_finish': node_data.get('latest_finish', 0),
                        'total_float': node_data.get('total_float', 0),
                        'predecessors': list(G.predecessors(node))
                    })

            print(f"DEBUG: Built {len(activities)} activities from graph")
            return activities

        except Exception as e:
            print(f"ERROR: Activity building failed: {e}")
            return []

    def generate_professional_gantt_chart(self, G, critical_activities):
        """Enhanced professional chart generation with success tracking"""
        try:
            print("DEBUG: Starting professional chart generation")

            # Clear any existing plot
            self.figure.clear()

            # Create new axes
            ax = self.figure.add_subplot(111)

            # --- CRITICAL: Map CPM/PERT fields to verbose names for Gantt chart ---
            for node in G.nodes():
                node_data = G.nodes[node]
                # Only map if CPM/PERT fields exist
                if 'ES' in node_data:
                    node_data['earliest_start'] = node_data['ES']
                if 'EF' in node_data:
                    node_data['earliest_finish'] = node_data['EF']
                if 'LS' in node_data:
                    node_data['latest_start'] = node_data['LS']
                if 'LF' in node_data:
                    node_data['latest_finish'] = node_data['LF']

            # Extract and validate activities from graph
            activities = []
            for node in G.nodes():
                if node not in ['START', 'END']:
                    node_data = G.nodes[node]
                    activity = {
                        'id': node,
                        'activity': node_data.get('activity', node),
                        # Ensure name field
                        'name': node_data.get('activity', node),
                        'duration': node_data.get('duration', 0),
                        'earliest_start': node_data.get('earliest_start', 0),
                        'earliest_finish': node_data.get('earliest_finish', 0),
                        'latest_start': node_data.get('latest_start', 0),
                        'latest_finish': node_data.get('latest_finish', 0),
                        'critical': node in critical_activities
                    }
                    activities.append(activity)

            print(activities)

            if not activities:
                print("DEBUG: No valid activities to display")
                self.create_empty_plot()
                return False

            # Sort activities by earliest_start, then by ID (to match CPM
            # Gantt)
            activities.sort(key=lambda x: (x['earliest_start'], x['id']))

            print(f"DEBUG: Generating bars for {len(activities)} activities")

            # --- VISUAL ADJUSTMENT FOR Y-AXIS AND TIME LABELS ---
            import numpy as np
            y_pos = np.arange(len(activities))[::-1]
            activity_labels = []
            critical_color = 'red'
            normal_color = 'lightblue'
            slack_color = 'lightgrey'
            for i, activity in enumerate(activities):
                activity_id = activity['id']
                early_start = activity['earliest_start']
                early_finish = activity['earliest_finish']
                latest_finish = activity['latest_finish']
                duration = activity['duration']
                float_time = max(0, latest_finish - early_finish)
                is_critical = activity['critical']
                bar_color = critical_color if is_critical else normal_color
                # Main activity bar: from ES to EF (width=duration, left=ES)
                ax.barh(y_pos[i], duration, left=early_start,
                        color=bar_color, alpha=0.7, height=0.6,
                        edgecolor='black', linewidth=0.8)
                # Slack bar: from EF to LF (for non-critical, width=LF-EF,
                # left=EF)
                if not is_critical and float_time > 0:
                    ax.barh(y_pos[i], float_time, left=early_finish,
                            color=slack_color, alpha=0.5, height=0.6,
                            edgecolor='gray', linewidth=0.5, linestyle='--')
                # Activity ID centered on bar
                bar_center_x = early_start + duration / 2
                ax.text(
                    bar_center_x,
                    y_pos[i],
                    activity_id,
                    ha='center',
                    va='center',
                    fontweight='bold',
                    fontsize=10)
                activity_labels.append(activity_id)

            # Draw predecessor arrows if enabled (preserve existing)
            if hasattr(
                    self,
                    'show_predecessors_var') and self.show_predecessors_var.get():
                self.draw_predecessor_arrows(G, activities, y_pos, ax)
            # --- Professional chart customization ---
            ax.set_yticks(y_pos)
            ax.set_yticklabels(activity_labels, fontsize=12, fontweight='bold')
            ax.set_xlabel(
                'Time Units',
                fontsize=12,
                fontweight='bold',
                color='darkgreen')
            ax.set_ylabel(
                'Activities',
                fontsize=12,
                fontweight='bold',
                color='darkgreen')
            # Title styling
            ax.set_title(
                'Project Gantt Chart',
                fontsize=14,
                fontweight='bold',
                pad=20)
            # Professional grid (controlled by Show Grid Lines checkbox)
            show_grid = self.show_grid_var.get() if hasattr(self, 'show_grid_var') else True
            ax.grid(show_grid, axis='x', alpha=0.3)
            # Add today line if enabled
            project_duration = max([a['latest_finish']
                                   for a in activities]) if activities else 0
            if hasattr(self, 'show_today_var') and self.show_today_var.get():
                # Parse project start date from UI
                try:
                    project_start = datetime.strptime(
                        self.start_date_var.get(), "%Y-%m-%d")
                except Exception:
                    project_start = datetime.now()
                # Calculate days from project start to today
                today = datetime.now()
                today_position = (today - project_start).days
                # Clamp to chart range
                if today_position < 0:
                    today_position = 0
                if activities:
                    max_time = max([a['latest_finish'] for a in activities])
                    if today_position > max_time:
                        today_position = max_time
                ax.axvline(
                    x=today_position,
                    color='green',
                    linestyle='-',
                    linewidth=2,
                    alpha=0.8,
                    label='Today')
            # Legend styling
            import matplotlib.patches as mpatches
            legend_elements = [
                mpatches.Patch(
                    color='red',
                    alpha=0.7,
                    label='Critical Activities'),
                mpatches.Patch(
                    color='lightblue',
                    alpha=0.7,
                    label='Non-Critical Activities'),
                mpatches.Patch(
                    color='lightgrey',
                    alpha=0.5,
                    label='Available Slack/Float')]
            if hasattr(self, 'show_today_var') and self.show_today_var.get():
                import matplotlib.lines as mlines
                legend_elements.append(
                    mlines.Line2D(
                        [0],
                        [0],
                        color='green',
                        linewidth=2,
                        label='Today'))
            ax.legend(handles=legend_elements, loc='lower left')
            # Set proper limits
            if activities:
                # Use latest_finish for x-axis end, matching CPM
                max_time = max([a['latest_finish'] for a in activities])
                ax.set_xlim(-0.5, max_time + 0.5)
                ax.set_ylim(-0.5, len(activities) - 0.5)

            # CRITICAL: Refresh canvas
            self.canvas.draw()
            self.canvas.flush_events()

            print("DEBUG: Professional Gantt chart generated and displayed successfully")
            return True

        except Exception as e:
            print(f"ERROR: Professional chart generation failed: {e}")
            import traceback
            traceback.print_exc()
            self.create_error_chart(f"Chart generation failed: {e}")
            return False

    def draw_predecessor_arrows(self, G, activities, y_positions, ax):
        """Draw predecessor arrows between activities"""
        try:
            # Map activity IDs to their Y positions
            activity_y_map = {}
            activity_x_map = {}

            for i, activity in enumerate(activities):
                activity_y_map[activity['id']] = y_positions[i]
                activity_x_map[activity['id']] = activity['earliest_finish']

            # Draw arrows for each dependency
            for activity in activities:
                activity_id = activity['id']
                predecessors = list(G.predecessors(activity_id))

                for pred_id in predecessors:
                    if pred_id in activity_y_map and pred_id in activity_x_map:
                        from_x = activity_x_map[pred_id]
                        from_y = activity_y_map[pred_id]
                        to_x = activity['earliest_start']
                        to_y = activity_y_map[activity_id]

                        # Draw curved arrow
                        if abs(
                                to_x -
                                from_x) > 0.1 or abs(
                                to_y -
                                from_y) > 0.1:
                            ax.annotate('',
                                        xy=(to_x - 0.1,
                                            to_y),
                                        xytext=(from_x + 0.1,
                                                from_y),
                                        arrowprops=dict(arrowstyle='->',
                                                        color='#2F4F4F',
                                                        lw=2,
                                                        alpha=0.7,
                                                        connectionstyle="arc3,rad=0.1"))

        except Exception as e:
            print(f"ERROR: Failed to draw predecessor arrows: {e}")

    # def update_chart(self):
    #     """Update the Gantt chart"""
    #     if not MATPLOTLIB_AVAILABLE or not self.results_data:
    #         return

    #     try:
    #         # Parse start date
    #         try:
    #             project_start = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
    #         except ValueError:
    #             project_start = datetime.now()
    #             self.start_date_var.set(project_start.strftime("%Y-%m-%d"))

    #         # Clear the figure
    #         self.figure.clear()
    #         ax = self.figure.add_subplot(111)

    #         # Create Gantt chart
    #         visualizer = GanttChartVisualizer()

    #         # Prepare options
    #         options = {
    #             'show_critical_path': self.show_critical_var.get(),
    #             'show_float': self.show_float_var.get(),
    #             'show_grid': self.show_grid_var.get(),
    #             'show_today': self.show_today_var.get(),
    #             'project_start_date': project_start,
    #             'analysis_mode': self.analysis_mode
    #         }

    #         # Create the chart
    #         visualizer.create_gantt_chart(
    #             activities=self.results_data.get('activities', []),
    #             critical_path=self.results_data.get('critical_path', []),
    #             ax=ax,
    #             options=options
    #         )

    #         # Set title
    #         project_duration = self.results_data.get('project_duration', 'Unknown')
    #         if self.analysis_mode == 'probabilistic':
    #             expected_duration = self.results_data.get('expected_duration', 'Unknown')
    #             title = f"Project Gantt Chart\nProject Duration: {project_duration} days, Expected: {expected_duration} days"
    #         else:
    #             title = f"Project Gantt Chart\nProject Duration: {project_duration} days"

    #         ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    #         # Format x-axis for dates
    #         if hasattr(ax, 'xaxis'):
    #             ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #             ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    #             plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    #         # Adjust layout
    #         self.figure.tight_layout()

    #         # Draw the canvas
    #         self.canvas.draw()

    #     except Exception as e:
    #         # Show error in the plot
    #         self.figure.clear()
    #         ax = self.figure.add_subplot(111)
    #         ax.text(0.5, 0.5, f'Error creating Gantt chart:\n{str(e)}',
    #                 horizontalalignment='center', verticalalignment='center',
    #                 transform=ax.transAxes, fontsize=12, color='red')
    #         ax.set_xlim(0, 1)
    #         ax.set_ylim(0, 1)
    #         ax.axis('off')
    #         self.canvas.draw()

    #         # Also show error message
    #         messagebox.showerror("Error", f"Failed to create Gantt chart: {str(e)}")

    def save_chart(self):
        """Save the current chart to file"""
        if not MATPLOTLIB_AVAILABLE or not self.results_data:
            messagebox.showwarning(
                "Warning", "No chart to save. Please run analysis first.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Gantt Chart",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("JPG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )

        if filename:
            try:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight',
                                    facecolor='white', edgecolor='none')
                messagebox.showinfo("Success", f"Chart saved to {filename}")
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to save chart: {
                        str(e)}")

    def export_schedule_data(self):
        """Export schedule data to file"""
        if not self.results_data:
            messagebox.showwarning(
                "Warning", "No schedule data to export. Please run analysis first.")
            return

        filename = filedialog.asksaveasfilename(
            title="Export Schedule Data",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )

        if filename:
            try:
                if filename.lower().endswith('.xlsx'):
                    self._export_excel(filename)
                else:
                    self._export_csv(filename)

                messagebox.showinfo(
                    "Success", f"Schedule data exported to {filename}")
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to export schedule data: {
                        str(e)}")

    def _export_csv(self, filename):
        """Export schedule data as CSV, extracting from the graph for up-to-date values"""
        import pandas as pd
        # Parse start date
        try:
            project_start = datetime.strptime(
                self.start_date_var.get(), "%Y-%m-%d")
        except ValueError:
            project_start = datetime.now()

        # Extract activities from the graph
        G = self.results_data.get('graph')
        critical_activities = set(
            self.results_data.get(
                'critical_activities', []))
        data = []
        if G is not None:
            for node in G.nodes():
                if node in ['START', 'END']:
                    continue
                node_data = G.nodes[node]
                es = node_data.get('earliest_start', 0)
                ef = node_data.get('earliest_finish', 0)
                ls = node_data.get('latest_start', 0)
                lf = node_data.get('latest_finish', 0)
                tf = node_data.get('float', 0)
                duration = node_data.get(
                    'expected_duration', node_data.get(
                        'duration', 0))
                start_date = project_start + \
                    timedelta(days=es) if es else project_start
                finish_date = project_start + \
                    timedelta(days=ef) if ef else project_start
                preds = list(G.predecessors(node))
                preds_str = ', '.join(str(p) for p in preds)
                row = {
                    "Activity_ID": node,
                    "Activity_Name": node_data.get(
                        'activity',
                        node),
                    "Duration": f"{
                        duration:.2f}" if self.analysis_mode == 'probabilistic' else str(duration),
                    "Start_Date": start_date.strftime('%Y-%m-%d'),
                    "Finish_Date": finish_date.strftime('%Y-%m-%d'),
                    "Earliest_Start": es,
                    "Earliest_Finish": ef,
                    "Latest_Start": ls,
                    "Latest_Finish": lf,
                    "Total_Float": f"{
                        tf:.2f}",
                    "Critical": "Yes" if node in critical_activities else "No",
                    "Predecessors": preds_str}
                data.append(row)
        df = pd.DataFrame(data)
        print("\n[DEBUG] Exporting Gantt DataFrame:")
        print(df.info())
        print(df.head())
        df.to_csv(filename, index=False)
        print(df.head())
        df.to_csv(filename, index=False)

    def _export_excel(self, filename):
        """Export schedule data as Excel, extracting from the graph for up-to-date values"""
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror(
                "Error", "pandas is required for Excel export. Please install pandas.")
            return
        # Parse start date
        try:
            project_start = datetime.strptime(
                self.start_date_var.get(), "%Y-%m-%d")
        except ValueError:
            project_start = datetime.now()

        # Extract activities from the graph
        G = self.results_data.get('graph')
        critical_activities = set(
            self.results_data.get(
                'critical_activities', []))
        data = []
        if G is not None:
            for node in G.nodes():
                if node in ['START', 'END']:
                    continue
                node_data = G.nodes[node]
                es = node_data.get('earliest_start', 0)
                ef = node_data.get('earliest_finish', 0)
                ls = node_data.get('latest_start', 0)
                lf = node_data.get('latest_finish', 0)
                tf = node_data.get('float', 0)
                duration = node_data.get(
                    'expected_duration', node_data.get(
                        'duration', 0))
                start_date = project_start + \
                    timedelta(days=es) if es else project_start
                finish_date = project_start + \
                    timedelta(days=ef) if ef else project_start
                preds = list(G.predecessors(node))
                preds_str = ', '.join(str(p) for p in preds)
                row = {
                    'Activity_ID': node,
                    'Activity_Name': node_data.get(
                        'activity',
                        node),
                    'Duration': f"{
                        duration:.2f}" if self.analysis_mode == 'probabilistic' else str(duration),
                    'Start_Date': start_date.strftime('%Y-%m-%d'),
                    'Finish_Date': finish_date.strftime('%Y-%m-%d'),
                    'Earliest_Start': es,
                    'Earliest_Finish': ef,
                    'Latest_Start': ls,
                    'Latest_Finish': lf,
                    'Total_Float': f"{
                        tf:.2f}",
                    'Critical': "Yes" if node in critical_activities else "No",
                    'Predecessors': preds_str}
                data.append(row)
        df = pd.DataFrame(data)
        print("\n[DEBUG] Exporting Gantt DataFrame:")
        print(df.info())
        print(df.head())
        df.to_excel(filename, index=False, sheet_name='Project_Schedule')

    # def clear_chart(self):
    #     """Clear the Gantt chart"""
    #     if not MATPLOTLIB_AVAILABLE:
    #         return

    #     self.results_data = None
    #     self.analysis_mode = None
    #     self.create_empty_plot()
