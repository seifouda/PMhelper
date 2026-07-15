"""
Multi-Objective Optimization & NPV Demo

Demonstrates NPV-based schedule optimization, Pareto frontier analysis,
and multi-objective trade-off analysis for project management.

This demo shows:
1. NPV optimization with discount rate sensitivity
2. Multi-objective optimization (duration, cost, NPV)
3. Pareto frontier visualization
4. Trade-off analysis between objectives

Author: PMHelper Team
Version: 1.1.0
"""

import sys

# cp1252 Windows consoles cannot encode the box-drawing glyphs below.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.core.npv_optimization import NPVOptimizer, CashFlowActivity
from pmhelper.core.multi_objective import (
    MultiObjectiveOptimizer, Solution, ScheduleGenerator
)
from pmhelper.core.multi_objective_visualizations import (
    plot_pareto_frontier_2d, plot_pareto_frontier_3d,
    plot_npv_sensitivity, plot_tradeoff_analysis,
    plot_objective_comparison, generate_multi_objective_report,
    export_pareto_solutions
)


def create_example_project():
    """
    Create example project with cash flows.
    
    Project: Software Development with Revenue Milestones
    Activities:
    - Design (5 days): Revenue at completion: $20,000
    - Development (10 days): Cost: $15,000
    - Testing (6 days): Revenue milestone: $25,000
    - Documentation (4 days): Cost: $5,000
    - Deployment (3 days): Final revenue: $30,000
    """
    activities = [
        # ID, duration, cash_flow, es, ef, ls, lf, float, predecessors, successors
        CashFlowActivity('Design', 5, 20000, 0, 5, 0, 5, 0, [], ['Development', 'Documentation']),
        CashFlowActivity('Development', 10, -15000, 5, 15, 5, 15, 0, ['Design'], ['Testing']),
        CashFlowActivity('Testing', 6, 25000, 15, 21, 15, 21, 0, ['Development'], ['Deployment']),
        CashFlowActivity('Documentation', 4, -5000, 5, 9, 17, 21, 12, ['Design'], ['Deployment']),
        CashFlowActivity('Deployment', 3, 30000, 21, 24, 21, 24, 0, ['Testing', 'Documentation'], [])
    ]
    
    return activities


def demo_npv_optimization():
    """Demonstrate NPV optimization"""
    print("=" * 80)
    print("NPV OPTIMIZATION DEMO")
    print("=" * 80)
    print()
    
    # Create project
    activities = create_example_project()
    
    print("Project Activities:")
    print("-" * 80)
    for act in activities:
        print(f"{act.id:15} Duration: {act.duration:2d} days, "
              f"Cash Flow: ${act.cash_flow:8,.0f}, Float: {act.float:2d} days")
    print()
    
    # Create optimizer
    discount_rate = 0.10  # 10% annual discount rate
    optimizer = NPVOptimizer(activities, discount_rate=discount_rate)
    
    print(f"Discount Rate: {discount_rate*100:.0f}%")
    print()
    
    # Calculate baseline NPV
    baseline_npv = optimizer.calculate_npv(optimizer.original_schedule)
    print(f"Baseline NPV (Early Start Schedule): ${baseline_npv:,.2f}")
    print()
    
    # Optimize
    print("Optimizing schedule for maximum NPV...")
    result = optimizer.maximize_npv()
    
    print(f"\nOptimization Results:")
    print("-" * 80)
    print(f"Original NPV:    ${result['original_npv']:,.2f}")
    print(f"Optimized NPV:   ${result['optimal_npv']:,.2f}")
    print(f"Improvement:     ${result['improvement']:,.2f} ({result['improvement_pct']:.2f}%)")
    print(f"Iterations:      {result['iterations']}")
    print()
    
    if result['moved_activities']:
        print("Activities Repositioned:")
        print("-" * 80)
        for moved in result['moved_activities']:
            print(f"{moved['id']:15} Original: {moved['original_start']:2d}, "
                  f"Optimal: {moved['optimal_start']:2d}, "
                  f"Cash Flow: ${moved['cash_flow']:8,.0f}")
        print()
    
    # Cash flow schedule
    cf_schedule = optimizer.get_cash_flow_schedule(result['optimal_schedule'])
    print("Cash Flow Schedule (Optimized):")
    print("-" * 80)
    print(cf_schedule.to_string(index=False))
    print()
    
    return optimizer, result


def demo_sensitivity_analysis(optimizer):
    """Demonstrate discount rate sensitivity"""
    print("=" * 80)
    print("DISCOUNT RATE SENSITIVITY ANALYSIS")
    print("=" * 80)
    print()
    
    # Test range of discount rates
    rates = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20]
    
    print(f"Testing {len(rates)} discount rates: {[f'{r*100:.0f}%' for r in rates]}")
    print()
    
    sensitivity_df = optimizer.sensitivity_analysis(rates)
    
    print("Sensitivity Analysis Results:")
    print("-" * 80)
    print(sensitivity_df.to_string(index=False))
    print()
    
    # Plot sensitivity
    fig = plot_npv_sensitivity(
        sensitivity_df,
        title='NPV Sensitivity to Discount Rate',
        save_path='npv_sensitivity.png'
    )
    plt.close(fig)
    print("✓ Saved: npv_sensitivity.png")
    print()
    
    return sensitivity_df


def demo_multi_objective_optimization(activities):
    """Demonstrate multi-objective optimization with Pareto frontier"""
    print("=" * 80)
    print("MULTI-OBJECTIVE OPTIMIZATION DEMO")
    print("=" * 80)
    print()
    
    # Define objective functions
    def calculate_duration(schedule):
        """Calculate project duration"""
        max_finish = 0
        for act in activities:
            start = schedule.get(act.id, act.es)
            finish = start + act.duration
            max_finish = max(max_finish, finish)
        return max_finish
    
    def calculate_cost(schedule):
        """Calculate total negative cash flows (costs)"""
        total_cost = sum(abs(act.cash_flow) for act in activities if act.cash_flow < 0)
        return total_cost
    
    def calculate_npv(schedule):
        """Calculate NPV for schedule"""
        discount_rate = 0.10
        npv = 0
        for act in activities:
            start = schedule.get(act.id, act.es)
            finish = start + act.duration
            if act.cash_flow != 0:
                pv = act.cash_flow / ((1 + discount_rate) ** finish)
                npv += pv
        return npv
    
    # Create multi-objective optimizer
    objectives = {
        'duration': calculate_duration,
        'cost': calculate_cost,
        'npv': lambda s: -calculate_npv(s)  # Negative to minimize (maximize actual NPV)
    }
    
    print("Objectives:")
    print("  1. Minimize Duration (days)")
    print("  2. Minimize Cost ($)")
    print("  3. Maximize NPV ($) [shown as minimize -NPV]")
    print()
    
    optimizer = MultiObjectiveOptimizer(objectives)
    
    # Generate candidate schedules
    print("Generating candidate schedules...")
    schedules = ScheduleGenerator.generate_sampled(activities, num_samples=100)
    print(f"Generated {len(schedules)} candidate schedules")
    print()
    
    # Compute Pareto frontier
    print("Computing Pareto frontier...")
    frontier = optimizer.generate_solutions_grid(
        schedules,
        minimize_objectives=['duration', 'cost', 'npv']
    )
    
    print(f"Pareto frontier contains {len(frontier)} non-dominated solutions")
    print(f"Out of {len(optimizer.solutions)} total solutions evaluated")
    print()
    
    # Get summaries
    solutions_df = optimizer.get_solution_summary()
    pareto_df = optimizer.get_pareto_summary()
    
    # Convert NPV back to positive for display
    solutions_df['npv_actual'] = -solutions_df['npv']
    pareto_df['npv_actual'] = -pareto_df['npv']
    
    print("Pareto Frontier Solutions:")
    print("-" * 80)
    display_cols = ['pareto_rank', 'duration', 'cost', 'npv_actual']
    print(pareto_df[display_cols].to_string(index=False))
    print()
    
    return optimizer, solutions_df, pareto_df


def demo_visualizations(optimizer, solutions_df, pareto_df):
    """Create visualizations for multi-objective analysis"""
    print("=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    print()
    
    # 2D Pareto frontiers
    print("Creating 2D Pareto frontier plots...")
    
    # Duration vs Cost
    fig1 = plot_pareto_frontier_2d(
        solutions_df, 'duration', 'cost',
        minimize_obj1=True, minimize_obj2=True,
        title='Pareto Frontier: Duration vs Cost',
        save_path='pareto_duration_cost.png'
    )
    plt.close(fig1)
    print("✓ Saved: pareto_duration_cost.png")
    
    # Duration vs NPV (flip sign for display)
    solutions_df_display = solutions_df.copy()
    solutions_df_display['npv_actual'] = -solutions_df_display['npv']
    
    fig2 = plot_pareto_frontier_2d(
        solutions_df_display, 'duration', 'npv_actual',
        minimize_obj1=True, minimize_obj2=False,  # Maximize NPV
        title='Pareto Frontier: Duration vs NPV',
        save_path='pareto_duration_npv.png'
    )
    plt.close(fig2)
    print("✓ Saved: pareto_duration_npv.png")
    
    # Cost vs NPV
    fig3 = plot_pareto_frontier_2d(
        solutions_df_display, 'cost', 'npv_actual',
        minimize_obj1=True, minimize_obj2=False,
        title='Pareto Frontier: Cost vs NPV',
        save_path='pareto_cost_npv.png'
    )
    plt.close(fig3)
    print("✓ Saved: pareto_cost_npv.png")
    
    # 3D Pareto frontier
    print("\nCreating 3D Pareto frontier plot...")
    fig4 = plot_pareto_frontier_3d(
        solutions_df_display, 'duration', 'cost', 'npv_actual',
        title='3D Pareto Frontier: Duration, Cost, NPV',
        save_path='pareto_3d.png'
    )
    plt.close(fig4)
    print("✓ Saved: pareto_3d.png")
    
    # Trade-off analysis
    print("\nCreating trade-off analysis plots...")
    tradeoffs_dc = optimizer.find_tradeoffs('duration', 'cost')
    if not tradeoffs_dc.empty:
        fig5 = plot_tradeoff_analysis(
            tradeoffs_dc, 'duration', 'cost',
            title='Trade-off Analysis: Duration vs Cost',
            save_path='tradeoff_duration_cost.png'
        )
        plt.close(fig5)
        print("✓ Saved: tradeoff_duration_cost.png")
    
    # Parallel coordinates
    print("\nCreating objective comparison plot...")
    fig6 = plot_objective_comparison(
        solutions_df_display,
        objectives=['duration', 'cost', 'npv_actual'],
        normalize=True,
        title='Multi-Objective Comparison (Normalized)',
        save_path='objective_comparison.png'
    )
    plt.close(fig6)
    print("✓ Saved: objective_comparison.png")
    
    print()


def demo_export_results(optimizer, pareto_df):
    """Export results in multiple formats"""
    print("=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    print()
    
    # Generate report
    print("Generating multi-objective optimization report...")
    objectives = ['duration', 'cost', 'npv_actual']
    report = generate_multi_objective_report(
        optimizer, pareto_df, objectives,
        save_path='multi_objective_report.txt'
    )
    print("✓ Saved: multi_objective_report.txt")
    
    # Export Pareto solutions
    print("\nExporting Pareto solutions...")
    pareto_schedules = [sol.schedule for sol in optimizer.pareto_frontier]
    export_pareto_solutions(
        pareto_df, pareto_schedules,
        base_path='pareto_solutions',
        formats=['csv', 'json', 'excel']
    )
    print("✓ Saved: pareto_solutions.csv")
    print("✓ Saved: pareto_solutions.json")
    print("✓ Saved: pareto_solutions.xlsx")
    
    print()


def main():
    """Run complete multi-objective optimization demo"""
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  MULTI-OBJECTIVE OPTIMIZATION & NPV DEMO".center(78) + "║")
    print("║" + "  PMHelper - Advanced Project Scheduling".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    try:
        # Part 1: NPV Optimization
        optimizer_npv, npv_result = demo_npv_optimization()
        
        # Part 2: Sensitivity Analysis
        sensitivity_df = demo_sensitivity_analysis(optimizer_npv)
        
        # Part 3: Multi-Objective Optimization
        activities = create_example_project()
        optimizer_mo, solutions_df, pareto_df = demo_multi_objective_optimization(activities)
        
        # Part 4: Visualizations
        demo_visualizations(optimizer_mo, solutions_df, pareto_df)
        
        # Part 5: Export Results
        demo_export_results(optimizer_mo, pareto_df)
        
        # Summary
        print("=" * 80)
        print("DEMO SUMMARY")
        print("=" * 80)
        print()
        print("NPV Optimization:")
        print(f"  • NPV Improvement: ${npv_result['improvement']:,.2f} ({npv_result['improvement_pct']:.2f}%)")
        print(f"  • Optimized NPV: ${npv_result['optimal_npv']:,.2f}")
        print()
        print("Multi-Objective Optimization:")
        print(f"  • Total Solutions Evaluated: {len(optimizer_mo.solutions)}")
        print(f"  • Pareto Frontier Size: {len(optimizer_mo.pareto_frontier)}")
        print(f"  • Pareto Efficiency: {len(optimizer_mo.pareto_frontier)/len(optimizer_mo.solutions)*100:.1f}%")
        print()
        print("Files Generated:")
        print("  • 7 visualization plots (PNG)")
        print("  • 1 text report")
        print("  • 3 data exports (CSV, JSON, Excel)")
        print()
        print("=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        
        return 0
    
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR OCCURRED")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
