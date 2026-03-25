"""
PMhelper Edu — Risk Register Model.
Risk dataclass + RiskRegister with CRUD, exposure computation, and flagging.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class RiskCategory(str, Enum):
    SCHEDULE = "Schedule"
    COST = "Cost"
    QUALITY = "Quality"
    SCOPE = "Scope"
    OTHER = "Other"


@dataclass
class Risk:
    id: str
    name: str
    description: str = ""
    probability: float = 0.0    # 0.0 – 1.0
    impact: float = 0.0        # monetary value (≥ 0)
    category: RiskCategory = RiskCategory.OTHER
    exposure: float = 0.0      # computed: probability × impact

    def __post_init__(self):
        self.validate()
        self.exposure = self.probability * self.impact

    def validate(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(f"Risk '{self.name}': probability must be 0–1")
        if self.impact < 0:
            raise ValueError(f"Risk '{self.name}': impact must be >= 0")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "probability": self.probability,
            "impact": self.impact,
            "category": self.category.value,
            "exposure": self.exposure,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Risk":
        data = dict(data)
        if "category" in data:
            data["category"] = RiskCategory(data["category"])
        # exposure is recomputed in __post_init__, drop if present
        data.pop("exposure", None)
        return cls(**data)


@dataclass
class RiskRegister:
    risks: List[Risk] = field(default_factory=list)
    bac: float = 0.0                           # synced from EVMProject.bac
    high_exposure_threshold_pct: float = 0.05   # flag if RE > 5% of BAC

    def recompute_exposures(self) -> None:
        """Recalculate exposure = p × I for every risk."""
        for r in self.risks:
            r.exposure = r.probability * r.impact

    def total_exposure(self) -> float:
        """Sum of all risk exposures."""
        return sum(r.exposure for r in self.risks)

    def contingency_reserve(self) -> float:
        """Contingency reserve = total exposure (simple EMV approach)."""
        return self.total_exposure()

    def risks_by_exposure(self) -> List[Risk]:
        """Return risks sorted by exposure descending."""
        return sorted(self.risks, key=lambda r: r.exposure, reverse=True)

    def flag_high_exposure(self) -> List[Risk]:
        """Return risks whose exposure exceeds the threshold % of BAC."""
        threshold = self.bac * self.high_exposure_threshold_pct
        return [r for r in self.risks if r.exposure > threshold]

    def add_risk(self, risk: Risk) -> None:
        """Add a risk, ensuring unique ID."""
        if any(r.id == risk.id for r in self.risks):
            raise ValueError(f"Duplicate risk ID: {risk.id}")
        self.risks.append(risk)
        self.recompute_exposures()

    def remove_risk(self, risk_id: str) -> None:
        """Remove a risk by ID."""
        self.risks = [r for r in self.risks if r.id != risk_id]

    def get_risk(self, risk_id: str) -> Optional[Risk]:
        """Get a risk by ID, or None."""
        return next((r for r in self.risks if r.id == risk_id), None)

    def update_risk(self, risk_id: str, **kwargs) -> None:
        """Update fields of an existing risk."""
        risk = self.get_risk(risk_id)
        if risk is None:
            raise ValueError(f"Risk not found: {risk_id}")
        for key, value in kwargs.items():
            if key == "category" and isinstance(value, str):
                value = RiskCategory(value)
            setattr(risk, key, value)
        risk.validate()
        self.recompute_exposures()

    def to_dict(self) -> dict:
        return {
            "bac": self.bac,
            "high_exposure_threshold_pct": self.high_exposure_threshold_pct,
            "risks": [r.to_dict() for r in self.risks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RiskRegister":
        risks = [Risk.from_dict(r) for r in data.get("risks", [])]
        return cls(
            risks=risks,
            bac=data.get("bac", 0.0),
            high_exposure_threshold_pct=data.get("high_exposure_threshold_pct", 0.05),
        )
