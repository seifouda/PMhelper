"""
PMhelper Edu — EVM Data Models.
All models use @dataclass with manual validation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Literal
from enum import Enum


class PVSpread(str, Enum):
    UNIFORM = "uniform"
    FRONT = "front"      # 50/30/20 weighting across thirds
    BACK = "back"        # 20/30/50 weighting across thirds


@dataclass
class EVMTask:
    task_id: str                                    # unique within project
    name: str
    budget: float = 0.0                             # this task's share of BAC
    pct_complete: float = 0.0                       # 0-100
    planned_start: int = 0                          # 0-based period index
    planned_finish: int = 0                         # >= planned_start
    actual_start: Optional[int] = None
    actual_finish: Optional[int] = None
    baseline_start: Optional[int] = None
    baseline_finish: Optional[int] = None
    pv_spread: PVSpread = PVSpread.UNIFORM
    cpm_task_id: Optional[str] = None               # optional link to CPM task
    predecessors: List[str] = field(
        default_factory=list)  # EVMTask IDs (for MC)

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if self.budget < 0:
            raise ValueError(
                f"Task '{
                    self.task_id}': budget cannot be negative")
        if not 0 <= self.pct_complete <= 100:
            raise ValueError(
                f"Task '{
                    self.task_id}': pct_complete must be 0\u2013100")
        if self.planned_finish < self.planned_start:
            raise ValueError(
                f"Task '{
                    self.task_id}': planned_finish ({
                    self.planned_finish}) " f"< planned_start ({
                    self.planned_start})")

    @property
    def ev(self) -> float:
        """Earned value = budget x % complete."""
        return self.budget * self.pct_complete / 100.0

    @property
    def duration_periods(self) -> int:
        """Number of periods this task spans."""
        return self.planned_finish - self.planned_start + 1

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "budget": self.budget,
            "pct_complete": self.pct_complete,
            "planned_start": self.planned_start,
            "planned_finish": self.planned_finish,
            "actual_start": self.actual_start,
            "actual_finish": self.actual_finish,
            "baseline_start": self.baseline_start,
            "baseline_finish": self.baseline_finish,
            "pv_spread": self.pv_spread.value,
            "cpm_task_id": self.cpm_task_id,
            "predecessors": self.predecessors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EVMTask":
        data = dict(data)  # copy
        if "pv_spread" in data:
            data["pv_spread"] = PVSpread(data["pv_spread"])
        if "predecessors" not in data:
            data["predecessors"] = []
        return cls(**data)


@dataclass
class EVMPeriod:
    index: int                                      # 0-based sort key
    label: str = ""                                 # e.g. "Month 1", "Week 3"
    pv_cumulative: float = 0.0
    ev_cumulative: float = 0.0
    ac_cumulative: float = 0.0
    ev_source: Literal["manual", "computed"] = "manual"

    def __post_init__(self):
        if self.index < 0:
            raise ValueError("Period index cannot be negative")

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "label": self.label,
            "pv_cumulative": self.pv_cumulative,
            "ev_cumulative": self.ev_cumulative,
            "ac_cumulative": self.ac_cumulative,
            "ev_source": self.ev_source,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EVMPeriod":
        return cls(**data)


@dataclass
class EVMProject:
    project_name: str = "New Project"
    bac: float = 0.0                                # Budget at Completion
    currency_symbol: str = "$"
    periods: List[EVMPeriod] = field(default_factory=list)
    tasks: List[EVMTask] = field(default_factory=list)
    schema_version: int = 1                         # for forward-compatibility
    # BAC = sum(task budgets) by default
    bac_auto_compute: bool = True

    def __post_init__(self):
        if self.bac < 0:
            raise ValueError("BAC cannot be negative")
        if self.bac_auto_compute and self.tasks:
            self.bac = sum(t.budget for t in self.tasks)

    def recompute_bac(self) -> None:
        """Recalculate BAC from task budgets if auto-compute is on."""
        if self.bac_auto_compute:
            self.bac = sum(t.budget for t in self.tasks)

    def current_ev(self) -> float:
        return self.periods[-1].ev_cumulative if self.periods else 0.0

    def current_pv(self) -> float:
        return self.periods[-1].pv_cumulative if self.periods else 0.0

    def current_ac(self) -> float:
        return self.periods[-1].ac_cumulative if self.periods else 0.0

    def task_ev(self) -> float:
        """EV computed from task %-complete x budget."""
        return sum(t.ev for t in self.tasks)

    def ev_discrepancy(self) -> float:
        """Non-zero means period EV and task-level EV differ."""
        return abs(self.task_ev() - self.current_ev())

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "project_name": self.project_name,
            "bac": self.bac,
            "bac_auto_compute": self.bac_auto_compute,
            "currency_symbol": self.currency_symbol,
            "tasks": [t.to_dict() for t in self.tasks],
            "periods": [p.to_dict() for p in self.periods],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EVMProject":
        tasks = [EVMTask.from_dict(t) for t in data.get("tasks", [])]
        periods = [EVMPeriod.from_dict(p) for p in data.get("periods", [])]
        return cls(
            project_name=data.get("project_name", "New Project"),
            bac=data.get("bac", 0.0),
            bac_auto_compute=data.get("bac_auto_compute", True),
            currency_symbol=data.get("currency_symbol", "$"),
            tasks=tasks,
            periods=periods,
            schema_version=data.get("schema_version", 1),
        )


def compute_pv_schedule(tasks: List[EVMTask], num_periods: int) -> List[float]:
    """
    Compute period-by-period CUMULATIVE planned value from task data.

    Algorithm:
        For each task, spread its budget across its active periods
        using the task's pv_spread rule (uniform/front/back).
        Sum across all tasks per period, then cumulate.

    Args:
        tasks: List of EVMTask with planned_start, planned_finish, budget
        num_periods: Total number of periods in the project

    Returns:
        List of cumulative PV values, one per period (length = num_periods)
    """
    pv_per_period = [0.0] * num_periods

    for task in tasks:
        start = task.planned_start
        finish = min(task.planned_finish, num_periods - 1)  # clamp
        if start >= num_periods:
            continue  # task starts after all periods

        active_count = finish - start + 1
        if active_count <= 0:
            continue

        weights = _spread_weights(active_count, task.pv_spread)

        for i, period_idx in enumerate(range(start, finish + 1)):
            pv_per_period[period_idx] += task.budget * weights[i]

    # Cumulate
    cumulative = []
    running = 0.0
    for val in pv_per_period:
        running += val
        cumulative.append(round(running, 2))

    return cumulative


def _spread_weights(n: int, spread: PVSpread) -> List[float]:
    """
    Generate normalized weights for distributing budget across n periods.

    Uniform: equal weights
    Front:   50/30/20 across thirds
    Back:    20/30/50 across thirds
    """
    if spread == PVSpread.UNIFORM or n <= 1:
        return [1.0 / n] * n

    # Split into thirds
    third = max(1, n // 3)
    remainder = n - 3 * third

    sizes = [third, third, third + remainder]  # last third absorbs remainder

    if spread == PVSpread.FRONT:
        group_weights = [0.50, 0.30, 0.20]
    else:  # BACK
        group_weights = [0.20, 0.30, 0.50]

    weights = []
    for size, gw in zip(sizes, group_weights):
        per_period = gw / size if size > 0 else 0
        weights.extend([per_period] * size)

    # Normalize to sum to 1.0 (safety)
    total = sum(weights)
    if total > 0:
        weights = [w / total for w in weights]

    return weights
