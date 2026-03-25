"""
Advanced Cost Optimization Tab

Provides GUI interface for:
- Time-Cost Optimization
- Resource Leveling
- Multi-Objective Optimization with Pareto frontiers

Author: PMHelper Team
Version: 1.1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class OptimizationTab(ttk.Frame):
    """Main optimization tab with sub-tabs for different optimization types"""
    
    def __init__(self, parent, cpm_analyzer=None):
        super().__init__(parent)
        self.cpm_analyzer = cpm_analyzer
        self.pack(fill='both', expand=True)
        
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create sub-tabs
        self.time_cost_tab = TimeCostOptimizationPanel(self.notebook, self.cpm_analyzer)
        self.resource_tab = ResourceLevelingPanel(self.notebook, self.cpm_analyzer)
        self.multi_obj_tab = MultiObjectivePanel(self.notebook, self.cpm_analyzer)
        
        self.notebook.add(self.time_cost_tab, text='Time-Cost Optimization')
        self.notebook.add(self.resource_tab, text='Resource Leveling')
        self.notebook.add(self.multi_obj_tab, text='Multi-Objective')
        
        logger.info("Optimization tab initialized")
    
    def set_analyzer(self, analyzer):
        """Update analyzer for all sub-tabs"""
        self.cpm_analyzer = analyzer
        self.time_cost_tab.set_analyzer(analyzer)
        self.resource_tab.set_analyzer(analyzer)
        self.multi_obj_tab.set_analyzer(analyzer)


class TimeCostOptimizationPanel(ttk.Frame):
    """Time-Cost Trade-off Optimization Panel"""
    
    def __init__(self, parent, cpm_analyzer=None):
        super().__init__(parent)
        self.cpm_analyzer = cpm_analyzer
        self.pack(fill='both', expand=True)
        
        # Create main container with panes
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel: Input and controls
        self.left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_frame, weight=1)
        
        # Right panel: Visualization
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=2)
        
        self.create_input_panel()
        self.create_visualization_panel()
    
    def create_input_panel(self):
        """Create input controls for indirect costs"""
        # Title
        title_frame = ttk.Frame(self.left_frame)
        title_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(title_frame, text="Time-Cost Optimization",
                 font=('Arial', 14, 'bold')).pack()
        
        # Indirect Cost Inputs
        cost_frame = ttk.LabelFrame(self.left_frame, text="Indirect Costs (Daily Rates)",
                                    padding=10)
        cost_frame.pack(fill='x', padx=5, pady=5)
        
        self.cost_entries = {}
        cost_categories = [
            ('facilities', 'Facilities ($)', 500.0),
            ('equipment', 'Equipment ($)', 300.0),
            ('utilities', 'Utilities ($)', 150.0),
            ('overhead', 'Overhead ($)', 250.0)
        ]
        
        for i, (key, label, default) in enumerate(cost_categories):
            ttk.Label(cost_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            entry = ttk.Entry(cost_frame, width=15)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.cost_entries[key] = entry
        
        # Total daily indirect cost display
        ttk.Separator(cost_frame, orient='horizontal').grid(row=len(cost_categories), 
                                                            column=0, columnspan=2, 
                                                            sticky='ew', pady=5)
        self.total_label = ttk.Label(cost_frame, text="Total Daily: $1,200.00",
                                     font=('Arial', 10, 'bold'))
        self.total_label.grid(row=len(cost_categories)+1, column=0, columnspan=2, pady=2)
        
        # Update total when entries change
        for entry in self.cost_entries.values():
            entry.bind('<KeyRelease>', self.update_total)
        
        # Optimize Button
        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill='x', padx=5, pady=10)
        
        self.optimize_btn = ttk.Button(btn_frame, text="Optimize", 
                                       command=self.run_optimization,
                                       style='Accent.TButton')
        self.optimize_btn.pack(fill='x', pady=2)
        
        ttk.Button(btn_frame, text="Clear Results",
                  command=self.clear_results).pack(fill='x', pady=2)
        
        # Results Display
        results_frame = ttk.LabelFrame(self.left_frame, text="Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, 
                                                       width=40, wrap=tk.WORD)
        self.results_text.pack(fill='both', expand=True)
    
    def create_visualization_panel(self):
        """Create matplotlib visualization panel"""
        viz_frame = ttk.LabelFrame(self.right_frame, text="Time-Cost Curve", padding=5)
        viz_frame.pack(fill='both', expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Project Duration (days)')
        self.ax.set_ylabel('Cost ($)')
        self.ax.set_title('Time-Cost Trade-off Curve')
        self.ax.grid(True, alpha=0.3)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(fill='x')
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
    
    def update_total(self, event=None):
        """Update total daily cost display"""
        try:
            total = sum(float(entry.get()) for entry in self.cost_entries.values())
            self.total_label.config(text=f"Total Daily: ${total:,.2f}")
        except ValueError:
            self.total_label.config(text="Total Daily: Invalid input")
    
    def run_optimization(self):
        """Run time-cost optimization"""
        if not self.cpm_analyzer or not hasattr(self.cpm_analyzer, 'G'):
            messagebox.showwarning("No Data", 
                                  "Please load and analyze a project first.")
            return
        
        try:
            # Get indirect cost rates
            daily_costs = {}
            for key, entry in self.cost_entries.items():
                daily_costs[key] = float(entry.get())
            
            # Import optimization modules
            from pmhelper.core.cost_optimization import IndirectCostModel, TimeCostOptimizer
            from pmhelper.core.cost_visualizations import plot_time_cost_curve, generate_cost_report
            
            # Create indirect cost model
            indirect_model = IndirectCostModel(daily_costs)
            
            # Create optimizer
            optimizer = TimeCostOptimizer(self.cpm_analyzer, indirect_model)
            
            # Find optimal duration
            result = optimizer.find_optimal_duration()
            
            # Generate curve data
            curve_data = optimizer.generate_curve()
            
            # Update visualization
            self.plot_curve(curve_data, result)
            
            # Update results text
            report = generate_cost_report(result, daily_costs)
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert('1.0', report)
            
            messagebox.showinfo("Optimization Complete",
                               f"Optimal duration: {result['optimal_duration']} days\n"
                               f"Cost savings: ${result.get('savings', 0):,.2f}")
        
        except Exception as e:
            logger.error(f"Optimization error: {e}", exc_info=True)
            messagebox.showerror("Error", f"Optimization failed: {str(e)}")
    
    def plot_curve(self, curve_data, result):
        """Plot time-cost curve"""
        self.ax.clear()
        
        # Plot curves
        self.ax.plot(curve_data['duration'], curve_data['direct_cost'],
                    marker='o', label='Direct Cost', color='blue', linewidth=2)
        self.ax.plot(curve_data['duration'], curve_data['indirect_cost'],
                    marker='s', label='Indirect Cost', color='green', linewidth=2)
        self.ax.plot(curve_data['duration'], curve_data['total_cost'],
                    marker='^', label='Total Cost', color='red', linewidth=3)
        
        # Mark optimal point
        if 'optimal_duration' in result:
            self.ax.scatter([result['optimal_duration']], 
                          [result['optimal_total_cost']],
                          s=300, color='gold', edgecolor='black', linewidth=2.5,
                          label='Optimal Point', zorder=5, marker='*')
        
        self.ax.set_xlabel('Project Duration (days)', fontsize=11)
        self.ax.set_ylabel('Cost ($)', fontsize=11)
        self.ax.set_title('Time-Cost Trade-off Curve', fontsize=13, fontweight='bold')
        self.ax.legend(loc='best', fontsize=10)
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def clear_results(self):
        """Clear results and visualization"""
        self.results_text.delete('1.0', tk.END)
        self.ax.clear()
        self.ax.set_xlabel('Project Duration (days)')
        self.ax.set_ylabel('Cost ($)')
        self.ax.set_title('Time-Cost Trade-off Curve')
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def set_analyzer(self, analyzer):
        """Update analyzer"""
        self.cpm_analyzer = analyzer


class ResourceLevelingPanel(ttk.Frame):
    """Resource Leveling and Smoothing Panel"""
    
    def __init__(self, parent, cpm_analyzer=None):
        super().__init__(parent)
        self.cpm_analyzer = cpm_analyzer
        self.pack(fill='both', expand=True)
        
        # Create main container
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel: Controls
        self.left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_frame, weight=1)
        
        # Right panel: Visualization
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=2)
        
        self.create_control_panel()
        self.create_visualization_panel()
    
    def create_control_panel(self):
        """Create controls for resource leveling"""
        # Title
        title_frame = ttk.Frame(self.left_frame)
        title_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(title_frame, text="Resource Leveling",
                 font=('Arial', 14, 'bold')).pack()
        
        # Method selection
        method_frame = ttk.LabelFrame(self.left_frame, text="Leveling Method", padding=10)
        method_frame.pack(fill='x', padx=5, pady=5)
        
        self.method_var = tk.StringVar(value='minimum_moment')
        ttk.Radiobutton(method_frame, text="Minimum Moment Algorithm",
                       variable=self.method_var, value='minimum_moment').pack(anchor='w')
        ttk.Radiobutton(method_frame, text="Burgess Method",
                       variable=self.method_var, value='burgess').pack(anchor='w')
        
        # Resource limit
        limit_frame = ttk.LabelFrame(self.left_frame, text="Resource Constraint (Optional)",
                                     padding=10)
        limit_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(limit_frame, text="Max Resource Units:").grid(row=0, column=0, sticky='w')
        self.limit_entry = ttk.Entry(limit_frame, width=15)
        self.limit_entry.grid(row=0, column=1, padx=5)
        self.limit_entry.insert(0, "")
        
        ttk.Label(limit_frame, text="(Leave blank for unconstrained)",
                 font=('Arial', 8, 'italic')).grid(row=1, column=0, columnspan=2, 
                                                   sticky='w', pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill='x', padx=5, pady=10)
        
        self.level_btn = ttk.Button(btn_frame, text="Level Resources",
                                    command=self.run_leveling,
                                    style='Accent.TButton')
        self.level_btn.pack(fill='x', pady=2)
        
        ttk.Button(btn_frame, text="Clear Results",
                  command=self.clear_results).pack(fill='x', pady=2)
        
        # Results Display
        results_frame = ttk.LabelFrame(self.left_frame, text="Metrics", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15,
                                                       width=40, wrap=tk.WORD)
        self.results_text.pack(fill='both', expand=True)
    
    def create_visualization_panel(self):
        """Create visualization panel with before/after charts"""
        viz_frame = ttk.LabelFrame(self.right_frame, text="Resource Profile", padding=5)
        viz_frame.pack(fill='both', expand=True)
        
        # Create matplotlib figure with 2 subplots
        self.fig = Figure(figsize=(8, 8), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        
        self.ax1.set_xlabel('Time (days)')
        self.ax1.set_ylabel('Resource Usage')
        self.ax1.set_title('Original Schedule')
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.set_xlabel('Time (days)')
        self.ax2.set_ylabel('Resource Usage')
        self.ax2.set_title('Leveled Schedule')
        self.ax2.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(fill='x')
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
    
    def run_leveling(self):
        """Run resource leveling"""
        if not self.cpm_analyzer or not hasattr(self.cpm_analyzer, 'G'):
            messagebox.showwarning("No Data",
                                  "Please load and analyze a project first.")
            return
        
        try:
            # Import leveling modules
            from pmhelper.core.resource_leveling import ResourceLevelingFactory, activities_from_cpm
            from pmhelper.core.resource_visualizations import plot_resource_profile
            
            # Convert CPM to activities
            activities = activities_from_cpm(self.cpm_analyzer)
            
            # Get resource limit
            resource_limit = None
            if self.limit_entry.get().strip():
                resource_limit = float(self.limit_entry.get())
            
            # Get method
            method = self.method_var.get()
            
            # Create leveler
            leveler = ResourceLevelingFactory.create(method, activities, resource_limit)
            
            # Run leveling
            result = leveler.level()
            
            # Add method name to result for display
            result['method'] = method
            
            # Plot results
            self.plot_profiles(result)
            
            # Display metrics
            self.display_metrics(result)
            
            # Show completion message
            improvement = result.get('improvement_pct', 0)
            iterations = result.get('iterations', 0)
            
            if improvement > 0.01:  # Show if improvement > 0.01%
                messagebox.showinfo("Leveling Complete",
                                   f"Leveling complete!\n"
                                   f"Iterations: {iterations}\n"
                                   f"Improvement: {improvement:.2f}%")
            else:
                messagebox.showinfo("Already Optimal",
                                   "Schedule is already optimally leveled!")
        
        except Exception as e:
            logger.error(f"Leveling error: {e}", exc_info=True)
            messagebox.showerror("Error", f"Resource leveling failed: {str(e)}")
    
    def plot_profiles(self, result):
        """Plot before and after resource profiles"""
        self.ax1.clear()
        self.ax2.clear()
        
        # Original profile
        if 'original_profile' in result:
            prof_orig = result['original_profile']
            # Convert ResourceProfile object to dataframe for plotting
            if hasattr(prof_orig, 'to_dataframe'):
                df_orig = prof_orig.to_dataframe()
                self.ax1.bar(df_orig['time'], df_orig['resource_usage'],
                            color='lightcoral', edgecolor='red', alpha=0.7)
            else:
                # Fallback: access profile dictionary directly
                times = sorted(prof_orig.profile.keys())
                usages = [prof_orig.profile[t] for t in times]
                self.ax1.bar(times, usages,
                            color='lightcoral', edgecolor='red', alpha=0.7)
            self.ax1.set_xlabel('Time (days)')
            self.ax1.set_ylabel('Resource Usage')
            self.ax1.set_title('Original Schedule')
            self.ax1.grid(True, alpha=0.3)
        
        # Leveled profile
        if 'leveled_profile' in result:
            prof_lev = result['leveled_profile']
            # Convert ResourceProfile object to dataframe for plotting
            if hasattr(prof_lev, 'to_dataframe'):
                df_lev = prof_lev.to_dataframe()
                self.ax2.bar(df_lev['time'], df_lev['resource_usage'],
                            color='lightgreen', edgecolor='green', alpha=0.7)
            else:
                # Fallback: access profile dictionary directly
                times = sorted(prof_lev.profile.keys())
                usages = [prof_lev.profile[t] for t in times]
                self.ax2.bar(times, usages,
                            color='lightgreen', edgecolor='green', alpha=0.7)
            
            # Add resource limit line if specified
            if result.get('resource_limit'):
                self.ax2.axhline(result['resource_limit'], color='red',
                               linestyle='--', linewidth=2,
                               label=f"Limit: {result['resource_limit']}")
                self.ax2.legend()
            
            self.ax2.set_xlabel('Time (days)')
            self.ax2.set_ylabel('Resource Usage')
            self.ax2.set_title('Leveled Schedule')
            self.ax2.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def display_metrics(self, result):
        """Display leveling metrics"""
        self.results_text.delete('1.0', tk.END)
        
        text = "RESOURCE LEVELING RESULTS\n"
        text += "=" * 40 + "\n\n"
        
        # Get method name from result or default
        method = result.get('method', 'Unknown')
        text += f"Method: {method}\n\n"
        
        # Calculate average usage from profiles if available
        original_avg = 0.0
        leveled_avg = 0.0
        if 'original_profile' in result and hasattr(result['original_profile'], 'profile'):
            orig_values = list(result['original_profile'].profile.values())
            original_avg = sum(orig_values) / len(orig_values) if orig_values else 0.0
        if 'leveled_profile' in result and hasattr(result['leveled_profile'], 'profile'):
            lev_values = list(result['leveled_profile'].profile.values())
            leveled_avg = sum(lev_values) / len(lev_values) if lev_values else 0.0
        
        text += "Original Schedule:\n"
        text += f"  Peak Usage: {result.get('peak_usage_original', 0):.1f}\n"
        text += f"  Total Moment: {result.get('original_moment', 0):.1f}\n"
        text += f"  Average Usage: {original_avg:.1f}\n\n"
        
        text += "Leveled Schedule:\n"
        text += f"  Peak Usage: {result.get('peak_usage_leveled', 0):.1f}\n"
        text += f"  Total Moment: {result.get('leveled_moment', 0):.1f}\n"
        text += f"  Average Usage: {leveled_avg:.1f}\n\n"
        
        text += f"Improvement: {result.get('improvement_pct', 0):.2f}%\n"
        text += f"Iterations: {result.get('iterations', 0)}\n"
        
        # Check if schedule is feasible
        if 'feasible' in result:
            text += f"Feasible: {'Yes' if result['feasible'] else 'No'}\n"
        
        self.results_text.insert('1.0', text)
    
    def clear_results(self):
        """Clear results"""
        self.results_text.delete('1.0', tk.END)
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.grid(True, alpha=0.3)
        self.ax2.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def set_analyzer(self, analyzer):
        """Update analyzer"""
        self.cpm_analyzer = analyzer


class MultiObjectivePanel(ttk.Frame):
    """Multi-Objective Optimization Panel"""
    
    def __init__(self, parent, cpm_analyzer=None):
        super().__init__(parent)
        self.cpm_analyzer = cpm_analyzer
        self.pack(fill='both', expand=True)
        
        # Create main container
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel: Controls
        self.left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_frame, weight=1)
        
        # Right panel: Visualization
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=2)
        
        self.create_control_panel()
        self.create_visualization_panel()
    
    def create_control_panel(self):
        """Create controls for multi-objective optimization"""
        # Title
        title_frame = ttk.Frame(self.left_frame)
        title_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(title_frame, text="Multi-Objective Optimization",
                 font=('Arial', 14, 'bold')).pack()
        
        # Objective selection
        obj_frame = ttk.LabelFrame(self.left_frame, text="Objectives", padding=10)
        obj_frame.pack(fill='x', padx=5, pady=5)
        
        self.objectives = {}
        self.objectives['duration'] = tk.BooleanVar(value=True)
        self.objectives['cost'] = tk.BooleanVar(value=True)
        self.objectives['npv'] = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(obj_frame, text="Minimize Duration",
                       variable=self.objectives['duration']).pack(anchor='w')
        ttk.Checkbutton(obj_frame, text="Minimize Cost",
                       variable=self.objectives['cost']).pack(anchor='w')
        ttk.Checkbutton(obj_frame, text="Maximize NPV",
                       variable=self.objectives['npv']).pack(anchor='w')
        
        # NPV Parameters
        npv_frame = ttk.LabelFrame(self.left_frame, text="NPV Parameters", padding=10)
        npv_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(npv_frame, text="Discount Rate:").grid(row=0, column=0, sticky='w')
        self.discount_entry = ttk.Entry(npv_frame, width=15)
        self.discount_entry.insert(0, "0.10")
        self.discount_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(npv_frame, text="(e.g., 0.10 for 10%)",
                 font=('Arial', 8, 'italic')).grid(row=1, column=0, columnspan=2,
                                                   sticky='w', pady=2)
        
        # Sampling
        sample_frame = ttk.LabelFrame(self.left_frame, text="Solution Generation", padding=10)
        sample_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(sample_frame, text="Sample Size:").grid(row=0, column=0, sticky='w')
        self.sample_entry = ttk.Entry(sample_frame, width=15)
        self.sample_entry.insert(0, "100")
        self.sample_entry.grid(row=0, column=1, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill='x', padx=5, pady=10)
        
        self.optimize_btn = ttk.Button(btn_frame, text="Generate Pareto Frontier",
                                       command=self.run_optimization,
                                       style='Accent.TButton')
        self.optimize_btn.pack(fill='x', pady=2)
        
        ttk.Button(btn_frame, text="Clear Results",
                  command=self.clear_results).pack(fill='x', pady=2)
        
        # Results
        results_frame = ttk.LabelFrame(self.left_frame, text="Pareto Solutions", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=10,
                                                       width=40, wrap=tk.WORD)
        self.results_text.pack(fill='both', expand=True)
    
    def create_visualization_panel(self):
        """Create Pareto frontier visualization"""
        viz_frame = ttk.LabelFrame(self.right_frame, text="Pareto Frontier", padding=5)
        viz_frame.pack(fill='both', expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Duration (days)')
        self.ax.set_ylabel('Cost ($)')
        self.ax.set_title('Pareto Frontier: Duration vs Cost')
        self.ax.grid(True, alpha=0.3)
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(fill='x')
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
    
    def run_optimization(self):
        """Run multi-objective optimization"""
        if not self.cpm_analyzer or not hasattr(self.cpm_analyzer, 'G'):
            messagebox.showwarning("No Data",
                                  "Please load and analyze a project first.")
            return
        
        try:
            # Get selected objectives
            selected = [name for name, var in self.objectives.items() if var.get()]
            
            if len(selected) < 2:
                messagebox.showwarning("Selection Error",
                                      "Please select at least 2 objectives.")
                return
            
            # Get parameters
            discount_rate = float(self.discount_entry.get())
            num_samples = int(self.sample_entry.get())
            
            # Import optimization modules
            from pmhelper.core.multi_objective import (
                MultiObjectiveOptimizer, ScheduleGenerator
            )
            from pmhelper.core.resource_leveling import activities_from_cpm
            from pmhelper.core.multi_objective_visualizations import plot_pareto_frontier_2d
            
            # Convert to activities
            activities = activities_from_cpm(self.cpm_analyzer)
            
            # Define objective functions (simplified for GUI)
            def calc_duration(schedule):
                return max(schedule.get(act.id, act.es) + act.duration 
                          for act in activities)
            
            def calc_cost(schedule):
                # Simplified cost calculation
                return sum(abs(act.duration * 100) for act in activities)
            
            def calc_npv(schedule):
                # Simplified NPV (needs cash flows in real implementation)
                npv = 0
                for act in activities:
                    finish = schedule.get(act.id, act.es) + act.duration
                    # Use duration as proxy for cash flow
                    pv = act.duration * 1000 / ((1 + discount_rate) ** finish)
                    npv += pv
                return npv
            
            # Build objective dict
            objectives = {}
            if 'duration' in selected:
                objectives['duration'] = calc_duration
            if 'cost' in selected:
                objectives['cost'] = calc_cost
            if 'npv' in selected:
                objectives['npv'] = lambda s: -calc_npv(s)  # Negative to minimize
            
            # Create optimizer
            optimizer = MultiObjectiveOptimizer(objectives)
            
            # Generate schedules
            schedules = ScheduleGenerator.generate_sampled(activities, num_samples)
            
            # Compute Pareto frontier
            minimize_objs = ['duration', 'cost', 'npv']  # All minimize
            frontier = optimizer.generate_solutions_grid(schedules, minimize_objs)
            
            # Get summary
            solutions_df = optimizer.get_solution_summary()
            pareto_df = optimizer.get_pareto_summary()
            
            # Plot frontier (2D for now)
            if 'duration' in selected and 'cost' in selected:
                self.plot_frontier(solutions_df, 'duration', 'cost')
            
            # Display results
            self.display_pareto_solutions(pareto_df, selected)
            
            messagebox.showinfo("Optimization Complete",
                               f"Generated {len(frontier)} Pareto-optimal solutions\n"
                               f"from {len(schedules)} candidates.")
        
        except Exception as e:
            logger.error(f"Multi-objective error: {e}", exc_info=True)
            messagebox.showerror("Error", f"Optimization failed: {str(e)}")
    
    def plot_frontier(self, solutions_df, obj1, obj2):
        """Plot 2D Pareto frontier"""
        self.ax.clear()
        
        # Separate solutions
        pareto = solutions_df[solutions_df['is_pareto'] == True]
        dominated = solutions_df[solutions_df['is_pareto'] == False]
        
        # Plot dominated
        if not dominated.empty:
            self.ax.scatter(dominated[obj1], dominated[obj2],
                          alpha=0.3, s=30, color='lightgray',
                          label='Dominated Solutions')
        
        # Plot Pareto
        if not pareto.empty:
            pareto_sorted = pareto.sort_values(obj1)
            self.ax.scatter(pareto_sorted[obj1], pareto_sorted[obj2],
                          alpha=0.8, s=100, color='red', marker='*',
                          label='Pareto Frontier', edgecolors='darkred', linewidths=1.5)
            self.ax.plot(pareto_sorted[obj1], pareto_sorted[obj2],
                       'r--', alpha=0.5, linewidth=2)
        
        self.ax.set_xlabel(obj1.replace('_', ' ').title(), fontsize=11)
        self.ax.set_ylabel(obj2.replace('_', ' ').title(), fontsize=11)
        self.ax.set_title(f'Pareto Frontier: {obj1.title()} vs {obj2.title()}',
                         fontsize=13, fontweight='bold')
        self.ax.legend(loc='best')
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def display_pareto_solutions(self, pareto_df, objectives):
        """Display Pareto solutions"""
        self.results_text.delete('1.0', tk.END)
        
        text = f"PARETO FRONTIER\n"
        text += "=" * 40 + "\n\n"
        text += f"Solutions: {len(pareto_df)}\n\n"
        
        for idx, row in pareto_df.iterrows():
            text += f"Solution #{row.get('pareto_rank', idx+1)}:\n"
            for obj in objectives:
                if obj in row:
                    value = row[obj]
                    if obj == 'npv':
                        value = -value  # Convert back to positive
                    text += f"  {obj.title()}: {value:.2f}\n"
            text += "\n"
        
        self.results_text.insert('1.0', text)
    
    def clear_results(self):
        """Clear results"""
        self.results_text.delete('1.0', tk.END)
        self.ax.clear()
        self.ax.set_xlabel('Duration (days)')
        self.ax.set_ylabel('Cost ($)')
        self.ax.set_title('Pareto Frontier')
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def set_analyzer(self, analyzer):
        """Update analyzer"""
        self.cpm_analyzer = analyzer
