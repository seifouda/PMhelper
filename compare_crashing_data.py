#!/usr/bin/env python3
"""
Crashing Data Comparison Tool

Compare the data structures and inputs between normal crashing and RCPS crashing
to identify what's missing in RCPS crashing that prevents it from working.
"""

import tkinter as tk
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def compare_crashing_data_inputs():
    """Compare data inputs between normal crashing and RCPS crashing"""
    
    print("🔍 CRASHING DATA COMPARISON ANALYSIS")
    print("=" * 80)
    
    try:
        from pmhelper.gui.main_window import MainWindow
        
        root = tk.Tk()
        app = MainWindow(root)
        
        # Run CPM analysis first
        print("1. 🚀 Running CPM analysis...")
        app.run_cpm_analysis()
        
        # Run RCPS analysis
        print("2. 🚀 Creating and running RCPS analysis...")
        app.show_rcps_tab()
        rcps_tab = app.rcps_tab
        rcps_tab.run_rcps()
        
        print("\n" + "=" * 80)
        print("📊 NORMAL CRASHING DATA ANALYSIS")
        print("=" * 80)
        
        # Analyze normal crashing data
        print("3. 📊 Analyzing NORMAL CRASHING data sources...")
        
        # Check what data normal crashing gets
        if hasattr(app, 'crashing_tab'):
            crashing_tab = app.crashing_tab
        else:
            print("   Creating normal crashing tab...")
            app.show_crashing_tab()
            crashing_tab = app.crashing_tab
        
        print(f"   Normal crashing tab type: {type(crashing_tab)}")
        
        # Check normal crashing data access methods
        print(f"\n   📋 Normal crashing data access methods:")
        
        # Check base analyzer access
        if hasattr(crashing_tab, 'get_base_analyzer'):
            base_analyzer = crashing_tab.get_base_analyzer()
            print(f"   ✅ get_base_analyzer(): {type(base_analyzer)}")
            
            if base_analyzer:
                print(f"      Has activities: {hasattr(base_analyzer, 'activities')}")
                print(f"      Has graph: {hasattr(base_analyzer, 'G')}")
                
                if hasattr(base_analyzer, 'activities'):
                    print(f"      Activities count: {len(base_analyzer.activities)}")
                    print(f"      Activity IDs: {[act.get('id') for act in base_analyzer.activities]}")
                    
                    # Check activity attributes for crashing
                    print(f"\\n   📋 Normal crashing activity attributes:")
                    for i, activity in enumerate(base_analyzer.activities[:3]):  # Show first 3
                        print(f"      Activity {activity.get('id', f'ACT_{i}')}:")
                        for key, value in activity.items():
                            print(f"         {key}: {value}")
                
                if hasattr(base_analyzer, 'G') and base_analyzer.G:
                    print(f"      Graph nodes: {list(base_analyzer.G.nodes())}")
                    print(f"      Graph edges: {list(base_analyzer.G.edges())}")
                    
                    # Check node attributes in graph
                    print(f"\\n   📋 Normal crashing graph node attributes:")
                    for node in list(base_analyzer.G.nodes())[:3]:  # Show first 3
                        attrs = base_analyzer.G.nodes[node]
                        print(f"      Node {node}: {attrs}")
        else:
            print(f"   ❌ get_base_analyzer method not found")
        
        print("\n" + "=" * 80)
        print("📊 RCPS CRASHING DATA ANALYSIS")
        print("=" * 80)
        
        # Analyze RCPS crashing data
        print("4. 📊 Analyzing RCPS CRASHING data sources...")
        
        # Create RCPS crashing tab
        app.show_rcps_crashing_tab()
        rcps_crashing_tab = app.rcps_crashing_tab
        
        print(f"   RCPS crashing tab type: {type(rcps_crashing_tab)}")
        
        # Check RCPS crashing data access methods
        print(f"\\n   📋 RCPS crashing data access methods:")
        
        # Check RCPS analyzer access
        if hasattr(rcps_crashing_tab, 'get_rcps_analyzer'):
            rcps_analyzer = rcps_crashing_tab.get_rcps_analyzer()
            print(f"   ✅ get_rcps_analyzer(): {type(rcps_analyzer)}")
            
            if rcps_analyzer:
                print(f"      Has activities: {hasattr(rcps_analyzer, 'activities')}")
                print(f"      Has graph: {hasattr(rcps_analyzer, 'G')}")
                
                if hasattr(rcps_analyzer, 'activities'):
                    print(f"      Activities count: {len(rcps_analyzer.activities)}")
                    print(f"      Activity IDs: {[act.get('id') for act in rcps_analyzer.activities]}")
                    
                    # Check activity attributes for crashing
                    print(f"\\n   📋 RCPS crashing activity attributes:")
                    for i, activity in enumerate(rcps_analyzer.activities[:3]):  # Show first 3
                        print(f"      Activity {activity.get('id', f'ACT_{i}')}:")
                        for key, value in activity.items():
                            print(f"         {key}: {value}")
                
                if hasattr(rcps_analyzer, 'G') and rcps_analyzer.G:
                    print(f"      Graph nodes: {list(rcps_analyzer.G.nodes())}")
                    print(f"      Graph edges: {list(rcps_analyzer.G.edges())}")
                    
                    # Check node attributes in graph
                    print(f"\\n   📋 RCPS crashing graph node attributes:")
                    for node in list(rcps_analyzer.G.nodes())[:3]:  # Show first 3
                        attrs = rcps_analyzer.G.nodes[node]
                        print(f"      Node {node}: {attrs}")
        else:
            print(f"   ❌ get_rcps_analyzer method not found")
        
        # Check RCPS table data access
        if hasattr(rcps_crashing_tab, 'rcps_tab') and rcps_crashing_tab.rcps_tab:
            rcps_tab_ref = rcps_crashing_tab.rcps_tab
            if hasattr(rcps_tab_ref, 'get_rcps_table_data'):
                rcps_table_data = rcps_tab_ref.get_rcps_table_data()
                print(f"\\n   ✅ RCPS table data access: {type(rcps_table_data)}")
                
                if rcps_table_data is not None:
                    print(f"      Table shape: {rcps_table_data.shape}")
                    print(f"      Table columns: {list(rcps_table_data.columns)}")
                    
                    # Check if table has crashing-required data
                    required_columns = ['id', 'duration', 'early_start', 'actual_start']
                    missing_columns = [col for col in required_columns if col not in rcps_table_data.columns]
                    print(f"      Required columns present: {[col for col in required_columns if col in rcps_table_data.columns]}")
                    if missing_columns:
                        print(f"      ❌ Missing columns: {missing_columns}")
                    
                    # Check for crash cost data
                    has_crash_cost = 'crash_cost' in rcps_table_data.columns
                    has_min_duration = 'min_duration' in rcps_table_data.columns
                    print(f"      Has crash_cost column: {has_crash_cost}")
                    print(f"      Has min_duration column: {has_min_duration}")
                    
                    if not has_crash_cost or not has_min_duration:
                        print(f"      🚨 CRITICAL: Missing crash cost data!")
            else:
                print(f"   ❌ get_rcps_table_data method not found")
        
        print("\n" + "=" * 80)
        print("🔍 CRITICAL DIFFERENCE ANALYSIS")
        print("=" * 80)
        
        print("5. 🎯 Identifying critical differences...")
        
        # Compare the two data sources
        print("\\n📊 COMPARISON SUMMARY:")
        print("┌─────────────────────────┬─────────────────┬─────────────────┐")
        print("│ Data Aspect             │ Normal Crashing │ RCPS Crashing   │")
        print("├─────────────────────────┼─────────────────┼─────────────────┤")
        
        # Analyzer comparison
        normal_analyzer = crashing_tab.get_base_analyzer() if hasattr(crashing_tab, 'get_base_analyzer') else None
        rcps_analyzer = rcps_crashing_tab.get_rcps_analyzer() if hasattr(rcps_crashing_tab, 'get_rcps_analyzer') else None
        
        print(f"│ Analyzer Available      │ {'✅ Yes' if normal_analyzer else '❌ No':<15} │ {'✅ Yes' if rcps_analyzer else '❌ No':<15} │")
        
        # Activities comparison
        normal_activities = normal_analyzer.activities if normal_analyzer and hasattr(normal_analyzer, 'activities') else []
        rcps_activities = rcps_analyzer.activities if rcps_analyzer and hasattr(rcps_analyzer, 'activities') else []
        
        print(f"│ Activities Count        │ {len(normal_activities):<15} │ {len(rcps_activities):<15} │")
        
        # Graph comparison
        normal_graph = normal_analyzer.G if normal_analyzer and hasattr(normal_analyzer, 'G') else None
        rcps_graph = rcps_analyzer.G if rcps_analyzer and hasattr(rcps_analyzer, 'G') else None
        
        print(f"│ Graph Available         │ {'✅ Yes' if normal_graph else '❌ No':<15} │ {'✅ Yes' if rcps_graph else '❌ No':<15} │")
        
        # Crash cost data comparison
        normal_has_crash_cost = False
        rcps_has_crash_cost = False
        
        if normal_activities:
            normal_has_crash_cost = any('crash_cost' in act for act in normal_activities)
        
        if rcps_activities:
            rcps_has_crash_cost = any('crash_cost' in act for act in rcps_activities)
        
        print(f"│ Crash Cost in Activities│ {'✅ Yes' if normal_has_crash_cost else '❌ No':<15} │ {'✅ Yes' if rcps_has_crash_cost else '❌ No':<15} │")
        
        # Check if RCPS table has crash data
        rcps_table_crash_cost = False
        if hasattr(rcps_crashing_tab, 'rcps_tab') and rcps_crashing_tab.rcps_tab:
            table_data = rcps_crashing_tab.rcps_tab.get_rcps_table_data()
            if table_data is not None:
                rcps_table_crash_cost = 'crash_cost' in table_data.columns
        
        print(f"│ Crash Cost in Table     │ {'N/A':<15} │ {'✅ Yes' if rcps_table_crash_cost else '❌ No':<15} │")
        print("└─────────────────────────┴─────────────────┴─────────────────┘")
        
        print("\\n🚨 CRITICAL ISSUES IDENTIFIED:")
        
        issues = []
        
        if not rcps_has_crash_cost and not rcps_table_crash_cost:
            issues.append("❌ RCPS crashing missing crash_cost data")
        
        if not rcps_analyzer:
            issues.append("❌ RCPS analyzer not available")
        
        if not rcps_graph:
            issues.append("❌ RCPS graph not available")
        
        if issues:
            for issue in issues:
                print(f"   {issue}")
        else:
            print("   ✅ No obvious data issues found")
        
        print("\\n💡 RECOMMENDATIONS:")
        
        if not rcps_has_crash_cost and not rcps_table_crash_cost:
            print("   🔧 Add crash_cost and min_duration data to RCPS activities")
            print("   🔧 Ensure crash cost data transfers from normal analyzer to RCPS")
        
        if len(normal_activities) != len(rcps_activities):
            print("   🔧 Verify all activities transfer from normal to RCPS analysis")
        
        print("   🔧 Check ProjectCrashing vs RCPSProjectCrashing initialization")
        print("   🔧 Verify data format compatibility between the two crashing engines")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ ERROR during comparison: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    compare_crashing_data_inputs()
