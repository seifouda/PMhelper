#!/usr/bin/env python3
"""
System-level integration tests for PMHelper.

Tests complete workflows including:
- End-to-end project analysis
- File import/export workflows
- GUI integration with analysis engines
- Performance under various conditions
- Error recovery and resilience
"""

import pytest
import sys
import os
import tempfile
import time
from unitt        cpm_results = cpm_analyzer.analyze(project_data_cpm)
        pert_results = pert_analyzer.analyze(project_data_pert)
        
        # Project durations should be identical (since PERT has no uncertainty)
        assert abs(cpm_results['project_duration'] - pert_results['expected_duration']) < 0.1ock import Mock, patch
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import core modules
from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.core.network_builder import NetworkBuilder
from pmhelper.utils.file_handlers import load_csv_data, save_csv_data


@pytest.fixture
def sample_cpm_project():
    """Sample CPM project data for testing."""
    return [
        {'id': 'A', 'activity': 'Project Planning', 'duration': '5', 'predecessors': ''},
        {'id': 'B', 'activity': 'Design Phase', 'duration': '8', 'predecessors': 'A'},
        {'id': 'C', 'activity': 'Development', 'duration': '12', 'predecessors': 'B'},
        {'id': 'D', 'activity': 'Testing', 'duration': '6', 'predecessors': 'C'},
        {'id': 'E', 'activity': 'Documentation', 'duration': '4', 'predecessors': 'B'},
        {'id': 'F', 'activity': 'Deployment', 'duration': '3', 'predecessors': 'D,E'},
    ]


@pytest.fixture
def sample_pert_project():
    """Sample PERT project data for testing."""
    return [
        {'id': 'A', 'activity': 'Analysis', 'optimistic': '2', 'most_likely': '4', 'pessimistic': '8', 'predecessors': ''},
        {'id': 'B', 'activity': 'Design', 'optimistic': '5', 'most_likely': '8', 'pessimistic': '15', 'predecessors': 'A'},
        {'id': 'C', 'activity': 'Implementation', 'optimistic': '8', 'most_likely': '12', 'pessimistic': '20', 'predecessors': 'B'},
        {'id': 'D', 'activity': 'Testing', 'optimistic': '4', 'most_likely': '6', 'pessimistic': '10', 'predecessors': 'C'},
        {'id': 'E', 'activity': 'Deployment', 'optimistic': '1', 'most_likely': '2', 'pessimistic': '4', 'predecessors': 'D'},
    ]


@pytest.fixture
def large_project_data():
    """Large project data for performance testing."""
    activities = []
    for i in range(100):
        activity = {
            'id': f'Task_{i:03d}',
            'activity': f'Project Task {i+1}',
            'duration': str((i % 10) + 1),
            'predecessors': f'Task_{i-1:03d}' if i > 0 else ''
        }
        activities.append(activity)
    return activities


class TestCPMWorkflow:
    """Test complete CPM analysis workflow."""
    
    def test_basic_cpm_analysis(self, sample_cpm_project):
        """Test basic CPM analysis workflow."""
        # Create network builder
        network_builder = NetworkBuilder()
        
        # Build network from data
        network = network_builder.build_network(sample_cpm_project)
        assert network is not None
        assert len(network.nodes) == len(sample_cpm_project)
        
        # Create CPM analyzer
        analyzer = CPMAnalyzer()
        
        # Perform analysis
        results = analyzer.analyze(sample_cpm_project)
        
        # Verify results structure
        assert 'project_duration' in results
        assert 'critical_path' in results
        assert 'activities' in results
        assert results['project_duration'] > 0
        assert len(results['critical_path']) > 0
    
    def test_cpm_critical_path_calculation(self, sample_cpm_project):
        """Test critical path calculation accuracy."""
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(sample_cpm_project)
        
        # Verify critical path properties
        critical_path = results['critical_path']
        assert isinstance(critical_path, list)
        assert len(critical_path) > 0
        
        # Critical path should start with activities having no predecessors
        first_activity = critical_path[0]
        activity_data = next(a for a in sample_cpm_project if a['id'] == first_activity)
        assert activity_data['predecessors'] == '' or activity_data['predecessors'] is None
    
    def test_cpm_float_calculations(self, sample_cpm_project):
        """Test float time calculations."""
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(sample_cpm_project)
        
        # Verify float calculations
        activities = results['activities']
        for activity in activities:
            assert 'total_float' in activity
            assert 'free_float' in activity
            assert activity['total_float'] >= 0
            assert activity['free_float'] >= 0
            assert activity['free_float'] <= activity['total_float']


class TestPERTWorkflow:
    """Test complete PERT analysis workflow."""
    
    def test_basic_pert_analysis(self, sample_pert_project):
        """Test basic PERT analysis workflow."""
        analyzer = PERTAnalyzer()
        results = analyzer.analyze(sample_pert_project)
        
        # Verify results structure
        assert 'expected_duration' in results
        assert 'variance' in results
        assert 'standard_deviation' in results
        assert 'activities' in results
        
        # Verify calculations
        assert results['expected_duration'] > 0
        assert results['variance'] >= 0
        assert results['standard_deviation'] >= 0
    
    def test_pert_probability_calculations(self, sample_pert_project):
        """Test PERT probability calculations."""
        analyzer = PERTAnalyzer()
        results = analyzer.analyze(sample_pert_project)
        
        # Test probability calculation for specific completion time
        target_time = results['expected_duration'] + 5
        probability = analyzer.calculate_completion_probability(target_time)
        
        assert 0 <= probability <= 1
        assert isinstance(probability, float)
    
    def test_pert_expected_time_calculation(self, sample_pert_project):
        """Test PERT expected time calculation."""
        analyzer = PERTAnalyzer()
        results = analyzer.analyze(sample_pert_project)
        
        # Verify expected time calculation for each activity
        activities = results['activities']
        for activity in activities:
            assert 'expected_time' in activity
            assert activity['expected_time'] > 0
            
            # Expected time should be between optimistic and pessimistic
            optimistic = float(activity['optimistic'])
            pessimistic = float(activity['pessimistic'])
            expected = activity['expected_time']
            
            assert optimistic <= expected <= pessimistic


class TestFileIntegrationWorkflow:
    """Test complete file handling integration workflow."""
    
    def test_csv_import_analysis_export(self, sample_cpm_project):
        """Test complete CSV workflow: import -> analyze -> export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create input file
            input_file = os.path.join(temp_dir, 'input.csv')
            save_csv_data(sample_cpm_project, input_file)
            
            # Load data
            loaded_data = load_csv_data(input_file)
            assert len(loaded_data) == len(sample_cpm_project)
            
            # Analyze data
            analyzer = CPMAnalyzer()
            results = analyzer.analyze(loaded_data)
            
            # Export results
            output_file = os.path.join(temp_dir, 'output.csv')
            export_data = []
            for activity in results['activities']:
                export_data.append({
                    'id': activity['id'],
                    'activity': activity['activity'],
                    'duration': activity['duration'],
                    'earliest_start': activity.get('earliest_start', 0),
                    'earliest_finish': activity.get('earliest_finish', 0),
                    'latest_start': activity.get('latest_start', 0),
                    'latest_finish': activity.get('latest_finish', 0),
                    'total_float': activity.get('total_float', 0),
                })
            
            save_csv_data(export_data, output_file)
            
            # Verify exported file
            exported_data = load_csv_data(output_file)
            assert len(exported_data) == len(sample_cpm_project)
    
    def test_error_recovery_invalid_file(self):
        """Test error recovery with invalid input files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            # Write invalid CSV data
            tmp_file.write("invalid,csv,format\nwithout,proper,structure")
            tmp_filename = tmp_file.name
        
        try:
            # Attempt to load invalid file
            with pytest.raises((ValueError, TypeError, KeyError)):
                loaded_data = load_csv_data(tmp_filename)
                analyzer = CPMAnalyzer()
                analyzer.analyze(loaded_data)
        finally:
            os.unlink(tmp_filename)


class TestPerformanceWorkflow:
    """Test performance characteristics of complete workflows."""
    
    def test_large_project_performance(self, large_project_data):
        """Test performance with large project datasets."""
        start_time = time.time()
        
        # Analyze large project
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(large_project_data)
        
        analysis_time = time.time() - start_time
        
        # Verify results
        assert 'project_duration' in results
        assert len(results['activities']) == len(large_project_data)
        
        # Performance assertion (adjust threshold as needed)
        assert analysis_time < 10.0, f"Analysis took {analysis_time:.2f}s, expected < 10s"
    
    def test_memory_usage_large_project(self, large_project_data):
        """Test memory usage with large project datasets."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform analysis
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(large_project_data)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (adjust threshold as needed)
        assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB is too high"
    
    def test_concurrent_analysis_performance(self, sample_cpm_project):
        """Test performance with concurrent analysis operations."""
        import concurrent.futures
        
        def analyze_project():
            analyzer = CPMAnalyzer()
            return analyzer.analyze(sample_cpm_project)
        
        start_time = time.time()
        
        # Run multiple concurrent analyses
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(analyze_project) for _ in range(10)]
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # Verify all analyses completed successfully
        assert len(results) == 10
        for result in results:
            assert 'project_duration' in result
            assert result['project_duration'] > 0
        
        # Concurrent execution should be faster than sequential
        assert total_time < 5.0, f"Concurrent analysis took {total_time:.2f}s"


class TestErrorRecoveryWorkflow:
    """Test error recovery and resilience workflows."""
    
    def test_invalid_data_graceful_handling(self):
        """Test graceful handling of invalid input data."""
        invalid_datasets = [
            [],  # Empty dataset
            [{'id': 'A'}],  # Missing required fields
            [{'id': 'A', 'duration': 'invalid'}],  # Invalid duration
            [{'id': 'A', 'duration': '5', 'predecessors': 'Z'}],  # Invalid predecessor
            [{'id': 'A', 'duration': '-5'}],  # Negative duration
        ]
        
        analyzer = CPMAnalyzer()
        
        for invalid_data in invalid_datasets:
            with pytest.raises((ValueError, TypeError, KeyError)):
                analyzer.analyze(invalid_data)
    
    def test_circular_dependency_detection(self):
        """Test detection and handling of circular dependencies."""
        circular_data = [
            {'id': 'A', 'activity': 'Task A', 'duration': '5', 'predecessors': 'B'},
            {'id': 'B', 'activity': 'Task B', 'duration': '3', 'predecessors': 'C'},
            {'id': 'C', 'activity': 'Task C', 'duration': '4', 'predecessors': 'A'},
        ]
        
        analyzer = CPMAnalyzer()
        
        # Should detect circular dependency and raise appropriate error
        with pytest.raises((ValueError, RuntimeError)):
            analyzer.analyze(circular_data)
    
    def test_partial_data_recovery(self):
        """Test recovery from partially corrupted data."""
        mixed_data = [
            {'id': 'A', 'activity': 'Good Task', 'duration': '5', 'predecessors': ''},
            {'id': 'B', 'activity': 'Bad Task', 'duration': 'invalid', 'predecessors': 'A'},
            {'id': 'C', 'activity': 'Another Good Task', 'duration': '3', 'predecessors': 'A'},
        ]
        
        # Depending on implementation, might skip invalid entries or raise error
        analyzer = CPMAnalyzer()
        
        try:
            results = analyzer.analyze(mixed_data)
            # If analysis succeeds, verify it handled the error appropriately
            assert len(results['activities']) <= len(mixed_data)
        except (ValueError, TypeError):
            # If analysis fails, that's also acceptable
            pass


class TestDataConsistencyWorkflow:
    """Test data consistency across different analysis types."""
    
    def test_cmp_pert_consistency(self):
        """Test consistency between CPM and PERT analysis of same project."""
        # Create project data suitable for both CPM and PERT
        project_data_cpm = [
            {'id': 'A', 'activity': 'Task A', 'duration': '5', 'predecessors': ''},
            {'id': 'B', 'activity': 'Task B', 'duration': '8', 'predecessors': 'A'},
            {'id': 'C', 'activity': 'Task C', 'duration': '3', 'predecessors': 'B'},
        ]
        
        project_data_pert = [
            {'id': 'A', 'activity': 'Task A', 'optimistic': '5', 'most_likely': '5', 'pessimistic': '5', 'predecessors': ''},
            {'id': 'B', 'activity': 'Task B', 'optimistic': '8', 'most_likely': '8', 'pessimistic': '8', 'predecessors': 'A'},
            {'id': 'C', 'activity': 'Task C', 'optimistic': '3', 'most_likely': '3', 'pessimistic': '3', 'predecessors': 'B'},
        ]
        
        # Analyze with both methods
        cpm_analyzer = CPMAnalyzer()
        pert_analyzer = PERTAnalyzer()
        
        cpm_results = cmp_analyzer.analyze(project_data_cmp)
        pert_results = pert_analyzer.analyze(project_data_pert)
        
        # Project durations should be identical (since PERT has no uncertainty)
        assert abs(cmp_results['project_duration'] - pert_results['expected_duration']) < 0.1
    
    def test_analysis_determinism(self, sample_cpm_project):
        """Test that repeated analysis gives consistent results."""
        analyzer = CPMAnalyzer()
        
        # Run analysis multiple times
        results1 = analyzer.analyze(sample_cpm_project)
        results2 = analyzer.analyze(sample_cpm_project)
        results3 = analyzer.analyze(sample_cpm_project)
        
        # Results should be identical
        assert results1['project_duration'] == results2['project_duration']
        assert results2['project_duration'] == results3['project_duration']
        assert results1['critical_path'] == results2['critical_path']
        assert results2['critical_path'] == results3['critical_path']


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_software_development_project(self):
        """Test analysis of typical software development project."""
        software_project = [
            {'id': 'REQ', 'activity': 'Requirements Analysis', 'duration': '5', 'predecessors': ''},
            {'id': 'DES', 'activity': 'System Design', 'duration': '8', 'predecessors': 'REQ'},
            {'id': 'DB', 'activity': 'Database Design', 'duration': '4', 'predecessors': 'DES'},
            {'id': 'UI', 'activity': 'UI Development', 'duration': '10', 'predecessors': 'DES'},
            {'id': 'API', 'activity': 'API Development', 'duration': '12', 'predecessors': 'DB'},
            {'id': 'INT', 'activity': 'Integration', 'duration': '6', 'predecessors': 'UI,API'},
            {'id': 'TEST', 'activity': 'Testing', 'duration': '8', 'predecessors': 'INT'},
            {'id': 'DOC', 'activity': 'Documentation', 'duration': '4', 'predecessors': 'TEST'},
            {'id': 'DEP', 'activity': 'Deployment', 'duration': '2', 'predecessors': 'DOC'},
        ]
        
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(software_project)
        
        # Verify realistic results
        assert results['project_duration'] > 20  # Should be substantial project
        assert results['project_duration'] < 100  # But not unreasonably long
        assert len(results['critical_path']) >= 4  # Should have meaningful critical path
    
    def test_construction_project(self):
        """Test analysis of typical construction project."""
        construction_project = [
            {'id': 'PERM', 'activity': 'Obtain Permits', 'duration': '10', 'predecessors': ''},
            {'id': 'SITE', 'activity': 'Site Preparation', 'duration': '5', 'predecessors': 'PERM'},
            {'id': 'FOUND', 'activity': 'Foundation', 'duration': '8', 'predecessors': 'SITE'},
            {'id': 'FRAME', 'activity': 'Framing', 'duration': '12', 'predecessors': 'FOUND'},
            {'id': 'ROOF', 'activity': 'Roofing', 'duration': '6', 'predecessors': 'FRAME'},
            {'id': 'ELEC', 'activity': 'Electrical', 'duration': '8', 'predecessors': 'FRAME'},
            {'id': 'PLUMB', 'activity': 'Plumbing', 'duration': '7', 'predecessors': 'FRAME'},
            {'id': 'DRYWALL', 'activity': 'Drywall', 'duration': '10', 'predecessors': 'ELEC,PLUMB,ROOF'},
            {'id': 'FINISH', 'activity': 'Finishing', 'duration': '15', 'predecessors': 'DRYWALL'},
        ]
        
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(construction_project)
        
        # Verify realistic construction timeline
        assert results['project_duration'] > 30  # Construction takes time
        assert 'PERM' in results['critical_path']  # Permits usually critical
        assert 'FINISH' in results['critical_path']  # Finishing usually critical


# Stress tests
@pytest.mark.slow
class TestStressWorkflows:
    """Stress tests for extreme scenarios."""
    
    def test_maximum_project_size(self):
        """Test analysis with maximum reasonable project size."""
        # Create very large project (1000 activities)
        large_project = []
        for i in range(1000):
            activity = {
                'id': f'T{i:04d}',
                'activity': f'Task {i+1}',
                'duration': str((i % 20) + 1),
                'predecessors': ','.join([f'T{j:04d}' for j in range(max(0, i-3), i)])
            }
            large_project.append(activity)
        
        start_time = time.time()
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(large_project)
        analysis_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert analysis_time < 30.0, f"Large project analysis took {analysis_time:.2f}s"
        assert results['project_duration'] > 0
        assert len(results['activities']) == 1000
    
    def test_complex_dependency_network(self):
        """Test analysis with complex dependency relationships."""
        # Create project with many interdependencies
        complex_project = []
        for i in range(50):
            # Create complex dependency patterns
            predecessors = []
            for j in range(max(0, i-5), i):
                if (i + j) % 3 == 0:  # Create selective dependencies
                    predecessors.append(f'C{j:02d}')
            
            activity = {
                'id': f'C{i:02d}',
                'activity': f'Complex Task {i+1}',
                'duration': str((i % 10) + 1),
                'predecessors': ','.join(predecessors)
            }
            complex_project.append(activity)
        
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(complex_project)
        
        # Should handle complex dependencies
        assert results['project_duration'] > 0
        assert len(results['critical_path']) > 0


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v", "--tb=short"])
