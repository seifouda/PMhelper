#!/usr/bin/env python3
"""
PERT Diagram Tab Module

Displays professional PERT network diagrams with rectangle-semicircle nodes,
showing ID, Duration, ES, EF, LS, LF in 6 sections, with critical path highlighting.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
from pathlib import Path
import textwrap

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
        """Create matplotlib plot area and control widgets"""
        plot_frame = ttk.Frame(self.main_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create toolbar frame and pack at the bottom
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create canvas frame and pack above toolbar
        canvas_frame = ttk.Frame(plot_frame)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(14, 10), dpi=100)
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create and pack the toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        # Initialize with empty plot
        self.create_empty_plot()

        # Display option variables
        self.highlight_critical = tk.BooleanVar(value=True)
        self.show_float = tk.BooleanVar(value=False)

        # Create display options frame
        options_frame = ttk.LabelFrame(control_frame, text="Display Options", padding="5")
        options_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Checkboxes for display options
        ttk.Checkbutton(options_frame, text="Highlight Critical Path", 
                variable=self.highlight_critical, 
                command=self.update_diagram).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Show Float Values", 
                variable=self.show_float, 
                command=self.update_diagram).pack(side=tk.LEFT, padx=5)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(button_frame, text="Save Image", 
            command=self.save_diagram).pack(side=tk.LEFT, padx=5)
    
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
        
        try:
            # Clear the figure completely
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            
            # Extract activities and critical activities from results_data
            activities = self.results_data.get('activities', [])
            critical_activities = self.results_data.get('critical_activities', [])
            
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
                title = f"PERT Network Diagram\nScheduling Duration: {project_duration}, Expected Duration: {expected_duration}"
            else:
                title = f"PERT Network Diagram\nProject Duration: {project_duration}"
            
            self.ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Adjust layout and draw
            self.figure.tight_layout()
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
                    duration = activity['expected']  # Integer expected duration
                elif 'expected_duration' in activity:
                    duration = int(activity['expected_duration'])  # Round for display
            
            # ENSURE float value is captured from multiple possible field names
            float_value = activity.get('float', activity.get('total_float', activity.get('Float', 0)))
            
            # Get timing values
            ES = activity.get('ES', activity.get('earliest_start', 0))
            EF = activity.get('EF', activity.get('earliest_finish', duration))
            LS = activity.get('LS', activity.get('latest_start', 0))
            LF = activity.get('LF', activity.get('latest_finish', duration))
            
            G.add_node(activity_id, 
                    duration=duration,
                    critical=activity.get('critical', False),
                    float=float_value,
                    ES=ES,
                    EF=EF,
                    LS=LS,
                    LF=LF,
                    activity=activity.get('activity', activity.get('name', '')),
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
        """Add START and END nodes to graph - COPIED FROM NetworkTab"""
        # Find nodes with no predecessors (start activities)
        start_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]
        
        if start_nodes and 'START' not in G.nodes():
            G.add_node('START', duration=0, activity='Start', ES=0, EF=0, LS=0, LF=0, float=0)
            for node in start_nodes:
                G.add_edge('START', node)
        
        # Find nodes with no successors (end activities)
        end_nodes = [node for node in G.nodes() if G.out_degree(node) == 0 and node != 'START']
        
        if end_nodes and 'END' not in G.nodes():
            # Calculate END node timing from predecessors
            max_ef = max([G.nodes[node]['EF'] for node in end_nodes])
            G.add_node('END', duration=0, activity='End', ES=max_ef, EF=max_ef, LS=max_ef, LF=max_ef, float=0)
            for node in end_nodes:
                G.add_edge(node, 'END')
    
    def draw_pert_network_diagram(self, G, critical_activities):
        """Draw professional PERT network diagram with rectangle-semicircle nodes - BASED ON cmp_app.py"""
        self.ax.clear()
        
        if not G.nodes():
            self.ax.text(0.5, 0.5, 'No network data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # 1. Create hierarchical layout
        pos = self.create_hierarchical_layout(G)
        
        # 2. Draw edges with arrows
        self.draw_network_edges(G, pos)
        
        # 3. Draw nodes with rectangle-semicircle format
        self.draw_pert_nodes(G, pos, critical_activities)
        
        # 4. Add legend
        self.add_network_legend()
        
        # 5. Apply display options
        self.apply_display_options(G, pos)
        
        # 6. Add node format legend
        self.figure.text(0.01, 0.01, "Node Format:", fontsize=9)
        self.figure.text(0.07, 0.01, "ID   | ES | EF\nDur | LS | LF", fontsize=9)
        
        self.ax.set_title("PERT Network Diagram")
        self.ax.axis('equal')
        self.ax.axis('off')
        self.canvas.draw()
    
    def create_hierarchical_layout(self, G):
        """Create hierarchical layout with increased spacing for larger nodes"""
        pos = {}
        generations = list(nx.topological_generations(G))
        
        for i, gen in enumerate(generations):
            sorted_gen = sorted(gen)
            for j, node in enumerate(sorted_gen):
                # INCREASED spacing for larger nodes
                y_pos = (j - len(sorted_gen) / 2 + 0.5) * 4  # Increased from 3 to 4
                pos[node] = (i * 5, y_pos)  # Increased from 4 to 5
        
        return pos
    
    def draw_network_edges(self, G, pos):
        """Draw edges with proper arrows - UPDATED for larger nodes"""
        # UPDATED node size parameters for larger nodes
        width = 1.8  # Increased from 1.2
        height = width * 2/3
        semicircle_width = width/3
        square_width = width * 2/3
        node_radius = 0.4  # Increased from 0.3
        
        for u, v in G.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            
            # Calculate starting and ending points based on node type
            if u in ['START', 'END']:
                # For START/END nodes (circles), start from edge
                dx = x2 - x1
                dy = y2 - y1
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > 0:
                    dx_norm = dx / distance
                    dy_norm = dy / distance
                    start_x = x1 + node_radius * dx_norm
                    start_y = y1 + node_radius * dy_norm
                else:
                    start_x = x1
                    start_y = y1
            else:
                # For regular nodes, start from far right
                start_x = x1 + square_width / 2
                start_y = y1
            
            if v in ['START', 'END']:
                # For START/END nodes (circles), end at edge
                dx = x2 - x1
                dy = y2 - y1
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > 0:
                    dx_norm = dx / distance
                    dy_norm = dy / distance
                    end_x = x2 - node_radius * dx_norm
                    end_y = y2 - node_radius * dy_norm
                else:
                    end_x = x2
                    end_y = y2
            else:
                # For regular nodes, end at far left
                end_x = x2 - square_width/2 - semicircle_width
                end_y = y2

            # Draw arrow
            self.ax.annotate("", xy=(end_x, end_y), xytext=(start_x, start_y),
                            arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
    
    def draw_pert_nodes(self, G, pos, critical_activities):
        """Draw nodes with enlarged size and improved text positioning"""
        # ENLARGED node size parameters
        width = 2  # Increased from 1.2
        height = width * 2/3  # 1.2
        semicircle_width = width/3  # 0.6
        square_width = width * 2/3  # 1.2
        node_radius = 0.6  # Increased from 0.3
        
        for node in G.nodes():
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
                self.ax.text(x, y, display_text,
                            horizontalalignment='center', verticalalignment='center',
                            fontsize=10, fontweight='bold', zorder=5)
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
                self.ax.plot([x - square_width / 2 - semicircle_width, x + square_width / 2], [y, y],
                            color='black', linewidth=0.8, zorder=4)
                
                # Vertical divider between semicircle and square
                self.ax.plot([x - square_width / 2, x - square_width / 2], [y - height / 2, y + height / 2],
                            color='black', linewidth=0.8, zorder=5)
                
                # Vertical divider in square section
                self.ax.plot([x, x], [y - height / 2, y + height / 2],
                            color='black', linewidth=0.8, zorder=4)

                # IMPROVED text positioning for "ID | ES | EF" format
                # Top row: ID | ES | EF
                self.ax.text(x - square_width / 2 - semicircle_width / 2, y + height / 4, node,
                            horizontalalignment='center', verticalalignment='center', 
                            fontsize=9, fontweight='bold', zorder=5)
                self.ax.text(x - square_width / 4, y + height / 4, str(G.nodes[node]['ES']),
                            horizontalalignment='center', verticalalignment='center', 
                            fontsize=9, zorder=5)
                self.ax.text(x + square_width / 4, y + height / 4, str(G.nodes[node]['EF']),
                            horizontalalignment='center', verticalalignment='center', 
                            fontsize=9, zorder=5)

                # IMPROVED text positioning for "Dur | LS | LF" format
                # Bottom row: Duration | LS | LF
                self.ax.text(x - square_width / 2 - semicircle_width / 2, y - height / 4, str(G.nodes[node]['duration']),
                            horizontalalignment='center', verticalalignment='center', 
                            fontsize=9, zorder=5)
                self.ax.text(x - square_width / 4, y - height / 4, str(G.nodes[node]['LS']),
                            horizontalalignment='center', verticalalignment='center', 
                            fontsize=9, zorder=5)
                self.ax.text(x + square_width / 4, y - height / 4, str(G.nodes[node]['LF']),
                            horizontalalignment='center', verticalalignment='center', 
                            fontsize=9, zorder=5)

                # IMPROVED activity name above node with space-based wrapping
                activity_name = G.nodes[node].get('activity', '')
                if activity_name and activity_name not in ['Start', 'End']:
                    wrapped_lines = self.wrap_activity_name(activity_name)
                    
                    # Display each line separately, stacked vertically
                    line_height = 0.3
                    start_y = y + height / 2 + 0.2
                    
                    for i, line in enumerate(wrapped_lines):
                        self.ax.text(x - 0.2, start_y + (i * line_height), line,
                                    horizontalalignment='center', verticalalignment='bottom',
                                    fontsize=8, color='purple', fontweight='bold', zorder=5)
    
    def wrap_activity_name(self, text, max_chars_per_line=12):
        """Wrap activity name by character count, returns lines split for display"""
        if not text:
            return []
        return text.split()
    
    def add_network_legend(self):
        """Add simplified legend without START/END entries - COPIED FROM NetworkTab"""
        legend_elements = [
            mpatches.Patch(color='red', alpha=0.7, label='Critical Path'),
            mpatches.Patch(color='lightblue', alpha=0.7, label='Normal Activity')
        ]
        self.ax.legend(handles=legend_elements, loc='lower right')
    
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
        
        for node in G.nodes():
            if node in ['START', 'END']:
                continue  # Skip START/END nodes
            
            x, y = pos[node]
            
            # GET ACTUAL FLOAT VALUE from node data
            float_value = G.nodes[node].get('float', 0)
            
            # Handle different float value formats
            if isinstance(float_value, (int, float)):
                float_text = str(int(float_value))  # Remove decimals for cleaner display
            else:
                float_text = str(float_value)
            
            # Position BELOW the node (negative y offset)
            float_y = y - 1.2  # Changed from y + 1.0 to y - 1.2
            
            # LARGER font, NO "F" prefix, just the number
            self.ax.text(x - 0.3, float_y, float_text, ha='center', va='center',
                        fontsize=12, fontweight='bold', color='darkblue',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                 alpha=0.8, edgecolor='darkblue'))
    
    def save_diagram(self):
        """Save the current diagram to file - COPIED FROM NetworkTab"""
        if not MATPLOTLIB_AVAILABLE or not self.results_data:
            messagebox.showwarning("Warning", "No diagram to save. Please run analysis first.")
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
                messagebox.showinfo("Success", f"PERT diagram saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save diagram: {str(e)}")
    
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
