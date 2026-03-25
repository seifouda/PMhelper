"""
PMhelper Edu — Risk Register I/O.
JSON save/load and CSV export/import for risk register data.
"""

import json
import csv
from pathlib import Path
from typing import List

from pmhelper.core.risk_register_edu import Risk, RiskRegister, RiskCategory


def save_register(register: RiskRegister, filepath: str) -> None:
    """Save RiskRegister to JSON file."""
    Path(filepath).write_text(
        json.dumps(register.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def load_register(filepath: str) -> RiskRegister:
    """Load RiskRegister from JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Risk register file not found: {filepath}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return RiskRegister.from_dict(data)


def export_to_csv(register: RiskRegister, filepath: str) -> None:
    """Export risk register to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "name", "description", "probability", "impact",
            "category", "exposure"])
        writer.writeheader()
        for r in register.risks:
            writer.writerow(r.to_dict())


def import_from_csv(filepath: str) -> RiskRegister:
    """Import risk register from CSV. Returns a new RiskRegister."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    risks: List[Risk] = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                risks.append(Risk(
                    id=row["id"],
                    name=row["name"],
                    description=row.get("description", ""),
                    probability=float(row["probability"]),
                    impact=float(row["impact"]),
                    category=RiskCategory(row.get("category", "Other")),
                ))
            except (ValueError, KeyError):
                continue  # skip invalid rows
    return RiskRegister(risks=risks)
