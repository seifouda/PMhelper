#!/usr/bin/env python3
"""
Integration test for RC        # Run CPM analysis on sample data
        try:
            cpm_results = mock_main.cpm_analyzer.analyze_project(sample_data)
            mock_main.current_data = cpm_results
            print("✅ CPM analysis completed successfully")
        except Exception as e:lscreen comparison feature with real data
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_rcps_fullscreen_integration():
    """Test RCPS fullscreen feature with the actual application data"""
    
    print("=== RCPS Fullscreen Integration Test ===")
    
    # Load sample project data
    try:
        sample_data = pd.DataFrame({
            'id': ['A', 'B', 'C', 'D', 'E'],
            'description': ['Design', 'Coding', 'Testing', 'Review', 'Deploy'],
            'duration': [3, 5, 2, 1, 2],
            'resource': [2, 3, 1, 1, 2],
            'predecessors': ['', 'A', 'B', 'C', 'D']
        })
        print("✅ Sample project data created")
        
        # Create main test window
        root = tk.Tk()
        root.title("RCPS Fullscreen Integration Test")
        root.geometry("800x600")
        
        # Import required modules
        from src.pmhelper.core.cpm_analyzer import CPMAnalyzer
        from src.pmhelper.gui.tabs.rcps_tab import RCPSTab
        
        print("✅ Successfully imported CPM analyzer and RCPS tab")
        
        # Create a mock main window class
        class MockMainWindow:
            def __init__(self):
                self.current_data = None
                self.analysis_mode = 'deterministic'
                self.cpm_analyzer = CPMAnalyzer()
                self.pert_analyzer = None
                
        # Create mock main window and run CPM analysis
        mock_main = MockMainWindow()
        
        # Run CPM analysis on sample data
        try:
            cpm_results = mock_main.cmp_analyzer.analyze_project(sample_data)
            mock_main.current_data = cpm_results
            print("✅ CPM analysis completed successfully")
        except Exception as e:
            print(f"❌ CPM analysis failed: {e}")
            # Create fallback data for testing
            mock_main.current_data = sample_data.copy()
            mock_main.current_data['early_start'] = [0, 3, 8, 10, 11]
            mock_main.current_data['late_finish'] = [3, 8, 10, 11, 13]
            mock_main.current_data['float'] = [0, 0, 0, 0, 0]
            print("✅ Using fallback data for testing")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create RCPS tab
        rcps_tab = RCPSTab(notebook, mock_main)
        print("✅ RCPS tab created successfully")
        
        # Create test interface
        test_frame = ttk.Frame(root)
        test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        status_label = tk.Label(test_frame, text="Integration test ready", 
                               font=("Arial", 12, "bold"))
        status_label.pack(pady=10)
        
        def run_rcps_test():
            """Run RCPS analysis and test fullscreen feature"""
            try:
                # Run RCPS analysis
                status_label.config(text="Running RCPS analysis...", fg="blue")
                root.update()
                
                rcps_tab.run_rcps()
                
                status_label.config(text="RCPS analysis completed! Fullscreen button should be enabled.", 
                                   fg="green")
                
                # Test the fullscreen feature
                def test_fullscreen():
                    try:
                        rcps_tab.open_fullscreen_comparison()
                        status_label.config(text="✅ Fullscreen comparison opened successfully!", 
                                           fg="green")
                    except Exception as e:
                        status_label.config(text=f"❌ Fullscreen test failed: {e}", fg="red")
                        print(f"Fullscreen error: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Add fullscreen test button
                fullscreen_test_btn = ttk.Button(test_frame, text="Test Fullscreen Feature", 
                                                command=test_fullscreen)
                fullscreen_test_btn.pack(pady=5)
                
            except Exception as e:
                status_label.config(text=f"❌ RCPS analysis failed: {e}", fg="red")
                print(f"RCPS error: {e}")
                import traceback
                traceback.print_exc()
        
        # Create test buttons
        run_btn = ttk.Button(test_frame, text="Run RCPS Analysis", command=run_rcps_test)
        run_btn.pack(pady=5)
        
        close_btn = ttk.Button(test_frame, text="Close Test", command=root.quit)
        close_btn.pack(pady=5)
        
        print("\n🚀 Integration test interface created")
        print("📋 Test Steps:")
        print("   1. Click 'Run RCPS Analysis' to generate data")
        print("   2. Click 'Test Fullscreen Feature' to open fullscreen view")
        print("   3. Verify that both CPM and RCPS Gantt charts display correctly")
        
        # Start the test
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rcps_fullscreen_integration()
    if success:
        print("\n✅ Integration test completed!")
    else:
        print("\n❌ Integration test failed!")
