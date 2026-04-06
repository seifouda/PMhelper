"""
Tests for pmhelper.core.financial_calcs  (V2 Phase 3A).

Coverage
--------
- Payback Period (simple)
- Discounted Payback Period
- ROI
- NPV
- IRR
- Profitability Index
- Combined FinancialCalcs.calculate()
- Edge cases: zero investment, never-recovered investment, single CF
"""

import pytest
from pmhelper.core.financial_calcs import (
    FinancialCalcs,
    FinancialInputs,
    FinancialResult,
    PaybackDetail,
)

# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def simple_inputs():
    """$100k invested, $30k/yr for 5 years, 10% discount rate."""
    return FinancialInputs(
        initial_investment=100_000,
        cash_flows=[30_000, 30_000, 30_000, 30_000, 30_000],
        discount_rate=0.10,
    )


@pytest.fixture
def uneven_inputs():
    """$200k invested, uneven CFs, 8% rate — positive NPV scenario."""
    return FinancialInputs(
        initial_investment=200_000,
        cash_flows=[20_000, 40_000, 60_000, 80_000, 80_000, 60_000],
        discount_rate=0.08,
    )


@pytest.fixture
def bad_investment_inputs():
    """$200k invested, tiny CFs: negative NPV, PI < 1, never recovered."""
    return FinancialInputs(
        initial_investment=200_000,
        cash_flows=[10_000, 10_000, 10_000],
        discount_rate=0.08,
    )


@pytest.fixture
def breakeven_inputs():
    """NPV exactly 0 investment (IRR equals discount rate)."""
    return FinancialInputs(
        initial_investment=100,
        cash_flows=[110],
        discount_rate=0.10,
    )


# ── Payback Period ────────────────────────────────────────────────────

class TestPaybackPeriod:

    def test_even_cfs(self, simple_inputs):
        pb = FinancialCalcs.payback_period(
            simple_inputs.initial_investment, simple_inputs.cash_flows)
        # 3 full years cover 90k; 10k remains; 10k/30k ≈ 0.333 → 3.333
        assert abs(pb - 3.3333) < 0.01

    def test_uneven_cfs(self, uneven_inputs):
        pb = FinancialCalcs.payback_period(
            uneven_inputs.initial_investment, uneven_inputs.cash_flows)
        # t1=20k(cum 20), t2=40k(cum 60), t3=60k(cum 120), t4=80k(cum 200) → exactly 4
        assert abs(pb - 4.0) < 0.01

    def test_never_recovered(self):
        pb = FinancialCalcs.payback_period(500_000, [10_000, 10_000])
        assert pb is None

    def test_immediate_recovery(self):
        """If first CF covers investment entirely."""
        pb = FinancialCalcs.payback_period(50, [100, 100])
        assert abs(pb - 0.5) < 0.01

    def test_single_profitable_cf(self):
        pb = FinancialCalcs.payback_period(100, [200])
        assert abs(pb - 0.5) < 0.01

    def test_zero_investment(self):
        pb = FinancialCalcs.payback_period(0, [100, 200])
        # 0 investment → already recovered before t=1
        assert pb == 0.0 or pb is not None


# ── Discounted Payback ────────────────────────────────────────────────

class TestDiscountedPayback:

    def test_even_cfs(self, simple_inputs):
        dpb = FinancialCalcs.discounted_payback(
            simple_inputs.initial_investment,
            simple_inputs.cash_flows,
            simple_inputs.discount_rate,
        )
        # DF = 30k/(1.1^t); cumDPV crosses 100k between yr 4 and 5
        assert dpb is not None
        assert 4.0 < dpb < 5.0

    def test_never_recovered_discounted(self, bad_investment_inputs):
        # Sum of discounted CFs << 200k — never recovered
        dpb = FinancialCalcs.discounted_payback(
            bad_investment_inputs.initial_investment,
            bad_investment_inputs.cash_flows,
            bad_investment_inputs.discount_rate,
        )
        assert dpb is None

    def test_high_rate_never_recovered(self):
        dpb = FinancialCalcs.discounted_payback(10_000, [1_000], rate=0.50)
        assert dpb is None


# ── ROI ───────────────────────────────────────────────────────────────

class TestROI:

    def test_simple(self, simple_inputs):
        roi = FinancialCalcs.roi(
            simple_inputs.initial_investment, simple_inputs.cash_flows)
        # total CF = 150k; net gain = 50k; ROI = 50%
        assert abs(roi - 50.0) < 0.01

    def test_loss(self):
        roi = FinancialCalcs.roi(100, [30, 30])  # net = -40 → -40%
        assert abs(roi - (-40.0)) < 0.01

    def test_zero_investment(self):
        roi = FinancialCalcs.roi(0, [100, 200])
        assert roi == 0.0

    def test_breakeven(self):
        roi = FinancialCalcs.roi(100, [60, 40])
        assert abs(roi - 0.0) < 0.01


# ── NPV ───────────────────────────────────────────────────────────────

class TestNPV:

    def test_positive_npv(self, simple_inputs):
        npv = FinancialCalcs.npv(
            simple_inputs.initial_investment,
            simple_inputs.cash_flows,
            simple_inputs.discount_rate,
        )
        # Annuity factor = 3.7908 → PV = 113,724 → NPV ≈ 13,724
        assert abs(npv - 13_724) < 200  # tolerance ±200

    def test_negative_npv(self, bad_investment_inputs):
        npv = FinancialCalcs.npv(
            bad_investment_inputs.initial_investment,
            bad_investment_inputs.cash_flows,
            bad_investment_inputs.discount_rate,
        )
        assert npv < 0

    def test_single_cf(self):
        # NPV = -100 + 110/1.10 = 0
        npv = FinancialCalcs.npv(100, [110], 0.10)
        assert abs(npv) < 0.01

    def test_zero_rate(self):
        npv = FinancialCalcs.npv(100, [40, 40, 40], 0.0)
        assert abs(npv - 20.0) < 0.01

    def test_large_rate(self):
        npv = FinancialCalcs.npv(1_000, [1_000, 1_000], 1.0)
        # PV = 500 + 250 = 750 → NPV = -250
        assert abs(npv - (-250.0)) < 0.01


# ── IRR ───────────────────────────────────────────────────────────────

class TestIRR:

    def test_positive_irr(self, simple_inputs):
        irr = FinancialCalcs.irr(
            simple_inputs.initial_investment,
            simple_inputs.cash_flows,
        )
        # Known ≈ 15.24%
        assert irr is not None
        assert abs(irr - 0.1524) < 0.002

    def test_irr_breakeven(self, breakeven_inputs):
        # NPV = 0 at discount rate, so IRR should equal discount rate
        irr = FinancialCalcs.irr(
            breakeven_inputs.initial_investment,
            breakeven_inputs.cash_flows,
        )
        assert irr is not None
        assert abs(irr - 0.10) < 0.001

    def test_negative_irr_returns_none(self):
        # All-negative future cash flows → NPV always negative → no root
        irr = FinancialCalcs.irr(10_000, [-1, -1, -1])
        assert irr is None

    def test_irr_above_zero(self):
        irr = FinancialCalcs.irr(1_000, [600, 600])
        assert irr is not None
        assert irr > 0


# ── Profitability Index ───────────────────────────────────────────────

class TestProfitabilityIndex:

    def test_positive_pi(self, simple_inputs):
        pi = FinancialCalcs.profitability_index(
            simple_inputs.initial_investment,
            simple_inputs.cash_flows,
            simple_inputs.discount_rate,
        )
        # PV ≈ 113,724; PI ≈ 1.137
        assert abs(pi - 1.137) < 0.005

    def test_pi_less_than_one(self, bad_investment_inputs):
        pi = FinancialCalcs.profitability_index(
            bad_investment_inputs.initial_investment,
            bad_investment_inputs.cash_flows,
            bad_investment_inputs.discount_rate,
        )
        assert pi < 1.0

    def test_pi_breakeven(self, breakeven_inputs):
        pi = FinancialCalcs.profitability_index(
            breakeven_inputs.initial_investment,
            breakeven_inputs.cash_flows,
            breakeven_inputs.discount_rate,
        )
        assert abs(pi - 1.0) < 0.001

    def test_zero_investment(self):
        pi = FinancialCalcs.profitability_index(0, [100], 0.10)
        assert pi == 0.0


# ── Combined calculate() ──────────────────────────────────────────────

class TestFinancialCalcsCalculate:

    def test_returns_financial_result(self, simple_inputs):
        result = FinancialCalcs.calculate(simple_inputs)
        assert isinstance(result, FinancialResult)

    def test_all_fields_populated(self, simple_inputs):
        result = FinancialCalcs.calculate(simple_inputs)
        assert result.payback_period is not None
        assert result.discounted_payback is not None
        assert result.roi is not None
        assert result.npv is not None
        assert result.profitability_index is not None
        # IRR may be None for some inputs but should be a float here
        assert isinstance(result.irr, float)

    def test_payback_details_populated(self, simple_inputs):
        result = FinancialCalcs.calculate(simple_inputs)
        assert len(result.payback_details) == 5
        assert all(isinstance(d, PaybackDetail) for d in result.payback_details)

    def test_interpretation_dict_populated(self, simple_inputs):
        result = FinancialCalcs.calculate(simple_inputs)
        assert isinstance(result.interpretation, dict)
        assert len(result.interpretation) > 0

    def test_npv_matches_standalone(self, simple_inputs):
        result = FinancialCalcs.calculate(simple_inputs)
        standalone = FinancialCalcs.npv(
            simple_inputs.initial_investment,
            simple_inputs.cash_flows,
            simple_inputs.discount_rate,
        )
        assert abs(result.npv - standalone) < 0.001

    def test_irr_stored_as_percentage(self, simple_inputs):
        """IRR in FinancialResult is stored as percentage (e.g. 15.24 not 0.1524)."""
        result = FinancialCalcs.calculate(simple_inputs)
        assert result.irr is not None
        assert result.irr > 1.0  # must be percentage, not decimal

    def test_payback_detail_columns(self, simple_inputs):
        result = FinancialCalcs.calculate(simple_inputs)
        d = result.payback_details[0]
        assert d.period == 1
        assert d.cash_flow == 30_000
        assert abs(d.discounted_cf - 30_000 / 1.10) < 0.01
        assert abs(d.cumulative - 30_000) < 0.01
        assert abs(d.discounted_cumulative - 30_000 / 1.10) < 0.01

    def test_uneven_cfs_result(self, uneven_inputs):
        result = FinancialCalcs.calculate(uneven_inputs)
        assert result.payback_period is not None
        assert abs(result.payback_period - 4.0) < 0.01
        assert result.npv > 0  # 340k total CFs vs 200k investment is profitable

    def test_never_recovered(self):
        inputs = FinancialInputs(
            initial_investment=1_000_000,
            cash_flows=[1_000, 1_000],
            discount_rate=0.05,
        )
        result = FinancialCalcs.calculate(inputs)
        assert result.payback_period is None
        assert result.discounted_payback is None
