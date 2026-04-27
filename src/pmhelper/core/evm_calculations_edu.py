"""
PMhelper Edu — EVM Calculation Engine.
All functions are PURE — no GUI, state, or I/O imports.
"""

from __future__ import annotations
from typing import List, Dict, Any

from pmhelper.core.evm_models_edu import EVMProject, EVMTask


# ── Individual KPI Functions ──────────────────────────────────────────

def compute_ev(tasks: List[EVMTask]) -> float:
    """EV = Σ(budget × pct_complete / 100). Returns 0.0 for empty list."""
    return sum(t.budget * t.pct_complete / 100.0 for t in tasks)


def compute_cv(ev: float, ac: float) -> float:
    """Cost Variance = EV − AC."""
    return ev - ac


def compute_sv(ev: float, pv: float) -> float:
    """Schedule Variance = EV − PV."""
    return ev - pv


def compute_cpi(ev: float, ac: float) -> float:
    """Cost Performance Index = EV / AC."""
    if ac == 0:
        raise ValueError("AC is zero — CPI undefined")
    return ev / ac


def compute_spi(ev: float, pv: float) -> float:
    """Schedule Performance Index = EV / PV."""
    if pv == 0:
        raise ValueError("PV is zero — SPI undefined")
    return ev / pv


def compute_pc(ev: float, bac: float) -> float:
    """Percent Complete = (EV / BAC) × 100."""
    if bac == 0:
        raise ValueError("BAC is zero")
    return (ev / bac) * 100.0


def compute_ps(ac: float, bac: float) -> float:
    """Percent Spent = (AC / BAC) × 100."""
    if bac == 0:
        raise ValueError("BAC is zero")
    return (ac / bac) * 100.0


def compute_cr(cpi: float, spi: float) -> float:
    """Critical Ratio = CPI × SPI."""
    return cpi * spi


def compute_eac1(ac: float, bac: float, ev: float) -> float:
    """EAC₁ = AC + (BAC − EV). Assumes future performance at budget rate."""
    return ac + (bac - ev)


def compute_eac2(bac: float, cpi: float) -> float:
    """EAC₂ = BAC / CPI. Assumes future performance at current CPI rate."""
    if cpi == 0:
        raise ValueError("CPI is zero")
    return bac / cpi


def compute_eac3(ac: float, bac: float, ev: float,
                 cpi: float, spi: float) -> float:
    """EAC₃ = AC + (BAC − EV) / (CPI × SPI). Uses both cost & schedule performance."""
    cr = cpi * spi
    if cr == 0:
        raise ValueError("CPI × SPI is zero")
    return ac + (bac - ev) / cr


def compute_vac(bac: float, eac: float) -> float:
    """Variance at Completion = BAC − EAC."""
    return bac - eac


def compute_tcpi_bac(bac: float, ev: float, ac: float) -> float:
    """TCPI (BAC) = (BAC − EV) / (BAC − AC)."""
    if bac == ac:
        raise ValueError("BAC equals AC — TCPI undefined")
    return (bac - ev) / (bac - ac)


# ── Orchestrator ─────────────────────────────────────────────────────

def compute_all_kpis(project: EVMProject,
                     primary_eac: int = 1) -> Dict[str, Any]:
    """
    Compute all EVM KPIs from project data.

    Returns a flat dict with keys:
        ev, pv, ac, bac, cv, sv, cpi, spi, pc, ps, cr,
        eac1, eac2, eac3, vac, tcpi_bac, primary_eac_value
    Values are float or None (if undefined).
    An additional 'errors' key maps KPI name → error message.
    """
    ev = project.current_ev()
    pv = project.current_pv()
    ac = project.current_ac()
    bac = project.bac

    result: Dict[str, Any] = {
        "ev": ev, "pv": pv, "ac": ac, "bac": bac,
        "errors": {},
    }

    def _safe(name, fn, *args):
        try:
            result[name] = fn(*args)
        except ValueError as e:
            result[name] = None
            result["errors"][name] = str(e)

    # Variances (always defined)
    result["cv"] = compute_cv(ev, ac)
    result["sv"] = compute_sv(ev, pv)

    # Indices
    _safe("cpi", compute_cpi, ev, ac)
    _safe("spi", compute_spi, ev, pv)

    # Percent complete / spent
    _safe("pc", compute_pc, ev, bac)
    _safe("ps", compute_ps, ac, bac)

    # Critical Ratio — depends on CPI and SPI
    cpi = result.get("cpi")
    spi = result.get("spi")
    if cpi is not None and spi is not None:
        result["cr"] = compute_cr(cpi, spi)
    else:
        result["cr"] = None
        result["errors"]["cr"] = "CPI or SPI unavailable"

    # EAC variants
    result["eac1"] = compute_eac1(ac, bac, ev)
    _safe("eac2", compute_eac2, bac, cpi if cpi is not None else 0)
    if cpi is not None and spi is not None:
        _safe("eac3", compute_eac3, ac, bac, ev, cpi, spi)
    else:
        result["eac3"] = None
        result["errors"]["eac3"] = "CPI or SPI unavailable"

    # Primary EAC selection
    eac_map = {1: result.get("eac1"), 2: result.get("eac2"),
               3: result.get("eac3")}
    result["primary_eac_value"] = eac_map.get(primary_eac, result.get("eac1"))

    # VAC — uses primary EAC
    primary_eac_val = result["primary_eac_value"]
    if primary_eac_val is not None:
        result["vac"] = compute_vac(bac, primary_eac_val)
    else:
        result["vac"] = None
        result["errors"]["vac"] = "Primary EAC is unavailable"

    # TCPI
    _safe("tcpi_bac", compute_tcpi_bac, bac, ev, ac)

    return result


# ── RAG Engine ───────────────────────────────────────────────────────

RAG_DEFAULTS: Dict[str, Dict[str, float]] = {
    "cpi": {"amber_lower": 0.95, "green_lower": 1.0},
    "spi": {"amber_lower": 0.95, "green_lower": 1.0},
    "cr": {"amber_lower": 0.80, "green_lower": 0.90},
    "tcpi_bac": {"amber_upper": 1.10, "red_upper": 1.20},
    # For CV, SV, VAC: thresholds expressed as % of BAC
    "cv": {"amber_pct": 0.05},
    "sv": {"amber_pct": 0.05},
    "vac": {"amber_pct": 0.10},
    "eac": {"amber_pct": 0.10},
}


def get_rag(kpi: str, value, bac: float,
            thresholds: dict = None) -> str:
    """
    Return 'green', 'amber', 'red', or 'grey'.

    Boundary rule: the boundary value goes to the BETTER band.
        CPI=0.95 → amber   CPI=1.0 → green
    """
    if value is None:
        return "grey"

    th = (thresholds or {}).get(kpi, RAG_DEFAULTS.get(kpi, {}))

    # ── CPI / SPI / CR — "higher is better" indices ──
    if kpi in ("cpi", "spi", "cr"):
        amber_lower = th.get("amber_lower", 0.95)
        green_lower = th.get("green_lower", 1.0)
        if value >= green_lower:
            return "green"
        if value >= amber_lower:
            return "amber"
        return "red"

    # ── TCPI — "lower is better" (high TCPI = hard to recover) ──
    if kpi == "tcpi_bac":
        amber_upper = th.get("amber_upper", 1.10)
        red_upper = th.get("red_upper", 1.20)
        if value <= amber_upper:
            return "green"
        if value <= red_upper:
            return "amber"
        return "red"

    # ── CV, SV — variance-based (negative = bad) ──
    if kpi in ("cv", "sv"):
        amber_pct = th.get("amber_pct", 0.05)
        threshold = bac * amber_pct
        if value >= 0:
            return "green"
        if value >= -threshold:
            return "amber"
        return "red"

    # ── VAC — variance at completion (negative = overrun) ──
    if kpi == "vac":
        amber_pct = th.get("amber_pct", 0.10)
        threshold = bac * amber_pct
        if value >= 0:
            return "green"
        if value >= -threshold:
            return "amber"
        return "red"

    # ── EAC — estimate at completion (higher than BAC = bad) ──
    if kpi in ("eac", "eac1", "eac2", "eac3"):
        amber_pct = th.get("amber_pct",
                           RAG_DEFAULTS.get("eac", {}).get("amber_pct", 0.10))
        amber_limit = bac * (1 + amber_pct)
        if value <= bac:
            return "green"
        if value <= amber_limit:
            return "amber"
        return "red"

    # ── PC, PS — no RAG defined; default to grey ──
    return "grey"


# ── Step-by-Step Walkthrough ─────────────────────────────────────────

_KPI_META = {
    "cv": {"formula": "CV = EV − AC",
           "good": "Positive CV — under budget.",
           "bad": "Negative CV — over budget."},
    "sv": {"formula": "SV = EV − PV",
           "good": "Positive SV — ahead of schedule.",
           "bad": "Negative SV — behind schedule."},
    "cpi": {"formula": "CPI = EV / AC",
            "good": "CPI ≥ 1.0 — earning more per dollar spent.",
            "bad": "CPI < 1.0 — spending more per dollar of work earned."},
    "spi": {"formula": "SPI = EV / PV",
            "good": "SPI ≥ 1.0 — ahead of schedule.",
            "bad": "SPI < 1.0 — behind schedule."},
    "cr": {"formula": "CR = CPI × SPI",
           "good": "CR ≥ 1.0 — favourable overall performance.",
           "bad": "CR < 1.0 — unfavourable combined performance."},
    "pc": {"formula": "PC = (EV / BAC) × 100",
           "good": "Percent complete based on earned value.",
           "bad": "Percent complete based on earned value."},
    "ps": {"formula": "PS = (AC / BAC) × 100",
           "good": "Percent of budget spent.",
           "bad": "More than the earned fraction of budget has been spent."},
    "eac1": {"formula": "EAC₁ = AC + (BAC − EV)",
             "good": "Forecast total cost (atypical variance assumed).",
             "bad": "Forecast exceeds BAC — corrective action needed."},
    "eac2": {"formula": "EAC₂ = BAC / CPI",
             "good": "Forecast total cost (typical variance assumed).",
             "bad": "Forecast exceeds BAC — current efficiency will persist."},
    "eac3": {"formula": "EAC₃ = AC + (BAC − EV) / (CPI × SPI)",
             "good": "Forecast total cost (both schedule & cost factors).",
             "bad": "Forecast exceeds BAC with combined index correction."},
    "vac": {"formula": "VAC = BAC − EAC",
            "good": "Positive VAC — expected to finish under budget.",
            "bad": "Negative VAC — expected to finish over budget."},
    "tcpi_bac": {"formula": "TCPI = (BAC − EV) / (BAC − AC)",
                 "good": "TCPI ≤ 1.0 — remaining work is achievable at current rate.",
                 "bad": "TCPI > 1.0 — must improve efficiency on remaining work."},
}


def get_kpi_walkthrough(kpi_name: str, kpis: Dict[str, Any],
                        currency: str = "$") -> Dict[str, str]:
    """
    Generate a step-by-step walkthrough for a KPI.

    Returns dict with keys: formula, substitution, result, interpretation.
    """
    meta = _KPI_META.get(kpi_name, {})
    formula_text = meta.get("formula", kpi_name)
    value = kpis.get(kpi_name)

    if value is None:
        error_msg = kpis.get("errors", {}).get(kpi_name, "Undefined")
        return {
            "formula": formula_text,
            "substitution": "N/A",
            "result": "N/A",
            "interpretation": f"⚠ {error_msg}",
        }

    ev = kpis.get("ev", 0)
    ac = kpis.get("ac", 0)
    pv = kpis.get("pv", 0)
    bac = kpis.get("bac", 0)
    cpi = kpis.get("cpi")
    spi = kpis.get("spi")

    def _fmt(v):
        if v is None:
            return "N/A"
        if isinstance(v, float) and abs(v) >= 1:
            return f"{currency}{v:,.2f}"
        if isinstance(v, float):
            return f"{v:.3f}"
        return str(v)

    # Build substitution line
    subs = {
        "cv": f"= {_fmt(ev)} − {_fmt(ac)}",
        "sv": f"= {_fmt(ev)} − {_fmt(pv)}",
        "cpi": f"= {_fmt(ev)} ÷ {_fmt(ac)}",
        "spi": f"= {_fmt(ev)} ÷ {_fmt(pv)}",
        "cr": f"= {_fmt(cpi)} × {_fmt(spi)}",
        "pc": f"= {_fmt(ev)} ÷ {_fmt(bac)} × 100",
        "ps": f"= {_fmt(ac)} ÷ {_fmt(bac)} × 100",
        "eac1": f"= {_fmt(ac)} + ({_fmt(bac)} − {_fmt(ev)})",
        "eac2": f"= {_fmt(bac)} ÷ {_fmt(cpi)}",
        "eac3": f"= {_fmt(ac)} + ({_fmt(bac)} − {_fmt(ev)}) ÷ ({_fmt(cpi)} × {_fmt(spi)})",
        "vac": f"= {_fmt(bac)} − {_fmt(kpis.get('primary_eac_value'))}",
        "tcpi_bac": f"= ({_fmt(bac)} − {_fmt(ev)}) ÷ ({_fmt(bac)} − {_fmt(ac)})",
    }

    # Result
    if kpi_name in ("cv", "sv", "eac1", "eac2", "eac3", "vac"):
        result_text = f"= {_fmt(value)}"
    elif kpi_name in ("pc", "ps"):
        result_text = f"= {value:.1f}%"
    else:
        result_text = f"= {value:.3f}"

    # Interpretation
    is_good = False
    if kpi_name in ("cv", "sv", "vac"):
        is_good = value >= 0
    elif kpi_name in ("cpi", "spi", "cr"):
        is_good = value >= 1.0
    elif kpi_name == "tcpi_bac":
        is_good = value <= 1.0
    elif kpi_name in ("eac1", "eac2", "eac3"):
        is_good = value <= bac
    else:
        is_good = True  # pc, ps — neutral

    interp = meta.get("good" if is_good else "bad", "")

    return {
        "formula": formula_text,
        "substitution": subs.get(kpi_name, ""),
        "result": result_text,
        "interpretation": interp,
    }
