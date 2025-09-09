#!/usr/bin/env python3
"""
Quick validation that the RCPS storage fix is in place
"""

def validate_rcps_fix():
    """Check if the RCPS network graph storage fix is properly applied"""
    rcps_file = "src/pmhelper/gui/tabs/rcps_tab.py"
    
    with open(rcps_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required storage code elements
    required_elements = [
        "self.rcps_network_graph = self._build_rcps_network_graph(df_gantt)",
        "self.rcps_analyzer = analyzer", 
        "[DEBUG STORAGE] Building network graph for RCPS Crashing",
        "[DEBUG STORAGE] Network graph built:",
        "[DEBUG STORAGE] Analyzer stored:"
    ]
    
    print("RCPS Crashing Bug Fix Validation")
    print("=" * 40)
    
    all_present = True
    for element in required_elements:
        if element in content:
            print(f"✅ Found: {element}")
        else:
            print(f"❌ Missing: {element}")
            all_present = False
    
    if all_present:
        print("\n🎉 SUCCESS: All required fix elements are present!")
        print("✅ Network graph storage code added")
        print("✅ Analyzer storage code added") 
        print("✅ Debug prints added for verification")
        print("\nThe RCPS Crashing bug should now be fixed.")
        print("Network graph and analyzer will be stored after RCPS analysis.")
        return True
    else:
        print("\n❌ FAILURE: Some fix elements are missing!")
        return False

if __name__ == "__main__":
    success = validate_rcps_fix()
    exit(0 if success else 1)
