#!/usr/bin/env python3
"""
Test GUI Components

Unit tests for the refactored GUI components including tabs and main window.
"""

import unittest
import sys
from pathlib import Path
import tkinter as tk

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pmhelper.gui.main_window import MainWindow
from pmhelper.gui.tabs import InputTab, ResultsTab, NetworkTab, GanttTab, ProbabilityTab


class TestGUIComponents(unittest.TestCase):
    """Test GUI components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Create root window for testing
        cls.root = tk.Tk()
        cls.root.withdraw()  # Hide the window during testing
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        cls.root.destroy()
    
    def setUp(self):
        """Set up each test"""
        # Create a test notebook
        import tkinter.ttk as ttk
        self.test_window = tk.Toplevel(self.root)
        self.test_window.withdraw()
        self.notebook = ttk.Notebook(self.test_window)
        
        # Mock main window
        self.mock_main_window = MockMainWindow()
    
    def tearDown(self):
        """Clean up each test"""
        if hasattr(self, 'test_window'):
            self.test_window.destroy()
    
    def test_input_tab_creation(self):
        """Test InputTab creation"""
        try:
            input_tab = InputTab(self.notebook, self.mock_main_window)
            self.assertIsNotNone(input_tab)
            self.assertEqual(input_tab.current_mode, 'deterministic')
        except Exception as e:
            self.fail(f"InputTab creation failed: {e}")
    
    def test_results_tab_creation(self):
        """Test ResultsTab creation"""
        try:
            results_tab = ResultsTab(self.notebook, self.mock_main_window)
            self.assertIsNotNone(results_tab)
            self.assertIsNone(results_tab.results_data)
        except Exception as e:
            self.fail(f"ResultsTab creation failed: {e}")
    
    def test_network_tab_creation(self):
        """Test NetworkTab creation"""
        try:
            network_tab = NetworkTab(self.notebook, self.mock_main_window)
            self.assertIsNotNone(network_tab)
            self.assertIsNone(network_tab.results_data)
        except Exception as e:
            self.fail(f"NetworkTab creation failed: {e}")
    
    def test_gantt_tab_creation(self):
        """Test GanttTab creation"""
        try:
            gantt_tab = GanttTab(self.notebook, self.mock_main_window)
            self.assertIsNotNone(gantt_tab)
            self.assertIsNone(gantt_tab.results_data)
        except Exception as e:
            self.fail(f"GanttTab creation failed: {e}")
    
    def test_probability_tab_creation(self):
        """Test ProbabilityTab creation"""
        try:
            probability_tab = ProbabilityTab(self.notebook, self.mock_main_window)
            self.assertIsNotNone(probability_tab)
            self.assertIsNone(probability_tab.results_data)
        except Exception as e:
            self.fail(f"ProbabilityTab creation failed: {e}")
    
    def test_input_tab_mode_switching(self):
        """Test InputTab mode switching"""
        input_tab = InputTab(self.notebook, self.mock_main_window)
        
        # Test switching to probabilistic mode
        input_tab.set_mode('probabilistic')
        self.assertEqual(input_tab.current_mode, 'probabilistic')
        
        # Test switching back to deterministic mode
        input_tab.set_mode('deterministic')
        self.assertEqual(input_tab.current_mode, 'deterministic')
    
    def test_input_tab_sample_data(self):
        """Test InputTab sample data loading"""
        input_tab = InputTab(self.notebook, self.mock_main_window)
        
        # Test loading sample CPM data
        try:
            input_tab.load_sample_cmp()
            self.assertEqual(input_tab.current_mode, 'deterministic')
        except Exception as e:
            self.fail(f"Loading sample CPM data failed: {e}")
        
        # Test loading sample PERT data
        try:
            input_tab.load_sample_pert()
            self.assertEqual(input_tab.current_mode, 'probabilistic')
        except Exception as e:
            self.fail(f"Loading sample PERT data failed: {e}")
    
    def test_input_tab_data_extraction(self):
        """Test InputTab data extraction"""
        input_tab = InputTab(self.notebook, self.mock_main_window)
        
        # Load sample data and test extraction
        input_tab.load_sample_cmp()
        activities_data = input_tab.get_activities_data()
        
        self.assertIsInstance(activities_data, list)
        if activities_data:
            self.assertIsInstance(activities_data[0], dict)
            self.assertIn('id', activities_data[0])
            self.assertIn('activity', activities_data[0])


class MockMainWindow:
    """Mock main window for testing"""
    
    def __init__(self):
        self.analysis_mode = None
        self.status_message = ""
    
    def set_analysis_mode(self, mode):
        """Mock set analysis mode"""
        self.analysis_mode = mode
    
    def set_status(self, message):
        """Mock set status"""
        self.status_message = message
    
    def analyze_project(self):
        """Mock analyze project"""
        pass


class TestMainWindow(unittest.TestCase):
    """Test MainWindow class"""
    
    def test_main_window_creation(self):
        """Test MainWindow creation (without actually showing it)"""
        try:
            # Test that MainWindow can be imported and instantiated
            # We won't actually create the window to avoid GUI in tests
            self.assertTrue(hasattr(MainWindow, '__init__'))
            self.assertTrue(hasattr(MainWindow, 'analyze_project'))
            self.assertTrue(hasattr(MainWindow, 'set_analysis_mode'))
        except Exception as e:
            self.fail(f"MainWindow class test failed: {e}")


class TestGUIIntegration(unittest.TestCase):
    """Test GUI integration"""
    
    def test_all_imports(self):
        """Test that all GUI components can be imported"""
        try:
            from pmhelper.gui.main_window import MainWindow
            from pmhelper.gui.tabs import InputTab, ResultsTab, NetworkTab, GanttTab, ProbabilityTab
            
            # Check that classes are properly imported
            self.assertTrue(callable(MainWindow))
            self.assertTrue(callable(InputTab))
            self.assertTrue(callable(ResultsTab))
            self.assertTrue(callable(NetworkTab))
            self.assertTrue(callable(GanttTab))
            self.assertTrue(callable(ProbabilityTab))
            
        except ImportError as e:
            self.fail(f"Failed to import GUI components: {e}")
    
    def test_tab_interface_compatibility(self):
        """Test that all tabs have compatible interfaces"""
        # Define expected methods for tab classes
        expected_methods = [
            '__init__',
            'create_tab'
        ]
        
        tab_classes = [InputTab, ResultsTab, NetworkTab, GanttTab, ProbabilityTab]
        
        for tab_class in tab_classes:
            for method in expected_methods:
                self.assertTrue(hasattr(tab_class, method), 
                              f"{tab_class.__name__} missing method: {method}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
