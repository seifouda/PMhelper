"""
Integration tests for optimization GUI components.
Tests module imports and component structure (non-GUI aspects).

Note: Full GUI tests require a display environment and are skipped in headless mode.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def skip_if_no_display():
    """Skip tests if no display is available (headless environment)."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.destroy()
        return False
    except:
        return True


HEADLESS = skip_if_no_display()


class TestModuleImports:
    """Test that optimization GUI modules import successfully."""
    
    def test_optimization_tab_import(self):
        """Test that optimization tab module imports."""
        from pmhelper.gui.tabs import optimization_tab
        assert optimization_tab is not None
    
    def test_optimization_classes_importable(self):
        """Test that main optimization classes can be imported."""
        from pmhelper.gui.tabs.optimization_tab import (
            OptimizationTab,
            TimeCostOptimizationPanel,
            ResourceLevelingPanel,
            MultiObjectivePanel
        )
        
        assert OptimizationTab is not None
        assert TimeCostOptimizationPanel is not None
        assert ResourceLevelingPanel is not None
        assert MultiObjectivePanel is not None
    
    def test_optimization_dependencies_available(self):
        """Test that required dependencies are available."""
        import tkinter as tk
        from tkinter import ttk
        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        # All imports successful
        assert tk is not None
        assert ttk is not None
        assert matplotlib is not None
        assert plt is not None
        assert FigureCanvasTkAgg is not None


@pytest.mark.skipif(HEADLESS, reason="No display available")
class TestOptimizationTabStructure:
    """Test optimization tab structure (requires display)."""
    
    def test_tab_has_required_attributes(self):
        """Test that OptimizationTab has required attributes."""
        from pmhelper.gui.tabs.optimization_tab import OptimizationTab
        
        # Check class has required methods
        assert hasattr(OptimizationTab, '__init__')


@pytest.mark.skipif(HEADLESS, reason="No display available")
class TestPanelStructure:
    """Test panel structures (requires display)."""
    
    def test_time_cost_panel_structure(self):
        """Test that TimeCostOptimizationPanel has required attributes."""
        from pmhelper.gui.tabs.optimization_tab import TimeCostOptimizationPanel
        
        assert hasattr(TimeCostOptimizationPanel, '__init__')
    
    def test_resource_panel_structure(self):
        """Test that ResourceLevelingPanel has required attributes."""
        from pmhelper.gui.tabs.optimization_tab import ResourceLevelingPanel
        
        assert hasattr(ResourceLevelingPanel, '__init__')
    
    def test_multi_objective_panel_structure(self):
        """Test that MultiObjectivePanel has required attributes."""
        from pmhelper.gui.tabs.optimization_tab import MultiObjectivePanel
        
        assert hasattr(MultiObjectivePanel, '__init__')


class TestBackendIntegration:
    """Test that GUI components can access backend modules."""
    
    def test_cost_optimization_available(self):
        """Test that cost optimization module is available."""
        from pmhelper.core import cost_optimization
        assert cost_optimization is not None
        assert hasattr(cost_optimization, 'TimeCostOptimizer')
    
    def test_resource_leveling_available(self):
        """Test that resource leveling module is available."""
        from pmhelper.core import resource_leveling
        assert resource_leveling is not None
        assert hasattr(resource_leveling, 'ResourceLevelingFactory')
    
    def test_multi_objective_available(self):
        """Test that multi-objective module is available."""
        from pmhelper.core import multi_objective
        assert multi_objective is not None
        assert hasattr(multi_objective, 'MultiObjectiveOptimizer')
    
    def test_visualization_modules_available(self):
        """Test that visualization modules are available."""
        from pmhelper.core import cost_visualizations
        from pmhelper.core import resource_visualizations
        from pmhelper.core import multi_objective_visualizations
        
        assert cost_visualizations is not None
        assert resource_visualizations is not None
        assert multi_objective_visualizations is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

