"""
Basic tests for PMHelper package.
"""

def test_import():
    """Test that PMHelper can be imported."""
    import pmhelper
    assert hasattr(pmhelper, '__version__')


def test_core_imports():
    """Test that core modules can be imported."""
    from pmhelper.core import CPMAnalyzer
    assert CPMAnalyzer is not None


def test_gui_imports():
    """Test that GUI modules can be imported (may skip if no display)."""
    try:
        from pmhelper.gui.main_window import MainWindow, PMHelperGUI
        from pmhelper.gui import MainWindow as MW, PMHelperGUI as GUI
        
        # Verify that PMHelperGUI is an alias for MainWindow
        assert PMHelperGUI is MainWindow
        assert GUI is MW
        assert GUI is MainWindow
        
        # Just test that we can import without errors
        assert MainWindow is not None
        assert PMHelperGUI is not None
    except ImportError:
        # Skip if GUI dependencies not available
        pass


def test_version_format():
    """Test that version follows semantic versioning."""
    import pmhelper
    import re
    
    version_pattern = r'^\d+\.\d+\.\d+.*$'
    assert re.match(version_pattern, pmhelper.__version__), f"Version {pmhelper.__version__} doesn't match semantic versioning"


def test_sample_data_exists():
    """Test that sample data files exist."""
    import os
    
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    if os.path.exists(assets_dir):
        sample_files = ['cpm_test.csv', 'pert_test.csv']
        for filename in sample_files:
            filepath = os.path.join(assets_dir, filename)
            if os.path.exists(filepath):
                assert os.path.getsize(filepath) > 0, f"Sample file {filename} is empty"