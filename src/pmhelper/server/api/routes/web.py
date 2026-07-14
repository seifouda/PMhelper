"""
Web API — synchronous REST endpoints for the Angular frontend.

All endpoints accept JSON bodies and return structured JSON immediately
(no job queue). These wrap the existing Python computation engines.
"""

from __future__ import annotations

import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/web", tags=["web"])

# ── Shared request/response models ───────────────────────────────────────────


class ActivityIn(BaseModel):
    id: str
    activity: str
    duration: int
    predecessors: List[str] = []
    min_duration: Optional[int] = None
    crash_cost: Optional[float] = None
    resource_demand: Optional[float] = None
    normal_cost: Optional[float] = None
    optimistic: Optional[float] = None
    most_likely: Optional[float] = None
    pessimistic: Optional[float] = None


class ActivitiesRequest(BaseModel):
    activities: List[ActivityIn]


# ── CPM ─────────────────────────────────────────────────────────────────


@router.post("/analysis/cpm")
@limiter.limit("30/minute")
async def run_cpm(request: Request, req: ActivitiesRequest) -> Dict[str, Any]:
    """Run CPM forward/backward pass and return full scheduling results."""
    try:
        from pmhelper.core.cpm_analyzer import CPMAnalyzer

        data = [a.model_dump() for a in req.activities]
        analyzer = CPMAnalyzer()
        G, critical_paths, critical_activities = analyzer.analyze(data)

        nodes = []
        for node_id in G.nodes():
            if node_id in ("START", "END"):
                continue
            nd = G.nodes[node_id]
            nodes.append(
                {
                    "id": node_id,
                    "activity": nd.get("activity", node_id),
                    "duration": nd.get("duration", 0),
                    "ES": nd.get("ES", 0),
                    "EF": nd.get("EF", 0),
                    "LS": nd.get("LS", 0),
                    "LF": nd.get("LF", 0),
                    "total_float": nd.get("float", 0),
                    "free_float": nd.get("free_float", 0),
                    "is_critical": node_id in critical_activities,
                }
            )

        edges = [
            {"from": u, "to": v}
            for u, v in G.edges()
            if u != "START" and v != "END"
        ]

        project_duration = max((n["EF"] for n in nodes), default=0)

        return {
            "project_duration": project_duration,
            "critical_paths": critical_paths,
            "critical_activities": list(critical_activities),
            "nodes": nodes,
            "edges": edges,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("CPM analysis failed")
        raise HTTPException(
            status_code=500,
            detail=f"CPM analysis failed: {e}")


# ── PERT ────────────────────────────────────────────────────────────────


class PERTRequest(BaseModel):
    activities: List[ActivityIn]
    target_duration: Optional[float] = None


@router.post("/analysis/pert")
@limiter.limit("30/minute")
async def run_pert(request: Request, req: PERTRequest) -> Dict[str, Any]:
    """Run PERT 3-point estimation and probability analysis."""
    try:
        from pmhelper.core.pert_analyzer import PERTAnalyzer

        data = [a.model_dump() for a in req.activities]
        analyzer = PERTAnalyzer()
        results = analyzer.analyze(data)

        node_rows = []
        for item in results.get("activities", []):
            node_rows.append(
                {
                    "id": item["id"],
                    "activity": item.get("activity", item["id"]),
                    "optimistic": item.get("optimistic", 0),
                    "most_likely": item.get("most_likely", 0),
                    "pessimistic": item.get("pessimistic", 0),
                    "expected_time": item.get("expected_time", 0),
                    "variance": item.get("variance", 0),
                    "std_dev": item.get("std_dev", 0),
                }
            )

        response: Dict[str, Any] = {
            "nodes": node_rows,
            "project_expected_duration": results.get("project_duration", 0),
            "project_variance": results.get("project_variance", 0),
            "project_std_dev": results.get("project_std_dev", 0),
        }

        if req.target_duration is not None:
            prob = results.get("probability_on_time", None)
            response["probability_on_time"] = prob

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("PERT analysis failed")
        raise HTTPException(
            status_code=500,
            detail=f"PERT analysis failed: {e}")


# ── Crashing ────────────────────────────────────────────────────────────


class CrashingRequest(BaseModel):
    activities: List[ActivityIn]
    indirect_cost_rate: float = 0.0


@router.post("/analysis/crashing")
@limiter.limit("30/minute")
async def run_crashing(
        request: Request, req: CrashingRequest) -> Dict[str, Any]:
    """Run time-cost trade-off (crashing) analysis."""
    try:
        from pmhelper.core.cost_optimization import TimeCostOptimizer, IndirectCostModel
        from pmhelper.core.cpm_analyzer import CPMAnalyzer

        data = [a.model_dump() for a in req.activities]
        analyzer = CPMAnalyzer()
        G, _, _ = analyzer.analyze(data)

        indirect_model = IndirectCostModel(rate=req.indirect_cost_rate)
        optimizer = TimeCostOptimizer(G, indirect_model)
        result = optimizer.optimize()

        steps = []
        for step in result.get("steps", []):
            steps.append(
                {
                    "step": step.get("step", 0),
                    "activity_crashed": step.get("activity", ""),
                    "cost_slope": step.get("cost_slope", 0),
                    "new_duration": step.get("project_duration", 0),
                    "total_cost": step.get("total_cost", 0),
                    "critical_path": step.get("critical_path", []),
                }
            )

        return {
            "steps": steps,
            "optimal_duration": result.get("optimal_duration", 0),
            "optimal_cost": result.get("optimal_cost", 0),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Crashing analysis failed")
        raise HTTPException(status_code=500,
                            detail=f"Crashing analysis failed: {e}")


# ── EVM ─────────────────────────────────────────────────────────────────


class EVMPeriodIn(BaseModel):
    index: int
    label: str
    pv_cumulative: float
    ev_cumulative: float
    ac_cumulative: float


class EVMTaskIn(BaseModel):
    task_id: str
    name: str
    budget: float
    pct_complete: float
    planned_start: int
    planned_finish: int


class EVMProjectIn(BaseModel):
    project_name: str = "Project"
    bac: float
    currency_symbol: str = "$"
    periods: List[EVMPeriodIn]
    tasks: List[EVMTaskIn] = []


class EVMRequest(BaseModel):
    project: EVMProjectIn
    current_period_index: Optional[int] = None


@router.post("/analysis/evm")
@limiter.limit("30/minute")
async def run_evm(request: Request, req: EVMRequest) -> Dict[str, Any]:
    """Compute EVM KPIs from period data."""
    try:
        from pmhelper.core.evm_calculations_edu import EVMCalculator

        proj_data = req.project
        periods = [p.model_dump() for p in proj_data.periods]
        tasks = [t.model_dump() for t in proj_data.tasks]

        # Use the last period if no current_period_index given
        idx = req.current_period_index if req.current_period_index is not None else len(
            periods) - 1
        idx = min(idx, len(periods) - 1)
        period = periods[idx]

        pv = period["pv_cumulative"]
        ev = period["ev_cumulative"]
        ac = period["ac_cumulative"]
        bac = proj_data.bac

        calc = EVMCalculator(bac=bac, pv=pv, ev=ev, ac=ac)
        kpis = calc.compute_all()

        return {"kpis": kpis, "period_index": idx}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("EVM analysis failed")
        raise HTTPException(
            status_code=500,
            detail=f"EVM analysis failed: {e}")


# ── Risk ────────────────────────────────────────────────────────────────


class RiskIn(BaseModel):
    id: str
    name: str
    description: str = ""
    probability: float = Field(ge=0, le=1)
    impact: float = Field(ge=0)
    category: str = "Other"
    exposure: float = 0.0


class RiskRequest(BaseModel):
    risks: List[RiskIn]


@router.post("/analysis/risk")
@limiter.limit("30/minute")
async def run_risk(request: Request, req: RiskRequest) -> Dict[str, Any]:
    """Compute risk exposures and contingency reserve."""
    risks = []
    for r in req.risks:
        exposure = r.probability * r.impact
        risks.append({**r.model_dump(), "exposure": exposure})

    total_exposure = sum(r["exposure"] for r in risks)
    return {
        "risks": risks,
        "total_exposure": total_exposure,
        "contingency_reserve": total_exposure,
    }


# ── Monte Carlo ─────────────────────────────────────────────────────────


class MCRequest(BaseModel):
    activities: List[ActivityIn]
    n_trials: int = Field(default=5000, ge=100, le=50000)
    seed: Optional[int] = None
    cost_min_factor: float = 0.8
    cost_max_factor: float = 1.2


@router.post("/analysis/monte-carlo")
@limiter.limit("5/minute")
async def run_monte_carlo(request: Request, req: MCRequest) -> Dict[str, Any]:
    """Run Monte Carlo simulation (requires O/M/P estimates or will use duration as mode)."""
    try:
        from pmhelper.core.monte_carlo_edu import MonteCarloSimulator

        data = [a.model_dump() for a in req.activities]
        simulator = MonteCarloSimulator(
            activities_data=data,
            n_trials=req.n_trials,
            seed=req.seed,
            cost_min_factor=req.cost_min_factor,
            cost_max_factor=req.cost_max_factor,
        )
        result = simulator.run()

        return {
            "durations": result.get("durations", []),
            "costs": result.get("costs", []),
            "cp_frequencies": result.get("cp_frequencies", {}),
            "p50_duration": result.get("p50_duration", 0),
            "p80_duration": result.get("p80_duration", 0),
            "p90_duration": result.get("p90_duration", 0),
            "p_cost_within_bac": result.get("p_cost_within_bac", 0),
            "n_trials": req.n_trials,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Monte Carlo simulation failed")
        raise HTTPException(status_code=500, detail=f"Monte Carlo failed: {e}")


# ── RCPS ────────────────────────────────────────────────────────────────


class RCPSRequest(BaseModel):
    activities: List[ActivityIn]
    resource_limit: float
    algorithm: str = "burgess"


@router.post("/analysis/rcps")
@limiter.limit("30/minute")
async def run_rcps(request: Request, req: RCPSRequest) -> Dict[str, Any]:
    """Run resource-constrained project scheduling."""
    try:
        from pmhelper.core.resource_leveling import ResourceLevelingFactory

        data = [a.model_dump() for a in req.activities]
        leveler = ResourceLevelingFactory.create(algorithm=req.algorithm)
        result = leveler.level(
            activities_data=data,
            resource_limit=req.resource_limit,
        )

        return {
            "original_duration": result.get("original_duration", 0),
            "leveled_duration": result.get("leveled_duration", 0),
            "schedule": result.get("schedule", {}),
            "resource_usage": result.get("resource_usage", []),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("RCPS analysis failed")
        raise HTTPException(
            status_code=500,
            detail=f"RCPS analysis failed: {e}")


# ── Calculation steps (Learn Mode) ──────────────────────────────────────


@router.post("/analysis/steps/cpm")
@limiter.limit("30/minute")
async def get_cpm_steps(
        request: Request, req: ActivitiesRequest) -> List[Dict[str, Any]]:
    """Return step-by-step CPM calculation walkthrough for Learn Mode."""
    try:
        from pmhelper.core.step_generators_edu import generate_cpm_steps
        from pmhelper.core.cpm_analyzer import CPMAnalyzer

        data = [a.model_dump() for a in req.activities]
        analyzer = CPMAnalyzer()
        G, critical_paths, critical_activities = analyzer.analyze(data)
        steps = generate_cpm_steps(G, critical_paths)
        return steps
    except Exception as e:
        logger.exception("CPM steps generation failed")
        raise HTTPException(status_code=500,
                            detail=f"Steps generation failed: {e}")


@router.post("/analysis/steps/pert")
@limiter.limit("30/minute")
async def get_pert_steps(
        request: Request, req: ActivitiesRequest) -> List[Dict[str, Any]]:
    """Return step-by-step PERT calculation walkthrough for Learn Mode."""
    try:
        from pmhelper.core.step_generators_edu import generate_pert_steps
        from pmhelper.core.pert_analyzer import PERTAnalyzer

        data = [a.model_dump() for a in req.activities]
        analyzer = PERTAnalyzer()
        results = analyzer.analyze(data)
        steps = generate_pert_steps(results)
        return steps
    except Exception as e:
        logger.exception("PERT steps generation failed")
        raise HTTPException(status_code=500,
                            detail=f"Steps generation failed: {e}")


@router.post("/analysis/steps/evm")
@limiter.limit("30/minute")
async def get_evm_steps(
        request: Request, req: EVMRequest) -> List[Dict[str, Any]]:
    """Return step-by-step EVM KPI walkthrough for Learn Mode."""
    try:
        from pmhelper.core.step_generators_edu import generate_evm_steps

        proj = req.project
        idx = req.current_period_index if req.current_period_index is not None else len(
            proj.periods) - 1
        period = proj.periods[min(idx, len(proj.periods) - 1)]
        steps = generate_evm_steps(
            bac=proj.bac,
            pv=period.pv_cumulative,
            ev=period.ev_cumulative,
            ac=period.ac_cumulative,
        )
        return steps
    except Exception as e:
        logger.exception("EVM steps generation failed")
        raise HTTPException(status_code=500,
                            detail=f"Steps generation failed: {e}")


# ── Samples ─────────────────────────────────────────────────────────────

# Locate demo project files
_DEMOS_DIR = Path(__file__).parent.parent.parent.parent / "demos_edu"

_SAMPLE_CATALOG: List[Dict[str,
                           Any]] = [{"id": "office_renovation_ug",
                                     "name": "Office Renovation",
                                     "description": "15-task office renovation project — UG demo",
                                     "level": "ug",
                                     "task_count": 15,
                                     },
                                    {"id": "hospital_construction_ug_medium",
                                     "name": "Hospital Construction (Medium)",
                                     "description": "150-task hospital construction project — medium UG demo",
                                     "level": "ug",
                                     "task_count": 150,
                                     },
                                    {"id": "campus_construction_ug_large",
                                     "name": "Campus Construction (Large)",
                                     "description": "600-task campus construction — large UG demo",
                                     "level": "ug",
                                     "task_count": 600,
                                     },
                                    {"id": "software_project_pg",
                                     "name": "Software Project",
                                     "description": "13-task software development project — PG demo",
                                     "level": "pg",
                                     "task_count": 13,
                                     },
                                    {"id": "digital_transformation_pg_medium",
                                     "name": "Digital Transformation (Medium)",
                                     "description": "150-task digital transformation programme — medium PG demo",
                                     "level": "pg",
                                     "task_count": 150,
                                     },
                                    {"id": "erp_implementation_pg_large",
                                     "name": "ERP Implementation (Large)",
                                     "description": "600-task ERP implementation — large PG demo",
                                     "level": "pg",
                                     "task_count": 600,
                                     },
                                    ]


@router.get("/samples")
async def list_samples() -> List[Dict[str, Any]]:
    """Return the list of available sample/demo projects."""
    return _SAMPLE_CATALOG


@router.get("/samples/{sample_id}")
async def get_sample(sample_id: str) -> Dict[str, Any]:
    """Load a sample project's activities from the demos_edu directory."""
    # Validate sample_id is in catalog (prevent path traversal)
    known_ids = {s["id"] for s in _SAMPLE_CATALOG}
    if sample_id not in known_ids:
        raise HTTPException(status_code=404,
                            detail=f"Sample '{sample_id}' not found")

    demo_file = _DEMOS_DIR / f"{sample_id}.pmproj"
    if not demo_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Demo file for '{sample_id}' not found on server")

    try:
        with open(demo_file, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        return {"activities": project_data.get("activities", [])}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid demo file: {e}")


# ── CSV Import ──────────────────────────────────────────────────────────


@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Parse an uploaded CSV file and return a validated activities list.
    Auto-detects column names (case-insensitive, with common aliases).
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        import pandas as pd

        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))

        # Normalize column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Column aliases
        aliases = {
            "task_id": "id",
            "task": "id",
            "name": "activity",
            "task_name": "activity",
            "description": "activity",
            "dur": "duration",
            "d": "duration",
            "pred": "predecessors",
            "predecessor": "predecessors",
            "depends_on": "predecessors",
        }
        df = df.rename(columns=aliases)

        required = {"id", "activity", "duration"}
        missing = required - set(df.columns)
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required columns: {
                    ', '.join(
                        sorted(missing))}. " f"Found: {
                    ', '.join(
                        df.columns)}",
            )

        # Parse predecessors
        def parse_preds(val: Any) -> List[str]:
            if pd.isna(val) or str(val).strip() in ("", "-", "none", "None"):
                return []
            s = str(val).strip()
            # Handle both comma and semicolon separators
            for sep in [";", ",", "|"]:
                if sep in s:
                    return [p.strip() for p in s.split(sep) if p.strip()]
            return [s] if s else []

        activities = []
        errors = []
        for idx, row in df.iterrows():
            row_num = idx + 2  # 1-based + header
            try:
                act: Dict[str, Any] = {
                    "id": str(row["id"]).strip(),
                    "activity": str(row["activity"]).strip(),
                    "duration": int(float(row["duration"])),
                    "predecessors": parse_preds(row.get("predecessors")),
                }
                # Optional columns
                for col in [
                    "min_duration",
                    "crash_cost",
                    "resource_demand",
                    "normal_cost",
                    "optimistic",
                    "most_likely",
                        "pessimistic"]:
                    if col in df.columns and not pd.isna(row.get(col)):
                        try:
                            act[col] = float(row[col])
                        except (ValueError, TypeError):
                            pass
                activities.append(act)
            except (ValueError, TypeError) as e:
                errors.append(f"Row {row_num}: {e}")

        return {
            "activities": activities,
            "errors": errors,
            "row_count": len(activities)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("CSV import failed")
        raise HTTPException(status_code=500, detail=f"CSV import failed: {e}")


# ── Telemetry ───────────────────────────────────────────────────────────


class TelemetryError(BaseModel):
    message: str = Field(max_length=2000)
    stack: Optional[str] = Field(default=None, max_length=10000)
    url: str = Field(max_length=2000)
    timestamp: str = Field(max_length=50)


@router.post("/telemetry/error", status_code=204)
async def telemetry_error(payload: TelemetryError):  # no return annotation: '-> None' trips FastAPI's 204 body assert
    """Receive client-side error telemetry (fire-and-forget sink)."""
    logger.warning(
        "Client error: %s | url=%s | ts=%s",
        payload.message[:200],
        payload.url[:200],
        payload.timestamp,
    )
