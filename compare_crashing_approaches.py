#!/usr/bin/env python3
"""
Compare normal crashing vs RCPS crashing to find the real differences
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def compare_crashing_implementations():
    print("🔍 COMPARING NORMAL vs RCPS CRASHING IMPLEMENTATIONS")
    print("="*80)
    
    print("1. 📊 Let me check what's actually different...")
    
    # Check normal crashing data availability
    print("\n2. 🔍 Checking Normal Crashing Implementation:")
    try:
        from src.pmhelper.gui.tabs.project_crashing_tab_gui import ProjectCrashingTabGUI
        print("   ✅ Normal crashing tab imports successfully")
        
        # Check what analyzer normal crashing uses
        print("   📋 Normal crashing uses: Standard CPM/PERT analyzer")
        print("   📋 Data source: Direct table data converted to NetworkX graph")
        
    except Exception as e:
        print(f"   ❌ Error importing normal crashing: {e}")
    
    print("\n3. 🔍 Checking RCPS Crashing Implementation:")
    try:
        from src.pmhelper.gui.tabs.rcps_crashing_tab_gui import RCPSCrashingTabGUIManager
        print("   ✅ RCPS crashing tab imports successfully")
        
        print("   📋 RCPS crashing uses: RCPSAnalyzer with resource constraints")
        print("   📋 Data source: RCPS tab's analyzer and network graph")
        
    except Exception as e:
        print(f"   ❌ Error importing RCPS crashing: {e}")
    
    print("\n4. 💡 KEY HYPOTHESIS:")
    print("   The issue might be:")
    print("   a) RCPSAnalyzer creates a different graph structure than normal analyzer")
    print("   b) Graph generation is missing in RCPS crashing tab")
    print("   c) Data flow from RCPS tab to RCPS crashing is broken")
    
    print("\n5. 🔧 SOLUTION APPROACHES:")
    print("   APPROACH 1: Bypass RCPSAnalyzer - Use normal analyzer like normal crashing")
    print("   APPROACH 2: Fix RCPSAnalyzer to be compatible with crashing engine")
    print("   APPROACH 3: Convert RCPS data to normal crashing format")
    
    print("\n6. 🎯 RECOMMENDED APPROACH:")
    print("   APPROACH 1 (Bypass) - Most reliable:")
    print("   - Take RCPS table data")
    print("   - Convert it to the same format normal crashing uses")
    print("   - Use the normal ProjectCrashing engine instead of RCPSProjectCrashing")
    print("   - Add graph generation like normal crashing has")
    
    print("\n7. 📋 IMPLEMENTATION PLAN:")
    print("   1. Check how normal crashing converts table data to analyzer")
    print("   2. Replicate this process in RCPS crashing tab")
    print("   3. Use ProjectCrashing instead of RCPSProjectCrashing")
    print("   4. Add graph generation functionality")
    print("   5. Test with the same data structure as normal crashing")

if __name__ == "__main__":
    compare_crashing_implementations()
