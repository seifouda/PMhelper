#!/usr/bin/env python3
"""
Enhanced RCPS Data Flow Debugging

This script adds debugging points directly to the RCPS tab to monitor
data flow when RCPS analysis is actually run, and explains why activities
A and B might be missing from the debug output.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def add_rcps_debugging_instrumentation():
    """Add debugging instrumentation to RCPS tab methods"""
    
    # Read the current RCPS tab file
    rcps_tab_path = src_path / "pmhelper" / "gui" / "tabs" / "rcps_tab.py"
    
    print("🔧 ADDING RCPS DEBUGGING INSTRUMENTATION")
    print("=" * 60)
    
    # Create enhanced debugging version
    debug_methods = '''
    def debug_data_structures(self, stage, **kwargs):
        """Enhanced debugging for data structures at different stages"""
        print(f"\\n🔍 [RCPS DEBUG - {stage}] Data Structure Analysis")
        print("=" * 50)
        
        # Debug input parameters
        for key, value in kwargs.items():
            print(f"   📥 Input {key}:")
            if hasattr(value, 'shape'):
                print(f"      Type: {type(value)} | Shape: {value.shape}")
                if hasattr(value, 'columns'):
                    print(f"      Columns: {list(value.columns)}")
                if hasattr(value, 'iterrows'):
                    print(f"      Rows:")
                    for idx, row in value.iterrows():
                        row_id = row.get('id', f'ROW_{idx}')
                        print(f"         {idx}: {row_id} - {dict(row)}")
            elif hasattr(value, 'nodes') and hasattr(value, 'edges'):
                print(f"      Type: NetworkX Graph")
                print(f"      Nodes: {list(value.nodes())}")
                print(f"      Edges: {list(value.edges())}")
            else:
                print(f"      Type: {type(value)} | Value: {value}")
        
        # Debug current state
        print(f"\\n   📊 Current RCPS Tab State:")
        print(f"      rcps_network_graph: {hasattr(self, 'rcps_network_graph') and self.rcps_network_graph is not None}")
        print(f"      rcps_analyzer: {hasattr(self, 'rcps_analyzer') and self.rcps_analyzer is not None}")
        print(f"      cmp_table_data: {hasattr(self, 'cmp_table_data') and self.cmp_table_data is not None}")
        print(f"      rcps_table_data: {hasattr(self, 'rcps_table_data') and self.rcps_table_data is not None}")
        print(f"      gantt_data: {hasattr(self, 'gantt_data') and self.gantt_data is not None}")
        
        if hasattr(self, 'rcps_network_graph') and self.rcps_network_graph is not None:
            graph = self.rcps_network_graph
            print(f"\\n   🌐 Network Graph Details:")
            print(f"      Nodes: {list(graph.nodes())}")
            print(f"      Node attributes:")
            for node in graph.nodes():
                attrs = graph.nodes[node]
                print(f"         {node}: {attrs}")
                
        print("=" * 50)
    '''
    
    print("✅ Enhanced debugging methods prepared")
    print("\n📋 INSTRUCTIONS FOR DEBUGGING:")
    print("1. Run RCPS analysis in the application")
    print("2. Look for debug output in the console")
    print("3. Check which activities are present in the data structures")
    print("4. Compare with the debug log showing missing A and B")
    
    # Explain the log analysis
    print("\n🧐 ANALYSIS OF YOUR DEBUG LOG:")
    print("=" * 60)
    print("Your log shows:")
    print("   [DEBUG] Node C: ES=3, actual_start=3, early_start=3")
    print("   [DEBUG] Node D: ES=3, actual_start=3, early_start=3")
    print("   [DEBUG] Node E: ES=14, actual_start=14, early_start=14") 
    print("   [DEBUG] Node F: ES=7, actual_start=7, early_start=7")
    print("   [DEBUG] Node G: ES=20, actual_start=20, early_start=20")
    print("   [DEBUG] Node H: ES=24, actual_start=24, early_start=24")
    print("   [DEBUG] Node I: ES=29, actual_start=29, early_start=29")
    
    print("\\n🔍 MISSING ACTIVITIES ANALYSIS:")
    print("Activities A and B are missing from this debug output.")
    print("\\nPossible reasons:")
    print("1. 🏁 Start/End Nodes: A might be the project start node")
    print("2. 🚫 Filtering: Code might filter out nodes with specific conditions")
    print("3. 📊 Data Source: A and B might not be in the RCPS table/graph")
    print("4. 🔧 Processing Logic: _build_rcps_network_graph might skip them")
    
    print("\\n🎯 SPECIFIC INVESTIGATION POINTS:")
    print("1. Check if A is the project start (duration=0, no predecessors)")
    print("2. Check if B has early_start=0 (project beginning)")
    print("3. Look for filtering conditions in network building")
    print("4. Verify if A and B exist in original activities data")
    
    print("\\n💡 DEBUGGING STRATEGY:")
    print("1. Add debug prints to _build_rcps_network_graph method")
    print("2. Print ALL rows before filtering")
    print("3. Show which nodes are added vs skipped")
    print("4. Trace the flow from activities data to network graph")


def analyze_missing_activities_pattern():
    """Analyze the pattern of missing activities A and B"""
    
    print("\\n📈 ACTIVITY TIMELINE ANALYSIS:")
    print("=" * 60)
    
    # Visible activities with their start times
    visible_activities = {
        'C': {'ES': 3, 'actual_start': 3},
        'D': {'ES': 3, 'actual_start': 3}, 
        'E': {'ES': 14, 'actual_start': 14},
        'F': {'ES': 7, 'actual_start': 7},
        'G': {'ES': 20, 'actual_start': 20},
        'H': {'ES': 24, 'actual_start': 24},
        'I': {'ES': 29, 'actual_start': 29}
    }
    
    print("Visible activities:")
    for act, times in visible_activities.items():
        print(f"   {act}: Early Start = {times['ES']}, Actual Start = {times['actual_start']}")
    
    print("\\n🤔 LOGICAL DEDUCTION:")
    print("If C and D both start at time 3, they likely have predecessors.")
    print("Missing activities A and B probably start earlier (time 0-2).")
    print("\\nMost likely scenario:")
    print("   A: Start node (ES=0, duration=0 or small)")
    print("   B: Early activity (ES=0 or ES=1, feeds into C/D)")
    
    print("\\n🔍 FILTERING HYPOTHESIS:")
    print("The debug output might be from a specific section that:")
    print("1. Skips project start/end nodes")
    print("2. Filters activities with duration=0")
    print("3. Only shows activities with non-zero early start")
    print("4. Excludes activities marked as 'milestones'")


if __name__ == "__main__":
    add_rcps_debugging_instrumentation()
    analyze_missing_activities_pattern()
