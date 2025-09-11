#!/usr/bin/env python3
"""
RCPS Crashing Direct Test

Test RCPS crashing directly to see where it fails.
"""

import tkinter as tk
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def test_rcps_crashing_directly():
    """Test RCPS crashing directly to identify the failure point"""
    
    print("🧪 DIRECT RCPS CRASHING TEST")
    print("=" * 60)
    
    try:
        from pmhelper.gui.main_window import MainWindow
        from pmhelper.gui.tabs.project_crashing_core import RCPSProjectCrashing, CrashingStrategy, OptimizationObjective
        
        root = tk.Tk()
        app = MainWindow(root)
        
        # Setup: Run CPM and RCPS analysis
        print("1. 🚀 Setting up data...")
        app.run_cpm_analysis()
        app.show_rcps_tab()
        rcps_tab = app.rcps_tab
        rcps_tab.run_rcps()
        
        # Get RCPS analyzer
        rcps_analyzer = rcps_tab.get_rcps_analyzer()
        resource_limit = rcps_tab.get_resource_limit()
        
        print(f"   ✅ RCPS analyzer: {type(rcps_analyzer)}")
        print(f"   ✅ Resource limit: {resource_limit}")
        
        # Test direct instantiation
        print("\n2. 🔧 Testing RCPSProjectCrashing instantiation...")
        
        try:
            crashing_engine = RCPSProjectCrashing(rcps_analyzer, resource_limit)
            print(f"   ✅ RCPSProjectCrashing created: {type(crashing_engine)}")
            print(f"   ✅ Base analyzer: {type(crashing_engine.base_analyzer)}")
            print(f"   ✅ Resource limit: {crashing_engine.resource_limit}")
        except Exception as e:
            print(f"   ❌ RCPSProjectCrashing instantiation failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test strategy access
        print("\n3. 🎯 Testing strategy access...")
        
        try:
            strategies = crashing_engine.strategies
            print(f"   ✅ Strategies available: {list(strategies.keys())}")
            
            # Test specific strategy
            strategy = CrashingStrategy.LOWEST_COST
            if strategy in strategies:
                print(f"   ✅ Strategy {strategy} is available")
                strategy_method = strategies[strategy]
                print(f"   ✅ Strategy method: {strategy_method}")
            else:
                print(f"   ❌ Strategy {strategy} not found")
                
        except Exception as e:
            print(f"   ❌ Strategy access failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test run method
        print("\n4. 🚀 Testing run method...")
        
        try:
            target_duration = 25
            strategy = CrashingStrategy.LOWEST_COST
            objective = OptimizationObjective.MINIMIZE_COST
            
            print(f"   Parameters:")
            print(f"     Target duration: {target_duration}")
            print(f"     Strategy: {strategy}")
            print(f"     Objective: {objective}")
            
            print(f"   Calling run method...")
            result = crashing_engine.run(
                target_duration=target_duration,
                strategy=strategy,
                objective=objective,
                max_budget=None,
                max_crash_cost=None,
                max_normal_cost=None,
                max_iterations=10  # Limit iterations for testing
            )
            
            print(f"   ✅ Run method completed!")
            print(f"   ✅ Result type: {type(result)}")
            print(f"   ✅ Original duration: {result.original_duration}")
            print(f"   ✅ Final duration: {result.final_duration}")
            print(f"   ✅ Total crash cost: {result.total_crash_cost}")
            print(f"   ✅ Termination reason: {result.termination_reason}")
            
        except Exception as e:
            print(f"   ❌ Run method failed: {e}")
            import traceback
            traceback.print_exc()
        
        root.destroy()
        
        print("\n" + "=" * 60)
        print("🎯 DIRECT TEST SUMMARY:")
        print("If this test passes, the issue is in the GUI integration")
        print("If this test fails, the issue is in the crashing engine itself")
        
    except Exception as e:
        print(f"❌ ERROR during direct test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_rcps_crashing_directly()
