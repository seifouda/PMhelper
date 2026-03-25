"""
PMhelper Edu — EVM Project File I/O.
Handles .pmproj JSON files and CSV import/export for EVM data.
"""

import json
import csv
from pathlib import Path
from typing import List

from pmhelper.core.evm_models_edu import EVMProject, EVMTask, EVMPeriod, PVSpread


def save_evm_project(project: EVMProject, filepath: str) -> None:
    """Save EVMProject to JSON file."""
    Path(filepath).write_text(
        json.dumps(project.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def load_evm_project(filepath: str) -> EVMProject:
    """Load EVMProject from JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {filepath}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return EVMProject.from_dict(data)


def export_periods_to_csv(project: EVMProject, filepath: str) -> None:
    """Export period data to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "index", "label", "pv_cumulative", "ev_cumulative",
            "ac_cumulative", "ev_source"])
        writer.writeheader()
        for p in project.periods:
            writer.writerow(p.to_dict())


def import_periods_from_csv(filepath: str) -> List[EVMPeriod]:
    """Import period data from CSV."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    periods = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                periods.append(EVMPeriod(
                    index=int(row["index"]),
                    label=row.get("label", ""),
                    pv_cumulative=float(row["pv_cumulative"]),
                    ev_cumulative=float(row["ev_cumulative"]),
                    ac_cumulative=float(row["ac_cumulative"]),
                    ev_source=row.get("ev_source", "manual"),
                ))
            except (ValueError, KeyError):
                continue  # skip rows with non-numeric values
    return periods


def export_tasks_to_csv(project: EVMProject, filepath: str) -> None:
    """Export EVM tasks to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "task_id", "name", "budget", "pct_complete",
            "planned_start", "planned_finish", "pv_spread"])
        writer.writeheader()
        for t in project.tasks:
            writer.writerow({
                "task_id": t.task_id,
                "name": t.name,
                "budget": t.budget,
                "pct_complete": t.pct_complete,
                "planned_start": t.planned_start,
                "planned_finish": t.planned_finish,
                "pv_spread": t.pv_spread.value,
            })


def import_tasks_from_csv(filepath: str) -> List[EVMTask]:
    """Import EVM tasks from CSV. Returns list of EVMTask objects."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    tasks = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                tasks.append(EVMTask(
                    task_id=row["task_id"],
                    name=row["name"],
                    budget=float(row["budget"]),
                    pct_complete=float(row.get("pct_complete", 0)),
                    planned_start=int(row["planned_start"]),
                    planned_finish=int(row["planned_finish"]),
                    pv_spread=PVSpread(row.get("pv_spread", "uniform")),
                ))
            except (ValueError, KeyError):
                continue  # skip invalid rows
    return tasks
