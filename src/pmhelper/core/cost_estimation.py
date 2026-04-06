"""
PMhelper Edu — Cost Estimation Engine (V2 Phase 5).

Seven classic PM cost-estimation techniques, each in its own class:

1. **AnalogousEstimator** — scale from a reference project with adjustment factors
2. **BottomUpEstimator** — sum of work-package level estimates (labour + materials + equipment + overhead)
3. **WorkElementEstimator** — cost = labour + materials + equipment per work element
4. **PowerSizingEstimator** — C₂ = C₁ × (S₂/S₁)^x  (also called Cost-Capacity Index)
5. **UnitFactorEstimator** — Cost = Σ UnitCost × Quantity × Factor per line item
6. **CostCapacityEstimator** — alias / extended version of power sizing with clearer naming
7. **LearningCurveEstimator** — Tₙ = T₁ × N^b,  b = ln(rate)/ln(2)

Each estimator exposes:
  * ``estimate(**inputs) → CostEstimateResult``
  * The result contains ``total_cost``, ``breakdown``, ``formula_text``, ``substitution_text``.

All arithmetic uses Python ``float``; no external numerical libraries are required.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ════════════════════════════════════════════════════════════════════
#  Shared result container
# ════════════════════════════════════════════════════════════════════

@dataclass
class CostEstimateResult:
    """
    Output produced by every estimator.

    Attributes
    ----------
    total_cost : float
        Final estimated cost (or time for learning curves).
    breakdown : list of (label, value) pairs
        Per-item costs for display in a results table.
    formula_text : str
        Human-readable formula string (no substitution yet).
    substitution_text : str
        Formula with values substituted in.
    interpretation : str
        Plain-English summary sentence.
    extra : dict
        Technique-specific extra output (e.g. cumulative learning curves).
    """
    total_cost: float
    breakdown: List[Tuple[str, float]] = field(default_factory=list)
    formula_text: str = ""
    substitution_text: str = ""
    interpretation: str = ""
    extra: Dict = field(default_factory=dict)


# ════════════════════════════════════════════════════════════════════
#  Technique 1 — Analogous (Top-Down) Estimation
# ════════════════════════════════════════════════════════════════════

@dataclass
class AdjustmentFactor:
    """One multiplicative adjustment applied to the reference cost."""
    name: str            # e.g. "Complexity"
    factor: float        # e.g. 1.15  (1.0 = no change, >1 = increase)


class AnalogousEstimator:
    """
    Top-Down (Analogous) Estimator.

    Formula::

        C_new = C_ref × F₁ × F₂ × … × Fₙ

    where *F_i* are adjustment factors.
    """

    def estimate(
        self,
        reference_cost: float,
        factors: Optional[List[AdjustmentFactor]] = None,
    ) -> CostEstimateResult:
        """
        Parameters
        ----------
        reference_cost
            Cost of the historical reference project.
        factors
            List of :class:`AdjustmentFactor`.  Empty = no adjustment.

        Returns
        -------
        CostEstimateResult
        """
        factors = factors or []
        combined = math.prod(f.factor for f in factors) if factors else 1.0
        total = reference_cost * combined

        breakdown = [("Reference Cost", reference_cost)]
        for af in factors:
            breakdown.append((f"× {af.name}", af.factor))
        breakdown.append(("= Estimated Cost", total))

        factor_str = " · ".join(
            f"F_{i+1}" for i in range(len(factors))) or "1"
        formula = f"C_new = C_ref × {factor_str}"

        parts = " × ".join(
            [f"{reference_cost:,.2f}"] +
            [f"{f.factor}" for f in factors]) or f"{reference_cost:,.2f}"
        subst = f"C_new = {parts} = {total:,.2f}"

        interp = (
            f"Estimated cost = {total:,.2f}  "
            f"(adjusted from reference cost of {reference_cost:,.2f} "
            f"using {len(factors)} factor(s), combined multiplier = {combined:.4f})."
        )
        return CostEstimateResult(
            total_cost=total, breakdown=breakdown,
            formula_text=formula, substitution_text=subst,
            interpretation=interp,
        )


# ════════════════════════════════════════════════════════════════════
#  Technique 2 — Bottom-Up Estimation
# ════════════════════════════════════════════════════════════════════

@dataclass
class WorkPackage:
    """One work-package line in a bottom-up estimate."""
    name: str
    labour_cost: float   = 0.0
    material_cost: float = 0.0
    equipment_cost: float = 0.0
    overhead_pct: float  = 0.0   # percentage, e.g. 10.0 = 10 %

    @property
    def direct_cost(self) -> float:
        return self.labour_cost + self.material_cost + self.equipment_cost

    @property
    def overhead_amount(self) -> float:
        return self.direct_cost * (self.overhead_pct / 100.0)

    @property
    def total(self) -> float:
        return self.direct_cost + self.overhead_amount


class BottomUpEstimator:
    """
    Bottom-Up Estimator.

    Formula::

        C_total = Σ (Labour_i + Material_i + Equipment_i) × (1 + Overhead_i%)
    """

    def estimate(
        self,
        work_packages: List[WorkPackage],
    ) -> CostEstimateResult:
        if not work_packages:
            return CostEstimateResult(
                total_cost=0.0,
                formula_text="C_total = Σ WP_i",
                substitution_text="No work packages",
                interpretation="No items to estimate.",
            )

        breakdown = []
        total = 0.0
        for wp in work_packages:
            t = wp.total
            breakdown.append((wp.name, t))
            total += t

        formula = "C_total = Σ (Labour_i + Material_i + Equipment_i) × (1 + Overhead_i%)"
        terms = [f"WP('{wp.name}')={wp.total:,.2f}" for wp in work_packages]
        subst = "C_total = " + " + ".join(terms) + f" = {total:,.2f}"
        interp = (
            f"Total bottom-up estimate = {total:,.2f}  "
            f"({len(work_packages)} work package(s))."
        )
        return CostEstimateResult(
            total_cost=total, breakdown=breakdown,
            formula_text=formula, substitution_text=subst,
            interpretation=interp,
        )


# ════════════════════════════════════════════════════════════════════
#  Technique 3 — Work Element (Template) Estimator
# ════════════════════════════════════════════════════════════════════

@dataclass
class WorkElement:
    """One cost element (labour + materials + equipment)."""
    name: str
    hours: float        = 0.0   # labour hours
    hourly_rate: float  = 0.0   # currency per hour
    material_cost: float = 0.0
    equipment_cost: float = 0.0

    @property
    def labour_cost(self) -> float:
        return self.hours * self.hourly_rate

    @property
    def total(self) -> float:
        return self.labour_cost + self.material_cost + self.equipment_cost


class WorkElementEstimator:
    """
    Work Element (Template) Estimator.

    Formula::

        Cost_i = (Hours_i × Rate_i) + Material_i + Equipment_i
        C_total = Σ Cost_i
    """

    def estimate(
        self,
        elements: List[WorkElement],
    ) -> CostEstimateResult:
        if not elements:
            return CostEstimateResult(
                total_cost=0.0,
                formula_text="C_total = Σ (H_i × R_i + M_i + E_i)",
                interpretation="No elements to estimate.",
            )

        breakdown = []
        total = 0.0
        for el in elements:
            c = el.total
            breakdown.append((el.name, c))
            total += c

        formula = "C_total = Σ (Hours_i × Rate_i + Material_i + Equipment_i)"
        subst_parts = [
            f"({el.hours}×{el.hourly_rate}+{el.material_cost}+{el.equipment_cost})={el.total:,.2f}"
            for el in elements
        ]
        subst = "C_total = " + " + ".join(subst_parts) + f" = {total:,.2f}"
        interp = (
            f"Total work-element estimate = {total:,.2f}  "
            f"({len(elements)} element(s))."
        )
        return CostEstimateResult(
            total_cost=total, breakdown=breakdown,
            formula_text=formula, substitution_text=subst,
            interpretation=interp,
            extra={
                "labour_total": sum(el.labour_cost for el in elements),
                "material_total": sum(el.material_cost for el in elements),
                "equipment_total": sum(el.equipment_cost for el in elements),
            },
        )


# ════════════════════════════════════════════════════════════════════
#  Technique 4 & 6 — Power Sizing / Cost-Capacity Index
# ════════════════════════════════════════════════════════════════════

class PowerSizingEstimator:
    """
    Power Sizing / Cost-Capacity Index Estimator.

    Formula::

        C_new = C_ref × (S_new / S_ref) ^ x

    where *x* is the capacity scaling exponent (typically 0.6 for chemical
    plant, closer to 1.0 for linear systems).

    This covers both the "Power Sizing Model" (5.6) and the
    "Cost-Capacity Index" (5.4) — they are the same formula.
    """

    def estimate(
        self,
        reference_cost: float,
        reference_capacity: float,
        new_capacity: float,
        exponent: float = 0.6,
    ) -> CostEstimateResult:
        """
        Raises
        ------
        ValueError
            If capacities are non-positive.
        """
        if reference_capacity <= 0 or new_capacity <= 0:
            raise ValueError("Capacities must be positive.")

        ratio = new_capacity / reference_capacity
        total = reference_cost * (ratio ** exponent)

        formula = "C_new = C_ref × (S_new / S_ref) ^ x"
        subst = (
            f"C_new = {reference_cost:,.2f} × "
            f"({new_capacity} / {reference_capacity}) ^ {exponent} = {total:,.2f}"
        )
        interp = (
            f"Estimated cost = {total:,.2f}  "
            f"(capacity ratio = {ratio:.4f}, exponent = {exponent}, "
            f"scale factor = {ratio**exponent:.4f})."
        )
        breakdown = [
            ("Reference Cost", reference_cost),
            ("Reference Capacity", reference_capacity),
            ("New Capacity", new_capacity),
            ("Capacity Ratio", ratio),
            ("Exponent (x)", exponent),
            ("Scale Factor", ratio ** exponent),
            ("Estimated Cost", total),
        ]
        return CostEstimateResult(
            total_cost=total, breakdown=breakdown,
            formula_text=formula, substitution_text=subst,
            interpretation=interp,
            extra={"ratio": ratio, "scale_factor": ratio ** exponent},
        )


# Alias for plan item 5.4 (Cost-Capacity Index = same formula)
CostCapacityEstimator = PowerSizingEstimator


# ════════════════════════════════════════════════════════════════════
#  Technique 5 — Unit / Factor Method
# ════════════════════════════════════════════════════════════════════

@dataclass
class UnitFactorItem:
    """One line item in a Unit/Factor estimate."""
    name: str
    unit_cost: float
    quantity: float
    factor: float = 1.0   # adjustment/location/complexity factor

    @property
    def extended_cost(self) -> float:
        return self.unit_cost * self.quantity * self.factor


class UnitFactorEstimator:
    """
    Unit / Factor Estimator.

    Formula::

        Cost_i = UnitCost_i × Quantity_i × Factor_i
        C_total = Σ Cost_i
    """

    def estimate(
        self,
        items: List[UnitFactorItem],
    ) -> CostEstimateResult:
        if not items:
            return CostEstimateResult(
                total_cost=0.0,
                formula_text="C_total = Σ UnitCost_i × Qty_i × Factor_i",
                interpretation="No items to estimate.",
            )

        breakdown = [(item.name, item.extended_cost) for item in items]
        total = sum(item.extended_cost for item in items)

        formula = "C_total = Σ (UnitCost_i × Quantity_i × Factor_i)"
        subst_parts = [
            f"({item.unit_cost}×{item.quantity}×{item.factor})={item.extended_cost:,.2f}"
            for item in items
        ]
        subst = "C_total = " + " + ".join(subst_parts) + f" = {total:,.2f}"
        interp = (
            f"Total unit/factor estimate = {total:,.2f}  "
            f"({len(items)} line item(s))."
        )
        return CostEstimateResult(
            total_cost=total, breakdown=breakdown,
            formula_text=formula, substitution_text=subst,
            interpretation=interp,
        )


# ════════════════════════════════════════════════════════════════════
#  Technique 7 — Learning Curves
# ════════════════════════════════════════════════════════════════════

@dataclass
class LearningCurvePoint:
    """Data for unit N on the learning curve."""
    unit_number: int
    unit_time: float            # time / cost for this single unit
    cumulative_average: float   # average per unit up to and including N
    cumulative_total: float     # sum from unit 1 to N


class LearningCurveEstimator:
    """
    Learning Curve Estimator (Wright's model).

    Formula::

        T_N = T₁ × N^b,   where b = ln(learning_rate) / ln(2)

    *learning_rate* is typically expressed as a decimal (e.g. 0.80 for an
    80% learning curve).  Each time cumulative production doubles, the
    cumulative *average* time per unit drops to ``learning_rate`` of its
    previous value.

    This implementation uses the **unit time formula** T_N = T₁ × N^b.
    Cumulative averages are computed by numerical summation (exact for
    the Wright unit-time model).
    """

    def estimate(
        self,
        first_unit_cost: float,
        learning_rate: float,
        target_unit: int,
        *,
        build_curve: bool = True,
    ) -> CostEstimateResult:
        """
        Parameters
        ----------
        first_unit_cost
            Cost/time for the very first unit (T₁).
        learning_rate
            Decimal fraction (0 < r ≤ 1).  E.g. 0.80 = 80 % learning curve.
        target_unit
            The unit number N we want the cost for.
        build_curve
            If True, include per-unit data for all units 1 … target_unit in
            ``extra["curve"]``.

        Raises
        ------
        ValueError
            If *learning_rate* is outside (0, 1] or *target_unit* < 1.
        """
        if not (0 < learning_rate <= 1.0):
            raise ValueError(
                f"learning_rate must be in (0, 1], got {learning_rate}."
            )
        if target_unit < 1:
            raise ValueError(f"target_unit must be ≥ 1, got {target_unit}.")

        b = math.log(learning_rate) / math.log(2)
        t_n = first_unit_cost * (target_unit ** b)

        # Cumulative total (numerical sum from 1 to N)
        points: List[LearningCurvePoint] = []
        cum_total = 0.0
        for n in range(1, target_unit + 1):
            unit_t = first_unit_cost * (n ** b)
            cum_total += unit_t
            cum_avg = cum_total / n
            points.append(LearningCurvePoint(
                unit_number=n,
                unit_time=unit_t,
                cumulative_average=cum_avg,
                cumulative_total=cum_total,
            ))

        formula = "T_N = T₁ × N^b,  b = ln(learning_rate) / ln(2)"
        b_str = f"ln({learning_rate})/ln(2) = {b:.6f}"
        subst = (
            f"b = {b_str}\n"
            f"T_{target_unit} = {first_unit_cost} × {target_unit}^{b:.6f}"
            f" = {t_n:,.4f}"
        )
        lr_pct = learning_rate * 100
        interp = (
            f"Unit {target_unit} cost = {t_n:,.4f}  "
            f"({lr_pct:.0f}% learning curve, b = {b:.6f}, "
            f"cumulative total for {target_unit} unit(s) = {cum_total:,.4f})."
        )
        breakdown = [
            ("T₁ (first unit cost)", first_unit_cost),
            ("Learning Rate", learning_rate),
            ("Exponent b", b),
            (f"T_{target_unit} (target unit cost)", t_n),
            ("Cumulative Total", cum_total),
            (f"Cumulative Average (unit 1–{target_unit})", cum_total / target_unit),
        ]
        return CostEstimateResult(
            total_cost=t_n,
            breakdown=breakdown,
            formula_text=formula,
            substitution_text=subst,
            interpretation=interp,
            extra={
                "b": b,
                "cumulative_total": cum_total,
                "cumulative_average": cum_total / target_unit,
                "curve": [
                    {
                        "n": pt.unit_number,
                        "unit_time": pt.unit_time,
                        "cum_avg": pt.cumulative_average,
                        "cum_total": pt.cumulative_total,
                    }
                    for pt in points
                ] if build_curve else [],
            },
        )


# ════════════════════════════════════════════════════════════════════
#  Convenience method registry (used by the tab + tests)
# ════════════════════════════════════════════════════════════════════

METHOD_LABELS = [
    "Top-Down (Analogous)",
    "Bottom-Up",
    "Work Element",
    "Power Sizing",
    "Unit / Factor",
    "Cost-Capacity Index",
    "Learning Curves",
]
