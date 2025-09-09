#!/usr/bin/env python3
"""
Quick test to verify the normal crashing fix works in the application context
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_application_crashing():
    """Test that ProjectCrashing can be instantiated without errors"""
    print("🔧 TESTING APPLICATION CRASHING FIX")
    print("=" * 50)
    
    try:
        from src.pmhelper.gui.tabs.project_crashing_core import ProjectCrashing, CrashingStrategy
        print("✅ Import successful")
        
        # Create mock analyzer
        class MockAnalyzer:
            def __init__(self):
                import networkx as nx
                self.G = nx.DiGraph()
                self.G.add_node('A', duration=5, ES=0, EF=5)
                self.G.add_node('B', duration=3, ES=5, EF=8)
        
        analyzer = MockAnalyzer()
        print("✅ Mock analyzer created")
        
        # Test ProjectCrashing instantiation
        crashing_engine = ProjectCrashing(analyzer)
        print("✅ ProjectCrashing instantiated successfully")
        
        # Check available strategies
        available_strategies = list(crashing_engine.strategies.keys())
        print(f"✅ Available strategies: {[s.value for s in available_strategies]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_application_crashing()
    if success:
        print("\n🎉 Normal crashing should now work in the application!")
    else:
        print("\n❌ There's still an issue that needs to be resolved.")
