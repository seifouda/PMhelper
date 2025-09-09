#!/usr/bin/env python3
"""
Simple Phase 1 Integration Test

Direct test of the foundation methods in the integrated file.
"""

import sys
import os
import inspect

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_methods():
    """Test the foundation methods directly."""
    try:
        from pmhelper.gui.tabs.project_crashing_core import RCPSProjectCrashing
        
        print("🔍 Direct Method Check")
        print("=" * 30)
        
        # Check all methods in the class
        all_methods = [name for name, method in inspect.getmembers(RCPSProjectCrashing, predicate=inspect.isfunction)]
        
        print(f"Total methods found: {len(all_methods)}")
        
        target_methods = [
            'generate_rcps_schedule_for_graph',
            'analyze_activity_status',
            'evaluate_crash_candidates'
        ]
        
        for method in target_methods:
            if method in all_methods:
                print(f"✅ {method} - FOUND")
            else:
                print(f"❌ {method} - NOT FOUND")
        
        print("\nAll methods in class:")
        for method in sorted(all_methods):
            if not method.startswith('_'):  # Skip private methods
                print(f"  - {method}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_methods()
