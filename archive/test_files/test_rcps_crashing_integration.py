#!/usr/bin/env python3
"""
RCPS Crashing Feature Integration Test

This script tests the complete RCPS crashing feature integration.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_rcps_crashing_imports():
    """Test that all RCPS crashing components can be imported"""
    print("Testing RCPS Crashing imports...")
    
    try:
        # Test core components
        from src.pmhelper.core.rcps_analyzer import RCPSAnalyzer
        print("✓ RCPSAnalyzer imported successfully")
        
        from src.pmhelper.gui.tabs.project_crashing_core import RCPSProjectCrashing
        print("✓ RCPSProjectCrashing imported successfully")
        
        # Test GUI components
        from src.pmhelper.gui.tabs.rcps_crashing_tab import RCPSCrashingTab
        print("✓ RCPSCrashingTab imported successfully")
        
        from src.pmhelper.gui.tabs.rcps_crashing_tab_gui import RCPSCrashingTabGUIManager
        print("✓ RCPSCrashingTabGUIManager imported successfully")
        
        # Test that classes can be instantiated (without actual GUI)
        print("\\nTesting class instantiation...")
        
        # Mock analyzer for testing
        class MockAnalyzer:
            def __init__(self):
                import networkx as nx
                self.graph = nx.DiGraph()
                self.G = self.graph
                self.activities = []
        
        mock_analyzer = MockAnalyzer()
        rcps_analyzer = RCPSAnalyzer(mock_analyzer.graph, resource_limit=5, original_analyzer=mock_analyzer)
        print("✓ RCPSAnalyzer instantiated successfully")
        
        rcps_crashing = RCPSProjectCrashing(rcps_analyzer, resource_limit=5)
        print("✓ RCPSProjectCrashing instantiated successfully")
        
        print("\\n🎉 ALL RCPS CRASHING COMPONENTS IMPORTED AND INSTANTIATED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Import/instantiation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window_integration():
    """Test that main window can import RCPS crashing components"""
    print("\\nTesting main window integration...")
    
    try:
        from src.pmhelper.gui.main_window import MainWindow
        print("✓ MainWindow with RCPS Crashing imported successfully")
        
        # Check that the import includes RCPS crashing tab
        import src.pmhelper.gui.main_window as mw_module
        import inspect
        source = inspect.getsource(mw_module)
        
        if "RCPSCrashingTab" in source:
            print("✓ RCPSCrashingTab import found in MainWindow")
        else:
            print("❌ RCPSCrashingTab import not found in MainWindow")
            return False
            
        if "rcps_crashing_tab" in source:
            print("✓ RCPS Crashing tab instantiation found in MainWindow")
        else:
            print("❌ RCPS Crashing tab instantiation not found in MainWindow")
            return False
            
        print("✓ Main window integration successful")
        return True
        
    except Exception as e:
        print(f"❌ Main window integration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("RCPS CRASHING FEATURE INTEGRATION TEST")
    print("="*60)
    
    # Run tests
    imports_ok = test_rcps_crashing_imports()
    integration_ok = test_main_window_integration()
    
    print("\\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Component Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Main Window Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    if imports_ok and integration_ok:
        print("\\n🎉 RCPS CRASHING FEATURE SUCCESSFULLY INTEGRATED!")
        print("\\nNext steps:")
        print("1. Launch the application: python launch_app.py")
        print("2. Load project data and run RCPS analysis")
        print("3. Use the 'RCPS Crashing' tab to run resource-aware crashing")
        print("4. Compare results with regular crashing tab")
    else:
        print("\\n❌ INTEGRATION FAILED - Please fix the issues above")
    
    print("="*60)
