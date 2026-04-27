"""
PMhelper Edu — Cost Estimation Step Generator (V2 Phase 5).

Produces educational :class:`~pmhelper.core.step_generators_edu.Step` trees
that walk students through each of the 7 cost estimation techniques.

Entry points
------------
Each function returns ``List[Step]`` suitable for a :class:`WorkedSolutionWindow`.

* ``analogous_steps(result, reference_cost, factors)``
* ``bottom_up_steps(result, work_packages)``
* ``work_element_steps(result, elements)``
* ``power_sizing_steps(result, ref_cost, ref_cap, new_cap, exponent)``
* ``unit_factor_steps(result, items)``
* ``learning_curve_steps(result, T1, rate, N)``
* ``cost_estimation_theory_steps()`` — pure theory, no result needed
"""

from __future__ import annotations

import math
from typing import List, Optional

from pmhelper.core.step_generators_edu import Step
from pmhelper.core.cost_estimation import (
    CostEstimateResult,
    AdjustmentFactor,
    WorkPackage,
    WorkElement,
    UnitFactorItem,
)


# ════════════════════════════════════════════════════════════════════
#  Theory (no calculation needed)
# ════════════════════════════════════════════════════════════════════

def cost_estimation_theory_steps() -> List[Step]:
    """Educational overview of all 7 cost estimation techniques."""
    steps: List[Step] = []

    steps.append(
        Step(
            title="Step 1 — What is Cost Estimation?",
            formula="Estimated Cost = f(scope, resources, time, risk)",
            interpretation=(
                "Cost estimation is the process of predicting the total cost of "
                "completing a project. Estimates become more accurate as the project "
                "progresses (funnel of uncertainty).\n\n"
                "Common accuracy ranges by phase:\n"
                "  • Rough Order of Magnitude (ROM): −50% to +100%\n"
                "  • Budgetary: −10% to +25%\n"
                "  • Definitive: −5% to +10%"),
        ))

    steps.append(Step(
        title="Step 2 — Top-Down vs Bottom-Up",
        formula="Top-Down: C_new = C_ref × adjustment  |  Bottom-Up: C = Σ WP_i",
        interpretation=(
            "Top-Down (Analogous): Use a past similar project as reference and "
            "adjust for size, complexity and risk. Fast but less accurate.\n\n"
            "Bottom-Up: Estimate each work package individually and sum up. "
            "Slow but most accurate."
        ),
        children=[
            Step(
                title="Analogous Estimation",
                formula="C_new = C_ref × F₁ × F₂ × … × Fₙ",
                interpretation="Best used in early phases when detailed scope is unknown.",
            ),
            Step(
                title="Bottom-Up Estimation",
                formula="C = Σ (Labour_i + Material_i + Equip_i) × (1 + Overhead_i%)",
                interpretation="Requires a complete WBS; most accurate technique.",
            ),
        ],
    ))

    steps.append(Step(
        title="Step 3 — Parametric / Mathematical Models",
        formula="C_new = C_ref × (S_new/S_ref)^x",
        interpretation=(
            "Parametric models use statistical relationships between cost and "
            "project parameters (size, weight, capacity, etc.).\n\n"
            "Power Sizing exponent x:\n"
            "  x < 1 → economies of scale\n"
            "  x = 1 → linear scaling\n"
            "  x > 1 → diseconomies of scale"
        ),
        children=[
            Step(
                title="Power Sizing / Cost-Capacity Index",
                formula="C_new = C_ref × (S_new / S_ref) ^ x",
                interpretation="x ≈ 0.6 for chemical plants; x ≈ 1.0 for linear processes.",
            ),
            Step(
                title="Unit / Factor Method",
                formula="Cost_i = UnitCost_i × Quantity_i × Factor_i",
                interpretation="Simple and transparent; widely used in construction.",
            ),
        ],
    ))

    steps.append(Step(
        title="Step 4 — Learning Curves",
        formula="T_N = T₁ × N^b,   b = ln(learning_rate) / ln(2)",
        interpretation=(
            "Learning curve theory states that each time cumulative "
            "production doubles, the average cost per unit decreases to a "
            "fixed fraction (the learning rate) of its prior value.\n\n"
            "Wright's Law (unit time model):\n"
            "  T_N = T₁ × N ^ b\n"
            "  b   = ln(r) / ln(2)  (negative for r < 1)\n\n"
            "E.g. 80% learning curve: every doubling → average unit cost × 0.80."
        ),
        children=[
            Step(
                title="Compute exponent b",
                formula="b = ln(learning_rate) / ln(2)",
                interpretation="For an 80% curve: b = ln(0.8)/ln(2) ≈ −0.3219",
            ),
            Step(
                title="Compute unit N cost",
                formula="T_N = T₁ × N ^ b",
                interpretation="Plug in N (target unit) and T₁ (first unit cost).",
            ),
        ],
    ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Analogous (Top-Down)
# ════════════════════════════════════════════════════════════════════

def analogous_steps(
    result: CostEstimateResult,
    reference_cost: float,
    factors: Optional[List[AdjustmentFactor]] = None,
) -> List[Step]:
    factors = factors or []
    steps: List[Step] = []

    steps.append(Step(
        title="Step 1 — Identify Reference Project Cost",
        formula="C_ref = cost of historical comparable project",
        substitution=f"C_ref = {reference_cost:,.2f}",
        result=f"{reference_cost:,.2f}",
        interpretation=(
            "Select a completed project that is comparable in scope, "
            "technology and context to the new project."
        ),
    ))

    if factors:
        children = []
        combined = math.prod(f.factor for f in factors)
        for af in factors:
            children.append(Step(
                title=f"Factor — {af.name}",
                formula=f"F({af.name})",
                substitution=f"{af.factor}",
                result=f"{af.factor}",
                interpretation=(
                    f"Adjustment factor {af.factor} "
                    f"({'increases' if af.factor > 1 else 'decreases' if af.factor < 1 else 'no change to'} "
                    f"the reference cost)."
                ),
            ))
        steps.append(Step(
            title="Step 2 — Apply Adjustment Factors",
            formula="Combined Factor = F₁ × F₂ × … × Fₙ",
            substitution=" × ".join(str(f.factor) for f in factors),
            result=f"{combined:.6f}",
            children=children,
            interpretation=(
                f"Multiply all {len(factors)} adjustment factor(s) together. "
                f"Combined multiplier = {combined:.6f}."
            ),
        ))
    else:
        steps.append(
            Step(
                title="Step 2 — No Adjustment Factors",
                interpretation="No adjustment factors provided; estimate equals the reference cost.",
            ))

    steps.append(Step(
        title="Step 3 — Calculate Estimated Cost",
        formula="C_new = C_ref × Combined Factor",
        substitution=result.substitution_text,
        result=f"{result.total_cost:,.2f}",
        interpretation=result.interpretation,
        rag="green" if result.total_cost > 0 else "amber",
    ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Bottom-Up
# ════════════════════════════════════════════════════════════════════

def bottom_up_steps(
    result: CostEstimateResult,
    work_packages: List[WorkPackage],
) -> List[Step]:
    steps: List[Step] = []

    steps.append(Step(
        title="Step 1 — List Work Packages",
        formula="WBS Work Packages define the scope",
        interpretation=(
            f"{len(work_packages)} work package(s) identified from the WBS."
        ),
    ))

    wp_children = []
    for wp in work_packages:
        wp_children.append(Step(
            title=f"Work Package: {wp.name}",
            formula="WP Cost = (Labour + Material + Equipment) × (1 + Overhead%)",
            substitution=(
                f"({wp.labour_cost:,.2f} + {wp.material_cost:,.2f} + "
                f"{wp.equipment_cost:,.2f}) × (1 + {wp.overhead_pct}%)"
            ),
            result=f"{wp.total:,.2f}",
        ))

    steps.append(
        Step(
            title="Step 2 — Estimate Each Work Package",
            formula="Cost_i = (L_i + M_i + E_i) × (1 + Overhead%_i)",
            children=wp_children,
            interpretation="Estimate direct costs (labour, materials, equipment) plus overhead for each WP.",
        ))

    steps.append(Step(
        title="Step 3 — Sum All Work Packages",
        formula="C_total = Σ WP_i",
        substitution=result.substitution_text,
        result=f"{result.total_cost:,.2f}",
        interpretation=result.interpretation,
        rag="green",
    ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Work Element
# ════════════════════════════════════════════════════════════════════

def work_element_steps(
    result: CostEstimateResult,
    elements: List[WorkElement],
) -> List[Step]:
    steps: List[Step] = []

    steps.append(Step(
        title="Step 1 — Identify Work Elements",
        interpretation=f"{len(elements)} work element(s) identified.",
    ))

    el_children = []
    for el in elements:
        el_children.append(Step(
            title=f"Element: {el.name}",
            formula="Cost = Hours × Rate + Material + Equipment",
            substitution=(
                f"{el.hours} hrs × {el.hourly_rate}/hr "
                f"+ {el.material_cost} + {el.equipment_cost}"
            ),
            result=f"{el.total:,.2f}",
        ))

    steps.append(
        Step(
            title="Step 2 — Cost Each Element",
            formula="Cost_i = (H_i × Rate_i) + Material_i + Equipment_i",
            children=el_children,
            interpretation="Break down each element into labour, material and equipment cost.",
        ))

    steps.append(Step(
        title="Step 3 — Sum Elements",
        formula="C_total = Σ Cost_i",
        substitution=result.substitution_text,
        result=f"{result.total_cost:,.2f}",
        interpretation=result.interpretation,
        rag="green",
    ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Power Sizing / Cost-Capacity
# ════════════════════════════════════════════════════════════════════

def power_sizing_steps(
    result: CostEstimateResult,
    ref_cost: float,
    ref_capacity: float,
    new_capacity: float,
    exponent: float,
) -> List[Step]:
    ratio = new_capacity / ref_capacity
    scale = ratio ** exponent

    steps = [
        Step(
            title="Step 1 — Identify Reference Parameters",
            formula="C_ref, S_ref",
            substitution=f"C_ref = {ref_cost:,.2f},  S_ref = {ref_capacity}",
            interpretation="The reference project's known cost and capacity.",
        ),
        Step(
            title="Step 2 — Compute Capacity Ratio",
            formula="Ratio = S_new / S_ref",
            substitution=f"{new_capacity} / {ref_capacity}",
            result=f"{ratio:.6f}",
            interpretation="How many times larger (or smaller) the new project's capacity is.",
        ),
        Step(
            title="Step 3 — Apply Power Sizing Exponent",
            formula="Scale Factor = Ratio ^ x",
            substitution=f"{ratio:.6f} ^ {exponent}",
            result=f"{scale:.6f}",
            interpretation=(
                f"Exponent x = {exponent}.  "
                f"{'Economies of scale apply (x<1).' if exponent < 1 else 'Linear scaling (x=1).' if exponent == 1 else 'Diseconomies of scale (x>1).'}"
            ),
        ),
        Step(
            title="Step 4 — Compute Estimated Cost",
            formula="C_new = C_ref × Scale Factor",
            substitution=result.substitution_text,
            result=f"{result.total_cost:,.2f}",
            interpretation=result.interpretation,
            rag="green",
        ),
    ]
    return steps


# ════════════════════════════════════════════════════════════════════
#  Unit / Factor
# ════════════════════════════════════════════════════════════════════

def unit_factor_steps(
    result: CostEstimateResult,
    items: List[UnitFactorItem],
) -> List[Step]:
    item_children = [
        Step(
            title=f"Item: {item.name}",
            formula="Cost = UnitCost × Quantity × Factor",
            substitution=f"{item.unit_cost} × {item.quantity} × {item.factor}",
            result=f"{item.extended_cost:,.2f}",
        )
        for item in items
    ]

    return [
        Step(
            title="Step 1 — List Items with Unit Costs",
            formula="Each item has: UnitCost, Quantity, Factor",
            children=item_children,
            interpretation=f"{len(items)} line item(s) provided.",
        ),
        Step(
            title="Step 2 — Compute Extended Cost per Item",
            formula="Cost_i = UnitCost_i × Qty_i × Factor_i",
            interpretation="Multiply unit cost by quantity and any adjustment factor.",
        ),
        Step(
            title="Step 3 — Sum All Items",
            formula="C_total = Σ Cost_i",
            substitution=result.substitution_text,
            result=f"{result.total_cost:,.2f}",
            interpretation=result.interpretation,
            rag="green",
        ),
    ]


# ════════════════════════════════════════════════════════════════════
#  Learning Curves
# ════════════════════════════════════════════════════════════════════

def learning_curve_steps(
    result: CostEstimateResult,
    t1: float,
    learning_rate: float,
    target_unit: int,
) -> List[Step]:
    b = math.log(learning_rate) / math.log(2)
    t_n = result.total_cost
    lr_pct = learning_rate * 100

    steps = [
        Step(
            title="Step 1 — Understand the Learning Curve",
            formula="Each time cumulative production doubles → avg cost × learning_rate",
            interpretation=(
                f"This is a {lr_pct:.0f}% learning curve.  "
                f"Every doubling of cumulative output reduces the average unit cost "
                f"to {lr_pct:.0f}% of its previous value."
            ),
        ),
        Step(
            title="Step 2 — Compute the Learning Exponent b",
            formula="b = ln(learning_rate) / ln(2)",
            substitution=f"b = ln({learning_rate}) / ln(2) = {math.log(learning_rate):.6f} / {math.log(2):.6f}",
            result=f"b = {b:.6f}",
            interpretation=(
                "b is negative for learning rates < 1, meaning unit costs "
                "decline as production increases."
            ),
        ),
        Step(
            title=f"Step 3 — Compute Cost for Unit {target_unit}",
            formula="T_N = T₁ × N ^ b",
            substitution=f"T_{target_unit} = {t1} × {target_unit} ^ {b:.6f}",
            result=f"T_{target_unit} = {t_n:,.4f}",
            interpretation=result.interpretation,
            rag="green",
        ),
        Step(
            title="Step 4 — Cumulative Totals",
            formula="Cumulative Total = Σ T_n  for n = 1 to N",
            substitution=f"N = {target_unit}",
            result=(
                f"Cumulative Total = {result.extra.get('cumulative_total', 0):,.4f}\n"
                f"Cumulative Average = {result.extra.get('cumulative_average', 0):,.4f}"
            ),
            interpretation=(
                "The cumulative average declines continuously as more units "
                "are produced — this is the fundamental benefit of the learning effect."
            ),
        ),
    ]
    return steps
