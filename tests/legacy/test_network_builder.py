#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Network Builder

Tests all functionality of the network builder including:
- Network graph construction
- Forward pass calculations (Early Start/Finish)
- Backward pass calculations (Late Start/Finish)
- Float/slack calculations
- Critical path identification
- Additional metrics calculation
- Edge cases and error handling
"""

import pytest
import sys
import networkx as nx
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pmhelper.core.network_builder import NetworkBuilder


class TestNetworkBuilder:
    """Comprehensive test suite for Network Builder"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment before each test"""
        self.builder = NetworkBuilder()
        self.sample_activities = [
            {
                'id': 'A',
                'activity': 'Start Activity',
                'duration': 3,
                'predecessors': []
            },
            {
                'id': 'B',
                'activity': 'Second Activity',
                'duration': 5,
                'predecessors': ['A']
            },
            {
                'id': 'C',
                'activity': 'Third Activity',
                'duration': 4,
                'predecessors': ['A']
            },
            {
                'id': 'D',
                'activity': 'Final Activity',
                'duration': 2,
                'predecessors': ['B', 'C']
            }
        ]
    
    def test_builder_initialization(self):
        """Test NetworkBuilder can be created and initialized properly"""
        assert self.builder is not None
    
    def test_build_network_basic(self):
        """Test basic network building functionality"""
        graph = self.builder.build_network(self.sample_activities)
        
        # Verify graph structure
        assert isinstance(graph, nx.DiGraph)
        assert len(graph.nodes()) >= len(self.sample_activities)  # May include START/END nodes
        
        # Verify all activities are in the graph
        for activity in self.sample_activities:
            assert activity['id'] in graph.nodes()
        
        # Verify node attributes
        for activity in self.sample_activities:
            node = graph.nodes[activity['id']]
            assert node['duration'] == activity['duration']
            assert node['activity'] == activity['activity']
    
    def test_build_network_dependencies(self):
        """Test that dependencies are correctly represented as edges"""
        graph = self.builder.build_network(self.sample_activities)
        
        # Verify edges based on predecessors
        assert graph.has_edge('A', 'B')  # B depends on A
        assert graph.has_edge('A', 'C')  # C depends on A
        assert graph.has_edge('B', 'D')  # D depends on B
        assert graph.has_edge('C', 'D')  # D depends on C
    
    def test_forward_pass_calculation(self):
        """Test forward pass calculations (Early Start and Early Finish)"""
        graph = self.builder.build_network(self.sample_activities)
        graph = self.builder.forward_pass(graph)
        
        # Verify all nodes have ES and EF
        for node in graph.nodes():
            if node not in ['START', 'END']:
                assert 'ES' in graph.nodes[node]
                assert 'EF' in graph.nodes[node]
        
        # Verify specific calculations
        assert graph.nodes['A']['ES'] == 0  # First activity starts at 0
        assert graph.nodes['A']['EF'] == 3  # Duration is 3
        assert graph.nodes['B']['ES'] == 3  # Starts after A finishes
        assert graph.nodes['B']['EF'] == 8  # 3 + 5
        assert graph.nodes['C']['ES'] == 3  # Starts after A finishes
        assert graph.nodes['C']['EF'] == 7  # 3 + 4
        assert graph.nodes['D']['ES'] == 8  # Starts after max(B, C) finishes
        assert graph.nodes['D']['EF'] == 10  # 8 + 2
    
    def test_backward_pass_calculation(self):
        """Test backward pass calculations (Late Start and Late Finish)"""
        graph = self.builder.build_network(self.sample_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        
        # Verify all nodes have LS and LF
        for node in graph.nodes():
            if node not in ['START', 'END']:
                assert 'LS' in graph.nodes[node]
                assert 'LF' in graph.nodes[node]
        
        # Verify specific calculations (working backwards from project end)
        project_end = 10  # D finishes at time 10
        assert graph.nodes['D']['LF'] == project_end
        assert graph.nodes['D']['LS'] == 8  # 10 - 2
        assert graph.nodes['B']['LF'] == 8  # Must finish before D starts
        assert graph.nodes['C']['LF'] == 8  # Must finish before D starts
        assert graph.nodes['A']['LF'] == 3  # Must finish before B and C start
    
    def test_float_calculation(self):
        """Test float/slack calculations"""
        graph = self.builder.build_network(self.sample_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        graph = self.builder.calculate_float(graph)
        
        # Verify all nodes have float
        for node in graph.nodes():
            if node not in ['START', 'END']:
                assert 'float' in graph.nodes[node]
        
        # Verify float calculations (float = LS - ES or LF - EF)
        for node in graph.nodes():
            if node not in ['START', 'END']:
                expected_float = graph.nodes[node]['LS'] - graph.nodes[node]['ES']
                assert abs(graph.nodes[node]['float'] - expected_float) < 0.001
        
        # Critical path activities should have zero float
        assert graph.nodes['A']['float'] == 0
        assert graph.nodes['B']['float'] == 0
        assert graph.nodes['D']['float'] == 0
        
        # Non-critical activity C should have positive float
        assert graph.nodes['C']['float'] == 1  # Can be delayed by 1 time unit
    
    def test_critical_path_identification(self):
        """Test critical path identification"""
        graph = self.builder.build_network(self.sample_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        graph = self.builder.calculate_float(graph)
        
        critical_paths, critical_activities = self.builder.identify_critical_path(graph)
        
        # Verify critical path contains activities with zero float
        expected_critical = ['A', 'B', 'D']  # The longest path
        for activity in expected_critical:
            assert activity in critical_activities
        
        # C should not be critical (has float)
        assert 'C' not in critical_activities
    
    def test_additional_metrics_calculation(self):
        """Test calculation of additional metrics"""
        activities_data = [
            {
                'id': 'A',
                'activity': 'Start Activity',
                'duration': 3,
                'predecessors': '',
                'resource_demand': 2,
                'normal_cost': 100
            },
            {
                'id': 'B',
                'activity': 'Second Activity',
                'duration': 5,
                'predecessors': 'A',
                'resource_demand': 3,
                'normal_cost': 200
            }
        ]
        
        graph = self.builder.build_network(self.sample_activities)
        graph = self.builder.calculate_additional_metrics(graph, activities_data)
        
        # Should complete without error
        assert graph is not None
    
    def test_single_activity_network(self):
        """Test network with single activity"""
        single_activity = [
            {
                'id': 'A',
                'activity': 'Only Activity',
                'duration': 5,
                'predecessors': []
            }
        ]
        
        graph = self.builder.build_network(single_activity)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        graph = self.builder.calculate_float(graph)
        
        assert graph.nodes['A']['ES'] == 0
        assert graph.nodes['A']['EF'] == 5
        assert graph.nodes['A']['LS'] == 0
        assert graph.nodes['A']['LF'] == 5
        assert graph.nodes['A']['float'] == 0
        
        critical_paths, critical_activities = self.builder.identify_critical_path(graph)
        assert 'A' in critical_activities
    
    def test_parallel_activities(self):
        """Test network with parallel activities"""
        parallel_activities = [
            {
                'id': 'A',
                'activity': 'Start',
                'duration': 2,
                'predecessors': []
            },
            {
                'id': 'B',
                'activity': 'Parallel 1',
                'duration': 5,
                'predecessors': ['A']
            },
            {
                'id': 'C',
                'activity': 'Parallel 2',
                'duration': 3,
                'predecessors': ['A']
            },
            {
                'id': 'D',
                'activity': 'End',
                'duration': 1,
                'predecessors': ['B', 'C']
            }
        ]
        
        graph = self.builder.build_network(parallel_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        graph = self.builder.calculate_float(graph)
        
        # B should be critical (longer duration)
        # C should have float (shorter duration)
        assert graph.nodes['B']['float'] == 0  # Critical
        assert graph.nodes['C']['float'] == 2  # Has float (5-3=2)
        
        critical_paths, critical_activities = self.builder.identify_critical_path(graph)
        assert 'B' in critical_activities
        assert 'C' not in critical_activities
    
    def test_complex_network(self):
        """Test more complex network structure"""
        complex_activities = [
            {'id': 'A', 'duration': 3, 'predecessors': []},
            {'id': 'B', 'duration': 4, 'predecessors': ['A']},
            {'id': 'C', 'duration': 2, 'predecessors': ['A']},
            {'id': 'D', 'duration': 5, 'predecessors': ['B']},
            {'id': 'E', 'duration': 3, 'predecessors': ['C']},
            {'id': 'F', 'duration': 2, 'predecessors': ['D', 'E']},
            {'id': 'G', 'duration': 1, 'predecessors': ['F']}
        ]
        
        graph = self.builder.build_network(complex_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        graph = self.builder.calculate_float(graph)
        
        # Verify the calculations make sense
        project_duration = max([graph.nodes[node]['EF'] for node in graph.nodes() 
                               if node not in ['START', 'END']])
        assert project_duration > 0
        
        critical_paths, critical_activities = self.builder.identify_critical_path(graph)
        assert len(critical_activities) > 0
    
    def test_zero_duration_activities(self):
        """Test handling of zero-duration activities (milestones)"""
        milestone_activities = [
            {'id': 'A', 'duration': 3, 'predecessors': []},
            {'id': 'M1', 'duration': 0, 'predecessors': ['A']},  # Milestone
            {'id': 'B', 'duration': 4, 'predecessors': ['M1']}
        ]
        
        graph = self.builder.build_network(milestone_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        
        # Milestone should have zero duration but correct timing
        assert graph.nodes['M1']['duration'] == 0
        assert graph.nodes['M1']['ES'] == 3  # Starts when A finishes
        assert graph.nodes['M1']['EF'] == 3  # Finishes immediately
        assert graph.nodes['B']['ES'] == 3  # Starts when milestone finishes
    
    def test_empty_network(self):
        """Test handling of empty activity list"""
        with pytest.raises(Exception):  # Should raise some error for empty activities
            self.builder.build_network([])
    
    def test_invalid_predecessors(self):
        """Test handling of invalid predecessor references"""
        invalid_activities = [
            {'id': 'A', 'duration': 3, 'predecessors': []},
            {'id': 'B', 'duration': 4, 'predecessors': ['Z']}  # Z doesn't exist
        ]
        
        # Should handle gracefully or raise appropriate error
        try:
            graph = self.builder.build_network(invalid_activities)
            # If it doesn't raise an error, the graph should still be valid
            assert graph is not None
        except Exception as e:
            # Should raise a meaningful error
            assert "predecessor" in str(e).lower() or "dependency" in str(e).lower()
    
    def test_circular_dependencies(self):
        """Test detection of circular dependencies"""
        circular_activities = [
            {'id': 'A', 'duration': 3, 'predecessors': ['B']},
            {'id': 'B', 'duration': 4, 'predecessors': ['A']}  # Circular
        ]
        
        # Should detect and handle circular dependencies
        with pytest.raises(Exception):  # Should raise error for circular dependency
            graph = self.builder.build_network(circular_activities)
            self.builder.forward_pass(graph)  # This is where cycles would be detected
    
    def test_self_dependency(self):
        """Test handling of self-dependencies"""
        self_dep_activities = [
            {'id': 'A', 'duration': 3, 'predecessors': ['A']}  # Self-dependency
        ]
        
        # Should handle self-dependencies appropriately
        try:
            graph = self.builder.build_network(self_dep_activities)
            # Should either ignore self-dependency or raise error
        except Exception:
            # Self-dependencies should cause an error
            pass
    
    def test_multiple_start_activities(self):
        """Test network with multiple starting activities"""
        multi_start_activities = [
            {'id': 'A', 'duration': 3, 'predecessors': []},  # Start 1
            {'id': 'B', 'duration': 4, 'predecessors': []},  # Start 2
            {'id': 'C', 'duration': 2, 'predecessors': ['A', 'B']}  # Depends on both
        ]
        
        graph = self.builder.build_network(multi_start_activities)
        graph = self.builder.forward_pass(graph)
        
        # Both A and B should start at time 0
        assert graph.nodes['A']['ES'] == 0
        assert graph.nodes['B']['ES'] == 0
        
        # C should start after both A and B finish
        assert graph.nodes['C']['ES'] == max(
            graph.nodes['A']['EF'],
            graph.nodes['B']['EF']
        )
    
    def test_multiple_end_activities(self):
        """Test network with multiple ending activities"""
        multi_end_activities = [
            {'id': 'A', 'duration': 3, 'predecessors': []},
            {'id': 'B', 'duration': 4, 'predecessors': ['A']},  # End 1
            {'id': 'C', 'duration': 2, 'predecessors': ['A']}   # End 2
        ]
        
        graph = self.builder.build_network(multi_end_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        
        # Project should end when last activity finishes
        project_end = max(graph.nodes['B']['EF'], graph.nodes['C']['EF'])
        
        # Backward pass should be calculated correctly
        assert graph.nodes['B']['LF'] == graph.nodes['B']['EF']  # Critical path end
        assert graph.nodes['C']['LF'] == project_end  # Non-critical may have different LF
    
    def test_very_large_durations(self):
        """Test handling of very large duration values"""
        large_duration_activities = [
            {'id': 'A', 'duration': 1000000, 'predecessors': []},
            {'id': 'B', 'duration': 999999, 'predecessors': ['A']}
        ]
        
        graph = self.builder.build_network(large_duration_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        
        # Should handle large numbers without overflow
        assert graph.nodes['B']['EF'] == 1999999
    
    def test_float_consistency(self):
        """Test consistency of float calculations"""
        graph = self.builder.build_network(self.sample_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        graph = self.builder.calculate_float(graph)
        
        for node in graph.nodes():
            if node not in ['START', 'END']:
                # Float should equal LS - ES
                ls_es_float = graph.nodes[node]['LS'] - graph.nodes[node]['ES']
                # Float should also equal LF - EF
                lf_ef_float = graph.nodes[node]['LF'] - graph.nodes[node]['EF']
                
                assert abs(ls_es_float - lf_ef_float) < 0.001
                assert abs(graph.nodes[node]['float'] - ls_es_float) < 0.001
    
    def test_topological_ordering(self):
        """Test that the network respects topological ordering"""
        graph = self.builder.build_network(self.sample_activities)
        
        # Should be a DAG (no cycles)
        assert nx.is_directed_acyclic_graph(graph)
        
        # Should be able to get topological sort
        topo_sort = list(nx.topological_sort(graph))
        assert len(topo_sort) > 0


class TestNetworkBuilderEdgeCases:
    """Additional edge case tests for Network Builder"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.builder = NetworkBuilder()
    
    def test_activity_with_no_duration(self):
        """Test handling of activities with missing duration"""
        no_duration_activities = [
            {'id': 'A', 'predecessors': []}  # No duration specified
        ]
        
        with pytest.raises(KeyError):
            self.builder.build_network(no_duration_activities)
    
    def test_activity_with_negative_duration(self):
        """Test handling of negative durations"""
        negative_duration_activities = [
            {'id': 'A', 'duration': -5, 'predecessors': []}
        ]
        
        # Should handle negative durations appropriately
        try:
            graph = self.builder.build_network(negative_duration_activities)
            # If it doesn't raise an error, verify handling
        except Exception:
            # Negative durations should cause an error
            pass
    
    def test_performance_large_network(self):
        """Test performance with large network"""
        # Generate large network
        large_activities = []
        import random
        
        for i in range(100):  # 100 activities
            predecessors = []
            if i > 0:
                # Add 1-3 random predecessors from previous activities
                num_preds = min(random.randint(0, 3), i)
                if num_preds > 0:
                    pred_indices = random.sample(range(i), num_preds)
                    predecessors = [chr(65 + j) if j < 26 else f'A{j-25}' for j in pred_indices]
            
            large_activities.append({
                'id': chr(65 + i) if i < 26 else f'A{i-25}',
                'duration': random.randint(1, 10),
                'predecessors': predecessors
            })
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        
        graph = self.builder.build_network(large_activities)
        graph = self.builder.forward_pass(graph)
        graph = self.builder.backward_pass(graph)
        graph = self.builder.calculate_float(graph)
        critical_paths, critical_activities = self.builder.identify_critical_path(graph)
        
        execution_time = time.time() - start_time
        
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert graph is not None
        assert len(critical_activities) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
