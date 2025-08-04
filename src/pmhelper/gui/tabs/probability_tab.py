#!/usr/bin/env python3
"""
Probability Tab Module

Displays PERT probability analysis including completion probability
calculations, risk analysis, and statistical visualizations.
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
    import numpy as np
    from scipy import stats
    MATPLOTLIB_AVAILABLE = True
    SCIPY_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    SCIPY_AVAILABLE = False

from pmhelper.utils.calculations import ProbabilityCalculations


class ProbabilityTab:
    """Probability analysis tab for PERT mode"""
    
    def __init__(self, notebook, main_window):
        self.notebook = notebook
        self.main_window = main_window
        self.results_data = None
        self.analysis_mode = None
        self.figure = None
        self.canvas = None
        
        self.create_tab()
    
    def create_tab(self):
        """Create the probability tab"""
        self.probability_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.probability_frame, text="Probability Analysis")
        
        if not MATPLOTLIB_AVAILABLE or not SCIPY_AVAILABLE:
            self.create_dependencies_message()
            return
        
        # Create main layout with paned window
        self.paned_window = ttk.PanedWindow(self.probability_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create control and analysis frame
        self.create_control_frame()
        
        # Create visualization frame
        self.create_plot_area()
    
    def create_dependencies_message(self):
        """Create message when required dependencies are not available"""
        message_frame = ttk.Frame(self.probability_frame)
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        missing = []
        if not MATPLOTLIB_AVAILABLE:
            missing.append("matplotlib")
        if not SCIPY_AVAILABLE:
            missing.append("scipy")
        
        message_text = f"Probability analysis requires {' and '.join(missing)}.\n"
        message_text += f"Please install {' and '.join(missing)} to view probability analysis."
        
        message_label = ttk.Label(
            message_frame,
            text=message_text,
            font=("Arial", 12),
            justify=tk.CENTER
        )
        message_label.pack(expand=True)
        
        install_button = ttk.Button(
            message_frame,
            text=f"Install {' and '.join(missing)}",
            command=lambda: self.install_dependencies(missing)
        )
        install_button.pack(pady=10)
    
    def install_dependencies(self, packages):
        """Attempt to install required dependencies"""
        try:
            import subprocess
            import sys
            
            result = messagebox.askyesno(
                "Install Dependencies",
                f"This will install {' and '.join(packages)} using pip. Continue?"
            )
            
            if result:
                for package in packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                messagebox.showinfo("Success", f"{' and '.join(packages)} installed successfully. Please restart the application.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install dependencies: {str(e)}")
    
    def create_control_frame(self):
        """Create control and analysis frame"""
        control_frame = ttk.Frame(self.paned_window, width=350)
        self.paned_window.add(control_frame, weight=1)
        
        # Project statistics frame
        self.create_statistics_frame(control_frame)
        
        # Probability calculator frame
        self.create_calculator_frame(control_frame)
        
        # Risk analysis frame
        self.create_risk_frame(control_frame)
    
    def create_statistics_frame(self, parent):
        """Create project statistics display frame"""
        stats_frame = ttk.LabelFrame(parent, text="Project Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Project duration statistics
        self.expected_duration_label = ttk.Label(stats_frame, text="Expected Duration: --", 
                                               font=("Arial", 10, "bold"))
        self.expected_duration_label.pack(anchor="w", pady=2)
        
        self.variance_label = ttk.Label(stats_frame, text="Project Variance: --")
        self.variance_label.pack(anchor="w", pady=2)
        
        self.std_deviation_label = ttk.Label(stats_frame, text="Standard Deviation: --")
        self.std_deviation_label.pack(anchor="w", pady=2)
        
        self.confidence_interval_label = ttk.Label(stats_frame, text="95% Confidence Interval: --")
        self.confidence_interval_label.pack(anchor="w", pady=2)
        
        # Critical path statistics
        ttk.Separator(stats_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.critical_path_label = ttk.Label(stats_frame, text="Critical Path Length: --")
        self.critical_path_label.pack(anchor="w", pady=2)
        
        self.critical_variance_label = ttk.Label(stats_frame, text="Critical Path Variance: --")
        self.critical_variance_label.pack(anchor="w", pady=2)
    
    def create_calculator_frame(self, parent):
        """Create probability calculator frame"""
        calc_frame = ttk.LabelFrame(parent, text="Completion Probability Calculator", padding="10")
        calc_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Target duration input
        target_frame = ttk.Frame(calc_frame)
        target_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(target_frame, text="Target Duration:").pack(side=tk.LEFT)
        self.target_duration_var = tk.StringVar()
        target_entry = ttk.Entry(target_frame, textvariable=self.target_duration_var, width=10)
        target_entry.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(target_frame, text="days").pack(side=tk.LEFT)
        
        # Calculate button
        ttk.Button(calc_frame, text="Calculate Probability", 
                  command=self.calculate_completion_probability).pack(pady=5)
        
        # Results display
        self.probability_result_label = ttk.Label(calc_frame, text="Completion Probability: --", 
                                                font=("Arial", 10, "bold"))
        self.probability_result_label.pack(anchor="w", pady=5)
        
        # Common probability scenarios
        scenarios_frame = ttk.LabelFrame(calc_frame, text="Common Scenarios", padding="5")
        scenarios_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Quick calculation buttons
        button_frame1 = ttk.Frame(scenarios_frame)
        button_frame1.pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame1, text="P(≤ Expected)", width=12,
                  command=lambda: self.quick_probability("expected")).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame1, text="P(≤ Expected+1σ)", width=12,
                  command=lambda: self.quick_probability("plus_1sigma")).pack(side=tk.LEFT, padx=2)
        
        button_frame2 = ttk.Frame(scenarios_frame)
        button_frame2.pack(fill=tk.X, pady=2)
        
        ttk.Button(button_frame2, text="P(≤ Expected-1σ)", width=12,
                  command=lambda: self.quick_probability("minus_1sigma")).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame2, text="P(≤ Expected+2σ)", width=12,
                  command=lambda: self.quick_probability("plus_2sigma")).pack(side=tk.LEFT, padx=2)
    
    def create_risk_frame(self, parent):
        """Create risk analysis frame"""
        risk_frame = ttk.LabelFrame(parent, text="Risk Analysis", padding="10")
        risk_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Risk level indicators
        self.risk_level_label = ttk.Label(risk_frame, text="Overall Risk Level: --", 
                                        font=("Arial", 10, "bold"))
        self.risk_level_label.pack(anchor="w", pady=2)
        
        self.schedule_risk_label = ttk.Label(risk_frame, text="Schedule Risk: --")
        self.schedule_risk_label.pack(anchor="w", pady=2)
        
        # Risk factors
        ttk.Separator(risk_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        ttk.Label(risk_frame, text="High Risk Activities:", font=("Arial", 9, "bold")).pack(anchor="w")
        
        # Scrollable text for risk activities
        self.risk_text = tk.Text(risk_frame, height=4, wrap=tk.WORD)
        risk_scrollbar = ttk.Scrollbar(risk_frame, orient=tk.VERTICAL, command=self.risk_text.yview)
        self.risk_text.configure(yscrollcommand=risk_scrollbar.set)
        
        self.risk_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        risk_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Export buttons
        export_frame = ttk.Frame(parent)
        export_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(export_frame, text="Export Analysis", 
                  command=self.export_probability_analysis).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Generate Report", 
                  command=self.generate_risk_report).pack(side=tk.LEFT)
    
    def create_plot_area(self):
        """Create matplotlib plot area"""
        plot_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(plot_frame, weight=2)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.figure.patch.set_facecolor('white')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.pack(fill=tk.X)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Chart type selection
        chart_frame = ttk.Frame(plot_frame)
        chart_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(chart_frame, text="Chart Type:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.chart_type_var = tk.StringVar(value="distribution")
        chart_combo = ttk.Combobox(chart_frame, textvariable=self.chart_type_var, width=20,
                                  values=["distribution", "cumulative", "sensitivity", "monte_carlo"])
        chart_combo.pack(side=tk.LEFT, padx=(0, 10))
        chart_combo.bind('<<ComboboxSelected>>', lambda e: self.update_visualization())
        
        ttk.Button(chart_frame, text="Update Chart", 
                  command=self.update_visualization).pack(side=tk.LEFT, padx=10)
        
        # Initialize with empty plot
        self.create_empty_plot()
    
    def create_empty_plot(self):
        """Create empty plot with instruction message"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Run PERT analysis to display probability charts', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
    
    def update_analysis(self, results_data):
        """Update probability analysis with PERT results data
        
        This method provides the interface expected by MainWindow for PERT analysis.
        It accepts the same results_data format as other tabs.
        """
        try:
            print("DEBUG: ProbabilityTab.update_analysis() called")
            
            if not results_data:
                print("DEBUG: No results data provided to ProbabilityTab")
                self.update_probability(None, 'probabilistic')
                return
            
            print(f"DEBUG: ProbabilityTab updating with PERT results")
            print(f"       Activities: {len(results_data.get('activities', []))}")
            print(f"       Project Duration: {results_data.get('project_duration', 'N/A')}")
            print(f"       Project Variance: {results_data.get('project_variance', 'N/A')}")
            
            # Delegate to the existing update_probability method
            self.update_probability(results_data, 'probabilistic')
            
            print("DEBUG: ProbabilityTab update completed successfully")
            
        except Exception as e:
            print(f"ERROR: ProbabilityTab.update_analysis() failed: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to clearing the display
            self.update_probability(None, 'probabilistic')
    
    def update_probability(self, results_data, analysis_mode):
        """Update the probability analysis with new data"""
        self.results_data = results_data
        self.analysis_mode = analysis_mode
        
        if not MATPLOTLIB_AVAILABLE or not SCIPY_AVAILABLE:
            return
        
        if not results_data or analysis_mode != 'probabilistic':
            self.create_empty_plot()
            self.clear_statistics()
            return
        
        # Update statistics
        self.update_statistics()
        
        # Update visualization
        self.update_visualization()
        
        # Update risk analysis
        self.update_risk_analysis()
    
    def update_statistics(self):
        """Update project statistics display"""
        if not self.results_data:
            return
        
        expected_duration = self.results_data.get('expected_duration', 0)
        variance = self.results_data.get('project_variance', 0)
        std_deviation = self.results_data.get('standard_deviation', 0)
        
        # Update labels
        self.expected_duration_label.config(text=f"Expected Duration: {expected_duration:.2f} days")
        self.variance_label.config(text=f"Project Variance: {variance:.3f}")
        self.std_deviation_label.config(text=f"Standard Deviation: {std_deviation:.2f} days")
        
        # Calculate 95% confidence interval
        if std_deviation > 0:
            ci_lower = expected_duration - 1.96 * std_deviation
            ci_upper = expected_duration + 1.96 * std_deviation
            self.confidence_interval_label.config(
                text=f"95% Confidence Interval: [{ci_lower:.1f}, {ci_upper:.1f}] days"
            )
        
        # Critical path statistics
        critical_path = self.results_data.get('critical_path', [])
        activities = self.results_data.get('activities', [])
        critical_activities = [a for a in activities if a.get('critical', False)]
        
        critical_variance = sum(a.get('variance', 0) for a in critical_activities)
        
        self.critical_path_label.config(text=f"Critical Path Length: {len(critical_path)} activities")
        self.critical_variance_label.config(text=f"Critical Path Variance: {critical_variance:.3f}")
    
    def calculate_completion_probability(self):
        """Calculate completion probability for target duration"""
        if not self.results_data:
            messagebox.showwarning("Warning", "No analysis data available.")
            return
        
        try:
            target_duration = float(self.target_duration_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid target duration.")
            return
        
        expected_duration = self.results_data.get('expected_duration', 0)
        std_deviation = self.results_data.get('standard_deviation', 0)
        
        if std_deviation <= 0:
            messagebox.showerror("Error", "Invalid standard deviation.")
            return
        
        # Calculate probability using normal distribution
        probability = ProbabilityCalculations.calculate_completion_probability(
            target_duration, expected_duration, std_deviation
        )
        
        self.probability_result_label.config(
            text=f"Completion Probability: {probability:.1%}"
        )
        
        # Update target line on distribution chart if visible
        if self.chart_type_var.get() == "distribution":
            self.update_visualization(target_duration)
    
    def quick_probability(self, scenario):
        """Calculate probability for common scenarios"""
        if not self.results_data:
            return
        
        expected_duration = self.results_data.get('expected_duration', 0)
        std_deviation = self.results_data.get('standard_deviation', 0)
        
        if scenario == "expected":
            target = expected_duration
        elif scenario == "plus_1sigma":
            target = expected_duration + std_deviation
        elif scenario == "minus_1sigma":
            target = expected_duration - std_deviation
        elif scenario == "plus_2sigma":
            target = expected_duration + 2 * std_deviation
        else:
            return
        
        self.target_duration_var.set(f"{target:.1f}")
        self.calculate_completion_probability()
    
    def update_visualization(self, target_duration=None):
        """Update the probability visualization"""
        if not self.results_data:
            return
        
        chart_type = self.chart_type_var.get()
        
        # Clear the figure
        self.figure.clear()
        
        try:
            if chart_type == "distribution":
                self.create_distribution_chart(target_duration)
            elif chart_type == "cumulative":
                self.create_cumulative_chart()
            elif chart_type == "sensitivity":
                self.create_sensitivity_chart()
            elif chart_type == "monte_carlo":
                self.create_monte_carlo_chart()
            
            # Adjust layout and draw
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            # Show error
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error creating chart:\n{str(e)}', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='red')
            ax.axis('off')
            self.canvas.draw()
    
    def create_distribution_chart(self, target_duration=None):
        """Create probability distribution chart"""
        ax = self.figure.add_subplot(111)
        
        expected_duration = self.results_data.get('expected_duration', 0)
        std_deviation = self.results_data.get('standard_deviation', 0)
        
        # Create x values for the distribution
        x_min = expected_duration - 4 * std_deviation
        x_max = expected_duration + 4 * std_deviation
        x = np.linspace(x_min, x_max, 1000)
        
        # Calculate normal distribution
        y = stats.norm.pdf(x, expected_duration, std_deviation)
        
        # Plot distribution
        ax.plot(x, y, 'b-', linewidth=2, label='Project Duration Distribution')
        ax.fill_between(x, y, alpha=0.3, color='lightblue')
        
        # Add expected value line
        ax.axvline(expected_duration, color='red', linestyle='--', linewidth=2,
                  label=f'Expected Duration: {expected_duration:.1f}')
        
        # Add target duration line if specified
        if target_duration is not None:
            ax.axvline(target_duration, color='green', linestyle='-', linewidth=2,
                      label=f'Target Duration: {target_duration:.1f}')
            
            # Shade area to the left of target (completion probability)
            x_target = x[x <= target_duration]
            y_target = stats.norm.pdf(x_target, expected_duration, std_deviation)
            ax.fill_between(x_target, y_target, alpha=0.5, color='green',
                           label='Completion Probability')
        
        ax.set_xlabel('Project Duration (days)')
        ax.set_ylabel('Probability Density')
        ax.set_title('Project Duration Probability Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def create_cumulative_chart(self):
        """Create cumulative distribution chart"""
        ax = self.figure.add_subplot(111)
        
        expected_duration = self.results_data.get('expected_duration', 0)
        std_deviation = self.results_data.get('standard_deviation', 0)
        
        # Create x values
        x_min = expected_duration - 3 * std_deviation
        x_max = expected_duration + 3 * std_deviation
        x = np.linspace(x_min, x_max, 1000)
        
        # Calculate cumulative distribution
        y = stats.norm.cdf(x, expected_duration, std_deviation)
        
        # Plot cumulative distribution
        ax.plot(x, y, 'b-', linewidth=2, label='Cumulative Probability')
        
        # Add reference lines
        ax.axhline(0.5, color='red', linestyle='--', alpha=0.7, label='50% Probability')
        ax.axhline(0.9, color='orange', linestyle='--', alpha=0.7, label='90% Probability')
        ax.axvline(expected_duration, color='red', linestyle='--', alpha=0.7,
                  label=f'Expected Duration: {expected_duration:.1f}')
        
        ax.set_xlabel('Project Duration (days)')
        ax.set_ylabel('Cumulative Probability')
        ax.set_title('Cumulative Probability Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)
    
    def create_sensitivity_chart(self):
        """Create sensitivity analysis chart"""
        ax = self.figure.add_subplot(111)
        
        activities = self.results_data.get('activities', [])
        critical_activities = [a for a in activities if a.get('critical', False)]
        
        # Calculate variance contribution for each critical activity
        activity_names = []
        variances = []
        
        for activity in critical_activities[:10]:  # Top 10 activities
            activity_names.append(activity.get('id', ''))
            variances.append(activity.get('variance', 0))
        
        # Create horizontal bar chart
        y_pos = np.arange(len(activity_names))
        bars = ax.barh(y_pos, variances, color='skyblue', edgecolor='navy')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(activity_names)
        ax.set_xlabel('Variance Contribution')
        ax.set_title('Activity Variance Sensitivity Analysis\n(Critical Path Activities)')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{width:.3f}', ha='left', va='center')
        
        ax.grid(True, alpha=0.3, axis='x')
    
    def create_monte_carlo_chart(self):
        """Create Monte Carlo simulation chart"""
        ax = self.figure.add_subplot(111)
        
        # Simple Monte Carlo simulation
        activities = self.results_data.get('activities', [])
        critical_activities = [a for a in activities if a.get('critical', False)]
        
        # Run Monte Carlo simulation
        n_simulations = 1000
        simulation_results = []
        
        for _ in range(n_simulations):
            total_duration = 0
            for activity in critical_activities:
                # Sample from beta distribution (PERT distribution)
                optimistic = activity.get('optimistic', 0)
                most_likely = activity.get('most_likely', 0)
                pessimistic = activity.get('pessimistic', 0)
                
                if optimistic and most_likely and pessimistic:
                    # PERT beta distribution approximation
                    alpha = 1 + 4 * (most_likely - optimistic) / (pessimistic - optimistic)
                    beta = 1 + 4 * (pessimistic - most_likely) / (pessimistic - optimistic)
                    
                    # Sample from beta distribution and scale
                    sample = np.random.beta(alpha, beta)
                    duration = optimistic + sample * (pessimistic - optimistic)
                    total_duration += duration
                else:
                    total_duration += activity.get('expected_duration', 0)
            
            simulation_results.append(total_duration)
        
        # Plot histogram
        ax.hist(simulation_results, bins=50, density=True, alpha=0.7, 
               color='lightblue', edgecolor='navy', label='Monte Carlo Simulation')
        
        # Add expected duration line
        expected_duration = self.results_data.get('expected_duration', 0)
        ax.axvline(expected_duration, color='red', linestyle='--', linewidth=2,
                  label=f'Analytical Expected: {expected_duration:.1f}')
        
        # Add simulation mean
        sim_mean = np.mean(simulation_results)
        ax.axvline(sim_mean, color='green', linestyle='-', linewidth=2,
                  label=f'Simulation Mean: {sim_mean:.1f}')
        
        ax.set_xlabel('Project Duration (days)')
        ax.set_ylabel('Probability Density')
        ax.set_title(f'Monte Carlo Simulation Results\n({n_simulations} simulations)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def update_risk_analysis(self):
        """Update risk analysis display"""
        if not self.results_data:
            return
        
        activities = self.results_data.get('activities', [])
        std_deviation = self.results_data.get('standard_deviation', 0)
        
        # Calculate overall risk level
        if std_deviation <= 2:
            risk_level = "Low"
            risk_color = "green"
        elif std_deviation <= 5:
            risk_level = "Medium"
            risk_color = "orange"
        else:
            risk_level = "High"
            risk_color = "red"
        
        self.risk_level_label.config(text=f"Overall Risk Level: {risk_level}")
        
        # Schedule risk assessment
        expected_duration = self.results_data.get('expected_duration', 0)
        if expected_duration > 0:
            cv = std_deviation / expected_duration  # Coefficient of variation
            if cv <= 0.1:
                schedule_risk = "Low variability"
            elif cv <= 0.2:
                schedule_risk = "Moderate variability"
            else:
                schedule_risk = "High variability"
        else:
            schedule_risk = "Unknown"
        
        self.schedule_risk_label.config(text=f"Schedule Risk: {schedule_risk}")
        
        # High risk activities
        self.risk_text.delete(1.0, tk.END)
        
        # Sort activities by variance (descending)
        high_risk_activities = sorted(activities, 
                                    key=lambda x: x.get('variance', 0), 
                                    reverse=True)[:5]
        
        risk_text = "Top 5 High-Risk Activities:\n\n"
        for i, activity in enumerate(high_risk_activities):
            variance = activity.get('variance', 0)
            risk_text += f"{i+1}. {activity.get('id', '')} - {activity.get('name', '')}\n"
            risk_text += f"   Variance: {variance:.3f}\n"
            if activity.get('critical', False):
                risk_text += "   ⚠️ Critical Path Activity\n"
            risk_text += "\n"
        
        self.risk_text.insert(1.0, risk_text)
    
    def clear_statistics(self):
        """Clear all statistics displays"""
        self.expected_duration_label.config(text="Expected Duration: --")
        self.variance_label.config(text="Project Variance: --")
        self.std_deviation_label.config(text="Standard Deviation: --")
        self.confidence_interval_label.config(text="95% Confidence Interval: --")
        self.critical_path_label.config(text="Critical Path Length: --")
        self.critical_variance_label.config(text="Critical Path Variance: --")
        self.probability_result_label.config(text="Completion Probability: --")
        self.risk_level_label.config(text="Overall Risk Level: --")
        self.schedule_risk_label.config(text="Schedule Risk: --")
        self.risk_text.delete(1.0, tk.END)
    
    def export_probability_analysis(self):
        """Export probability analysis results"""
        if not self.results_data:
            messagebox.showwarning("Warning", "No analysis data to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Probability Analysis",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self._export_analysis_data(filename)
                messagebox.showinfo("Success", f"Analysis exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export analysis: {str(e)}")
    
    def _export_analysis_data(self, filename):
        """Export analysis data to file"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            if filename.lower().endswith('.csv'):
                writer = csv.writer(file)
                
                # Project statistics
                writer.writerow(["Probability Analysis Results"])
                writer.writerow(["Expected Duration", self.results_data.get('expected_duration', '')])
                writer.writerow(["Project Variance", self.results_data.get('project_variance', '')])
                writer.writerow(["Standard Deviation", self.results_data.get('standard_deviation', '')])
                writer.writerow([])
                
                # Activity analysis
                writer.writerow(["Activity", "Expected Duration", "Variance", "Standard Deviation", "Critical"])
                activities = self.results_data.get('activities', [])
                for activity in activities:
                    writer.writerow([
                        activity.get('id', ''),
                        f"{activity.get('expected_duration', 0):.2f}",
                        f"{activity.get('variance', 0):.3f}",
                        f"{np.sqrt(activity.get('variance', 0)):.2f}",
                        "Yes" if activity.get('critical', False) else "No"
                    ])
            else:
                # Text format
                file.write("Probability Analysis Results\n")
                file.write("=" * 50 + "\n\n")
                
                file.write(f"Expected Duration: {self.results_data.get('expected_duration', '')}\n")
                file.write(f"Project Variance: {self.results_data.get('project_variance', '')}\n")
                file.write(f"Standard Deviation: {self.results_data.get('standard_deviation', '')}\n\n")
                
                file.write("Activity Analysis:\n")
                file.write("-" * 30 + "\n")
                
                activities = self.results_data.get('activities', [])
                for activity in activities:
                    file.write(f"\nActivity: {activity.get('id', '')}\n")
                    file.write(f"  Expected Duration: {activity.get('expected_duration', 0):.2f}\n")
                    file.write(f"  Variance: {activity.get('variance', 0):.3f}\n")
                    file.write(f"  Critical: {'Yes' if activity.get('critical', False) else 'No'}\n")
    
    def generate_risk_report(self):
        """Generate comprehensive risk report"""
        if not self.results_data:
            messagebox.showwarning("Warning", "No analysis data available.")
            return
        
        # Create new window for report
        report_window = tk.Toplevel(self.probability_frame)
        report_window.title("Risk Analysis Report")
        report_window.geometry("600x700")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(report_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        report_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)
        
        report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate report content
        report_content = self._generate_report_content()
        report_text.insert(1.0, report_content)
        
        # Add save button
        button_frame = ttk.Frame(report_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Save Report", 
                  command=lambda: self._save_report(report_content)).pack(side=tk.RIGHT)
    
    def _generate_report_content(self):
        """Generate risk report content"""
        report = "PROJECT RISK ANALYSIS REPORT\n"
        report += "=" * 50 + "\n\n"
        
        # Project overview
        expected_duration = self.results_data.get('expected_duration', 0)
        std_deviation = self.results_data.get('standard_deviation', 0)
        
        report += f"Project Expected Duration: {expected_duration:.2f} days\n"
        report += f"Standard Deviation: {std_deviation:.2f} days\n"
        report += f"Coefficient of Variation: {(std_deviation/expected_duration)*100:.1f}%\n\n"
        
        # Risk assessment
        if std_deviation <= 2:
            risk_assessment = "LOW RISK - Project has low uncertainty"
        elif std_deviation <= 5:
            risk_assessment = "MEDIUM RISK - Project has moderate uncertainty"
        else:
            risk_assessment = "HIGH RISK - Project has high uncertainty"
        
        report += f"Overall Risk Assessment: {risk_assessment}\n\n"
        
        # Probability scenarios
        report += "COMPLETION PROBABILITY SCENARIOS:\n"
        report += "-" * 40 + "\n"
        
        scenarios = [
            ("On time (Expected Duration)", expected_duration),
            ("Conservative (Expected + 1σ)", expected_duration + std_deviation),
            ("Optimistic (Expected - 1σ)", expected_duration - std_deviation),
            ("Very Conservative (Expected + 2σ)", expected_duration + 2 * std_deviation)
        ]
        
        for desc, target in scenarios:
            prob = ProbabilityCalculations.calculate_completion_probability(
                target, expected_duration, std_deviation
            )
            report += f"{desc}: {prob:.1%} chance of completion by day {target:.1f}\n"
        
        report += "\n"
        
        # High-risk activities
        activities = self.results_data.get('activities', [])
        high_risk = sorted(activities, key=lambda x: x.get('variance', 0), reverse=True)[:5]
        
        report += "HIGH-RISK ACTIVITIES:\n"
        report += "-" * 30 + "\n"
        
        for i, activity in enumerate(high_risk):
            report += f"{i+1}. {activity.get('id', '')} - {activity.get('name', '')}\n"
            report += f"   Expected Duration: {activity.get('expected_duration', 0):.2f} days\n"
            report += f"   Variance: {activity.get('variance', 0):.3f}\n"
            if activity.get('critical', False):
                report += "   Status: CRITICAL PATH ACTIVITY\n"
            report += "\n"
        
        # Recommendations
        report += "RISK MITIGATION RECOMMENDATIONS:\n"
        report += "-" * 40 + "\n"
        
        if std_deviation > 5:
            report += "• Consider breaking down high-variance activities into smaller tasks\n"
            report += "• Implement closer monitoring of critical path activities\n"
            report += "• Develop contingency plans for high-risk activities\n"
        elif std_deviation > 2:
            report += "• Monitor critical path activities closely\n"
            report += "• Consider buffer time for high-variance activities\n"
        else:
            report += "• Project appears well-planned with low risk\n"
            report += "• Continue with current project management approach\n"
        
        return report
    
    def _save_report(self, content):
        """Save risk report to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Risk Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("Success", f"Report saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")
    
    def show(self):
        """Show the probability tab"""
        # Add the tab to the notebook if it's not already there
        if self.probability_frame not in [self.notebook.nametowidget(tab) for tab in self.notebook.tabs()]:
            self.notebook.add(self.probability_frame, text="Probability Analysis")
    
    def hide(self):
        """Hide the probability tab"""
        # Remove the tab from the notebook if it exists
        try:
            self.notebook.forget(self.probability_frame)
        except tk.TclError:
            # Tab might not be in the notebook
            pass
