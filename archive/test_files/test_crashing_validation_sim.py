#!/usr/bin/env python3
"""
Test script to simulate crashing tab validation behavior
"""
import sys
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.core.cpm_analyzer import CPMAnalyzer
import tkinter as tk
from tkinter import messagebox

def simulate_validation_test():
    """Simulate the validation that happens in crashing_tab_gui.py"""
    print("Testing Crashing Tab Validation Simulation")
    print("=" * 50)
    
    # Create a simple root window (but don't show it)
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Sample activities data 
    activities_data = [
        {'id': 'A', 'activity': 'Design Phase', 'duration': 5, 'predecessors': '', 'normal_cost': 1000, 'crash_cost': 200, 'min_duration': 3},
        {'id': 'B', 'activity': 'Requirements Analysis', 'duration': 3, 'predecessors': '', 'normal_cost': 600, 'crash_cost': 150, 'min_duration': 2},
        {'id': 'C', 'activity': 'Architecture Design', 'duration': 7, 'predecessors': 'A,B', 'normal_cost': 1400, 'crash_cost': 300, 'min_duration': 5},
        {'id': 'D', 'activity': 'Database Design', 'duration': 5, 'predecessors': 'C', 'normal_cost': 1000, 'crash_cost': 250, 'min_duration': 3},
        {'id': 'E', 'activity': 'Frontend Development', 'duration': 6, 'predecessors': 'C', 'normal_cost': 1200, 'crash_cost': 300, 'min_duration': 4},
        {'id': 'F', 'activity': 'Backend Development', 'duration': 8, 'predecessors': 'C', 'normal_cost': 1600, 'crash_cost': 400, 'min_duration': 6},
        {'id': 'G', 'activity': 'Testing', 'duration': 3, 'predecessors': 'D', 'normal_cost': 600, 'crash_cost': 200, 'min_duration': 2},
        {'id': 'H', 'activity': 'Deployment', 'duration': 4, 'predecessors': 'E,F', 'normal_cost': 800, 'crash_cost': 300, 'min_duration': 3},
        {'id': 'I', 'activity': 'Documentation', 'duration': 3, 'predecessors': 'G,H', 'normal_cost': 600, 'crash_cost': 200, 'min_duration': 2},
    ]
    
    # Simulate the analyzer setup
    base_analyzer = CPMAnalyzer()
    G, critical_paths, critical_activities = base_analyzer.analyze(activities_data)
    
    print(f"Project analysis completed:")
    print(f"  Critical path: {critical_paths[0] if critical_paths else 'None'}")
    
    # Calculate original duration using the same logic as crashing_tab_gui.py
    ef_values = [base_analyzer.graph.nodes[node].get('EF', 0) for node in base_analyzer.graph.nodes()]
    original_duration = max(ef_values) if ef_values else 0
    print(f"  Original project duration: {original_duration}")
    
    # Test different target durations
    test_targets = [20, 25, 27, 30, 35]
    
    for target_duration in test_targets:
        print(f"\nTesting target duration: {target_duration}")
        
        # Simulate the validation logic from crashing_tab_gui.py
        try:
            # Check if analysis has been run (EF values should be > 0 for at least one node)
            if not any(ef > 0 for ef in ef_values):
                print("  ❌ Would show: Analysis Required warning")
                continue
            
            if target_duration > original_duration:
                print(f"  ❌ Would show: Invalid Target Duration warning")
                print(f"     Message: Target duration ({target_duration}) cannot be greater than original duration ({original_duration})")
            else:
                print(f"  ✅ Validation passed - would proceed with crashing analysis")
                
        except Exception as e:
            print(f"  ⚠️  Error in validation: {e}")
    
    # Test the "no analysis" scenario
    print(f"\nTesting scenario with no analysis run:")
    # Simulate analyzer with no EF values
    empty_ef_values = [0, 0, 0, 0, 0]  # Simulate no analysis run
    if not any(ef > 0 for ef in empty_ef_values):
        print("  ❌ Would show: Analysis Required warning")
        print("     Message: Please run CPM or PERT analysis first before using project crashing")
    
    root.destroy()
    print(f"\n✅ Validation simulation completed successfully!")

if __name__ == "__main__":
    simulate_validation_test()
