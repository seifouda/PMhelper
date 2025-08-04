#!/usr/bin/env python3

import sys
from pathlib import Path
import math
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pmhelper.core.pert_analyzer import PERTAnalyzer
from pmhelper.utils.file_handlers import FileHandler

def test_variance_with_different_datasets():
    """Test variance calculation with different PERT datasets"""
    print("=" * 80)
    print("VARIANCE CALCULATION TEST WITH MULTIPLE DATASETS")
    print("=" * 80)
    
    datasets = ['pert_test.csv', 'exam_pert.csv']
    
    for dataset in datasets:
        try:
            print(f"\n{'='*50}")
            print(f"Testing with {dataset}")
            print(f"{'='*50}")
            
            # Load data
            file_handler = FileHandler()
            activities_data = file_handler.load_csv(dataset)
            
            print(f"Loaded {len(activities_data)} activities")
            
            # Run analysis
            analyzer = PERTAnalyzer()
            G, critical_paths, critical_activities = analyzer.analyze(activities_data)
            
            critical_path = critical_paths[0] if critical_paths else []
            print(f"Critical Path: {critical_path}")
            
            # Manual calculation
            manual_variance = 0
            print(f"\nCritical Path Activity Variances:")
            for activity_id in critical_path:
                if activity_id not in ['START', 'END']:
                    if activity_id in G.nodes:
                        variance = G.nodes[activity_id]['variance']
                        manual_variance += variance
                        
                        # Get original data for verification
                        for act_data in activities_data:
                            if act_data.get('id') == activity_id:
                                o = float(act_data.get('optimistic', 0))
                                p = float(act_data.get('pessimistic', 0))
                                expected_variance = ((p - o) / 6) ** 2
                                print(f"  {activity_id}: {variance:.3f} (expected: {expected_variance:.3f})")
                                break
            
            manual_std_dev = math.sqrt(manual_variance)
            
            print(f"\nResults:")
            print(f"  Manual Variance: {manual_variance:.3f}")
            print(f"  Manual Std Dev: {manual_std_dev:.3f}")
            print(f"  Analyzer Variance: {analyzer.project_variance:.3f}")
            print(f"  Analyzer Std Dev: {analyzer.project_std:.3f}")
            
            # Verification
            variance_match = abs(manual_variance - analyzer.project_variance) < 0.001
            std_dev_match = abs(manual_std_dev - analyzer.project_std) < 0.001
            
            print(f"\nVerification:")
            print(f"  Variance Match: {'✅' if variance_match else '❌'}")
            print(f"  Std Dev Match: {'✅' if std_dev_match else '❌'}")
            
            # Test get_project_statistics
            stats = analyzer.get_project_statistics()
            if stats:
                print(f"\nget_project_statistics():")
                print(f"  variance: {stats.get('variance', 'MISSING')}")
                print(f"  std_deviation: {stats.get('std_deviation', 'MISSING')}")
                print(f"  expected_duration: {stats.get('expected_duration', 'MISSING')}")
            
        except FileNotFoundError:
            print(f"Dataset {dataset} not found, skipping...")
        except Exception as e:
            print(f"Error with {dataset}: {e}")

if __name__ == "__main__":
    test_variance_with_different_datasets()
