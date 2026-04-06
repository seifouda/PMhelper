#!/usr/bin/env python3
"""
Network Tab Module

Displays project network diagrams with node positioning,
activity dependencies, and critical path highlighting.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import matplotlib.patches as mpatches
    import networkx as nx
    MATPLOTLIB_AVAILABLE = True
    NETWORKX_AVAILABLE = True
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    NETWORKX_AVAILABLE = False

try:
    from pmhelper.core.network_converter import aon_to_aoa
    AOA_AVAILABLE = True
except ImportError:
    AOA_AVAILABLE = False

from pmhelper.utils.visualizations import NetworkDiagramVisualizer
from pmhelper.utils.network_layout import sugiyama_layout, cleanup_virtual_nodes, draw_edges_polyline
from pmhelper.gui.widgets.scrollable_mpl_frame import ScrollableMatplotlibFrame
from pmhelper.utils.interactive_network import open_interactive_network, PYVIS_AVAILABLE


class NetworkTab:
    """Network diagram tab for displaying project network"""
    
    def __init__(self, notebook, main_window):
        self.notebook = notebook
        self.main_window = main_window
        self.results_data = None
        self.analysis_mode = None
        self.figure = None
        self.canvas = None
        self._view_mode_var = tk.StringVar(value="AON")
        
        self.create_tab()
    
    def create_tab(self):
        """Create the network tab"""
        self.network_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.network_frame, text="Network Diagram")
        
        if not MATPLOTLIB_AVAILABLE:
            self.create_no_matplotlib_message()
            return
        
        # Create control frame at the top
        self.create_control_frame()
        # Create plot area (canvas and toolbar frames)
        self.create_plot_area()
    
    def create_no_matplotlib_message(self):
        """Create message when matplotlib is not available"""
        message_frame = ttk.Frame(self.network_frame)
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        message_label = ttk.Label(
            message_frame,
            text="Network diagrams require matplotlib.\nPlease install matplotlib to view network diagrams.",
            font=("Arial", 12),
            justify=tk.CENTER
        )
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
                subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
                messagebox.showinfo("Success", "matplotlib installed successfully. Please restart the application.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install matplotlib: {str(e)}")
    
    def create_control_frame(self):
        """Create control buttons frame"""
        control_frame = ttk.Frame(self.network_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Diagram options
        options_frame = ttk.LabelFrame(control_frame, text="Display Options", padding="5")
        options_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Checkboxes for display options
        self.show_critical_var = tk.BooleanVar(value=True)
        self.show_times_var = tk.BooleanVar(value=True)
        self.show_float_var = tk.BooleanVar(value=False)
        # REMOVED: Activity labels option (always show labels now)
        # self.show_labels_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Highlight Critical Path", 
                       variable=self.show_critical_var, 
                       command=self.update_diagram).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Show Times", 
                       variable=self.show_times_var, 
                       command=self.update_diagram).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Show Float", 
                       variable=self.show_float_var, 
                       command=self.update_diagram).pack(side=tk.LEFT, padx=5)
        # REMOVED: Activity labels checkbox - labels are always shown now
        
        # Network Type (AON / AOA) toggle
        if AOA_AVAILABLE:
            type_frame = ttk.LabelFrame(control_frame, text="Network Type", padding="3")
            type_frame.pack(side=tk.LEFT, padx=(0, 10))
            ttk.Radiobutton(
                type_frame, text="AON (Activity on Node)", value="AON",
                variable=self._view_mode_var, command=self.update_diagram,
            ).pack(side=tk.LEFT, padx=4)
            ttk.Radiobutton(
                type_frame, text="AOA (Activity on Arrow)", value="AOA",
                variable=self._view_mode_var, command=self.update_diagram,
            ).pack(side=tk.LEFT, padx=4)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Save Image", 
                  command=self.save_diagram).pack(side=tk.LEFT, padx=5)
        if PYVIS_AVAILABLE:
            ttk.Button(button_frame, text="\U0001f310 Interactive View",
                      command=self._open_interactive_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="? Help", 
                  command=self.main_window.show_network_tab_help).pack(side=tk.LEFT, padx=5)
        # Removed Refresh and Reset View buttons
    
    def create_plot_area(self):
        """Create matplotlib plot area with scrollable viewport."""
        self._scroll_frame = ScrollableMatplotlibFrame(
            self.network_frame, figsize=(12, 8), dpi=100, toolbar=True)
        self._scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.figure = self._scroll_frame.figure
        self.canvas = self._scroll_frame.canvas
        self.toolbar = self._scroll_frame.toolbar
        self.create_empty_plot()
        
    def create_empty_plot(self):
        """Create empty plot with instruction message"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Run project analysis to display network diagram', 
            horizontalalignment='center', verticalalignment='center',
            transform=ax.transAxes, fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_network(self, results_data, analysis_mode):
        """Update the network diagram with new data"""
        self.results_data = results_data
        self.analysis_mode = analysis_mode
        
        if not MATPLOTLIB_AVAILABLE:
            return
        
        if not results_data:
            self.create_empty_plot()
            return
        
        self.update_diagram()
    
    def update_diagram(self):
        """Update the network diagram with professional critical path visualization"""
        if not MATPLOTLIB_AVAILABLE or not NETWORKX_AVAILABLE or not self.results_data:
            return
        
        try:
            # Clear the figure completely
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            
            # Extract activities and critical activities from results_data
            activities = self.results_data.get('activities', [])
            critical_activities = self.results_data.get('critical_activities', [])
            
            if activities:
                # Check view mode
                view_mode = self._view_mode_var.get()
                if view_mode == "AOA" and AOA_AVAILABLE:
                    self._draw_aoa_diagram(activities)
                    # AOA sets its own title — skip AON title setting below
                    self.canvas.draw()
                    return

                # Build NetworkX graph from activities (AON mode)
                G = self.build_graph_from_activities(activities)
                
                # Draw the professional network diagram
                self.draw_network_diagram(G, critical_activities)
            else:
                # No activities data available
                self.ax.text(0.5, 0.5, 'No network data available', 
                            ha='center', va='center', transform=self.ax.transAxes, 
                            fontsize=12)
                self.ax.axis('off')
            
            # Set title
            project_duration = self.results_data.get('project_duration', 'Unknown')
            if self.analysis_mode == 'probabilistic':
                expected_duration = self.results_data.get('expected_duration', 'Unknown')
                if isinstance(expected_duration, (int, float)):
                    expected_duration = f"{expected_duration:.1f}"
                title = f"Project Network Diagram\nScheduling Duration: {project_duration}, Expected Duration: {expected_duration}"
            else:
                title = f"Project Network Diagram\nProject Duration: {project_duration}"
            
            self.ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Final draw (draw_network_diagram sets layout; title added above)
            self.canvas.draw()
            
        except Exception as e:
            # Show error in the plot
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            self.ax.text(0.5, 0.5, f'Error creating network diagram:\n{str(e)}', 
                        ha='center', va='center', transform=self.ax.transAxes, 
                        fontsize=12, color='red')
            self.ax.axis('off')
            self.canvas.draw()
            
            # Also print error for debugging
            print(f"Failed to create network diagram: {str(e)}")
    
    def build_graph_from_activities(self, activities):
        """Build NetworkX graph from activities data"""
        import networkx as nx
        
        G = nx.DiGraph()
        
        # Add activity nodes with ALL data including float values
        for activity in activities:
            activity_id = activity.get('id', '')
            duration = activity.get('duration', 0)
            
            # For PERT mode, use expected duration for display
            if self.analysis_mode == 'probabilistic':
                if 'expected' in activity:
                    duration = activity['expected']  # Integer expected duration
                elif 'expected_duration' in activity:
                    duration = int(activity['expected_duration'])  # Round for display
            
            # ENSURE float value is captured from multiple possible field names
            float_value = activity.get('float', activity.get('total_float', activity.get('Float', 0)))
            
            G.add_node(activity_id, 
                      duration=duration,
                      critical=activity.get('critical', False),
                      float=float_value,  # Explicitly store float
                      id=activity_id)
        
        # Add predecessor relationships
        for activity in activities:
            activity_id = activity.get('id', '')
            predecessors = activity.get('predecessors', [])
            
            # Handle different predecessor formats
            if isinstance(predecessors, str):
                predecessors = [p.strip() for p in predecessors.split(',') if p.strip()]
            
            for pred in predecessors:
                if pred and pred in G.nodes:
                    G.add_edge(pred, activity_id)
        
        # Add START and END nodes if needed
        self.add_start_end_nodes(G)
        
        return G
    
    def add_start_end_nodes(self, G):
        """Add START and END nodes to graph"""
        # Find nodes with no predecessors (start activities)
        start_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]
        
        if start_nodes and 'START' not in G.nodes():
            G.add_node('START', duration=0, activity='Start')
            for node in start_nodes:
                G.add_edge('START', node)
        
        # Find nodes with no successors (end activities)
        end_nodes = [node for node in G.nodes() if G.out_degree(node) == 0 and node != 'START']
        
        if end_nodes and 'END' not in G.nodes():
            G.add_node('END', duration=0, activity='End')
            for node in end_nodes:
                G.add_edge(node, 'END')
    
    # Adaptive sizing thresholds
    _SIZE_SMALL = 50
    _SIZE_MEDIUM = 200

    def _adaptive_params(self, n_activities):
        """Return (node_radius, label_fontsize) for the current project size."""
        if n_activities <= self._SIZE_SMALL:
            return 0.6, 10
        if n_activities <= self._SIZE_MEDIUM:
            return 0.4, 7
        return 0.25, 5

    def draw_network_diagram(self, G, critical_activities):
        """Professional network diagram with critical path highlighting"""
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
        n_act = len([nd for nd in G.nodes()
                     if nd not in ('START', 'END')])
        self._node_radius, self._label_fs = self._adaptive_params(n_act)

        # 1. Create hierarchical layout (inserts virtual nodes into G)
        pos = self.create_hierarchical_layout(G)

        # 2. Set figure size proportional to data range
        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        if xs and ys:
            pad = self._node_radius + 1
            x_min, x_max = min(xs) - pad, max(xs) + pad
            y_min, y_max = min(ys) - pad, max(ys) + pad
            data_w = x_max - x_min
            data_h = y_max - y_min
        else:
            x_min, x_max, y_min, y_max = 0, 10, 0, 10
            data_w = data_h = 10

        # Always fit to the available viewport so the full diagram is visible.
        # The toolbar provides zoom / pan for detail.
        self._scroll_frame.fit_to_viewport()

        # 3. Draw edges with arrows (polyline through virtual waypoints)
        self.draw_network_edges(G, pos)

        # 4. Draw nodes with critical path coloring (skips virtual nodes)
        self.draw_network_nodes(G, pos, critical_activities)

        # 5. Add legend
        self.add_network_legend()

        # 6. Apply display options
        self.apply_display_options(G, pos)

        # 7. Clean up virtual nodes from graph
        cleanup_virtual_nodes(G, self._virtual_nodes)

        self.ax.set_title("Project Network Diagram")
        # Set explicit data limits and minimal margins so content fills figure
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.axis('off')
        self.figure.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.02)
        self.canvas.draw()
    
    def create_hierarchical_layout(self, G):
        """Sugiyama-style layered layout — delegates to shared engine.

        Adapts spacing for large projects so the layout stays within
        renderable figure dimensions.
        """
        n = len([nd for nd in G.nodes() if not str(nd).startswith('_virt_')])
        if n <= 50:
            x_sp, y_sp = 3.5, 4.0
        elif n <= 200:
            x_sp, y_sp = 2.0, 2.5
        else:
            x_sp, y_sp = 1.0, 1.5
        result = sugiyama_layout(G, x_spacing=x_sp, y_spacing=y_sp)
        self._virtual_nodes = result['virtual_nodes']
        self._edge_paths = result['edge_paths']
        self._all_pos = result['all_pos']
        return result['pos']
    
    def draw_network_edges(self, G, pos):
        """Draw edges as polylines routed through virtual-node waypoints."""
        show_crit = self.show_critical_var.get()

        def critical_check(u, v):
            return (show_crit
                    and G.nodes.get(u, {}).get('critical', False)
                    and G.nodes.get(v, {}).get('critical', False))

        draw_edges_polyline(
            self.ax, G, pos,
            self._all_pos, self._virtual_nodes, self._edge_paths,
            node_radius=getattr(self, '_node_radius', 0.6),
            critical_check=critical_check,
        )
    
    def draw_network_nodes(self, G, pos, critical_activities):
        """Draw nodes with corrected critical path highlighting"""
        node_radius = getattr(self, '_node_radius', 0.6)
        label_fs = getattr(self, '_label_fs', 10)
        virtual_nodes = getattr(self, '_virtual_nodes', set())
        
        for node in G.nodes():
            if node in virtual_nodes:
                continue  # Skip virtual/dummy nodes
            if node not in pos:
                continue
            x, y = pos[node]
            
            # NEW LOGIC: Critical path highlighting behavior
            if node == 'START':
                color = 'lightgreen'
            elif node == 'END':
                color = 'orange'
            else:
                # Check if critical path highlighting is enabled
                if self.show_critical_var.get():
                    # Highlighting ON: red for critical, light blue for non-critical
                    if node in critical_activities:
                        color = 'red'
                    else:
                        color = 'lightblue'
                else:
                    # Highlighting OFF: all activities light blue
                    color = 'lightblue'
            
            # Draw node circle
            circle = plt.Circle((x, y), node_radius, fill=True, color=color, alpha=0.7,
                               edgecolor='black', linewidth=1.5)
            self.ax.add_patch(circle)
            
            # ALWAYS show activity labels (no toggle)
            if node in ['START', 'END']:
                display_text = 'Start' if node == 'START' else 'End'
                self.ax.text(x, y, display_text, ha='center', va='center',
                            fontsize=label_fs, fontweight='bold')
            else:
                if self.show_times_var.get():
                    # Split node into ID and duration sections
                    self.ax.plot([x - node_radius, x + node_radius], [y, y],
                                color='black', linewidth=1.2)
                    
                    # Activity ID (top) - ALWAYS SHOWN
                    self.ax.text(x, y + node_radius / 2, node, ha='center', va='center',
                                fontsize=label_fs, fontweight='bold')
                    
                    # Duration (bottom) - ALWAYS SHOWN
                    duration = G.nodes[node].get('duration', 0)
                    self.ax.text(x, y - node_radius / 2, str(duration),
                                ha='center', va='center', fontsize=max(5, label_fs - 1))
                else:
                    # Just show activity ID - ALWAYS SHOWN
                    self.ax.text(x, y, node, ha='center', va='center',
                                fontsize=label_fs, fontweight='bold')
    
    def add_network_legend(self):
        """Add simplified legend without START/END entries"""
        try:
            from matplotlib import patches as mpatches
            
            # SIMPLIFIED legend - only activity types
            legend_elements = [
                mpatches.Patch(color='red', alpha=0.7, label='Critical Path'),
                mpatches.Patch(color='lightblue', alpha=0.7, label='Normal Activity')
            ]
            # REMOVED: Start and End legend entries
            
            self.ax.legend(handles=legend_elements, loc='lower right')
        except ImportError:
            # Fallback if patches not available
            pass
    
    def apply_display_options(self, G, pos):
        """Apply user-selected display options"""
        # Activity labels are ALWAYS shown (no option)
        
        # Apply float display if enabled
        if hasattr(self, 'show_float_var') and self.show_float_var.get():
            self.add_float_labels(G, pos)
    
    def add_float_labels(self, G, pos):
        """Add float values over nodes - fixed and improved"""
        if not self.show_float_var.get():
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
                float_text = str(int(float_value))  # Remove decimals for cleaner display
            else:
                float_text = str(float_value)
            
            # Display float value OVER the node (higher y position)
            float_y = y + 1.2  # Position above the node
            
            # LARGER font, NO "F" prefix, just the number
            self.ax.text(x, float_y, float_text, ha='center', va='center',
                        fontsize=12, fontweight='bold', color='darkblue',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                 alpha=0.8, edgecolor='darkblue'))
    
    def save_diagram(self):
        """Save the current diagram to file"""
        if not MATPLOTLIB_AVAILABLE or not self.results_data:
            messagebox.showwarning("Warning", "No diagram to save. Please run analysis first.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Network Diagram",
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
                messagebox.showinfo("Success", f"Diagram saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save diagram: {str(e)}")
    
    def _open_interactive_view(self):
        """Open the interactive vis.js network viewer in the default browser."""
        if not self.results_data:
            messagebox.showwarning("Warning",
                                   "No diagram to display. Please run analysis first.")
            return
        html_path = open_interactive_network(
            self.results_data, analysis_mode=self.analysis_mode, mode='network')
        if not html_path:
            messagebox.showerror("Error",
                                 "Could not generate interactive view. "
                                 "Please ensure pyvis is installed.")

    def reset_view(self):
        """Reset the plot view"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        if hasattr(self.toolbar, 'home'):
            self.toolbar.home()
        else:
            # Fallback: recreate the diagram
            self.update_diagram()
    
    def clear_diagram(self):
        """Clear the network diagram"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.results_data = None
        self.analysis_mode = None
        self.create_empty_plot()

    # ---- AOA diagram (Activity-on-Arrow) ----------------------------------------

    def _aoa_event_layout(self, network) -> dict:
        """Compute (x, y) positions for each event based on topological level.

        Events at the same level share an x-column; they are spread vertically
        within each column.
        """
        order = network._topo_event_order()

        # Longest-path level for each event (forward sweep)
        levels = {network.start_event_id: 0}
        for eid in order:
            cur_lev = levels.get(eid, 0)
            for a in network._outgoing(eid):
                cand = cur_lev + 1
                if cand > levels.get(a.to_event, -1):
                    levels[a.to_event] = cand

        # Group events per level
        from collections import defaultdict
        level_events: dict = defaultdict(list)
        for eid, lev in levels.items():
            level_events[lev].append(eid)

        x_gap = 3.5
        y_gap = 2.5
        pos: dict = {}
        for lev, eids in level_events.items():
            eids_sorted = sorted(eids)
            n = len(eids_sorted)
            for i, eid in enumerate(eids_sorted):
                x = lev * x_gap
                y = (i - (n - 1) / 2.0) * y_gap
                pos[eid] = (x, y)

        return pos

    def _draw_aoa_diagram(self, activities: list) -> None:
        """Render an Activity-on-Arrow (AOA) network diagram.

        Converts the current AON activity list to AOA via network_converter,
        runs CPM, then draws:
          * Events as split circles  [event# | ET | LT]
          * Real arrows labelled with activity id and duration
          * Dummy arrows as dashed grey lines
          * Critical path in red
        """
        self.ax.clear()

        # Convert + CPM
        try:
            network = aon_to_aoa(activities)
            network.run_cpm()
        except Exception as exc:
            self.ax.text(
                0.5, 0.5,
                f"Could not convert to AOA:\n{exc}",
                ha="center", va="center",
                transform=self.ax.transAxes, fontsize=11, color="red",
            )
            return

        pos = self._aoa_event_layout(network)
        if not pos:
            return

        xs = [p[0] for p in pos.values()]
        ys = [p[1] for p in pos.values()]
        pad = 2.0
        x_min, x_max = min(xs) - pad, max(xs) + pad
        y_min, y_max = min(ys) - pad, max(ys) + pad

        try:
            self._scroll_frame.fit_to_viewport()
        except Exception:
            pass

        show_crit  = self.show_critical_var.get()
        show_times = self.show_times_var.get()
        r_ev = 0.55   # event circle radius

        # ── Draw arrows ──────────────────────────────────────────────
        for act in network.activities:
            if act.from_event not in pos or act.to_event not in pos:
                continue
            x1, y1 = pos[act.from_event]
            x2, y2 = pos[act.to_event]

            if act.is_dummy:
                color, ls, lw, alpha = "#888888", "--", 1.0, 0.55
            elif act.is_critical and show_crit:
                color, ls, lw, alpha = "#cc2222", "-", 2.5, 0.92
            else:
                color, ls, lw, alpha = "#1a5296", "-", 1.8, 0.85

            dx, dy = x2 - x1, y2 - y1
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length < 1e-9:
                continue
            ux, uy = dx / length, dy / length

            # Shorten by event-circle radius at both ends
            x1a = x1 + ux * r_ev
            y1a = y1 + uy * r_ev
            x2a = x2 - ux * r_ev
            y2a = y2 - uy * r_ev

            # Arrow line
            self.ax.plot(
                [x1a, x2a], [y1a, y2a],
                color=color, linewidth=lw, linestyle=ls, alpha=alpha, zorder=3,
            )
            # Arrowhead
            self.ax.annotate(
                "",
                xy=(x2a, y2a),
                xytext=(x2a - ux * 0.01, y2a - uy * 0.01),
                arrowprops=dict(
                    arrowstyle="->", color=color, lw=lw, mutation_scale=13,
                ),
                zorder=4,
            )

            # Arrow label (real activities only)
            if not act.is_dummy:
                mx = (x1a + x2a) / 2
                my = (y1a + y2a) / 2
                # Perpendicular offset so label doesn't sit on the line
                perp_x = -uy * 0.35
                perp_y =  ux * 0.35
                lx, ly = mx + perp_x, my + perp_y

                if show_times:
                    tf_str = f"\nTF={act.total_float:.0f}"
                else:
                    tf_str = ""
                label_text = f"{act.activity_id} ({act.duration:.0f}){tf_str}"

                self.ax.text(
                    lx, ly, label_text,
                    ha="center", va="center", fontsize=7.5, zorder=5,
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor="white", alpha=0.78, edgecolor="none",
                    ),
                )

        # ── Draw events ──────────────────────────────────────────────
        for eid, ev in network.events.items():
            if eid not in pos:
                continue
            x, y = pos[eid]

            is_start_end = eid in (network.start_event_id, network.end_event_id)
            is_crit_ev    = show_crit and abs(ev.slack) < 1e-9

            if is_start_end:
                fc, ec_col, lw = "#ffffcc", "#999900", 2.0
            elif is_crit_ev:
                fc, ec_col, lw = "#ffdddd", "#cc2222", 2.2
            else:
                fc, ec_col, lw = "#dde8ff", "#336699", 1.5

            circle = plt.Circle(
                (x, y), r_ev, fill=True,
                facecolor=fc, edgecolor=ec_col, linewidth=lw, zorder=5,
            )
            self.ax.add_patch(circle)

            if show_times:
                # Horizontal divider (lower half)
                self.ax.plot(
                    [x - r_ev, x + r_ev], [y, y],
                    color=ec_col, linewidth=0.8, zorder=6,
                )
                # Vertical divider (lower half only)
                self.ax.plot(
                    [x, x], [y - r_ev, y],
                    color=ec_col, linewidth=0.8, zorder=6,
                )
                # Event number (top)
                self.ax.text(
                    x, y + r_ev * 0.42, str(eid),
                    ha="center", va="center", fontsize=7, fontweight="bold", zorder=7,
                )
                # ET (bottom-left)
                self.ax.text(
                    x - r_ev * 0.38, y - r_ev * 0.42,
                    f"{ev.earliest_time:.0f}",
                    ha="center", va="center", fontsize=6, color="#1a5296", zorder=7,
                )
                # LT (bottom-right)
                self.ax.text(
                    x + r_ev * 0.38, y - r_ev * 0.42,
                    f"{ev.latest_time:.0f}",
                    ha="center", va="center", fontsize=6, color="#aa0000", zorder=7,
                )
            else:
                self.ax.text(
                    x, y, str(eid),
                    ha="center", va="center", fontsize=8, fontweight="bold", zorder=7,
                )

            # Start / End label below circle
            if ev.label in ("Start", "End"):
                self.ax.text(
                    x, y - r_ev - 0.28, ev.label,
                    ha="center", va="top", fontsize=7, style="italic", zorder=7,
                )

        # ── Legend ───────────────────────────────────────────────────
        from matplotlib import patches as mpatches_local
        legend_items = [
            mpatches_local.Patch(
                facecolor="#ffdddd", edgecolor="#cc2222", label="Critical Event"
            ),
            mpatches_local.Patch(
                facecolor="#dde8ff", edgecolor="#336699", label="Normal Event"
            ),
            mpatches_local.Patch(
                facecolor="#ffffcc", edgecolor="#999900", label="Start / End Event"
            ),
        ]
        if show_crit:
            legend_items += [
                mpatches_local.Patch(color="#cc2222", label="Critical Arrow"),
            ]
        legend_items += [
            mpatches_local.Patch(color="#1a5296", label="Normal Arrow"),
            mpatches_local.Patch(color="#888888", label="Dummy Arrow (dashed)"),
        ]
        self.ax.legend(handles=legend_items, loc="lower right", fontsize=7)

        # ── Title and axis ───────────────────────────────────────────
        pd_val = network.project_duration
        title_lines = [
            "AOA Network Diagram",
            f"Project Duration: {pd_val:.0f}",
        ]
        if show_times:
            title_lines.append("Event circle: [ id | ET | LT ]")
        self.ax.set_title("\n".join(title_lines), fontsize=12, fontweight="bold")

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.axis("off")
        self.figure.subplots_adjust(left=0.01, right=0.99, top=0.90, bottom=0.02)

    # ---- end AOA section --------------------------------------------------------

    def trace_float_values(self):
        """Trace float values from analysis to display"""
        print("=" * 80)
        print("FLOAT VALUE TRACING")
        print("=" * 80)
        
        # Check if current results_data has float values
        if self.results_data:
            activities = self.results_data.get('activities', [])
            print("Activities from results_data:")
            for activity in activities:
                if activity.get('id') not in ['START', 'END']:
                    float_val = activity.get('float', activity.get('total_float', 'MISSING'))
                    print(f"  {activity.get('id')}: float = {float_val}")
        
        print("=" * 80)
    
    def test_critical_highlighting(self):
        """Test critical path highlighting logic"""
        print("=" * 80)
        print("CRITICAL PATH HIGHLIGHTING TEST")
        print("=" * 80)
        
        # Simulate highlighting on/off
        test_nodes = ['A', 'B', 'C', 'D']
        test_critical = ['A', 'C']
        
        print("Testing highlighting ON:")
        for node in test_nodes:
            if node in test_critical:
                expected_color = 'red'
            else:
                expected_color = 'lightblue'
            print(f"  {node}: Expected color = {expected_color}")
        
        print("\nTesting highlighting OFF:")
        for node in test_nodes:
            expected_color = 'lightblue'
            print(f"  {node}: Expected color = {expected_color}")
        
        print("=" * 80)
    
    def export_network_data(self):
        """Export network data for external tools"""
        if not self.results_data:
            messagebox.showwarning("Warning", "No network data to export. Please run analysis first.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Network Data",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("GraphML files", "*.graphml"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                if filename.lower().endswith('.json'):
                    self._export_json(filename)
                elif filename.lower().endswith('.graphml'):
                    self._export_graphml(filename)
                else:
                    self._export_csv(filename)
                
                messagebox.showinfo("Success", f"Network data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export network data: {str(e)}")
    
    def _export_csv(self, filename):
        """Export network data as CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write headers
            writer.writerow(["From", "To", "Activity_ID", "Activity_Name", "Duration", "Critical"])
            
            # Write edges/dependencies
            activities = self.results_data.get('activities', [])
            for activity in activities:
                predecessors = activity.get('predecessors', [])
                if not predecessors:
                    predecessors = ['START']
                
                for pred in predecessors:
                    row = [
                        pred,
                        activity.get('id', ''),
                        activity.get('id', ''),
                        activity.get('name', ''),
                        activity.get('duration', ''),
                        "Yes" if activity.get('critical', False) else "No"
                    ]
                    writer.writerow(row)
    
    def _export_json(self, filename):
        """Export network data as JSON"""
        import json
        
        # Prepare network data
        network_data = {
            'project_info': {
                'duration': self.results_data.get('project_duration', ''),
                'critical_path': self.results_data.get('critical_path', []),
                'analysis_mode': self.analysis_mode
            },
            'nodes': [],
            'edges': []
        }
        
        # Add nodes (activities)
        activities = self.results_data.get('activities', [])
        for activity in activities:
            node = {
                'id': activity.get('id', ''),
                'name': activity.get('name', ''),
                'duration': activity.get('duration', ''),
                'critical': activity.get('critical', False),
                'earliest_start': activity.get('earliest_start', ''),
                'earliest_finish': activity.get('earliest_finish', ''),
                'latest_start': activity.get('latest_start', ''),
                'latest_finish': activity.get('latest_finish', ''),
                'total_float': activity.get('total_float', 0)
            }
            
            if self.analysis_mode == 'probabilistic':
                node.update({
                    'optimistic': activity.get('optimistic', ''),
                    'most_likely': activity.get('most_likely', ''),
                    'pessimistic': activity.get('pessimistic', ''),
                    'expected_duration': activity.get('expected_duration', ''),
                    'variance': activity.get('variance', '')
                })
            
            network_data['nodes'].append(node)
        
        # Add edges (dependencies)
        for activity in activities:
            predecessors = activity.get('predecessors', [])
            for pred in predecessors:
                edge = {
                    'from': pred,
                    'to': activity.get('id', ''),
                    'critical': activity.get('critical', False)
                }
                network_data['edges'].append(edge)
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(network_data, file, indent=2)
    
    def _export_graphml(self, filename):
        """Export network data as GraphML"""
        # Simple GraphML export
        activities = self.results_data.get('activities', [])
        
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
            file.write('  <key id="name" for="node" attr.name="name" attr.type="string"/>\n')
            file.write('  <key id="duration" for="node" attr.name="duration" attr.type="double"/>\n')
            file.write('  <key id="critical" for="node" attr.name="critical" attr.type="boolean"/>\n')
            file.write('  <graph id="project_network" edgedefault="directed">\n')
            
            # Write nodes
            for activity in activities:
                file.write(f'    <node id="{activity.get("id", "")}">\n')
                file.write(f'      <data key="name">{activity.get("name", "")}</data>\n')
                file.write(f'      <data key="duration">{activity.get("duration", 0)}</data>\n')
                file.write(f'      <data key="critical">{"true" if activity.get("critical", False) else "false"}</data>\n')
                file.write('    </node>\n')
            
            # Write edges
            edge_id = 0
            for activity in activities:
                predecessors = activity.get('predecessors', [])
                for pred in predecessors:
                    file.write(f'    <edge id="e{edge_id}" source="{pred}" target="{activity.get("id", "")}">\n')
                    file.write('    </edge>\n')
                    edge_id += 1
            
            file.write('  </graph>\n')
            file.write('</graphml>\n')
