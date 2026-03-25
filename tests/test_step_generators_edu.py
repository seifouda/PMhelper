"""
Tests for Phase 11 — Worked-Solution Step Generators.
"""

import math
import pytest

from pmhelper.core.step_generators_edu import (
    Step, pert_steps, evm_steps, cpm_forward_steps, cpm_backward_steps,
)


# ════════════════════════════════════════════════════════════════════
#  Step dataclass
# ════════════════════════════════════════════════════════════════════

class TestStepDataclass:
    def test_default_fields(self):
        s = Step(title="T")
        assert s.title == "T"
        assert s.formula == ""
        assert s.substitution == ""
        assert s.result == ""
        assert s.interpretation == ""
        assert s.rag == ""
        assert s.children == []

    def test_to_text_simple(self):
        s = Step(title="Add", formula="1+1", result="= 2")
        text = s.to_text()
        assert "Add" in text
        assert "1+1" in text
        assert "= 2" in text

    def test_to_text_nested(self):
        child = Step(title="Child", result="= 3")
        parent = Step(title="Parent", children=[child])
        text = parent.to_text()
        assert "Parent" in text
        assert "Child" in text
        assert "= 3" in text

    def test_children_independence(self):
        """Each Step should have its own children list."""
        a = Step(title="A")
        b = Step(title="B")
        a.children.append(Step(title="C"))
        assert len(b.children) == 0


# ════════════════════════════════════════════════════════════════════
#  PERT Steps
# ════════════════════════════════════════════════════════════════════

def _make_pert_results():
    """Build a minimal results_data dict for PERT tests."""
    import networkx as nx

    G = nx.DiGraph()
    # Simple network: A → B → C (all critical)
    activities = [
        {"id": "A", "optimistic": 2, "most_likely": 4, "pessimistic": 6,
         "expected_duration": 4.0, "variance": 0.4444},
        {"id": "B", "optimistic": 3, "most_likely": 5, "pessimistic": 7,
         "expected_duration": 5.0, "variance": 0.4444},
        {"id": "C", "optimistic": 1, "most_likely": 3, "pessimistic": 5,
         "expected_duration": 3.0, "variance": 0.4444},
    ]
    for act in activities:
        G.add_node(act["id"], duration=act["expected_duration"],
                   expected_time=act["expected_duration"],
                   variance=act["variance"],
                   optimistic=act["optimistic"],
                   most_likely=act["most_likely"],
                   pessimistic=act["pessimistic"],
                   ES=0, EF=0, LS=0, LF=0, float=0)
    G.add_edge("A", "B")
    G.add_edge("B", "C")

    proj_var = sum(a["variance"] for a in activities)  # 1.3332
    std = math.sqrt(proj_var)

    return {
        "graph": G,
        "critical_path": ["A", "B", "C"],
        "activities": activities,
        "expected_duration": 12.0,
        "project_variance": round(proj_var, 4),
        "standard_deviation": round(std, 4),
        "project_duration": 12,
    }


class TestPertSteps:
    def test_basic_steps_without_target(self):
        rd = _make_pert_results()
        steps = pert_steps(rd)
        titles = [s.title for s in steps]
        assert any("Expected Time" in t for t in titles)
        assert any("Variance" in t for t in titles)
        assert any("Project Variance" in t for t in titles)
        assert any("Standard Deviation" in t for t in titles)
        # No Z-score without target
        assert not any("Z-Score" in t for t in titles)

    def test_steps_with_target_duration(self):
        rd = _make_pert_results()
        steps = pert_steps(rd, target_duration=14.0)
        titles = [s.title for s in steps]
        assert any("Z-Score" in t for t in titles)
        assert any("Probability" in t for t in titles)

    def test_expected_time_children(self):
        rd = _make_pert_results()
        steps = pert_steps(rd)
        te_step = [s for s in steps if "Expected Time" in s.title][0]
        assert len(te_step.children) == 3  # A, B, C

    def test_variance_children_critical_only(self):
        rd = _make_pert_results()
        steps = pert_steps(rd)
        var_step = [s for s in steps if "Variance" in s.title and "Project" not in s.title][0]
        # All 3 are critical in this network
        assert len(var_step.children) == 3

    def test_project_variance_value(self):
        rd = _make_pert_results()
        steps = pert_steps(rd)
        pv_step = [s for s in steps if "Project Variance" in s.title][0]
        assert "1.3332" in pv_step.result

    def test_z_score_calculation(self):
        rd = _make_pert_results()
        steps = pert_steps(rd, target_duration=12.0)
        z_step = [s for s in steps if "Z-Score" in s.title][0]
        # Z = (12 - 12) / std ≈ 0
        assert "0.0000" in z_step.result

    def test_probability_rag_high(self):
        rd = _make_pert_results()
        steps = pert_steps(rd, target_duration=15.0)
        prob_step = [s for s in steps if "Probability" in s.title][0]
        assert prob_step.rag == "green"

    def test_probability_rag_low(self):
        rd = _make_pert_results()
        steps = pert_steps(rd, target_duration=8.0)
        prob_step = [s for s in steps if "Probability" in s.title][0]
        assert prob_step.rag == "red"

    def test_empty_results(self):
        steps = pert_steps({})
        assert steps == [] or all(not s.children for s in steps)


# ════════════════════════════════════════════════════════════════════
#  EVM Steps
# ════════════════════════════════════════════════════════════════════

def _make_evm_kpis():
    """Build a realistic KPIs dict."""
    return {
        "ev": 100_000.0,
        "pv": 120_000.0,
        "ac": 110_000.0,
        "bac": 200_000.0,
        "cv": -10_000.0,     # over budget
        "sv": -20_000.0,     # behind schedule
        "cpi": 0.909,
        "spi": 0.833,
        "cr": 0.757,
        "pc": 50.0,
        "ps": 55.0,
        "eac1": 210_000.0,
        "eac2": 220_022.0,
        "eac3": 242_000.0,
        "vac": -10_000.0,
        "tcpi_bac": 1.111,
        "primary_eac_value": 210_000.0,
        "errors": {},
    }


class TestEvmSteps:
    def test_generates_steps(self):
        kpis = _make_evm_kpis()
        steps = evm_steps(kpis, "$")
        assert len(steps) >= 10

    def test_base_values_step(self):
        kpis = _make_evm_kpis()
        steps = evm_steps(kpis, "$")
        first = steps[0]
        assert "Base" in first.title
        assert "$100,000.00" in first.substitution

    def test_cv_step(self):
        kpis = _make_evm_kpis()
        steps = evm_steps(kpis, "$")
        cv_step = [s for s in steps if "Cost Variance" in s.title][0]
        assert "EV − AC" in cv_step.formula
        assert cv_step.rag in ("green", "amber", "red")

    def test_cpi_interpretation(self):
        kpis = _make_evm_kpis()
        steps = evm_steps(kpis, "$")
        cpi_step = [s for s in steps if "CPI" in s.title][0]
        # CPI = 0.909 < 1, so bad interpretation
        assert "spending more" in cpi_step.interpretation or "< 1.0" in cpi_step.interpretation

    def test_eac_steps_present(self):
        kpis = _make_evm_kpis()
        steps = evm_steps(kpis, "$")
        titles = [s.title for s in steps]
        assert any("EAC" in t for t in titles)

    def test_tcpi_step(self):
        kpis = _make_evm_kpis()
        steps = evm_steps(kpis, "$")
        tcpi_step = [s for s in steps if "TCPI" in s.title][0]
        assert "1.111" in tcpi_step.result

    def test_none_kpis(self):
        """Should not crash with None values."""
        kpis = {
            "ev": 100, "pv": 0, "ac": 0, "bac": 200,
            "cv": 100, "sv": 100,
            "cpi": None, "spi": None, "cr": None,
            "pc": None, "ps": None,
            "eac1": 200, "eac2": None, "eac3": None,
            "vac": None, "tcpi_bac": None,
            "primary_eac_value": 200,
            "errors": {"cpi": "AC is zero"},
        }
        steps = evm_steps(kpis, "£")
        assert len(steps) >= 3  # At least base + CV + SV

    def test_currency_symbol(self):
        kpis = _make_evm_kpis()
        steps = evm_steps(kpis, "€")
        text = steps[0].substitution
        assert "€" in text


# ════════════════════════════════════════════════════════════════════
#  CPM Steps
# ════════════════════════════════════════════════════════════════════

def _make_cpm_results():
    """Build a minimal CPM results_data dict."""
    import networkx as nx

    G = nx.DiGraph()
    # A → B → D, A → C → D
    for nid, dur, es, ef, ls, lf, flt in [
        ("A", 3, 0, 3, 0, 3, 0),
        ("B", 4, 3, 7, 3, 7, 0),
        ("C", 2, 3, 5, 5, 7, 2),
        ("D", 2, 7, 9, 7, 9, 0),
    ]:
        G.add_node(nid, duration=dur, ES=es, EF=ef, LS=ls, LF=lf, float=flt)

    G.add_node("START", duration=0, ES=0, EF=0, LS=0, LF=0, float=0)
    G.add_node("END", duration=0, ES=9, EF=9, LS=9, LF=9, float=0)
    G.add_edge("START", "A")
    G.add_edge("A", "B")
    G.add_edge("A", "C")
    G.add_edge("B", "D")
    G.add_edge("C", "D")
    G.add_edge("D", "END")

    return {
        "graph": G,
        "critical_path": ["A", "B", "D"],
        "project_duration": 9,
    }


class TestCpmForwardSteps:
    def test_generates_wrapper_step(self):
        rd = _make_cpm_results()
        steps = cpm_forward_steps(rd)
        assert len(steps) == 1
        assert "Forward Pass" in steps[0].title

    def test_children_per_activity(self):
        rd = _make_cpm_results()
        steps = cpm_forward_steps(rd)
        children = steps[0].children
        # A, B, C, D = 4 activities (START/END excluded)
        assert len(children) == 4

    def test_critical_activities_marked_red(self):
        rd = _make_cpm_results()
        steps = cpm_forward_steps(rd)
        children = steps[0].children
        a_step = [c for c in children if "A" in c.title][0]
        assert a_step.rag == "red"

    def test_non_critical_no_red(self):
        rd = _make_cpm_results()
        steps = cpm_forward_steps(rd)
        children = steps[0].children
        c_step = [c for c in children if " C" in c.title][0]
        assert c_step.rag != "red"

    def test_es_ef_values(self):
        rd = _make_cpm_results()
        steps = cpm_forward_steps(rd)
        children = steps[0].children
        b_step = [c for c in children if " B" in c.title][0]
        assert "ES = 3" in b_step.result
        assert "EF = 7" in b_step.result

    def test_empty_graph(self):
        steps = cpm_forward_steps({})
        assert steps == []


class TestCpmBackwardSteps:
    def test_generates_wrapper_step(self):
        rd = _make_cpm_results()
        steps = cpm_backward_steps(rd)
        assert len(steps) == 1
        assert "Backward Pass" in steps[0].title

    def test_children_per_activity(self):
        rd = _make_cpm_results()
        steps = cpm_backward_steps(rd)
        children = steps[0].children
        assert len(children) == 4

    def test_float_in_result(self):
        rd = _make_cpm_results()
        steps = cpm_backward_steps(rd)
        children = steps[0].children
        c_step = [c for c in children if " C" in c.title][0]
        assert "Float = 2" in c_step.result

    def test_critical_interpretation(self):
        rd = _make_cpm_results()
        steps = cpm_backward_steps(rd)
        children = steps[0].children
        a_step = [c for c in children if " A" in c.title][0]
        assert "Critical" in a_step.interpretation

    def test_project_duration_in_interpretation(self):
        rd = _make_cpm_results()
        steps = cpm_backward_steps(rd)
        wrapper = steps[0]
        assert "9" in wrapper.interpretation

    def test_empty_graph(self):
        steps = cpm_backward_steps({})
        assert steps == []


# ════════════════════════════════════════════════════════════════════
#  Integration: to_text for all generators
# ════════════════════════════════════════════════════════════════════

class TestToTextIntegration:
    def test_pert_to_text(self):
        rd = _make_pert_results()
        steps = pert_steps(rd, target_duration=14.0)
        text = "\n\n".join(s.to_text() for s in steps)
        assert len(text) > 100
        assert "tₑ" in text
        assert "Z-Score" in text

    def test_evm_to_text(self):
        kpis = _make_evm_kpis()
        steps = evm_steps(kpis, "$")
        text = "\n\n".join(s.to_text() for s in steps)
        assert "EV" in text
        assert "$" in text

    def test_cpm_to_text(self):
        rd = _make_cpm_results()
        fwd = cpm_forward_steps(rd)
        bwd = cpm_backward_steps(rd)
        text = "\n\n".join(s.to_text() for s in fwd + bwd)
        assert "Forward Pass" in text
        assert "Backward Pass" in text
