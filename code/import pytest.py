import pytest
from unittest import mock
import sys
from .cpm_app import CPMDesktopApp

# code/test_cpm_app.py


# Patch tkinter to avoid opening real GUI windows
with mock.patch.dict(sys.modules, {
    'tkinter': mock.MagicMock(),
    'tkinter.ttk': mock.MagicMock(),
    'tkinter.filedialog': mock.MagicMock(),
    'tkinter.messagebox': mock.MagicMock(),
    'tkinter.scrolledtext': mock.MagicMock(),
    'matplotlib.pyplot': mock.MagicMock(),
    'matplotlib.backends.backend_tkagg': mock.MagicMock(),
    'matplotlib.patches': mock.MagicMock(),
    'tabulate': mock.MagicMock(),
    'networkx': mock.MagicMock(),
    'numpy': mock.MagicMock(),
    'pandas': mock.MagicMock(),
    'PIL.Image': mock.MagicMock(),
    'PIL.ImageTk': mock.MagicMock(),
    'matplotlib.backends.backend_agg': mock.MagicMock(),
    'scipy.stats': mock.MagicMock(),
}):

@pytest.fixture
def app():
    # Mock root window
    root = mock.MagicMock()
    app = CPMDesktopApp(root)
    return app

def test_initialization(app):
    assert hasattr(app, 'root')
    assert hasattr(app, 'notebook')
    assert hasattr(app, 'cpm_analyzer')
    assert hasattr(app, 'pert_analyzer')

def test_load_sample_data(app):
    app.load_sample_data()
    # Should populate the treeview (mocked)
    assert app.analysis_mode == 'deterministic'
    assert app.current_analyzer == app.cpm_analyzer

def test_add_and_delete_row(app):
    initial_count = len(app.tree.get_children())
    app.add_row()
    after_add = len(app.tree.get_children())
    assert after_add == initial_count + 1
    # Select and delete the last row
    last_item = app.tree.get_children()[-1]
    app.tree.selection.return_value = [last_item]
    app.delete_row()
    after_delete = len(app.tree.get_children())
    assert after_delete == initial_count

def test_clear_all(app):
    app.load_sample_data()
    app.clear_all()
    assert app.analysis_mode is None
    assert app.current_analyzer is None
    assert app.mode_label.config.called

def test_switch_modes(app):
    # Deterministic mode
    app.analysis_mode = 'deterministic'
    app.setup_deterministic_tree()
    assert app.analysis_mode == 'deterministic'
    # Probabilistic mode
    app.analysis_mode = 'probabilistic'
    app.setup_probabilistic_tree()
    assert app.analysis_mode == 'probabilistic'

def test_analyze_project_no_data(app):
    app.analysis_mode = 'deterministic'
    app.get_activities_data = mock.MagicMock(return_value=[])
    with mock.patch('tkinter.messagebox.showwarning') as warn:
        app.analyze_project()
        assert warn.called

def test_analyze_project_with_data(app):
    app.analysis_mode = 'deterministic'
    # Provide minimal valid data
    app.get_activities_data = mock.MagicMock(return_value=[
        {'id': 'A', 'activity': 'Task A', 'duration': '5', 'predecessors': '', 'min_duration': '2', 'crash_cost': '100', 'resource_demand': '1', 'normal_cost': '500'}
    ])
    app.cpm_analyzer.analyze = mock.MagicMock(return_value=(mock.Mock(), [], []))
    app.display_results = mock.MagicMock()
    app.generate_network_diagram = mock.MagicMock()
    app.visualize_critical_path_network = mock.MagicMock()
    app.generate_gantt_chart = mock.MagicMock()
    with mock.patch('tkinter.messagebox.showinfo'):
        app.analyze_project()
        assert app.display_results.called
        assert app.generate_network_diagram.called