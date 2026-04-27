"""
Crashing Tab GUI Components

Contains all GUI and visualization logic for the Crashing tab.
All references to 'enhanced' have been removed.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
from PIL import Image, ImageTk
from .project_crashing_core import (
    ProjectCrashing,
    CrashingStrategy,
    OptimizationObjective,
    generate_crashing_report)
from pmhelper.core.crashing_visualization import draw_network_diagram_on_ax, draw_network_diagram_on_ax_small

# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame, WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import plotly_crashing_network, PLOTLY_AVAILABLE as _PLT_AVAIL
    _PLOTLY_EMBED = WEBVIEW2_AVAILABLE and _PLT_AVAIL
except ImportError:
    _PLOTLY_EMBED = False


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
            messagebox.showerror(
                "Input Error",
                "Target Duration must be an integer.")
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
            messagebox.showerror("Input Error",
                                 "Max Budget must be an integer or blank.")
            return

        max_crash_cost = self.max_crash_cost_var.get()
        try:
            max_crash_cost = int(round(float(max_crash_cost))
                                 ) if max_crash_cost else None
        except ValueError:
            messagebox.showerror(
                "Input Error",
                "Max Crashing Cost must be an integer or blank.")
            return

        max_normal_cost = self.max_normal_cost_var.get()
        try:
            max_normal_cost = int(
                round(float(max_normal_cost))) if max_normal_cost else None
        except ValueError:
            messagebox.showerror(
                "Input Error",
                "Max Normal Cost must be an integer or blank.")
            return

        max_iterations = 1500  # Fixed as per requirements

        # 2. Retrieve project data (base_analyzer) from main app
        # Try current_analyzer (preferred), fallback to base_analyzer
        base_analyzer = getattr(self.app, "current_analyzer", None)
        if base_analyzer is None:
            base_analyzer = getattr(self.app, "base_analyzer", None)
        if base_analyzer is None:
            messagebox.showerror("Data Error", "No project data loaded.")
            # print("[DEBUG] No project data loaded. self.app:", self.app)
            return
        # Debug: print input data summary
        # print("[DEBUG] base_analyzer:", base_analyzer)
        if hasattr(base_analyzer, 'activities'):
            # print("[DEBUG] base_analyzer.activities:", getattr(base_analyzer, 'activities', 'Not found'))
            pass
        if hasattr(base_analyzer, 'G'):
            # print("[DEBUG] base_analyzer.G nodes:", getattr(base_analyzer, 'G').nodes() if getattr(base_analyzer, 'G') else 'No graph')
            pass

        # Validate target duration against original project duration
        if hasattr(base_analyzer, 'G') and base_analyzer.G is not None:
            try:
                # Calculate original project duration using maximum EF value
                ef_values = [
                    base_analyzer.G.nodes[node].get(
                        'EF', 0) for node in base_analyzer.G.nodes()]
                # Check if analysis has been run (EF values should be > 0 for
                # at least one node)
                if not any(ef > 0 for ef in ef_values):
                    messagebox.showwarning(
                        "Analysis Required",
                        "Please run CPM or PERT analysis first before using project crashing.\n\n"
                        "Go to Analysis menu and run the appropriate analysis.")
                    return

                original_duration = max(ef_values) if ef_values else 0

                if target_duration >= original_duration:
                    messagebox.showwarning(
                        "Invalid Target Duration",
                        f"Target duration ({target_duration}) must be less than the original project duration ({original_duration}).\n\n"
                        f"Please enter a target duration less than {original_duration}."
                    )
                    return
            except Exception as e:
                # print(f"[DEBUG] Error calculating original duration: {e}")
                # If we can't calculate the original duration, proceed with
                # warning
                messagebox.showwarning(
                    "Duration Check",
                    "Could not validate target duration against original project duration.")
        else:
            # No graph available - user probably hasn't run analysis yet
            messagebox.showwarning(
                "Analysis Required",
                "Please run CPM or PERT analysis first before using project crashing.\n\n"
                "Go to Analysis menu and run the appropriate analysis.")
            return

        # 3. Instantiate ProjectCrashing and run analysis
        crashing_engine = ProjectCrashing(base_analyzer)
        if hasattr(crashing_engine, "run"):
            try:
                result = crashing_engine.run(
                    target_duration=target_duration,
                    strategy=strategy,
                    objective=objective,
                    max_budget=max_budget,
                    max_crash_cost=max_crash_cost,
                    max_normal_cost=max_normal_cost,
                    max_iterations=max_iterations
                )
            except NotImplementedError as nie:
                messagebox.showwarning(
                    "Strategy Not Available",
                    f"The selected strategy is not yet implemented:\n\n{nie}\n\n"
                    "Please use 'lowest_cost' or 'enhanced_lowest_cost' instead.")
                return
        else:
            messagebox.showerror(
                "Implementation Error",
                "ProjectCrashing.run() not implemented.")
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
            self.log_text.delete('1.0', tk.END)
            self.log_text.insert('1.0', "No results to display.")
            self.metrics_text.delete('1.0', tk.END)
            self.metrics_text.insert('1.0', "No results to display.")
            return

        # Summary Report
        report = generate_crashing_report(result)
        if not isinstance(report, str):
            report = str(
                report) if report is not None else "No report generated."
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', report)

        # Detailed Log
        log_lines = []
        for entry in result.crash_log:
            line = f"--- Time Step {
                entry.get('current_time')} (Iteration {
                entry.get('iteration')}) ---\n"
            activity = entry.get('activity', 'None')
            if activity != 'None':
                line += f"  Action: Crashed '{activity}' to duration {
                    entry.get('duration')}\n"
                line += f"  Crash Cost Incurred: ${
                    entry.get(
                        'cost', 0):,.2f}\n"
            else:
                line += "  Action: No crash occurred.\n"

            active_tasks = entry.get('active_activities', [])
            line += f"  Active Tasks: {
                ', '.join(active_tasks) if active_tasks else 'None'}\n"
            line += f"  Normal Cost for this Step: ${
                entry.get(
                    'step_normal_cost',
                    0):,.2f}\n"
            line += f"  Accumulated Normal Cost: ${
                entry.get(
                    'total_normal_cost_accumulated',
                    0):,.2f}\n"
            line += f"  Accumulated Crash Cost: ${
                entry.get(
                    'total_crash_cost',
                    0):,.2f}\n"
            line += f"  Project Duration at this point: {
                entry.get('current_project_duration')}\n\n"
            log_lines.append(line)

        self.log_text.delete('1.0', tk.END)
        self.log_text.insert('1.0', "".join(log_lines))

        # Metrics
        metrics_lines = []
        total_project_cost = result.total_normal_cost + result.total_crash_cost
        avg_cost_per_unit = total_project_cost / \
            result.final_duration if result.final_duration > 0 else 0

        metrics_lines.append("--- Final Cost & Efficiency Metrics ---\n")
        metrics_lines.append(
            f"Total Accumulated Normal Cost: ${
                result.total_normal_cost:,.2f}\n")
        metrics_lines.append(
            f"Total Accumulated Crash Cost: ${
                result.total_crash_cost:,.2f}\n")
        metrics_lines.append("=" * 40 + "\n")
        metrics_lines.append(
            f"Final Total Project Cost: ${
                total_project_cost:,.2f}\n")
        metrics_lines.append("=" * 40 + "\n\n")
        metrics_lines.append(
            f"Original Duration: {
                result.original_duration} time units\n")
        metrics_lines.append(
            f"Final Duration: {
                result.final_duration} time units\n")
        metrics_lines.append(
            f"Time Saved: {
                result.original_duration -
                result.final_duration} time units\n\n")
        metrics_lines.append(
            f"Average Cost Per Time Unit: ${
                avg_cost_per_unit:,.2f}\n")

        self.metrics_text.delete('1.0', tk.END)
        self.metrics_text.insert('1.0', "".join(metrics_lines))

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

        # print(f"[DEBUG] Crashing result: {result}")
        # print(f"[DEBUG] Crash log: {getattr(result, 'crash_log', 'No crash_log')}")

        # Use the ORIGINAL network from base_analyzer for step visualization,
        # NOT the crashed network, to ensure initial state shows uncrashed
        # network
        base_graph = None
        base_analyzer = getattr(
            self.app,
            "current_analyzer",
            None) or getattr(
            self.app,
            "base_analyzer",
            None)
        if base_analyzer is not None:
            # print(f"[DEBUG] base_analyzer type: {type(base_analyzer)}")
            # print(f"[DEBUG] base_analyzer attributes: {dir(base_analyzer)}")

            # Try different possible attribute names for the original network
            for attr_name in [
                'graph',
                'G',
                'network',
                'original_graph',
                    'build_network']:
                if hasattr(base_analyzer, attr_name):
                    try:
                        attr_value = getattr(base_analyzer, attr_name)
                        if attr_value is not None:
                            # If it's a method, try calling it
                            if callable(attr_value):
                                if hasattr(base_analyzer, 'activities'):
                                    base_graph = attr_value(
                                        base_analyzer.activities)
                                    # print(f"[DEBUG] Using base_analyzer.{attr_name}(activities) for visualization")
                                else:
                                    base_graph = attr_value()
                                    # print(f"[DEBUG] Using base_analyzer.{attr_name}() for visualization")
                            else:
                                base_graph = attr_value
                                # print(f"[DEBUG] Using base_analyzer.{attr_name} for visualization")
                            break
                    except Exception as e:
                        # print(f"[DEBUG] Failed to get {attr_name} from base_analyzer: {e}")
                        continue

            # Final fallback: check if we can build network from activities
            if base_graph is None and hasattr(base_analyzer, 'activities'):
                try:
                    # Try to build network using the same logic as the analyzer
                    if hasattr(base_analyzer, 'build_network'):
                        base_graph = base_analyzer.build_network(
                            base_analyzer.activities)
                        # print("[DEBUG] Built network using base_analyzer.build_network(activities)")
                    elif hasattr(base_analyzer, '__class__') and hasattr(base_analyzer.__class__, 'build_network'):
                        base_graph = base_analyzer.__class__.build_network(
                            base_analyzer.activities)
                        # print("[DEBUG] Built network using analyzer class build_network method")
                except Exception as e:
                    # print(f"[DEBUG] Failed to build network from activities: {e}")
                    pass

        # Last resort: use the crashed graph from result if no original found
        if base_graph is None and hasattr(
                result, 'crashed_graph') and getattr(
                result, 'crashed_graph', None) is not None:
            base_graph = getattr(result, 'crashed_graph')
            # print("[DEBUG] Fallback to result.crashed_graph (will show wrong initial state)")

        # print(f"[DEBUG] base_graph is None? {base_graph is None}")
        if base_graph is not None:
            try:
                nodes_list = list(base_graph.nodes())
                # print(f"[DEBUG] base_graph type: {type(base_graph)}, nodes_count: {len(nodes_list)}")
                # print(f"[DEBUG] base_graph nodes repr: {[repr(n) for n in nodes_list]}")
                # print(f"[DEBUG] base_graph node types sample: {[type(n) for n in nodes_list[:10]]}")
            except Exception as _e:
                # print(f"[DEBUG] Error inspecting base_graph nodes: {_e}")
                pass

        if result and hasattr(result, 'crash_log') and result.crash_log:
            # Step 0: Add the original, uncrashed network state
            if base_graph is not None:
                original_G = base_graph.copy()
                self.step_graphs.append((0, 'Initial', None, original_G))
                # print("[DEBUG] Added step 0: Initial network state")

            # Steps 1-N: Create network state after each crash step
            # Each step shows the cumulative result of all crashes up to that
            # point
            for i, step_data in enumerate(result.crash_log):
                step_num = i + 1  # Navigation step numbers start from 1
                activity = step_data.get(
                    'activity', 'Unknown') if isinstance(
                    step_data, dict) else 'Unknown'
                new_duration = step_data.get(
                    'new_duration', None) if isinstance(
                    step_data, dict) else None
                if new_duration is None:
                    new_duration = step_data.get(
                        'duration', None) if isinstance(
                        step_data, dict) else None

                # Always build from the original graph and apply all crashes up
                # to this step
                if base_graph is not None:
                    try:
                        G_step = base_graph.copy()

                        # Apply ALL crashes from crash_log[0] to crash_log[i]
                        # (inclusive)
                        for j in range(i + 1):
                            crash_entry = result.crash_log[j]
                            if isinstance(crash_entry, dict):
                                crashed_activity = crash_entry.get(
                                    'activity', None)
                                crashed_duration = crash_entry.get(
                                    'new_duration', None) or crash_entry.get(
                                    'duration', None)
                                if crashed_activity and crashed_activity in G_step.nodes(
                                ) and crashed_duration is not None:
                                    G_step.nodes[crashed_activity]['duration'] = crashed_duration
                                    # print(f"[DEBUG] Step {step_num}: Applied crash {j+1} - {crashed_activity} to duration {crashed_duration}")

                        # Recalculate CPM for this step to get correct float
                        # values
                        network_builder = getattr(
                            getattr(
                                self.app,
                                "current_analyzer",
                                None) or getattr(
                                self.app,
                                "base_analyzer",
                                None),
                            'network_builder',
                            None)
                        if network_builder:
                            G_step = network_builder.forward_pass(G_step)
                            G_step = network_builder.backward_pass(G_step)
                            G_step = network_builder.calculate_float(G_step)

                        # Use critical path from crash log if available,
                        # otherwise calculate
                        cp = step_data.get(
                            'critical_path', None) if isinstance(
                            step_data, dict) else None
                        if cp:
                            for n in G_step.nodes():
                                G_step.nodes[n]['float'] = 0 if n in cp else G_step.nodes[n].get(
                                    'float', 1)

                        self.step_graphs.append(
                            (step_num, activity, new_duration if new_duration is not None else 0, G_step))
                        # print(f"[DEBUG] Added step {step_num}: {activity} crashed to {new_duration}")

                    except Exception as e:
                        # print(f"[DEBUG] Failed to synthesize G_step for step {step_num}: {e}")
                        continue

        # print(f"[DEBUG] Step graphs populated: {len(self.step_graphs)}")

        # Update navigation controls
        self.total_steps = len(self.step_graphs)
        self.step_select_spinbox.config(to=max(0, self.total_steps - 1))

        # Show first step if available
        if self.step_graphs:
            self.show_step(0)
        else:
            # Clear visualization frame
            for widget in self.step_display_frame.winfo_children():
                widget.destroy()
            # Show "No visualization data" message
            tk.Label(self.step_display_frame,
                     text="No visualization data available").pack()

    def export_results(self):
        """
        Export the current crashing results to a file.
        """
        try:
            # Check if there are results to export
            summary_content = self.summary_text.get('1.0', tk.END).strip()
            if not summary_content or summary_content == "No results to display.":
                messagebox.showwarning(
                    "No Results",
                    "No crashing results to export. Please run crashing analysis first.")
                return

            from tkinter import filedialog
            from datetime import datetime

            # Ask user for file location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"crashing_results_{timestamp}.txt"

            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfilename=default_filename,
                title="Export Crashing Results"
            )

            if file_path:
                # Combine all results into one file
                log_content = self.log_text.get('1.0', tk.END).strip()
                metrics_content = self.metrics_text.get('1.0', tk.END).strip()

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("PROJECT CRASHING ANALYSIS RESULTS\n")
                    f.write(
                        f"Generated: {
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")

                    f.write("SUMMARY REPORT\n")
                    f.write("-" * 40 + "\n")
                    f.write(summary_content + "\n\n")

                    f.write("DETAILED LOG\n")
                    f.write("-" * 40 + "\n")
                    f.write(log_content + "\n\n")

                    f.write("COST METRICS\n")
                    f.write("-" * 40 + "\n")
                    f.write(metrics_content + "\n")

                messagebox.showinfo(
                    "Success", f"Results exported successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Failed to export results:\n{
                    str(e)}")

    def clear_results(self):
        """
        Clear all displayed results and reset the UI.
        """
        self.summary_text.delete('1.0', tk.END)
        self.log_text.delete('1.0', tk.END)
        self.metrics_text.delete('1.0', tk.END)

        # Clear visualization
        for widget in self.step_display_frame.winfo_children():
            widget.destroy()

        # Reset step navigation
        self.step_graphs = []
        self.current_step = 0
        self.total_steps = 0
        self.step_select_spinbox.config(to=0)
        self.step_info_label.config(text="Step 0 of 0")
        self.step_select_var.set("0")

        # Show "No results" message
        tk.Label(
            self.step_display_frame,
            text="No crashing results to display").pack()

    def open_results_in_new_window(self):
        """
        Open the crashing results (summary, log, metrics) in a new window for better visibility.
        Similar to the "Show All Steps" functionality but for text results.
        """
        # Check if there are any results to display
        summary_content = self.summary_text.get('1.0', tk.END).strip()
        log_content = self.log_text.get('1.0', tk.END).strip()
        metrics_content = self.metrics_text.get('1.0', tk.END).strip()

        if not summary_content or summary_content == "No results to display.":
            messagebox.showwarning(
                "No Results",
                "No crashing results to display. Please run crashing analysis first.")
            return

        # Create new window
        results_window = tk.Toplevel(self.tab)
        results_window.title("Crashing Analysis Results - Detailed View")
        results_window.geometry("1200x800")
        # Start normal, user can maximize if needed
        results_window.state('normal')

        # Create notebook for the three tabs
        results_notebook = ttk.Notebook(results_window)
        results_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Summary Tab
        summary_frame = ttk.Frame(results_notebook)
        results_notebook.add(summary_frame, text="📊 Summary Report")

        summary_scroll = scrolledtext.ScrolledText(
            summary_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        summary_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        summary_scroll.insert('1.0', summary_content)
        summary_scroll.config(state=tk.DISABLED)  # Make read-only

        # Detailed Log Tab
        log_frame = ttk.Frame(results_notebook)
        results_notebook.add(log_frame, text="📋 Detailed Log")

        log_scroll = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            padx=10,
            pady=10
        )
        log_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scroll.insert('1.0', log_content)
        log_scroll.config(state=tk.DISABLED)  # Make read-only

        # Metrics Tab
        metrics_frame = ttk.Frame(results_notebook)
        results_notebook.add(metrics_frame, text="📈 Cost Metrics")

        metrics_scroll = scrolledtext.ScrolledText(
            metrics_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        metrics_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        metrics_scroll.insert('1.0', metrics_content)
        metrics_scroll.config(state=tk.DISABLED)  # Make read-only

        # Add control buttons at the bottom
        button_frame = ttk.Frame(results_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(
            button_frame,
            text="💾 Save All Results",
            command=lambda: self.save_results_from_window(
                summary_content,
                log_content,
                metrics_content)).pack(
            side=tk.LEFT,
            padx=5)

        ttk.Button(
            button_frame,
            text="📋 Copy Current Tab",
            command=lambda: self.copy_current_tab_content(results_notebook)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="❌ Close",
            command=results_window.destroy
        ).pack(side=tk.RIGHT, padx=5)

        # Focus on the new window
        results_window.focus_force()
        results_window.lift()

        # print("[DEBUG] Opened crashing results in new window")

    def save_results_from_window(
            self,
            summary_content,
            log_content,
            metrics_content):
        """Save all results from the new window to files"""
        from tkinter import filedialog
        import os
        from datetime import datetime

        try:
            # Ask user for directory to save files
            save_dir = filedialog.askdirectory(
                title="Choose directory to save results")
            if not save_dir:
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save summary
            summary_file = os.path.join(
                save_dir, f"crashing_summary_{timestamp}.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)

            # Save log
            log_file = os.path.join(save_dir, f"crashing_log_{timestamp}.txt")
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)

            # Save metrics
            metrics_file = os.path.join(
                save_dir, f"crashing_metrics_{timestamp}.txt")
            with open(metrics_file, 'w', encoding='utf-8') as f:
                f.write(metrics_content)

            messagebox.showinfo("Success",
                                f"Results saved successfully!\n\n"
                                f"Files saved in: {save_dir}\n"
                                f"- crashing_summary_{timestamp}.txt\n"
                                f"- crashing_log_{timestamp}.txt\n"
                                f"- crashing_metrics_{timestamp}.txt")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")

    def copy_current_tab_content(self, notebook):
        """Copy the content of the currently selected tab to clipboard"""
        try:
            current_tab = notebook.select()
            tab_text = notebook.tab(current_tab, "text")

            # Get the scrolled text widget from the current tab
            current_frame = notebook.nametowidget(current_tab)
            for widget in current_frame.winfo_children():
                if isinstance(widget, scrolledtext.ScrolledText):
                    content = widget.get('1.0', tk.END)
                    # Copy to clipboard
                    notebook.clipboard_clear()
                    notebook.clipboard_append(content)
                    messagebox.showinfo(
                        "Copied", f"Content from '{tab_text}' copied to clipboard!")
                    return

            messagebox.showwarning("Error", "Could not find content to copy.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy content: {str(e)}")

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
        if _PLOTLY_EMBED:
            self._render_mode_var = tk.StringVar(value="matplotlib")
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
        ttk.Label(
            params_frame,
            text="Target Duration:").grid(
            row=0,
            column=0,
            padx=5,
            pady=2,
            sticky="w")
        self.target_duration_var = tk.StringVar(value="25")
        ttk.Entry(
            params_frame,
            textvariable=self.target_duration_var,
            width=10).grid(
            row=0,
            column=1,
            padx=5,
            pady=2)

        ttk.Label(
            params_frame,
            text="Strategy:").grid(
            row=0,
            column=2,
            padx=5,
            pady=2,
            sticky="w")
        self.strategy_var = tk.StringVar(
            value=CrashingStrategy.LOWEST_COST.value)
        strategy_combo = ttk.Combobox(
            params_frame, textvariable=self.strategy_var, width=15)
        strategy_combo['values'] = [s.value for s in CrashingStrategy]
        strategy_combo.grid(row=0, column=3, padx=5, pady=2)
        strategy_combo.state(['readonly'])

        ttk.Label(
            params_frame,
            text="Objective:").grid(
            row=0,
            column=4,
            padx=5,
            pady=2,
            sticky="w")
        self.objective_var = tk.StringVar(
            value=OptimizationObjective.MINIMIZE_COST.value)
        objective_combo = ttk.Combobox(
            params_frame, textvariable=self.objective_var, width=15)
        objective_combo['values'] = [o.value for o in OptimizationObjective]
        objective_combo.grid(row=0, column=5, padx=5, pady=2)
        objective_combo.state(['readonly'])

        ttk.Label(
            params_frame,
            text="Max Budget:").grid(
            row=0,
            column=6,
            padx=5,
            pady=2,
            sticky="w")
        self.budget_var = tk.StringVar(value="")
        ttk.Entry(
            params_frame,
            textvariable=self.budget_var,
            width=10).grid(
            row=0,
            column=7,
            padx=5,
            pady=2)

        ttk.Label(
            params_frame,
            text="Max Crashing Cost:").grid(
            row=0,
            column=8,
            padx=5,
            pady=2,
            sticky="w")
        self.max_crash_cost_var = tk.StringVar(value="")
        ttk.Entry(
            params_frame,
            textvariable=self.max_crash_cost_var,
            width=10).grid(
            row=0,
            column=9,
            padx=5,
            pady=2)

        ttk.Label(
            params_frame,
            text="Max Normal Cost:").grid(
            row=0,
            column=10,
            padx=5,
            pady=2,
            sticky="w")
        self.max_normal_cost_var = tk.StringVar(value="")
        ttk.Entry(
            params_frame,
            textvariable=self.max_normal_cost_var,
            width=10).grid(
            row=0,
            column=11,
            padx=5,
            pady=2)

        # Set max_iterations to 1500 (no advanced parameters UI)
        self.max_iterations_var = tk.StringVar(value="1500")

        # Run Crashing button next to input fields
        ttk.Button(
            params_frame,
            text="Run Crashing",
            command=self.run_crashing
        ).grid(row=0, column=12, padx=10, pady=2, sticky="e")

        # Add a stretchable empty column to push right buttons to the far end
        params_frame.grid_columnconfigure(13, weight=1)

        # Frame for far right buttons
        right_buttons_frame = ttk.Frame(params_frame)
        right_buttons_frame.grid(row=0, column=14, padx=0, pady=2, sticky="e")

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

        ttk.Button(
            right_buttons_frame,
            text="? Help",
            command=self.app.show_crashing_tab_help
        ).pack(side=tk.LEFT, padx=2)

        # Results Section
        results_frame = ttk.LabelFrame(self.tab, text="Crashing Results")
        results_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)

        # Notebook with integrated button
        notebook_frame = ttk.Frame(results_frame)
        notebook_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)

        self.results_notebook = ttk.Notebook(notebook_frame)
        self.results_notebook.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            notebook_frame,
            text="Open Results in New Window",
            command=self.open_results_in_new_window
        ).pack(side=tk.RIGHT, padx=(5, 0))

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
        # List of (step_num, activity, new_duration, G_step)
        self.step_graphs = []
        self.current_step = 0
        self.total_steps = 0
        # Navigation controls
        nav_frame = ttk.Frame(viz_frame)
        nav_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(
            nav_frame,
            text="◀◀ First",
            command=self.show_first_step).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            nav_frame,
            text="◀ Previous",
            command=self.show_previous_step).pack(
            side=tk.LEFT,
            padx=2)
        self.step_info_label = ttk.Label(nav_frame, text="Step 0 of 0")
        self.step_info_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(
            nav_frame,
            text="Next ▶",
            command=self.show_next_step).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            nav_frame,
            text="Last ▶▶",
            command=self.show_last_step).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Label(
            nav_frame,
            text="Go to step:").pack(
            side=tk.LEFT,
            padx=(
                20,
                5))
        self.step_select_var = tk.StringVar(value="0")
        self.step_select_spinbox = ttk.Spinbox(
            nav_frame,
            from_=0,
            to=0,
            width=5,
            textvariable=self.step_select_var,
            command=self.show_selected_step)
        self.step_select_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Button(
            nav_frame,
            text="Show All Steps",
            command=self.show_all_steps_grid).pack(
            side=tk.RIGHT,
            padx=2)

        self.step_display_frame = ttk.Frame(viz_frame)
        self.step_display_frame.pack(fill=tk.BOTH, expand=True)

        # Plotly toggle + frame
        if _PLOTLY_EMBED:
            tog = ttk.Frame(nav_frame)
            tog.pack(side=tk.RIGHT, padx=10)
            ttk.Radiobutton(
                tog,
                text="Classic",
                variable=self._render_mode_var,
                value="matplotlib",
                command=self._switch_renderer).pack(
                side='left')
            ttk.Radiobutton(
                tog,
                text="\U0001f4ca Plotly",
                variable=self._render_mode_var,
                value="plotly",
                command=self._switch_renderer).pack(
                side='left')
            self._plotly_frame = PlotlyChartFrame(viz_frame)

    def show_step(self, step_index):
        if 0 <= step_index < len(self.step_graphs):
            self.current_step = step_index
            step_num, activity, new_duration, G_step = self.step_graphs[step_index]

            # --- Plotly path ---
            if _PLOTLY_EMBED and self._render_mode_var.get() == "plotly":
                if step_num == 0:
                    label = "Initial Network"
                    crit = set()
                else:
                    label = f"Step {step_num}"
                    if activity and activity != 'None':
                        label += f": {activity} → {new_duration}"
                    crit = {n for n in G_step.nodes()
                            if G_step.nodes[n].get('float', 1) == 0}
                try:
                    fig = plotly_crashing_network(G_step, step_label=label,
                                                  critical_activities=crit)
                    if fig:
                        self._plotly_frame.update_chart(fig)
                except Exception:
                    pass
                self.step_info_label.config(
                    text=f"Step {step_index} of {self.total_steps - 1}")
                self.step_select_var.set(str(step_index))
                return

            # --- Matplotlib path (original) ---
            for widget in self.step_display_frame.winfo_children():
                widget.destroy()
            fig = plt.Figure(figsize=(10, 6))
            fig.patch.set_facecolor('white')
            ax = fig.add_subplot(111)
            ax.set_facecolor('white')
            if step_num == 0:
                draw_network_diagram_on_ax(ax, G_step, initial=True)
                ax.set_title("Initial Network", fontsize=14, fontweight='bold')
            else:
                draw_network_diagram_on_ax(ax, G_step)
                title = f"Time Step {step_num}"
                if activity and activity != 'None':
                    title += f": Activity {activity} crashed to {new_duration}"
                else:
                    title += ": No Crash"
                ax.set_title(title, fontsize=14, fontweight='bold')
            canvas = FigureCanvasTkAgg(fig, self.step_display_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()
            self.step_info_label.config(
                text=f"Step {step_index} of {
                    self.total_steps - 1}")
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
        grid_window.state('zoomed')
        canvas = tk.Canvas(grid_window)
        scrollbar = ttk.Scrollbar(
            grid_window,
            orient="vertical",
            command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        cols = 3
        step_images = []
        for idx, (step_num, activity, new_duration,
                  G_step) in enumerate(self.step_graphs):
            fig = plt.Figure(figsize=(5, 4))
            fig.patch.set_facecolor('white')
            ax = fig.add_subplot(111)
            ax.set_facecolor('white')
            draw_network_diagram_on_ax_small(ax, G_step)
            if step_num == 0:
                ax.set_title("Initial Network", fontsize=10, fontweight='bold')
            else:
                ax.set_title(
                    f"Step {step_num}: {activity} → {new_duration}",
                    fontsize=10,
                    fontweight='bold')
            canvas_agg = agg.FigureCanvasAgg(fig)
            canvas_agg.draw()
            buf = canvas_agg.buffer_rgba()
            img = Image.frombuffer(
                "RGBA",
                canvas_agg.get_width_height(),
                buf,
                "raw",
                "RGBA",
                0,
                1)
            tk_img = ImageTk.PhotoImage(img)
            step_images.append(tk_img)
            row = idx // cols
            col = idx % cols
            lbl = tk.Label(scrollable_frame, image=tk_img)
            lbl.grid(row=row, column=col, padx=5, pady=5)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        grid_window.step_images = step_images

        def _on_destroy(event):
            if event.widget == grid_window:
                canvas.unbind_all("<MouseWheel>")
        grid_window.bind("<Destroy>", _on_destroy)

    # -- Plotly helpers (Crashing) ------------------------------------------
    def _switch_renderer(self):
        if not _PLOTLY_EMBED:
            return
        if self._render_mode_var.get() == "plotly":
            self.step_display_frame.pack_forget()
            self._plotly_frame.pack(fill="both", expand=True)
            if self.step_graphs:
                self.show_step(self.current_step)
        else:
            self._plotly_frame.pack_forget()
            self.step_display_frame.pack(fill="both", expand=True)
            if self.step_graphs:
                self.show_step(self.current_step)
