import unittest
import pandas as pd
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from pmhelper.core.cpm_analyzer import CPMAnalyzer

class TestRCPSAlgorithms(unittest.TestCase):
    """Test suite for RCPS core algorithms"""
    
    def setUp(self):
        """Set up test data and analyzers"""
        self.cpm_analyzer = CPMAnalyzer()
        
        # Sample project data for testing
        self.sample_data = [
            {'id': 'A', 'activity': 'Task A', 'duration': 3, 'resource': 2, 'predecessors': ''},
            {'id': 'B', 'activity': 'Task B', 'duration': 4, 'resource': 1, 'predecessors': ''},
            {'id': 'C', 'activity': 'Task C', 'duration': 2, 'resource': 3, 'predecessors': 'A,B'},
            {'id': 'D', 'activity': 'Task D', 'duration': 5, 'resource': 2, 'predecessors': 'C'},
            {'id': 'E', 'activity': 'Task E', 'duration': 3, 'resource': 1, 'predecessors': 'C'},
        ]
        
        # Create DataFrame with CPM analysis
        self.df = pd.DataFrame(self.sample_data)
        
        # Run CPM analysis to get proper timing data
        G, _, _ = self.cpm_analyzer.analyze(self.sample_data)
        
        # Extract timing data from graph
        for idx, row in self.df.iterrows():
            activity_id = row['id']
            if activity_id in G.nodes:
                self.df.at[idx, 'early_start'] = G.nodes[activity_id].get('ES', 0)
                self.df.at[idx, 'late_finish'] = G.nodes[activity_id].get('LF', 0)
                self.df.at[idx, 'float'] = G.nodes[activity_id].get('float', 0)
        
    def test_resource_constraint_validation(self):
        """Test resource limit validation logic"""
        # Test valid resource limit
        resource_limit = 5
        try:
            table, _, _ = self.cpm_analyzer.rcps_heuristic_schedule_table(
                self.df, resource_limit, 'minimum_slack'
            )
            self.assertIsInstance(table, pd.DataFrame)
        except Exception as e:
            self.fail(f"Valid resource limit should not raise exception: {e}")
        
    def test_priority_rule_sorting(self):
        """Test different priority rule implementations"""
        resource_limit = 10  # High limit to avoid resource conflicts
        
        priority_rules = ['minimum_slack', 'shortest_duration', 'earliest_start']
        
        for rule in priority_rules:
            with self.subTest(priority_rule=rule):
                table, actual_starts, _ = self.cpm_analyzer.rcps_heuristic_schedule_table(
                    self.df, resource_limit, rule
                )
                
                # Verify table structure
                self.assertIsInstance(table, pd.DataFrame)
                self.assertIn('actual_start', table.columns)
                self.assertIsInstance(actual_starts, dict)
                
                # Verify all activities have start times
                activities = table[~table['id'].isin(['RA', 'RS'])]
                for _, activity in activities.iterrows():
                    self.assertIsNotNone(activity['actual_start'])
    
    def test_schedule_generation_accuracy(self):
        """Test RCPS schedule generation accuracy"""
        resource_limit = 3
        
        table, actual_starts, critical_ids = self.cpm_analyzer.rcps_heuristic_schedule_table(
            self.df, resource_limit, 'minimum_slack'
        )
        
        # Verify schedule structure
        self.assertIsInstance(table, pd.DataFrame)
        self.assertGreater(len(table), 0)
        
        # Check for resource rows
        self.assertIn('RA', table['id'].values)  # Resource Available
        self.assertIn('RS', table['id'].values)  # Resource Scheduled

if __name__ == '__main__':
    unittest.main()
