#!/usr/bin/env python3
"""
PERT Diagram Tab Module

Displays professional PERT network diagrams with rectangle-semicircle nodes,
showing ID, Duration, ES, EF, LS, LF in 6 sections, with critical path highlighting.
"""

from pmhelper.utils.interactive_network import open_interactive_network, PYVIS_AVAILABLE
from pmhelper.gui.widgets.scrollable_mpl_frame import ScrollableMatplotlibFrame
from pmhelper.utils.network_layout import sugiyama_layout, cleanup_virtual_nodes
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
    NETWORKX_AVAILABLE = True
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    NETWORKX_AVAILABLE = False


# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame, WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import plotly_pert_network, PLOTLY_AVAILABLE as _PLT_AVAIL
    _PLOTLY_EMBED = WEBVIEW2_AVAILABLE and _PLT_AVAIL
except ImportError:
    _PLOTLY_EMBED = False


class PertDiagramTab:
    """PERT Diagram tab with professional rectangle-semicircle node visualization"""

    def __init__(self, notebook, main_window):
        self.notebook = notebook
        self.main_window = main_window
        self.results_data = None
        self.analysis_mode = None
        self.figure = None
        self.canvas = None
        self.ax = None

        # Current data storage
        self.current_graph = None
        self.current_critical_activities = []

        self.create_tab()

    def create_tab(self):
        """Create the PERT diagram tab"""
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="PERT Diagram")

        if not MATPLOTLIB_AVAILABLE:
            self.create_no_matplotlib_message()
            return

        # Create control frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Create plot area and pass control_frame
        self.create_plot_area(control_frame)

    def create_plot_area(self, control_frame):
        """Create matplotlib plot area with scrollable viewport and control widgets"""
        # --- Renderer toggle ---
        if _PLOTLY_EMBED:
            self._render_mode_var = tk.StringVar(value="matplotlib")

        self._mpl_frame = ttk.Frame(self.main_frame)
        self._mpl_frame.pack(fill=tk.BOTH, expand=True)

        self._scroll_frame = ScrollableMatplotlibFrame(
            self._mpl_frame, figsize=(14, 10), dpi=100, toolbar=True)
        self._scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.figure = self._scroll_frame.figure
        self.canvas = self._scroll_frame.canvas
        self.toolbar = self._scroll_frame.toolbar

        # Plotly frame (hidden)
        if _PLOTLY_EMBED:
            self._plotly_frame = PlotlyChartFrame(self.main_frame)

        # Initialize with empty plot
        self.create_empty_plot()

        # Display option variables
        self.highlight_critical = tk.BooleanVar(value=True)
        self.show_float = tk.BooleanVar(value=False)

        # Create display options frame
        options_frame = ttk.LabelFrame(
            control_frame, text="Display Options", padding="5")
        options_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Checkboxes for display options
        ttk.Checkbutton(options_frame, text="Highlight Critical Path",
                        variable=self.highlight_critical,
                        command=self.update_diagram).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Show Float Values",
                        variable=self.show_float,
                        command=self.update_diagram).pack(side=tk.LEFT, padx=5)

        if _PLOTLY_EMBED:
            ttk.Separator(
                options_frame,
                orient='vertical').pack(
                side='left',
                fill='y',
                padx=8)
            ttk.Radiobutton(
                options_frame,
                text="Classic",
                variable=self._render_mode_var,
                value="matplotlib",
                command=self._switch_renderer).pack(
                side='left',
                padx=2)
            ttk.Radiobutton(
                options_frame,
                text="\U0001f4ca Plotly",
                variable=self._render_mode_var,
                value="plotly",
                command=self._switch_renderer).pack(
                side='left',
                padx=2)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(button_frame, text="Save Image",
                   command=self.save_diagram).pack(side=tk.LEFT, padx=5)
        if PYVIS_AVAILABLE:
            ttk.Button(
                button_frame,
                text="\U0001f310 Interactive View",
                command=self._open_interactive_view).pack(
                side=tk.LEFT,
                padx=5)
        # Help button
        ttk.Button(
            button_frame,
            text="? Help",
            command=self.show_pert_tab_help).pack(
            side=tk.LEFT,
            padx=5)

    def show_pert_tab_help(self):
        """Show PERT Diagram Tab specific help dialog"""
        help_window = tk.Toplevel(self.main_window.root)
        help_window.title("PERT Diagram Tab - Help")
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
            "PERT DIAGRAM TAB - DETAILED HELP\n"
            "================================================================\n"
            "\n"
            "PURPOSE\n"
            "The PERT Diagram tab displays a professional network diagram with rectangle-semicircle nodes,\n"
            "showing detailed activity information and highlighting the critical path.\n"
            "\n"
            "DIAGRAM ELEMENTS\n"
            "\n"
            "NODES (ACTIVITIES)\n"
            "• Rectangle-semicircle shaped nodes represent project activities\n"
            "• Each node shows 6 sections with key information:\n"
            "  - Activity ID (top left)\n"
            "  - Duration (top right)\n"
            "  - Earliest Start - ES (middle left)\n"
            "  - Earliest Finish - EF (middle right)\n"
            "  - Latest Start - LS (bottom left)\n"
            "  - Latest Finish - LF (bottom right)\n"
            "\n"
            "COLOR CODING\n"
            "• Red nodes: Critical activities (zero float)\n"
            "• Blue nodes: Non-critical activities (positive float)\n"
            "\n"
            "ARROWS (DEPENDENCIES)\n"
            "• Lines connect predecessor to successor activities\n"
            "• Arrow direction shows dependency flow\n"
            "• Critical path arrows are highlighted\n"
            "\n"
            "HOW TO USE\n"
            "1. Run CPM or PERT analysis to generate the diagram\n"
            "2. Use 'Highlight Critical Path' checkbox to toggle critical path display\n"
            "3. Use 'Show Float Values' checkbox to display float information\n"
            "4. Save the diagram as an image using the 'Save Image' button\n"
            "5. Use navigation toolbar to zoom and pan the diagram\n"
            "\n"
            "READING THE DIAGRAM\n"
            "• Follow the critical path (red nodes) from start to finish\n"
            "• Critical activities determine the minimum project duration\n"
            "• Non-critical activities have scheduling flexibility\n"
            "• Use ES/LS and EF/LF times to plan activity schedules\n"
            "\n"
            "FUTURE DEPLOYMENTS\n"
            "The following features are planned for future releases:\n"
            "• Interactive node editing\n"
            "• Advanced layout algorithms\n"
            "• Custom node styling options\n"
            "• Export to various image formats\n"
            "\n"
            "================================================================\n")
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy)
        close_btn.pack(pady=10)
        help_window.transient(self.main_window.root)

    # Removed duplicate create_plot_area method

    def create_empty_plot(self):
        """Create empty plot with instruction message"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.text(0.5, 0.5, 'Run project analysis to display PERT diagram',
                     horizontalalignment='center', verticalalignment='center',
                     transform=self.ax.transAxes, fontsize=14, color='gray')
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
        self.canvas.draw()

    def update_network(self, results_data, analysis_mode):
        """Update the PERT diagram with new data - COPIED FROM NetworkTab"""
        self.results_data = results_data
        self.analysis_mode = analysis_mode

        if not MATPLOTLIB_AVAILABLE:
            return

        if not results_data:
            self.create_empty_plot()
            return

        self.update_diagram()

    def update_diagram(self):
        """Update the PERT diagram with professional critical path visualization"""
        if not MATPLOTLIB_AVAILABLE or not NETWORKX_AVAILABLE or not self.results_data:
            return

        # Plotly path
        if _PLOTLY_EMBED and self._render_mode_var.get() == "plotly":
            self._update_plotly_pert()
            return

        try:
            # Clear the figure completely
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)

            # Extract activities and critical activities from results_data
            activities = self.results_data.get('activities', [])
            critical_activities = self.results_data.get(
                'critical_activities', [])

            if activities:
                # Build NetworkX graph from activities
                G = self.build_graph_from_activities(activities)

                # Store current data
                self.current_graph = G
                self.current_critical_activities = critical_activities

                # Draw the professional PERT network diagram
                self.draw_pert_network_diagram(G, critical_activities)
            else:
                # No activities data available
                self.ax.text(
                    0.5,
                    0.5,
                    'No network data available',
                    ha='center',
                    va='center',
                    transform=self.ax.transAxes,
                    fontsize=12)
                self.ax.axis('off')

            # Set title
            project_duration = self.results_data.get(
                'project_duration', 'Unknown')
            if self.analysis_mode == 'probabilistic':
                expected_duration = self.results_data.get(
                    'expected_duration', 'Unknown')
                if isinstance(expected_duration, (int, float)):
                    expected_duration = f"{expected_duration:.1f}"
                title = f"PERT Network Diagram\nScheduling Duration: {project_duration}, Expected Duration: {expected_duration}"
            else:
                title = f"PERT Network Diagram\nProject Duration: {project_duration}"

            self.ax.set_title(title, fontsize=14, fontweight='bold', pad=5)

            # Final draw (draw_pert_network_diagram sets layout; title added
            # above)
            self.canvas.draw()

        except Exception as e:
            # Show error in the plot
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self.ax.text(0.5, 0.5, f'Error creating PERT diagram:\\n{str(e)}',
                         ha='center', va='center', transform=self.ax.transAxes,
                         fontsize=12, color='red')
            self.ax.axis('off')
            self.canvas.draw()

            # Also print error for debugging
            print(f"Failed to create PERT diagram: {str(e)}")

    def build_graph_from_activities(self, activities):
        """Build NetworkX graph from activities data - COPIED FROM NetworkTab"""
        import networkx as nx

        G = nx.DiGraph()

        # Add activity nodes with ALL data including float values
        for activity in activities:
            activity_id = activity.get('id', '')
            duration = activity.get('duration', 0)

            # For PERT mode, use expected duration for display
            if self.analysis_mode == 'probabilistic':
                if 'expected' in activity:
                    # Integer expected duration
                    duration = activity['expected']
                elif 'expected_duration' in activity:
                    duration = int(
                        activity['expected_duration'])  # Round for display

            # ENSURE float value is captured from multiple possible field names
            float_value = activity.get(
                'float', activity.get(
                    'total_float', activity.get(
                        'Float', 0)))

            # Get timing values
            ES = activity.get('ES', activity.get('earliest_start', 0))
            EF = activity.get('EF', activity.get('earliest_finish', duration))
            LS = activity.get('LS', activity.get('latest_start', 0))
            LF = activity.get('LF', activity.get('latest_finish', duration))

            G.add_node(
                activity_id,
                duration=duration,
                critical=activity.get(
                    'critical',
                    False),
                float=float_value,
                ES=ES,
                EF=EF,
                LS=LS,
                LF=LF,
                activity=activity.get(
                    'activity',
                    activity.get(
                        'name',
                        '')),
                id=activity_id)

        # Add predecessor relationships
        for activity in activities:
            activity_id = activity.get('id', '')
            predecessors = activity.get('predecessors', [])

            # Handle different predecessor formats
            if isinstance(predecessors, str):
                predecessors = [p.strip()
                                for p in predecessors.split(',') if p.strip()]

            for pred in predecessors:
                if pred and pred in G.nodes:
                    G.add_edge(pred, activity_id)

        # Add START and END nodes if needed
        self.add_start_end_nodes(G)

        return G

    def add_start_end_nodes(self, G):
        """Add START and END nodes to graph - COPIED FROM NetworkTab"""
        # Find nodes with no predecessors (start activities)
        start_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]

        if start_nodes and 'START' not in G.nodes():
            G.add_node(
                'START',
                duration=0,
                activity='Start',
                ES=0,
                EF=0,
                LS=0,
                LF=0,
                float=0)
            for node in start_nodes:
                G.add_edge('START', node)

        # Find nodes with no successors (end activities)
        end_nodes = [node for node in G.nodes() if G.out_degree(node)
                     == 0 and node != 'START']

        if end_nodes and 'END' not in G.nodes():
            # Calculate END node timing from predecessors
            max_ef = max([G.nodes[node]['EF'] for node in end_nodes])
            G.add_node(
                'END',
                duration=0,
                activity='End',
                ES=max_ef,
                EF=max_ef,
                LS=max_ef,
                LF=max_ef,
                float=0)
            for node in end_nodes:
                G.add_edge(node, 'END')

    # Adaptive sizing thresholds
    _SIZE_SMALL = 50
    _SIZE_MEDIUM = 200

    def _adaptive_scale(self, n_activities):
        """Return scale factor (1.0 = default) for the current project size."""
        if n_activities <= self._SIZE_SMALL:
            return 1.0
        if n_activities <= self._SIZE_MEDIUM:
            return 0.65
        return 0.4

    def draw_pert_network_diagram(self, G, critical_activities):
        """Draw professional PERT network diagram with rectangle-semicircle nodes"""
        self.ax.clear()

        # Reset virtual node tracking
        self._virtual_nodes = set()
        self._edge_paths = {}
        self._all_pos = {}

        if not G.nodes():
            self.ax.text(0.5, 0.5, 'No network data available',
                         ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return

        # Adaptive sizing
        n_act = len([nd for nd in G.nodes() if nd not in ('START', 'END')])
        self._scale = self._adaptive_scale(n_act)

        # 1. Create hierarchical layout (Sugiyama)
        pos = self.create_hierarchical_layout(G)

        # 2. Set figure size proportional to data range
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        if xs and ys:
            pad = 1.5 * self._scale + 1
            x_min, x_max = min(xs) - pad, max(xs) + pad
            y_min, y_max = min(ys) - pad, max(ys) + pad
            data_w = x_max - x_min
            data_h = y_max - y_min
        else:
            x_min, x_max, y_min, y_max = 0, 10, 0, 10
            data_w = data_h = 10

        # Always fit to the available viewport so the full diagram is visible.
        self._scroll_frame.fit_to_viewport()

        # 3. Draw edges with arrows (polyline through virtual waypoints)
        self.draw_network_edges(G, pos)

        # 4. Draw nodes with rectangle-semicircle format
        self.draw_pert_nodes(G, pos, critical_activities)

        # 5. Add legend
        self.add_network_legend()

        # 6. Apply display options
        self.apply_display_options(G, pos)

        # 7. Clean up virtual nodes from graph
        cleanup_virtual_nodes(G, self._virtual_nodes)

        # 8. Add node format legend
        self.figure.text(0.01, 0.01, "Node Format:", fontsize=9)
        self.figure.text(
            0.07,
            0.01,
            "ID   | ES | EF\nDur | LS | LF",
            fontsize=9)

        self.ax.set_title("PERT Network Diagram")
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min - 1.5, y_max + 1.5)
        self.ax.axis('off')
        self.figure.subplots_adjust(
            left=0.01, right=0.99, top=0.88, bottom=0.10)
        self.canvas.draw()

    def create_hierarchical_layout(self, G):
        """Sugiyama-style layered layout — delegates to shared engine.

        Adapts spacing for large projects.
        """
        n = len([nd for nd in G.nodes() if not str(nd).startswith('_virt_')])
        if n <= 50:
            x_sp, y_sp = 5.0, 2.5
        elif n <= 200:
            x_sp, y_sp = 3.0, 2.5
        else:
            x_sp, y_sp = 1.5, 1.5
        result = sugiyama_layout(G, x_spacing=x_sp, y_spacing=y_sp)
        self._virtual_nodes = result['virtual_nodes']
        self._edge_paths = result['edge_paths']
        self._all_pos = result['all_pos']
        return result['pos']

    def draw_network_edges(self, G, pos):
        """Draw edges as polylines routed through virtual-node waypoints.

        Handles PERT-specific node shapes: rectangle-semicircle for regular
        nodes, circles for START/END.
        """
        scale = getattr(self, '_scale', 1.0)
        width = 1.8 * scale
        height = width * 2 / 3
        semicircle_width = width / 3
        square_width = width * 2 / 3
        node_radius = 0.4 * scale  # for START/END circles

        all_pos = getattr(self, '_all_pos', pos)
        edge_paths = getattr(self, '_edge_paths', {})
        virtual_nodes = getattr(self, '_virtual_nodes', set())
        drawn_edges = set()

        def _edge_start(node, target_pos):
            """Compute arrow start point leaving *node* toward *target_pos*."""
            x, y = pos.get(node, all_pos.get(node, (0, 0)))
            if node in virtual_nodes:
                return x, y
            if node in ['START', 'END']:
                tx, ty = target_pos
                dx, dy = tx - x, ty - y
                d = (dx**2 + dy**2) ** 0.5
                if d > 0:
                    return x + node_radius * dx / d, y + node_radius * dy / d
                return x, y
            # Regular PERT node: exit from right edge of square
            return x + square_width / 2, y

        def _edge_end(node, source_pos):
            """Compute arrow end point arriving at *node* from *source_pos*."""
            x, y = pos.get(node, all_pos.get(node, (0, 0)))
            if node in virtual_nodes:
                return x, y
            if node in ['START', 'END']:
                sx, sy = source_pos
                dx, dy = x - sx, y - sy
                d = (dx**2 + dy**2) ** 0.5
                if d > 0:
                    return x - node_radius * dx / d, y - node_radius * dy / d
                return x, y
            # Regular PERT node: enter at left edge of semicircle
            return x - square_width / 2 - semicircle_width, y

        # --- polyline paths from edge_paths --------------------------
        for (u_orig, v_orig), path in edge_paths.items():
            if len(path) < 2:
                continue
            waypoints_raw = [(n, all_pos[n]) for n in path if n in all_pos]
            if len(waypoints_raw) < 2:
                continue

            # Build adjusted waypoints
            adjusted = []
            for idx, (n, (wx, wy)) in enumerate(waypoints_raw):
                if idx == 0:
                    nxt = waypoints_raw[1][1]
                    adjusted.append(_edge_start(n, nxt))
                elif idx == len(waypoints_raw) - 1:
                    prev = adjusted[-1]
                    adjusted.append(_edge_end(n, prev))
                else:
                    adjusted.append((wx, wy))  # virtual: use raw position

            for seg_idx in range(len(adjusted) - 1):
                x1, y1 = adjusted[seg_idx]
                x2, y2 = adjusted[seg_idx + 1]
                if seg_idx == len(adjusted) - 2:
                    self.ax.annotate(
                        "", xy=(
                            x2, y2), xytext=(
                            x1, y1), arrowprops=dict(
                            arrowstyle="->", color="black", lw=1.5), zorder=1, )
                else:
                    self.ax.plot([x1, x2], [y1, y2],
                                 color='black', lw=1.5, zorder=1)

            for i in range(len(path) - 1):
                drawn_edges.add((path[i], path[i + 1]))

        # --- remaining direct edges ---------------------------------
        for u, v in G.edges():
            if (u, v) in drawn_edges:
                continue
            if u in virtual_nodes or v in virtual_nodes:
                continue
            if u not in pos or v not in pos:
                continue
            end_pt = _edge_end(v, pos[u])
            start_pt = _edge_start(u, pos[v])
            self.ax.annotate(
                "", xy=end_pt, xytext=start_pt,
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
            )

    def draw_pert_nodes(self, G, pos, critical_activities):
        """Draw nodes with adaptive size based on project scale"""
        scale = getattr(self, '_scale', 1.0)
        # ENLARGED node size parameters, scaled for large projects
        width = 2 * scale
        height = width * 2 / 3
        semicircle_width = width / 3
        square_width = width * 2 / 3
        node_radius = 0.6 * scale
        label_fs = max(5, int(9 * scale))
        virtual_nodes = getattr(self, '_virtual_nodes', set())

        for node in G.nodes():
            if node in virtual_nodes:
                continue  # Skip virtual/dummy nodes
            if node not in pos:
                continue
            x, y = pos[node]

            # Determine node color based on critical path highlighting
            if node == 'START':
                color = 'lightgreen'
            elif node == 'END':
                color = 'orange'
            else:
                # Check if critical path highlighting is enabled
                if self.highlight_critical.get():
                    if node in critical_activities:
                        color = 'red'
                    else:
                        color = 'lightblue'
                else:
                    # Highlighting OFF: all activities light blue
                    color = 'lightblue'

            # Special handling for START and END nodes (circles)
            if node in ['START', 'END']:
                circle = plt.Circle((x, y), node_radius,
                                    fill=True, color=color, alpha=0.7,
                                    edgecolor='black', linewidth=1.5, zorder=3)
                self.ax.add_patch(circle)

                display_text = 'Start' if node == 'START' else 'End'
                self.ax.text(
                    x,
                    y,
                    display_text,
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=label_fs,
                    fontweight='bold',
                    zorder=5)
            else:
                # Draw semicircle on left side
                semicircle = mpatches.Wedge(
                    (x - square_width / 2, y),
                    semicircle_width,  # radius
                    90, 270,  # angles for left-facing semicircle
                    fill=True, color=color, alpha=0.7,
                    edgecolor='black', linewidth=1.4, zorder=3
                )
                self.ax.add_patch(semicircle)

                # Draw square on right side
                square = plt.Rectangle(
                    (x - square_width / 2, y - height / 2),
                    square_width, height,
                    fill=True, color=color, alpha=0.7,
                    edgecolor='black', linewidth=1.5, zorder=3
                )
                self.ax.add_patch(square)

                # Draw grid lines
                # Horizontal divider across entire shape
                self.ax.plot([x -
                              square_width /
                              2 -
                              semicircle_width, x +
                              square_width /
                              2], [y, y], color='black', linewidth=0.8, zorder=4)

                # Vertical divider between semicircle and square
                self.ax.plot([x -
                              square_width /
                              2, x -
                              square_width /
                              2], [y -
                                   height /
                                   2, y +
                                   height /
                                   2], color='black', linewidth=0.8, zorder=5)

                # Vertical divider in square section
                self.ax.plot([x, x], [y - height / 2, y + height / 2],
                             color='black', linewidth=0.8, zorder=4)

                # IMPROVED text positioning for "ID | ES | EF" format
                # Top row: ID | ES | EF
                node_label = node if len(
                    str(node)) <= 8 else str(node)[:8] + '…'
                self.ax.text(
                    x - square_width / 2 - semicircle_width / 2,
                    y + height / 4,
                    node_label,
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=label_fs,
                    fontweight='bold',
                    zorder=5)
                self.ax.text(x - square_width / 4,
                             y + height / 4,
                             str(G.nodes[node]['ES']),
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=label_fs,
                             zorder=5)
                self.ax.text(x + square_width / 4,
                             y + height / 4,
                             str(G.nodes[node]['EF']),
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=label_fs,
                             zorder=5)

                # IMPROVED text positioning for "Dur | LS | LF" format
                # Bottom row: Duration | LS | LF
                self.ax.text(x - square_width / 2 - semicircle_width / 2,
                             y - height / 4,
                             str(G.nodes[node]['duration']),
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=label_fs,
                             zorder=5)
                self.ax.text(x - square_width / 4,
                             y - height / 4,
                             str(G.nodes[node]['LS']),
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=label_fs,
                             zorder=5)
                self.ax.text(x + square_width / 4,
                             y - height / 4,
                             str(G.nodes[node]['LF']),
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=label_fs,
                             zorder=5)

                # IMPROVED activity name above node with space-based wrapping
                activity_name = G.nodes[node].get('activity', '')
                if activity_name and activity_name not in ['Start', 'End']:
                    wrapped_lines = self.wrap_activity_name(activity_name)

                    # Display each line separately, stacked vertically
                    line_height = 0.3 * scale
                    start_y = y + height / 2 + 0.2 * scale

                    for i, line in enumerate(wrapped_lines):
                        self.ax.text(x - 0.2,
                                     start_y + (i * line_height),
                                     line,
                                     horizontalalignment='center',
                                     verticalalignment='bottom',
                                     fontsize=max(5,
                                                  int(8 * scale)),
                                     color='purple',
                                     fontweight='bold',
                                     zorder=5)

    def wrap_activity_name(self, text, max_chars_per_line=12):
        """Wrap activity name by character count, returns lines split for display"""
        if not text:
            return []
        import textwrap
        return textwrap.wrap(text, width=max_chars_per_line)

    def add_network_legend(self):
        """Add simplified legend without START/END entries - COPIED FROM NetworkTab"""
        legend_elements = [
            mpatches.Patch(
                color='red',
                alpha=0.7,
                label='Critical Path'),
            mpatches.Patch(
                color='lightblue',
                alpha=0.7,
                label='Normal Activity')]
        self.ax.legend(handles=legend_elements, loc='upper right')

    def apply_display_options(self, G, pos):
        """Apply user-selected display options - REMOVED edge labels"""
        # REMOVED: Edge labels functionality
        # if self.show_edge_labels.get():
        #     self.add_edge_labels(G, pos)

        # Apply float values option
        if self.show_float.get():
            self.add_float_labels(G, pos)

    # REMOVED: add_edge_labels method no longer needed
    # def add_edge_labels(self, G, pos):
    #     """REMOVED: Edge labels method no longer needed"""
    #     pass

    def add_float_labels(self, G, pos):
        """Add float values BELOW nodes - repositioned"""
        if not self.show_float.get():
            return

        virtual_nodes = getattr(self, '_virtual_nodes', set())

        for node in G.nodes():
            if node in ['START', 'END']:
                continue  # Skip START/END nodes
            if node in virtual_nodes:
                continue  # Skip virtual/dummy nodes
            if node not in pos:
                continue

            x, y = pos[node]

            # GET ACTUAL FLOAT VALUE from node data
            float_value = G.nodes[node].get('float', 0)

            # Handle different float value formats
            if isinstance(float_value, (int, float)):
                # Remove decimals for cleaner display
                float_text = str(int(float_value))
            else:
                float_text = str(float_value)

            # Position BELOW the node (negative y offset)
            float_y = y - 1.2  # Changed from y + 1.0 to y - 1.2

            # LARGER font, NO "F" prefix, just the number
            self.ax.text(
                x - 0.3,
                float_y,
                float_text,
                ha='center',
                va='center',
                fontsize=12,
                fontweight='bold',
                color='darkblue',
                bbox=dict(
                    boxstyle='round,pad=0.3',
                    facecolor='white',
                    alpha=0.8,
                    edgecolor='darkblue'))

    def save_diagram(self):
        """Save the current diagram to file - COPIED FROM NetworkTab"""
        if not MATPLOTLIB_AVAILABLE or not self.results_data:
            messagebox.showwarning(
                "Warning", "No diagram to save. Please run analysis first.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save PERT Diagram",
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
                messagebox.showinfo(
                    "Success", f"PERT diagram saved to {filename}")
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to save diagram: {
                        str(e)}")

    def _open_interactive_view(self):
        """Open the interactive vis.js PERT network viewer in the default browser."""
        if not self.results_data:
            messagebox.showwarning(
                "Warning", "No diagram to display. Please run analysis first.")
            return
        html_path = open_interactive_network(
            self.results_data, analysis_mode=self.analysis_mode, mode='pert')
        if not html_path:
            messagebox.showerror("Error",
                                 "Could not generate interactive view. "
                                 "Please ensure pyvis is installed.")

    def reset_view(self):
        """Reset the plot view - COPIED FROM NetworkTab"""
        if not MATPLOTLIB_AVAILABLE:
            return

        if hasattr(self.toolbar, 'home'):
            self.toolbar.home()
        else:
            # Fallback: recreate the diagram
            self.update_diagram()

    def clear_network(self):
        """Clear the PERT diagram - COPIED FROM NetworkTab"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.results_data = None
        self.analysis_mode = None
        self.current_graph = None
        self.current_critical_activities = []
        self.create_empty_plot()
        if _PLOTLY_EMBED:
            self._plotly_frame.clear()

    # -- Plotly helpers (PERT Diagram) --------------------------------------
    def _switch_renderer(self):
        if not _PLOTLY_EMBED:
            return
        if self._render_mode_var.get() == "plotly":
            self._mpl_frame.pack_forget()
            self._plotly_frame.pack(fill="both", expand=True)
            if self.results_data:
                self._update_plotly_pert()
        else:
            self._plotly_frame.pack_forget()
            self._mpl_frame.pack(fill="both", expand=True)

    def _update_plotly_pert(self):
        if not self.results_data:
            return
        try:
            fig = plotly_pert_network(self.results_data, self.analysis_mode)
            if fig:
                self._plotly_frame.update_chart(fig)
        except Exception:
            pass
