#!/usr/bin/env python3
"""
Enhanced Project Crashing Integration Module

This module integrates the enhanced project crashing features into the existing
CPMDesktopApp without modifying any existing code.

Usage:
1. Import this module
2. Call integrate_enhanced_crashing(app_instance) 
3. Enhanced features will be added as new tabs
"""

import sys
import os
import traceback
from typing import Optional, Any

# Import the enhanced modules
try:
    from enhanced_project_crashing import (
        EnhancedProjectCrashing,
        EnhancedRCPSProjectCrashing,
        CrashingStrategy,
        OptimizationObjective
    )
    from enhanced_crashing_gui import EnhancedCrashingGUIManager, add_enhanced_crashing_to_app
    ENHANCED_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced crashing modules not available: {e}")
    ENHANCED_MODULES_AVAILABLE = False


def integrate_enhanced_crashing(app_instance) -> Optional[Any]:
    """
    Integrate enhanced project crashing features into existing CPM app
    
    Args:
        app_instance: Instance of CPMDesktopApp
        
    Returns:
        EnhancedCrashingGUIManager instance if successful, None otherwise
    """
    if not ENHANCED_MODULES_AVAILABLE:
        print("❌ Enhanced crashing modules are not available")
        return None
    
    try:
        print("🚀 Integrating Enhanced Project Crashing features...")
        
        # Verify app instance has required attributes
        if not hasattr(app_instance, 'notebook'):
            print("❌ App instance does not have notebook widget")
            return None
        
        # Add enhanced crashing features
        gui_manager = add_enhanced_crashing_to_app(app_instance)
        
        if gui_manager:
            print("✅ Enhanced Project Crashing integration successful!")
            print("📋 New tabs added:")
            print("   - Enhanced Crashing")
            print("   - Enhanced RCPS Crashing") 
            print("   - Results Comparison")
            
            # Add menu items if app has a menu
            if hasattr(app_instance, 'root'):
                try:
                    _add_enhanced_menu_items(app_instance, gui_manager)
                except Exception as e:
                    print(f"⚠️  Menu integration failed (non-critical): {e}")
            
            return gui_manager
        else:
            print("❌ Enhanced crashing integration failed")
            return None
            
    except Exception as e:
        print(f"❌ Integration error: {e}")
        traceback.print_exc()
        return None


def _add_enhanced_menu_items(app_instance, gui_manager):
    """Add enhanced crashing menu items to the existing app"""
    try:
        import tkinter as tk
        
        # Check if app has a menubar
        root = app_instance.root
        
        # Create menubar if it doesn't exist
        if not hasattr(app_instance, 'menubar'):
            app_instance.menubar = tk.Menu(root)
            root.config(menu=app_instance.menubar)
        
        # Add Enhanced Crashing menu
        enhanced_menu = tk.Menu(app_instance.menubar, tearoff=0)
        app_instance.menubar.add_cascade(label="Enhanced Crashing", menu=enhanced_menu)
        
        # Add menu items
        enhanced_menu.add_command(
            label="Run Enhanced CPM Crashing",
            command=gui_manager.run_enhanced_crashing
        )
        enhanced_menu.add_command(
            label="Run Enhanced RCPS Crashing", 
            command=gui_manager.run_enhanced_rcps_crashing
        )
        enhanced_menu.add_separator()
        enhanced_menu.add_command(
            label="Compare All Results",
            command=gui_manager.compare_all_results
        )
        enhanced_menu.add_command(
            label="Generate Report",
            command=gui_manager.generate_comparison_report
        )
        enhanced_menu.add_separator()
        enhanced_menu.add_command(
            label="Clear All Results",
            command=gui_manager.clear_comparison
        )
        
        print("📋 Enhanced menu items added successfully")
        
    except Exception as e:
        print(f"⚠️  Menu creation failed: {e}")


def verify_integration(app_instance) -> bool:
    """
    Verify that enhanced crashing features have been properly integrated
    
    Args:
        app_instance: Instance of CPMDesktopApp
        
    Returns:
        True if integration is successful, False otherwise
    """
    try:
        # Check if enhanced manager exists
        if not hasattr(app_instance, 'enhanced_crashing_manager'):
            return False
        
        manager = app_instance.enhanced_crashing_manager
        
        # Check if manager has required attributes
        required_attributes = [
            'enhanced_engine', 'enhanced_rcps_engine',
            'enhanced_target_duration_var', 'enhanced_strategy_var'
        ]
        
        for attr in required_attributes:
            if not hasattr(manager, attr):
                print(f"❌ Missing attribute: {attr}")
                return False
        
        # Check if tabs were added
        if hasattr(app_instance, 'notebook'):
            tab_count = app_instance.notebook.index("end")
            if tab_count < 3:  # Should have at least original tabs + enhanced tabs
                print(f"❌ Insufficient tabs: {tab_count}")
                return False
        
        print("✅ Integration verification successful")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def get_enhanced_features_info() -> dict:
    """
    Get information about available enhanced features
    
    Returns:
        Dictionary with feature information
    """
    try:
        if not ENHANCED_MODULES_AVAILABLE:
            return {"status": "unavailable", "reason": "Modules not imported"}
        
        features = {
            "status": "available",
            "version": "1.0.0",
            "strategies": [s.value for s in CrashingStrategy],
            "objectives": [o.value for o in OptimizationObjective],
            "capabilities": [
                "Enhanced CPM Crashing with multiple strategies",
                "RCPS-aware project crashing", 
                "Comprehensive resource utilization analysis",
                "Advanced cost-benefit optimization",
                "Multi-objective optimization",
                "Real-time progress tracking",
                "Detailed performance metrics",
                "Result comparison and benchmarking",
                "Export capabilities",
                "Interactive visualizations"
            ],
            "new_tabs": [
                "Enhanced Crashing",
                "Enhanced RCPS Crashing",
                "Results Comparison"
            ]
        }
        
        return features
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'version': '1.0.0',
            'strategies': [],
            'objectives': []
        }

def verify_integration_requirements():
    """
    Verify that all requirements for integration are met
    
    Returns:
        dict: Status of integration requirements
    """
    try:
        requirements = {
            'modules_available': False,
            'gui_ready': False,
            'integration_ready': False,
            'details': {}
        }
        
        # Check if enhanced modules can be imported
        try:
            from enhanced_project_crashing import (
                EnhancedProjectCrashing,
                EnhancedRCPSProjectCrashing,
                CrashingStrategy,
                OptimizationObjective
            )
            requirements['modules_available'] = True
            requirements['details']['enhanced_crashing'] = 'Available'
        except Exception as e:
            requirements['details']['enhanced_crashing'] = f'Error: {e}'
        
        # Check if GUI components can be imported
        try:
            from enhanced_crashing_gui import (
                EnhancedCrashingGUIManager,
                add_enhanced_crashing_to_app
            )
            requirements['gui_ready'] = True
            requirements['details']['gui_components'] = 'Available'
        except Exception as e:
            requirements['details']['gui_components'] = f'Error: {e}'
        
        # Check overall integration readiness
        requirements['integration_ready'] = (
            requirements['modules_available'] and 
            requirements['gui_ready']
        )
        
        # Check tkinter availability
        try:
            import tkinter as tk
            requirements['details']['tkinter'] = 'Available'
        except Exception as e:
            requirements['details']['tkinter'] = f'Error: {e}'
        
        # Check required libraries
        libraries = ['networkx', 'matplotlib', 'numpy']
        for lib in libraries:
            try:
                __import__(lib)
                requirements['details'][lib] = 'Available'
            except ImportError:
                requirements['details'][lib] = 'Missing'
        
        return requirements
        
    except Exception as e:
        return {
            'modules_available': False,
            'gui_ready': False,
            'integration_ready': False,
            'error': str(e),
            'details': {}
        }


def demonstrate_enhanced_features(app_instance):
    """
    Demonstrate enhanced crashing features with sample data
    
    Args:
        app_instance: Instance of CPMDesktopApp
    """
    try:
        if not hasattr(app_instance, 'enhanced_crashing_manager'):
            print("❌ Enhanced features not integrated")
            return
        
        print("🎯 Demonstrating Enhanced Project Crashing Features...")
        
        # Check if analysis has been run
        if not hasattr(app_instance, 'current_analyzer') or not app_instance.current_analyzer:
            print("❌ No analysis data available. Run analysis first.")
            return
        
        if not hasattr(app_instance.current_analyzer, 'G') or not app_instance.current_analyzer.G:
            print("❌ No network graph available. Run analysis first.")
            return
        
        manager = app_instance.enhanced_crashing_manager
        
        # Demo 1: Enhanced CPM Crashing
        print("\n📊 Demo 1: Enhanced CPM Crashing")
        try:
            if manager.enhanced_engine:
                # Get current project duration
                original_duration = max([
                    app_instance.current_analyzer.G.nodes[node]['EF'] 
                    for node in app_instance.current_analyzer.G.nodes()
                ])
                target = original_duration * 0.85  # 15% reduction
                
                print(f"   Original Duration: {original_duration:.1f}")
                print(f"   Target Duration: {target:.1f}")
                print("   Strategy: Lowest Cost")
                
                # Set parameters programmatically
                manager.enhanced_target_duration_var.set(str(target))
                manager.enhanced_strategy_var.set(CrashingStrategy.LOWEST_COST.value)
                manager.enhanced_budget_var.set("5000")
                
                print("   ✅ Parameters set for demo")
                
        except Exception as e:
            print(f"   ❌ Demo 1 failed: {e}")
        
        # Demo 2: RCPS Crashing
        print("\n📊 Demo 2: Enhanced RCPS Crashing")
        try:
            if manager.enhanced_rcps_engine:
                # Set RCPS parameters
                manager.enhanced_rcps_target_duration_var.set(str(target))
                manager.enhanced_rcps_resource_limit_var.set("5")
                manager.enhanced_rcps_strategy_var.set(CrashingStrategy.RESOURCE_AWARE.value)
                
                print(f"   Target Duration: {target:.1f}")
                print("   Resource Limit: 5")
                print("   Strategy: Resource Aware")
                print("   ✅ Parameters set for demo")
                
        except Exception as e:
            print(f"   ❌ Demo 2 failed: {e}")
        
        print("\n🎯 Demo complete! Use the GUI to run the analyses.")
        print("💡 Tip: Try different strategies and compare results using the comparison tab.")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        traceback.print_exc()


def test_enhanced_features(app_instance) -> bool:
    """
    Test enhanced features with minimal sample data
    
    Args:
        app_instance: Instance of CPMDesktopApp
        
    Returns:
        True if tests pass, False otherwise
    """
    try:
        print("🧪 Testing Enhanced Project Crashing Features...")
        
        if not ENHANCED_MODULES_AVAILABLE:
            print("❌ Enhanced modules not available")
            return False
        
        # Create test data
        test_activities = [
            {
                'id': 'A', 'activity': 'Design', 'duration': '4', 'predecessors': '',
                'min_duration': '2', 'crash_cost': '200', 'resource_demand': '1', 'normal_cost': '800'
            },
            {
                'id': 'B', 'activity': 'Build', 'duration': '6', 'predecessors': 'A',
                'min_duration': '3', 'crash_cost': '150', 'resource_demand': '2', 'normal_cost': '900'
            },
            {
                'id': 'C', 'activity': 'Test', 'duration': '3', 'predecessors': 'B',
                'min_duration': '2', 'crash_cost': '300', 'resource_demand': '1', 'normal_cost': '600'
            }
        ]
        
        # Test with temporary analyzer
        from cpm_app import CPMAnalyzer
        
        test_analyzer = CPMAnalyzer()
        test_analyzer.analyze(test_activities)
        
        # Test Enhanced CPM Crashing
        print("   Testing Enhanced CPM Crashing...")
        enhanced_cpm = EnhancedProjectCrashing(test_analyzer)
        result1 = enhanced_cpm.enhanced_crash_project(
            target_duration=10,
            strategy=CrashingStrategy.LOWEST_COST,
            max_iterations=10
        )
        
        if result1.final_duration < result1.original_duration:
            print("   ✅ Enhanced CPM Crashing works")
        else:
            print("   ❌ Enhanced CPM Crashing failed")
            return False
        
        # Test Enhanced RCPS Crashing
        print("   Testing Enhanced RCPS Crashing...")
        enhanced_rcps = EnhancedRCPSProjectCrashing(test_analyzer)
        result2 = enhanced_rcps.enhanced_rcps_crash_project(
            target_duration=10,
            resource_limit=3,
            max_iterations=10
        )
        
        if result2.final_duration < result2.original_duration:
            print("   ✅ Enhanced RCPS Crashing works")
        else:
            print("   ❌ Enhanced RCPS Crashing failed")
            return False
        
        # Test comparison
        print("   Testing result comparison...")
        from enhanced_project_crashing import compare_crashing_results
        comparison = compare_crashing_results([result1, result2])
        
        if comparison and 'total_results' in comparison:
            print("   ✅ Result comparison works")
        else:
            print("   ❌ Result comparison failed")
            return False
        
        print("✅ All enhanced features tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        traceback.print_exc()
        return False


def print_integration_summary():
    """Print summary of integration capabilities"""
    print("\n" + "="*70)
    print("ENHANCED PROJECT CRASHING INTEGRATION SUMMARY")
    print("="*70)
    
    if ENHANCED_MODULES_AVAILABLE:
        print("✅ Status: AVAILABLE")
        
        features = get_enhanced_features_info()
        
        print(f"\n📋 Available Strategies:")
        for strategy in features['strategies']:
            print(f"   • {strategy}")
        
        print(f"\n🎯 Available Objectives:")
        for objective in features['objectives']:
            print(f"   • {objective}")
        
        print(f"\n🔧 Key Capabilities:")
        for capability in features['capabilities']:
            print(f"   • {capability}")
        
        print(f"\n📊 New GUI Tabs:")
        for tab in features['new_tabs']:
            print(f"   • {tab}")
        
        print(f"\n💡 Usage:")
        print("   1. from enhanced_crashing_integration import integrate_enhanced_crashing")
        print("   2. gui_manager = integrate_enhanced_crashing(app_instance)")
        print("   3. Use new tabs in the application!")
        
    else:
        print("❌ Status: NOT AVAILABLE")
        print("   Reason: Required modules could not be imported")
        print("   Solution: Ensure enhanced_project_crashing.py and enhanced_crashing_gui.py are available")
    
    print("="*70)


# Auto-integration for the main app
def auto_integrate_if_possible():
    """
    Automatically integrate enhanced features if main app is running
    """
    try:
        # Try to find the main app instance
        import tkinter as tk
        
        # Look for existing tkinter root windows
        for widget in tk._default_root.winfo_children() if tk._default_root else []:
            if hasattr(widget, 'title') and 'CPM' in str(widget.title()):
                # Found potential CPM app window
                print(f"🔍 Found potential CPM app: {widget.title()}")
                # Could attempt auto-integration here
                break
    except:
        # No existing app found or auto-integration not possible
        pass


if __name__ == "__main__":
    print_integration_summary()
    
    # If running standalone, try to test the enhanced features
    if ENHANCED_MODULES_AVAILABLE:
        print("\n🧪 Running standalone tests...")
        
        # Create a mock app instance for testing
        class MockApp:
            def __init__(self):
                import tkinter as tk
                self.root = tk.Tk()
                self.root.withdraw()  # Hide the window
                self.notebook = None
                self.current_analyzer = None
        
        mock_app = MockApp()
        success = test_enhanced_features(mock_app)
        
        if success:
            print("✅ Standalone tests passed!")
        else:
            print("❌ Standalone tests failed!")
        
        mock_app.root.destroy()
    else:
        print("\n❌ Cannot run tests - enhanced modules not available")
