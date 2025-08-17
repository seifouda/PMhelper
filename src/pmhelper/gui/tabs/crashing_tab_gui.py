"""
Crashing Tab GUI Components

Contains all GUI and visualization logic for the Crashing tab.
All references to 'enhanced' have been removed.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any
import matplotlib.backends.backend_agg as agg
from PIL import Image, ImageTk
from .project_crashing_core import (
    ProjectCrashing, RCPSProjectCrashing, CrashingStrategy, OptimizationObjective, CrashingResult,
    compare_crashing_results, generate_crashing_report
)
from pmhelper.core.crashing_visualization import draw_network_diagram_on_ax, draw_network_diagram_on_ax_small

class CrashingTabGUIManager:
    def run_crashing(self):
        """
        Run the project crashing analysis using the selected parameters.
        Collects input, runs analysis, and updates results/visualization.
        """
        # 1. Collect input parameters from UI
        try:
            target_duration = int(round(float(self.target_duration_var.get())))
        except ValueError:
            messagebox.showerror("Input Error", "Target Duration must be an integer.")
            return

        try:
            strategy = CrashingStrategy(self.strategy_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Invalid strategy selected.")
            return

        try:
            objective = OptimizationObjective(self.objective_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Invalid objective selected.")
            return

        max_budget = self.budget_var.get()
        try:
            max_budget = int(round(float(max_budget))) if max_budget else None
        except ValueError:
            messagebox.showerror("Input Error", "Max Budget must be an integer or blank.")
            return

        max_iterations = 300  # Fixed as per requirements

        # 2. Retrieve project data (base_analyzer) from main app
        # Try current_analyzer (preferred), fallback to base_analyzer
        base_analyzer = getattr(self.app, "current_analyzer", None)
        if base_analyzer is None:
            base_analyzer = getattr(self.app, "base_analyzer", None)
        if base_analyzer is None:
            messagebox.showerror("Data Error", "No project data loaded.")
            print("[DEBUG] No project data loaded. self.app:", self.app)
            return
        # Debug: print input data summary
        print("[DEBUG] base_analyzer:", base_analyzer)
        if hasattr(base_analyzer, 'activities'):
            print("[DEBUG] base_analyzer.activities:", getattr(base_analyzer, 'activities'))
        if hasattr(base_analyzer, 'graph'):
            print("[DEBUG] base_analyzer.graph nodes:", getattr(base_analyzer, 'graph').nodes())

        # 3. Instantiate ProjectCrashing and run analysis
        crashing_engine = ProjectCrashing(base_analyzer)
        if hasattr(crashing_engine, "run"):
            result = crashing_engine.run(
                target_duration=target_duration,
                strategy=strategy,
                objective=objective,
                max_budget=max_budget,
                max_iterations=max_iterations
            )
        else:
            messagebox.showerror("Implementation Error", "ProjectCrashing.run() not implemented.")
            return

        # 4. Display results and update visualization
        self.display_results(result)
        self.update_visualization(result)

    def display_results(self, result):
        """
        Display the crashing analysis results in the summary, log, and metrics widgets.
        """
        if result is None:
            self.summary_text.delete('1.0', tk.END)
            self.summary_text.insert('1.0', "No results to display.")
            return
        report = generate_crashing_report(result)
        if not isinstance(report, str):
            report = str(report) if report is not None else "No report generated."
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', report)
        # Log and metrics (stub, expand as needed)
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert('1.0', str(result.crash_log))
        self.metrics_text.delete('1.0', tk.END)
        self.metrics_text.insert('1.0', str(result.efficiency_metrics))

    # def update_visualization(self, result):
    #     """Update the matplotlib plots with the new crashing analysis results."""
    #     # Clear previous step data
    #     self.step_graphs = []
        
    #     print(f"[DEBUG] Crashing result: {result}")
    #     print(f"[DEBUG] Crash log: {getattr(result, 'crash_log', 'No crash_log')}")
        
    #     if result and hasattr(result, 'crash_log') and result.crash_log:
    #         # Extract step graphs from crash_log
    #         for i, step_data in enumerate(result.crash_log):
    #             step_num = i
    #             activity = step_data.get('activity', 'Unknown') if isinstance(step_data, dict) else 'Unknown'
    #             new_duration = step_data.get('new_duration', 0) if isinstance(step_data, dict) else 0
    #             G_step = step_data.get('graph', None) if isinstance(step_data, dict) else None
                
    #             if G_step:
    #                 self.step_graphs.append((step_num, activity, new_duration, G_step))
        
    #     print(f"[DEBUG] Step graphs populated: {len(self.step_graphs)}")
        
    #     # Update navigation controls
    #     self.total_steps = len(self.step_graphs)
    #     self.step_select_spinbox.config(to=max(0, self.total_steps-1))
        
    #     # Show first step if available
    #     if self.step_graphs:
    #         self.show_step(0)
    #     else:
    #         # Clear visualization frame
    #         for widget in self.step_display_frame.winfo_children():
    #             widget.destroy()
    #         # Show "No visualization data" message
    #         tk.Label(self.step_display_frame, text="No visualization data available").pack()

    # def update_visualization(self, result):
    #     """Update the matplotlib plots with the new crashing analysis results."""
    #     # Clear previous step data
    #     self.step_graphs = []
        
    #     print(f"[DEBUG] Crashing result: {result}")
    #     print(f"[DEBUG] Crash log: {getattr(result, 'crash_log', 'No crash_log')}")
        
    #     # Try to get a base project graph from the application/analyzer to synthesize step graphs
    #     base_graph = None
    #     base_analyzer = getattr(self.app, "current_analyzer", None) or getattr(self.app, "base_analyzer", None)
    #     if base_analyzer is not None and hasattr(base_analyzer, 'graph'):
    #         try:
    #             base_graph = getattr(base_analyzer, 'graph')
    #         except Exception:
    #             base_graph = None
        
    #     # DEBUG: inspect base_graph and node labels/types
    #     print(f"[DEBUG] base_graph is None? {base_graph is None}")
    #     if base_graph is not None:
    #         try:
    #             nodes_list = list(base_graph.nodes())
    #             print(f"[DEBUG] base_graph type: {type(base_graph)}, nodes_count: {len(nodes_list)}")
    #             print(f"[DEBUG] base_graph nodes repr: {[repr(n) for n in nodes_list]}")
    #             # show types of the first few node labels
    #             print(f"[DEBUG] base_graph node types sample: {[type(n) for n in nodes_list[:10]]}")
    #         except Exception as _e:
    #             print(f"[DEBUG] Error inspecting base_graph nodes: {_e}")
        
    #     if result and hasattr(result, 'crash_log') and result.crash_log:
    #         # Extract step graphs from crash_log; if an entry lacks a 'graph' key, synthesize one
    #         for i, step_data in enumerate(result.crash_log):
    #             step_num = i
    #             activity = step_data.get('activity', 'Unknown') if isinstance(step_data, dict) else 'Unknown'
    #             # prefer explicit new_duration, fallback to 'duration' key in crash_log entry
    #             new_duration = step_data.get('new_duration', None) if isinstance(step_data, dict) else None
    #             if new_duration is None:
    #                 new_duration = step_data.get('duration', None) if isinstance(step_data, dict) else None
    #             G_step = step_data.get('graph', None) if isinstance(step_data, dict) else None
                
    #             # Synthesize a graph for visualization when none provided, using base_graph as template
    #             if G_step is None and base_graph is not None:
    #                 try:
    #                     G_step = base_graph.copy()
    #                     # Apply duration update for the crashed activity if present
    #                     if activity in G_step.nodes():
    #                         if new_duration is not None:
    #                             G_step.nodes[activity]['duration'] = new_duration
    #                     # Mark critical nodes if crash log provides a critical_path
    #                     cp = step_data.get('critical_path', None) if isinstance(step_data, dict) else None
    #                     if cp:
    #                         for n in G_step.nodes():
    #                             # float == 0 indicates critical
    #                             G_step.nodes[n]['float'] = 0 if n in cp else G_step.nodes[n].get('float', 1)
    #                     else:
    #                         # Ensure nodes have a 'float' attribute (non-critical default)
    #                         for n in G_step.nodes():
    #                             if 'float' not in G_step.nodes[n]:
    #                                 G_step.nodes[n]['float'] = G_step.nodes[n].get('float', 1)
    #                 except Exception as e:
    #                     print(f"[DEBUG] Failed to synthesize G_step for step {step_num}: {e}")
    #                     G_step = None
                
    #             if G_step:
    #                 self.step_graphs.append((step_num, activity, new_duration if new_duration is not None else 0, G_step))
        
    #     print(f"[DEBUG] Step graphs populated: {len(self.step_graphs)}")
        
    #     # Update navigation controls
    #     self.total_steps = len(self.step_graphs)
    #     self.step_select_spinbox.config(to=max(0, self.total_steps-1))
        
    #     # Show first step if available
    #     if self.step_graphs:
    #         self.show_step(0)
    #     else:
    #         # Clear visualization frame
    #         for widget in self.step_display_frame.winfo_children():
    #             widget.destroy()
    #         # Show "No visualization data" message
    #         tk.Label(self.step_display_frame, text="No visualization data available").pack()

    
    
    # def update_visualization(self, result):
    #     """Update the matplotlib plots with the new crashing analysis results."""
    #     # Clear previous step data
    #     self.step_graphs = []
        
    #     print(f"[DEBUG] Crashing result: {result}")
    #     print(f"[DEBUG] Crash log: {getattr(result, 'crash_log', 'No crash_log')}")
        
    #     # Prefer any graph produced by the crashing run (CrashingResult.crashed_graph),
    #     # then fall back to analyzer.graph if available.
    #     base_graph = None
    #     if hasattr(result, 'crashed_graph') and getattr(result, 'crashed_graph', None) is not None:
    #         base_graph = getattr(result, 'crashed_graph')
    #         print("[DEBUG] Using result.crashed_graph for visualization")
    #     else:
    #         base_analyzer = getattr(self.app, "current_analyzer", None) or getattr(self.app, "base_analyzer", None)
    #         if base_analyzer is not None:
    #             if hasattr(base_analyzer, 'graph'):
    #                 try:
    #                     base_graph = getattr(base_analyzer, 'graph')
    #                 except Exception:
    #                     base_graph = None
    #             elif hasattr(base_analyzer, 'crashed_graph'):
    #                 base_graph = getattr(base_analyzer, 'crashed_graph')
        
    #     print(f"[DEBUG] base_graph is None? {base_graph is None}")
    #     if base_graph is not None:
    #         try:
    #             nodes_list = list(base_graph.nodes())
    #             print(f"[DEBUG] base_graph type: {type(base_graph)}, nodes_count: {len(nodes_list)}")
    #             print(f"[DEBUG] base_graph nodes repr: {[repr(n) for n in nodes_list]}")
    #             print(f"[DEBUG] base_graph node types sample: {[type(n) for n in nodes_list[:10]]}")
    #         except Exception as _e:
    #             print(f"[DEBUG] Error inspecting base_graph nodes: {_e}")
        
    #     if result and hasattr(result, 'crash_log') and result.crash_log:
    #         # Extract step graphs from crash_log; if an entry lacks a 'graph' key, synthesize one
    #         for i, step_data in enumerate(result.crash_log):
    #             step_num = i
    #             activity = step_data.get('activity', 'Unknown') if isinstance(step_data, dict) else 'Unknown'
    #             new_duration = step_data.get('new_duration', None) if isinstance(step_data, dict) else None
    #             if new_duration is None:
    #                 new_duration = step_data.get('duration', None) if isinstance(step_data, dict) else None
    #             G_step = step_data.get('graph', None) if isinstance(step_data, dict) else None
                
    #             # Use base_graph (prefer result.crashed_graph) to synthesize step diagram when needed
    #             if G_step is None and base_graph is not None:
    #                 try:
    #                     G_step = base_graph.copy()
    #                     # Apply duration update for the crashed activity if present
    #                     if activity in G_step.nodes():
    #                         if new_duration is not None:
    #                             G_step.nodes[activity]['duration'] = new_duration
    #                     # Mark critical nodes if crash log provides a critical_path
    #                     cp = step_data.get('critical_path', None) if isinstance(step_data, dict) else None
    #                     if cp:
    #                         for n in G_step.nodes():
    #                             G_step.nodes[n]['float'] = 0 if n in cp else G_step.nodes[n].get('float', 1)
    #                     else:
    #                         for n in G_step.nodes():
    #                             if 'float' not in G_step.nodes[n]:
    #                                 G_step.nodes[n]['float'] = G_step.nodes[n].get('float', 1)
    #                 except Exception as e:
    #                     print(f"[DEBUG] Failed to synthesize G_step for step {step_num}: {e}")
    #                     G_step = None
                
    #             if G_step:
    #                 self.step_graphs.append((step_num, activity, new_duration if new_duration is not None else 0, G_step))
        
    #     print(f"[DEBUG] Step graphs populated: {len(self.step_graphs)}")
        
    #     # Update navigation controls
    #     self.total_steps = len(self.step_graphs)
    #     self.step_select_spinbox.config(to=max(0, self.total_steps-1))
        
    #     # Show first step if available
    #     if self.step_graphs:
    #         self.show_step(0)
    #     else:
    #         # Clear visualization frame
    #         for widget in self.step_display_frame.winfo_children():
    #             widget.destroy()
    #         # Show "No visualization data" message
    #         tk.Label(self.step_display_frame, text="No visualization data available").pack()
    
    
    def update_visualization(self, result):
        """Update the matplotlib plots with the new crashing analysis results."""
        # Clear previous step data
        self.step_graphs = []
        
        print(f"[DEBUG] Crashing result: {result}")
        print(f"[DEBUG] Crash log: {getattr(result, 'crash_log', 'No crash_log')}")
        
        # Use the ORIGINAL network from base_analyzer for step visualization,
        # NOT the crashed network, to ensure initial state shows uncrashed network
        base_graph = None
        base_analyzer = getattr(self.app, "current_analyzer", None) or getattr(self.app, "base_analyzer", None)
        if base_analyzer is not None:
            print(f"[DEBUG] base_analyzer type: {type(base_analyzer)}")
            print(f"[DEBUG] base_analyzer attributes: {dir(base_analyzer)}")
            
            # Try different possible attribute names for the original network
            for attr_name in ['graph', 'G', 'network', 'original_graph', 'build_network']:
                if hasattr(base_analyzer, attr_name):
                    try:
                        attr_value = getattr(base_analyzer, attr_name)
                        if attr_value is not None:
                            # If it's a method, try calling it
                            if callable(attr_value):
                                if hasattr(base_analyzer, 'activities'):
                                    base_graph = attr_value(base_analyzer.activities)
                                    print(f"[DEBUG] Using base_analyzer.{attr_name}(activities) for visualization")
                                else:
                                    base_graph = attr_value()
                                    print(f"[DEBUG] Using base_analyzer.{attr_name}() for visualization")
                            else:
                                base_graph = attr_value
                                print(f"[DEBUG] Using base_analyzer.{attr_name} for visualization")
                            break
                    except Exception as e:
                        print(f"[DEBUG] Failed to get {attr_name} from base_analyzer: {e}")
                        continue
            
            # Final fallback: check if we can build network from activities
            if base_graph is None and hasattr(base_analyzer, 'activities'):
                try:
                    # Try to build network using the same logic as the analyzer
                    if hasattr(base_analyzer, 'build_network'):
                        base_graph = base_analyzer.build_network(base_analyzer.activities)
                        print("[DEBUG] Built network using base_analyzer.build_network(activities)")
                    elif hasattr(base_analyzer, '__class__') and hasattr(base_analyzer.__class__, 'build_network'):
                        base_graph = base_analyzer.__class__.build_network(base_analyzer.activities)
                        print("[DEBUG] Built network using analyzer class build_network method")
                except Exception as e:
                    print(f"[DEBUG] Failed to build network from activities: {e}")
        
        # Last resort: use the crashed graph from result if no original found
        if base_graph is None and hasattr(result, 'crashed_graph') and getattr(result, 'crashed_graph', None) is not None:
            base_graph = getattr(result, 'crashed_graph')
            print("[DEBUG] Fallback to result.crashed_graph (will show wrong initial state)")
        
        print(f"[DEBUG] base_graph is None? {base_graph is None}")
        if base_graph is not None:
            try:
                nodes_list = list(base_graph.nodes())
                print(f"[DEBUG] base_graph type: {type(base_graph)}, nodes_count: {len(nodes_list)}")
                print(f"[DEBUG] base_graph nodes repr: {[repr(n) for n in nodes_list]}")
                print(f"[DEBUG] base_graph node types sample: {[type(n) for n in nodes_list[:10]]}")
            except Exception as _e:
                print(f"[DEBUG] Error inspecting base_graph nodes: {_e}")
        
        if result and hasattr(result, 'crash_log') and result.crash_log:
            # Step 0: Add the original, uncrashed network state
            if base_graph is not None:
                original_G = base_graph.copy()
                self.step_graphs.append((0, 'Initial', None, original_G))
                print("[DEBUG] Added step 0: Initial network state")
            
            # Steps 1-N: Create network state after each crash step
            # Each step shows the cumulative result of all crashes up to that point
            for i, step_data in enumerate(result.crash_log):
                step_num = i + 1  # Navigation step numbers start from 1
                activity = step_data.get('activity', 'Unknown') if isinstance(step_data, dict) else 'Unknown'
                new_duration = step_data.get('new_duration', None) if isinstance(step_data, dict) else None
                if new_duration is None:
                    new_duration = step_data.get('duration', None) if isinstance(step_data, dict) else None
                
                # Always build from the original graph and apply all crashes up to this step
                if base_graph is not None:
                    try:
                        G_step = base_graph.copy()
                        
                        # Apply ALL crashes from crash_log[0] to crash_log[i] (inclusive)
                        for j in range(i + 1):
                            crash_entry = result.crash_log[j]
                            if isinstance(crash_entry, dict):
                                crashed_activity = crash_entry.get('activity', None)
                                crashed_duration = crash_entry.get('new_duration', None) or crash_entry.get('duration', None)
                                if crashed_activity and crashed_activity in G_step.nodes() and crashed_duration is not None:
                                    G_step.nodes[crashed_activity]['duration'] = crashed_duration
                                    print(f"[DEBUG] Step {step_num}: Applied crash {j+1} - {crashed_activity} to duration {crashed_duration}")
                        
                        # Recalculate CPM for this step to get correct float values
                        network_builder = getattr(getattr(self.app, "current_analyzer", None) or getattr(self.app, "base_analyzer", None), 'network_builder', None)
                        if network_builder:
                            G_step = network_builder.forward_pass(G_step)
                            G_step = network_builder.backward_pass(G_step)
                            G_step = network_builder.calculate_float(G_step)
                        
                        # Use critical path from crash log if available, otherwise calculate
                        cp = step_data.get('critical_path', None) if isinstance(step_data, dict) else None
                        if cp:
                            for n in G_step.nodes():
                                G_step.nodes[n]['float'] = 0 if n in cp else G_step.nodes[n].get('float', 1)
                        
                        self.step_graphs.append((step_num, activity, new_duration if new_duration is not None else 0, G_step))
                        print(f"[DEBUG] Added step {step_num}: {activity} crashed to {new_duration}")
                        
                    except Exception as e:
                        print(f"[DEBUG] Failed to synthesize G_step for step {step_num}: {e}")
                        continue
        
        print(f"[DEBUG] Step graphs populated: {len(self.step_graphs)}")
        
        # Update navigation controls
        self.total_steps = len(self.step_graphs)
        self.step_select_spinbox.config(to=max(0, self.total_steps-1))
        
        # Show first step if available
        if self.step_graphs:
            self.show_step(0)
        else:
            # Clear visualization frame
            for widget in self.step_display_frame.winfo_children():
                widget.destroy()
            # Show "No visualization data" message
            tk.Label(self.step_display_frame, text="No visualization data available").pack()
    
    def export_results(self):
        """
        Export the current crashing results to a file.
        TODO: Implement export logic.
        """
        messagebox.showinfo("Export Results", "Export functionality would run here.")

    def clear_results(self):
        """
        Clear all displayed results and reset the UI.
        TODO: Implement clear logic.
        """
        self.summary_text.delete('1.0', tk.END)
        self.log_text.delete('1.0', tk.END)
        self.metrics_text.delete('1.0', tk.END)
    """
    Manager for Project Crashing GUI Components
    Handles all controls, result displays, and visualizations for the Crashing tab.
    """
    def __init__(self, tab_instance, app_instance):
        self.tab = tab_instance
        self.app = app_instance
        self.engine = None
        self.rcps_engine = None
        self.current_results = []
        self.comparison_window = None
        # Build the interface when the manager is initialized
        self.build_interface()

    def build_interface(self):
        """
        Build all controls, results, and visualization sections for the Crashing tab.
        """
        # Controls Section
        controls_frame = ttk.LabelFrame(self.tab, text="Crashing Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        params_frame = ttk.Frame(controls_frame)
        params_frame.pack(fill=tk.X, padx=5, pady=5)

        # Row 0: Target Duration, Strategy, Objective, Max Budget, Buttons
        ttk.Label(params_frame, text="Target Duration:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.target_duration_var = tk.StringVar(value="25")
        ttk.Entry(params_frame, textvariable=self.target_duration_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(params_frame, text="Strategy:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.strategy_var = tk.StringVar(value=CrashingStrategy.LOWEST_COST.value)
        strategy_combo = ttk.Combobox(params_frame, textvariable=self.strategy_var, width=15)
        strategy_combo['values'] = [s.value for s in CrashingStrategy]
        strategy_combo.grid(row=0, column=3, padx=5, pady=2)
        strategy_combo.state(['readonly'])

        ttk.Label(params_frame, text="Objective:").grid(row=0, column=4, padx=5, pady=2, sticky="w")
        self.objective_var = tk.StringVar(value=OptimizationObjective.MINIMIZE_COST.value)
        objective_combo = ttk.Combobox(params_frame, textvariable=self.objective_var, width=15)
        objective_combo['values'] = [o.value for o in OptimizationObjective]
        objective_combo.grid(row=0, column=5, padx=5, pady=2)
        objective_combo.state(['readonly'])

        ttk.Label(params_frame, text="Max Budget:").grid(row=0, column=6, padx=5, pady=2, sticky="w")
        self.budget_var = tk.StringVar(value="")
        ttk.Entry(params_frame, textvariable=self.budget_var, width=10).grid(row=0, column=7, padx=5, pady=2)

        # Set max_iterations to 300 (no advanced parameters UI)
        self.max_iterations_var = tk.StringVar(value="300")

        # Run Crashing button next to input fields
        ttk.Button(
            params_frame,
            text="Run Crashing",
            command=self.run_crashing
        ).grid(row=0, column=8, padx=10, pady=2, sticky="e")

        # Add a stretchable empty column to push right buttons to the far end
        params_frame.grid_columnconfigure(9, weight=1)

        # Frame for far right buttons
        right_buttons_frame = ttk.Frame(params_frame)
        right_buttons_frame.grid(row=0, column=10, padx=0, pady=2, sticky="e")

        ttk.Button(
            right_buttons_frame,
            text="Export Results",
            command=self.export_results
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            right_buttons_frame,
            text="Clear Results",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=2)

        # Results Section
        results_frame = ttk.LabelFrame(self.tab, text="Crashing Results")
        results_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)

        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.X, expand=False, pady=5)

        summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(summary_frame, text="Summary")
        self.summary_text = scrolledtext.ScrolledText(
            summary_frame, wrap=tk.WORD, height=6, width=80
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        log_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(log_frame, text="Detailed Log")
        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, height=6, width=80
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        metrics_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(metrics_frame, text="Metrics")
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame, wrap=tk.WORD, height=6, width=80
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Visualization Section
        viz_frame = ttk.LabelFrame(self.tab, text="Crashing Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Removed old chart code. Network diagram will be shown in step_display_frame only.
        # --- Step Visualization State and Navigation ---
        self.step_graphs = []  # List of (step_num, activity, new_duration, G_step)
        self.current_step = 0
        self.total_steps = 0
        # Navigation controls
        nav_frame = ttk.Frame(viz_frame)
        nav_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(nav_frame, text="◀◀ First", command=self.show_first_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="◀ Previous", command=self.show_previous_step).pack(side=tk.LEFT, padx=2)
        self.step_info_label = ttk.Label(nav_frame, text="Step 0 of 0")
        self.step_info_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="Next ▶", command=self.show_next_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Last ▶▶", command=self.show_last_step).pack(side=tk.LEFT, padx=2)
        ttk.Label(nav_frame, text="Go to step:").pack(side=tk.LEFT, padx=(20, 5))
        self.step_select_var = tk.StringVar(value="0")
        self.step_select_spinbox = ttk.Spinbox(nav_frame, from_=0, to=0, width=5,
                            textvariable=self.step_select_var,
                            command=self.show_selected_step)
        self.step_select_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Show All Steps", command=self.show_all_steps_grid).pack(side=tk.RIGHT, padx=2)
        
        self.step_display_frame = ttk.Frame(viz_frame)
        self.step_display_frame.pack(fill=tk.BOTH, expand=True)

    # --- CPM Crashing Step Visualization Integration ---
    def _draw_network_diagram_on_ax(self, ax, G):
        import networkx as nx
        import matplotlib.pyplot as plt
        pos = {}
        generations = list(nx.topological_generations(G))
        for i, gen in enumerate(generations):
            sorted_gen = sorted(gen)
            for j, node in enumerate(sorted_gen):
                y_pos = (j - len(sorted_gen) / 2 + 0.5) * 4
                pos[node] = (i * 3, y_pos)
        node_radius = 0.4
        for u, v in G.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx = x2 - x1
            dy = y2 - y1
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
                start_x = x1 + node_radius * dx_norm
                start_y = y1 + node_radius * dy_norm
                end_x = x2 - node_radius * dx_norm
                end_y = y2 - node_radius * dy_norm
                ax.annotate("", xy=(end_x, end_y), xytext=(start_x, start_y),
                            arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
        critical_activities = [node for node in G.nodes() if G.nodes[node].get('float', None) == 0 and node not in ['START', 'END']]
        for node in G.nodes():
            x, y = pos[node]
            if node == 'START':
                color = 'lightgreen'
            elif node == 'END':
                color = 'orange'
            elif node in critical_activities:
                color = 'red'
            else:
                color = 'lightblue'
            circle = plt.Circle((x, y), node_radius, fill=True, color=color, alpha=0.7,
                                edgecolor='black', linewidth=1.5)
            ax.add_patch(circle)
            if node in ['START', 'END']:
                display_text = 'Start' if node == 'START' else 'End'
                ax.text(x, y, display_text, ha='center', va='center',
                        fontsize=10, fontweight='bold')
            else:
                ax.plot([x - node_radius, x + node_radius], [y, y],
                        color='black', linewidth=1.2)
                ax.text(x, y + node_radius / 2, node, ha='center', va='center',
                        fontsize=10, fontweight='bold')
                ax.text(x, y - node_radius / 2, str(G.nodes[node].get('duration', '')), ha='center', va='center', fontsize=9)
        ax.set_axis_off()
        ax.set_aspect('equal')

    def _draw_network_diagram_on_ax_small(self, ax, G):
        import networkx as nx
        import matplotlib.pyplot as plt
        pos = {}
        generations = list(nx.topological_generations(G))
        for i, gen in enumerate(generations):
            sorted_gen = sorted(gen)
            for j, node in enumerate(sorted_gen):
                y_pos = (j - len(sorted_gen) / 2 + 0.5) * 2
                pos[node] = (i * 2, y_pos)
        node_radius = 0.3
        for u, v in G.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx = x2 - x1
            dy = y2 - y1
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
                start_x = x1 + node_radius * dx_norm
                start_y = y1 + node_radius * dy_norm
                end_x = x2 - node_radius * dx_norm
                end_y = y2 - node_radius * dy_norm
                ax.annotate("", xy=(end_x, end_y), xytext=(start_x, start_y),
                            arrowprops=dict(arrowstyle="->", color="black", lw=1))
        critical_activities = [node for node in G.nodes() if G.nodes[node].get('float', None) == 0 and node not in ['START', 'END']]
        for node in G.nodes():
            x, y = pos[node]
            if node == 'START':
                color = 'lightgreen'
            elif node == 'END':
                color = 'orange'
            elif node in critical_activities:
                color = 'red'
            else:
                color = 'lightblue'
            circle = plt.Circle((x, y), node_radius, fill=True, color=color, alpha=0.7,
                                edgecolor='black', linewidth=1)
            ax.add_patch(circle)
            if node in ['START', 'END']:
                display_text = 'Start' if node == 'START' else 'End'
                ax.text(x, y, display_text, ha='center', va='center',
                        fontsize=7, fontweight='bold')
            else:
                ax.plot([x - node_radius, x + node_radius], [y, y],
                        color='black', linewidth=0.8)
                ax.text(x, y + node_radius / 2, node, ha='center', va='center',
                        fontsize=7, fontweight='bold')
                ax.text(x, y - node_radius / 2, str(G.nodes[node].get('duration', '')), ha='center', va='center', fontsize=6)
        ax.set_axis_off()
        ax.set_aspect('equal')

    def show_step(self, step_index):
        if 0 <= step_index < len(self.step_graphs):
            self.current_step = step_index
            step_num, activity, new_duration, G_step = self.step_graphs[step_index]
            for widget in self.step_display_frame.winfo_children():
                widget.destroy()
            fig = plt.Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            if step_num == 0:
                draw_network_diagram_on_ax(ax, G_step, initial=True)
                ax.set_title("Initial Network", fontsize=14, fontweight='bold')
            else:
                draw_network_diagram_on_ax(ax, G_step)
                ax.set_title(f"Step {step_num}: Activity {activity} crashed to {new_duration}", fontsize=14, fontweight='bold')
            canvas = FigureCanvasTkAgg(fig, self.step_display_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()
            self.step_info_label.config(text=f"Step {step_index} of {self.total_steps-1}")
            self.step_select_var.set(str(step_index))

    def show_first_step(self):
        self.show_step(0)

    def show_previous_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def show_next_step(self):
        if self.current_step < self.total_steps - 1:
            self.show_step(self.current_step + 1)

    def show_last_step(self):
        if self.total_steps > 0:
            self.show_step(self.total_steps - 1)

    def show_selected_step(self):
        try:
            step_index = int(self.step_select_var.get())
            self.show_step(step_index)
        except ValueError:
            pass

    def show_all_steps_grid(self):
        if not self.step_graphs:
            messagebox.showwarning("Warning", "No steps to display.")
            return
        grid_window = tk.Toplevel(self.tab)
        grid_window.title("All Crashing Steps")
        grid_window.geometry("1200x800")
        canvas = tk.Canvas(grid_window)
        scrollbar = ttk.Scrollbar(grid_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        cols = 3
        step_images = []
        for idx, (step_num, activity, new_duration, G_step) in enumerate(self.step_graphs):
            fig = plt.Figure(figsize=(4, 3))
            ax = fig.add_subplot(111)
            draw_network_diagram_on_ax_small(ax, G_step)
            if step_num == 0:
                ax.set_title("Initial Network", fontsize=10, fontweight='bold')
            else:
                ax.set_title(f"Step {step_num}: {activity} → {new_duration}", fontsize=10, fontweight='bold')
            canvas_agg = agg.FigureCanvasAgg(fig)
            canvas_agg.draw()
            buf = canvas_agg.buffer_rgba()
            img = Image.frombuffer("RGBA", canvas_agg.get_width_height(), buf, "raw", "RGBA", 0, 1)
            tk_img = ImageTk.PhotoImage(img)
            step_images.append(tk_img)
            row = idx // cols
            col = idx % cols
            lbl = tk.Label(scrollable_frame, image=tk_img)
            lbl.grid(row=row, column=col, padx=5, pady=5)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        grid_window.step_images = step_images
