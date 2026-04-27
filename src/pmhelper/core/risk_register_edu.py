"""
PMhelper Edu — Risk Register Model.
Risk dataclass + RiskRegister with CRUD, exposure computation, and flagging.

V2 Phase 6 additions:
- ResponseStrategy enum (Avoid/Transfer/Mitigate/Accept/Exploit/Share/Enhance)
- Risk fields: prob_score (1-5), impact_score (1-5), risk_score (auto),
  risk_rank, response_strategy, response_description, response_owner,
  response_cost, residual_probability, residual_impact, residual_score,
  trigger_conditions, contingency_plan.
- RiskRegister methods: recompute_scores(), update_ranks(), risks_by_score(),
  zone_of(), zone_counts(), risks_in_cell(), total_residual_exposure(),
  response_effectiveness().
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class RiskCategory(str, Enum):
    SCHEDULE = "Schedule"
    COST = "Cost"
    QUALITY = "Quality"
    SCOPE = "Scope"
    OTHER = "Other"


class ResponseStrategy(str, Enum):
    """Standard PM risk response strategies (threats + opportunities)."""
    # Threats
    AVOID = "Avoid"
    TRANSFER = "Transfer"
    MITIGATE = "Mitigate"
    ACCEPT = "Accept"
    # Opportunities
    EXPLOIT = "Exploit"
    SHARE = "Share"
    ENHANCE = "Enhance"


# 5x5 matrix zone boundaries
_ZONE_CRITICAL = 16   # 16-25  → red
_ZONE_HIGH = 10   # 10-15  → orange
_ZONE_MEDIUM = 5  # 5-9   → yellow
# < 5          → green (low)


def risk_zone(score: float) -> str:
    """Return zone label for a given risk score (1-25)."""
    if score >= _ZONE_CRITICAL:
        return "Critical"
    if score >= _ZONE_HIGH:
        return "High"
    if score >= _ZONE_MEDIUM:
        return "Medium"
    return "Low"


def zone_color(score: float) -> str:
    """Return a hex colour for a risk score (1-25)."""
    if score >= _ZONE_CRITICAL:
        return "#e74c3c"
    if score >= _ZONE_HIGH:
        return "#e67e22"
    if score >= _ZONE_MEDIUM:
        return "#f1c40f"
    return "#27ae60"


@dataclass
class Risk:
    # ── Original fields (V1) ──────────────────────────────────
    id: str
    name: str
    description: str = ""
    probability: float = 0.0    # 0.0 – 1.0  (monetary model)
    impact: float = 0.0         # monetary value (≥ 0)
    category: RiskCategory = RiskCategory.OTHER
    exposure: float = 0.0       # computed: probability × impact

    # ── Phase 6 additions ────────────────────────────────────
    # 5×5 matrix scores (1=Very Low ... 5=Very High)
    prob_score: int = 3        # probability rating  1-5
    impact_score: int = 3        # impact rating       1-5
    risk_score: float = 0.0    # auto: prob_score × impact_score (1-25)
    risk_rank: int = 0      # ordinal rank in register (set by update_ranks)

    # Response planning
    response_strategy: Optional[ResponseStrategy] = None
    response_description: str = ""
    response_owner: str = ""
    response_cost: float = 0.0

    # Residual risk (post-response)
    residual_probability: float = 3.0   # 1-5
    residual_impact: float = 3.0   # 1-5
    residual_score: float = 0.0   # auto: residual_probability × residual_impact

    # Narrative fields
    trigger_conditions: str = ""
    contingency_plan: str = ""

    # Extended response fields
    budget_impact: float = 0.0  # estimated budget impact ($)
    stakeholder_owner: str = ""   # additional stakeholder owner

    def __post_init__(self):
        self.validate()
        self.exposure = self.probability * self.impact
        self.risk_score = self.prob_score * self.impact_score
        self.residual_score = self.residual_probability * self.residual_impact

    def validate(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(f"Risk '{self.name}': probability must be 0–1")
        if self.impact < 0:
            raise ValueError(f"Risk '{self.name}': impact must be >= 0")
        if not 1 <= self.prob_score <= 5:
            raise ValueError(f"Risk '{self.name}': prob_score must be 1–5")
        if not 1 <= self.impact_score <= 5:
            raise ValueError(f"Risk '{self.name}': impact_score must be 1–5")
        if not 1 <= self.residual_probability <= 5:
            raise ValueError(
                f"Risk '{self.name}': residual_probability must be 1–5")
        if not 1 <= self.residual_impact <= 5:
            raise ValueError(
                f"Risk '{self.name}': residual_impact must be 1–5")
        if self.response_cost < 0:
            raise ValueError(
                f"Risk '{self.name}': response_cost must be >= 0")
        if self.budget_impact < 0:
            raise ValueError(
                f"Risk '{self.name}': budget_impact must be >= 0")

    @property
    def zone(self) -> str:
        """Risk zone label based on risk_score."""
        return risk_zone(self.risk_score)

    @property
    def residual_zone(self) -> str:
        """Risk zone label based on residual_score."""
        return risk_zone(self.residual_score)

    def to_dict(self) -> dict:
        return {
            # original fields
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "probability": self.probability,
            "impact": self.impact,
            "category": self.category.value,
            "exposure": self.exposure,
            # Phase 6 fields
            "prob_score": self.prob_score,
            "impact_score": self.impact_score,
            "risk_score": self.risk_score,
            "risk_rank": self.risk_rank,
            "response_strategy": self.response_strategy.value if self.response_strategy else None,
            "response_description": self.response_description,
            "response_owner": self.response_owner,
            "response_cost": self.response_cost,
            "residual_probability": self.residual_probability,
            "residual_impact": self.residual_impact,
            "residual_score": self.residual_score,
            "trigger_conditions": self.trigger_conditions,
            "contingency_plan": self.contingency_plan,
            "budget_impact": self.budget_impact,
            "stakeholder_owner": self.stakeholder_owner,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Risk":
        data = dict(data)
        if "category" in data:
            data["category"] = RiskCategory(data["category"])
        # exposure and derived scores are recomputed in __post_init__
        for drop in ("exposure", "risk_score", "residual_score"):
            data.pop(drop, None)
        # Convert response_strategy string → enum (or None)
        rs = data.get("response_strategy")
        if rs is not None and not isinstance(rs, ResponseStrategy):
            data["response_strategy"] = ResponseStrategy(rs)
        # Strip any unexpected keys from older project files gracefully
        known_fields = {
            "id", "name", "description", "probability", "impact",
            "budget_impact", "stakeholder_owner",
            "category", "prob_score", "impact_score", "risk_rank",
            "response_strategy", "response_description", "response_owner",
            "response_cost", "residual_probability", "residual_impact",
            "trigger_conditions", "contingency_plan",
        }
        data = {k: v for k, v in data.items() if k in known_fields}
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

    def recompute_scores(self) -> None:
        """Recompute risk_score and residual_score for every risk."""
        for r in self.risks:
            r.risk_score = r.prob_score * r.impact_score
            r.residual_score = r.residual_probability * r.residual_impact

    def update_ranks(self) -> None:
        """Assign risk_rank (1 = highest risk) based on risk_score descending."""
        for rank, risk in enumerate(
            sorted(self.risks, key=lambda r: r.risk_score, reverse=True), 1
        ):
            risk.risk_rank = rank

    def risks_by_score(self) -> List[Risk]:
        """Return risks sorted by risk_score descending."""
        return sorted(self.risks, key=lambda r: r.risk_score, reverse=True)

    def zone_counts(self) -> Dict[str, int]:
        """Return count of risks per zone label."""
        zones: Dict[str, int] = {
            "Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for r in self.risks:
            zones[r.zone] += 1
        return zones

    def risks_in_cell(self, prob_score: int, impact_score: int) -> List[Risk]:
        """Return risks at a specific (prob_score, impact_score) cell."""
        return [
            r for r in self.risks
            if r.prob_score == prob_score and r.impact_score == impact_score
        ]

    def total_residual_exposure(self) -> float:
        """Sum of residual_score for all risks."""
        self.recompute_scores()
        return sum(r.residual_score for r in self.risks)

    def response_effectiveness(self) -> float:
        """Overall % score reduction: (original − residual) / original × 100."""
        self.recompute_scores()
        original = sum(r.risk_score for r in self.risks)
        residual = sum(r.residual_score for r in self.risks)
        if original == 0:
            return 0.0
        return (original - residual) / original * 100.0

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
            if key == "response_strategy" and isinstance(value, str) and value:
                value = ResponseStrategy(value)
            setattr(risk, key, value)
        risk.validate()
        self.recompute_exposures()
        self.recompute_scores()

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
            risks=risks, bac=data.get(
                "bac", 0.0), high_exposure_threshold_pct=data.get(
                "high_exposure_threshold_pct", 0.05), )
