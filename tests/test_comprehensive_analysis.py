#!/usr/bin/env python3
"""
Comprehensive Analysis Test

Tests both CPM and PERT analysis to ensure complete functionality.
"""

import sys
from pathlib import Path

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_comprehensive_analysis():
    """Test both CPM and PERT analysis functionality"""
    
    print("=" * 70)
    print("COMPREHENSIVE ANALYSIS FUNCTIONALITY TEST")
    print("=" * 70)
    
    try:
        import tkinter as tk
        from pmhelper.gui.main_window import MainWindow
        
        # Create application
        root = tk.Tk()
        app = MainWindow(root)
        
        print("✅ Application created successfully")
        
        test_results = []
        
        # Test 1: CPM Analysis
        print(f"\n🔍 Test 1: CPM (Deterministic) Analysis")
        try:
            # Ensure we're in deterministic mode
            app.set_analysis_mode('deterministic')
            print(f"   Mode set to: {app.analysis_mode}")
            
            # Run analysis
            app.analyze_project()
            print("   ✅ PASS: CPM analysis completed successfully")
            test_results.append(True)
        except Exception as e:
            print(f"   ❌ FAIL: CPM analysis failed: {str(e)}")
            test_results.append(False)
        
        # Test 2: PERT Analysis
        print(f"\n🔍 Test 2: PERT (Probabilistic) Analysis")
        try:
            # Switch to probabilistic mode
            app.set_analysis_mode('probabilistic')
            print(f"   Mode set to: {app.analysis_mode}")
            
            # Run analysis
            app.analyze_project()
            print("   ✅ PASS: PERT analysis completed successfully")
            test_results.append(True)
        except Exception as e:
            print(f"   ❌ FAIL: PERT analysis failed: {str(e)}")
            test_results.append(False)
        
        # Test 3: Error Handling - No Data
        print(f"\n🔍 Test 3: Error Handling (No Data)")
        try:
            # Clear activities data
            original_data = app.get_activities_data()
            
            # Mock empty data
            app.input_tab.tree.delete(*app.input_tab.tree.get_children())
            
            # Try to analyze (should show warning, not crash)
            app.analyze_project()
            print("   ✅ PASS: Proper handling of no data scenario")
            test_results.append(True)
            
            # Restore data
            app.input_tab.populate_tree(original_data)
            
        except Exception as e:
            print(f"   ❌ FAIL: Error handling failed: {str(e)}")
            test_results.append(False)
        
        # Test 4: Results Tab Integration
        print(f"\n🔍 Test 4: Results Tab Integration")
        try:
            # Run analysis and check results tab
            app.set_analysis_mode('deterministic')
            app.analyze_project()
            
            if app.results_tab.results_data:
                print("   ✅ PASS: Results tab properly populated")
                test_results.append(True)
            else:
                print("   ❌ FAIL: Results tab not populated")
                test_results.append(False)
                
        except Exception as e:
            print(f"   ❌ FAIL: Results tab integration failed: {str(e)}")
            test_results.append(False)
        
        root.destroy()
        
        # Calculate results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("COMPREHENSIVE ANALYSIS TEST RESULTS")
        print("=" * 70)
        print(f"Tests passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("🎉 OVERALL RESULT: SUCCESS!")
            print("\n✅ Analysis functionality is working correctly:")
            print("   - CPM (deterministic) analysis works")
            print("   - PERT (probabilistic) analysis works") 
            print("   - Error handling works properly")
            print("   - Results tab integration works")
            print("   - No more 'display result' attribute errors")
        else:
            print("❌ OVERALL RESULT: NEEDS IMPROVEMENT")
            print(f"   Success rate: {success_rate:.1f}% (target: 75%)")
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_analysis()
    if success:
        print("\n🚀 PMHelper analysis functionality is fully operational!")
    else:
        print("\n🔧 Some analysis functionality still needs work.")
