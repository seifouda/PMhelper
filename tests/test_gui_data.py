#!/usr/bin/env python3

import sys
from pathlib import Path
import math

# Add src to path for GUI testing
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Test the main window data preparation
from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler

def test_gui_data_preparation():
    print("Testing GUI Data Preparation")
    print("=" * 50)
    
    # Load test PERT data
    file_handler = FileHandler()
    activities_data = file_handler.load_csv('pert_test.csv')
    
    # Test the PERT analysis
    analyzer = PERTAnalyzer()
    G, critical_paths, critical_activities = analyzer.analyze(activities_data)
    
    # Calculate precise expected duration (like main_window.py does)
    critical_path = critical_paths[0] if critical_paths else []
    precise_expected_duration = 0
    if critical_path:
        for activity_id in critical_path:
            if activity_id not in ['START', 'END']:
                # Find the original activity data to get precise expected_time
                for activity_data in activities_data:
                    if activity_data.get('id') == activity_id:
                        # Calculate precise expected time using PERT formula
                        opt = float(activity_data.get('optimistic', 0))
                        most = float(activity_data.get('most_likely', 0))
                        pess = float(activity_data.get('pessimistic', 0))
                        precise_expected_duration += (opt + 4 * most + pess) / 6
                        break
    
    print(f"Expected Duration for GUI: {precise_expected_duration:.1f}")
    
    # Prepare activities like main_window.py does
    activities_for_display = []
    for activity_data in activities_data[:3]:  # Test first 3
        activity_id = activity_data.get('id', '')
        
        # Get node data from graph
        node_data = G.nodes.get(activity_id, {}) if G else {}
        
        activity_display = {
            'id': activity_id,
            'name': activity_data.get('activity', activity_data.get('name', activity_id)),
            'duration': activity_data.get('duration', 0),
            'ES': node_data.get('ES', 0),
            'EF': node_data.get('EF', 0), 
            'LS': node_data.get('LS', 0),
            'LF': node_data.get('LF', 0),
            'float': node_data.get('float', 0),
            'critical': activity_id in critical_activities,
            'predecessors': activity_data.get('predecessors', '')
        }
        
        # Add PERT-specific data (like main_window.py does)
        opt = activity_data.get('optimistic', 0)
        most = activity_data.get('most_likely', 0)
        pess = activity_data.get('pessimistic', 0)
        expected_time = (float(opt) + 4 * float(most) + float(pess)) / 6
        variance = ((float(pess) - float(opt)) / 6) ** 2
        
        activity_display.update({
            'optimistic': opt,
            'most_likely': most,
            'pessimistic': pess,
            'expected_duration': expected_time,  # Keep precise for any legacy needs
            'expected': math.ceil(expected_time),  # Integer expected duration for display
            'variance': round(variance, 3)
        })
        
        activities_for_display.append(activity_display)
    
    # Test how results_tab.py will display these
    print(f"\nActivity Display Data (how ResultsTab will see it):")
    for activity in activities_for_display:
        print(f"Activity {activity['id']}:")
        print(f"  Expected (statistical): {activity['expected_duration']:.2f}")
        print(f"  Expected (display): {activity['expected']}")
        print(f"  ES: {activity['ES']}, EF: {activity['EF']}")
        print(f"  LS: {activity['LS']}, LF: {activity['LF']}")
        print(f"  Float: {activity['float']}")
        print(f"  Critical: {activity['critical']}")
        print()
    
    # Show what the results tab values tuple will be
    print("Results Tab Values (PERT mode):")
    for activity in activities_for_display:
        values = (
            activity.get('id', ''),
            activity.get('name', ''),
            activity.get('optimistic', ''),
            activity.get('most_likely', ''),
            activity.get('pessimistic', ''),
            str(activity.get('expected', activity.get('duration', 0))),  # Integer expected
            f"{activity.get('variance', 0):.3f}",
            activity.get('ES', ''),
            activity.get('EF', ''),
            activity.get('LS', ''),
            activity.get('LF', ''),
            str(activity.get('float', 0)),  # Integer float
            "Yes" if activity.get('critical', False) else "No"
        )
        print(f"  {values}")

if __name__ == "__main__":
    test_gui_data_preparation()
