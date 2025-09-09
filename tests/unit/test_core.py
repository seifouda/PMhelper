#!/usr/bin/env python3
"""
Test Core Modules

Unit tests for core PMHelper modules (CPM, PERT, NetworkBuilder).
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestCPMAnalyzer(unittest.TestCase):
    """Test CPM Analyzer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        from pmhelper.utils.file_handlers import FileHandler
        
        self.analyzer = CPMAnalyzer()
        self.sample_data = FileHandler.get_sample_cpm_data()
    
    def test_analyzer_creation(self):
        """Test CPM analyzer can be created"""
        self.assertIsNotNone(self.analyzer)
    
    def test_data_loading(self):
        """Test loading sample data"""
        activities = self.analyzer.load_activities_from_data(self.sample_data)
        self.assertIsNotNone(activities)
        self.assertGreater(len(activities), 0)
    
    def test_analysis_execution(self):
        """Test running CPM analysis"""
        try:
            graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_data)
            self.assertIsNotNone(graph)
            self.assertIsNotNone(critical_paths)
            self.assertIsNotNone(critical_activities)
        except Exception as e:
            self.fail(f"CPM analysis failed: {e}")


class TestPERTAnalyzer(unittest.TestCase):
    """Test PERT Analyzer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        from pmhelper.core.pert_analyzer import PERTAnalyzer
        from pmhelper.utils.file_handlers import FileHandler
        
        self.analyzer = PERTAnalyzer()
        self.sample_data = FileHandler.get_sample_pert_data()
    
    def test_analyzer_creation(self):
        """Test PERT analyzer can be created"""
        self.assertIsNotNone(self.analyzer)
    
    def test_data_loading(self):
        """Test loading sample PERT data"""
        activities = self.analyzer.load_activities_from_pert_data(self.sample_data)
        self.assertIsNotNone(activities)
        self.assertGreater(len(activities), 0)
    
    def test_analysis_execution(self):
        """Test running PERT analysis"""
        try:
            graph, critical_paths, critical_activities = self.analyzer.analyze(self.sample_data)
            self.assertIsNotNone(graph)
            self.assertIsNotNone(critical_paths)
            self.assertIsNotNone(critical_activities)
        except Exception as e:
            self.fail(f"PERT analysis failed: {e}")


class TestNetworkBuilder(unittest.TestCase):
    """Test NetworkBuilder functionality"""
    
    def setUp(self):
        """Set up test environment"""
        from pmhelper.core.network_builder import NetworkBuilder
        from pmhelper.utils.file_handlers import FileHandler
        
        self.builder = NetworkBuilder()
        self.sample_data = FileHandler.get_sample_cpm_data()
    
    def test_builder_creation(self):
        """Test NetworkBuilder can be created"""
        self.assertIsNotNone(self.builder)
    
    def test_network_building(self):
        """Test building network graph"""
        try:
            # Convert sample data to activities format
            activities = []
            for item in self.sample_data:
                activity = {
                    'id': item.get('id', ''),
                    'duration': float(item.get('duration', 0)),
                    'predecessors': item.get('predecessors', '').split(',') if item.get('predecessors') else []
                }
                activities.append(activity)
            
            graph = self.builder.build_network(activities)
            self.assertIsNotNone(graph)
        except Exception as e:
            self.fail(f"Network building failed: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
