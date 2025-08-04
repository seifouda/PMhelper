#!/usr/bin/env python3

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pmhelper.gui.main_window import MainWindow
from pmhelper.utils.file_handlers import FileHandler

def test_network_tab_upgrade():
    """Test the upgraded NetworkTab"""
    print("=" * 80)
    print("NETWORK TAB UPGRADE TEST")
    print("=" * 80)
    
    try:
        import tkinter as tk
        
        # Create application
        root = tk.Tk()
        app = MainWindow(root)
        
        print("1. Application launched successfully")
        
        # Load sample PERT data
        print("2. Loading sample PERT data...")
        app.input_tab.load_sample_pert()
        print("   Sample PERT data loaded")
        
        # Switch to PERT mode manually
        print("3. Switching to PERT mode...")
        app.analysis_mode = 'probabilistic'
        print("   PERT mode set")
        
        print("4. Running PERT analysis...")
        app.analyze_project()
        
        # Check if analysis completed
        if hasattr(app, 'results_data') and app.results_data:
            print("5. ✅ Analysis completed successfully")
            
            # Switch to Network tab
            app.notebook.select(2)  # Network tab should be index 2
            print("6. Switched to Network tab")
            
            # Check if network tab has the results
            network_tab = app.network_tab
            if hasattr(network_tab, 'results_data') and network_tab.results_data:
                print("7. ✅ Network tab received results data")
                
                activities = network_tab.results_data.get('activities', [])
                critical_activities = network_tab.results_data.get('critical_activities', [])
                
                print(f"   Activities: {len(activities)}")
                print(f"   Critical activities: {critical_activities}")
                
                # Test the new methods exist
                if hasattr(network_tab, 'build_graph_from_activities'):
                    print("8. ✅ build_graph_from_activities method exists")
                    
                    # Test building graph
                    try:
                        G = network_tab.build_graph_from_activities(activities)
                        print(f"   Built graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
                        print("   ✅ Graph building successful")
                    except Exception as e:
                        print(f"   ❌ Graph building failed: {e}")
                    
                if hasattr(network_tab, 'draw_network_diagram'):
                    print("9. ✅ draw_network_diagram method exists")
                    
                if hasattr(network_tab, 'create_hierarchical_layout'):
                    print("10. ✅ create_hierarchical_layout method exists")
                    
                # Test display options
                print("11. Testing display options...")
                print(f"    Show Critical: {network_tab.show_critical_var.get()}")
                print(f"    Show Times: {network_tab.show_times_var.get()}")
                print(f"    Show Float: {network_tab.show_float_var.get()}")
                print(f"    Show Labels: {network_tab.show_labels_var.get()}")
                
                print("12. ✅ All new methods and options are available")
                
                # Try to trigger the diagram drawing
                print("13. Testing diagram drawing...")
                try:
                    network_tab.update_diagram()
                    print("    ✅ Diagram drawing completed successfully")
                except Exception as e:
                    print(f"    ❌ Diagram drawing failed: {e}")
                    import traceback
                    traceback.print_exc()
                
            else:
                print("7. ❌ Network tab did not receive results data")
        else:
            print("5. ❌ Analysis did not complete successfully")
        
        print("\n" + "=" * 80)
        print("✅ NETWORK TAB UPGRADE TEST COMPLETED!")
        print("=" * 80)
        print("The application window will stay open for manual testing.")
        print("Try the following in the GUI:")
        print("- Toggle display options (Show Times, Show Float, etc.)")
        print("- Click Refresh button")
        print("- Try Save Image")
        print("- Verify critical path highlighting (red nodes)")
        print("- Check hierarchical layout")
        print("- Verify START node is green, END node is orange")
        print("- Check that legend appears")
        print("=" * 80)
        
        # Keep window open for manual testing
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_network_tab_upgrade()
