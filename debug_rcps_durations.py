#!/usr/bin/env python3
"""
Debug the actual RCPS durations and crashing be    # Theoretical CPM (no resource constraints)
    cpm_duration = 5 + 7 + 8 + 4 + 3  # A->C->F->H->I critical path
    print(f"   📐 Theoretical CPM duration: {cpm_duration}")ior
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.pmhelper.gui.tabs.rcps_crashing_tab_gui import RCPSCrashingTabGUI
from pmhelper.gui.tabs.project_crashing_core import RCPSProjectCrashing, CrashingStrategy, OptimizationObjective

def debug_rcps_durations():
    print("🕰️ DEBUGGING RCPS DURATIONS AND CRASHING")
    print("="*80)
    
    # Create mock widgets
    class MockWidget:
        def config(self, **kwargs): pass
        def delete(self, *args): pass
        def insert(self, *args): pass
        def get(self, *args): return ""
        def pack(self, **kwargs): pass
        def grid(self, **kwargs): pass
        
    class MockParent:
        def winfo_toplevel(self): return self
        def state(self): return "normal"
        def attributes(self, *args): pass
        def title(self, *args): pass
        
    mock_widgets = {
        'parent': MockParent(),
        'summary_text': MockWidget(),
        'log_text': MockWidget(),
        'metrics_text': MockWidget(),
        'result_frame': MockWidget()
    }
    
    # Create RCPS crashing tab
    rcps_crashing_tab = RCPSCrashingTabGUI(**mock_widgets)
    
    print("1. 📊 Checking RCPS data availability...")
    # Simulate that we have RCPS data available
    from src.pmhelper.gui.tabs.rcps_tab import RCPSTab
    
    # Mock RCPS tab with data
    rcps_tab_mock = MockWidget()
    rcps_tab_mock.rcps_analyzer = None  # We'll check this
    rcps_tab_mock.rcps_network_graph = None
    rcps_tab_mock.rcps_table_data = None
    
    # Check if the GUI can find RCPS data
    try:
        has_data = rcps_crashing_tab.validate_rcps_data()
        print(f"   RCPS data validation: {'✅' if has_data else '❌'}")
    except Exception as e:
        print(f"   ❌ Error validating RCPS data: {e}")
    
    # Manual check from our previous tests
    print("\n2. 🔍 Manual RCPS analysis...")
    sample_data = {
        'A': {'name': 'Design Phase', 'duration': 5, 'predecessors': '', 'resource': 2, 'crash_cost': 100, 'min_duration': 3},
        'B': {'name': 'Requirements Analysis', 'duration': 3, 'predecessors': '', 'resource': 1, 'crash_cost': 150, 'min_duration': 2},
        'C': {'name': 'Architecture Design', 'duration': 7, 'predecessors': 'A,B', 'resource': 3, 'crash_cost': 200, 'min_duration': 4},
        'D': {'name': 'Database Design', 'duration': 5, 'predecessors': 'C', 'resource': 1, 'crash_cost': 120, 'min_duration': 3},
        'E': {'name': 'Frontend Development', 'duration': 6, 'predecessors': 'C', 'resource': 4, 'crash_cost': 180, 'min_duration': 4},
        'F': {'name': 'Backend Development', 'duration': 8, 'predecessors': 'C', 'resource': 5, 'crash_cost': 250, 'min_duration': 5},
        'G': {'name': 'Testing', 'duration': 3, 'predecessors': 'D', 'resource': 2, 'crash_cost': 90, 'min_duration': 2},
        'H': {'name': 'Deployment', 'duration': 4, 'predecessors': 'E,F', 'resource': 1, 'crash_cost': 160, 'min_duration': 2},
        'I': {'name': 'Documentation', 'duration': 3, 'predecessors': 'G,H', 'resource': 2, 'crash_cost': 110, 'min_duration': 2}
    }
    
    # Test what durations we get
    print("   Sample project durations:")
    
    # Theoretical CPM (no resource constraints)
    cpm_duration = 5 + 7 + 8 + 4 + 3  # A->C->F->H->I critical path
    print(f"   📐 Theoretical CPM duration: {cpm_duration}")
    
    # Resource-constrained (this would be much longer)
    print(f"   🎯 Resource-constrained duration: Would be calculated by RCPS")
    
    # From our test results, RCPS duration was 33
    rcps_duration = 33
    print(f"   📊 Actual RCPS duration (from tests): {rcps_duration}")
    
    print("\n3. 💡 The Issue Analysis:")
    print("   The RCPS crashing is designed to work on resource-constrained schedules.")
    print("   In a resource-constrained project:")
    print(f"   - CPM duration: ~{cpm_duration} (theoretical)")
    print(f"   - RCPS duration: {rcps_duration} (actual with resource limits)")
    print("   - Crashing target: User probably expects to crash from CPM duration")
    print("   - But RCPS crashing works from RCPS duration")
    
    print(f"\n4. 🎯 Testing different target durations:")
    
    targets_to_test = [30, 25, 20, 15]
    
    for target in targets_to_test:
        if target >= rcps_duration:
            print(f"   Target {target}: ⚠️  Already shorter than RCPS duration ({rcps_duration})")
        else:
            reduction = rcps_duration - target
            print(f"   Target {target}: 🎯 Needs {reduction} time units reduction")
    
    print(f"\n💡 CONCLUSION:")
    print(f"   The user likely wants to crash from theoretical CPM duration ({cpm_duration}),")
    print(f"   but RCPS crashing works from resource-constrained duration ({rcps_duration}).")
    print(f"   Target durations like 25 are very aggressive for RCPS (needs 8 unit reduction)!")

if __name__ == "__main__":
    debug_rcps_durations()
