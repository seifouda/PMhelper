"""
PMhelper Edu — Monte Carlo Simulation Engine.
PERT-Beta duration sampling, Triangular cost sampling, threaded runner.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Callable
import numpy as np

from pmhelper.core.cpm_sampler_edu import run_cpm_on_sample


# ---------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------

@dataclass
class MCInputs:
    """Inputs for a Monte Carlo simulation run."""
    cpm_activities: list      # List[dict] from InputTab — id, predecessors, durations, O/M/P
    evm_tasks: list           # List[EVMTask] — budget data for cost sampling
    risks: list               # List[Risk] — optional; used for cost sampling
    bac: float
    n_trials: int = 5000
    seed: Optional[int] = None
    cost_min_factor: float = 0.8
    cost_max_factor: float = 1.3


@dataclass
class MCResults:
    """Results from a Monte Carlo simulation."""
    durations: np.ndarray              # shape (n_trials,)
    costs: np.ndarray                  # shape (n_trials,)
    cp_frequencies: Dict[str, float]   # task_id → fraction of trials on CP
    p50_duration: float
    p80_duration: float
    p90_duration: float
    p_cost_within_bac: float
    n_trials: int
    seed_used: int

    def to_serializable(self) -> dict:
        """Convert to JSON-safe dict (np.ndarray → list)."""
        return {
            "durations": self.durations.tolist(),
            "costs": self.costs.tolist(),
            "cp_frequencies": self.cp_frequencies,
            "p50_duration": float(self.p50_duration),
            "p80_duration": float(self.p80_duration),
            "p90_duration": float(self.p90_duration),
            "p_cost_within_bac": float(self.p_cost_within_bac),
            "n_trials": self.n_trials,
            "seed_used": self.seed_used,
        }

    @classmethod
    def from_serializable(cls, data: dict) -> "MCResults":
        """Reconstruct from JSON-loaded dict."""
        return cls(
            durations=np.array(data["durations"]),
            costs=np.array(data["costs"]),
            cp_frequencies=data["cp_frequencies"],
            p50_duration=data["p50_duration"],
            p80_duration=data["p80_duration"],
            p90_duration=data["p90_duration"],
            p_cost_within_bac=data["p_cost_within_bac"],
            n_trials=data["n_trials"],
            seed_used=data["seed_used"],
        )


# ---------------------------------------------------------------
# Sampling helpers
# ---------------------------------------------------------------

def _sample_pert_beta(rng: np.random.Generator,
                      optimistic: float, most_likely: float,
                      pessimistic: float) -> float:
    """Sample from a PERT-Beta distribution."""
    if pessimistic <= optimistic:
        return most_likely
    mean = (optimistic + 4 * most_likely + pessimistic) / 6.0
    rng_val = (mean - optimistic) / (pessimistic - optimistic)
    # Clamp to avoid degenerate alpha/beta
    rng_val = max(0.001, min(0.999, rng_val))
    alpha = rng_val * 4.0 + 1.0
    beta = (1.0 - rng_val) * 4.0 + 1.0
    sample = optimistic + (pessimistic - optimistic) * rng.beta(alpha, beta)
    return float(sample)


def _get_task_duration(act: dict) -> float:
    """Get deterministic duration from an activity dict."""
    # Try 'duration' key first, then planned_finish - planned_start
    if "duration" in act:
        return float(act["duration"])
    ps = act.get("planned_start", 0)
    pf = act.get("planned_finish", 0)
    return float(pf - ps) if pf > ps else 1.0


# ---------------------------------------------------------------
# Core simulation
# ---------------------------------------------------------------

def run_simulation(
    inputs: MCInputs,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> MCResults:
    """Run Monte Carlo simulation.

    Parameters
    ----------
    inputs : MCInputs
    progress_callback : callable(float) or None
        Called with progress fraction 0.0–1.0.

    Returns
    -------
    MCResults
    """
    seed = inputs.seed if inputs.seed is not None else np.random.default_rng().integers(0,
                                                                                        2**31)
    rng = np.random.default_rng(seed)

    n = inputs.n_trials
    activities = inputs.cpm_activities
    evm_tasks = inputs.evm_tasks
    risks = inputs.risks or []

    # Build budget lookup from evm_tasks
    budget_by_id: Dict[str, float] = {}
    for t in evm_tasks:
        tid = getattr(t, "task_id", None) or getattr(t, "id", None)
        budget = getattr(t, "budget", 0.0)
        if tid is not None:
            budget_by_id[tid] = budget

    # Determine which activities have PERT data
    has_pert: Dict[str, bool] = {}
    for act in activities:
        aid = act["id"]
        o = act.get("optimistic") or act.get("optimistic_duration")
        m = act.get("most_likely") or act.get("most_likely_duration")
        p = act.get("pessimistic") or act.get("pessimistic_duration")
        has_pert[aid] = (o is not None and m is not None and p is not None)

    # Storage
    durations_arr = np.zeros(n)
    costs_arr = np.zeros(n)
    cp_counts: Dict[str, int] = {act["id"]: 0 for act in activities}

    progress_interval = max(1, n // 100)

    for trial in range(n):
        sampled_durations: Dict[str, float] = {}
        sampled_cost = 0.0

        for act in activities:
            aid = act["id"]

            # --- Duration sampling ---
            if has_pert[aid]:
                o = float(act.get("optimistic")
                          or act.get("optimistic_duration"))
                m = float(act.get("most_likely")
                          or act.get("most_likely_duration"))
                p = float(act.get("pessimistic")
                          or act.get("pessimistic_duration"))
                dur = _sample_pert_beta(rng, o, m, p)
            else:
                dur = _get_task_duration(act)

            sampled_durations[aid] = dur

            # --- Cost sampling (Triangular) ---
            task_budget = budget_by_id.get(aid, 0.0)
            if task_budget > 0:
                min_cost = task_budget * inputs.cost_min_factor
                likely = task_budget
                max_cost = task_budget * inputs.cost_max_factor
                sampled_task_cost = float(
                    rng.triangular(
                        min_cost, likely, max_cost))
            else:
                sampled_task_cost = 0.0
            sampled_cost += sampled_task_cost

        # Add risk cost contributions
        for risk in risks:
            prob = getattr(risk, "probability", 0.0)
            impact = getattr(risk, "impact", 0.0)
            if rng.random() < prob:
                sampled_cost += impact

        # Run CPM on sampled durations
        project_dur, cp_set = run_cpm_on_sample(activities, sampled_durations)

        durations_arr[trial] = project_dur
        costs_arr[trial] = sampled_cost

        for aid in cp_set:
            if aid in cp_counts:
                cp_counts[aid] += 1

        # Progress callback
        if progress_callback and trial % progress_interval == 0:
            progress_callback(trial / n)

    # Final progress
    if progress_callback:
        progress_callback(1.0)

    # Compute summary statistics
    p50, p80, p90 = np.percentile(durations_arr, [50, 80, 90])
    p_cost_within_bac = float(
        np.mean(costs_arr <= inputs.bac)) if inputs.bac > 0 else 0.0

    cp_freq = {aid: count / n for aid, count in cp_counts.items()}

    return MCResults(
        durations=durations_arr,
        costs=costs_arr,
        cp_frequencies=cp_freq,
        p50_duration=float(p50),
        p80_duration=float(p80),
        p90_duration=float(p90),
        p_cost_within_bac=p_cost_within_bac,
        n_trials=n,
        seed_used=seed,
    )


# ---------------------------------------------------------------
# Threading wrapper
# ---------------------------------------------------------------

class MonteCarloRunner:
    """Thread-safe wrapper for running MC from Tkinter UI."""

    def __init__(self, root=None):
        """
        Parameters
        ----------
        root : tk.Tk or None
            The Tkinter root for scheduling via `root.after()`.
            If None, callbacks are called synchronously (for testing).
        """
        self._root = root
        self._cancel_flag = False

    @property
    def cancelled(self) -> bool:
        return self._cancel_flag

    def cancel(self) -> None:
        """Request cancellation of a running simulation."""
        self._cancel_flag = True

    def run_async(
        self,
        inputs: MCInputs,
        on_progress: Callable[[float], None],
        on_complete: Callable[[MCResults], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        """Run simulation in a background thread.

        All three callbacks are invoked on the Tkinter main thread
        (via ``root.after``), so they may safely touch widgets.
        """
        import threading
        import queue as queue_mod

        self._cancel_flag = False
        q: queue_mod.Queue = queue_mod.Queue()

        cancel_ref = self                       # capture for closure

        def worker():
            try:
                def progress_cb(pct: float):
                    q.put(("progress", pct))
                    if cancel_ref._cancel_flag:
                        raise _SimulationCancelled()

                result = run_simulation(inputs, progress_cb)
                q.put(("done", result))
            except _SimulationCancelled:
                q.put(("cancelled", None))
            except Exception as e:
                q.put(("error", e))

        def poll():
            # Process ONE message per tick to avoid micro-freezes when
            # many progress updates accumulate in a single 50 ms window.
            try:
                msg_type, payload = q.get_nowait()
                if msg_type == "progress":
                    on_progress(payload)
                elif msg_type == "done":
                    on_complete(payload)
                    return          # stop polling
                elif msg_type == "cancelled":
                    on_error(Exception("Simulation cancelled by user."))
                    return
                elif msg_type == "error":
                    on_error(payload)
                    return          # stop polling
            except queue_mod.Empty:
                pass
            if self._root is not None:
                self._root.after(50, poll)

        threading.Thread(target=worker, daemon=True).start()
        if self._root is not None:
            self._root.after(50, poll)


class _SimulationCancelled(Exception):
    """Internal sentinel — raised inside the worker thread to abort."""
