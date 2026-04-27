"""
PMhelper Edu — Financial Analysis Step Generator (V2 Phase 3A).

Produces :class:`~pmhelper.core.step_generators_edu.Step` trees for
each of the six financial metrics, driven by a
:class:`~pmhelper.core.financial_calcs.FinancialResult`.

One ``Step`` is generated per metric, each with child steps that walk
through the per-period arithmetic.
"""

from __future__ import annotations

from typing import List, Optional

from pmhelper.core.step_generators_edu import Step
from pmhelper.core.financial_calcs import FinancialInputs, FinancialResult


def financial_steps(
    inputs: FinancialInputs,
    result: FinancialResult,
    metrics: Optional[List[str]] = None,
) -> List[Step]:
    """
    Generate worked-solution steps for the chosen *metrics*.

    Parameters
    ----------
    inputs : FinancialInputs
    result : FinancialResult
        Output of :meth:`FinancialCalcs.calculate`.
    metrics : list of str, optional
        Subset of ``{"payback", "discounted_payback", "roi", "npv",
        "irr", "pi"}``.  If *None*, all six metrics are included.

    Returns
    -------
    list[Step]
    """
    _all = ["payback", "discounted_payback", "roi", "npv", "irr", "pi"]
    selected = [m.lower() for m in (metrics or _all)] if metrics else _all

    steps: List[Step] = []

    if "payback" in selected:
        steps.append(_payback_step(inputs, result))
    if "discounted_payback" in selected:
        steps.append(_disc_payback_step(inputs, result))
    if "roi" in selected:
        steps.append(_roi_step(inputs, result))
    if "npv" in selected:
        steps.append(_npv_step(inputs, result))
    if "irr" in selected:
        steps.append(_irr_step(inputs, result))
    if "pi" in selected:
        steps.append(_pi_step(inputs, result))

    return steps


# ── Individual metric step builders ─────────────────────────────────

def _payback_step(inputs: FinancialInputs, result: FinancialResult) -> Step:
    inv = inputs.initial_investment
    pb = result.payback_period
    rag = "green" if pb is not None else "red"

    children: List[Step] = []
    cum = 0.0
    for row in result.payback_details:
        prev_cum = cum
        cum = row.cumulative
        status = "✓ Recovered" if cum >= inv and prev_cum < inv else ""
        children.append(Step(
            title=f"Period {row.period}",
            formula="Cumulative = prev + CF",
            substitution=f"= {prev_cum:.2f} + {row.cash_flow:.2f}",
            result=f"= {cum:.2f}"
            + (f"  ← ≥ {inv:.2f} {status}" if status else ""),
        ))
        if cum >= inv:
            break

    pb_str = f"{pb:.2f}" if pb is not None else "Never"
    return Step(
        title="Payback Period",
        formula="Find t such that Σ CFₜ ≥ Initial Investment",
        substitution=f"Initial Investment = {inv:,.2f}",
        result=f"Payback = {pb_str} periods",
        interpretation=result.interpretation.get("payback", ""),
        rag=rag,
        children=children,
    )


def _disc_payback_step(
        inputs: FinancialInputs,
        result: FinancialResult) -> Step:
    inv = inputs.initial_investment
    rate = inputs.discount_rate
    dpb = result.discounted_payback
    rag = "green" if dpb is not None else "red"

    children: List[Step] = []
    cum = 0.0
    for row in result.payback_details:
        prev_cum = cum
        cum = row.discounted_cumulative
        status = "✓ Recovered" if cum >= inv and prev_cum < inv else ""
        children.append(Step(
            title=f"Period {row.period}",
            formula="DCFₜ = CFₜ / (1+r)ᵗ",
            substitution=(
                f"= {row.cash_flow:.2f} / (1 + {rate})^{row.period}"
                f" = {row.discounted_cf:.4f}"
            ),
            result=f"Cumulative DCF = {cum:.4f}"
            + (f"  ← ≥ {inv:.2f} {status}" if status else ""),
        ))
        if cum >= inv:
            break

    dpb_str = f"{dpb:.2f}" if dpb is not None else "Never"
    return Step(
        title="Discounted Payback Period",
        formula="Find t such that Σ [CFₜ / (1+r)ᵗ] ≥ Initial Investment",
        substitution=f"Discount rate r = {rate * 100:.1f}%",
        result=f"Discounted Payback = {dpb_str} periods",
        interpretation=result.interpretation.get("discounted_payback", ""),
        rag=rag,
        children=children,
    )


def _roi_step(inputs: FinancialInputs, result: FinancialResult) -> Step:
    inv = inputs.initial_investment
    total = sum(inputs.cash_flows)
    roi = result.roi
    rag = "green" if roi > 0 else "red"

    return Step(
        title="Return on Investment (ROI)",
        formula="ROI = (Total CF − C₀) / C₀ × 100%",
        substitution=f"= ({total:,.2f} − {inv:,.2f}) / {inv:,.2f} × 100",
        result=f"= {roi:.2f}%",
        interpretation=result.interpretation.get("roi", ""),
        rag=rag,
        children=[
            Step(
                title="Total Cash Flows",
                formula="Σ CFₜ for t = 1 … n",
                substitution=" + ".join(f"{cf:,.2f}" for cf in inputs.cash_flows),
                result=f"= {total:,.2f}",
            ),
            Step(
                title="Net Profit",
                formula="Total CF − Initial Investment",
                substitution=f"{total:,.2f} − {inv:,.2f}",
                result=f"= {total - inv:,.2f}",
            ),
        ],
    )


def _npv_step(inputs: FinancialInputs, result: FinancialResult) -> Step:
    inv = inputs.initial_investment
    rate = inputs.discount_rate
    npv = result.npv
    rag = "green" if npv > 0 else "red" if npv < 0 else "amber"

    pv_children: List[Step] = []
    for t, cf in enumerate(inputs.cash_flows, start=1):
        dcf = cf / ((1 + rate) ** t)
        pv_children.append(Step(
            title=f"t = {t}",
            formula="PVₜ = CFₜ / (1 + r)ᵗ",
            substitution=f"= {cf:,.2f} / (1 + {rate})^{t}",
            result=f"= {dcf:,.4f}",
        ))

    pv_sum = sum(cf / ((1 + rate) ** (t + 1))
                 for t, cf in enumerate(inputs.cash_flows))

    return Step(
        title="Net Present Value (NPV)",
        formula="NPV = -C₀ + Σ [CFₜ / (1+r)ᵗ]",
        substitution=f"C₀ = {inv:,.2f},  r = {rate * 100:.1f}%",
        result=f"NPV = {npv:,.4f}",
        interpretation=result.interpretation.get("npv", ""),
        rag=rag,
        children=[
            Step(
                title="Step 1 — Discount each cash flow",
                formula="PVₜ = CFₜ / (1 + r)ᵗ",
                children=pv_children,
            ),
            Step(
                title="Step 2 — Sum discounted cash flows",
                formula="Σ PVₜ",
                result=f"= {pv_sum:,.4f}",
            ),
            Step(
                title="Step 3 — Subtract initial investment",
                formula="NPV = Σ PVₜ − C₀",
                substitution=f"= {pv_sum:,.4f} − {inv:,.2f}",
                result=f"= {npv:,.4f}",
            ),
        ],
    )


def _irr_step(inputs: FinancialInputs, result: FinancialResult) -> Step:
    irr = result.irr
    rate = inputs.discount_rate

    if irr is None:
        return Step(
            title="Internal Rate of Return (IRR)",
            formula="Find r such that NPV(r) = 0",
            result="IRR could not be determined",
            interpretation="No real IRR exists for this cash flow pattern.",
            rag="red",
        )

    rag = "green" if irr > rate * 100 else "red"
    return Step(
        title="Internal Rate of Return (IRR)",
        formula="Solve: -C₀ + Σ [CFₜ / (1+r)ᵗ] = 0  for r",
        substitution=(
            "IRR found by bisection search — the rate that equates the "
            "present value of inflows to the initial investment."
        ),
        result=f"IRR = {irr:.2f}%",
        interpretation=result.interpretation.get("irr", ""),
        rag=rag,
        children=[
            Step(
                title="Method: Bisection",
                interpretation=(
                    "Narrow the search interval [lo, hi] by repeatedly "
                    "testing the midpoint until NPV(mid) ≈ 0."
                ),
            ),
            Step(
                title=f"NPV at IRR ({irr:.2f}%)",
                formula="NPV(IRR) ≈ 0",
                result="Confirmed numerically",
            ),
        ],
    )


def _pi_step(inputs: FinancialInputs, result: FinancialResult) -> Step:
    inv = inputs.initial_investment
    rate = inputs.discount_rate
    pi = result.profitability_index
    rag = "green" if pi > 1 else "red" if pi < 1 else "amber"

    pv_sum = sum(
        cf / ((1 + rate) ** (t + 1))
        for t, cf in enumerate(inputs.cash_flows)
    )

    return Step(
        title="Profitability Index (PI)",
        formula="PI = PV(future inflows) / C₀",
        substitution=f"= {pv_sum:,.4f} / {inv:,.2f}",
        result=f"PI = {pi:.4f}",
        interpretation=result.interpretation.get("pi", ""),
        rag=rag,
        children=[
            Step(
                title="PV of future inflows",
                formula="Σ CFₜ / (1+r)ᵗ   for t=1…n",
                result=f"= {pv_sum:,.4f}",
            ),
            Step(
                title="Divide by initial investment",
                formula="PI = PV_inflows / C₀",
                substitution=f"= {pv_sum:,.4f} / {inv:,.2f}",
                result=f"= {pi:.4f}",
                interpretation=(
                    "PI > 1 → each £/$ invested returns more than £/$1 in PV. "
                    "PI < 1 → project destroys value."
                ),
            ),
        ],
    )
