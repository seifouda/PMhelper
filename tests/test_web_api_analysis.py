"""Tests for the /api/web analysis endpoints.

These exercise the router through the deployed app (``server.main``) so a
route that is mounted in one app object but not the other cannot pass here
while 404-ing in production.

The EVM and Monte Carlo routes previously imported ``EVMCalculator`` and
``MonteCarloSimulator`` -- names that never existed. The lazy import sat
inside a broad ``except Exception``, so every call returned a generic 500
rather than failing loudly. These tests pin the real function-based API.
"""

import pytest
from fastapi.testclient import TestClient

from pmhelper.server.api.routes.web import limiter
from pmhelper.server.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _disable_rate_limiting():
    """The routes are rate limited (Monte Carlo at 5/min); several tests here
    would otherwise 429 rather than exercise the handler."""
    limiter.enabled = False
    yield
    limiter.enabled = True


# ── EVM ──────────────────────────────────────────────────────────────────

def _evm_body(**overrides):
    body = {
        "project": {
            "project_name": "P",
            "bac": 1000.0,
            "periods": [
                {"index": 0, "label": "M1", "pv_cumulative": 200.0,
                 "ev_cumulative": 150.0, "ac_cumulative": 180.0},
                {"index": 1, "label": "M2", "pv_cumulative": 500.0,
                 "ev_cumulative": 400.0, "ac_cumulative": 450.0},
            ],
            "tasks": [],
        }
    }
    body.update(overrides)
    return body


def test_evm_returns_hand_checked_kpis():
    """EV=400, PV=500, AC=450 -> CV=-50, SV=-100, CPI=8/9, SPI=0.8."""
    response = client.post("/api/web/analysis/evm", json=_evm_body())

    assert response.status_code == 200
    data = response.json()
    assert data["period_index"] == 1

    kpis = data["kpis"]
    assert kpis["ev"] == 400.0
    assert kpis["pv"] == 500.0
    assert kpis["ac"] == 450.0
    assert kpis["cv"] == -50.0
    assert kpis["sv"] == -100.0
    assert kpis["cpi"] == pytest.approx(400 / 450)
    assert kpis["spi"] == pytest.approx(0.8)
    assert kpis["errors"] == {}


def test_evm_current_period_index_selects_that_period():
    """Index 0 must report the first period, not the latest."""
    response = client.post(
        "/api/web/analysis/evm", json=_evm_body(current_period_index=0))

    assert response.status_code == 200
    data = response.json()
    assert data["period_index"] == 0
    assert data["kpis"]["ev"] == 150.0
    assert data["kpis"]["ac"] == 180.0


def test_evm_index_beyond_range_clamps_to_last_period():
    response = client.post(
        "/api/web/analysis/evm", json=_evm_body(current_period_index=99))

    assert response.status_code == 200
    assert response.json()["period_index"] == 1


def test_evm_honours_explicit_bac_over_task_budgets():
    """EVMProject auto-computes BAC from tasks; the request's BAC must win."""
    body = _evm_body()
    body["project"]["tasks"] = [{
        "task_id": "T1", "name": "t", "budget": 7.0,
        "pct_complete": 0.0, "planned_start": 0, "planned_finish": 1,
    }]

    response = client.post("/api/web/analysis/evm", json=body)

    assert response.status_code == 200
    assert response.json()["kpis"]["bac"] == 1000.0


def test_evm_without_periods_is_client_error():
    response = client.post(
        "/api/web/analysis/evm", json={"project": {"bac": 1.0, "periods": []}})

    assert response.status_code == 400
    assert "period" in response.json()["detail"].lower()


# ── Monte Carlo ──────────────────────────────────────────────────────────

def _mc_body(**overrides):
    body = {
        "activities": [
            {"id": "A", "activity": "A", "duration": 5, "predecessors": [],
             "optimistic": 3, "most_likely": 5, "pessimistic": 9},
            {"id": "B", "activity": "B", "duration": 4, "predecessors": ["A"],
             "optimistic": 2, "most_likely": 4, "pessimistic": 7},
        ],
        "n_trials": 200,
        "seed": 42,
    }
    body.update(overrides)
    return body


def test_monte_carlo_returns_full_trial_series():
    response = client.post("/api/web/analysis/monte-carlo", json=_mc_body())

    assert response.status_code == 200
    data = response.json()
    assert data["n_trials"] == 200
    assert len(data["durations"]) == 200
    assert len(data["costs"]) == 200
    assert data["p50_duration"] <= data["p80_duration"] <= data["p90_duration"]


def test_monte_carlo_marks_sole_path_always_critical():
    """A -> B is the only path, so both are on the critical path every trial."""
    response = client.post("/api/web/analysis/monte-carlo", json=_mc_body())

    frequencies = response.json()["cp_frequencies"]
    assert frequencies["A"] == 1.0
    assert frequencies["B"] == 1.0


def test_monte_carlo_seed_is_reproducible():
    first = client.post("/api/web/analysis/monte-carlo", json=_mc_body())
    second = client.post("/api/web/analysis/monte-carlo", json=_mc_body())

    assert first.json()["durations"] == second.json()["durations"]
    assert first.json()["seed_used"] == second.json()["seed_used"] == 42


def test_monte_carlo_samples_cost_from_task_budgets():
    response = client.post("/api/web/analysis/monte-carlo", json=_mc_body(
        bac=100.0,
        task_budgets=[{"task_id": "A", "budget": 50.0},
                      {"task_id": "B", "budget": 40.0}],
    ))

    assert response.status_code == 200
    data = response.json()
    assert all(cost > 0 for cost in data["costs"])
    assert 0.0 <= data["p_cost_within_bac"] <= 1.0


def test_monte_carlo_without_budgets_yields_zero_cost():
    """Budgets are optional; their absence must not error."""
    response = client.post("/api/web/analysis/monte-carlo", json=_mc_body())

    assert response.status_code == 200
    data = response.json()
    assert set(data["costs"]) == {0.0}
    assert data["p_cost_within_bac"] == 0.0


def test_monte_carlo_without_activities_is_client_error():
    response = client.post(
        "/api/web/analysis/monte-carlo",
        json={"activities": [], "n_trials": 100})

    assert response.status_code == 400
    assert "activity" in response.json()["detail"].lower()


# ── Learn Mode step walkthroughs ─────────────────────────────────────────
#
# Same failure family as EVM/Monte Carlo above, in a different place.
# `/analysis/steps/pert` called `generate_pert_steps(analyzer.analyze(...))`,
# but `analyze()` returns a 3-tuple `(graph, critical_paths, critical_acts)`
# while the generator called `.get()` on it -> AttributeError -> swallowed by
# `except Exception` -> 500 on every call. `pert.service.ts` calls this, so
# the Learn Mode panel was broken in the deployed app. Untested until now.

def _steps_activities():
    return [
        {"id": "A", "activity": "Design", "duration": 5, "optimistic": 2,
         "most_likely": 5, "pessimistic": 8, "predecessors": []},
        {"id": "B", "activity": "Build", "duration": 3, "optimistic": 1,
         "most_likely": 3, "pessimistic": 6, "predecessors": ["A"]},
    ]


def test_pert_steps_returns_walkthrough():
    response = client.post("/api/web/analysis/steps/pert",
                           json={"activities": _steps_activities()})

    assert response.status_code == 200, response.text
    steps = response.json()
    assert len(steps) >= 4
    titles = " ".join(s["title"] for s in steps)
    assert "Expected Time" in titles
    assert "Variance" in titles
    assert "Standard Deviation" in titles


def test_pert_steps_maths_reaches_the_client():
    """var(A)=((8-2)/6)^2=1.0, var(B)=((6-1)/6)^2=0.6944 -> 1.6944; sigma=1.302.

    Guards more than "not a 500": a wrong results_data shape yields steps
    that render but report 0.0000.
    """
    response = client.post("/api/web/analysis/steps/pert",
                           json={"activities": _steps_activities()})

    steps = response.json()
    proj_var = next(s for s in steps if "Project Variance" in s["title"])
    std_dev = next(s for s in steps if "Standard Deviation" in s["title"])
    assert "1.69" in proj_var["result"]
    assert "1.30" in std_dev["result"]


def test_cpm_steps_returns_walkthrough():
    response = client.post("/api/web/analysis/steps/cpm",
                           json={"activities": _steps_activities()})

    assert response.status_code == 200, response.text
    steps = response.json()
    assert steps
    # _step_to_dict renames `interpretation` -> `explanation`
    assert {"title", "explanation"} <= set(steps[0])


def test_evm_steps_returns_walkthrough():
    """Takes the same EVMRequest shape as /analysis/evm; the route pulls
    bac/pv/ev/ac off the selected period itself."""
    response = client.post("/api/web/analysis/steps/evm", json=_evm_body())

    assert response.status_code == 200, response.text
    steps = response.json()
    assert steps
    assert {"title", "explanation"} <= set(steps[0])
