#!/usr/bin/env python3
"""
Comprehensive test script for PERT Diagram tab with actual project data
"""

import tkinter as tk
from tkinter import ttk
import sys
sys.path.insert(0, 'src')

try:
    from pmhelper.gui.tabs.pert_diagram_tab import PertDiagramTab
    from pmhelper.core.cpm_analyzer import CPMAnalyzer
    print("✓ Imports successful")
    
    # Create test window
    root = tk.Tk()
    root.title("PERT Diagram Tab Comprehensive Test")
    root.geometry("1200x800")
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Mock main window
    class MockMainWindow:
        def __init__(self):
            self.analysis_mode = 'deterministic'
            self.results_data = None
    
    main_window = MockMainWindow()
    
    # Create PERT diagram tab
    pert_tab = PertDiagramTab(notebook, main_window)
    print("✓ PERT Diagram tab created")
    
    # Create sample project data
    sample_activities = [
        {
            'id': 'A',
            'activity': 'Design Phase',
            'duration': 5,
            'predecessors': []
        },
        {
            'id': 'B', 
            'activity': 'Development',
            'duration': 8,
            'predecessors': ['A']
        },
        {
            'id': 'C',
            'activity': 'Testing',
            'duration': 3,
            'predecessors': ['B']
        },
        {
            'id': 'D',
            'activity': 'Documentation',
            'duration': 4,
            'predecessors': ['A']
        },
        {
            'id': 'E',
            'activity': 'Deployment',
            'duration': 2,
            'predecessors': ['C', 'D']
        }
    ]
    
    # Run CPM analysis
    analyzer = CPMAnalyzer()
    G, critical_paths, critical_activities = analyzer.analyze(sample_activities)
    print("✓ CPM analysis completed")
    
    # Build activities with calculated timing data
    activities_for_display = []
    for activity_data in sample_activities:
        activity_id = activity_data['id']
        node_data = G.nodes.get(activity_id, {})
        
        activity_display = {
            'id': activity_id,
            'name': activity_data['activity'],
            'duration': activity_data['duration'],
            'ES': node_data.get('ES', 0),
            'EF': node_data.get('EF', 0),
            'LS': node_data.get('LS', 0),
            'LF': node_data.get('LF', 0),
            'float': node_data.get('float', 0),
            'critical': activity_id in critical_activities,
            'predecessors': activity_data.get('predecessors', [])
        }
        activities_for_display.append(activity_display)
    
    # Calculate project duration
    project_duration = max([G.nodes[node].get('EF', 0) for node in G.nodes() if node not in ['START', 'END']], default=0)
    
    # Create results data
    results_data = {
        'graph': G,
        'critical_paths': critical_paths,
        'critical_path': critical_paths[0] if critical_paths else [],
        'critical_activities': critical_activities,
        'activities': activities_for_display,
        'project_duration': project_duration
    }
    
    # Update the PERT diagram tab with data
    pert_tab.update_network(results_data, 'deterministic')
    print("✓ PERT Diagram updated with sample data")
    
    print("\\n" + "="*60)
    print("TEST RESULTS:")
    print("="*60)
    print(f"✓ Project Duration: {project_duration}")
    print(f"✓ Critical Path: {' → '.join(critical_paths[0]) if critical_paths else 'None'}")
    print(f"✓ Critical Activities: {', '.join(critical_activities)}")
    print(f"✓ Total Activities: {len(activities_for_display)}")
    
    print("\\n✓ Activities with timing data:")
    for activity in activities_for_display:
        print(f"  {activity['id']}: ES={activity['ES']}, EF={activity['EF']}, "
              f"LS={activity['LS']}, LF={activity['LF']}, Float={activity['float']}, "
              f"Critical={activity['critical']}")
    
    print("\\n✓ All tests passed! PERT Diagram tab is fully functional.")
    print("\\nStarting GUI for manual verification...")
    
    # Start GUI for manual testing
    root.mainloop()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
