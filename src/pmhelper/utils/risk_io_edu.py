"""
PMhelper Edu — Risk Register I/O.
JSON save/load and CSV export/import for risk register data.
"""

import json
import csv
from pathlib import Path
from typing import List

from pmhelper.core.risk_register_edu import Risk, RiskRegister, RiskCategory

# Ordered fieldnames for CSV export (V1 + Phase 6 additions)
_CSV_FIELDS = [
    "id", "name", "description", "probability", "impact",
    "category", "exposure",
    # Phase 6
    "prob_score", "impact_score", "risk_score", "risk_rank",
    "response_strategy", "response_description", "response_owner", "response_cost",
    "residual_probability", "residual_impact", "residual_score",
    "trigger_conditions", "contingency_plan",
]


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
    """Export risk register to CSV (V1 + Phase 6 fields)."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS, extrasaction="ignore")
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
                risks.append(Risk.from_dict({
                    "id":          row["id"],
                    "name":        row["name"],
                    "description": row.get("description", ""),
                    "probability": float(row["probability"]),
                    "impact":      float(row["impact"]),
                    "category":    row.get("category", "Other"),
                    # Phase 6 optional fields (may not exist in old CSV files)
                    "prob_score":            int(row["prob_score"])   if row.get("prob_score")   else 3,
                    "impact_score":          int(row["impact_score"]) if row.get("impact_score") else 3,
                    "response_strategy":     row.get("response_strategy") or None,
                    "response_description":  row.get("response_description", ""),
                    "response_owner":        row.get("response_owner", ""),
                    "response_cost":         float(row["response_cost"]) if row.get("response_cost") else 0.0,
                    "residual_probability":  float(row["residual_probability"]) if row.get("residual_probability") else 3.0,
                    "residual_impact":       float(row["residual_impact"])      if row.get("residual_impact")      else 3.0,
                    "trigger_conditions":    row.get("trigger_conditions", ""),
                    "contingency_plan":      row.get("contingency_plan", ""),
                }))
            except (ValueError, KeyError):
                continue  # skip invalid rows
    return RiskRegister(risks=risks)

