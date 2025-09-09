#!/usr/bin/env python3
"""Comprehensive test of the Gantt chart fix"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

print("=== COMPREHENSIVE GANTT CHART FIX TEST ===")

try:
    # Test 1: Import all required modules
    print("\n1. Testing imports...")
    from pmhelper.gui.tabs.gantt_tab import GanttTab
    from pmhelper.utils.visualizations import GanttChartVisualizer
    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')  # Non-GUI backend for testing
    print("✅ All imports successful")
    
    # Test 2: Check method signature
    print("\n2. Checking method signature...")
    import inspect
    sig = inspect.signature(GanttChartVisualizer.create_gantt_chart)
    print(f"✅ Method signature: {sig}")
    
    # Test 3: Create test graph and call the method
    print("\n3. Testing method call with correct parameters...")
    
    # Create a simple test graph with node attributes
    G = nx.DiGraph()
    G.add_node('A', ES=0, EF=3, LS=0, LF=3, duration=3, float=0, activity='Task A')
    G.add_node('B', ES=3, EF=7, LS=3, LF=7, duration=4, float=0, activity='Task B')
    G.add_node('C', ES=7, EF=9, LS=7, LF=9, duration=2, float=0, activity='Task C')
    G.add_edges_from([('A', 'B'), ('B', 'C')])
    
    critical_activities = ['A', 'B', 'C']
    
    # Test the method call
    visualizer = GanttChartVisualizer()
    result_fig = visualizer.create_gantt_chart(
        G,                    # NetworkX graph
        critical_activities,  # List of critical activities
        (12, 8)              # Figure size
    )
    
    print("✅ GanttChartVisualizer.create_gantt_chart() called successfully!")
    print(f"✅ Returned figure: {result_fig}")
    
    # Test 4: Simulate the exact call pattern from GanttTab
    print("\n4. Testing GanttTab parameter pattern...")
    
    # Mock results_data like what GanttTab receives
    results_data = {
        'graph': G,
        'critical_activities': critical_activities,
        'project_duration': 9
    }
    
    # Simulate the exact extraction pattern from update_gantt
    G_extracted = results_data.get('graph')
    critical_activities_extracted = results_data.get('critical_activities', [])
    project_duration_extracted = results_data.get('project_duration', None)
    
    print(f"✅ Graph extracted: {G_extracted}")
    print(f"✅ Critical activities extracted: {critical_activities_extracted}")
    print(f"✅ Project duration extracted: {project_duration_extracted}")
    
    # Simulate the exact call pattern from update_chart
    result_fig2 = visualizer.create_gantt_chart(
        G_extracted,                    # NetworkX graph
        critical_activities_extracted,  # List of critical activities
        (12, 8)                        # Figure size
    )
    
    print("✅ GanttTab call pattern successful!")
    
    print("\n🎉 ALL TESTS PASSED - GANTT CHART FIX IS WORKING!")
    print("The 'unexpected keyword argument activities' error should be resolved.")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
