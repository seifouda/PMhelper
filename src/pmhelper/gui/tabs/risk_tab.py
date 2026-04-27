#!/usr/bin/env python3
"""
Risk Analysis Tab Module

Comprehensive risk analysis interface for PERT projects including:
- Delay Risk Analysis
- Contingency Planning
- Variance Reduction Strategies
- Activity Risk Prioritization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
from pathlib import Path

from pmhelper.gui.widgets.sortable_treeview import enhance_treeview

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Check dependencies


def check_dependencies():
    """Check if required libraries are available"""
    try:
        return True
    except ImportError:
        return False


DEPENDENCIES_AVAILABLE = check_dependencies()


class RiskAnalysisTab:
    """Risk Analysis tab for comprehensive project risk assessment"""

    def __init__(self, notebook, main_window):
        self.notebook = notebook
        self.main_window = main_window
        self.pert_analyzer = None
        self.risk_results = {}

        # Data storage
        self.delay_risk_data = None
        self.contingency_data = None
        self.strategies_data = None
        self.activity_risks_data = None

        self.create_tab()

    def create_tab(self):
        """Create the risk analysis tab"""
        self.risk_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.risk_frame, text="Risk Analysis")

        if not DEPENDENCIES_AVAILABLE:
            self.create_dependencies_message()
            return

        # Create header with help button
        header_frame = ttk.Frame(self.risk_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        title_label = ttk.Label(
            header_frame,
            text="Comprehensive Risk Analysis",
            font=(
                "Arial",
                12,
                "bold"))
        title_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(header_frame, text="? Help",
                   command=self.show_help).pack(side=tk.RIGHT)

        # Create notebook for different risk analysis sections
        self.risk_notebook = ttk.Notebook(self.risk_frame)
        self.risk_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create four tabs
        self.create_delay_risk_tab()
        self.create_contingency_tab()
        self.create_strategies_tab()
        self.create_activity_risks_tab()

    def create_dependencies_message(self):
        """Show message when dependencies are missing"""
        message_frame = ttk.Frame(self.risk_frame)
        message_frame.pack(fill=tk.BOTH, expand=True)

        message_text = "Risk Analysis requires numpy, pandas, and matplotlib.\n\n"
        message_text += "Please install required packages to use this feature."

        message_label = ttk.Label(message_frame, text=message_text,
                                  font=("Arial", 12), justify=tk.CENTER)
        message_label.pack(expand=True)

    # ========================================================================
    # TAB 1: DELAY RISK ANALYSIS
    # ========================================================================

    def create_delay_risk_tab(self):
        """Create delay risk analysis tab"""
        delay_frame = ttk.Frame(self.risk_notebook)
        self.risk_notebook.add(delay_frame, text="Delay Risk")

        # Create paned window for input and results
        paned = ttk.PanedWindow(delay_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Input panel
        input_frame = ttk.Frame(paned, width=300)
        paned.add(input_frame, weight=1)

        self.create_delay_input_panel(input_frame)

        # Right: Results panel
        results_frame = ttk.Frame(paned)
        paned.add(results_frame, weight=2)

        self.create_delay_results_panel(results_frame)

    def create_delay_input_panel(self, parent):
        """Create input panel for delay risk analysis"""
        # Input fields frame
        inputs_frame = ttk.LabelFrame(parent, text="Parameters", padding="10")
        inputs_frame.pack(fill=tk.X, padx=5, pady=5)

        # Contract time
        ttk.Label(inputs_frame, text="Contract Time (weeks):").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.contract_time_var = tk.StringVar(value="15.0")
        ttk.Entry(inputs_frame, textvariable=self.contract_time_var,
                  width=15).grid(row=0, column=1, pady=5, padx=5)

        # Penalty rate
        ttk.Label(inputs_frame, text="Penalty Rate ($/week):").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.penalty_rate_var = tk.StringVar(value="1000")
        ttk.Entry(inputs_frame, textvariable=self.penalty_rate_var,
                  width=15).grid(row=1, column=1, pady=5, padx=5)

        # Max penalty percent
        ttk.Label(inputs_frame, text="Max Penalty (%):").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.max_penalty_var = tk.StringVar(value="20")
        ttk.Entry(inputs_frame, textvariable=self.max_penalty_var,
                  width=15).grid(row=2, column=1, pady=5, padx=5)

        # Calculate button
        ttk.Button(inputs_frame, text="Calculate Delay Risk",
                   command=self.calculate_delay_risk).grid(
            row=3, column=0, columnspan=2, pady=15)

        # Info frame
        info_frame = ttk.LabelFrame(parent, text="Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        info_text = """Delay Risk Analysis calculates:

• Probability of project delay
• Expected delay period
• Risk cost and financial impact

Uses normal distribution and
truncated normal formulas from
IM 738 course material."""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

    def create_delay_results_panel(self, parent):
        """Create results panel for delay risk analysis"""
        # Results display
        results_frame = ttk.LabelFrame(
            parent, text="Risk Assessment", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create text widget for results
        self.delay_results_text = tk.Text(results_frame, height=15, width=50,
                                          font=("Courier", 10))
        self.delay_results_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            results_frame,
            command=self.delay_results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.delay_results_text.config(yscrollcommand=scrollbar.set)

        # Configure tags for colored output
        self.delay_results_text.tag_config(
            "header", font=("Courier", 10, "bold"))
        self.delay_results_text.tag_config("low_risk", foreground="green")
        self.delay_results_text.tag_config("medium_risk", foreground="orange")
        self.delay_results_text.tag_config("high_risk", foreground="red")

    def calculate_delay_risk(self):
        """Calculate and display delay risk"""
        try:
            # Get PERT analyzer
            if not hasattr(
                    self.main_window,
                    'pert_analyzer') or self.main_window.pert_analyzer is None:
                messagebox.showerror(
                    "Error", "Please run PERT analysis first!")
                return

            # Check if analysis has been run
            if not hasattr(
                    self.main_window.pert_analyzer,
                    'G') or self.main_window.pert_analyzer.G is None:
                messagebox.showerror(
                    "Error", "No analysis results available. Please run PERT analysis first!")
                return

            # Get parameters
            contract_time = float(self.contract_time_var.get())
            penalty_rate = float(self.penalty_rate_var.get())
            max_penalty_percent = float(self.max_penalty_var.get()) / 100.0

            # Calculate delay risk
            risk = self.main_window.pert_analyzer.analyze_delay_risk(
                contract_time=contract_time,
                penalty_rate=penalty_rate,
                max_penalty_percent=max_penalty_percent
            )

            self.delay_risk_data = risk

            # Display results
            self.display_delay_risk_results(risk, contract_time, penalty_rate)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def display_delay_risk_results(self, risk, contract_time, penalty_rate):
        """Display delay risk results"""
        self.delay_results_text.delete(1.0, tk.END)

        # Header
        self.delay_results_text.insert(tk.END, "=" * 50 + "\n", "header")
        self.delay_results_text.insert(
            tk.END, "DELAY RISK ANALYSIS RESULTS\n", "header")
        self.delay_results_text.insert(tk.END, "=" * 50 + "\n\n", "header")

        # Parameters
        self.delay_results_text.insert(
            tk.END, f"Contract Time: {
                contract_time:.2f} weeks\n")
        self.delay_results_text.insert(
            tk.END, f"Penalty Rate: ${
                penalty_rate:,.2f}/week\n\n")

        # Results
        delay_prob = risk['delay_probability']
        self.delay_results_text.insert(
            tk.END, f"Delay Probability: {
                delay_prob:.1%}\n")

        # Risk level indicator
        if delay_prob < 0.1:
            risk_level = "✓ LOW RISK"
            tag = "low_risk"
        elif delay_prob < 0.3:
            risk_level = "⚠ MODERATE RISK"
            tag = "medium_risk"
        else:
            risk_level = "🔴 HIGH RISK"
            tag = "high_risk"

        self.delay_results_text.insert(
            tk.END, f"Risk Level: {risk_level}\n\n", tag)

        self.delay_results_text.insert(
            tk.END, f"Expected Delay: {
                risk['expected_delay']:.2f} weeks\n")
        self.delay_results_text.insert(
            tk.END, f"Risk Cost: ${
                risk['risk_cost']:,.2f}\n")

        if risk['max_penalty'] is not None:
            self.delay_results_text.insert(
                tk.END, f"Capped Risk Cost: ${
                    risk['capped_risk_cost']:,.2f}\n")
            self.delay_results_text.insert(
                tk.END, f"Max Penalty: ${
                    risk['max_penalty']:,.2f}\n")

        self.delay_results_text.insert(tk.END,
                                       f"\nZ-Score: {risk['z_score']:.2f}\n")

        # Recommendation
        self.delay_results_text.insert(
            tk.END, "\n" + "-" * 50 + "\n", "header")
        self.delay_results_text.insert(tk.END, "RECOMMENDATION\n", "header")
        self.delay_results_text.insert(tk.END, "-" * 50 + "\n\n", "header")

        if delay_prob > 0.3:
            rec = "High delay risk detected. Consider:\n"
            rec += "• Adding contingency buffer\n"
            rec += "• Variance reduction strategies\n"
            rec += "• Activity risk mitigation\n"
        elif delay_prob > 0.1:
            rec = "Moderate risk. Monitor closely and\n"
            rec += "prepare contingency plans.\n"
        else:
            rec = "Low risk. Project likely to complete\n"
            rec += "on time with current estimates.\n"

        self.delay_results_text.insert(tk.END, rec)

    # ========================================================================
    # TAB 2: CONTINGENCY PLANNING
    # ========================================================================

    def create_contingency_tab(self):
        """Create contingency planning tab"""
        contingency_frame = ttk.Frame(self.risk_notebook)
        self.risk_notebook.add(contingency_frame, text="Contingency")

        # Create paned window
        paned = ttk.PanedWindow(contingency_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Input panel
        input_frame = ttk.Frame(paned, width=300)
        paned.add(input_frame, weight=1)

        self.create_contingency_input_panel(input_frame)

        # Right: Results panel
        results_frame = ttk.Frame(paned)
        paned.add(results_frame, weight=2)

        self.create_contingency_results_panel(results_frame)

    def create_contingency_input_panel(self, parent):
        """Create input panel for contingency planning"""
        inputs_frame = ttk.LabelFrame(parent, text="Parameters", padding="10")
        inputs_frame.pack(fill=tk.X, padx=5, pady=5)

        # Confidence level slider
        ttk.Label(inputs_frame, text="Confidence Level:").grid(
            row=0, column=0, sticky=tk.W, pady=5)

        self.confidence_var = tk.DoubleVar(value=0.95)
        confidence_scale = ttk.Scale(inputs_frame, from_=0.80, to=0.99,
                                     variable=self.confidence_var,
                                     orient=tk.HORIZONTAL, length=150,
                                     command=self.update_confidence_label)
        confidence_scale.grid(row=0, column=1, pady=5, padx=5)

        self.confidence_label = ttk.Label(inputs_frame, text="95%")
        self.confidence_label.grid(row=0, column=2, pady=5)

        # Daily cost rate
        ttk.Label(inputs_frame, text="Daily Cost Rate ($):").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.daily_cost_var = tk.StringVar(value="5000")
        ttk.Entry(inputs_frame, textvariable=self.daily_cost_var,
                  width=15).grid(row=1, column=1, pady=5, padx=5)

        # Calculate button
        ttk.Button(inputs_frame, text="Calculate Contingency",
                   command=self.calculate_contingency).grid(
            row=2, column=0, columnspan=3, pady=15)

        # Quick calculate buttons for common confidence levels
        quick_frame = ttk.LabelFrame(
            parent, text="Quick Calculate", padding="10")
        quick_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            quick_frame,
            text="80%",
            width=8,
            command=lambda: self.quick_contingency(0.80)).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            quick_frame,
            text="90%",
            width=8,
            command=lambda: self.quick_contingency(0.90)).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            quick_frame,
            text="95%",
            width=8,
            command=lambda: self.quick_contingency(0.95)).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            quick_frame,
            text="99%",
            width=8,
            command=lambda: self.quick_contingency(0.99)).pack(
            side=tk.LEFT,
            padx=2)

        # Info
        info_frame = ttk.LabelFrame(parent, text="Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        info_text = """Contingency Planning estimates:

• Time buffer needed for desired
  confidence level
• Project completion time
• Contingency budget

Higher confidence = larger buffer
Standard: 90-95% for most projects"""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

    def update_confidence_label(self, value=None):
        """Update confidence level label"""
        self.confidence_label.config(
            text=f"{self.confidence_var.get() * 100:.0f}%")

    def quick_contingency(self, confidence):
        """Quick calculate with specific confidence level"""
        self.confidence_var.set(confidence)
        self.update_confidence_label()
        self.calculate_contingency()

    def create_contingency_results_panel(self, parent):
        """Create results panel for contingency planning"""
        results_frame = ttk.LabelFrame(
            parent, text="Contingency Estimates", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create text widget
        self.contingency_results_text = tk.Text(
            results_frame, height=15, width=50, font=("Courier", 10))
        self.contingency_results_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(results_frame,
                                  command=self.contingency_results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.contingency_results_text.config(yscrollcommand=scrollbar.set)

        # Tags
        self.contingency_results_text.tag_config(
            "header", font=("Courier", 10, "bold"))
        self.contingency_results_text.tag_config(
            "highlight", background="yellow")

    def calculate_contingency(self):
        """Calculate contingency buffer"""
        try:
            if not hasattr(
                    self.main_window,
                    'pert_analyzer') or self.main_window.pert_analyzer is None:
                messagebox.showerror(
                    "Error", "Please run PERT analysis first!")
                return

            # Check if analysis has been run
            if not hasattr(
                    self.main_window.pert_analyzer,
                    'G') or self.main_window.pert_analyzer.G is None:
                messagebox.showerror(
                    "Error", "No analysis results available. Please run PERT analysis first!")
                return

            confidence = self.confidence_var.get()
            daily_cost = float(self.daily_cost_var.get()
                               ) if self.daily_cost_var.get() else None

            # Calculate contingency
            result = self.main_window.pert_analyzer.estimate_contingency(
                confidence_level=confidence,
                daily_cost_rate=daily_cost
            )

            self.contingency_data = result
            self.display_contingency_results(result)

        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def display_contingency_results(self, result):
        """Display contingency results"""
        self.contingency_results_text.delete(1.0, tk.END)

        # Header
        self.contingency_results_text.insert(tk.END, "=" * 50 + "\n", "header")
        self.contingency_results_text.insert(
            tk.END, "CONTINGENCY PLANNING RESULTS\n", "header")
        self.contingency_results_text.insert(
            tk.END, "=" * 50 + "\n\n", "header")

        # Results
        self.contingency_results_text.insert(
            tk.END, f"Confidence Level: {
                result['confidence_level'] * 100:.0f}%\n")
        self.contingency_results_text.insert(
            tk.END, f"Z-Score: {result['z_score']:.3f}\n\n")

        self.contingency_results_text.insert(
            tk.END, f"Time Buffer Required: {
                result['time_buffer']:.2f} weeks\n", "highlight")
        self.contingency_results_text.insert(
            tk.END, f"Buffer Percentage: {
                result['buffer_percentage']:.1f}%\n")
        self.contingency_results_text.insert(
            tk.END, f"\nCompletion Time: {
                result['completion_time']:.2f} weeks\n", "highlight")

        if result['contingency_cost'] is not None:
            self.contingency_results_text.insert(
                tk.END, f"Contingency Cost: ${
                    result['contingency_cost']:,.2f}\n")

        # Recommendation
        self.contingency_results_text.insert(
            tk.END, "\n" + "-" * 50 + "\n", "header")
        self.contingency_results_text.insert(
            tk.END, "RECOMMENDATION\n", "header")
        self.contingency_results_text.insert(
            tk.END, "-" * 50 + "\n\n", "header")
        self.contingency_results_text.insert(
            tk.END, result['recommendation'] + "\n")

    # ========================================================================
    # TAB 3: VARIANCE REDUCTION STRATEGIES
    # ========================================================================

    def create_strategies_tab(self):
        """Create variance reduction strategies tab"""
        strategies_frame = ttk.Frame(self.risk_notebook)
        self.risk_notebook.add(strategies_frame, text="Strategies")

        # Create paned window
        paned = ttk.PanedWindow(strategies_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Input panel
        input_frame = ttk.Frame(paned, width=300)
        paned.add(input_frame, weight=1)

        self.create_strategies_input_panel(input_frame)

        # Right: Results panel
        results_frame = ttk.Frame(paned)
        paned.add(results_frame, weight=2)

        self.create_strategies_results_panel(results_frame)

    def create_strategies_input_panel(self, parent):
        """Create input panel for strategies"""
        inputs_frame = ttk.LabelFrame(parent, text="Parameters", padding="10")
        inputs_frame.pack(fill=tk.X, padx=5, pady=5)

        row = 0
        # Contract time
        ttk.Label(
            inputs_frame,
            text="Contract Time:").grid(
            row=row,
            column=0,
            sticky=tk.W,
            pady=3)
        self.strat_contract_var = tk.StringVar(value="15.0")
        ttk.Entry(
            inputs_frame,
            textvariable=self.strat_contract_var,
            width=12).grid(
            row=row,
            column=1,
            pady=3)

        row += 1
        # Penalty rate
        ttk.Label(
            inputs_frame,
            text="Penalty Rate:").grid(
            row=row,
            column=0,
            sticky=tk.W,
            pady=3)
        self.strat_penalty_var = tk.StringVar(value="1000")
        ttk.Entry(
            inputs_frame,
            textvariable=self.strat_penalty_var,
            width=12).grid(
            row=row,
            column=1,
            pady=3)

        row += 1
        # Time reduction cost
        ttk.Label(
            inputs_frame,
            text="Time Reduction Cost:").grid(
            row=row,
            column=0,
            sticky=tk.W,
            pady=3)
        self.time_cost_var = tk.StringVar(value="3000")
        ttk.Entry(
            inputs_frame,
            textvariable=self.time_cost_var,
            width=12).grid(
            row=row,
            column=1,
            pady=3)

        row += 1
        # Variance reduction cost
        ttk.Label(
            inputs_frame,
            text="Variance Reduction Cost:").grid(
            row=row,
            column=0,
            sticky=tk.W,
            pady=3)
        self.var_cost_var = tk.StringVar(value="2000")
        ttk.Entry(inputs_frame, textvariable=self.var_cost_var, width=12).grid(
            row=row, column=1, pady=3)

        row += 1
        # Max budget
        ttk.Label(
            inputs_frame,
            text="Max Budget:").grid(
            row=row,
            column=0,
            sticky=tk.W,
            pady=3)
        self.budget_var = tk.StringVar(value="30000")
        ttk.Entry(inputs_frame, textvariable=self.budget_var, width=12).grid(
            row=row, column=1, pady=3)

        row += 1
        # Calculate button
        ttk.Button(inputs_frame, text="Analyze Strategies",
                   command=self.analyze_strategies).grid(
            row=row, column=0, columnspan=2, pady=15)

        # Info
        info_frame = ttk.LabelFrame(parent, text="Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        info_text = """Strategy Comparison:

A: Reduce expected time
   (keep variance constant)

B: Reduce variance
   (keep time constant)

Mixed: Optimal combination

Compares ROI and net benefit"""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

    def create_strategies_results_panel(self, parent):
        """Create results panel for strategies"""
        results_frame = ttk.LabelFrame(
            parent, text="Strategy Comparison", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.strategies_results_text = tk.Text(
            results_frame, height=15, width=50, font=("Courier", 9))
        self.strategies_results_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(results_frame,
                                  command=self.strategies_results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.strategies_results_text.config(yscrollcommand=scrollbar.set)

        self.strategies_results_text.tag_config(
            "header", font=("Courier", 9, "bold"))
        self.strategies_results_text.tag_config(
            "best", background="lightgreen")

    def analyze_strategies(self):
        """Analyze variance reduction strategies"""
        try:
            if not hasattr(
                    self.main_window,
                    'pert_analyzer') or self.main_window.pert_analyzer is None:
                messagebox.showerror(
                    "Error", "Please run PERT analysis first!")
                return

            # Check if analysis has been run
            if not hasattr(
                    self.main_window.pert_analyzer,
                    'G') or self.main_window.pert_analyzer.G is None:
                messagebox.showerror(
                    "Error", "No analysis results available. Please run PERT analysis first!")
                return

            # Get parameters
            contract_time = float(self.strat_contract_var.get())
            penalty_rate = float(self.strat_penalty_var.get())
            time_cost = float(self.time_cost_var.get())
            var_cost = float(self.var_cost_var.get())
            budget = float(self.budget_var.get())

            # Analyze strategies
            result = self.main_window.pert_analyzer.analyze_variance_reduction_strategies(
                contract_time=contract_time,
                penalty_rate=penalty_rate,
                time_reduction_cost=time_cost,
                variance_reduction_cost=var_cost,
                max_budget=budget
            )

            self.strategies_data = result
            self.display_strategies_results(result)

        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def display_strategies_results(self, result):
        """Display strategy comparison results"""
        self.strategies_results_text.delete(1.0, tk.END)

        # Header
        self.strategies_results_text.insert(tk.END, "=" * 60 + "\n", "header")
        self.strategies_results_text.insert(
            tk.END, "VARIANCE REDUCTION STRATEGY COMPARISON\n", "header")
        self.strategies_results_text.insert(
            tk.END, "=" * 60 + "\n\n", "header")

        # Baseline
        self.strategies_results_text.insert(
            tk.END, f"Baseline Risk Cost: ${
                result['baseline']['risk_cost']:,.2f}\n\n")

        # Strategy A
        self.strategies_results_text.insert(
            tk.END, "STRATEGY A (Reduce Time)\n", "header")
        self.strategies_results_text.insert(tk.END, "-" * 60 + "\n")
        sa = result['strategy_a']
        self.strategies_results_text.insert(
            tk.END, f"  Time Reduction: {
                sa['time_reduction']:.2f} weeks\n")
        self.strategies_results_text.insert(
            tk.END, f"  Investment: ${
                sa['investment']:,.2f}\n")
        self.strategies_results_text.insert(
            tk.END, f"  Benefit: ${sa['benefit']:,.2f}\n")
        self.strategies_results_text.insert(
            tk.END, f"  Net Benefit: ${
                sa['net_benefit']:,.2f}\n")
        self.strategies_results_text.insert(tk.END,
                                            f"  ROI: {sa['roi']:.1f}%\n\n")

        # Strategy B
        self.strategies_results_text.insert(
            tk.END, "STRATEGY B (Reduce Variance)\n", "header")
        self.strategies_results_text.insert(tk.END, "-" * 60 + "\n")
        sb = result['strategy_b']
        self.strategies_results_text.insert(
            tk.END, f"  Variance Reduction: {
                sb['variance_reduction']:.2f}\n")
        self.strategies_results_text.insert(
            tk.END, f"  Investment: ${
                sb['investment']:,.2f}\n")
        self.strategies_results_text.insert(
            tk.END, f"  Benefit: ${sb['benefit']:,.2f}\n")
        self.strategies_results_text.insert(
            tk.END, f"  Net Benefit: ${
                sb['net_benefit']:,.2f}\n")
        self.strategies_results_text.insert(tk.END,
                                            f"  ROI: {sb['roi']:.1f}%\n\n")

        # Mixed Strategy
        self.strategies_results_text.insert(
            tk.END, "MIXED STRATEGY\n", "header")
        self.strategies_results_text.insert(tk.END, "-" * 60 + "\n")
        sm = result['mixed_strategy']
        self.strategies_results_text.insert(
            tk.END, f"  Time Reduction: {
                sm['time_reduction']:.2f} weeks\n")
        self.strategies_results_text.insert(
            tk.END, f"  Variance Reduction: {
                sm['variance_reduction']:.2f}\n")
        self.strategies_results_text.insert(
            tk.END, f"  Investment: ${
                sm['investment']:,.2f}\n")
        self.strategies_results_text.insert(
            tk.END, f"  Benefit: ${sm['benefit']:,.2f}\n")
        self.strategies_results_text.insert(
            tk.END, f"  Net Benefit: ${
                sm['net_benefit']:,.2f}\n")
        self.strategies_results_text.insert(tk.END,
                                            f"  ROI: {sm['roi']:.1f}%\n\n")

        # Recommendation
        best = result['best_strategy']
        self.strategies_results_text.insert(tk.END, "=" * 60 + "\n", "header")
        self.strategies_results_text.insert(
            tk.END, "✓ RECOMMENDED STRATEGY\n", "header")
        self.strategies_results_text.insert(tk.END, "=" * 60 + "\n")
        self.strategies_results_text.insert(tk.END,
                                            f"{best['name']}\n", "best")
        self.strategies_results_text.insert(
            tk.END, f"Best Net Benefit: ${
                best['net_benefit']:,.2f}\n\n", "best")

    # ========================================================================
    # TAB 4: ACTIVITY RISK PRIORITIZATION
    # ========================================================================

    def create_activity_risks_tab(self):
        """Create activity risk prioritization tab"""
        activity_frame = ttk.Frame(self.risk_notebook)
        self.risk_notebook.add(activity_frame, text="Activity Risks")

        # Create controls at top
        control_frame = ttk.Frame(activity_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            control_frame,
            text="Calculate Risk Scores",
            command=self.calculate_activity_risks).pack(
            side=tk.LEFT,
            padx=5)

        ttk.Button(
            control_frame,
            text="Generate Mitigation Plan",
            command=self.generate_mitigation_plan).pack(
            side=tk.LEFT,
            padx=5)

        ttk.Button(
            control_frame,
            text="Export to CSV",
            command=self.export_activity_risks).pack(
            side=tk.LEFT,
            padx=5)

        # Create treeview for activity risks
        tree_frame = ttk.Frame(activity_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        columns = ('Activity', 'Risk Score', 'Expected Time', 'Variance',
                   'Float', 'Recommendation')
        self.activity_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)

        # Configure columns
        self.activity_tree.heading('Activity', text='Activity')
        self.activity_tree.heading('Risk Score', text='Risk Score')
        self.activity_tree.heading('Expected Time', text='Expected Time')
        self.activity_tree.heading('Variance', text='Variance')
        self.activity_tree.heading('Float', text='Float')
        self.activity_tree.heading('Recommendation', text='Recommendation')

        self.activity_tree.column('Activity', width=80)
        self.activity_tree.column('Risk Score', width=100)
        self.activity_tree.column('Expected Time', width=120)
        self.activity_tree.column('Variance', width=100)
        self.activity_tree.column('Float', width=80)
        self.activity_tree.column('Recommendation', width=300)

        self.activity_tree.pack(fill=tk.BOTH, expand=True)

        vsb.config(command=self.activity_tree.yview)
        hsb.config(command=self.activity_tree.xview)

        # Tags for color coding
        self.activity_tree.tag_configure('high_risk', background='#ffcccc')
        self.activity_tree.tag_configure('medium_risk', background='#ffffcc')
        self.activity_tree.tag_configure('low_risk', background='#ccffcc')
        enhance_treeview(self.activity_tree)

    def calculate_activity_risks(self):
        """Calculate and display activity risk scores"""
        try:
            if not hasattr(
                    self.main_window,
                    'pert_analyzer') or self.main_window.pert_analyzer is None:
                messagebox.showerror(
                    "Error", "Please run PERT analysis first!")
                return

            # Check if analysis has been run
            if not hasattr(
                    self.main_window.pert_analyzer,
                    'G') or self.main_window.pert_analyzer.G is None:
                messagebox.showerror(
                    "Error", "No analysis results available. Please run PERT analysis first!")
                return

            # Calculate risk scores
            df = self.main_window.pert_analyzer.prioritize_activity_risks()
            self.activity_risks_data = df

            # Clear tree
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)

            # Populate tree
            for idx, row in df.iterrows():
                risk_score = row['risk_score']

                # Determine tag
                if risk_score >= 0.6:
                    tag = 'high_risk'
                elif risk_score >= 0.3:
                    tag = 'medium_risk'
                else:
                    tag = 'low_risk'

                values = (
                    row['activity_id'],
                    f"{risk_score:.3f}",
                    f"{row['expected_time']:.2f}",
                    f"{row['variance']:.3f}",
                    f"{row['total_float']:.2f}",
                    row['recommendation']
                )

                self.activity_tree.insert(
                    '', tk.END, values=values, tags=(tag,))

            messagebox.showinfo(
                "Success", f"Risk scores calculated for {
                    len(df)} activities")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def generate_mitigation_plan(self):
        """Generate and display mitigation plan"""
        try:
            if not hasattr(
                    self.main_window,
                    'pert_analyzer') or self.main_window.pert_analyzer is None:
                messagebox.showerror(
                    "Error", "Please run PERT analysis first!")
                return

            # Generate plan
            plan = self.main_window.pert_analyzer.generate_risk_mitigation_plan()

            # Show summary dialog
            summary = f"""Mitigation Plan Summary

Total Activities: {plan['total_activities']}
High Priority: {len(plan['high_priority'])} activities
Medium Priority: {len(plan['medium_priority'])} activities
Low Priority: {len(plan['low_priority'])} activities
Critical Path Risks: {len(plan['critical_path_risks'])} activities

Focus on high-priority activities first!"""

            messagebox.showinfo("Mitigation Plan", summary)

        except Exception as e:
            messagebox.showerror("Error", f"Plan generation failed: {str(e)}")

    def export_activity_risks(self):
        """Export activity risks to CSV"""
        try:
            if self.activity_risks_data is None:
                messagebox.showwarning(
                    "Warning", "Please calculate risk scores first!")
                return

            # Ask for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                self.activity_risks_data.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def show_help(self):
        """Show help dialog"""
        help_text = """Risk Analysis Module Help

This module provides comprehensive project risk assessment:

1. DELAY RISK ANALYSIS
   - Calculate probability of project delay
   - Estimate expected delay period
   - Assess financial risk costs

2. CONTINGENCY PLANNING
   - Estimate time buffers for confidence levels
   - Calculate contingency budgets
   - Get recommendations

3. VARIANCE REDUCTION STRATEGIES
   - Compare time vs variance reduction
   - Optimize mixed strategies
   - Calculate ROI and net benefits

4. ACTIVITY RISK PRIORITIZATION
   - Score activities by risk level
   - Identify high-risk activities
   - Generate mitigation plans

All calculations based on IM 738 methodologies.

Note: Run PERT analysis first before using risk analysis!"""

        messagebox.showinfo("Risk Analysis Help", help_text)

    def update_from_pert_analysis(self):
        """Update when new PERT analysis is available"""
        # Called by main window when PERT analysis completes
        # Could pre-populate some fields based on PERT results


if __name__ == "__main__":
    # For testing purposes
    root = tk.Tk()
    root.title("Risk Analysis Tab Test")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Mock main window
    class MockMainWindow:
        def __init__(self):
            self.pert_analyzer = None

    main_window = MockMainWindow()
    risk_tab = RiskAnalysisTab(notebook, main_window)

    root.mainloop()
