#!/usr/bin/env python3

import sys
from pathlib import Path
import math

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler

def test_gui_data_flow():
    """Test the complete data flow from analyzer to GUI display"""
    print("=" * 80)
    print("GUI DATA FLOW TEST")
    print("=" * 80)
    
    # Load test PERT data
    file_handler = FileHandler()
    activities_data = file_handler.load_csv('pert_test.csv')
    
    # Simulate MainWindow.analyze_project()
    print("1. Running PERT analysis (simulating MainWindow)...")
    analyzer = PERTAnalyzer()
    G, critical_paths, critical_activities = analyzer.analyze(activities_data)
    
    # Calculate precise expected duration (like MainWindow does)
    critical_path = critical_paths[0] if critical_paths else []
    precise_expected_duration = 0
    if critical_path:
        for activity_id in critical_path:
            if activity_id not in ['START', 'END']:
                for activity_data in activities_data:
                    if activity_data.get('id') == activity_id:
                        opt = float(activity_data.get('optimistic', 0))
                        most = float(activity_data.get('most_likely', 0))
                        pess = float(activity_data.get('pessimistic', 0))
                        precise_expected_duration += (opt + 4 * most + pess) / 6
                        break
    
    # Get statistics from analyzer (like MainWindow does)
    project_variance = analyzer.project_variance
    standard_deviation = analyzer.project_std
    
    # Create results_data (like MainWindow does)
    results_data = {
        'expected_duration': precise_expected_duration,
        'project_variance': project_variance,
        'standard_deviation': standard_deviation,
        'critical_path': critical_path,
        'activities': []  # Would contain activity data
    }
    
    print(f"\n2. MainWindow results_data:")
    print(f"  expected_duration: {results_data['expected_duration']:.2f}")
    print(f"  project_variance: {results_data['project_variance']:.3f}")
    print(f"  standard_deviation: {results_data['standard_deviation']:.3f}")
    
    # Simulate ResultsTab.update_summary() (PERT mode)
    print(f"\n3. ResultsTab summary display simulation:")
    analysis_mode = 'probabilistic'
    
    if analysis_mode == 'probabilistic':
        expected_duration = results_data.get('expected_duration', '--')
        variance = results_data.get('project_variance', '--')
        std_deviation = results_data.get('standard_deviation', '--')
        
        # Format with proper precision (like ResultsTab does)
        if expected_duration != '--':
            expected_duration = f"{expected_duration:.2f}"
        if variance != '--':
            variance = f"{variance:.3f}"
        if std_deviation != '--':
            std_deviation = f"{std_deviation:.3f}"
        
        print(f"  Expected Duration: {expected_duration}")
        print(f"  Project Variance: {variance}")
        print(f"  Standard Deviation: {std_deviation}")
    
    # Manual verification
    print(f"\n4. Manual verification:")
    print(f"  Critical Path: {critical_path}")
    
    manual_variance = 0
    print(f"  Critical path variances:")
    if critical_path:
        for activity_id in critical_path:
            if activity_id not in ['START', 'END']:
                if activity_id in G.nodes:
                    act_variance = G.nodes[activity_id]['variance']
                    manual_variance += act_variance
                    print(f"    {activity_id}: {act_variance:.3f}")
    
    manual_std_dev = math.sqrt(manual_variance)
    print(f"  Manual total variance: {manual_variance:.3f}")
    print(f"  Manual std deviation: {manual_std_dev:.3f}")
    
    # Check if values match
    print(f"\n5. Verification:")
    if abs(project_variance - manual_variance) < 0.001:
        print(f"  ✅ Project variance matches manual calculation")
    else:
        print(f"  ❌ Project variance mismatch: {project_variance:.3f} vs {manual_variance:.3f}")
    
    if abs(standard_deviation - manual_std_dev) < 0.001:
        print(f"  ✅ Standard deviation matches manual calculation")
    else:
        print(f"  ❌ Standard deviation mismatch: {standard_deviation:.3f} vs {manual_std_dev:.3f}")
    
    print(f"\n6. Final GUI Display Values:")
    print(f"  Expected Duration: {expected_duration} days")
    print(f"  Project Variance: {variance}")
    print(f"  Standard Deviation: {std_deviation} days")

if __name__ == "__main__":
    test_gui_data_flow()
