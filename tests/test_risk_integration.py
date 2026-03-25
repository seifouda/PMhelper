#!/usr/bin/env python3
"""
Integration test for Risk Analysis with PERT Module
"""

import pytest
from src.pmhelper.core.pert_analyzer import PERTAnalyzer


def test_pert_risk_integration():
    """Test that PERT analyzer integrates correctly with risk analysis"""
    
    # Sample PERT data
    activities_data = [
        {'id': 'A', 'predecessors': '', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 4},
        {'id': 'B', 'predecessors': 'A', 'optimistic': 3, 'most_likely': 4, 'pessimistic': 5},
        {'id': 'C', 'predecessors': 'A', 'optimistic': 4, 'most_likely': 5, 'pessimistic': 9},
        {'id': 'D', 'predecessors': 'B', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 4},
        {'id': 'E', 'predecessors': 'B,C', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 7},
        {'id': 'F', 'predecessors': 'D,E', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 3}
    ]
    
    # Run PERT analysis
    analyzer = PERTAnalyzer()
    network, critical_paths, critical_activities = analyzer.analyze(activities_data)
    
    # Test get_risk_analysis_input
    risk_input = analyzer.get_risk_analysis_input()
    
    assert 'expected_duration' in risk_input
    assert 'variance' in risk_input
    assert 'critical_path' in risk_input
    assert 'activities' in risk_input
    
    assert risk_input['expected_duration'] > 0
    assert risk_input['variance'] >= 0
    assert len(risk_input['critical_path']) > 0
    assert len(risk_input['activities']) > 0
    
    # Test delay risk analysis
    delay_risk = analyzer.analyze_delay_risk(
        contract_time=15.0,
        penalty_rate=1000.0
    )
    
    assert 'delay_probability' in delay_risk
    assert 'expected_delay' in delay_risk
    assert 'risk_cost' in delay_risk
    assert 0 <= delay_risk['delay_probability'] <= 1
    
    # Test contingency planning
    contingency = analyzer.estimate_contingency(
        confidence_level=0.95,
        daily_cost_rate=5000.0
    )
    
    assert 'time_buffer' in contingency
    assert 'buffer_percentage' in contingency
    assert 'contingency_cost' in contingency
    assert contingency['time_buffer'] >= 0
    
    # Test activity risk prioritization
    risk_scores = analyzer.prioritize_activity_risks()
    
    assert len(risk_scores) > 0
    assert 'activity_id' in risk_scores.columns
    assert 'risk_score' in risk_scores.columns
    assert 'recommendation' in risk_scores.columns
    
    # Test mitigation plan generation
    mitigation_plan = analyzer.generate_risk_mitigation_plan()
    
    assert 'high_priority' in mitigation_plan
    assert 'critical_path_risks' in mitigation_plan
    assert 'total_activities' in mitigation_plan
    
    print("✓ All PERT-Risk integration tests passed!")


if __name__ == '__main__':
    test_pert_risk_integration()
    print("\n✓ Integration test completed successfully!")
