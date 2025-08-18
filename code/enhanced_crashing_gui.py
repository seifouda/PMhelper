#!/usr/bin/env python3
"""
Enhanced Project Crashing GUI Components

This module provides GUI components for the enhanced project crashing features.
It extends the existing CPMDesktopApp without modifying the original code.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
import threading
import queue
import time

# Import the enhanced crashing modules
from enhanced_project_crashing import (
    EnhancedProjectCrashing, 
    EnhancedRCPSProjectCrashing,
    CrashingStrategy, 
    OptimizationObjective, 
    CrashingResult,
    compare_crashing_results,
    generate_crashing_report
)


class EnhancedCrashingGUIManager:
    """
    Manager for Enhanced Project Crashing GUI Components
    
    This class extends the existing CPMDesktopApp with enhanced crashing features
    without modifying the original code.
    """
    
    def __init__(self, app_instance):
        """
        Initialize with reference to the main app instance
        
        Args:
            app_instance: Reference to CPMDesktopApp instance
        """
        self.app = app_instance
        self.enhanced_engine = None
        self.enhanced_rcps_engine = None
        self.current_results = []
        self.comparison_window = None
        
        # Initialize enhanced engines
        if hasattr(self.app, 'current_analyzer') and self.app.current_analyzer:
            self.enhanced_engine = EnhancedProjectCrashing(self.app.current_analyzer)
            self.enhanced_rcps_engine = EnhancedRCPSProjectCrashing(self.app.current_analyzer)
    
    def add_enhanced_crashing_tabs(self):
        """Add enhanced crashing tabs to the existing notebook"""
        if hasattr(self.app, 'notebook'):
            # Add Enhanced Project Crashing tab
            self.create_enhanced_crashing_tab()
            # Add Enhanced RCPS Project Crashing tab
            self.create_enhanced_rcps_crashing_tab()
            # Add Results Comparison tab
            self.create_results_comparison_tab()
    
    def create_enhanced_crashing_tab(self):
        """Create the Enhanced Project Crashing tab"""
        enhanced_frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(enhanced_frame, text="Enhanced Crashing")
        
        # Create main sections
        self._create_enhanced_crashing_controls(enhanced_frame)
        self._create_enhanced_crashing_results(enhanced_frame)
        self._create_enhanced_crashing_visualization(enhanced_frame)
    
    def _create_enhanced_crashing_controls(self, parent):
        """Create controls section for enhanced crashing"""
        controls_frame = ttk.LabelFrame(parent, text="Enhanced Crashing Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input parameters frame
        params_frame = ttk.Frame(controls_frame)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Target Duration
        ttk.Label(params_frame, text="Target Duration:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.enhanced_target_duration_var = tk.StringVar(value="25")
        ttk.Entry(params_frame, textvariable=self.enhanced_target_duration_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # Strategy Selection
        ttk.Label(params_frame, text="Strategy:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.enhanced_strategy_var = tk.StringVar(value=CrashingStrategy.LOWEST_COST.value)
        strategy_combo = ttk.Combobox(params_frame, textvariable=self.enhanced_strategy_var, width=15)
        strategy_combo['values'] = [s.value for s in CrashingStrategy]
        strategy_combo.grid(row=0, column=3, padx=5, pady=2)
        strategy_combo.state(['readonly'])
        
        # Objective Selection
        ttk.Label(params_frame, text="Objective:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.enhanced_objective_var = tk.StringVar(value=OptimizationObjective.MINIMIZE_COST.value)
        objective_combo = ttk.Combobox(params_frame, textvariable=self.enhanced_objective_var, width=15)
        objective_combo['values'] = [o.value for o in OptimizationObjective]
        objective_combo.grid(row=1, column=1, padx=5, pady=2)
        objective_combo.state(['readonly'])
        
        # Max Budget
        ttk.Label(params_frame, text="Max Budget:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.enhanced_budget_var = tk.StringVar(value="")
        ttk.Entry(params_frame, textvariable=self.enhanced_budget_var, width=10).grid(row=1, column=3, padx=5, pady=2)
        
        # Advanced parameters frame
        advanced_frame = ttk.LabelFrame(controls_frame, text="Advanced Parameters")
        advanced_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Max Iterations
        ttk.Label(advanced_frame, text="Max Iterations:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.enhanced_max_iterations_var = tk.StringVar(value="1000")
        ttk.Entry(advanced_frame, textvariable=self.enhanced_max_iterations_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # Step Size
        ttk.Label(advanced_frame, text="Step Size:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.enhanced_step_size_var = tk.StringVar(value="1.0")
        ttk.Entry(advanced_frame, textvariable=self.enhanced_step_size_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        # Early Termination
        self.enhanced_early_termination_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_frame, 
            text="Early Termination", 
            variable=self.enhanced_early_termination_var
        ).grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        
        # Buttons frame
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Run Enhanced Crashing button
        ttk.Button(
            buttons_frame, 
            text="Run Enhanced Crashing",
            command=self.run_enhanced_crashing
        ).pack(side=tk.LEFT, padx=5)
        
        # Export Results button
        ttk.Button(
            buttons_frame, 
            text="Export Results",
            command=self.export_enhanced_results
        ).pack(side=tk.LEFT, padx=5)
        
        # Clear Results button
        ttk.Button(
            buttons_frame, 
            text="Clear Results",
            command=self.clear_enhanced_results
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_enhanced_crashing_results(self, parent):
        """Create results section for enhanced crashing"""
        results_frame = ttk.LabelFrame(parent, text="Enhanced Crashing Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for different result views
        self.enhanced_results_notebook = ttk.Notebook(results_frame)
        self.enhanced_results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(self.enhanced_results_notebook)
        self.enhanced_results_notebook.add(summary_frame, text="Summary")
        
        self.enhanced_summary_text = scrolledtext.ScrolledText(
            summary_frame, wrap=tk.WORD, height=10, width=80
        )
        self.enhanced_summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Detailed Log tab
        log_frame = ttk.Frame(self.enhanced_results_notebook)
        self.enhanced_results_notebook.add(log_frame, text="Detailed Log")
        
        self.enhanced_log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, height=10, width=80
        )
        self.enhanced_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Metrics tab
        metrics_frame = ttk.Frame(self.enhanced_results_notebook)
        self.enhanced_results_notebook.add(metrics_frame, text="Metrics")
        
        self.enhanced_metrics_text = scrolledtext.ScrolledText(
            metrics_frame, wrap=tk.WORD, height=10, width=80
        )
        self.enhanced_metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_enhanced_crashing_visualization(self, parent):
        """Create visualization section for enhanced crashing"""
        viz_frame = ttk.LabelFrame(parent, text="Enhanced Crashing Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure
        self.enhanced_fig, self.enhanced_axes = plt.subplots(2, 2, figsize=(12, 8))
        self.enhanced_fig.suptitle("Enhanced Crashing Analysis")
        
        # Cost vs Duration plot
        self.enhanced_axes[0, 0].set_title("Cost vs Duration Reduction")
        self.enhanced_axes[0, 0].set_xlabel("Duration Reduction")
        self.enhanced_axes[0, 0].set_ylabel("Crash Cost")
        
        # Efficiency plot
        self.enhanced_axes[0, 1].set_title("Crashing Efficiency")
        self.enhanced_axes[0, 1].set_xlabel("Iteration")
        self.enhanced_axes[0, 1].set_ylabel("Efficiency Score")
        
        # Activity crash frequency
        self.enhanced_axes[1, 0].set_title("Activity Crash Frequency")
        self.enhanced_axes[1, 0].set_xlabel("Activities")
        self.enhanced_axes[1, 0].set_ylabel("Times Crashed")
        
        # Cumulative cost
        self.enhanced_axes[1, 1].set_title("Cumulative Cost")
        self.enhanced_axes[1, 1].set_xlabel("Iteration")
        self.enhanced_axes[1, 1].set_ylabel("Cumulative Cost")
        
        # Embed in tkinter
        self.enhanced_canvas = FigureCanvasTkAgg(self.enhanced_fig, viz_frame)
        self.enhanced_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_enhanced_rcps_crashing_tab(self):
        """Create the Enhanced RCPS Project Crashing tab"""
        enhanced_rcps_frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(enhanced_rcps_frame, text="Enhanced RCPS Crashing")
        
        # Create main sections
        self._create_enhanced_rcps_controls(enhanced_rcps_frame)
        self._create_enhanced_rcps_results(enhanced_rcps_frame)
        self._create_enhanced_rcps_visualization(enhanced_rcps_frame)
    
    def _create_enhanced_rcps_controls(self, parent):
        """Create controls section for enhanced RCPS crashing"""
        controls_frame = ttk.LabelFrame(parent, text="Enhanced RCPS Crashing Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input parameters frame
        params_frame = ttk.Frame(controls_frame)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Target Duration
        ttk.Label(params_frame, text="Target Duration:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.enhanced_rcps_target_duration_var = tk.StringVar(value="25")
        ttk.Entry(params_frame, textvariable=self.enhanced_rcps_target_duration_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # Resource Limit
        ttk.Label(params_frame, text="Resource Limit:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.enhanced_rcps_resource_limit_var = tk.StringVar(value="5")
        ttk.Entry(params_frame, textvariable=self.enhanced_rcps_resource_limit_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        # Priority Rule
        ttk.Label(params_frame, text="Priority Rule:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.enhanced_rcps_priority_var = tk.StringVar(value="minimum_slack")
        priority_combo = ttk.Combobox(params_frame, textvariable=self.enhanced_rcps_priority_var, width=15)
        priority_combo['values'] = ['minimum_slack', 'shortest_duration', 'earliest_start']
        priority_combo.grid(row=1, column=1, padx=5, pady=2)
        priority_combo.state(['readonly'])
        
        # Strategy
        ttk.Label(params_frame, text="Strategy:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.enhanced_rcps_strategy_var = tk.StringVar(value=CrashingStrategy.RESOURCE_AWARE.value)
        strategy_combo = ttk.Combobox(params_frame, textvariable=self.enhanced_rcps_strategy_var, width=15)
        strategy_combo['values'] = [s.value for s in CrashingStrategy]
        strategy_combo.grid(row=1, column=3, padx=5, pady=2)
        strategy_combo.state(['readonly'])
        
        # Advanced parameters frame
        advanced_frame = ttk.LabelFrame(controls_frame, text="Advanced RCPS Parameters")
        advanced_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Max Budget
        ttk.Label(advanced_frame, text="Max Budget:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.enhanced_rcps_budget_var = tk.StringVar(value="")
        ttk.Entry(advanced_frame, textvariable=self.enhanced_rcps_budget_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # Resource Efficiency Weight
        ttk.Label(advanced_frame, text="Resource Weight:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.enhanced_rcps_weight_var = tk.StringVar(value="0.3")
        ttk.Entry(advanced_frame, textvariable=self.enhanced_rcps_weight_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        # Max Iterations
        ttk.Label(advanced_frame, text="Max Iterations:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.enhanced_rcps_max_iterations_var = tk.StringVar(value="1000")
        ttk.Entry(advanced_frame, textvariable=self.enhanced_rcps_max_iterations_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Run Enhanced RCPS Crashing button
        ttk.Button(
            buttons_frame, 
            text="Run Enhanced RCPS Crashing",
            command=self.run_enhanced_rcps_crashing
        ).pack(side=tk.LEFT, padx=5)
        
        # Export Results button
        ttk.Button(
            buttons_frame, 
            text="Export RCPS Results",
            command=self.export_enhanced_rcps_results
        ).pack(side=tk.LEFT, padx=5)
        
        # Show Resource Analysis button
        ttk.Button(
            buttons_frame, 
            text="Resource Analysis",
            command=self.show_resource_analysis
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_enhanced_rcps_results(self, parent):
        """Create results section for enhanced RCPS crashing"""
        results_frame = ttk.LabelFrame(parent, text="Enhanced RCPS Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for different result views
        self.enhanced_rcps_results_notebook = ttk.Notebook(results_frame)
        self.enhanced_rcps_results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(self.enhanced_rcps_results_notebook)
        self.enhanced_rcps_results_notebook.add(summary_frame, text="Summary")
        
        self.enhanced_rcps_summary_text = scrolledtext.ScrolledText(
            summary_frame, wrap=tk.WORD, height=10, width=80
        )
        self.enhanced_rcps_summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Resource Utilization tab
        resource_frame = ttk.Frame(self.enhanced_rcps_results_notebook)
        self.enhanced_rcps_results_notebook.add(resource_frame, text="Resource Analysis")
        
        self.enhanced_rcps_resource_text = scrolledtext.ScrolledText(
            resource_frame, wrap=tk.WORD, height=10, width=80
        )
        self.enhanced_rcps_resource_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Detailed Log tab
        log_frame = ttk.Frame(self.enhanced_rcps_results_notebook)
        self.enhanced_rcps_results_notebook.add(log_frame, text="Detailed Log")
        
        self.enhanced_rcps_log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, height=10, width=80
        )
        self.enhanced_rcps_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_enhanced_rcps_visualization(self, parent):
        """Create visualization section for enhanced RCPS crashing"""
        viz_frame = ttk.LabelFrame(parent, text="Enhanced RCPS Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure
        self.enhanced_rcps_fig, self.enhanced_rcps_axes = plt.subplots(2, 2, figsize=(12, 8))
        self.enhanced_rcps_fig.suptitle("Enhanced RCPS Crashing Analysis")
        
        # Resource utilization over time
        self.enhanced_rcps_axes[0, 0].set_title("Resource Utilization Over Time")
        self.enhanced_rcps_axes[0, 0].set_xlabel("Time Period")
        self.enhanced_rcps_axes[0, 0].set_ylabel("Resource Usage")
        
        # Duration vs Resource Trade-off
        self.enhanced_rcps_axes[0, 1].set_title("Duration vs Resource Trade-off")
        self.enhanced_rcps_axes[0, 1].set_xlabel("Project Duration")
        self.enhanced_rcps_axes[0, 1].set_ylabel("Peak Resource Usage")
        
        # Cost-Duration-Resource 3D view (projected to 2D)
        self.enhanced_rcps_axes[1, 0].set_title("Cost vs Duration (Resource-Aware)")
        self.enhanced_rcps_axes[1, 0].set_xlabel("Duration Reduction")
        self.enhanced_rcps_axes[1, 0].set_ylabel("Crash Cost")
        
        # Resource efficiency
        self.enhanced_rcps_axes[1, 1].set_title("Resource Efficiency by Activity")
        self.enhanced_rcps_axes[1, 1].set_xlabel("Activities")
        self.enhanced_rcps_axes[1, 1].set_ylabel("Resource Efficiency")
        
        # Embed in tkinter
        self.enhanced_rcps_canvas = FigureCanvasTkAgg(self.enhanced_rcps_fig, viz_frame)
        self.enhanced_rcps_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_results_comparison_tab(self):
        """Create the Results Comparison tab"""
        comparison_frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(comparison_frame, text="Results Comparison")
        
        # Controls frame
        controls_frame = ttk.LabelFrame(comparison_frame, text="Comparison Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame, 
            text="Compare All Results",
            command=self.compare_all_results
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame, 
            text="Generate Report",
            command=self.generate_comparison_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame, 
            text="Clear Comparison",
            command=self.clear_comparison
        ).pack(side=tk.LEFT, padx=5)
        
        # Results display
        results_frame = ttk.LabelFrame(comparison_frame, text="Comparison Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.comparison_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, height=15, width=80
        )
        self.comparison_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Comparison visualization
        viz_frame = ttk.LabelFrame(comparison_frame, text="Comparison Visualization")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.comparison_fig, self.comparison_axes = plt.subplots(1, 2, figsize=(12, 5))
        self.comparison_fig.suptitle("Results Comparison")
        
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_fig, viz_frame)
        self.comparison_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def run_enhanced_crashing(self):
        """Run enhanced project crashing"""
        try:
            # Validate analyzer
            if not self._validate_analyzer():
                return
            
            # Get parameters
            target_duration = float(self.enhanced_target_duration_var.get())
            strategy = CrashingStrategy(self.enhanced_strategy_var.get())
            objective = OptimizationObjective(self.enhanced_objective_var.get())
            max_iterations = int(self.enhanced_max_iterations_var.get())
            step_size = float(self.enhanced_step_size_var.get())
            early_termination = self.enhanced_early_termination_var.get()
            
            # Get budget (optional)
            max_budget = None
            budget_str = self.enhanced_budget_var.get().strip()
            if budget_str:
                max_budget = float(budget_str)
            
            # Clear previous results
            self._clear_enhanced_crashing_display()
            
            # Run enhanced crashing
            self.enhanced_summary_text.insert(tk.END, "Running Enhanced Project Crashing...\n")
            self.enhanced_summary_text.update()
            
            result = self.enhanced_engine.enhanced_crash_project(
                target_duration=target_duration,
                strategy=strategy,
                objective=objective,
                max_budget=max_budget,
                max_iterations=max_iterations,
                step_size=step_size,
                early_termination=early_termination
            )
            
            # Store result
            self.current_results.append(('Enhanced CPM', result))
            
            # Display results
            self._display_enhanced_crashing_results(result)
            
            messagebox.showinfo("Success", "Enhanced project crashing completed successfully!")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Enhanced crashing failed: {str(e)}")
    
    def run_enhanced_rcps_crashing(self):
        """Run enhanced RCPS project crashing"""
        try:
            # Validate analyzer
            if not self._validate_analyzer():
                return
            
            # Get parameters
            target_duration = float(self.enhanced_rcps_target_duration_var.get())
            resource_limit = int(self.enhanced_rcps_resource_limit_var.get())
            priority_rule = self.enhanced_rcps_priority_var.get()
            strategy = CrashingStrategy(self.enhanced_rcps_strategy_var.get())
            max_iterations = int(self.enhanced_rcps_max_iterations_var.get())
            resource_weight = float(self.enhanced_rcps_weight_var.get())
            
            # Get budget (optional)
            max_budget = None
            budget_str = self.enhanced_rcps_budget_var.get().strip()
            if budget_str:
                max_budget = float(budget_str)
            
            # Clear previous results
            self._clear_enhanced_rcps_display()
            
            # Run enhanced RCPS crashing
            self.enhanced_rcps_summary_text.insert(tk.END, "Running Enhanced RCPS Project Crashing...\n")
            self.enhanced_rcps_summary_text.update()
            
            result = self.enhanced_rcps_engine.enhanced_rcps_crash_project(
                target_duration=target_duration,
                resource_limit=resource_limit,
                priority_rule=priority_rule,
                strategy=strategy,
                max_budget=max_budget,
                max_iterations=max_iterations,
                resource_efficiency_weight=resource_weight
            )
            
            # Store result
            self.current_results.append(('Enhanced RCPS', result))
            
            # Display results
            self._display_enhanced_rcps_results(result)
            
            messagebox.showinfo("Success", "Enhanced RCPS project crashing completed successfully!")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Enhanced RCPS crashing failed: {str(e)}")
    
    def _validate_analyzer(self):
        """Validate that analyzer is available and has data"""
        if not hasattr(self.app, 'current_analyzer') or not self.app.current_analyzer:
            messagebox.showwarning("Warning", "Please run the analysis first.")
            return False
        
        if not hasattr(self.app.current_analyzer, 'G') or not self.app.current_analyzer.G:
            messagebox.showwarning("Warning", "No network graph available. Run analysis first.")
            return False
        
        # Update engines with current analyzer
        self.enhanced_engine = EnhancedProjectCrashing(self.app.current_analyzer)
        self.enhanced_rcps_engine = EnhancedRCPSProjectCrashing(self.app.current_analyzer)
        
        return True
    
    def _clear_enhanced_crashing_display(self):
        """Clear enhanced crashing display"""
        self.enhanced_summary_text.delete(1.0, tk.END)
        self.enhanced_log_text.delete(1.0, tk.END)
        self.enhanced_metrics_text.delete(1.0, tk.END)
        
        # Clear plots
        for ax in self.enhanced_axes.flat:
            ax.clear()
        self.enhanced_canvas.draw()
    
    def _clear_enhanced_rcps_display(self):
        """Clear enhanced RCPS display"""
        self.enhanced_rcps_summary_text.delete(1.0, tk.END)
        self.enhanced_rcps_resource_text.delete(1.0, tk.END)
        self.enhanced_rcps_log_text.delete(1.0, tk.END)
        
        # Clear plots
        for ax in self.enhanced_rcps_axes.flat:
            ax.clear()
        self.enhanced_rcps_canvas.draw()
    
    def _display_enhanced_crashing_results(self, result: CrashingResult):
        """Display enhanced crashing results"""
        # Summary
        summary_text = generate_crashing_report(result)
        self.enhanced_summary_text.insert(tk.END, summary_text)
        
        # Detailed log
        log_lines = ["DETAILED CRASH LOG", "=" * 50, ""]
        for i, entry in enumerate(result.crash_log, 1):
            log_lines.append(f"Step {i}: {entry['activity']} ({entry['old_duration']:.1f} -> {entry['new_duration']:.1f})")
            log_lines.append(f"  Cost: ${entry['crash_cost']:.2f}, Strategy: {entry.get('strategy', 'N/A')}")
            log_lines.append(f"  Efficiency: {entry.get('efficiency_score', 0):.4f}")
            log_lines.append("")
        
        self.enhanced_log_text.insert(tk.END, "\n".join(log_lines))
        
        # Metrics
        metrics_lines = ["COMPREHENSIVE METRICS", "=" * 50, ""]
        for key, value in result.efficiency_metrics.items():
            if isinstance(value, float):
                metrics_lines.append(f"{key.replace('_', ' ').title()}: {value:.4f}")
            else:
                metrics_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        self.enhanced_metrics_text.insert(tk.END, "\n".join(metrics_lines))
        
        # Visualizations
        self._create_enhanced_crashing_plots(result)
    
    def _display_enhanced_rcps_results(self, result: CrashingResult):
        """Display enhanced RCPS results"""
        # Summary
        summary_text = generate_crashing_report(result)
        self.enhanced_rcps_summary_text.insert(tk.END, summary_text)
        
        # Resource analysis
        if result.resource_utilization:
            resource_lines = ["RESOURCE UTILIZATION ANALYSIS", "=" * 50, ""]
            resource_lines.append(f"Average Utilization: {result.resource_utilization.get('average_utilization', 0):.2f}")
            resource_lines.append(f"Peak Utilization: {result.resource_utilization.get('max_utilization', 0):.2f}")
            resource_lines.append(f"Resource Limit: {result.resource_utilization.get('resource_limit', 0)}")
            resource_lines.append(f"Utilization %: {result.resource_utilization.get('utilization_percentage', 0):.1f}%")
            resource_lines.append(f"Over-limit Periods: {result.resource_utilization.get('over_limit_periods', 0)}")
            resource_lines.append("")
            
            # Time periods detail
            if 'time_periods' in result.resource_utilization:
                resource_lines.append("RESOURCE USAGE BY TIME PERIOD:")
                for t, usage in result.resource_utilization['time_periods'].items():
                    status = " (OVER LIMIT)" if usage > result.resource_utilization.get('resource_limit', 0) else ""
                    resource_lines.append(f"  Period {t}: {usage:.1f}{status}")
            
            self.enhanced_rcps_resource_text.insert(tk.END, "\n".join(resource_lines))
        
        # Detailed log
        log_lines = ["DETAILED RCPS CRASH LOG", "=" * 50, ""]
        for i, entry in enumerate(result.crash_log, 1):
            log_lines.append(f"Step {i}: {entry['activity']} ({entry['old_duration']:.1f} -> {entry['new_duration']:.1f})")
            log_lines.append(f"  Cost: ${entry['crash_cost']:.2f}")
            log_lines.append(f"  Duration Reduction: {entry.get('duration_reduction', 0):.2f}")
            log_lines.append(f"  Resource Efficiency: {entry.get('resource_efficiency', 0):.4f}")
            if 'rcps_schedule_info' in entry:
                info = entry['rcps_schedule_info']
                log_lines.append(f"  Schedule: Start={info.get('actual_start', 0)}, Finish={info.get('actual_finish', 0)}")
            log_lines.append("")
        
        self.enhanced_rcps_log_text.insert(tk.END, "\n".join(log_lines))
        
        # Visualizations
        self._create_enhanced_rcps_plots(result)
    
    def _create_enhanced_crashing_plots(self, result: CrashingResult):
        """Create visualization plots for enhanced crashing"""
        # Clear previous plots
        for ax in self.enhanced_axes.flat:
            ax.clear()
        
        # Plot 1: Cost vs Duration Reduction
        ax1 = self.enhanced_axes[0, 0]
        ax1.scatter([result.duration_reduction], [result.total_crash_cost], 
                   color='red', s=100, label='Current Result')
        ax1.set_title("Cost vs Duration Reduction")
        ax1.set_xlabel("Duration Reduction")
        ax1.set_ylabel("Crash Cost ($)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Efficiency over iterations
        if result.crash_log:
            ax2 = self.enhanced_axes[0, 1]
            iterations = [entry['iteration'] for entry in result.crash_log]
            efficiencies = [entry.get('efficiency_score', 0) for entry in result.crash_log]
            ax2.plot(iterations, efficiencies, 'b-o', linewidth=2, markersize=4)
            ax2.set_title("Crashing Efficiency Over Time")
            ax2.set_xlabel("Iteration")
            ax2.set_ylabel("Efficiency Score")
            ax2.grid(True, alpha=0.3)
        
        # Plot 3: Activity crash frequency
        if result.crash_log:
            ax3 = self.enhanced_axes[1, 0]
            activity_counts = {}
            for entry in result.crash_log:
                activity = entry['activity']
                activity_counts[activity] = activity_counts.get(activity, 0) + 1
            
            activities = list(activity_counts.keys())
            counts = list(activity_counts.values())
            ax3.bar(activities, counts, color='lightblue', edgecolor='navy')
            ax3.set_title("Activity Crash Frequency")
            ax3.set_xlabel("Activities")
            ax3.set_ylabel("Times Crashed")
            ax3.tick_params(axis='x', rotation=45)
        
        # Plot 4: Cumulative cost
        if result.crash_log:
            ax4 = self.enhanced_axes[1, 1]
            iterations = [entry['iteration'] for entry in result.crash_log]
            cumulative_costs = [entry['cumulative_cost'] for entry in result.crash_log]
            ax4.plot(iterations, cumulative_costs, 'g-o', linewidth=2, markersize=4)
            ax4.set_title("Cumulative Crash Cost")
            ax4.set_xlabel("Iteration")
            ax4.set_ylabel("Cumulative Cost ($)")
            ax4.grid(True, alpha=0.3)
        
        self.enhanced_fig.tight_layout()
        self.enhanced_canvas.draw()
    
    def _create_enhanced_rcps_plots(self, result: CrashingResult):
        """Create visualization plots for enhanced RCPS crashing"""
        # Clear previous plots
        for ax in self.enhanced_rcps_axes.flat:
            ax.clear()
        
        # Plot 1: Resource utilization over time
        if result.resource_utilization and 'time_periods' in result.resource_utilization:
            ax1 = self.enhanced_rcps_axes[0, 0]
            time_periods = result.resource_utilization['time_periods']
            resource_limit = result.resource_utilization.get('resource_limit', 0)
            
            times = list(time_periods.keys())
            usages = list(time_periods.values())
            
            ax1.bar(times, usages, color='lightcoral', alpha=0.7, label='Resource Usage')
            ax1.axhline(y=resource_limit, color='red', linestyle='--', linewidth=2, label=f'Limit ({resource_limit})')
            ax1.set_title("Resource Utilization Over Time")
            ax1.set_xlabel("Time Period")
            ax1.set_ylabel("Resource Usage")
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Plot 2: Duration vs Resource trade-off
        ax2 = self.enhanced_rcps_axes[0, 1]
        if result.resource_utilization:
            max_util = result.resource_utilization.get('max_utilization', 0)
            ax2.scatter([result.final_duration], [max_util], 
                       color='blue', s=100, label='Final State')
            ax2.scatter([result.original_duration], [max_util], 
                       color='gray', s=100, label='Original State', alpha=0.7)
        ax2.set_title("Duration vs Peak Resource Usage")
        ax2.set_xlabel("Project Duration")
        ax2.set_ylabel("Peak Resource Usage")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Cost vs Duration (Resource-aware)
        ax3 = self.enhanced_rcps_axes[1, 0]
        ax3.scatter([result.duration_reduction], [result.total_crash_cost], 
                   color='green', s=100, label='RCPS Result')
        ax3.set_title("Cost vs Duration (Resource-Aware)")
        ax3.set_xlabel("Duration Reduction")
        ax3.set_ylabel("Crash Cost ($)")
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Resource efficiency by activity
        if result.crash_log:
            ax4 = self.enhanced_rcps_axes[1, 1]
            activities = []
            efficiencies = []
            for entry in result.crash_log:
                if entry['activity'] not in activities:
                    activities.append(entry['activity'])
                    efficiencies.append(entry.get('resource_efficiency', 0))
            
            ax4.bar(activities, efficiencies, color='lightgreen', edgecolor='darkgreen')
            ax4.set_title("Resource Efficiency by Activity")
            ax4.set_xlabel("Activities")
            ax4.set_ylabel("Resource Efficiency")
            ax4.tick_params(axis='x', rotation=45)
        
        self.enhanced_rcps_fig.tight_layout()
        self.enhanced_rcps_canvas.draw()
    
    def compare_all_results(self):
        """Compare all stored results"""
        if len(self.current_results) < 2:
            messagebox.showinfo("Info", "Need at least 2 results to compare.")
            return
        
        try:
            # Extract just the results for comparison
            results = [result for _, result in self.current_results]
            comparison = compare_crashing_results(results)
            
            # Display comparison
            self._display_comparison_results(comparison)
            
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
    
    def _display_comparison_results(self, comparison: Dict[str, Any]):
        """Display comparison results"""
        self.comparison_text.delete(1.0, tk.END)
        
        lines = [
            "ENHANCED CRASHING RESULTS COMPARISON",
            "=" * 60,
            "",
            f"Total Results Compared: {comparison['total_results']}",
            "",
            "BEST PERFORMERS:",
        ]
        
        if 'best_cost' in comparison:
            lines.append(f"  Lowest Cost: ${comparison['best_cost'].total_crash_cost:.2f} "
                        f"(Duration: {comparison['best_cost'].final_duration})")
        
        if 'best_duration' in comparison:
            lines.append(f"  Shortest Duration: {comparison['best_duration'].final_duration} "
                        f"(Cost: ${comparison['best_duration'].total_crash_cost:.2f})")
        
        if 'best_efficiency' in comparison:
            lines.append(f"  Best Efficiency: {comparison['best_efficiency'].efficiency_metrics.get('efficiency_score', 0):.4f}")
        
        if 'fastest_computation' in comparison:
            lines.append(f"  Fastest Computation: {comparison['fastest_computation'].computation_time:.2f}s")
        
        lines.extend([
            "",
            "SUMMARY STATISTICS:",
        ])
        
        if 'summary_stats' in comparison:
            stats = comparison['summary_stats']
            lines.append(f"  Average Crash Cost: ${stats['avg_crash_cost']:.2f}")
            lines.append(f"  Average Final Duration: {stats['avg_final_duration']:.2f}")
            lines.append(f"  Average Iterations: {stats['avg_iterations']:.1f}")
            lines.append(f"  Targets Achieved: {stats['targets_achieved']}/{comparison['total_results']}")
            lines.append(f"  Success Rate: {stats['success_rate']:.1f}%")
        
        lines.extend([
            "",
            "DETAILED RESULTS:",
            ""
        ])
        
        for i, (method, result) in enumerate(self.current_results, 1):
            lines.append(f"{i}. {method}:")
            lines.append(f"   Duration: {result.original_duration} -> {result.final_duration}")
            lines.append(f"   Cost: ${result.total_crash_cost:.2f}")
            lines.append(f"   Target Achieved: {'✓' if result.target_achieved else '✗'}")
            lines.append(f"   Iterations: {result.iterations_used}")
            lines.append("")
        
        self.comparison_text.insert(tk.END, "\n".join(lines))
        
        # Create comparison plots
        self._create_comparison_plots()
    
    def _create_comparison_plots(self):
        """Create comparison visualization plots"""
        if not self.current_results:
            return
        
        # Clear previous plots
        for ax in self.comparison_axes:
            ax.clear()
        
        # Extract data for plotting
        methods = [method for method, _ in self.current_results]
        costs = [result.total_crash_cost for _, result in self.current_results]
        durations = [result.final_duration for _, result in self.current_results]
        
        # Plot 1: Cost comparison
        ax1 = self.comparison_axes[0]
        bars1 = ax1.bar(methods, costs, color=['lightcoral', 'lightblue', 'lightgreen', 'lightyellow'][:len(methods)])
        ax1.set_title("Crash Cost Comparison")
        ax1.set_ylabel("Total Crash Cost ($)")
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, cost in zip(bars1, costs):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${cost:.0f}', ha='center', va='bottom')
        
        # Plot 2: Duration comparison
        ax2 = self.comparison_axes[1]
        bars2 = ax2.bar(methods, durations, color=['lightcoral', 'lightblue', 'lightgreen', 'lightyellow'][:len(methods)])
        ax2.set_title("Final Duration Comparison")
        ax2.set_ylabel("Final Duration")
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, duration in zip(bars2, durations):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{duration:.1f}', ha='center', va='bottom')
        
        self.comparison_fig.tight_layout()
        self.comparison_canvas.draw()
    
    def generate_comparison_report(self):
        """Generate and display a comprehensive comparison report"""
        if not self.current_results:
            messagebox.showinfo("Info", "No results available for report generation.")
            return
        
        try:
            # Create a new window for the report
            report_window = tk.Toplevel(self.app.root)
            report_window.title("Enhanced Crashing Comparison Report")
            report_window.geometry("800x600")
            
            # Create scrolled text widget
            report_text = scrolledtext.ScrolledText(
                report_window, wrap=tk.WORD, width=100, height=40
            )
            report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Generate comprehensive report
            report_lines = [
                "ENHANCED PROJECT CRASHING COMPREHENSIVE REPORT",
                "=" * 70,
                f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Total Analysis Runs: {len(self.current_results)}",
                "",
            ]
            
            # Individual result reports
            for i, (method, result) in enumerate(self.current_results, 1):
                report_lines.extend([
                    f"ANALYSIS {i}: {method.upper()}",
                    "-" * 50,
                    generate_crashing_report(result),
                    "",
                ])
            
            # Comparative analysis
            if len(self.current_results) > 1:
                results = [result for _, result in self.current_results]
                comparison = compare_crashing_results(results)
                
                report_lines.extend([
                    "COMPARATIVE ANALYSIS",
                    "=" * 70,
                    "",
                    "PERFORMANCE RANKINGS:",
                    ""
                ])
                
                # Rank by different criteria
                cost_ranked = sorted(enumerate(results), key=lambda x: x[1].total_crash_cost)
                duration_ranked = sorted(enumerate(results), key=lambda x: x[1].final_duration)
                efficiency_ranked = sorted(enumerate(results), key=lambda x: x[1].efficiency_metrics.get('efficiency_score', 0), reverse=True)
                
                report_lines.extend([
                    "By Lowest Cost:",
                    *[f"  {i+1}. {self.current_results[idx][0]}: ${result.total_crash_cost:.2f}" 
                      for i, (idx, result) in enumerate(cost_ranked)],
                    "",
                    "By Shortest Duration:",
                    *[f"  {i+1}. {self.current_results[idx][0]}: {result.final_duration:.2f}" 
                      for i, (idx, result) in enumerate(duration_ranked)],
                    "",
                    "By Best Efficiency:",
                    *[f"  {i+1}. {self.current_results[idx][0]}: {result.efficiency_metrics.get('efficiency_score', 0):.4f}" 
                      for i, (idx, result) in enumerate(efficiency_ranked)],
                    ""
                ])
            
            # Insert report into text widget
            report_text.insert(tk.END, "\n".join(report_lines))
            
            # Add export button
            export_frame = ttk.Frame(report_window)
            export_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Button(
                export_frame,
                text="Export Report to File",
                command=lambda: self._export_report_to_file("\n".join(report_lines))
            ).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Report generation failed: {str(e)}")
    
    def _export_report_to_file(self, report_content: str):
        """Export report to a text file"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(report_content)
                messagebox.showinfo("Success", f"Report exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_enhanced_results(self):
        """Export enhanced crashing results"""
        if not self.current_results:
            messagebox.showinfo("Info", "No results to export.")
            return
        
        # Find the latest enhanced CPM result
        enhanced_result = None
        for method, result in self.current_results:
            if 'Enhanced CPM' in method:
                enhanced_result = result
                break
        
        if enhanced_result:
            report = generate_crashing_report(enhanced_result)
            self._export_report_to_file(report)
        else:
            messagebox.showinfo("Info", "No enhanced CPM results to export.")
    
    def export_enhanced_rcps_results(self):
        """Export enhanced RCPS results"""
        if not self.current_results:
            messagebox.showinfo("Info", "No results to export.")
            return
        
        # Find the latest enhanced RCPS result
        enhanced_result = None
        for method, result in self.current_results:
            if 'Enhanced RCPS' in method:
                enhanced_result = result
                break
        
        if enhanced_result:
            report = generate_crashing_report(enhanced_result)
            self._export_report_to_file(report)
        else:
            messagebox.showinfo("Info", "No enhanced RCPS results to export.")
    
    def clear_enhanced_results(self):
        """Clear enhanced crashing results"""
        self._clear_enhanced_crashing_display()
        messagebox.showinfo("Info", "Enhanced crashing results cleared.")
    
    def clear_comparison(self):
        """Clear comparison results"""
        self.current_results.clear()
        self.comparison_text.delete(1.0, tk.END)
        
        # Clear plots
        for ax in self.comparison_axes:
            ax.clear()
        self.comparison_canvas.draw()
        
        messagebox.showinfo("Info", "All results cleared.")
    
    def show_resource_analysis(self):
        """Show detailed resource analysis window"""
        if not self.current_results:
            messagebox.showinfo("Info", "No results available for resource analysis.")
            return
        
        # Find RCPS results
        rcps_results = [result for method, result in self.current_results if 'RCPS' in method]
        
        if not rcps_results:
            messagebox.showinfo("Info", "No RCPS results available for resource analysis.")
            return
        
        # Create resource analysis window
        resource_window = tk.Toplevel(self.app.root)
        resource_window.title("Resource Utilization Analysis")
        resource_window.geometry("900x700")
        
        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Comprehensive Resource Analysis")
        
        # Analyze first RCPS result
        result = rcps_results[0]
        if result.resource_utilization:
            self._create_detailed_resource_plots(axes, result.resource_utilization)
        
        # Embed in window
        canvas = FigureCanvasTkAgg(fig, resource_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add summary text
        summary_frame = ttk.Frame(resource_window)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        summary_text = tk.Text(summary_frame, height=8, wrap=tk.WORD)
        summary_text.pack(fill=tk.X)
        
        if result.resource_utilization:
            summary_lines = [
                "RESOURCE UTILIZATION SUMMARY:",
                f"Average Utilization: {result.resource_utilization.get('average_utilization', 0):.2f}",
                f"Peak Utilization: {result.resource_utilization.get('max_utilization', 0):.2f}",
                f"Resource Limit: {result.resource_utilization.get('resource_limit', 0)}",
                f"Efficiency: {result.resource_utilization.get('utilization_percentage', 0):.1f}%",
                f"Over-limit Periods: {result.resource_utilization.get('over_limit_periods', 0)}"
            ]
            summary_text.insert(tk.END, "\n".join(summary_lines))
    
    def _create_detailed_resource_plots(self, axes, resource_data):
        """Create detailed resource utilization plots"""
        if 'time_periods' not in resource_data:
            return
        
        time_periods = resource_data['time_periods']
        resource_limit = resource_data.get('resource_limit', 0)
        
        times = list(time_periods.keys())
        usages = list(time_periods.values())
        
        # Plot 1: Resource usage over time
        ax1 = axes[0, 0]
        ax1.bar(times, usages, color='skyblue', alpha=0.7)
        ax1.axhline(y=resource_limit, color='red', linestyle='--', linewidth=2)
        ax1.set_title("Resource Usage Over Time")
        ax1.set_xlabel("Time Period")
        ax1.set_ylabel("Resource Usage")
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Utilization distribution
        ax2 = axes[0, 1]
        ax2.hist(usages, bins=min(10, len(set(usages))), color='lightgreen', alpha=0.7, edgecolor='black')
        ax2.axvline(x=resource_limit, color='red', linestyle='--', linewidth=2)
        ax2.set_title("Resource Usage Distribution")
        ax2.set_xlabel("Resource Usage")
        ax2.set_ylabel("Frequency")
        
        # Plot 3: Cumulative resource demand
        ax3 = axes[1, 0]
        cumulative = np.cumsum(usages)
        ax3.plot(times, cumulative, color='purple', linewidth=2, marker='o')
        ax3.set_title("Cumulative Resource Demand")
        ax3.set_xlabel("Time Period")
        ax3.set_ylabel("Cumulative Usage")
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Resource efficiency over time
        ax4 = axes[1, 1]
        efficiency = [min(usage / resource_limit, 1.0) if resource_limit > 0 else 0 for usage in usages]
        ax4.plot(times, efficiency, color='orange', linewidth=2, marker='s')
        ax4.axhline(y=1.0, color='red', linestyle='--', linewidth=2)
        ax4.set_title("Resource Efficiency Over Time")
        ax4.set_xlabel("Time Period")
        ax4.set_ylabel("Efficiency Ratio")
        ax4.set_ylim(0, max(1.2, max(efficiency) if efficiency else 1.2))
        ax4.grid(True, alpha=0.3)


# Utility function to integrate with existing app
def add_enhanced_crashing_to_app(app_instance):
    """
    Add enhanced crashing capabilities to an existing CPMDesktopApp instance
    
    Args:
        app_instance: The CPMDesktopApp instance to enhance
    """
    try:
        # Create the GUI manager
        gui_manager = EnhancedCrashingGUIManager(app_instance)
        
        # Add enhanced tabs
        gui_manager.add_enhanced_crashing_tabs()
        
        # Store reference in app for later use
        app_instance.enhanced_crashing_manager = gui_manager
        
        print("Enhanced Project Crashing features added successfully!")
        return gui_manager
        
    except Exception as e:
        print(f"Failed to add enhanced crashing features: {str(e)}")
        return None


if __name__ == "__main__":
    print("Enhanced Project Crashing GUI Module Loaded Successfully")
    print("Use add_enhanced_crashing_to_app(app_instance) to integrate with existing app")
