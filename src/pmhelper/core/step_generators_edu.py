"""
PMhelper Edu — Worked-Solution Step Generators.

Produces structured Step trees for PERT, EVM, and CPM calculations.
Each Step contains a title, formula, numeric substitution, result,
interpretation text, optional RAG colour, and optional child steps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import math


@dataclass
class Step:
    """One step in a worked solution."""
    title: str
    formula: str = ""
    substitution: str = ""
    result: str = ""
    interpretation: str = ""
    rag: str = ""                         # green / amber / red / grey / ""
    children: List["Step"] = field(default_factory=list)

    # ── Flat-text helpers (for clipboard / export) ──────────────────
    def to_text(self, indent: int = 0) -> str:
        pad = "  " * indent
        lines = [f"{pad}{self.title}"]
        if self.formula:
            lines.append(f"{pad}  Formula:        {self.formula}")
        if self.substitution:
            lines.append(f"{pad}  Substitution:   {self.substitution}")
        if self.result:
            lines.append(f"{pad}  Result:         {self.result}")
        if self.interpretation:
            lines.append(f"{pad}  Interpretation: {self.interpretation}")
        for child in self.children:
            lines.append(child.to_text(indent + 1))
        return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════
#  PERT  Steps
# ════════════════════════════════════════════════════════════════════

def pert_steps(results_data: Dict[str, Any],
               target_duration: Optional[float] = None) -> List[Step]:
    """
    Generate PERT worked-solution steps from analysis results.

    Parameters
    ----------
    results_data : dict
        The results_data dict produced by main_window_edu.analyze_project().
        Expected keys: graph, critical_path, expected_duration,
        project_variance, standard_deviation, activities.
    target_duration : float, optional
        If provided an extra Z-score + probability step is appended.

    Returns
    -------
    list[Step]
    """
    steps: List[Step] = []
    graph = results_data.get("graph")
    activities = results_data.get("activities", [])
    critical_path = results_data.get("critical_path", [])
    cp_set = set(critical_path) - {"START", "END"}

    # ── Step 1: Expected Time per Activity ──────────────────────────
    te_children: List[Step] = []
    for act in activities:
        aid = act["id"]
        if aid in ("START", "END"):
            continue
        o = act.get("optimistic")
        m = act.get("most_likely")
        p = act.get("pessimistic")
        te = act.get("expected_duration", act.get("expected_time"))
        if o is None or m is None or p is None or te is None:
            continue
        te_children.append(Step(
            title=f"Activity {aid}",
            formula="tₑ = (o + 4m + p) / 6",
            substitution=f"= ({o} + 4×{m} + {p}) / 6",
            result=f"= {te:.4f}",
        ))
    if te_children:
        steps.append(Step(
            title="Step 1 — Expected Time (tₑ) per Activity",
            formula="tₑ = (o + 4m + p) / 6",
            interpretation="Weighted average of optimistic, most-likely and pessimistic estimates.",
            children=te_children,
        ))

    # ── Step 2: Variance per Activity (critical-path only) ──────────
    var_children: List[Step] = []
    for act in activities:
        aid = act["id"]
        if aid not in cp_set:
            continue
        o = act.get("optimistic")
        p = act.get("pessimistic")
        v = act.get("variance")
        if o is None or p is None or v is None:
            continue
        var_children.append(Step(
            title=f"Activity {aid} (critical)",
            formula="σ² = ((p − o) / 6)²",
            substitution=f"= (({p} − {o}) / 6)²",
            result=f"= {v:.4f}",
        ))
    if var_children:
        steps.append(Step(
            title="Step 2 — Variance (σ²) per Critical-Path Activity",
            formula="σ² = ((p − o) / 6)²",
            interpretation="Only critical-path activities contribute to project variance.",
            children=var_children,
        ))

    # ── Step 3: Project Variance ────────────────────────────────────
    proj_var = results_data.get("project_variance", 0)
    cp_labels = " + ".join(f"σ²({a})" for a in sorted(cp_set) if a not in ("START", "END"))
    cp_values = []
    for act in activities:
        if act["id"] in cp_set:
            v = act.get("variance")
            if v is not None:
                cp_values.append(f"{v:.4f}")
    sub_str = " + ".join(cp_values) if cp_values else "—"
    steps.append(Step(
        title="Step 3 — Project Variance",
        formula=f"σ²_project = Σ σ²(critical) = {cp_labels}",
        substitution=f"= {sub_str}",
        result=f"= {proj_var:.4f}",
        interpretation="Sum of variances along the critical path.",
    ))

    # ── Step 4: Standard Deviation ──────────────────────────────────
    std_dev = results_data.get("standard_deviation", 0)
    steps.append(Step(
        title="Step 4 — Project Standard Deviation (σ)",
        formula="σ = √(σ²_project)",
        substitution=f"= √({proj_var:.4f})",
        result=f"= {std_dev:.4f}",
        interpretation="Measures the spread of possible project durations.",
    ))

    # ── Step 5 & 6: Z-score + Probability (if target given) ────────
    exp_dur = results_data.get("expected_duration", 0)
    if target_duration is not None and std_dev > 0:
        z = (target_duration - exp_dur) / std_dev
        steps.append(Step(
            title="Step 5 — Z-Score",
            formula="Z = (d − μ) / σ",
            substitution=f"= ({target_duration:.2f} − {exp_dur:.4f}) / {std_dev:.4f}",
            result=f"= {z:.4f}",
            interpretation="Number of standard deviations from the expected duration.",
        ))

        try:
            from scipy.stats import norm as _norm
            prob = _norm.cdf(z)
        except ImportError:
            prob = 0.5 * (1 + math.erf(z / math.sqrt(2)))

        pct = prob * 100
        if pct >= 80:
            rag = "green"
            interp = f"High confidence ({pct:.1f}%) of finishing within {target_duration:.2f} periods."
        elif pct >= 50:
            rag = "amber"
            interp = f"Moderate confidence ({pct:.1f}%) of finishing within {target_duration:.2f} periods."
        else:
            rag = "red"
            interp = f"Low confidence ({pct:.1f}%) of finishing within {target_duration:.2f} periods."

        steps.append(Step(
            title="Step 6 — Probability P(T ≤ d)",
            formula="P(T ≤ d) = Φ(Z)   (standard normal CDF)",
            substitution=f"= Φ({z:.4f})",
            result=f"= {pct:.2f}%",
            interpretation=interp,
            rag=rag,
        ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  EVM  Steps
# ════════════════════════════════════════════════════════════════════

_EVM_FORMULAS = {
    "cv":  ("Cost Variance (CV)",         "CV = EV − AC"),
    "sv":  ("Schedule Variance (SV)",     "SV = EV − PV"),
    "cpi": ("Cost Performance Index",     "CPI = EV / AC"),
    "spi": ("Schedule Performance Index", "SPI = EV / PV"),
    "cr":  ("Critical Ratio",            "CR = CPI × SPI"),
    "pc":  ("Percent Complete",          "PC = (EV / BAC) × 100"),
    "ps":  ("Percent Spent",             "PS = (AC / BAC) × 100"),
    "eac1": ("EAC₁ (Atypical)",          "EAC₁ = AC + (BAC − EV)"),
    "eac2": ("EAC₂ (Typical)",           "EAC₂ = BAC / CPI"),
    "eac3": ("EAC₃ (Composite)",         "EAC₃ = AC + (BAC − EV) / (CPI × SPI)"),
    "vac":  ("Variance at Completion",   "VAC = BAC − EAC"),
    "tcpi_bac": ("TCPI (BAC)",           "TCPI = (BAC − EV) / (BAC − AC)"),
}


def evm_steps(kpis: Dict[str, Any], currency: str = "$") -> List[Step]:
    """
    Generate EVM worked-solution steps from computed KPIs.

    Parameters
    ----------
    kpis : dict
        Output of ``compute_all_kpis()``.
    currency : str
        Currency symbol for formatting.

    Returns
    -------
    list[Step]
    """
    from pmhelper.core.evm_calculations_edu import get_rag

    ev = kpis.get("ev", 0)
    pv = kpis.get("pv", 0)
    ac = kpis.get("ac", 0)
    bac = kpis.get("bac", 0)
    cpi = kpis.get("cpi")
    spi = kpis.get("spi")

    def _fc(v):
        """Format currency value."""
        if v is None:
            return "N/A"
        return f"{currency}{v:,.2f}"

    def _fi(v):
        """Format index value."""
        if v is None:
            return "N/A"
        return f"{v:.3f}"

    def _fp(v):
        """Format percentage."""
        if v is None:
            return "N/A"
        return f"{v:.1f}%"

    steps: List[Step] = []

    # ── Base values ────────────────────────────────────────
    steps.append(Step(
        title="Step 1 — Base Earned Value Metrics",
        formula="EV, PV, AC, BAC are inputs from the project data.",
        substitution=f"EV = {_fc(ev)},  PV = {_fc(pv)},  AC = {_fc(ac)},  BAC = {_fc(bac)}",
        result="(base values)",
        interpretation="These are the foundation for all other KPIs.",
    ))

    # ── Variances ──────────────────────────────────────────
    cv = kpis.get("cv")
    sv = kpis.get("sv")
    steps.append(Step(
        title="Step 2 — Cost Variance (CV)",
        formula="CV = EV − AC",
        substitution=f"= {_fc(ev)} − {_fc(ac)}",
        result=f"= {_fc(cv)}",
        interpretation="Positive = under budget, Negative = over budget." if cv is not None else "",
        rag=get_rag("cv", cv, bac) if cv is not None else "grey",
    ))
    steps.append(Step(
        title="Step 3 — Schedule Variance (SV)",
        formula="SV = EV − PV",
        substitution=f"= {_fc(ev)} − {_fc(pv)}",
        result=f"= {_fc(sv)}",
        interpretation="Positive = ahead of schedule, Negative = behind schedule." if sv is not None else "",
        rag=get_rag("sv", sv, bac) if sv is not None else "grey",
    ))

    # ── Indices ────────────────────────────────────────────
    step_num = 4
    if cpi is not None:
        steps.append(Step(
            title=f"Step {step_num} — Cost Performance Index (CPI)",
            formula="CPI = EV / AC",
            substitution=f"= {_fc(ev)} / {_fc(ac)}",
            result=f"= {_fi(cpi)}",
            interpretation="CPI ≥ 1.0 = earning more per £ spent." if cpi >= 1.0
                           else "CPI < 1.0 = spending more per £ of work earned.",
            rag=get_rag("cpi", cpi, bac),
        ))
    else:
        steps.append(Step(
            title=f"Step {step_num} — Cost Performance Index (CPI)",
            formula="CPI = EV / AC",
            result="N/A — AC is zero",
            rag="grey",
        ))
    step_num += 1

    if spi is not None:
        steps.append(Step(
            title=f"Step {step_num} — Schedule Performance Index (SPI)",
            formula="SPI = EV / PV",
            substitution=f"= {_fc(ev)} / {_fc(pv)}",
            result=f"= {_fi(spi)}",
            interpretation="SPI ≥ 1.0 = ahead of schedule." if spi >= 1.0
                           else "SPI < 1.0 = behind schedule.",
            rag=get_rag("spi", spi, bac),
        ))
    else:
        steps.append(Step(
            title=f"Step {step_num} — Schedule Performance Index (SPI)",
            formula="SPI = EV / PV",
            result="N/A — PV is zero",
            rag="grey",
        ))
    step_num += 1

    # ── Critical Ratio ─────────────────────────────────────
    cr = kpis.get("cr")
    if cr is not None:
        steps.append(Step(
            title=f"Step {step_num} — Critical Ratio (CR)",
            formula="CR = CPI × SPI",
            substitution=f"= {_fi(cpi)} × {_fi(spi)}",
            result=f"= {_fi(cr)}",
            interpretation="CR ≥ 1.0 = project performing favourably overall.",
            rag=get_rag("cr", cr, bac),
        ))
    step_num += 1

    # ── Percent Complete / Spent ───────────────────────────
    pc = kpis.get("pc")
    ps = kpis.get("ps")
    if pc is not None:
        steps.append(Step(
            title=f"Step {step_num} — Percent Complete (PC)",
            formula="PC = (EV / BAC) × 100",
            substitution=f"= ({_fc(ev)} / {_fc(bac)}) × 100",
            result=f"= {_fp(pc)}",
        ))
    step_num += 1
    if ps is not None:
        steps.append(Step(
            title=f"Step {step_num} — Percent Spent (PS)",
            formula="PS = (AC / BAC) × 100",
            substitution=f"= ({_fc(ac)} / {_fc(bac)}) × 100",
            result=f"= {_fp(ps)}",
        ))
    step_num += 1

    # ── EAC variants ───────────────────────────────────────
    eac1 = kpis.get("eac1")
    if eac1 is not None:
        steps.append(Step(
            title=f"Step {step_num} — EAC₁ (Atypical Variance)",
            formula="EAC₁ = AC + (BAC − EV)",
            substitution=f"= {_fc(ac)} + ({_fc(bac)} − {_fc(ev)})",
            result=f"= {_fc(eac1)}",
            interpretation="Assumes remaining work will be done at budget rate.",
            rag=get_rag("eac1", eac1, bac),
        ))
    step_num += 1

    eac2 = kpis.get("eac2")
    if eac2 is not None and cpi is not None:
        steps.append(Step(
            title=f"Step {step_num} — EAC₂ (Typical Variance)",
            formula="EAC₂ = BAC / CPI",
            substitution=f"= {_fc(bac)} / {_fi(cpi)}",
            result=f"= {_fc(eac2)}",
            interpretation="Assumes remaining work continues at current CPI.",
            rag=get_rag("eac2", eac2, bac),
        ))
    step_num += 1

    eac3 = kpis.get("eac3")
    if eac3 is not None and cpi is not None and spi is not None:
        steps.append(Step(
            title=f"Step {step_num} — EAC₃ (Composite)",
            formula="EAC₃ = AC + (BAC − EV) / (CPI × SPI)",
            substitution=f"= {_fc(ac)} + ({_fc(bac)} − {_fc(ev)}) / ({_fi(cpi)} × {_fi(spi)})",
            result=f"= {_fc(eac3)}",
            interpretation="Uses both cost and schedule performance.",
            rag=get_rag("eac3", eac3, bac),
        ))
    step_num += 1

    # ── VAC ────────────────────────────────────────────────
    vac = kpis.get("vac")
    primary_eac = kpis.get("primary_eac_value")
    if vac is not None and primary_eac is not None:
        steps.append(Step(
            title=f"Step {step_num} — Variance at Completion (VAC)",
            formula="VAC = BAC − EAC",
            substitution=f"= {_fc(bac)} − {_fc(primary_eac)}",
            result=f"= {_fc(vac)}",
            interpretation="Positive = expected under-run, Negative = expected over-run.",
            rag=get_rag("vac", vac, bac),
        ))
    step_num += 1

    # ── TCPI ───────────────────────────────────────────────
    tcpi = kpis.get("tcpi_bac")
    if tcpi is not None:
        steps.append(Step(
            title=f"Step {step_num} — TCPI (BAC)",
            formula="TCPI = (BAC − EV) / (BAC − AC)",
            substitution=f"= ({_fc(bac)} − {_fc(ev)}) / ({_fc(bac)} − {_fc(ac)})",
            result=f"= {_fi(tcpi)}",
            interpretation="TCPI ≤ 1.0 = achievable at current rate."
                           if tcpi <= 1.0
                           else "TCPI > 1.0 = must improve efficiency on remaining work.",
            rag=get_rag("tcpi_bac", tcpi, bac),
        ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  CPM  Steps
# ════════════════════════════════════════════════════════════════════

def cpm_forward_steps(results_data: Dict[str, Any]) -> List[Step]:
    """
    Generate CPM forward-pass worked-solution steps.

    Shows ES and EF calculation for each activity in topological order.
    """
    import networkx as nx

    graph = results_data.get("graph")
    if graph is None:
        return []

    steps: List[Step] = []
    topo_order = list(nx.topological_sort(graph))

    for node in topo_order:
        if node in ("START", "END"):
            continue
        data = graph.nodes[node]
        dur = data.get("duration", 0)
        es = data.get("ES", 0)
        ef = data.get("EF", 0)

        preds = [p for p in graph.predecessors(node) if p != "START"]
        if preds:
            pred_efs = [f"EF({p})={graph.nodes[p].get('EF', 0)}" for p in preds]
            sub_es = f"ES = max({', '.join(pred_efs)}) = {es}"
        else:
            sub_es = f"ES = 0  (no predecessors)"

        sub_ef = f"EF = ES + Duration = {es} + {dur}"

        is_critical = data.get("float", 1) == 0
        steps.append(Step(
            title=f"Activity {node}",
            formula="ES = max(EF of predecessors);  EF = ES + Duration",
            substitution=f"{sub_es}\n{sub_ef}",
            result=f"ES = {es},  EF = {ef}",
            rag="red" if is_critical else "",
        ))

    return [Step(
        title="Forward Pass — Early Start (ES) & Early Finish (EF)",
        formula="ES = max(EF of all predecessors);  EF = ES + Duration",
        interpretation="Process activities in topological order (left → right).",
        children=steps,
    )]


def cpm_backward_steps(results_data: Dict[str, Any]) -> List[Step]:
    """
    Generate CPM backward-pass worked-solution steps.

    Shows LF and LS calculation for each activity in reverse topological order.
    """
    import networkx as nx

    graph = results_data.get("graph")
    if graph is None:
        return []

    steps: List[Step] = []
    proj_dur = results_data.get("project_duration", 0)
    topo_order = list(reversed(list(nx.topological_sort(graph))))

    for node in topo_order:
        if node in ("START", "END"):
            continue
        data = graph.nodes[node]
        dur = data.get("duration", 0)
        ls = data.get("LS", 0)
        lf = data.get("LF", 0)
        flt = data.get("float", 0)

        succs = [s for s in graph.successors(node) if s != "END"]
        if succs:
            succ_lss = [f"LS({s})={graph.nodes[s].get('LS', 0)}" for s in succs]
            sub_lf = f"LF = min({', '.join(succ_lss)}) = {lf}"
        else:
            sub_lf = f"LF = {proj_dur}  (end activity)"

        sub_ls = f"LS = LF − Duration = {lf} − {dur}"
        sub_float = f"Float = LS − ES = {ls} − {data.get('ES', 0)}"

        is_critical = flt == 0
        steps.append(Step(
            title=f"Activity {node}",
            formula="LF = min(LS of successors);  LS = LF − Duration;  Float = LS − ES",
            substitution=f"{sub_lf}\n{sub_ls}\n{sub_float}",
            result=f"LS = {ls},  LF = {lf},  Float = {flt}",
            interpretation="Critical!" if is_critical else f"Float = {flt} (non-critical)",
            rag="red" if is_critical else "green",
        ))

    return [Step(
        title="Backward Pass — Late Finish (LF), Late Start (LS) & Float",
        formula="LF = min(LS of all successors);  LS = LF − Duration;  Float = LS − ES",
        interpretation=f"Process activities in reverse topological order (right → left). Project duration = {proj_dur}.",
        children=steps,
    )]


# ════════════════════════════════════════════════════════════════════
#  Serialisation + Public Wrappers (called by API endpoints)
# ════════════════════════════════════════════════════════════════════

def _step_to_dict(step: Step) -> Dict[str, Any]:
    """Convert a Step dataclass tree to a JSON-serialisable dict."""
    d: Dict[str, Any] = {
        "title": step.title,
        "formula": step.formula,
        "substitution": step.substitution,
        "result": step.result,
        "explanation": step.interpretation,
        "rag": step.rag,
    }
    if step.children:
        d["children"] = [_step_to_dict(c) for c in step.children]
    return d


def generate_cpm_steps(graph: Any, critical_paths: Any) -> List[Dict[str, Any]]:
    """Wrapper for the web API — returns serialised CPM forward + backward steps."""
    results_data = {"graph": graph, "critical_paths": critical_paths}
    forward = cpm_forward_steps(results_data)
    backward = cpm_backward_steps(results_data)
    return [_step_to_dict(s) for s in forward + backward]


def generate_pert_steps(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Wrapper for the web API — returns serialised PERT steps."""
    raw = pert_steps(results)
    return [_step_to_dict(s) for s in raw]


def generate_evm_steps(bac: float, pv: float, ev: float, ac: float) -> List[Dict[str, Any]]:
    """Wrapper for the web API — returns serialised EVM steps."""
    kpis: Dict[str, Any] = {"bac": bac, "pv": pv, "ev": ev, "ac": ac}
    # Compute derived KPIs so evm_steps can use them
    if ac:
        kpis["cpi"] = ev / ac
    if pv:
        kpis["spi"] = ev / pv
    raw = evm_steps(kpis)
    return [_step_to_dict(s) for s in raw]
