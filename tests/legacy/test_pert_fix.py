#!/usr/bin/env python3
"""
PERT Analysis Debug Script

Verify that ProbabilityTab now has the update_analysis method and test PERT workflow
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_tab_methods():
    """Test that all tabs have required update methods"""
    print("=" * 80)
    print("TAB METHOD VERIFICATION")
    print("=" * 80)
    
    try:
        # Import tab classes
        from pmhelper.gui.tabs.results_tab import ResultsTab
        from pmhelper.gui.tabs.network_tab import NetworkTab
        from pmhelper.gui.tabs.gantt_tab import GanttTab
        from pmhelper.gui.tabs.probability_tab import ProbabilityTab
        
        # Test each tab for required methods
        tabs_to_test = [
            ('ResultsTab', ResultsTab, 'update_results'),
            ('NetworkTab', NetworkTab, 'update_network'),
            ('GanttTab', GanttTab, 'update_gantt'),
            ('ProbabilityTab', ProbabilityTab, 'update_analysis')  # This should now exist
        ]
        
        all_good = True
        
        for tab_name, tab_class, expected_method in tabs_to_test:
            print(f"\n{tab_name}:")
            
            # Check if the expected method exists
            if hasattr(tab_class, expected_method):
                print(f"  ✅ {expected_method}() - Available")
                
                # Check method signature
                import inspect
                try:
                    sig = inspect.signature(getattr(tab_class, expected_method))
                    print(f"     Signature: {expected_method}{sig}")
                except:
                    print(f"     Signature: {expected_method}(signature unavailable)")
            else:
                print(f"  ❌ {expected_method}() - Missing")
                all_good = False
            
            # Show other update methods
            update_methods = [m for m in dir(tab_class) if 'update' in m.lower() and not m.startswith('_') and callable(getattr(tab_class, m))]
            if update_methods:
                print(f"     Other update methods: {update_methods}")
        
        print(f"\n{'='*80}")
        if all_good:
            print("🎉 SUCCESS: All tabs have their required update methods!")
        else:
            print("❌ FAILED: Some tabs are missing required methods")
            
        return all_good
        
    except Exception as e:
        print(f"ERROR: Failed to test tab methods: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pert_analysis_flow():
    """Test the PERT analysis workflow with mock data"""
    print("\\n" + "=" * 80)
    print("PERT ANALYSIS FLOW TEST")
    print("=" * 80)
    
    try:
        # Create sample PERT data
        sample_pert_data = [
            {'id': 'A', 'activity': 'Design', 'optimistic': 2, 'most_likely': 4, 'pessimistic': 8, 'predecessors': ''},
            {'id': 'B', 'activity': 'Code', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 9, 'predecessors': 'A'},
            {'id': 'C', 'activity': 'Test', 'optimistic': 1, 'most_likely': 2, 'pessimistic': 4, 'predecessors': 'B'},
        ]
        
        print(f"Sample PERT data created: {len(sample_pert_data)} activities")
        
        # Test PERT analyzer
        from pmhelper.core.pert_analyzer import PERTAnalyzer
        
        analyzer = PERTAnalyzer()
        print("✅ PERT analyzer created")
        
        # Test analysis
        G, critical_paths, critical_activities = analyzer.analyze(sample_pert_data)
        print("✅ PERT analysis completed")
        print(f"   Critical path: {' → '.join(critical_paths[0]) if critical_paths else 'None'}")
        print(f"   Project variance: {analyzer.project_variance}")
        print(f"   Project std dev: {analyzer.project_std}")
        
        # Create mock results_data structure
        mock_results_data = {
            'activities': [],
            'project_duration': 11,  # Example expected duration
            'project_variance': analyzer.project_variance,
            'standard_deviation': analyzer.project_std,
            'critical_path': critical_paths[0] if critical_paths else [],
            'critical_activities': critical_activities
        }
        
        # Test ProbabilityTab update_analysis method
        from pmhelper.gui.tabs.probability_tab import ProbabilityTab
        
        # Create a minimal mock notebook for testing
        class MockNotebook:
            def add(self, frame, text): pass
        
        class MockMainWindow:
            pass
            
        prob_tab = ProbabilityTab(MockNotebook(), MockMainWindow())
        print("✅ ProbabilityTab created")
        
        # Test the update_analysis method
        prob_tab.update_analysis(mock_results_data)
        print("✅ ProbabilityTab.update_analysis() called successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ PERT analysis flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("PERT ANALYSIS FIX VERIFICATION")
    print("=" * 80)
    
    success1 = test_tab_methods()
    success2 = test_pert_analysis_flow()
    
    print("\\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        print("✅ ProbabilityTab.update_analysis() method exists")
        print("✅ PERT analysis workflow works")
        print("✅ Ready for PERT analysis in GUI")
    else:
        print("❌ SOME TESTS FAILED")
        if not success1:
            print("❌ Tab method verification failed")
        if not success2:
            print("❌ PERT analysis flow test failed")

if __name__ == "__main__":
    main()
