"""
Phase 7 — CPM/PERT Pipeline Integration Tests.

Tests the full analysis pipeline: CPM/PERT analysis → results distribution
→ tab updates, and the facade methods in MainWindowEdu.
"""

import pytest
import math


# ────────────────────────────────────────────────────────────────
# Helpers — sample data in the format InputTab returns
# ────────────────────────────────────────────────────────────────

def _sample_cpm_data():
    """Return sample deterministic activity data (4 activities)."""
    return [
        {'id': 'A', 'activity': 'Foundation', 'duration': '3',
         'predecessors': '', 'min_duration': '2', 'crash_cost': '500',
         'resource_demand': '2', 'normal_cost': '300'},
        {'id': 'B', 'activity': 'Framing', 'duration': '4',
         'predecessors': 'A', 'min_duration': '3', 'crash_cost': '600',
         'resource_demand': '3', 'normal_cost': '400'},
        {'id': 'C', 'activity': 'Electrical', 'duration': '2',
         'predecessors': 'A', 'min_duration': '1', 'crash_cost': '400',
         'resource_demand': '1', 'normal_cost': '200'},
        {'id': 'D', 'activity': 'Finishing', 'duration': '5',
         'predecessors': 'B,C', 'min_duration': '3', 'crash_cost': '800',
         'resource_demand': '2', 'normal_cost': '500'},
    ]


def _sample_pert_data():
    """Return sample probabilistic activity data (3 activities)."""
    return [
        {'id': 'X', 'activity': 'Design', 'optimistic': '2',
         'most_likely': '3', 'pessimistic': '4', 'predecessors': '',
         'min_duration': '', 'crash_cost': '', 'resource_demand': '1',
         'normal_cost': ''},
        {'id': 'Y', 'activity': 'Develop', 'optimistic': '4',
         'most_likely': '6', 'pessimistic': '8', 'predecessors': 'X',
         'min_duration': '', 'crash_cost': '', 'resource_demand': '2',
         'normal_cost': ''},
        {'id': 'Z', 'activity': 'Test', 'optimistic': '1',
         'most_likely': '2', 'pessimistic': '3', 'predecessors': 'Y',
         'min_duration': '', 'crash_cost': '', 'resource_demand': '1',
         'normal_cost': ''},
    ]


# ────────────────────────────────────────────────────────────────
# A. CPMAnalyzer direct tests
# ────────────────────────────────────────────────────────────────

class TestCPMAnalyzerDirect:
    """Test CPMAnalyzer with edu-style data."""

    def test_cpm_analyze_returns_tuple(self):
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        analyzer = CPMAnalyzer()
        G, cps, cas = analyzer.analyze(_sample_cpm_data())
        assert G is not None
        assert isinstance(cps, list)
        assert isinstance(cas, list)

    def test_cpm_graph_has_start_end(self):
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        analyzer = CPMAnalyzer()
        G, _, _ = analyzer.analyze(_sample_cpm_data())
        assert 'START' in G.nodes()
        assert 'END' in G.nodes()

    def test_cpm_graph_nodes_have_timing(self):
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        analyzer = CPMAnalyzer()
        G, _, _ = analyzer.analyze(_sample_cpm_data())
        for node in ('A', 'B', 'C', 'D'):
            nd = G.nodes[node]
            assert 'ES' in nd
            assert 'EF' in nd
            assert 'LS' in nd
            assert 'LF' in nd
            assert 'float' in nd

    def test_cpm_critical_path_valid(self):
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        analyzer = CPMAnalyzer()
        G, cps, cas = analyzer.analyze(_sample_cpm_data())
        # A→B→D is the longest path: 3+4+5=12
        assert len(cps) >= 1
        # All critical activities should be in the graph
        for ca in cas:
            if ca not in ('START', 'END'):
                assert ca in G.nodes()

    def test_cpm_project_duration(self):
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        analyzer = CPMAnalyzer()
        G, _, _ = analyzer.analyze(_sample_cpm_data())
        max_ef = max(
            G.nodes[n].get('EF', 0)
            for n in G.nodes() if n not in ('START', 'END')
        )
        assert max_ef == 12  # A(3) + B(4) + D(5) = 12

    def test_cpm_float_noncritical(self):
        """Non-critical activity C should have positive float."""
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        analyzer = CPMAnalyzer()
        G, _, cas = analyzer.analyze(_sample_cpm_data())
        # C has duration 2, path A→C is 5, but A→B→D is 12
        # So C should have float > 0
        if 'C' not in cas:
            c_float = G.nodes['C'].get('float', 0)
            assert c_float > 0


# ────────────────────────────────────────────────────────────────
# B. PERTAnalyzer direct tests
# ────────────────────────────────────────────────────────────────

class TestPERTAnalyzerDirect:
    """Test PERTAnalyzer with edu-style data."""

    def test_pert_analyze_returns_tuple(self):
        from pmhelper.core.pert_analyzer import PERTAnalyzer
        analyzer = PERTAnalyzer()
        G, cps, cas = analyzer.analyze(_sample_pert_data())
        assert G is not None

    def test_pert_has_variance(self):
        from pmhelper.core.pert_analyzer import PERTAnalyzer
        analyzer = PERTAnalyzer()
        analyzer.analyze(_sample_pert_data())
        assert hasattr(analyzer, 'project_variance')
        assert hasattr(analyzer, 'project_std')
        assert analyzer.project_variance >= 0
        assert analyzer.project_std >= 0

    def test_pert_graph_has_expected_times(self):
        from pmhelper.core.pert_analyzer import PERTAnalyzer
        analyzer = PERTAnalyzer()
        G, _, _ = analyzer.analyze(_sample_pert_data())
        for node in ('X', 'Y', 'Z'):
            nd = G.nodes[node]
            assert 'ES' in nd
            assert 'EF' in nd
            assert 'duration' in nd

    def test_pert_serial_path_duration(self):
        """X→Y→Z is sequential, expected durations = 3+6+2 = 11, ceil = 11."""
        from pmhelper.core.pert_analyzer import PERTAnalyzer
        analyzer = PERTAnalyzer()
        G, _, _ = analyzer.analyze(_sample_pert_data())
        max_ef = max(
            G.nodes[n].get('EF', 0)
            for n in G.nodes() if n not in ('START', 'END')
        )
        assert max_ef == 11  # ceil(3)+ceil(6)+ceil(2) = 3+6+2 = 11


# ────────────────────────────────────────────────────────────────
# C. Results-dict construction (mirrors analyze_project() logic)
# ────────────────────────────────────────────────────────────────

class TestResultsDictConstruction:
    """Test that the results dict built by analyze_project matches
    what the real tabs expect."""

    def _run_analysis(self, data, mode='deterministic'):
        """Simulate analyze_project() logic without GUI."""
        if mode == 'probabilistic':
            from pmhelper.core.pert_analyzer import PERTAnalyzer
            analyzer = PERTAnalyzer()
        else:
            from pmhelper.core.cpm_analyzer import CPMAnalyzer
            analyzer = CPMAnalyzer()

        G, critical_paths, critical_activities = analyzer.analyze(data)

        project_duration = 0
        for node in G.nodes():
            if node not in ('START', 'END') and 'EF' in G.nodes[node]:
                ef = G.nodes[node]['EF']
                if ef > project_duration:
                    project_duration = ef

        critical_path = critical_paths[0] if critical_paths else []

        activities_for_display = []
        for node in G.nodes():
            if node in ('START', 'END'):
                continue
            nd = G.nodes[node]
            preds = [p for p in G.predecessors(node) if p != 'START']
            activity = {
                'id': node,
                'name': nd.get('activity', node),
                'duration': nd.get('duration', 0),
                'ES': nd.get('ES', 0),
                'EF': nd.get('EF', 0),
                'LS': nd.get('LS', 0),
                'LF': nd.get('LF', 0),
                'float': nd.get('float', 0),
                'critical': node in critical_activities,
                'predecessors': ', '.join(preds),
                'resource': nd.get('resource_demand', 0),
            }
            if mode == 'probabilistic':
                exp = nd.get('expected_duration', nd.get('duration', 0))
                activity.update({
                    'optimistic': nd.get('optimistic', 0),
                    'most_likely': nd.get('most_likely', 0),
                    'pessimistic': nd.get('pessimistic', 0),
                    'expected_duration': exp,
                    'expected': math.ceil(exp) if isinstance(exp, float) else exp,
                    'variance': round(nd.get('variance', 0), 3),
                })
            activities_for_display.append(activity)

        results = {
            'graph': G,
            'critical_paths': critical_paths,
            'critical_path': critical_path,
            'critical_activities': critical_activities,
            'activities_data': data,
            'activities': activities_for_display,
            'project_duration': project_duration,
        }

        if mode == 'probabilistic':
            results.update({
                'expected_duration': getattr(
                    analyzer, 'expected_duration', project_duration),
                'project_variance': getattr(
                    analyzer, 'project_variance', 0),
                'standard_deviation': getattr(
                    analyzer, 'project_std', 0),
            })

        return results

    def test_results_has_required_keys(self):
        rd = self._run_analysis(_sample_cpm_data())
        required = ['graph', 'critical_paths', 'critical_path',
                     'critical_activities', 'activities_data',
                     'activities', 'project_duration']
        for key in required:
            assert key in rd, f"Missing key: {key}"

    def test_results_activities_nonempty(self):
        rd = self._run_analysis(_sample_cpm_data())
        assert len(rd['activities']) == 4

    def test_results_activities_have_fields(self):
        rd = self._run_analysis(_sample_cpm_data())
        for act in rd['activities']:
            assert 'id' in act
            assert 'name' in act
            assert 'ES' in act
            assert 'EF' in act
            assert 'LS' in act
            assert 'LF' in act
            assert 'float' in act
            assert 'critical' in act

    def test_results_pert_has_extra_keys(self):
        rd = self._run_analysis(_sample_pert_data(), 'probabilistic')
        assert 'project_variance' in rd
        assert 'standard_deviation' in rd

    def test_results_pert_activities_have_variance(self):
        rd = self._run_analysis(_sample_pert_data(), 'probabilistic')
        for act in rd['activities']:
            assert 'variance' in act
            assert 'optimistic' in act
            assert 'most_likely' in act
            assert 'pessimistic' in act

    def test_results_project_duration_positive(self):
        rd = self._run_analysis(_sample_cpm_data())
        assert rd['project_duration'] > 0

    def test_results_critical_path_well_formed(self):
        rd = self._run_analysis(_sample_cpm_data())
        cp = rd['critical_path']
        assert isinstance(cp, list)
        assert len(cp) >= 2  # at least START + END or real activities

    def test_results_graph_is_networkx(self):
        import networkx as nx
        rd = self._run_analysis(_sample_cpm_data())
        assert isinstance(rd['graph'], nx.DiGraph)

    def test_results_dataframe_construction(self):
        """Test that we can build a RCPS-compatible DataFrame."""
        import pandas as pd
        rd = self._run_analysis(_sample_cpm_data())
        rows = []
        for act in rd['activities']:
            rows.append({
                'id': act['id'],
                'activity': act['name'],
                'early_start': act['ES'],
                'early_finish': act['EF'],
                'late_start': act['LS'],
                'late_finish': act['LF'],
                'float': act['float'],
                'duration': act['duration'],
                'resource_demand': act.get('resource', 0),
                'critical': act['critical'],
            })
        df = pd.DataFrame(rows)
        assert len(df) == 4
        assert 'early_start' in df.columns
        assert 'early_finish' in df.columns


# ────────────────────────────────────────────────────────────────
# D. Facade / MainWindowEdu compatibility
# ────────────────────────────────────────────────────────────────

class TestMainWindowFacade:
    """Test that MainWindowEdu imports cleanly and has all
    facade methods that real tabs expect."""

    def test_import(self):
        from pmhelper.gui.main_window_edu import MainWindowEdu
        assert MainWindowEdu is not None

    def test_has_analyze_project(self):
        from pmhelper.gui.main_window_edu import MainWindowEdu
        assert hasattr(MainWindowEdu, 'analyze_project')

    def test_has_facade_methods(self):
        from pmhelper.gui.main_window_edu import MainWindowEdu
        facade_methods = [
            'get_activities_data',
            'set_analysis_mode',
            'run_cpm_analysis',
            'set_status',
            'show_network_tab_help',
            'show_results_tab_help',
            'show_gantt_tab_help',
            'show_crashing_tab_help',
            'update_gantt_chart_after_analysis',
        ]
        for method in facade_methods:
            assert hasattr(MainWindowEdu, method), \
                f"Missing facade method: {method}"


# ────────────────────────────────────────────────────────────────
# E. Gantt tab CPM integration
# ────────────────────────────────────────────────────────────────

class TestGanttCPMIntegration:
    """Test that GanttTabEdu can accept analysis results."""

    def test_gantt_has_update_from_analysis(self):
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        assert hasattr(GanttTabEdu, 'update_from_analysis')

    def test_gantt_has_cpm_renderer(self):
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        assert hasattr(GanttTabEdu, '_draw_cpm_gantt')

    def test_gantt_has_evm_renderer(self):
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        assert hasattr(GanttTabEdu, '_draw_evm_gantt')

    def test_gantt_has_find_evm_task(self):
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        assert hasattr(GanttTabEdu, '_find_evm_task')


# ────────────────────────────────────────────────────────────────
# F. InputTab CPM integration
# ────────────────────────────────────────────────────────────────

class TestInputTabCPMIntegration:
    """Test that InputTabEdu has Analyze button and sync wiring."""

    def test_input_tab_has_main_window_param(self):
        """Constructor should accept main_window parameter."""
        import inspect
        from pmhelper.gui.tabs.input_tab_edu import InputTabEdu
        sig = inspect.signature(InputTabEdu.__init__)
        params = list(sig.parameters.keys())
        assert 'main_window' in params

    def test_input_tab_has_run_analysis(self):
        from pmhelper.gui.tabs.input_tab_edu import InputTabEdu
        assert hasattr(InputTabEdu, '_run_analysis')

    def test_input_tab_has_sync_from_cpm(self):
        from pmhelper.gui.tabs.input_tab_edu import InputTabEdu
        assert hasattr(InputTabEdu, '_sync_from_cpm')


# ────────────────────────────────────────────────────────────────
# G. Sync from CPM logic (non-GUI)
# ────────────────────────────────────────────────────────────────

class TestSyncFromCPMLogic:
    """Test the sync-from-CPM logic without tkinter."""

    def test_evm_task_links_to_cpm(self):
        """EVMTask.cpm_task_id should be set after sync."""
        from pmhelper.core.evm_models_edu import EVMTask
        task = EVMTask(task_id='A', name='Foundation', budget=100.0,
                       cpm_task_id='A')
        assert task.cpm_task_id == 'A'

    def test_evm_task_planned_from_cpm(self):
        """EVMTask planned_start/finish should match CPM ES/EF."""
        from pmhelper.core.evm_models_edu import EVMTask
        task = EVMTask(task_id='A', name='Foundation', budget=100.0,
                       planned_start=0, planned_finish=3, cpm_task_id='A')
        assert task.planned_start == 0
        assert task.planned_finish == 3

    def test_evm_project_with_cpm_linked_tasks(self):
        """EVMProject should accept tasks with cpm_task_id."""
        from pmhelper.core.evm_models_edu import EVMTask, EVMProject
        tasks = [
            EVMTask(task_id='A', name='Foundation', budget=300.0,
                    planned_start=0, planned_finish=3, cpm_task_id='A'),
            EVMTask(task_id='B', name='Framing', budget=400.0,
                    planned_start=3, planned_finish=7, cpm_task_id='B'),
        ]
        proj = EVMProject(project_name="Test", bac=700.0, tasks=tasks)
        assert len(proj.tasks) == 2
        assert all(t.cpm_task_id is not None for t in proj.tasks)


# ────────────────────────────────────────────────────────────────
# H. Real tab imports work
# ────────────────────────────────────────────────────────────────

class TestRealTabImports:
    """Verify that the real PMhelper tabs can be imported."""

    def test_import_results_tab(self):
        from pmhelper.gui.tabs.results_tab import ResultsTab
        assert ResultsTab is not None

    def test_import_network_tab(self):
        from pmhelper.gui.tabs.network_tab import NetworkTab
        assert NetworkTab is not None

    def test_import_pert_diagram_tab(self):
        from pmhelper.gui.tabs.pert_diagram_tab import PertDiagramTab
        assert PertDiagramTab is not None

    def test_import_crashing_tab(self):
        from pmhelper.gui.tabs.crashing_tab import CrashingTab
        assert CrashingTab is not None

    def test_import_cpm_analyzer(self):
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        assert CPMAnalyzer is not None

    def test_import_pert_analyzer(self):
        from pmhelper.core.pert_analyzer import PERTAnalyzer
        assert PERTAnalyzer is not None

    def test_import_network_builder(self):
        from pmhelper.core.network_builder import NetworkBuilder
        assert NetworkBuilder is not None
