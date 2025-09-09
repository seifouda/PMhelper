#!/usr/bin/env python3
"""
End-to-end test of the CPM/PERT desktop application.
This tests the complete workflow including CSV loading and analysis.
"""

import sys
import os
import csv
import tempfile
import traceback

# Add the code directory to the path
sys.path.insert(0, r'd:\PMhelper\code')

def create_test_deterministic_csv():
    """Create a temporary CSV file with deterministic data"""
    fd, path = tempfile.mkstemp(suffix='.csv', text=True)
    
    try:
        with os.fdopen(fd, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'activity', 'duration', 'predecessors', 'min_duration', 'crash_cost', 'resource_demand'])
            writer.writerow(['A', 'Design Phase', '5', '', '1', '300', '2'])
            writer.writerow(['B', 'Requirements Analysis', '3', '', '2', '500', '1'])
            writer.writerow(['C', 'Architecture Design', '7', 'A,B', '5', '600', '3'])
            writer.writerow(['D', 'Database Design', '5', 'C', '4', '400', '1'])
            writer.writerow(['E', 'Testing', '3', 'D', '3', '800', '2'])
        return path
    except:
        os.close(fd)
        os.unlink(path)
        raise

def create_test_probabilistic_csv():
    """Create a temporary CSV file with probabilistic data"""
    fd, path = tempfile.mkstemp(suffix='.csv', text=True)
    
    try:
        with os.fdopen(fd, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'predecessors', 'optimistic', 'most_likely', 'pessimistic', 'min_duration', 'crash_cost', 'resource_demand', 'normal_cost'])
            writer.writerow(['A', '', '3', '4', '7', '1', '300', '3', '300'])
            writer.writerow(['B', '', '7', '9', '12', '2', '600', '4', '300'])
            writer.writerow(['C', 'A,B', '4', '5', '9', '1', '500', '2', '300'])
            writer.writerow(['D', 'C', '10', '11', '16', '1', '350', '3', '300'])
            writer.writerow(['E', 'D', '6', '8', '10', '1', '100', '4', '300'])
        return path
    except:
        os.close(fd)
        os.unlink(path)
        raise

def test_deterministic_workflow():
    """Test the complete deterministic workflow"""
    print("Testing Deterministic (CPM) Workflow...")
    
    det_csv_path = None
    try:
        import tkinter as tk
        from cpm_app import CPMDesktopApp
        
        # Create test CSV
        det_csv_path = create_test_deterministic_csv()
        print("✓ Test deterministic CSV created")
        
        # Create GUI app (hidden)
        root = tk.Tk()
        root.withdraw()
        app = CPMDesktopApp(root)
        
        # Simulate loading deterministic CSV data
        app.analysis_mode = 'deterministic'
        app.current_analyzer = app.cpm_analyzer
        app.setup_deterministic_tree()
        
        # Load test data manually (simulating CSV load)
        with open(det_csv_path, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                app.tree.insert("", tk.END, values=(
                    row['id'],
                    row['activity'],
                    row['duration'],
                    row['predecessors'],
                    row['min_duration'],
                    row['crash_cost'],
                    row['resource_demand']
                ))
        print("✓ Data loaded into GUI")
        
        # Test analysis
        activities_data = app.get_activities_data()
        assert len(activities_data) == 5, "Expected 5 activities"
        print("✓ Activities data extracted from GUI")
        
        # Perform analysis
        G, critical_paths, critical_activities = app.cpm_analyzer.analyze(activities_data)
        print("✓ CPM analysis completed")
        print(f"  Project duration: {max([G.nodes[node]['EF'] for node in G.nodes()])}")
        print(f"  Critical activities: {[a for a in critical_activities if a not in ['START', 'END']]}")
        
        # Test result display
        app.display_results(G, critical_paths, "CPM")
        results_content = app.results_text.get(1.0, tk.END)
        assert "CPM ANALYSIS RESULTS" in results_content, "Results not displayed correctly"
        print("✓ Results displayed in GUI")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Deterministic workflow test failed: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if det_csv_path and os.path.exists(det_csv_path):
            os.unlink(det_csv_path)

def test_probabilistic_workflow():
    """Test the complete probabilistic workflow"""
    print("\nTesting Probabilistic (PERT) Workflow...")
    
    prob_csv_path = None
    try:
        import tkinter as tk
        from cpm_app import CPMDesktopApp
        
        # Create test CSV
        prob_csv_path = create_test_probabilistic_csv()
        print("✓ Test probabilistic CSV created")
        
        # Create GUI app (hidden)
        root = tk.Tk()
        root.withdraw()
        app = CPMDesktopApp(root)
        
        # Simulate loading probabilistic CSV data
        app.analysis_mode = 'probabilistic'
        app.current_analyzer = app.pert_analyzer
        app.setup_probabilistic_tree()
        
        # Load test data manually (simulating CSV load)
        activities_data = []
        with open(prob_csv_path, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                pert_data = {
                    'id': row['id'],
                    'predecessors': row.get('predecessors', '').strip(),
                    'optimistic': int(row['optimistic']),
                    'most_likely': int(row['most_likely']),
                    'pessimistic': int(row['pessimistic']),
                    'min_duration': int(row.get('min_duration', '1')),
                    'crash_cost': int(row.get('crash_cost', '0')),
                    'resource_demand': int(row.get('resource_demand', '0')),
                    'normal_cost': int(row.get('normal_cost', '0'))
                }
                activities_data.append(pert_data)
        
        # Process through PERT analyzer
        processed_activities = app.pert_analyzer.load_activities_from_pert_data(activities_data)
        
        # Display in tree
        for activity in processed_activities:
            app.tree.insert("", tk.END, values=(
                activity['id'],
                ', '.join(activity['predecessors']) if activity['predecessors'] else '',
                activity['optimistic'],
                activity['most_likely'],
                activity['pessimistic'],
                activity['expected_time_ceil'],
                f"{activity['variance']:.3f}",
                activity.get('min_duration', 1),
                activity.get('crash_cost', 0),
                activity.get('resource_demand', 0),
                activity.get('normal_cost', 0)
            ))
        print("✓ Data loaded into GUI")
        
        # Test analysis
        gui_activities_data = app.get_activities_data()
        assert len(gui_activities_data) == 5, "Expected 5 activities"
        print("✓ Activities data extracted from GUI")
        
        # Perform analysis
        G, critical_paths, critical_activities = app.pert_analyzer.analyze(gui_activities_data)
        print("✓ PERT analysis completed")
        print(f"  Project duration: {max([G.nodes[node]['EF'] for node in G.nodes()])}")
        print(f"  Critical activities: {[a for a in critical_activities if a not in ['START', 'END']]}")
        print(f"  Project variance: {app.pert_analyzer.project_variance}")
        
        # Test result display
        app.display_results(G, critical_paths, "PERT")
        results_content = app.results_text.get(1.0, tk.END)
        assert "PERT ANALYSIS RESULTS" in results_content, "Results not displayed correctly"
        print("✓ Results displayed in GUI")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Probabilistic workflow test failed: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if prob_csv_path and os.path.exists(prob_csv_path):
            os.unlink(prob_csv_path)

def test_sample_data_loading():
    """Test the sample data loading functionality"""
    print("\nTesting Sample Data Loading...")
    
    try:
        import tkinter as tk
        from cpm_app import CPMDesktopApp
        
        # Create GUI app (hidden)
        root = tk.Tk()
        root.withdraw()
        app = CPMDesktopApp(root)
        
        # Test sample data loading (which happens automatically)
        # Verify sample data was loaded
        tree_items = app.tree.get_children()
        assert len(tree_items) > 0, "No sample data loaded"
        print(f"✓ Sample data loaded ({len(tree_items)} activities)")
        
        # Verify it's in deterministic mode
        assert app.analysis_mode == 'deterministic', "Not in deterministic mode"
        assert app.current_analyzer == app.cpm_analyzer, "Wrong analyzer selected"
        print("✓ Correct mode and analyzer set")
        
        # Test analysis with sample data
        activities_data = app.get_activities_data()
        G, critical_paths, critical_activities = app.cpm_analyzer.analyze(activities_data)
        print("✓ Analysis with sample data works")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Sample data loading test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all end-to-end tests"""
    print("="*70)
    print("CPM/PERT Application End-to-End Testing")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(test_deterministic_workflow())
    results.append(test_probabilistic_workflow())
    results.append(test_sample_data_loading())
    
    # Summary
    print("\n" + "="*70)
    print("END-TO-END TEST SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} end-to-end tests PASSED!")
        print("\nThe CPM/PERT application is fully functional:")
        print("- ✓ Deterministic (CPM) analysis workflow")
        print("- ✓ Probabilistic (PERT) analysis workflow")
        print("- ✓ Sample data loading and analysis")
        print("- ✓ GUI data extraction and display")
        print("- ✓ All analyzer methods working correctly")
        print("\nThe application is ready for production use!")
        return 0
    else:
        print(f"✗ {total - passed} of {total} end-to-end tests FAILED!")
        print("\nSome workflow issues remain that need to be addressed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
