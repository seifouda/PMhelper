"""
PMhelper Edu — Risk Assessment Step Generator (V2 Phase 6).

Provides educational step trees for:
  * risk_assessment_theory_steps()  — how the 5×5 matrix works
  * risk_scoring_steps()            — computing score for one risk
  * response_strategy_steps()       — choosing and applying a strategy
  * residual_risk_steps()           — computing residual exposure
  * full_register_steps()           — overview for an entire register
"""

from __future__ import annotations

from typing import List, TYPE_CHECKING

from pmhelper.core.step_generators_edu import Step

if TYPE_CHECKING:
    from pmhelper.core.risk_register_edu import Risk, RiskRegister


# ════════════════════════════════════════════════════════════════════
#  Theory overview
# ════════════════════════════════════════════════════════════════════

def risk_assessment_theory_steps() -> List[Step]:
    """Four-step theory walkthrough: 5×5 matrix, scoring, strategies, residual."""
    return [
        Step(
            title="Step 1 — What is a Risk Assessment Matrix?",
            formula="Risk Score = Probability Score (1–5) × Impact Score (1–5)",
            substitution="Range: 1×1 = 1  to  5×5 = 25",
            result="Risk Score ∈ [1, 25]",
            interpretation=(
                "A 5×5 Risk Assessment Matrix places each risk on a grid "
                "using two discrete rating scales (1=Very Low, 5=Very High). "
                "The cell colour indicates risk zone: "
                "🟢 Low (1–4), 🟡 Medium (5–9), 🟠 High (10–15), 🔴 Critical (16–25)."
            ),
            rag="G",
            children=[],
        ),
        Step(
            title="Step 2 — Scoring Scales",
            formula=(
                "Probability Score:\n"
                "  1 = Rare (< 10%)\n"
                "  2 = Unlikely (10–30%)\n"
                "  3 = Possible (30–50%)\n"
                "  4 = Likely (50–70%)\n"
                "  5 = Almost Certain (> 70%)\n\n"
                "Impact Score:\n"
                "  1 = Insignificant\n"
                "  2 = Minor\n"
                "  3 = Moderate\n"
                "  4 = Major\n"
                "  5 = Catastrophic"
            ),
            substitution="",
            result="",
            interpretation=(
                "The ratings are ordinal (1–5 labels). "
                "Project teams agree on consistent definitions before scoring. "
                "Use team consensus or a facilitator to reduce subjectivity."
            ),
            rag="G",
            children=[],
        ),
        Step(
            title="Step 3 — Response Strategy Selection",
            formula=(
                "Threats:       Avoid | Transfer | Mitigate | Accept\n"
                "Opportunities: Exploit | Share | Enhance | Accept"
            ),
            substitution=(
                "Avoid    — eliminate the risk entirely (change scope/plan)\n"
                "Transfer — shift impact to third party (insurance, contracts)\n"
                "Mitigate — reduce P or I (testing, prototypes, training)\n"
                "Accept   — acknowledge & monitor (active or passive)\n"
                "Exploit  — ensure the opportunity occurs\n"
                "Share    — partner with another party to capture benefit\n"
                "Enhance  — increase P or I for the opportunity"
            ),
            result="",
            interpretation=(
                "Strategy choice depends on cost/benefit analysis. "
                "High/Critical risks usually warrant Avoid or Mitigate. "
                "Low risks are often Accepted. "
                "After applying a strategy, assign Residual P and I scores."
            ),
            rag="A",
            children=[],
        ),
        Step(
            title="Step 4 — Residual Risk & Response Effectiveness",
            formula=(
                "Residual Score = Residual_P × Residual_I\n"
                "Effectiveness (%) = (Original_Score − Residual_Score) / "
                "Original_Score × 100"
            ),
            substitution="",
            result="",
            interpretation=(
                "Residual risk is the risk remaining AFTER the response is implemented. "
                "A good response plan drives Critical/High risks down to Low/Medium. "
                "Effectiveness > 50% is generally considered strong mitigation."
            ),
            rag="G",
            children=[],
        ),
    ]


# ════════════════════════════════════════════════════════════════════
#  Per-risk scoring
# ════════════════════════════════════════════════════════════════════

def risk_scoring_steps(risk: "Risk") -> List[Step]:
    """Three steps: rate P, rate I, compute score and zone."""
    from pmhelper.core.risk_register_edu import risk_zone
    zone = risk_zone(risk.risk_score)
    return [
        Step(
            title=f"Step 1 — Assess Probability for '{risk.name}'",
            formula="Probability Score (1=Rare ... 5=Almost Certain)",
            substitution=f"Assigned: P = {risk.prob_score}",
            result=f"Probability Score = {risk.prob_score}",
            interpretation=(
                f"A score of {risk.prob_score} means "
                f"{'Rare' if risk.prob_score == 1 else 'Unlikely' if risk.prob_score == 2 else 'Possible' if risk.prob_score == 3 else 'Likely' if risk.prob_score == 4 else 'Almost Certain'} "
                f"probability of occurrence."
            ),
            rag="G",
            children=[],
        ),
        Step(
            title=f"Step 2 — Assess Impact for '{risk.name}'",
            formula="Impact Score (1=Insignificant ... 5=Catastrophic)",
            substitution=f"Assigned: I = {risk.impact_score}",
            result=f"Impact Score = {risk.impact_score}",
            interpretation=(
                f"A score of {risk.impact_score} means "
                f"{'Insignificant' if risk.impact_score == 1 else 'Minor' if risk.impact_score == 2 else 'Moderate' if risk.impact_score == 3 else 'Major' if risk.impact_score == 4 else 'Catastrophic'} "
                f"impact on the project."
            ),
            rag="G",
            children=[],
        ),
        Step(
            title=f"Step 3 — Compute Risk Score for '{risk.name}'",
            formula="Risk Score = P × I",
            substitution=f"Risk Score = {risk.prob_score} × {risk.impact_score} = {risk.risk_score:.0f}",
            result=f"Risk Score = {risk.risk_score:.0f}  →  Zone: {zone}",
            interpretation=(
                f"Risk '{risk.name}' scores {risk.risk_score:.0f} out of 25. "
                f"This places it in the {zone} zone "
                f"({'🟢' if zone == 'Low' else '🟡' if zone == 'Medium' else '🟠' if zone == 'High' else '🔴'} "
                f"{zone})."
            ),
            rag=(
                "G" if zone == "Low" else
                "A" if zone == "Medium" else
                "R"
            ),
            children=[],
        ),
    ]


# ════════════════════════════════════════════════════════════════════
#  Response strategy
# ════════════════════════════════════════════════════════════════════

def response_strategy_steps(risk: "Risk") -> List[Step]:
    """Three steps: strategy rationale, plan description, effectiveness preview."""
    from pmhelper.core.risk_register_edu import risk_zone
    strategy_name = risk.response_strategy.value if risk.response_strategy else "Not assigned"
    original_zone  = risk_zone(risk.risk_score)
    residual_zone  = risk_zone(risk.residual_score)

    # Effectiveness for this individual risk
    eff = 0.0
    if risk.risk_score > 0:
        eff = (risk.risk_score - risk.residual_score) / risk.risk_score * 100

    return [
        Step(
            title=f"Step 1 — Strategy Context for '{risk.name}'",
            formula="Threat strategies: Avoid | Transfer | Mitigate | Accept",
            substitution=f"Selected strategy: {strategy_name}",
            result=f"Strategy = {strategy_name}",
            interpretation=(
                _strategy_rationale(risk.response_strategy, original_zone)
            ),
            rag="A",
            children=[],
        ),
        Step(
            title="Step 2 — Response Plan Details",
            formula="Owner × Cost × Description",
            substitution=(
                f"Owner: {risk.response_owner or '(not assigned)'}\n"
                f"Estimated Cost: {risk.response_cost:,.2f}\n"
                f"Description: {risk.response_description or '(none)'}\n"
                f"Trigger: {risk.trigger_conditions or '(none)'}\n"
                f"Contingency: {risk.contingency_plan or '(none)'}"
            ),
            result="",
            interpretation=(
                "A complete response plan documents WHO is responsible, WHAT they do, "
                "HOW much it costs, and WHEN to act (trigger conditions). "
                "The contingency plan is activated if the risk actually occurs."
            ),
            rag="A",
            children=[],
        ),
        Step(
            title="Step 3 — Residual Risk After Response",
            formula=(
                "Residual Score = Residual_P × Residual_I\n"
                "Effectiveness = (Original − Residual) / Original × 100 %"
            ),
            substitution=(
                f"Residual Score = {risk.residual_probability} × {risk.residual_impact} "
                f"= {risk.residual_score:.0f}\n"
                f"Effectiveness = ({risk.risk_score:.0f} − {risk.residual_score:.0f}) / "
                f"{risk.risk_score:.0f} × 100 = {eff:.1f} %"
            ),
            result=(
                f"Residual Score = {risk.residual_score:.0f}  "
                f"({original_zone} → {residual_zone})"
            ),
            interpretation=(
                f"After applying '{strategy_name}', the risk moves from "
                f"{original_zone} zone (score {risk.risk_score:.0f}) to "
                f"{residual_zone} zone (score {risk.residual_score:.0f}). "
                f"Response effectiveness: {eff:.1f}%."
            ),
            rag=(
                "G" if residual_zone in ("Low", "Medium") else
                "A" if residual_zone == "High" else
                "R"
            ),
            children=[],
        ),
    ]


# ════════════════════════════════════════════════════════════════════
#  Full register overview
# ════════════════════════════════════════════════════════════════════

def full_register_steps(register: "RiskRegister") -> List[Step]:
    """Summary steps for a whole risk register (scoring, ranking, zones, effectiveness)."""
    register.recompute_scores()
    register.update_ranks()

    zones = register.zone_counts()
    total_score  = sum(r.risk_score for r in register.risks)
    total_resid  = register.total_residual_exposure()
    effectiveness = register.response_effectiveness()
    top5 = register.risks_by_score()[:5]

    return [
        Step(
            title="Step 1 — Risk Registry Scoring Summary",
            formula="Risk Score = P × I  for each risk",
            substitution="\n".join(
                f"  {r.id}: {r.prob_score} × {r.impact_score} = {r.risk_score:.0f} ({r.zone})"
                for r in register.risks_by_score()
            ) or "  (No risks in register)",
            result=f"Total Score = {total_score:.0f}",
            interpretation=(
                f"Register contains {len(register.risks)} risk(s). "
                f"Total risk score = {total_score:.0f}. "
                f"Zones: {zones['Critical']} Critical, {zones['High']} High, "
                f"{zones['Medium']} Medium, {zones['Low']} Low."
            ),
            rag=(
                "R" if zones["Critical"] > 0 else
                "A" if zones["High"] > 0 else
                "G"
            ),
            children=[],
        ),
        Step(
            title="Step 2 — Risk Ranking (Top 5)",
            formula="Rank by Risk Score descending",
            substitution="\n".join(
                f"  Rank {r.risk_rank}: {r.id} — {r.name} (Score={r.risk_score:.0f})"
                for r in top5
            ) or "  (No risks)",
            result=f"Top risk: {top5[0].name if top5 else 'N/A'}",
            interpretation=(
                "Highest-score risks need immediate attention. "
                "Ensure all Critical and High risks have defined response strategies."
            ),
            rag="A",
            children=[],
        ),
        Step(
            title="Step 3 — Response Effectiveness Overview",
            formula="Effectiveness (%) = (Total_Original − Total_Residual) / Total_Original × 100",
            substitution=(
                f"Effectiveness = ({total_score:.0f} − {total_resid:.0f}) / "
                f"{total_score:.0f} × 100 = {effectiveness:.1f} %"
            ),
            result=f"Portfolio Effectiveness = {effectiveness:.1f} %",
            interpretation=(
                f"After all planned responses, portfolio effectiveness is {effectiveness:.1f}%. "
                f"Residual total exposure = {total_resid:.0f}. "
                f"Target: drive all Critical risks below High zone post-response."
            ),
            rag=(
                "G" if effectiveness >= 50 else
                "A" if effectiveness >= 20 else
                "R"
            ),
            children=[],
        ),
    ]


# ════════════════════════════════════════════════════════════════════
#  Internal helpers
# ════════════════════════════════════════════════════════════════════

def _strategy_rationale(strategy, zone: str) -> str:
    from pmhelper.core.risk_register_edu import ResponseStrategy
    if strategy is None:
        return (
            f"No strategy assigned yet. "
            f"For a risk in the {zone} zone, consider: "
            + ("Avoid or Mitigate" if zone in ("Critical", "High") else "Accept or Mitigate")
        )
    rationales = {
        ResponseStrategy.AVOID:    "Eliminate the risk by changing the plan, scope, or approach.",
        ResponseStrategy.TRANSFER: "Shift the impact to a third party via insurance or contract clauses.",
        ResponseStrategy.MITIGATE: "Reduce the probability or impact to an acceptable level.",
        ResponseStrategy.ACCEPT:   "Acknowledge the risk; take no action unless it materialises.",
        ResponseStrategy.EXPLOIT:  "Ensure the opportunity definitely occurs.",
        ResponseStrategy.SHARE:    "Partner with another party to share the benefit.",
        ResponseStrategy.ENHANCE:  "Increase probability or impact of the positive event.",
    }
    return rationales.get(strategy, "")
