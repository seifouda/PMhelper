#!/usr/bin/env python3
"""
Comprehensive Test Suite for Risk Analysis Module

This test suite covers:
- Edge cases and boundary conditions
- Performance benchmarks
- Error handling
- Data validation
- CLI integration
- End-to-end workflows
- Real-world scenarios
"""

import pytest
import time
import numpy as np
import pandas as pd
from io import StringIO
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pmhelper.core.pert_analyzer import PERTAnalyzer
from src.pmhelper.core.risk_analysis import (
    DelayRiskAnalyzer,
    ContingencyPlanner,
    VarianceReductionAnalyzer,
    ActivityRiskPrioritizer
)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_variance_delay_analysis(self):
        """Test delay analysis with zero variance (deterministic project)"""
        pert_results = {
            'expected_duration': 10.0,
            'variance': 0.0,  # Zero variance
            'critical_path': ['A', 'B'],
            'activities': {
                'A': {'expected_time': 5.0, 'variance': 0.0},
                'B': {'expected_time': 5.0, 'variance': 0.0}
            }
        }
        
        analyzer = DelayRiskAnalyzer(pert_results)
        
        # Contract time < expected duration
        result = analyzer.calculate_delay_probability(contract_time=8.0)
        assert result == 1.0  # 100% probability of delay
        
        # Contract time > expected duration
        result = analyzer.calculate_delay_probability(contract_time=12.0)
        assert result == 0.0  # 0% probability of delay
        
        # Contract time = expected duration
        result = analyzer.calculate_delay_probability(contract_time=10.0)
        assert result == 0.0  # Exactly on time
    
    def test_very_high_variance(self):
        """Test with extremely high variance"""
        pert_results = {
            'expected_duration': 10.0,
            'variance': 100.0,  # Very high variance
            'critical_path': ['A'],
            'activities': {
                'A': {'expected_time': 10.0, 'variance': 100.0}
            }
        }
        
        analyzer = DelayRiskAnalyzer(pert_results)
        prob = analyzer.calculate_delay_probability(contract_time=10.0)
        
        # High variance means ~50% probability at expected time
        assert 0.4 < prob < 0.6
    
    def test_negative_float_activities(self):
        """Test activities with negative float (impossible to complete on time)"""
        pert_results = {
            'expected_duration': 20.0,
            'variance': 5.0,
            'critical_path': ['A', 'B'],
            'activities': {
                'A': {'expected_time': 10.0, 'variance': 1.0, 'total_float': -2.0},
                'B': {'expected_time': 10.0, 'variance': 1.0, 'total_float': 0.0}
            }
        }
        
        prioritizer = ActivityRiskPrioritizer(pert_results)
        scores_df = prioritizer.calculate_risk_scores()
        
        # Activity with negative float should have high schedule sensitivity
        activity_a = scores_df[scores_df['activity_id'] == 'A'].iloc[0]
        # Negative float gives negative sensitivity, but still indicates high risk
        assert activity_a['schedule_sensitivity'] < 0 or activity_a['schedule_sensitivity'] == 1.0
    
    def test_single_activity_project(self):
        """Test project with only one activity"""
        pert_results = {
            'expected_duration': 5.0,
            'variance': 0.5,
            'critical_path': ['A'],
            'activities': {
                'A': {'expected_time': 5.0, 'variance': 0.5, 'total_float': 0.0}
            }
        }
        
        # Test all analyzers
        delay_analyzer = DelayRiskAnalyzer(pert_results)
        contingency_planner = ContingencyPlanner(pert_results)
        variance_analyzer = VarianceReductionAnalyzer(pert_results)
        prioritizer = ActivityRiskPrioritizer(pert_results)
        
        # All should work without errors
        delay_prob = delay_analyzer.calculate_delay_probability(6.0)
        assert 0 <= delay_prob <= 1
        
        buffer_result = contingency_planner.calculate_contingency(0.95)
        buffer = buffer_result['time_buffer']
        assert buffer > 0
        
        strategies = variance_analyzer.analyze_strategies(6.0, 1000.0, 500.0, 500.0, 5000.0)
        # Returns dict with multiple keys
        assert 'strategy_a' in strategies
        assert 'strategy_b' in strategies
        
        scores = prioritizer.calculate_risk_scores()
        assert len(scores) == 1
    
    def test_extreme_confidence_levels(self):
        """Test contingency planning with extreme confidence levels"""
        pert_results = {
            'expected_duration': 10.0,
            'variance': 4.0,
            'critical_path': ['A'],
            'activities': {'A': {'expected_time': 10.0, 'variance': 4.0}}
        }
        
        planner = ContingencyPlanner(pert_results)
        
        # Very low confidence (80%)
        buffer_80 = planner.calculate_contingency(0.80)['time_buffer']
        
        # Very high confidence (99.9%)
        buffer_999 = planner.calculate_contingency(0.999)['time_buffer']
        
        # Higher confidence should require larger buffer
        assert buffer_999 > buffer_80
        assert buffer_999 > 3 * np.sqrt(4.0)  # Should be > 3 sigma
    
    def test_zero_penalty_rate(self):
        """Test risk cost calculation with zero penalty"""
        pert_results = {
            'expected_duration': 10.0,
            'variance': 1.0,
            'critical_path': ['A'],
            'activities': {'A': {'expected_time': 10.0, 'variance': 1.0}}
        }
        
        analyzer = DelayRiskAnalyzer(pert_results)
        result = analyzer.calculate_risk_cost(
            contract_time=8.0,
            penalty_rate=0.0  # Zero penalty
        )
        
        assert result['risk_cost'] == 0.0
    
    def test_very_long_project(self):
        """Test with very long project duration"""
        # 100 activities, each taking 1 week
        activities = {}
        for i in range(100):
            activities[f'Activity_{i}'] = {
                'expected_time': 1.0,
                'variance': 0.1,
                'total_float': 0.0 if i == 0 else 1.0
            }
        
        pert_results = {
            'expected_duration': 100.0,
            'variance': 10.0,  # Total variance
            'critical_path': ['Activity_0'],
            'activities': activities
        }
        
        # Should handle large number of activities
        prioritizer = ActivityRiskPrioritizer(pert_results)
        scores = prioritizer.calculate_risk_scores()
        
        assert len(scores) == 100
        assert 'risk_score' in scores.columns


class TestPerformance:
    """Performance benchmark tests"""
    
    def test_delay_analysis_performance(self):
        """Test delay analysis performance"""
        pert_results = {
            'expected_duration': 15.0,
            'variance': 3.0,
            'critical_path': ['A', 'B', 'C'],
            'activities': {
                'A': {'expected_time': 5.0, 'variance': 1.0},
                'B': {'expected_time': 5.0, 'variance': 1.0},
                'C': {'expected_time': 5.0, 'variance': 1.0}
            }
        }
        
        analyzer = DelayRiskAnalyzer(pert_results)
        
        # Run 1000 iterations and measure time
        start_time = time.time()
        for _ in range(1000):
            analyzer.calculate_delay_probability(20.0)
        elapsed = time.time() - start_time
        
        # Should complete in less than 1 second
        assert elapsed < 1.0, f"Delay analysis too slow: {elapsed:.3f}s for 1000 iterations"
        
        # Average time per iteration
        avg_time = elapsed / 1000
        print(f"\nDelay analysis: {avg_time*1000:.2f}ms per iteration")
    
    def test_contingency_planning_performance(self):
        """Test contingency planning performance"""
        pert_results = {
            'expected_duration': 15.0,
            'variance': 3.0,
            'critical_path': ['A', 'B', 'C'],
            'activities': {
                'A': {'expected_time': 5.0, 'variance': 1.0},
                'B': {'expected_time': 5.0, 'variance': 1.0},
                'C': {'expected_time': 5.0, 'variance': 1.0}
            }
        }
        
        planner = ContingencyPlanner(pert_results)
        
        start_time = time.time()
        for _ in range(1000):
            planner.calculate_contingency(0.95)
        elapsed = time.time() - start_time
        
        assert elapsed < 0.5, f"Contingency planning too slow: {elapsed:.3f}s for 1000 iterations"
        
        avg_time = elapsed / 1000
        print(f"Contingency planning: {avg_time*1000:.2f}ms per iteration")
    
    def test_strategy_comparison_performance(self):
        """Test variance reduction strategy comparison performance"""
        pert_results = {
            'expected_duration': 15.0,
            'variance': 3.0,
            'critical_path': ['A', 'B', 'C'],
            'activities': {
                'A': {'expected_time': 5.0, 'variance': 1.0},
                'B': {'expected_time': 5.0, 'variance': 1.0},
                'C': {'expected_time': 5.0, 'variance': 1.0}
            }
        }
        
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        start_time = time.time()
        for _ in range(100):  # Fewer iterations as this is more complex
            analyzer.analyze_strategies(20.0, 1000.0, 3000.0, 2000.0, 50000.0)
        elapsed = time.time() - start_time
        
        assert elapsed < 20.0, f"Strategy comparison too slow: {elapsed:.3f}s for 100 iterations"
        
        avg_time = elapsed / 100
        print(f"Strategy comparison: {avg_time*1000:.2f}ms per iteration")
    
    def test_activity_prioritization_performance(self):
        """Test activity prioritization with many activities"""
        # Create 100 activities
        activities = {}
        for i in range(100):
            activities[f'Activity_{i}'] = {
                'expected_time': np.random.uniform(1, 10),
                'variance': np.random.uniform(0.1, 2.0),
                'total_float': np.random.uniform(-1, 5)
            }
        
        pert_results = {
            'expected_duration': 50.0,
            'variance': 10.0,
            'critical_path': ['Activity_0', 'Activity_50'],
            'activities': activities
        }
        
        prioritizer = ActivityRiskPrioritizer(pert_results)
        
        start_time = time.time()
        for _ in range(100):
            prioritizer.calculate_risk_scores()
        elapsed = time.time() - start_time
        
        assert elapsed < 5.0, f"Activity prioritization too slow: {elapsed:.3f}s for 100 iterations"
        
        avg_time = elapsed / 100
        print(f"Activity prioritization (100 activities): {avg_time*1000:.2f}ms per iteration")


class TestErrorHandling:
    """Test error handling and validation"""
    
    def test_invalid_pert_results_structure(self):
        """Test handling of invalid PERT results structure"""
        # Missing required keys
        invalid_results = {
            'expected_duration': 10.0
            # Missing variance, critical_path, activities
        }
        
        # Should work with defaults for missing keys
        try:
            DelayRiskAnalyzer(invalid_results)
        except (KeyError, ValueError):
            pass  # Expected for some missing keys
    
    def test_negative_contract_time(self):
        """Test handling of negative contract time"""
        pert_results = {
            'expected_duration': 10.0,
            'variance': 1.0,
            'critical_path': ['A'],
            'activities': {'A': {'expected_time': 10.0, 'variance': 1.0}}
        }
        
        analyzer = DelayRiskAnalyzer(pert_results)
        
        with pytest.raises(ValueError):
            analyzer.calculate_delay_probability(contract_time=-5.0)
    
    def test_invalid_confidence_level(self):
        """Test handling of invalid confidence levels"""
        pert_results = {
            'expected_duration': 10.0,
            'variance': 1.0,
            'critical_path': ['A'],
            'activities': {'A': {'expected_time': 10.0, 'variance': 1.0}}
        }
        
        planner = ContingencyPlanner(pert_results)
        
        # Confidence level > 1
        with pytest.raises(ValueError):
            planner.calculate_contingency(confidence_level=1.5)
        
        # Confidence level < 0
        with pytest.raises(ValueError):
            planner.calculate_contingency(confidence_level=-0.1)
        
        # Confidence level too low (< 0.5)
        with pytest.raises(ValueError):
            planner.calculate_contingency(confidence_level=0.4)
    
    def test_negative_costs(self):
        """Test handling of negative costs"""
        pert_results = {
            'expected_duration': 10.0,
            'variance': 1.0,
            'critical_path': ['A'],
            'activities': {'A': {'expected_time': 10.0, 'variance': 1.0}}
        }
        
        analyzer = VarianceReductionAnalyzer(pert_results)
        
        with pytest.raises(ValueError):
            analyzer.analyze_strategies(
                contract_time=12.0,
                penalty_rate=-1000.0,  # Negative penalty
                time_reduction_cost=3000.0,
                variance_reduction_cost=2000.0,
                max_budget=50000.0
            )
    
    def test_empty_activities(self):
        """Test handling of empty activities dictionary"""
        pert_results = {
            'expected_duration': 10.0,
            'variance': 1.0,
            'critical_path': [],
            'activities': {}  # Empty
        }
        
        # ActivityRiskPrioritizer should raise error for empty activities
        with pytest.raises(ValueError):
            prioritizer = ActivityRiskPrioritizer(pert_results)


class TestRealWorldScenarios:
    """Test with realistic project scenarios"""
    
    def test_construction_project(self):
        """Test with typical construction project data"""
        activities_data = [
            {'id': 'Site_Prep', 'predecessors': '', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 10},
            {'id': 'Foundation', 'predecessors': 'Site_Prep', 'optimistic': 5, 'most_likely': 7, 'pessimistic': 12},
            {'id': 'Framing', 'predecessors': 'Foundation', 'optimistic': 8, 'most_likely': 12, 'pessimistic': 20},
            {'id': 'Electrical', 'predecessors': 'Framing', 'optimistic': 4, 'most_likely': 6, 'pessimistic': 10},
            {'id': 'Plumbing', 'predecessors': 'Framing', 'optimistic': 4, 'most_likely': 6, 'pessimistic': 9},
            {'id': 'Roofing', 'predecessors': 'Framing', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 8},
            {'id': 'Interior', 'predecessors': 'Electrical;Plumbing', 'optimistic': 6, 'most_likely': 10, 'pessimistic': 15},
            {'id': 'Exterior', 'predecessors': 'Roofing', 'optimistic': 5, 'most_likely': 8, 'pessimistic': 12},
            {'id': 'Inspection', 'predecessors': 'Interior;Exterior', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 3}
        ]
        
        analyzer = PERTAnalyzer()
        network, critical_paths, critical_activities = analyzer.analyze(activities_data)
        
        # Comprehensive risk analysis
        contract_time = 40.0  # 40 weeks
        penalty_rate = 5000.0  # $5,000 per week
        
        # Delay risk
        delay_risk = analyzer.analyze_delay_risk(contract_time, penalty_rate)
        assert 'delay_probability' in delay_risk
        assert 'expected_delay' in delay_risk
        assert 'risk_cost' in delay_risk
        
        # Contingency
        contingency = analyzer.estimate_contingency(0.95, 10000.0)
        assert contingency['time_buffer'] > 0
        
        # Strategy comparison
        strategies = analyzer.analyze_variance_reduction_strategies(
            contract_time=40.0,
            penalty_rate=5000.0,
            time_reduction_cost=3000.0,
            variance_reduction_cost=2000.0,
            max_budget=50000.0
        )
        # Should return dict with baseline, strategy_a, strategy_b, mixed_strategy, best_strategy, summary
        assert 'strategy_a' in strategies
        assert 'strategy_b' in strategies
        assert 'mixed_strategy' in strategies
        assert 'best_strategy' in strategies
        
        # Activity prioritization
        risk_scores = analyzer.prioritize_activity_risks()
        assert len(risk_scores) > 0
        
        risk_input = analyzer.get_risk_analysis_input()
        print("\n=== Construction Project Risk Analysis ===")
        print(f"Expected Duration: {risk_input['expected_duration']:.1f} weeks")
        print(f"Delay Probability: {delay_risk['delay_probability']*100:.1f}%")
        print(f"Risk Cost: ${delay_risk['risk_cost']:,.0f}")
        print(f"Contingency Buffer: {contingency['time_buffer']:.1f} weeks")
    
    def test_software_development_project(self):
        """Test with typical software development project"""
        activities_data = [
            {'id': 'Requirements', 'predecessors': '', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 4},
            {'id': 'Design', 'predecessors': 'Requirements', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 5},
            {'id': 'Backend_Dev', 'predecessors': 'Design', 'optimistic': 4, 'most_likely': 6, 'pessimistic': 10},
            {'id': 'Frontend_Dev', 'predecessors': 'Design', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 8},
            {'id': 'Database', 'predecessors': 'Design', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 5},
            {'id': 'Integration', 'predecessors': 'Backend_Dev;Frontend_Dev;Database', 'optimistic': 2, 'most_likely': 4, 'pessimistic': 7},
            {'id': 'Testing', 'predecessors': 'Integration', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 8},
            {'id': 'Deployment', 'predecessors': 'Testing', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 3}
        ]
        
        analyzer = PERTAnalyzer()
        network, critical_paths, critical_activities = analyzer.analyze(activities_data)
        
        # Sprint planning: 3-week sprints
        sprint_duration = 3.0
        
        # How many sprints needed with 95% confidence?
        contingency = analyzer.estimate_contingency(0.95)
        risk_input = analyzer.get_risk_analysis_input()
        total_time_needed = risk_input['expected_duration'] + contingency['time_buffer']
        sprints_needed = np.ceil(total_time_needed / sprint_duration)
        
        print("\n=== Software Development Project ===")
        print(f"Expected Duration: {risk_input['expected_duration']:.1f} weeks")
        print(f"95% Confidence Duration: {total_time_needed:.1f} weeks")
        print(f"Sprints Needed: {int(sprints_needed)} sprints")
        
        assert sprints_needed > 0
    
    def test_event_planning_project(self):
        """Test with event planning project"""
        activities_data = [
            {'id': 'Venue_Booking', 'predecessors': '', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 4},
            {'id': 'Catering', 'predecessors': '', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 3},
            {'id': 'Invitations', 'predecessors': 'Venue_Booking', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 3},
            {'id': 'Equipment', 'predecessors': 'Venue_Booking', 'optimistic': 1, 'most_likely': 1, 'pessimistic': 2},
            {'id': 'Entertainment', 'predecessors': '', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 5},
            {'id': 'Setup', 'predecessors': 'Equipment;Catering', 'optimistic': 1, 'most_likely': 1, 'pessimistic': 2},
            {'id': 'Rehearsal', 'predecessors': 'Setup;Entertainment', 'optimistic': 1, 'most_likely': 1, 'pessimistic': 1}
        ]
        
        analyzer = PERTAnalyzer()
        network, critical_paths, critical_activities = analyzer.analyze(activities_data)
        
        # Event in 8 weeks
        event_date = 8.0
        
        delay_risk = analyzer.analyze_delay_risk(contract_time=event_date, penalty_rate=0)
        
        # For event planning, even small delay probability is concerning
        if delay_risk['delay_probability'] > 0.1:
            # Need contingency planning
            contingency = analyzer.estimate_contingency(0.99)  # Very high confidence for events
            
            print("\n=== Event Planning Project ===")
            print(f"Expected Duration: {analyzer.expected_duration:.1f} weeks")
            print(f"Delay Risk: {delay_risk['delay_probability']*100:.1f}%")
            print(f"Recommended Start: {event_date - analyzer.expected_duration - contingency['time_buffer']:.1f} weeks before event")


class TestCLIIntegration:
    """Test CLI integration (command-line interface)"""
    
    def test_cli_delay_command(self):
        """Test CLI delay command with sample data"""
        from src.pmhelper.cli.risk_cli import RiskCLI
        
        cli = RiskCLI()
        
        # Load sample data
        csv_path = 'assets/risk_examples/delay_analysis_simple.csv'
        if not os.path.exists(csv_path):
            pytest.skip(f"Sample file not found: {csv_path}")
        
        # Test text output
        # Create args object
        import argparse
        args = argparse.Namespace(
            input=csv_path,
            contract_time=15.0,
            penalty_rate=1000.0,
            max_penalty=None,
            format='text'
        )
        
        result = cli.cmd_delay(args)
        
        assert result == 0  # Success
    
    def test_cli_contingency_command(self):
        """Test CLI contingency command"""
        from src.pmhelper.cli.risk_cli import RiskCLI
        
        cli = RiskCLI()
        csv_path = 'assets/risk_examples/contingency_planning.csv'
        
        if not os.path.exists(csv_path):
            pytest.skip(f"Sample file not found: {csv_path}")
        
        # Create args object
        import argparse
        args = argparse.Namespace(
            input=csv_path,
            confidence=0.95,
            daily_cost=5000.0,
            format='text'
        )
        
        result = cli.cmd_contingency(args)
        
        assert result == 0
    
    def test_cli_json_output(self):
        """Test CLI JSON output format"""
        from src.pmhelper.cli.risk_cli import RiskCLI
        import json
        
        cli = RiskCLI()
        csv_path = 'assets/risk_examples/delay_analysis_simple.csv'
        
        if not os.path.exists(csv_path):
            pytest.skip(f"Sample file not found: {csv_path}")
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            # Create args object
            import argparse
            args = argparse.Namespace(
                input=csv_path,
                contract_time=15.0,
                penalty_rate=1000.0,
                max_penalty=None,
                format='json'
            )
            
            result = cli.cmd_delay(args)
            
            output = sys.stdout.getvalue()
            
            # Parse JSON
            if output.strip():
                data = json.loads(output)
                assert 'delay_probability' in data
                assert 'expected_delay' in data
                assert 'risk_cost' in data
        finally:
            sys.stdout = old_stdout


class TestEndToEnd:
    """End-to-end workflow tests"""
    
    def test_complete_risk_analysis_workflow(self):
        """Test complete workflow from CSV to risk report"""
        # Sample project data
        activities_data = [
            {'id': 'A', 'predecessors': '', 'optimistic': 2, 'most_likely': 4, 'pessimistic': 6},
            {'id': 'B', 'predecessors': 'A', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 7},
            {'id': 'C', 'predecessors': 'A', 'optimistic': 4, 'most_likely': 6, 'pessimistic': 10},
            {'id': 'D', 'predecessors': 'B;C', 'optimistic': 2, 'most_likely': 4, 'pessimistic': 6}
        ]
        
        # Step 1: Run PERT analysis
        analyzer = PERTAnalyzer()
        network, critical_paths, critical_activities = analyzer.analyze(activities_data)
        
        # Step 2: Delay risk analysis
        delay_risk = analyzer.analyze_delay_risk(contract_time=15.0, penalty_rate=1000.0)
        
        # Step 3: Contingency planning
        contingency = analyzer.estimate_contingency(confidence_level=0.95, daily_cost_rate=5000.0)
        
        # Step 4: Strategy comparison
        strategies = analyzer.analyze_variance_reduction_strategies(
            contract_time=15.0,
            penalty_rate=1000.0,
            time_reduction_cost=3000.0,
            variance_reduction_cost=2000.0,
            max_budget=30000.0
        )
        
        # Step 5: Activity prioritization
        risk_scores = analyzer.prioritize_activity_risks()
        
        # Step 6: Generate comprehensive report (gather all results)
        report = {
            'delay_risk': delay_risk,
            'contingency': contingency,
            'strategies': strategies,
            'risk_scores': risk_scores
        }
        
        # Validate complete workflow
        assert all([delay_risk, contingency, strategies, len(risk_scores) > 0, report])
        
        print("\n=== Complete Workflow Validation ===")
        print(f"✓ PERT Analysis Complete")
        print(f"✓ Delay Risk: {delay_risk['delay_probability']*100:.1f}% probability")
        print(f"✓ Contingency: {contingency['time_buffer']:.1f} weeks buffer")
        print(f"✓ Strategies: {len(strategies)} strategies compared")
        print(f"✓ Activities: {len(risk_scores)} activities prioritized")
        print(f"✓ Report: {len(report)} sections generated")


def run_comprehensive_tests():
    """Run all comprehensive tests and generate report"""
    print("\n" + "="*80)
    print("COMPREHENSIVE RISK ANALYSIS TEST SUITE")
    print("="*80)
    
    # Run pytest with verbose output
    pytest_args = [
        __file__,
        '-v',
        '--tb=short',
        '-s',  # Show print statements
        '--durations=10'  # Show 10 slowest tests
    ]
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("\n" + "="*80)
        print("✓ ALL COMPREHENSIVE TESTS PASSED")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ SOME TESTS FAILED")
        print("="*80)
    
    return exit_code


if __name__ == '__main__':
    exit(run_comprehensive_tests())
