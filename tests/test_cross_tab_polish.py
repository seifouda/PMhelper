"""Tests for Phase 11 — Cross-Tab Polish.

Covers:
 * 🔍 Open Interactive button presence across tabs
 * 📖 Show Worked Solution in risk tab
 * Step generator RAG value consistency
 * WBS cost toggle, budget allocation, set_mode
 * SWOT bubble Plotly import
"""
from __future__ import annotations

import importlib
import math
import re
import types
from unittest.mock import MagicMock, patch

import pytest

# ════════════════════════════════════════════════════════════════════
#  Step Generator RAG Consistency
# ════════════════════════════════════════════════════════════════════

VALID_RAGS = {"", "green", "amber", "red", "grey"}


def _collect_rags(steps, out=None):
    """Recursively collect all rag values from step trees."""
    if out is None:
        out = []
    for s in steps:
        out.append(s.rag)
        _collect_rags(s.children, out)
    return out


class TestStepGeneratorRAG:
    """All step generators must use 'green'/'amber'/'red'/'' for rag."""

    def test_risk_theory_rags(self):
        from pmhelper.core.risk_step_generator import risk_assessment_theory_steps
        rags = _collect_rags(risk_assessment_theory_steps())
        assert all(r in VALID_RAGS for r in rags), f"Invalid RAGs: {set(rags) - VALID_RAGS}"

    def test_risk_scoring_rags(self):
        from pmhelper.core.risk_step_generator import risk_scoring_steps
        from pmhelper.core.risk_register_edu import Risk
        risk = Risk(id="r1", name="Test", prob_score=3, impact_score=4)
        rags = _collect_rags(risk_scoring_steps(risk))
        assert all(r in VALID_RAGS for r in rags)

    def test_full_register_rags(self):
        from pmhelper.core.risk_step_generator import full_register_steps
        from pmhelper.core.risk_register_edu import Risk, RiskRegister
        reg = RiskRegister()
        reg.risks.append(Risk(id="r1", name="R1", prob_score=2, impact_score=3))
        reg.risks.append(Risk(id="r2", name="R2", prob_score=5, impact_score=5))
        rags = _collect_rags(full_register_steps(reg))
        assert all(r in VALID_RAGS for r in rags), f"Invalid RAGs: {set(rags) - VALID_RAGS}"

    def test_pert_steps_rags(self):
        from pmhelper.core.step_generators_edu import pert_steps
        results_data = {
            "graph": {},
            "critical_path": ["A"],
            "expected_duration": 6.0,
            "project_variance": 1.0,
            "standard_deviation": 1.0,
            "activities": [{"id": "A", "optimistic": 2, "most_likely": 5, "pessimistic": 8,
                            "expected": 5.0, "variance": 1.0}],
        }
        rags = _collect_rags(pert_steps(results_data, 7.0))
        assert all(r in VALID_RAGS for r in rags)

    def test_evm_steps_rags(self):
        from pmhelper.core.step_generators_edu import evm_steps
        kpis = {
            "PV": 100, "EV": 90, "AC": 95, "BAC": 200,
            "SV": -10, "CV": -5, "SPI": 0.9, "CPI": 0.947,
            "EAC_cum": 211, "EAC_atypical": 210, "EAC_typical": 215,
            "ETC": 116, "TCPI_BAC": 1.05, "TCPI_EAC": 1.0,
            "VAC": -11, "VACE": -0.05,
        }
        rags = _collect_rags(evm_steps(kpis))
        assert all(r in VALID_RAGS for r in rags)

    def test_crashing_theory_rags(self):
        from pmhelper.core.crashing_step_generator import crashing_theory_steps
        rags = _collect_rags(crashing_theory_steps())
        assert all(r in VALID_RAGS for r in rags)

    def test_leveling_concepts_rags(self):
        from pmhelper.core.leveling_step_generator import leveling_concepts_steps
        rags = _collect_rags(leveling_concepts_steps())
        assert all(r in VALID_RAGS for r in rags)


# ════════════════════════════════════════════════════════════════════
#  WBS Cost Toggle & Budget Allocation
# ════════════════════════════════════════════════════════════════════

class TestWBSCostFeatures:
    """WBS cost toggle, allocation, and set_mode."""

    @pytest.fixture
    def wbs_tab(self):
        """Create a WBS tab with mocked Tkinter."""
        with patch("pmhelper.gui.tabs.wbs_tab_edu.tk"), \
             patch("pmhelper.gui.tabs.wbs_tab_edu.ttk"), \
             patch("pmhelper.gui.tabs.wbs_tab_edu.WBSLayoutEngine"), \
             patch("pmhelper.gui.tabs.wbs_tab_edu.messagebox"):
            from pmhelper.gui.tabs.wbs_tab_edu import WBSTabEdu
            from pmhelper.core.wbs_models_edu import WBSTree, WBSNode
            state = MagicMock()
            tree = WBSTree()
            root = WBSNode(id="1", name="Project", cost=1000)
            c1 = WBSNode(id="1.1", name="Phase 1", parent_id="1", cost=400)
            c2 = WBSNode(id="1.2", name="Phase 2", parent_id="1", cost=0)
            c3 = WBSNode(id="1.3", name="Phase 3", parent_id="1", cost=0)
            for n in [root, c1, c2, c3]:
                tree.add_node(n)
            state.wbs_tree = tree
            tab = WBSTabEdu.__new__(WBSTabEdu)
            tab.state = state
            tab._selected_id = "1"
            tab._cost_visible = True
            tab._cost_toggle_btn = MagicMock()
            tab._tree_view = MagicMock()
            yield tab, tree

    def _find_node(self, tree, node_id):
        return next((n for n in tree.nodes if n.id == node_id), None)

    def test_set_mode(self, wbs_tab):
        tab, _ = wbs_tab
        tab.set_mode("ug")
        assert tab._mode == "UG"
        tab.set_mode("PG")
        assert tab._mode == "PG"

    def test_toggle_cost_column_hides(self, wbs_tab):
        tab, _ = wbs_tab
        tab._toggle_cost_column()
        assert tab._cost_visible is False
        tab._tree_view.column.assert_called_with("cost", width=0, minwidth=0)

    def test_toggle_cost_column_shows(self, wbs_tab):
        tab, _ = wbs_tab
        tab._cost_visible = False
        tab._toggle_cost_column()
        assert tab._cost_visible is True
        tab._tree_view.column.assert_called_with("cost", width=60, minwidth=40)

    def test_allocate_budget_splits_equally(self, wbs_tab):
        tab, tree = wbs_tab
        tab._selected_id = "1"
        tab._refresh_all = MagicMock()
        tab._update_cost_toggle_state = MagicMock()
        tab._allocate_budget()
        c2 = self._find_node(tree, "1.2")
        c3 = self._find_node(tree, "1.3")
        assert c2.cost == 300.0
        assert c3.cost == 300.0

    def test_allocate_no_budget(self, wbs_tab):
        tab, tree = wbs_tab
        self._find_node(tree, "1").cost = 0
        tab._selected_id = "1"
        tab._refresh_all = MagicMock()
        tab._allocate_budget()
        assert self._find_node(tree, "1.2").cost == 0

    def test_update_cost_toggle_state_disabled(self, wbs_tab):
        tab, tree = wbs_tab
        for n in tree.nodes:
            n.cost = 0
        tab._update_cost_toggle_state()
        tab._cost_toggle_btn.configure.assert_called_with(state="disabled")

    def test_update_cost_toggle_state_enabled(self, wbs_tab):
        tab, _ = wbs_tab
        tab._update_cost_toggle_state()
        tab._cost_toggle_btn.configure.assert_called_with(state="normal")

    # ── 11.8: flat table view ────────────────────────────────────

    def test_toggle_table_view_switches_show_mode(self, wbs_tab):
        tab, _ = wbs_tab
        tab._flat_view = False
        tab._table_toggle_btn = MagicMock()
        tab._refresh_all = MagicMock()

        tab._toggle_table_view()
        assert tab._flat_view is True
        tab._tree_view.configure.assert_called_with(show="headings")

        tab._toggle_table_view()
        assert tab._flat_view is False
        tab._tree_view.configure.assert_called_with(show="tree headings")

    def test_flat_rows_are_not_nested(self, wbs_tab):
        """Every row parents to "" — that's what makes the table flat."""
        tab, tree = wbs_tab
        tab._insert_flat_rows(tree)
        parents = [c.args[0] for c in tab._tree_view.insert.call_args_list]
        assert parents == [""] * len(tree.nodes)
        assert tab._tree_view.insert.call_count == len(tree.nodes)

    # ── 11.9: WBS → Cost Estimation ──────────────────────────────

    def test_estimate_from_wbs_sends_only_costed_leaves(self, wbs_tab):
        """Root has cost but is not a leaf; zero-cost leaves are excluded."""
        tab, tree = wbs_tab
        ce_tab = MagicMock()
        mw = MagicMock()
        mw.tabs = {"cost_estimation": ce_tab}
        tab.main_window = mw

        with patch("pmhelper.gui.tabs.wbs_tab_edu.messagebox"):
            tab._estimate_from_wbs()

        ce_tab.load_bottom_up_from_wbs.assert_called_once()
        sent = ce_tab.load_bottom_up_from_wbs.call_args.args[0]
        # Only "Phase 1" (leaf, cost=400). Root "Project" has cost but children.
        assert sent == [("Phase 1", 400)]

    def test_estimate_from_wbs_no_costs_does_not_call_tab(self, wbs_tab):
        tab, tree = wbs_tab
        for n in tree.nodes:
            n.cost = 0
        ce_tab = MagicMock()
        mw = MagicMock()
        mw.tabs = {"cost_estimation": ce_tab}
        tab.main_window = mw

        with patch("pmhelper.gui.tabs.wbs_tab_edu.messagebox"):
            tab._estimate_from_wbs()

        ce_tab.load_bottom_up_from_wbs.assert_not_called()


# ════════════════════════════════════════════════════════════════════
#  11.6 — crashing cost-slope semantics
# ════════════════════════════════════════════════════════════════════

class TestCrashingCostSlope:
    """This codebase stores `crash_cost` as a **rate** — cost per period
    crashed (`project_crashing_core.py`: `cost = crash_cost * crash_amount`;
    the dataclass field is `crash_cost_per_unit`). The textbook derivation
    `(CC - NC) / (ND - CD)` assumes **totals**. Feeding a rate through it
    yields a slope-of-a-slope, i.e. wrong numbers in the worked solution.
    `cost_slope` lets a rate-based caller pass the slope directly."""

    def _first_activity_step(self, steps):
        return steps[0].children[0]

    def test_given_slope_is_shown_verbatim(self):
        from pmhelper.core.crashing_step_generator import crashing_steps
        acts = [{"id": "A", "normal_duration": 10, "crash_duration": 6,
                 "normal_cost": 100, "crash_cost": 250, "cost_slope": 250}]
        sub = self._first_activity_step(crashing_steps(acts))
        assert "250.00 per period" in sub.result
        # Must NOT derive (250-100)/4 = 37.50
        assert "37.50" not in sub.result

    def test_totals_still_derive_textbook_slope(self):
        from pmhelper.core.crashing_step_generator import crashing_steps
        acts = [{"id": "B", "normal_duration": 10, "crash_duration": 6,
                 "normal_cost": 8000, "crash_cost": 12000}]
        sub = self._first_activity_step(crashing_steps(acts))
        assert "1,000.00 per period" in sub.result  # (12000-8000)/4

    def test_uncrashable_activity_reported(self):
        from pmhelper.core.crashing_step_generator import crashing_steps
        acts = [{"id": "C", "normal_duration": 5, "crash_duration": 5,
                 "normal_cost": 100, "crash_cost": 200, "cost_slope": 200}]
        sub = self._first_activity_step(crashing_steps(acts))
        assert "Cannot be crashed" in sub.result


# ════════════════════════════════════════════════════════════════════
#  11.9 — Cost Estimation → WBS contract
# ════════════════════════════════════════════════════════════════════

class TestCostEstimateBreakdownContract:
    """`_load_costs_from_estimation` matches WBS leaves against
    `CostEstimateResult.breakdown`. It previously read `.items` /
    `.line_items`, which have never existed on that dataclass — so the
    load silently matched nothing. Lock the real shape down."""

    def test_breakdown_is_label_cost_pairs(self):
        from pmhelper.core.cost_estimation import (
            WorkPackage, BottomUpEstimator)
        wps = [
            WorkPackage(name="Design", labour_cost=5000, overhead_pct=0),
            WorkPackage(name="Testing", labour_cost=4000,
                        material_cost=500, overhead_pct=0),
        ]
        res = BottomUpEstimator().estimate(wps)
        assert res.breakdown == [("Design", 5000.0), ("Testing", 4500.0)]

    def test_result_has_no_items_attribute(self):
        """Guards the regression: if someone reintroduces `.items`,
        the two shapes must not silently diverge again."""
        from pmhelper.core.cost_estimation import CostEstimateResult
        r = CostEstimateResult(total_cost=0.0)
        assert not hasattr(r, "items")
        assert not hasattr(r, "line_items")
        assert hasattr(r, "breakdown")


# ════════════════════════════════════════════════════════════════════
#  11.6 — "Show All Calculations" label consistency
# ════════════════════════════════════════════════════════════════════

class TestCalculationsButtonLabel:
    """The button drifted into four different labels across tabs because
    nothing pinned it. Pin it."""

    LABEL = "\U0001f4ca Show All Calculations"
    TABS = [
        "evm_tab_edu", "probability_tab_edu", "three_point_tab_edu",
        "financial_tab_edu", "raci_tab_edu", "cost_estimation_tab_edu",
        "risk_tab_edu", "rcps_tab_edu", "crashing_tab_gui",
    ]

    def _source(self, mod):
        import pathlib
        import pmhelper.gui.tabs as tabs_pkg
        p = pathlib.Path(tabs_pkg.__file__).parent / f"{mod}.py"
        return p.read_text(encoding="utf-8")

    @pytest.mark.parametrize("mod", TABS)
    def test_tab_uses_canonical_label(self, mod):
        assert self.LABEL in self._source(mod), (
            f"{mod} does not use the canonical calculations-button label")

    @pytest.mark.parametrize("mod", TABS)
    def test_tab_has_no_legacy_label(self, mod):
        src = self._source(mod)
        for legacy in ("\U0001f4dd Worked Solution",
                       "\U0001f4dd Show Worked Solution",
                       "\U0001f4d6 Show Worked Solution"):
            assert f'text="{legacy}"' not in src, (
                f"{mod} still wires the legacy label {legacy!r}")


# ════════════════════════════════════════════════════════════════════
#  SWOT Plotly Bubble Import
# ════════════════════════════════════════════════════════════════════

class TestSWOTPlotlyImport:
    def test_plotly_swot_bubble_importable(self):
        from pmhelper.utils.plotly_charts import plotly_swot_bubble
        assert callable(plotly_swot_bubble)


# ════════════════════════════════════════════════════════════════════
#  Interactive Charts Helper
# ════════════════════════════════════════════════════════════════════

class TestInteractiveCharts:
    def test_open_chart_in_browser_none_fig(self):
        from pmhelper.utils.interactive_charts import open_chart_in_browser
        assert open_chart_in_browser(None) is None

    def test_open_chart_in_browser_creates_html(self, tmp_path):
        pytest.importorskip("plotly")
        import plotly.graph_objects as go
        from pmhelper.utils.interactive_charts import open_chart_in_browser
        fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])])
        with patch("pmhelper.utils.interactive_network._open_in_browser"):
            path = open_chart_in_browser(fig, "Test")
        assert path is not None
        assert path.endswith(".html")


# ════════════════════════════════════════════════════════════════════
#  Step Generator Title Format
# ════════════════════════════════════════════════════════════════════

class TestStepTitleFormat:
    """Step titles should use em dash (—) not en dash or hyphen for the Step N separator."""

    def _check_titles(self, steps):
        for s in steps:
            if s.title.startswith("Step "):
                assert "—" in s.title or ":" in s.title, \
                    f"Title missing em dash: {s.title}"
            self._check_titles(s.children)

    def test_risk_theory_titles(self):
        from pmhelper.core.risk_step_generator import risk_assessment_theory_steps
        self._check_titles(risk_assessment_theory_steps())

    def test_crashing_theory_titles(self):
        from pmhelper.core.crashing_step_generator import crashing_theory_steps
        self._check_titles(crashing_theory_steps())

    def test_leveling_concepts_titles(self):
        from pmhelper.core.leveling_step_generator import leveling_concepts_steps
        self._check_titles(leveling_concepts_steps())
