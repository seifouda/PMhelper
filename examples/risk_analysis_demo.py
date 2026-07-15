#!/usr/bin/env python3
"""
Risk Analysis Example - Simple Demonstration

This script demonstrates all four risk analysis capabilities:
1. Delay Risk Analysis
2. Contingency Planning
3. Variance Reduction Strategies
4. Activity Risk Prioritization
"""

import sys

# The default Windows console is cp1252 and raises UnicodeEncodeError on the
# box-drawing and check-mark glyphs this demo prints. Force UTF-8 so it runs
# on a stock Windows terminal as documented.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd
from pmhelper.core.pert_analyzer import PERTAnalyzer


def main():
    print("=" * 70)
    print("PMHelper Risk Analysis Module - Demonstration")
    print("=" * 70)
    print()
    
    # Sample project data (from delay_analysis_simple.csv)
    activities_data = [
        {'id': 'A', 'predecessors': '', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 4},
        {'id': 'B', 'predecessors': 'A', 'optimistic': 3, 'most_likely': 4, 'pessimistic': 5},
        {'id': 'C', 'predecessors': 'A', 'optimistic': 4, 'most_likely': 5, 'pessimistic': 9},
        {'id': 'D', 'predecessors': 'B', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 4},
        {'id': 'E', 'predecessors': 'B,C', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 7},
        {'id': 'F', 'predecessors': 'D,E', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 3}
    ]
    
    print("Step 1: Running PERT Analysis...")
    print("-" * 70)
    
    # Run PERT analysis
    analyzer = PERTAnalyzer()
    network, critical_paths, critical_activities = analyzer.analyze(activities_data)
    
    stats = analyzer.get_project_statistics()
    print(f"Expected Duration: {stats['expected_duration']:.2f} weeks")
    print(f"Project Variance: {stats['variance']:.2f}")
    print(f"Standard Deviation: {stats['std_deviation']:.2f} weeks")
    print(f"Critical Path: {' → '.join(stats['critical_path'])}")
    print()
    
    # 1. Delay Risk Analysis
    print("=" * 70)
    print("1. DELAY RISK ANALYSIS")
    print("=" * 70)
    
    contract_time = 15.0
    penalty_rate = 1000.0
    
    print(f"Contract Time: {contract_time} weeks")
    print(f"Penalty Rate: ${penalty_rate:,.0f} per week")
    print()
    
    delay_risk = analyzer.analyze_delay_risk(
        contract_time=contract_time,
        penalty_rate=penalty_rate,
        max_penalty_percent=0.20
    )
    
    print(f"Delay Probability: {delay_risk['delay_probability']:.1%}")
    print(f"Expected Delay (if it occurs): {delay_risk['expected_delay']:.2f} weeks")
    print(f"Risk Cost: ${delay_risk['risk_cost']:,.2f}")
    print(f"Z-Score: {delay_risk['z_score']:.2f}")
    print()
    
    if delay_risk['delay_probability'] > 0.3:
        print("⚠️  WARNING: High delay risk! Consider mitigation strategies.")
    elif delay_risk['delay_probability'] > 0.1:
        print("⚠️  MODERATE: Some delay risk exists. Monitor closely.")
    else:
        print("✓ LOW RISK: Project likely to complete on time.")
    print()
    
    # 2. Contingency Planning
    print("=" * 70)
    print("2. CONTINGENCY PLANNING")
    print("=" * 70)
    
    for confidence in [0.80, 0.90, 0.95, 0.99]:
        contingency = analyzer.estimate_contingency(
            confidence_level=confidence,
            daily_cost_rate=5000.0
        )
        
        print(f"\nConfidence Level: {confidence*100:.0f}%")
        print(f"  Time Buffer: {contingency['time_buffer']:.2f} weeks ({contingency['buffer_percentage']:.1f}%)")
        print(f"  Completion Time: {contingency['completion_time']:.2f} weeks")
        print(f"  Contingency Cost: ${contingency['contingency_cost']:,.2f}")
    print()
    
    # 3. Variance Reduction Strategies
    print("=" * 70)
    print("3. VARIANCE REDUCTION STRATEGIES")
    print("=" * 70)
    
    strategies = analyzer.analyze_variance_reduction_strategies(
        contract_time=15.0,
        penalty_rate=1000.0,
        time_reduction_cost=3000.0,
        variance_reduction_cost=2000.0,
        max_budget=30000.0
    )
    
    print(f"Baseline Risk Cost: ${strategies['baseline']['risk_cost']:,.2f}")
    print()
    
    print("Strategy A (Reduce Time):")
    print(f"  Time Reduction: {strategies['strategy_a']['time_reduction']:.2f} weeks")
    print(f"  Investment: ${strategies['strategy_a']['investment']:,.2f}")
    print(f"  Benefit: ${strategies['strategy_a']['benefit']:,.2f}")
    print(f"  Net Benefit: ${strategies['strategy_a']['net_benefit']:,.2f}")
    print(f"  ROI: {strategies['strategy_a']['roi']:.1f}%")
    print()
    
    print("Strategy B (Reduce Variance):")
    print(f"  Variance Reduction: {strategies['strategy_b']['variance_reduction']:.2f}")
    print(f"  Investment: ${strategies['strategy_b']['investment']:,.2f}")
    print(f"  Benefit: ${strategies['strategy_b']['benefit']:,.2f}")
    print(f"  Net Benefit: ${strategies['strategy_b']['net_benefit']:,.2f}")
    print(f"  ROI: {strategies['strategy_b']['roi']:.1f}%")
    print()
    
    print("Mixed Strategy:")
    print(f"  Time Reduction: {strategies['mixed_strategy']['time_reduction']:.2f} weeks")
    print(f"  Variance Reduction: {strategies['mixed_strategy']['variance_reduction']:.2f}")
    print(f"  Investment: ${strategies['mixed_strategy']['investment']:,.2f}")
    print(f"  Benefit: ${strategies['mixed_strategy']['benefit']:,.2f}")
    print(f"  Net Benefit: ${strategies['mixed_strategy']['net_benefit']:,.2f}")
    print(f"  ROI: {strategies['mixed_strategy']['roi']:.1f}%")
    print()
    
    print(f"✓ RECOMMENDED: {strategies['best_strategy']['name']}")
    print(f"  Best Net Benefit: ${strategies['best_strategy']['net_benefit']:,.2f}")
    print()
    
    # 4. Activity Risk Prioritization
    print("=" * 70)
    print("4. ACTIVITY RISK PRIORITIZATION")
    print("=" * 70)
    print()
    
    risk_scores = analyzer.prioritize_activity_risks()
    
    print("Top 5 High-Risk Activities:")
    print()
    
    # Display top 5
    top_risks = risk_scores.head(5)
    
    for idx, row in top_risks.iterrows():
        print(f"Activity {row['activity_id']} (Risk Score: {row['risk_score']:.3f})")
        print(f"  Expected Time: {row['expected_time']:.2f} weeks")
        print(f"  Variance: {row['variance']:.3f}")
        print(f"  Float: {row['total_float']:.2f}")
        print(f"  Recommendation: {row['recommendation']}")
        print()
    
    # Generate mitigation plan
    print("=" * 70)
    print("MITIGATION PLAN SUMMARY")
    print("=" * 70)
    
    mitigation_plan = analyzer.generate_risk_mitigation_plan()
    
    print(f"Total Activities Analyzed: {mitigation_plan['total_activities']}")
    print(f"High Priority Risks: {len(mitigation_plan['high_priority'])}")
    print(f"Medium Priority Risks: {len(mitigation_plan['medium_priority'])}")
    print(f"Low Priority Risks: {len(mitigation_plan['low_priority'])}")
    print(f"Critical Path Risks: {len(mitigation_plan['critical_path_risks'])}")
    print()
    
    print("✓ Risk analysis complete!")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
