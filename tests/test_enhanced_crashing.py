#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Project Crashing Features

This module provides comprehensive testing for both Enhanced Project Crashing
and Enhanced RCPS Project Crashing implementations.
"""

import unittest
import sys
import os
import time
import math
import networkx as nx
from typing import Dict, List, Any, Tuple

# Add the code directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

# Import the modules to test
try:
    from cpm_app import CPMAnalyzer
    from enhanced_project_crashing import (
        EnhancedProjectCrashing,
        EnhancedRCPSProjectCrashing,
        CrashingStrategy,
        OptimizationObjective,
        CrashingResult,
        ActivityCrashInfo,
        compare_crashing_results,
        generate_crashing_report
    )
    from enhanced_crashing_gui import EnhancedCrashingGUIManager
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_SUCCESSFUL = False


class TestEnhancedProjectCrashing(unittest.TestCase):
    """Test cases for Enhanced Project Crashing"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required modules not available")
        
        # Create sample project data
        self.sample_activities = [
            {
                'id': 'A',
                'activity': 'Design Phase',
                'duration': '5',
                'predecessors': '',
                'min_duration': '2',
                'crash_cost': '300',
                'resource_demand': '2',
                'normal_cost': '1000'
            },
            {
                'id': 'B',
                'activity': 'Requirements Analysis',
                'duration': '4',
                'predecessors': '',
                'min_duration': '2',
                'crash_cost': '500',
                'resource_demand': '1',
                'normal_cost': '800'
            },
            {
                'id': 'C',
                'activity': 'Architecture Design',
                'duration': '3',
                'predecessors': 'A,B',
                'min_duration': '1',
                'crash_cost': '400',
                'resource_demand': '3',
                'normal_cost': '1200'
            },
            {
                'id': 'D',
                'activity': 'Implementation',
                'duration': '8',
                'predecessors': 'C',
                'min_duration': '4',
                'crash_cost': '200',
                'resource_demand': '4',
                'normal_cost': '3200'
            },
            {
                'id': 'E',
                'activity': 'Testing',
                'duration': '6',
                'predecessors': 'D',
                'min_duration': '3',
                'crash_cost': '250',
                'resource_demand': '2',
                'normal_cost': '1500'
            },
            {
                'id': 'F',
                'activity': 'Deployment',
                'duration': '2',
                'predecessors': 'E',
                'min_duration': '1',
                'crash_cost': '600',
                'resource_demand': '1',
                'normal_cost': '400'
            }
        ]
        
        # Initialize analyzer and enhanced crashing
        self.analyzer = CPMAnalyzer()
        self.analyzer.analyze(self.sample_activities)
        self.enhanced_crashing = EnhancedProjectCrashing(self.analyzer)
        self.enhanced_rcps_crashing = EnhancedRCPSProjectCrashing(self.analyzer)
    
    def test_enhanced_crashing_initialization(self):
        """Test enhanced crashing engine initialization"""
        self.assertIsNotNone(self.enhanced_crashing)
        self.assertIsNotNone(self.enhanced_crashing.base_analyzer)
        self.assertIn(CrashingStrategy.LOWEST_COST, self.enhanced_crashing.strategies)
        self.assertIn(CrashingStrategy.BEST_EFFICIENCY, self.enhanced_crashing.strategies)
    
    def test_activity_analysis(self):
        """Test activity analysis functionality"""
        activities = self.enhanced_crashing._analyze_activities(self.analyzer.G)
        
        self.assertIsInstance(activities, list)
        self.assertGreater(len(activities), 0)
        
        # Check that all activities (except START/END) are analyzed
        activity_ids = [act.activity_id for act in activities]
        expected_ids = ['A', 'B', 'C', 'D', 'E', 'F']
        for expected_id in expected_ids:
            self.assertIn(expected_id, activity_ids)
        
        # Test activity properties
        for activity in activities:
            self.assertIsInstance(activity, ActivityCrashInfo)
            self.assertIsInstance(activity.current_duration, (int, float))
            self.assertIsInstance(activity.min_duration, (int, float))
            self.assertIsInstance(activity.crash_cost_per_unit, (int, float))
            self.assertGreaterEqual(activity.current_duration, activity.min_duration)
    
    def test_lowest_cost_strategy(self):
        """Test lowest cost crashing strategy"""
        result = self.enhanced_crashing.enhanced_crash_project(
            target_duration=20,
            strategy=CrashingStrategy.LOWEST_COST,
            max_iterations=50
        )
        
        self.assertIsInstance(result, CrashingResult)
        self.assertLess(result.final_duration, result.original_duration)
        self.assertGreater(result.total_crash_cost, 0)
        self.assertTrue(result.target_achieved or result.final_duration <= result.target_duration + 1)
        self.assertEqual(len(result.crash_log), result.iterations_used)
    
    def test_best_efficiency_strategy(self):
        """Test best efficiency crashing strategy"""
        result = self.enhanced_crashing.enhanced_crash_project(
            target_duration=22,
            strategy=CrashingStrategy.BEST_EFFICIENCY,
            max_iterations=50
        )
        
        self.assertIsInstance(result, CrashingResult)
        self.assertLess(result.final_duration, result.original_duration)
        self.assertGreater(result.efficiency_metrics['efficiency_score'], 0)
    
    def test_critical_path_strategy(self):
        """Test critical path priority strategy"""
        result = self.enhanced_crashing.enhanced_crash_project(
            target_duration=21,
            strategy=CrashingStrategy.CRITICAL_PATH_PRIORITY,
            max_iterations=50
        )
        
        self.assertIsInstance(result, CrashingResult)
        
        # Verify that critical activities were prioritized
        if result.critical_path_analysis:
            critical_activities = result.critical_path_analysis.get('critical_path', [])
            crashed_activities = [entry['activity'] for entry in result.crash_log]
            
            # At least some crashed activities should be on critical path
            critical_crashes = [act for act in crashed_activities if act in critical_activities]
            self.assertGreater(len(critical_crashes), 0)
    
    def test_budget_constraint(self):
        """Test budget constraint functionality"""
        max_budget = 1000
        result = self.enhanced_crashing.enhanced_crash_project(
            target_duration=15,  # Aggressive target
            strategy=CrashingStrategy.LOWEST_COST,
            max_budget=max_budget,
            max_iterations=100
        )
        
        self.assertLessEqual(result.total_crash_cost, max_budget)
        if not result.target_achieved:
            self.assertIn("budget", result.termination_reason.lower())
    
    def test_early_termination(self):
        """Test early termination when target is achieved"""
        result = self.enhanced_crashing.enhanced_crash_project(
            target_duration=25,  # Easy target
            strategy=CrashingStrategy.LOWEST_COST,
            early_termination=True,
            max_iterations=100
        )
        
        self.assertTrue(result.target_achieved)
        self.assertIn("target", result.termination_reason.lower())
    
    def test_step_size_variation(self):
        """Test different step sizes for crashing"""
        # Test with step size 0.5
        result1 = self.enhanced_crashing.enhanced_crash_project(
            target_duration=22,
            strategy=CrashingStrategy.LOWEST_COST,
            step_size=0.5,
            max_iterations=50
        )
        
        # Test with step size 2.0
        result2 = self.enhanced_crashing.enhanced_crash_project(
            target_duration=22,
            strategy=CrashingStrategy.LOWEST_COST,
            step_size=2.0,
            max_iterations=50
        )
        
        # Smaller step size should generally require more iterations
        # but achieve more precise results
        if result1.target_achieved and result2.target_achieved:
            self.assertGreaterEqual(result1.iterations_used, result2.iterations_used)
    
    def test_efficiency_metrics_calculation(self):
        """Test efficiency metrics calculation"""
        result = self.enhanced_crashing.enhanced_crash_project(
            target_duration=20,
            strategy=CrashingStrategy.LOWEST_COST,
            max_iterations=50
        )
        
        metrics = result.efficiency_metrics
        
        # Verify all expected metrics are present
        expected_metrics = [
            'duration_reduction', 'duration_reduction_percent',
            'cost_per_time_unit', 'total_crash_cost',
            'average_crash_cost_per_iteration', 'efficiency_score'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], (int, float))
        
        # Verify metric calculations
        expected_reduction = result.original_duration - result.final_duration
        self.assertAlmostEqual(metrics['duration_reduction'], expected_reduction, places=2)
        
        if expected_reduction > 0:
            expected_cost_per_unit = result.total_crash_cost / expected_reduction
            self.assertAlmostEqual(metrics['cost_per_time_unit'], expected_cost_per_unit, places=2)
    
    def test_crash_log_integrity(self):
        """Test crash log data integrity"""
        result = self.enhanced_crashing.enhanced_crash_project(
            target_duration=20,
            strategy=CrashingStrategy.LOWEST_COST,
            max_iterations=50
        )
        
        for i, entry in enumerate(result.crash_log, 1):
            # Check required fields
            required_fields = ['iteration', 'activity', 'strategy', 'old_duration', 
                             'new_duration', 'crash_cost', 'cumulative_cost']
            for field in required_fields:
                self.assertIn(field, entry)
            
            # Check field types and values
            self.assertEqual(entry['iteration'], i)
            self.assertIsInstance(entry['activity'], str)
            self.assertGreater(entry['old_duration'], entry['new_duration'])
            self.assertGreater(entry['crash_cost'], 0)
            self.assertGreaterEqual(entry['cumulative_cost'], entry['crash_cost'])


class TestEnhancedRCPSCrashing(unittest.TestCase):
    """Test cases for Enhanced RCPS Project Crashing"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required modules not available")
        
        # Use same sample data as regular crashing tests
        self.sample_activities = [
            {
                'id': 'A', 'activity': 'Design Phase', 'duration': '5', 'predecessors': '',
                'min_duration': '2', 'crash_cost': '300', 'resource_demand': '2', 'normal_cost': '1000'
            },
            {
                'id': 'B', 'activity': 'Requirements Analysis', 'duration': '4', 'predecessors': '',
                'min_duration': '2', 'crash_cost': '500', 'resource_demand': '1', 'normal_cost': '800'
            },
            {
                'id': 'C', 'activity': 'Architecture Design', 'duration': '3', 'predecessors': 'A,B',
                'min_duration': '1', 'crash_cost': '400', 'resource_demand': '3', 'normal_cost': '1200'
            },
            {
                'id': 'D', 'activity': 'Implementation', 'duration': '8', 'predecessors': 'C',
                'min_duration': '4', 'crash_cost': '200', 'resource_demand': '4', 'normal_cost': '3200'
            },
            {
                'id': 'E', 'activity': 'Testing', 'duration': '6', 'predecessors': 'D',
                'min_duration': '3', 'crash_cost': '250', 'resource_demand': '2', 'normal_cost': '1500'
            },
            {
                'id': 'F', 'activity': 'Deployment', 'duration': '2', 'predecessors': 'E',
                'min_duration': '1', 'crash_cost': '600', 'resource_demand': '1', 'normal_cost': '400'
            }
        ]
        
        self.analyzer = CPMAnalyzer()
        self.analyzer.analyze(self.sample_activities)
        self.enhanced_rcps_crashing = EnhancedRCPSProjectCrashing(self.analyzer)
    
    def test_rcps_crashing_initialization(self):
        """Test RCPS crashing engine initialization"""
        self.assertIsNotNone(self.enhanced_rcps_crashing)
        self.assertIsNotNone(self.enhanced_rcps_crashing.base_analyzer)
    
    def test_resource_aware_crashing(self):
        """Test resource-aware crashing strategy"""
        result = self.enhanced_rcps_crashing.enhanced_rcps_crash_project(
            target_duration=20,
            resource_limit=5,
            strategy=CrashingStrategy.RESOURCE_AWARE,
            max_iterations=50
        )
        
        self.assertIsInstance(result, CrashingResult)
        self.assertLess(result.final_duration, result.original_duration)
        self.assertIsNotNone(result.resource_utilization)
        
        # Check resource utilization doesn't exceed limit significantly
        if result.resource_utilization:
            max_util = result.resource_utilization.get('max_utilization', 0)
            resource_limit = result.resource_utilization.get('resource_limit', 0)
            # Allow some tolerance for resource scheduling
            self.assertLessEqual(max_util, resource_limit * 1.5)
    
    def test_different_priority_rules(self):
        """Test different RCPS priority rules"""
        priority_rules = ['minimum_slack', 'shortest_duration', 'earliest_start']
        results = []
        
        for rule in priority_rules:
            try:
                result = self.enhanced_rcps_crashing.enhanced_rcps_crash_project(
                    target_duration=22,
                    resource_limit=4,
                    priority_rule=rule,
                    max_iterations=30
                )
                results.append((rule, result))
            except Exception as e:
                print(f"Priority rule {rule} failed: {e}")
        
        # At least one priority rule should work
        self.assertGreater(len(results), 0)
        
        # All successful results should be valid
        for rule, result in results:
            self.assertIsInstance(result, CrashingResult)
            self.assertGreaterEqual(result.final_duration, 0)
    
    def test_resource_efficiency_weight(self):
        """Test resource efficiency weighting"""
        # Test with low resource weight (prioritize cost)
        result1 = self.enhanced_rcps_crashing.enhanced_rcps_crash_project(
            target_duration=21,
            resource_limit=5,
            resource_efficiency_weight=0.1,
            max_iterations=30
        )
        
        # Test with high resource weight (prioritize resource efficiency)
        result2 = self.enhanced_rcps_crashing.enhanced_rcps_crash_project(
            target_duration=21,
            resource_limit=5,
            resource_efficiency_weight=0.8,
            max_iterations=30
        )
        
        self.assertIsInstance(result1, CrashingResult)
        self.assertIsInstance(result2, CrashingResult)
        
        # Both should achieve reasonable results
        self.assertLess(result1.final_duration, result1.original_duration)
        self.assertLess(result2.final_duration, result2.original_duration)
    
    def test_resource_utilization_analysis(self):
        """Test resource utilization analysis"""
        result = self.enhanced_rcps_crashing.enhanced_rcps_crash_project(
            target_duration=20,
            resource_limit=6,
            max_iterations=40
        )
        
        self.assertIsNotNone(result.resource_utilization)
        
        utilization = result.resource_utilization
        expected_fields = [
            'max_time', 'total_periods', 'average_utilization',
            'max_utilization', 'resource_limit', 'utilization_percentage'
        ]
        
        for field in expected_fields:
            self.assertIn(field, utilization)
        
        # Check field validity
        self.assertGreaterEqual(utilization['average_utilization'], 0)
        self.assertGreaterEqual(utilization['max_utilization'], utilization['average_utilization'])
        self.assertEqual(utilization['resource_limit'], 6)
        self.assertGreaterEqual(utilization['utilization_percentage'], 0)
        self.assertLessEqual(utilization['utilization_percentage'], 200)  # Allow some over-utilization
    
    def test_rcps_vs_cpm_comparison(self):
        """Test comparison between RCPS and regular CPM crashing"""
        # Regular crashing
        enhanced_cpm = EnhancedProjectCrashing(self.analyzer)
        cpm_result = enhanced_cpm.enhanced_crash_project(
            target_duration=20,
            strategy=CrashingStrategy.LOWEST_COST,
            max_iterations=40
        )
        
        # RCPS crashing
        rcps_result = self.enhanced_rcps_crashing.enhanced_rcps_crash_project(
            target_duration=20,
            resource_limit=5,
            strategy=CrashingStrategy.RESOURCE_AWARE,
            max_iterations=40
        )
        
        # Both should produce valid results
        self.assertIsInstance(cmp_result, CrashingResult)
        self.assertIsInstance(rcps_result, CrashingResult)
        
        # RCPS should consider resource constraints
        self.assertIsNotNone(rcps_result.resource_utilization)
        self.assertIsNone(cmp_result.resource_utilization)
        
        # Results should be comparable in quality
        self.assertLess(abs(cmp_result.final_duration - rcps_result.final_duration), 5)


class TestCrashingResultDataClass(unittest.TestCase):
    """Test cases for CrashingResult data class"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required modules not available")
        
        # Create mock result data
        self.mock_graph = nx.DiGraph()
        self.mock_graph.add_node('A', duration=5, EF=5, LF=5, float=0)
        self.mock_graph.add_node('B', duration=3, EF=8, LF=8, float=0)
        
        self.crash_log = [
            {'iteration': 1, 'activity': 'A', 'crash_cost': 300, 'old_duration': 5, 'new_duration': 4},
            {'iteration': 2, 'activity': 'B', 'crash_cost': 200, 'old_duration': 3, 'new_duration': 2}
        ]
        
        self.efficiency_metrics = {
            'duration_reduction': 2.0,
            'cost_per_time_unit': 250.0,
            'efficiency_score': 0.004
        }
        
        self.result = CrashingResult(
            crashed_graph=self.mock_graph,
            original_duration=28.0,
            final_duration=26.0,
            target_duration=25.0,
            total_crash_cost=500.0,
            total_normal_cost=5000.0,
            crash_log=self.crash_log,
            efficiency_metrics=self.efficiency_metrics,
            termination_reason="Target achieved",
            iterations_used=2,
            computation_time=0.5
        )
    
    def test_property_calculations(self):
        """Test CrashingResult property calculations"""
        self.assertEqual(self.result.duration_reduction, 2.0)
        self.assertAlmostEqual(self.result.duration_reduction_percent, 7.14, places=1)
        self.assertEqual(self.result.cost_per_unit_reduction, 250.0)
        self.assertFalse(self.result.target_achieved)  # 26.0 > 25.0
    
    def test_target_achieved_property(self):
        """Test target achieved property"""
        # Create result where target is achieved
        achieved_result = CrashingResult(
            crashed_graph=self.mock_graph,
            original_duration=28.0,
            final_duration=24.0,  # Less than target of 25.0
            target_duration=25.0,
            total_crash_cost=500.0,
            total_normal_cost=5000.0,
            crash_log=self.crash_log,
            efficiency_metrics=self.efficiency_metrics,
            termination_reason="Target achieved",
            iterations_used=2,
            computation_time=0.5
        )
        
        self.assertTrue(achieved_result.target_achieved)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required modules not available")
        
        # Create sample results for testing
        self.results = []
        
        for i in range(3):
            mock_graph = nx.DiGraph()
            result = CrashingResult(
                crashed_graph=mock_graph,
                original_duration=30.0,
                final_duration=25.0 + i,
                target_duration=24.0,
                total_crash_cost=1000.0 + i * 200,
                total_normal_cost=5000.0,
                crash_log=[],
                efficiency_metrics={'efficiency_score': 0.01 - i * 0.002},
                termination_reason="Complete",
                iterations_used=10 + i,
                computation_time=1.0 + i * 0.5
            )
            self.results.append(result)
    
    def test_compare_crashing_results(self):
        """Test results comparison function"""
        comparison = compare_crashing_results(self.results)
        
        self.assertIsInstance(comparison, dict)
        
        # Check required fields
        required_fields = ['total_results', 'best_cost', 'best_duration', 
                          'best_efficiency', 'fastest_computation', 'summary_stats']
        for field in required_fields:
            self.assertIn(field, comparison)
        
        # Check values
        self.assertEqual(comparison['total_results'], 3)
        self.assertEqual(comparison['best_cost'].total_crash_cost, 1000.0)  # First result has lowest cost
        self.assertEqual(comparison['best_duration'].final_duration, 25.0)  # First result has shortest duration
        
        # Check summary statistics
        stats = comparison['summary_stats']
        self.assertAlmostEqual(stats['avg_crash_cost'], 1200.0, places=1)  # (1000+1200+1400)/3
        self.assertAlmostEqual(stats['avg_final_duration'], 26.0, places=1)  # (25+26+27)/3
    
    def test_generate_crashing_report(self):
        """Test report generation function"""
        result = self.results[0]
        report = generate_crashing_report(result)
        
        self.assertIsInstance(report, str)
        self.assertIn("ENHANCED PROJECT CRASHING ANALYSIS REPORT", report)
        self.assertIn("PROJECT OVERVIEW", report)
        self.assertIn("COST ANALYSIS", report)
        self.assertIn("EFFICIENCY METRICS", report)
        
        # Check that values are included
        self.assertIn("30.00", report)  # Original duration
        self.assertIn("25.00", report)  # Final duration
        self.assertIn("$1,000", report)  # Cost formatting


class TestPerformance(unittest.TestCase):
    """Performance tests for enhanced crashing algorithms"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required modules not available")
    
    def test_large_project_performance(self):
        """Test performance with larger project"""
        # Create a larger project (20 activities)
        large_activities = []
        for i in range(20):
            activity_id = f"ACT_{i:02d}"
            predecessors = []
            if i > 0:
                # Add 1-2 random predecessors from previous activities
                import random
                num_preds = min(2, i)
                pred_indices = random.sample(range(i), num_preds)
                predecessors = [f"ACT_{j:02d}" for j in pred_indices]
            
            large_activities.append({
                'id': activity_id,
                'activity': f'Activity {i}',
                'duration': str(3 + i % 5),  # Duration 3-7
                'predecessors': ','.join(predecessors),
                'min_duration': str(1 + i % 3),  # Min duration 1-3
                'crash_cost': str(100 + i * 50),  # Crash cost 100-1050
                'resource_demand': str(1 + i % 4),  # Resource demand 1-4
                'normal_cost': str(500 + i * 100)  # Normal cost 500-2400
            })
        
        # Test performance
        analyzer = CPMAnalyzer()
        analyzer.analyze(large_activities)
        enhanced_crashing = EnhancedProjectCrashing(analyzer)
        
        start_time = time.time()
        result = enhanced_crashing.enhanced_crash_project(
            target_duration=25,
            strategy=CrashingStrategy.LOWEST_COST,
            max_iterations=100
        )
        end_time = time.time()
        
        # Performance assertions
        self.assertLess(end_time - start_time, 10.0)  # Should complete within 10 seconds
        self.assertIsInstance(result, CrashingResult)
        self.assertLess(result.final_duration, result.original_duration)
    
    def test_computation_time_tracking(self):
        """Test that computation time is tracked accurately"""
        # Simple project for fast execution
        simple_activities = [
            {'id': 'A', 'activity': 'Task A', 'duration': '5', 'predecessors': '',
             'min_duration': '2', 'crash_cost': '100', 'resource_demand': '1', 'normal_cost': '500'},
            {'id': 'B', 'activity': 'Task B', 'duration': '3', 'predecessors': 'A',
             'min_duration': '1', 'crash_cost': '200', 'resource_demand': '1', 'normal_cost': '300'}
        ]
        
        analyzer = CPMAnalyzer()
        analyzer.analyze(simple_activities)
        enhanced_crashing = EnhancedProjectCrashing(analyzer)
        
        result = enhanced_crashing.enhanced_crash_project(
            target_duration=6,
            strategy=CrashingStrategy.LOWEST_COST,
            max_iterations=20
        )
        
        # Computation time should be reasonable and positive
        self.assertGreater(result.computation_time, 0)
        self.assertLess(result.computation_time, 5.0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete enhanced crashing system"""
    
    def setUp(self):
        """Set up test environment"""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Required modules not available")
    
    def test_full_workflow_cpm_crashing(self):
        """Test complete workflow for CPM crashing"""
        # Sample data
        activities = [
            {'id': 'A', 'activity': 'Design', 'duration': '4', 'predecessors': '',
             'min_duration': '2', 'crash_cost': '200', 'resource_demand': '1', 'normal_cost': '800'},
            {'id': 'B', 'activity': 'Build', 'duration': '6', 'predecessors': 'A',
             'min_duration': '3', 'crash_cost': '150', 'resource_demand': '2', 'normal_cost': '900'},
            {'id': 'C', 'activity': 'Test', 'duration': '3', 'predecessors': 'B',
             'min_duration': '2', 'crash_cost': '300', 'resource_demand': '1', 'normal_cost': '600'}
        ]
        
        # Step 1: Initialize analyzer
        analyzer = CPMAnalyzer()
        analyzer.analyze(activities)
        
        # Step 2: Create enhanced crashing engine
        enhanced_engine = EnhancedProjectCrashing(analyzer)
        
        # Step 3: Run crashing with different strategies
        strategies = [CrashingStrategy.LOWEST_COST, CrashingStrategy.BEST_EFFICIENCY]
        results = []
        
        for strategy in strategies:
            result = enhanced_engine.enhanced_crash_project(
                target_duration=10,
                strategy=strategy,
                max_iterations=20
            )
            results.append(result)
        
        # Step 4: Compare results
        comparison = compare_crashing_results(results)
        
        # Step 5: Generate reports
        for result in results:
            report = generate_crashing_report(result)
            self.assertIsInstance(report, str)
            self.assertGreater(len(report), 100)
        
        # Validate integration
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, CrashingResult)
            self.assertGreater(len(result.crash_log), 0)
    
    def test_full_workflow_rcps_crashing(self):
        """Test complete workflow for RCPS crashing"""
        # Sample data with resource demands
        activities = [
            {'id': 'A', 'activity': 'Design', 'duration': '4', 'predecessors': '',
             'min_duration': '2', 'crash_cost': '200', 'resource_demand': '2', 'normal_cost': '800'},
            {'id': 'B', 'activity': 'Build', 'duration': '6', 'predecessors': 'A',
             'min_duration': '3', 'crash_cost': '150', 'resource_demand': '3', 'normal_cost': '900'},
            {'id': 'C', 'activity': 'Test', 'duration': '3', 'predecessors': 'B',
             'min_duration': '2', 'crash_cost': '300', 'resource_demand': '1', 'normal_cost': '600'}
        ]
        
        # Initialize
        analyzer = CPMAnalyzer()
        analyzer.analyze(activities)
        enhanced_rcps_engine = EnhancedRCPSProjectCrashing(analyzer)
        
        # Run RCPS crashing
        result = enhanced_rcps_engine.enhanced_rcps_crash_project(
            target_duration=10,
            resource_limit=4,
            priority_rule='minimum_slack',
            strategy=CrashingStrategy.RESOURCE_AWARE,
            max_iterations=20
        )
        
        # Validate RCPS-specific features
        self.assertIsInstance(result, CrashingResult)
        self.assertIsNotNone(result.resource_utilization)
        self.assertIn('average_utilization', result.resource_utilization)
        self.assertIn('max_utilization', result.resource_utilization)
        
        # Generate report
        report = generate_crashing_report(result)
        self.assertIn("RESOURCE UTILIZATION", report)


def run_performance_benchmarks():
    """Run performance benchmarks for enhanced crashing"""
    if not IMPORTS_SUCCESSFUL:
        print("Cannot run benchmarks - imports failed")
        return
    
    print("\n" + "="*60)
    print("ENHANCED PROJECT CRASHING PERFORMANCE BENCHMARKS")
    print("="*60)
    
    # Test different project sizes
    project_sizes = [5, 10, 20, 50]
    
    for size in project_sizes:
        print(f"\nTesting project size: {size} activities")
        
        # Generate project data
        activities = []
        for i in range(size):
            predecessors = []
            if i > 0:
                # Add 1-2 predecessors from previous activities
                import random
                num_preds = min(2, max(1, i // 3))
                if num_preds > 0:
                    pred_indices = random.sample(range(i), min(num_preds, i))
                    predecessors = [f"ACT_{j:02d}" for j in pred_indices]
            
            activities.append({
                'id': f"ACT_{i:02d}",
                'activity': f'Activity {i}',
                'duration': str(3 + i % 5),
                'predecessors': ','.join(predecessors),
                'min_duration': str(1 + i % 3),
                'crash_cost': str(100 + i * 25),
                'resource_demand': str(1 + i % 4),
                'normal_cost': str(500 + i * 50)
            })
        
        try:
            # Initialize
            analyzer = CPMAnalyzer()
            analyzer.analyze(activities)
            enhanced_engine = EnhancedProjectCrashing(analyzer)
            
            # Benchmark regular crashing
            start_time = time.time()
            result = enhanced_engine.enhanced_crash_project(
                target_duration=max(10, size),
                strategy=CrashingStrategy.LOWEST_COST,
                max_iterations=min(100, size * 5)
            )
            regular_time = time.time() - start_time
            
            # Benchmark RCPS crashing
            enhanced_rcps_engine = EnhancedRCPSProjectCrashing(analyzer)
            start_time = time.time()
            rcps_result = enhanced_rcps_engine.enhanced_rcps_crash_project(
                target_duration=max(10, size),
                resource_limit=max(3, size // 4),
                max_iterations=min(100, size * 3)
            )
            rcps_time = time.time() - start_time
            
            print(f"  Regular Crashing: {regular_time:.3f}s ({result.iterations_used} iterations)")
            print(f"  RCPS Crashing: {rcps_time:.3f}s ({rcps_result.iterations_used} iterations)")
            print(f"  Duration reduction: {result.duration_reduction:.1f} / {rcps_result.duration_reduction:.1f}")
            
        except Exception as e:
            print(f"  Error with size {size}: {e}")


def main():
    """Main test runner"""
    print("Enhanced Project Crashing Test Suite")
    print("="*50)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ CRITICAL: Required modules could not be imported")
        print("Make sure all dependencies are available and the code is in the correct location")
        return
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestEnhancedProjectCrashing,
        TestEnhancedRCPSCrashing,
        TestCrashingResultDataClass,
        TestUtilityFunctions,
        TestPerformance,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    # Run performance benchmarks if tests passed
    if not result.failures and not result.errors:
        print("\n✅ All tests passed! Running performance benchmarks...")
        run_performance_benchmarks()
    else:
        print("\n❌ Some tests failed. Fix issues before running benchmarks.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
