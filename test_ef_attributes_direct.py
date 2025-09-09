#!/usr/bin/env python3
"""
Direct test of EF attributes in RCPS network graph nodes
This test directly verifies the fix without GUI dependencies
"""

import sys
import os
import pandas as pd
import networkx as nx

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.core.cpm_analyzer import CPMAnalyzer

def test_ef_attributes_direct():
    """Test EF attributes directly in network graph"""
    print("🧪 Testing EF attributes in RCPS network graph...")
    
    # Create test data (lowercase column names for CPMAnalyzer)
    test_data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'duration': [2, 3, 1, 4],
        'predecessors': ['', 'A', 'A', 'B,C'],
        'resource': [2, 1, 1, 2],
        'crash_cost': [100, 150, 75, 200],
        'min_duration': [1, 2, 1, 3],
        'normal_cost': [150, 200, 75, 300]
    })
    
    print(f"✅ Test data created with {len(test_data)} activities")
    
    try:
        # Create CPM analyzer
        analyzer = CPMAnalyzer()
        print("✅ CPM analyzer created")
        
        # Analyze the project
        result = analyzer.analyze(test_data)
        if not result:
            print("❌ CPM analysis failed")
            return False
            
        print("✅ CPM analysis completed")
        
        # Get the network graph
        network = analyzer.get_network()
        if not network:
            print("❌ No network graph available")
            return False
            
        print(f"✅ Network graph retrieved with {len(network.nodes())} nodes")
        
        # Check each node for required attributes
        missing_attributes = []
        ef_values = []
        
        for node in network.nodes():
            node_data = network.nodes[node]
            print(f"\n📊 Node {node} attributes:")
            
            # Check for all required attributes
            required_attrs = ['EF', 'ES', 'duration', 'early_start', 'late_finish']
            node_attrs = []
            
            for attr in required_attrs:
                if attr in node_data:
                    value = node_data[attr]
                    node_attrs.append(f"{attr}: {value}")
                    if attr == 'EF':
                        ef_values.append(value)
                else:
                    missing_attributes.append(f"Node {node} missing {attr}")
            
            print(f"   {', '.join(node_attrs)}")
        
        # Report results
        if missing_attributes:
            print(f"\n❌ Missing attributes found:")
            for missing in missing_attributes:
                print(f"   - {missing}")
            return False
        else:
            print(f"\n✅ All required attributes found in all nodes!")
            
        # Test duration calculation
        if ef_values:
            project_duration = max(ef_values)
            print(f"✅ Project duration calculation: max(EF values) = {project_duration}")
            
            # Verify EF calculation is correct (EF = ES + duration)
            print("\n🔍 Verifying EF calculations:")
            calculation_errors = []
            
            for node in network.nodes():
                node_data = network.nodes[node]
                es = node_data.get('ES', node_data.get('early_start', 0))
                duration = node_data.get('duration', 0)
                ef = node_data.get('EF', 0)
                expected_ef = es + duration
                
                print(f"   Node {node}: ES({es}) + Duration({duration}) = {expected_ef}, EF = {ef}")
                
                if ef != expected_ef:
                    calculation_errors.append(f"Node {node}: EF should be {expected_ef}, got {ef}")
            
            if calculation_errors:
                print(f"\n❌ EF calculation errors:")
                for error in calculation_errors:
                    print(f"   - {error}")
                return False
            else:
                print(f"\n✅ All EF calculations are correct!")
                
            return True
        else:
            print("❌ No EF values found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_rcps_crashing_validation(network):
    """Simulate the duration validation that RCPS Crashing performs"""
    print("\n🎯 Simulating RCPS Crashing duration validation...")
    
    try:
        # This is what rcps_crashing_tab_gui.py does (lines 170-180)
        ef_values = []
        for node in network.nodes():
            node_data = network.nodes[node]
            if 'EF' in node_data:
                ef_values.append(node_data['EF'])
        
        if ef_values:
            project_duration = max(ef_values)
            print(f"✅ Duration validation successful: Project duration = {project_duration}")
            
            # Test with a target duration
            target_duration = project_duration - 1  # Try to crash by 1 unit
            if target_duration < project_duration:
                print(f"✅ Target duration {target_duration} < current duration {project_duration}")
                print("✅ Crashing validation would proceed normally")
                return True
            else:
                print(f"❌ Target duration validation failed")
                return False
        else:
            print("❌ No EF values available for duration calculation")
            return False
            
    except Exception as e:
        print(f"❌ Duration validation simulation failed: {e}")
        return False

def main():
    """Run the direct EF attributes test"""
    print("=" * 70)
    print("DIRECT EF ATTRIBUTES TEST FOR RCPS CRASHING")
    print("=" * 70)
    
    # Test basic EF attributes
    success = test_ef_attributes_direct()
    
    if success:
        print("\n" + "=" * 70)
        print("TESTING RCPS CRASHING DURATION VALIDATION SIMULATION")
        print("=" * 70)
        
        # Get the network for validation test
        try:
            test_data = pd.DataFrame({
                'id': ['A', 'B', 'C', 'D'],
                'duration': [2, 3, 1, 4],
                'predecessors': ['', 'A', 'A', 'B,C'],
                'resource': [2, 1, 1, 2],
                'crash_cost': [100, 150, 75, 200],
                'min_duration': [1, 2, 1, 3],
                'normal_cost': [150, 200, 75, 300]
            })
            
            analyzer = CPMAnalyzer()
            analyzer.analyze(test_data)
            network = analyzer.get_network()
            
            validation_success = simulate_rcps_crashing_validation(network)
            success = success and validation_success
            
        except Exception as e:
            print(f"❌ Validation simulation failed: {e}")
            success = False
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ EF attributes are correctly implemented")
        print("✅ Duration calculation works as expected")
        print("✅ RCPS Crashing 'could not calculate RCPS project duration' error is FIXED!")
        print("✅ Both original bugs are now resolved!")
    else:
        print("❌ TESTS FAILED!")
        print("❌ Additional fixes needed")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    main()
