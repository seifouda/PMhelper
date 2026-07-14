"""
Cost Optimization Demo

Demonstrates the time-cost trade-off analysis functionality.
This example shows how to:
1. Perform CPM analysis
2. Add indirect cost model
3. Find optimal project duration
4. Generate visualizations and reports
"""

import pandas as pd
import matplotlib.pyplot as plt
from src.pmhelper.core.cpm_analyzer import CPMAnalyzer
from src.pmhelper.core.cost_optimization import (
    IndirectCostModel,
    TimeCostOptimizer,
    integrate_cost_optimization_with_cpm
)
from src.pmhelper.core.cost_visualizations import (
    plot_time_cost_curve,
    generate_cost_report,
    plot_cost_breakdown,
    plot_savings_analysis,
    export_optimization_results
)


def create_sample_project():
    """Create sample project data for demonstration"""
    activities = [
        {
            'id': 'A',
            'activity': 'Site Preparation',
            'duration': 4,
            'min_duration': 3,
            'normal_cost': 1000,
            'crash_cost': 1200,
            'predecessors': [],
            'resource_demand': 5
        },
        {
            'id': 'B',
            'activity': 'Foundation',
            'duration': 6,
            'min_duration': 4,
            'normal_cost': 1500,
            'crash_cost': 2000,
            'predecessors': ['A'],
            'resource_demand': 3
        },
        {
            'id': 'C',
            'activity': 'Frame Structure',
            'duration': 3,
            'min_duration': 2,
            'normal_cost': 800,
            'crash_cost': 1000,
            'predecessors': ['A'],
            'resource_demand': 2
        },
        {
            'id': 'D',
            'activity': 'Roofing',
            'duration': 5,
            'min_duration': 4,
            'normal_cost': 1200,
            'crash_cost': 1400,
            'predecessors': ['B', 'C'],
            'resource_demand': 4
        },
        {
            'id': 'E',
            'activity': 'Interior Work',
            'duration': 2,
            'min_duration': 1,
            'normal_cost': 500,
            'crash_cost': 700,
            'predecessors': ['D'],
            'resource_demand': 3
        }
    ]
    return activities


def main():
    """Run cost optimization demo"""
    
    print("="*70)
    print(" COST OPTIMIZATION DEMO".center(70))
    print("="*70)
    print()
    
    # Step 1: Create and analyze project with CPM
    print("Step 1: Performing CPM Analysis...")
    print("-" * 70)
    
    cpm = CPMAnalyzer()
    activities = create_sample_project()
    G, critical_paths, critical_activities = cpm.analyze(activities)
    
    # Get project duration from End node's EF
    project_duration = max([G.nodes[node].get('EF', 0) for node in G.nodes()])
    cpm.project_duration = int(project_duration)  # Store for later use
    
    print(f"Project Duration: {cpm.project_duration} days")
    print(f"Critical Path: {' -> '.join(critical_paths[0]) if critical_paths else 'N/A'}")
    print(f"Critical Activities: {', '.join(critical_activities)}")
    print()
    
    # Step 2: Set up indirect cost model
    print("Step 2: Setting up Indirect Cost Model...")
    print("-" * 70)
    
    indirect_costs = {
        'facilities': 200.0,      # Site facilities rental
        'equipment': 150.0,        # Equipment rental
        'utilities': 50.0,         # Utilities (power, water)
        'overhead': 100.0          # Administrative overhead
    }
    
    total_daily_rate = sum(indirect_costs.values())
    print(f"Indirect Cost Categories:")
    for category, rate in indirect_costs.items():
        print(f"  - {category.capitalize()}: ${rate:.2f}/day")
    print(f"Total Daily Rate: ${total_daily_rate:.2f}/day")
    print()
    
    # Step 3: Integrate cost optimization with CPM
    print("Step 3: Integrating Cost Optimization...")
    print("-" * 70)
    
    integrate_cost_optimization_with_cpm(cpm)
    cpm.attach_indirect_costs(indirect_costs)
    print("✓ Cost optimization integrated with CPM analyzer")
    print()
    
    # Step 4: Find optimal duration
    print("Step 4: Finding Optimal Project Duration...")
    print("-" * 70)
    
    optimal_result = cpm.optimize_cost()
    
    print(f"Normal Schedule:")
    print(f"  Duration: {optimal_result['normal_duration']} days")
    print(f"  Direct Cost: ${optimal_result['normal_direct']:,.2f}")
    print(f"  Indirect Cost: ${optimal_result['normal_indirect']:,.2f}")
    print(f"  Total Cost: ${optimal_result['normal_total']:,.2f}")
    print()
    
    print(f"Optimized Schedule:")
    print(f"  Duration: {optimal_result['optimal_duration']} days")
    print(f"  Direct Cost: ${optimal_result['direct_cost']:,.2f}")
    print(f"  Indirect Cost: ${optimal_result['indirect_cost']:,.2f}")
    print(f"  Total Cost: ${optimal_result['optimal_total_cost']:,.2f}")
    print()
    
    print(f"Savings:")
    print(f"  Amount: ${optimal_result['savings_vs_normal']:,.2f}")
    print(f"  Percentage: {optimal_result['savings_pct']:.1f}%")
    print(f"  Time Saved: {optimal_result['normal_duration'] - optimal_result['optimal_duration']} days")
    print()
    
    if optimal_result['activities_crashed']:
        print(f"Activities Crashed: {', '.join(optimal_result['activities_crashed'])}")
    else:
        print("No activities crashed (normal schedule is optimal)")
    print()
    
    # Step 5: Get full optimization curve
    print("Step 5: Generating Time-Cost Curve...")
    print("-" * 70)
    
    curve_data = cpm.get_optimization_curve()
    print(f"Generated curve with {len(curve_data)} data points")
    print()
    print("Time-Cost Curve Data:")
    print(curve_data.to_string(index=False))
    print()
    
    # Step 6: Generate visualizations
    print("Step 6: Creating Visualizations...")
    print("-" * 70)
    
    try:
        # Time-cost curve plot
        fig1 = plot_time_cost_curve(curve_data, optimal_result)
        fig1.savefig('cost_optimization_curve.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: cost_optimization_curve.png")
        
        # Cost breakdown plot
        fig2 = plot_cost_breakdown(optimal_result)
        fig2.savefig('cost_breakdown.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: cost_breakdown.png")
        
        # Savings analysis plot
        fig3 = plot_savings_analysis(curve_data, optimal_result)
        fig3.savefig('savings_analysis.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: savings_analysis.png")
        
        plt.close('all')
        
    except Exception as e:
        print(f"⚠ Visualization error: {e}")
    
    print()
    
    # Step 7: Generate report
    print("Step 7: Generating Report...")
    print("-" * 70)
    
    report = generate_cost_report(cpm, optimal_result)
    
    # Save report to file
    with open('cost_optimization_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("✓ Saved: cost_optimization_report.txt")
    print()
    
    # Display report
    print(report)
    
    # Step 8: Export results
    print("Step 8: Exporting Results...")
    print("-" * 70)
    
    try:
        export_optimization_results(curve_data, optimal_result, 
                                   'optimization_results.csv', format='csv')
        print("✓ Saved: optimization_results.csv")
        
        export_optimization_results(curve_data, optimal_result,
                                   'optimization_results.json', format='json')
        print("✓ Saved: optimization_results.json")
        
    except Exception as e:
        print(f"⚠ Export error: {e}")
    
    print()
    print("="*70)
    print(" DEMO COMPLETE".center(70))
    print("="*70)
    print()
    print("Generated files:")
    print("  • cost_optimization_curve.png    - Time-cost trade-off curve")
    print("  • cost_breakdown.png             - Cost breakdown comparison")
    print("  • savings_analysis.png           - Savings analysis visualization")
    print("  • cost_optimization_report.txt   - Detailed text report")
    print("  • optimization_results.csv       - Curve data (CSV format)")
    print("  • optimization_results.json      - Full results (JSON format)")
    print()


if __name__ == '__main__':
    main()
