#!/usr/bin/env python3
"""
RCPS Data Flow Debugging Enhancement

This script adds enhanced debugging to track the RCPS data flow 
and identify why activities A and B are missing from the debug output.
"""

# Enhanced _build_rcps_network_graph method with comprehensive debugging
enhanced_build_method = '''
def _build_rcps_network_graph(self, rcps_table, df_gantt, analyzer):
    """Convert RCPS table back to NetworkX graph with actual start times - ENHANCED DEBUG VERSION"""
    import networkx as nx
    
    print("\\n🔧 [RCPS NETWORK BUILDER] Starting network graph construction...")
    print("=" * 70)
    
    # Debug input parameters
    print(f"📊 INPUT DATA ANALYSIS:")
    print(f"   rcps_table type: {type(rcps_table)}")
    print(f"   rcps_table shape: {rcps_table.shape if hasattr(rcps_table, 'shape') else 'N/A'}")
    print(f"   df_gantt type: {type(df_gantt)}")
    print(f"   analyzer type: {type(analyzer)}")
    
    # Show all rows in RCPS table
    print(f"\\n📋 ALL ROWS IN RCPS TABLE:")
    for idx, row in rcps_table.iterrows():
        row_id = row.get('id', f'ROW_{idx}')
        duration = row.get('duration', 'N/A')
        early_start = row.get('early_start', 'N/A')
        actual_start = row.get('actual_start', 'N/A')
        print(f"   Row {idx}: ID='{row_id}' | Duration={duration} | ES={early_start} | AS={actual_start}")
    
    G = nx.DiGraph()
    nodes_added = []
    nodes_skipped = []
    
    # Add nodes with RCPS-specific attributes
    print(f"\\n🏗️  NODE CONSTRUCTION PROCESS:")
    for idx, row in rcps_table.iterrows():
        row_id = row.get('id', f'ROW_{idx}')
        
        if row_id in ['RA', 'RS']:  # Skip resource rows
            nodes_skipped.append((row_id, "Resource row"))
            print(f"   ⏭️  SKIPPED: {row_id} (Resource row)")
            continue
            
        # This is where we might lose A and B - let's see what happens
        print(f"   🔨 PROCESSING: {row_id}")
        
        node_attrs = {
            'duration': row.get('duration', 0),
            'early_start': row.get('early_start', 0),
            'late_finish': row.get('late_finish', 0),
            'float': row.get('float', 0)
        }
        
        # Add resource information if available
        if 'resource' in row:
            node_attrs['resource'] = row['resource']
        
        # Add actual start time from RCPS if available
        if 'actual_start' in row:
            node_attrs['actual_start'] = row['actual_start']
        else:
            node_attrs['actual_start'] = row.get('early_start', 0)
        
        # Add crash cost information if available in original data
        if hasattr(analyzer, 'activities') and analyzer.activities:
            for activity in analyzer.activities:
                if activity.get('id') == row_id:
                    if 'crash_cost' in activity:
                        node_attrs['crash_cost'] = activity['crash_cost']
                    if 'min_duration' in activity:
                        node_attrs['min_duration'] = activity['min_duration']
                    break
        
        G.add_node(row_id, **node_attrs)
        nodes_added.append(row_id)
        print(f"      ✅ ADDED: {row_id} with attributes: {node_attrs}")
    
    print(f"\\n📈 NODE SUMMARY:")
    print(f"   ✅ Nodes added: {nodes_added}")
    print(f"   ⏭️  Nodes skipped: {nodes_skipped}")
    print(f"   📊 Total nodes in graph: {len(G.nodes())}")
    
    # Rebuild edges from original project dependencies
    edges_added = []
    print(f"\\n🔗 EDGE CONSTRUCTION PROCESS:")
    
    if hasattr(analyzer, 'G') and analyzer.G is not None:
        print(f"   📊 Using analyzer's graph for edges...")
        print(f"   📊 Original graph has {len(analyzer.G.nodes())} nodes and {len(analyzer.G.edges())} edges")
        print(f"   📊 Original graph nodes: {list(analyzer.G.nodes())}")
        
        # Copy edges from original analyzer graph
        for u, v in analyzer.G.edges():
            if u in G.nodes() and v in G.nodes():
                G.add_edge(u, v)
                edges_added.append((u, v))
                print(f"      ✅ EDGE ADDED: {u} → {v}")
            else:
                print(f"      ⏭️  EDGE SKIPPED: {u} → {v} (missing nodes: u_exists={u in G.nodes()}, v_exists={v in G.nodes()})")
                
    elif hasattr(analyzer, 'activities') and analyzer.activities:
        print(f"   📊 Using activities data for edges...")
        print(f"   📊 Activities count: {len(analyzer.activities)}")
        
        # Build edges from activities data
        for activity in analyzer.activities:
            activity_id = activity.get('id')
            predecessors = activity.get('predecessors', [])
            print(f"   🔍 Activity {activity_id}: predecessors = {predecessors}")
            
            if activity_id in G.nodes():
                for pred in predecessors:
                    if pred in G.nodes():
                        G.add_edge(pred, activity_id)
                        edges_added.append((pred, activity_id))
                        print(f"      ✅ EDGE ADDED: {pred} → {activity_id}")
                    else:
                        print(f"      ⏭️  EDGE SKIPPED: {pred} → {activity_id} (predecessor {pred} not in graph)")
            else:
                print(f"      ⏭️  ACTIVITY SKIPPED: {activity_id} (not in graph nodes)")
    else:
        print(f"   ❌ No edge source available!")
        
    print(f"\\n🔗 EDGE SUMMARY:")
    print(f"   ✅ Edges added: {edges_added}")
    print(f"   📊 Total edges in graph: {len(G.edges())}")
    
    # Final graph analysis
    print(f"\\n🎯 FINAL GRAPH ANALYSIS:")
    print(f"   📊 Final nodes: {list(G.nodes())}")
    print(f"   📊 Final edges: {list(G.edges())}")
    
    # Specifically look for A and B
    print(f"\\n🔍 MISSING ACTIVITIES INVESTIGATION:")
    has_A = 'A' in G.nodes()
    has_B = 'B' in G.nodes()
    print(f"   Activity A in graph: {has_A}")
    print(f"   Activity B in graph: {has_B}")
    
    if not has_A:
        print(f"   🚨 ACTIVITY A MISSING - checking original data...")
        if hasattr(analyzer, 'activities'):
            a_in_activities = any(act.get('id') == 'A' for act in analyzer.activities)
            print(f"      A in analyzer.activities: {a_in_activities}")
        a_in_rcps_table = 'A' in rcps_table['id'].values if 'id' in rcps_table.columns else False
        print(f"      A in rcps_table: {a_in_rcps_table}")
        
    if not has_B:
        print(f"   🚨 ACTIVITY B MISSING - checking original data...")
        if hasattr(analyzer, 'activities'):
            b_in_activities = any(act.get('id') == 'B' for act in analyzer.activities)
            print(f"      B in analyzer.activities: {b_in_activities}")
        b_in_rcps_table = 'B' in rcps_table['id'].values if 'id' in rcps_table.columns else False
        print(f"      B in rcps_table: {b_in_rcps_table}")
    
    print(f"\\n✅ [RCPS NETWORK BUILDER] Built RCPS network graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
    print("=" * 70)
    return G
'''

# Enhanced run_rcps method with debugging
enhanced_run_rcps = '''
def run_rcps(self):
    """Execute RCPS analysis with comprehensive error handling - ENHANCED DEBUG VERSION"""
    print("\\n🚀 [RCPS ANALYSIS] Starting RCPS execution...")
    print("=" * 70)
    try:
        # Get input data
        df_gantt = self.main_window.get_activities_data()
        resource_limit = self.resource_limit_var.get()
        priority_rule = self.priority_rule_var.get()
        
        print(f"📊 INPUT VALIDATION:")
        print(f"   Activities data type: {type(df_gantt)}")
        print(f"   Activities shape: {df_gantt.shape if hasattr(df_gantt, 'shape') else 'N/A'}")
        print(f"   Resource limit: {resource_limit}")
        print(f"   Priority rule: {priority_rule}")
        
        # Show all activities before processing
        if hasattr(df_gantt, 'iterrows'):
            print(f"\\n📋 ALL INPUT ACTIVITIES:")
            for idx, row in df_gantt.iterrows():
                activity_id = row.get('id', f'ROW_{idx}')
                duration = row.get('duration', 'N/A')
                predecessors = row.get('predecessors', 'N/A')
                print(f"   Activity {activity_id}: Duration={duration}, Predecessors={predecessors}")
        
        # Continue with validation and analysis...
        self.validate_rcps_inputs(df_gantt, resource_limit, priority_rule)
        
        # Rest of the existing method...
        # [Previous RCPS analysis code continues here]
'''

def install_debugging_enhancements():
    """Instructions for installing the debugging enhancements"""
    print("🛠️  RCPS DEBUGGING ENHANCEMENT READY")
    print("=" * 60)
    print()
    print("📋 TO ENABLE ENHANCED DEBUGGING:")
    print("1. The enhanced methods above show comprehensive data flow tracking")
    print("2. They will help identify exactly where activities A and B disappear")
    print("3. Run RCPS analysis and watch for the detailed debug output")
    print()
    print("🔍 KEY DEBUGGING POINTS:")
    print("- Shows ALL rows in input RCPS table")
    print("- Tracks which nodes are added vs skipped")
    print("- Shows edge construction process")
    print("- Specifically investigates missing activities A and B")
    print("- Compares original analyzer data with final graph")
    print()
    print("💡 EXPECTED FINDINGS:")
    print("The debug output will reveal:")
    print("- Whether A and B exist in the original activities data")
    print("- Whether they're filtered out during node construction")
    print("- Whether they're missing from the RCPS table")
    print("- Whether they're project start/end nodes")
    print()
    print("🎯 NEXT STEPS:")
    print("1. Run the application")
    print("2. Go to RCPS Schedule tab") 
    print("3. Run RCPS analysis")
    print("4. Look for the enhanced debug output")
    print("5. The debug will show exactly why A and B are missing")

if __name__ == "__main__":
    install_debugging_enhancements()
