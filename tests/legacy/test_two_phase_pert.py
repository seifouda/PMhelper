#!/usr/bin/env python3

import sys
from pathlib import Path
import math

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler

def test_two_phase_pert():
    print("Testing Two-Phase PERT Analysis")
    print("=" * 50)
    
    # Load test PERT data
    file_handler = FileHandler()
    activities_data = file_handler.load_csv('pert_test.csv')
    print(f'Loaded {len(activities_data)} activities from pert_test.csv')
    
    # Show first few activities
    print("\nFirst 3 activities:")
    for i, activity in enumerate(activities_data[:3]):
        opt = activity.get('optimistic', 0)
        most = activity.get('most_likely', 0) 
        pess = activity.get('pessimistic', 0)
        expected = (float(opt) + 4 * float(most) + float(pess)) / 6
        expected_ceil = math.ceil(expected)
        print(f"  {activity.get('id')}: O={opt}, M={most}, P={pess} -> Expected={expected:.2f}, Ceil={expected_ceil}")
    
    # Test the new two-phase analysis
    analyzer = PERTAnalyzer()
    print('\nRunning two-phase PERT analysis...')
    G, critical_paths, critical_activities = analyzer.analyze(activities_data)
    
    print(f'\nPhase 1 - Statistical Results:')
    print(f'  Project Variance: {analyzer.project_variance:.3f}')
    print(f'  Project Std Dev: {analyzer.project_std:.3f}')
    
    print(f'\nPhase 2 - Scheduling Results (Integer-based):')
    print(f'  Critical Path: {critical_paths[0] if critical_paths else "None"}')
    print(f'  Critical Activities: {critical_activities}')
    
    # Check activities to verify integer scheduling values
    print('\nFirst 3 activity scheduling results:')
    for i, node in enumerate(list(G.nodes())[:5]):
        if node not in ['START', 'END']:
            node_data = G.nodes[node]
            es = node_data.get('ES', 0)
            ef = node_data.get('EF', 0) 
            ls = node_data.get('LS', 0)
            lf = node_data.get('LF', 0)
            float_val = node_data.get('float', 0)
            duration = node_data.get('duration', 0)
            print(f'  {node}: Duration={duration}, ES={es}, EF={ef}, LS={ls}, LF={lf}, Float={float_val}')
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    test_two_phase_pert()
