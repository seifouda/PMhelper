"""
PMhelper Edu — Financial Calculations Engine (V2 Phase 3A).

Provides six standalone financial analysis functions that work on a
simple input model: an initial investment plus a list of periodic
(usually annual) cash flows.

Supported metrics
-----------------
1. **Payback Period** — number of periods until cumulative cash flows
   recover the initial investment.
2. **Discounted Payback Period** — same but discounts each cash flow
   before accumulating.
3. **ROI** — Return on Investment = (Total Gains − Initial Cost) / Initial Cost × 100 %
4. **NPV** — Net Present Value = Σ CFₜ / (1 + r)ᵗ   (including t=0 outlay)
5. **IRR** — Internal Rate of Return: r where NPV = 0
   (bisection search; returns ``None`` if no real root found)
6. **Profitability Index** — PV of future inflows / |Initial Investment|
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ════════════════════════════════════════════════════════════════════
#  Data containers
# ════════════════════════════════════════════════════════════════════

@dataclass
class FinancialInputs:
    """Raw inputs for a financial analysis."""
    initial_investment: float          # positive number (the outlay)
    cash_flows: List[float]            # CF per period starting at t=1
    discount_rate: float = 0.10        # e.g. 0.10 = 10 %


@dataclass
class PaybackDetail:
    """Per-period detail row for payback tables."""
    period: int
    cash_flow: float
    discounted_cf: float
    cumulative: float
    discounted_cumulative: float


@dataclass
class FinancialResult:
    """All six metric values + supporting detail rows."""
    payback_period: Optional[float]            # periods; None if never recovered
    # periods; None if never recovered
    discounted_payback: Optional[float]
    roi: float                                 # %
    npv: float
    # decimal rate; None if not found
    irr: Optional[float]
    profitability_index: float

    payback_details: List[PaybackDetail] = field(default_factory=list)
    interpretation: dict = field(default_factory=dict)


# ════════════════════════════════════════════════════════════════════
#  Engine
# ════════════════════════════════════════════════════════════════════

class FinancialCalcs:
    """Stateless financial metrics calculator."""

    # ── NPV ──────────────────────────────────────────────────────

    @staticmethod
    def npv(initial_investment: float,
            cash_flows: List[float],
            rate: float) -> float:
        """
        NPV = -C₀ + Σ CFₜ / (1+r)ᵗ  for t = 1 … n.

        *initial_investment* should be a positive number (the cash outlay
        at t=0 is treated as negative).
        """
        pv_future = sum(
            cf / ((1 + rate) ** (t + 1))
            for t, cf in enumerate(cash_flows)
        )
        return -initial_investment + pv_future

    # ── IRR (bisection) ──────────────────────────────────────────

    @staticmethod
    def irr(initial_investment: float,
            cash_flows: List[float],
            lo: float = -0.9999,
            hi: float = 10.0,
            tol: float = 1e-7,
            max_iter: int = 200) -> Optional[float]:
        """
        Bisection search for the rate r where NPV = 0.

        Returns ``None`` if the NPV function does not change sign over
        [lo, hi] (i.e. the investment never pays back or always pays back
        regardless of rate).
        """
        def _npv(r: float) -> float:
            return FinancialCalcs.npv(initial_investment, cash_flows, r)

        f_lo = _npv(lo)
        f_hi = _npv(hi)

        if f_lo * f_hi > 0:
            return None  # no sign change → no root in range

        for _ in range(max_iter):
            mid = (lo + hi) / 2.0
            f_mid = _npv(mid)
            if abs(f_mid) < tol or (hi - lo) / 2.0 < tol:
                return round(mid, 8)
            if f_lo * f_mid < 0:
                hi = mid
                f_hi = f_mid
            else:
                lo = mid
                f_lo = f_mid

        return round((lo + hi) / 2.0, 8)

    # ── Payback (simple & discounted) ────────────────────────────

    @staticmethod
    def _payback_details(
        initial_investment: float,
        cash_flows: List[float],
        rate: float,
    ) -> List[PaybackDetail]:
        """Build period-by-period payback table."""
        rows: List[PaybackDetail] = []
        cum = 0.0
        dcum = 0.0
        for t, cf in enumerate(cash_flows, start=1):
            dcf = cf / ((1 + rate) ** t)
            cum += cf
            dcum += dcf
            rows.append(PaybackDetail(
                period=t,
                cash_flow=round(cf, 4),
                discounted_cf=round(dcf, 4),
                cumulative=round(cum, 4),
                discounted_cumulative=round(dcum, 4),
            ))
        return rows

    @staticmethod
    def payback_period(
        initial_investment: float,
        cash_flows: List[float],
        details: Optional[List[PaybackDetail]] = None,
    ) -> Optional[float]:
        """
        Simple payback: fractional number of periods until cumulative CF
        reaches *initial_investment*.  Returns ``None`` if never recovered.
        """
        cum = 0.0
        for t, cf in enumerate(cash_flows, start=1):
            prev_cum = cum
            cum += cf
            if cum >= initial_investment:
                # Linear interpolation within the period
                remaining = initial_investment - prev_cum
                frac = remaining / cf if cf != 0 else 0.0
                return round(t - 1 + frac, 4)
        return None

    @staticmethod
    def discounted_payback(
        initial_investment: float,
        cash_flows: List[float],
        rate: float,
    ) -> Optional[float]:
        """
        Discounted payback: fractional periods until cumulative discounted CF
        reaches *initial_investment*.
        """
        cum = 0.0
        for t, cf in enumerate(cash_flows, start=1):
            dcf = cf / ((1 + rate) ** t)
            prev_cum = cum
            cum += dcf
            if cum >= initial_investment:
                remaining = initial_investment - prev_cum
                frac = remaining / dcf if dcf != 0 else 0.0
                return round(t - 1 + frac, 4)
        return None

    # ── ROI ──────────────────────────────────────────────────────

    @staticmethod
    def roi(initial_investment: float, cash_flows: List[float]) -> float:
        """
        ROI = (Total Net Cash Flows − Initial Investment) / Initial Investment × 100 %
        """
        total_cf = sum(cash_flows)
        if initial_investment == 0:
            return 0.0
        return round(((total_cf - initial_investment) /
                     initial_investment) * 100.0, 4)

    # ── Profitability Index ───────────────────────────────────────

    @staticmethod
    def profitability_index(
        initial_investment: float,
        cash_flows: List[float],
        rate: float,
    ) -> float:
        """
        PI = PV of future inflows / |Initial Investment|

        PI > 1 → accept;  PI < 1 → reject;  PI = 1 → breakeven.
        """
        if initial_investment == 0:
            return 0.0
        pv_inflows = sum(
            cf / ((1 + rate) ** (t + 1))
            for t, cf in enumerate(cash_flows)
        )
        return round(pv_inflows / initial_investment, 4)

    # ── Combined entry point ─────────────────────────────────────

    @classmethod
    def calculate(cls, inputs: FinancialInputs) -> FinancialResult:
        """
        Run all six metrics for the given *inputs* and return a
        :class:`FinancialResult` with per-period detail rows.

        Parameters
        ----------
        inputs : FinancialInputs

        Returns
        -------
        FinancialResult
        """
        rate = inputs.discount_rate
        inv = inputs.initial_investment
        cfs = inputs.cash_flows

        # Build payback detail table (used by multiple metrics + step
        # generator)
        details = cls._payback_details(inv, cfs, rate)

        pb = cls.payback_period(inv, cfs, details)
        dpb = cls.discounted_payback(inv, cfs, rate)
        roi = cls.roi(inv, cfs)
        npv_val = cls.npv(inv, cfs, rate)
        irr_val = cls.irr(inv, cfs)
        pi = cls.profitability_index(inv, cfs, rate)

        # Build plain-English interpretations
        interp: dict = {}

        if pb is None:
            interp["payback"] = "Investment is NEVER recovered from cash flows."
        else:
            interp["payback"] = (
                f"Initial investment recovered after {pb:.2f} periods."
            )

        if dpb is None:
            interp["discounted_payback"] = (
                "Investment is never recovered when discounting cash flows."
            )
        else:
            interp["discounted_payback"] = (
                f"Discounted payback: {
                    dpb:.2f} periods at {
                    rate * 100:.1f}% discount rate.")

        interp["roi"] = (
            f"ROI of {roi:.2f}% — "
            + ("positive return over total project life." if roi > 0
               else "project does not pay back on a simple ROI basis.")
        )

        interp["npv"] = (
            f"NPV = {npv_val:,.2f}. "
            + ("Project creates value — ACCEPT." if npv_val > 0
               else "Project destroys value — REJECT." if npv_val < 0
               else "Breakeven project.")
        )

        if irr_val is None:
            interp["irr"] = "IRR could not be computed (no real root found)."
        else:
            interp["irr"] = (
                f"IRR = {irr_val * 100:.2f}%. "
                + (f"Exceeds hurdle rate ({rate * 100:.1f}%) — ACCEPT."
                   if irr_val > rate
                   else f"Below hurdle rate ({rate * 100:.1f}%) — REJECT.")
            )

        interp["pi"] = (
            f"Profitability Index = {pi:.4f}. "
            + ("PI > 1: project creates value per dollar invested."
               if pi > 1.0
               else "PI < 1: project destroys value." if pi < 1.0
               else "PI = 1: breakeven.")
        )

        return FinancialResult(
            payback_period=pb,
            discounted_payback=dpb,
            roi=roi,
            npv=round(npv_val, 4),
            irr=round(irr_val * 100, 4) if irr_val is not None else None,
            profitability_index=pi,
            payback_details=details,
            interpretation=interp,
        )
