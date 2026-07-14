"""
Resource Leveling Demo

Demonstrates resource leveling and smoothing functionality.
Shows how to:
1. Calculate resource profiles
2. Apply minimum moment leveling
3. Apply Burgess method leveling
4. Compare before/after visualizations
5. Generate reports
"""

import pandas as pd
import matplotlib.pyplot as plt
from pmhelper.core.resource_leveling import (
    Activity,
    ResourceProfile,
    MinimumMomentLeveling,
    BurgessLeveling,
    ResourceLevelingFactory
)
from pmhelper.core.resource_visualizations import (
    plot_resource_profile,
    plot_leveling_metrics,
    plot_gantt_comparison,
    generate_leveling_report,
    export_leveling_results
)


def create_sample_project():
    """Create sample construction project with resource demands"""
    activities = [
        Activity(
            id='A',
            duration=4,
            resource_demand=6.0,
            es=0, ef=4, ls=0, lf=4,
            float=0,
            predecessors=[],
            successors=['B', 'C']
        ),
        Activity(
            id='B',
            duration=5,
            resource_demand=4.0,
            es=4, ef=9, ls=4, lf=9,
            float=0,
            predecessors=['A'],
            successors=['E']
        ),
        Activity(
            id='C',
            duration=3,
            resource_demand=5.0,
            es=4, ef=7, ls=6, lf=9,
            float=2,
            predecessors=['A'],
            successors=['D']
        ),
        Activity(
            id='D',
            duration=4,
            resource_demand=3.0,
            es=7, ef=11, ls=9, lf=13,
            float=2,
            predecessors=['C'],
            successors=['F']
        ),
        Activity(
            id='E',
            duration=2,
            resource_demand=5.0,
            es=9, ef=11, ls=9, lf=11,
            float=0,
            predecessors=['B'],
            successors=['F']
        ),
        Activity(
            id='F',
            duration=3,
            resource_demand=4.0,
            es=11, ef=14, ls=11, lf=14,
            float=0,
            predecessors=['D', 'E'],
            successors=[]
        )
    ]
    return activities


def main():
    """Run resource leveling demo"""
    
    print("="*70)
    print(" RESOURCE LEVELING DEMO".center(70))
    print("="*70)
    print()
    
    # Step 1: Create project
    print("Step 1: Creating Sample Project...")
    print("-" * 70)
    
    activities = create_sample_project()
    
    print(f"Project: Construction with {len(activities)} activities")
    print("\nActivity Details:")
    print("  ID | Duration | Resource | Early Start | Late Start | Float")
    print("  " + "-" * 62)
    for act in activities:
        print(f"  {act.id:2} | {act.duration:8} | {act.resource_demand:8.1f} | "
              f"{act.es:11} | {act.ls:10} | {act.float:5}")
    print()
    
    # Calculate critical path
    critical_activities = [act.id for act in activities if act.float == 0]
    non_critical = [act.id for act in activities if act.float > 0]
    print(f"Critical Path: {' -> '.join(critical_activities)}")
    print(f"Non-Critical Activities: {', '.join(non_critical)} (can be shifted)")
    print()
    
    # Step 2: Calculate original resource profile
    print("Step 2: Analyzing Original Resource Profile...")
    print("-" * 70)
    
    early_start_schedule = {act.id: act.es for act in activities}
    original_profile = ResourceProfile(early_start_schedule, activities)
    
    print(f"Peak Resource Usage: {original_profile.get_peak_usage():.1f} units")
    print(f"Resource Moment: {original_profile.calculate_moment():.2f}")
    print(f"Utilization (limit=10): {original_profile.get_utilization(10.0):.1f}%")
    
    # Check feasibility
    resource_limit = 10.0
    if original_profile.is_feasible(resource_limit):
        print(f"✓ Schedule is FEASIBLE (peak ≤ {resource_limit} units)")
    else:
        overutilized = original_profile.get_overutilized_periods(resource_limit)
        print(f"✗ Schedule EXCEEDS resource limit at {len(overutilized)} periods")
    print()
    
    # Step 3: Apply Minimum Moment Leveling
    print("Step 3: Applying Minimum Moment Leveling...")
    print("-" * 70)
    
    mm_leveler = ResourceLevelingFactory.create('minimum_moment', activities, resource_limit)
    mm_result = mm_leveler.level()
    
    print(f"Algorithm: Minimum Moment Method")
    print(f"Iterations: {mm_result['iterations']}")
    print(f"Original Moment: {mm_result['original_moment']:.2f}")
    print(f"Leveled Moment: {mm_result['leveled_moment']:.2f}")
    print(f"Improvement: {mm_result['improvement_pct']:.1f}%")
    print(f"Peak Reduction: {mm_result['peak_usage_original']:.1f} → {mm_result['peak_usage_leveled']:.1f}")
    print(f"Feasibility: {'✓ FEASIBLE' if mm_result['feasible'] else '✗ INFEASIBLE'}")
    print()
    
    # Show schedule changes
    print("Schedule Changes (Minimum Moment):")
    moved = 0
    for act_id in sorted(mm_result['leveled_schedule'].keys()):
        orig = mm_result['original_schedule'][act_id]
        new = mm_result['leveled_schedule'][act_id]
        if orig != new:
            print(f"  {act_id}: moved from time {orig} to time {new} (shift: {new-orig:+d})")
            moved += 1
    if moved == 0:
        print("  No activities moved (already optimal)")
    print()
    
    # Step 4: Apply Burgess Method
    print("Step 4: Applying Burgess Method...")
    print("-" * 70)
    
    burgess_leveler = ResourceLevelingFactory.create('burgess', activities, resource_limit)
    burgess_result = burgess_leveler.level()
    
    print(f"Algorithm: Burgess Method")
    print(f"Iterations: {burgess_result['iterations']}")
    print(f"Original Cost: {burgess_result['original_cost']:.2f}")
    print(f"Leveled Cost: {burgess_result['leveled_cost']:.2f}")
    print(f"Improvement: {burgess_result['improvement_pct']:.1f}%")
    print(f"Peak Reduction: {burgess_result['peak_usage_original']:.1f} → {burgess_result['peak_usage_leveled']:.1f}")
    print(f"Feasibility: {'✓ FEASIBLE' if burgess_result['feasible'] else '✗ INFEASIBLE'}")
    print()
    
    # Step 5: Compare Methods
    print("Step 5: Comparing Leveling Methods...")
    print("-" * 70)
    
    print("Method Comparison:")
    print(f"  Minimum Moment: {mm_result['improvement_pct']:.1f}% improvement, "
          f"{mm_result['iterations']} iterations")
    print(f"  Burgess Method: {burgess_result['improvement_pct']:.1f}% improvement, "
          f"{burgess_result['iterations']} iterations")
    print()
    
    # Step 6: Generate Visualizations
    print("Step 6: Creating Visualizations...")
    print("-" * 70)
    
    try:
        # Resource profile comparison (Minimum Moment)
        original_df = mm_result['original_profile'].to_dataframe()
        leveled_df = mm_result['leveled_profile'].to_dataframe()
        
        fig1 = plot_resource_profile(original_df, leveled_df, resource_limit, "Minimum Moment")
        fig1.savefig('resource_leveling_profile.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: resource_leveling_profile.png")
        
        # Leveling metrics
        fig2 = plot_leveling_metrics(mm_result)
        fig2.savefig('resource_leveling_metrics.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: resource_leveling_metrics.png")
        
        # Gantt comparison
        fig3 = plot_gantt_comparison(
            mm_result['original_schedule'],
            mm_result['leveled_schedule'],
            activities,
            resource_limit
        )
        fig3.savefig('resource_leveling_gantt.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: resource_leveling_gantt.png")
        
        # Burgess method comparison
        burgess_original_df = burgess_result['original_profile'].to_dataframe()
        burgess_leveled_df = burgess_result['leveled_profile'].to_dataframe()
        
        fig4 = plot_resource_profile(burgess_original_df, burgess_leveled_df, 
                                     resource_limit, "Burgess Method")
        fig4.savefig('resource_leveling_burgess.png', dpi=150, bbox_inches='tight')
        print("✓ Saved: resource_leveling_burgess.png")
        
        plt.close('all')
        
    except Exception as e:
        print(f"⚠ Visualization error: {e}")
    
    print()
    
    # Step 7: Generate Reports
    print("Step 7: Generating Reports...")
    print("-" * 70)
    
    mm_report = generate_leveling_report(mm_result, "Minimum Moment Method")
    burgess_report = generate_leveling_report(burgess_result, "Burgess Method")
    
    # Save reports
    with open('resource_leveling_mm_report.txt', 'w', encoding='utf-8') as f:
        f.write(mm_report)
    print("✓ Saved: resource_leveling_mm_report.txt")
    
    with open('resource_leveling_burgess_report.txt', 'w', encoding='utf-8') as f:
        f.write(burgess_report)
    print("✓ Saved: resource_leveling_burgess_report.txt")
    print()
    
    # Display Minimum Moment report
    print(mm_report)
    
    # Step 8: Export Results
    print("Step 8: Exporting Results...")
    print("-" * 70)
    
    try:
        export_leveling_results(mm_result, 'leveling_results_mm.csv', format='csv')
        print("✓ Saved: leveling_results_mm.csv")
        
        export_leveling_results(mm_result, 'leveling_results_mm.json', format='json')
        print("✓ Saved: leveling_results_mm.json")
        
        export_leveling_results(burgess_result, 'leveling_results_burgess.csv', format='csv')
        print("✓ Saved: leveling_results_burgess.csv")
        
    except Exception as e:
        print(f"⚠ Export error: {e}")
    
    print()
    print("="*70)
    print(" DEMO COMPLETE".center(70))
    print("="*70)
    print()
    print("Generated files:")
    print("  Visualizations:")
    print("    • resource_leveling_profile.png  - Minimum Moment before/after")
    print("    • resource_leveling_burgess.png  - Burgess method before/after")
    print("    • resource_leveling_metrics.png  - Performance metrics")
    print("    • resource_leveling_gantt.png    - Gantt chart comparison")
    print("  Reports:")
    print("    • resource_leveling_mm_report.txt      - Minimum Moment report")
    print("    • resource_leveling_burgess_report.txt - Burgess method report")
    print("  Data:")
    print("    • leveling_results_mm.csv/.json        - Minimum Moment results")
    print("    • leveling_results_burgess.csv         - Burgess results")
    print()


if __name__ == '__main__':
    main()
