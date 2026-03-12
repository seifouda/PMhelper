"""
PMhelper Edu — PESTEL Analysis data model.
PG-only. Pure data classes, no Tkinter dependency.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PESTELCategory(Enum):
    """Six PESTEL dimensions."""
    POLITICAL = "Political"
    ECONOMIC = "Economic"
    SOCIAL = "Social"
    TECHNOLOGICAL = "Technological"
    ENVIRONMENTAL = "Environmental"
    LEGAL = "Legal"


# Colours for UI rendering
PESTEL_COLOURS: dict[PESTELCategory, str] = {
    PESTELCategory.POLITICAL:      "#4e79a7",
    PESTELCategory.ECONOMIC:       "#f28e2b",
    PESTELCategory.SOCIAL:         "#e15759",
    PESTELCategory.TECHNOLOGICAL:  "#76b7b2",
    PESTELCategory.ENVIRONMENTAL:  "#59a14f",
    PESTELCategory.LEGAL:          "#edc948",
}


@dataclass
class PESTELFactor:
    """One PESTEL factor."""
    category: PESTELCategory
    description: str
    impact_score: float = 0.0       # -5 (very negative) to +5 (very positive)
    probability: float = 0.5        # 0.0 to 1.0
    timeframe: str = "Medium-term"  # Short / Medium / Long
    mitigation: str = ""
    linked_to: str = ""             # optional link to Risk ID

    @property
    def exposure(self) -> float:
        """Weighted exposure = |impact_score| * probability."""
        return abs(self.impact_score) * self.probability

    def validate(self) -> List[str]:
        errors = []
        if not self.description.strip():
            errors.append("Description is required.")
        if not -5 <= self.impact_score <= 5:
            errors.append("Impact score must be between -5 and +5.")
        if not 0 <= self.probability <= 1:
            errors.append("Probability must be between 0 and 1.")
        if self.timeframe not in ("Short-term", "Medium-term", "Long-term"):
            errors.append("Timeframe must be Short-term, Medium-term, or Long-term.")
        return errors

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "description": self.description,
            "impact_score": self.impact_score,
            "probability": self.probability,
            "timeframe": self.timeframe,
            "mitigation": self.mitigation,
            "linked_to": self.linked_to,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PESTELFactor":
        return cls(
            category=PESTELCategory(d["category"]),
            description=d["description"],
            impact_score=float(d.get("impact_score", 0)),
            probability=float(d.get("probability", 0.5)),
            timeframe=d.get("timeframe", "Medium-term"),
            mitigation=d.get("mitigation", ""),
            linked_to=d.get("linked_to", ""),
        )


@dataclass
class PESTELAnalysis:
    """Collection of PESTEL factors with query helpers."""
    factors: List[PESTELFactor] = field(default_factory=list)

    # -- Query helpers --

    def by_category(self, cat: PESTELCategory) -> List[PESTELFactor]:
        return [f for f in self.factors if f.category == cat]

    @property
    def political(self) -> List[PESTELFactor]:
        return self.by_category(PESTELCategory.POLITICAL)

    @property
    def economic(self) -> List[PESTELFactor]:
        return self.by_category(PESTELCategory.ECONOMIC)

    @property
    def social(self) -> List[PESTELFactor]:
        return self.by_category(PESTELCategory.SOCIAL)

    @property
    def technological(self) -> List[PESTELFactor]:
        return self.by_category(PESTELCategory.TECHNOLOGICAL)

    @property
    def environmental(self) -> List[PESTELFactor]:
        return self.by_category(PESTELCategory.ENVIRONMENTAL)

    @property
    def legal(self) -> List[PESTELFactor]:
        return self.by_category(PESTELCategory.LEGAL)

    def total_exposure(self) -> float:
        return sum(f.exposure for f in self.factors)

    def factor_count(self) -> int:
        return len(self.factors)

    def top_risks(self, n: int = 5) -> List[PESTELFactor]:
        """Top N factors by exposure, negative impact only."""
        negatives = [f for f in self.factors if f.impact_score < 0]
        return sorted(negatives, key=lambda f: f.exposure, reverse=True)[:n]

    def top_opportunities(self, n: int = 5) -> List[PESTELFactor]:
        """Top N factors by exposure, positive impact only."""
        positives = [f for f in self.factors if f.impact_score > 0]
        return sorted(positives, key=lambda f: f.exposure, reverse=True)[:n]

    # -- CRUD --

    def add_factor(self, factor: PESTELFactor) -> None:
        self.factors.append(factor)

    def remove_factor(self, factor: PESTELFactor) -> bool:
        try:
            self.factors.remove(factor)
            return True
        except ValueError:
            return False

    def clear(self) -> None:
        self.factors.clear()

    # -- Risk Register bridge --

    def factors_for_risk_register(self) -> List[dict]:
        """Return factors suitable for import into the Risk Register.

        Only negative-impact factors with mitigation are included.
        Returns list of dicts with name, category, probability, impact fields.
        """
        results = []
        for f in self.factors:
            if f.impact_score < 0 and f.mitigation.strip():
                results.append({
                    "name": f"[PESTEL-{f.category.value[:3].upper()}] {f.description[:80]}",
                    "category": "External",
                    "probability": f.probability,
                    "impact": abs(f.impact_score) * 1000,  # scale to dollars
                    "mitigation": f.mitigation,
                })
        return results

    # -- Serialisation --

    def to_dict(self) -> dict:
        return {"factors": [f.to_dict() for f in self.factors]}

    @classmethod
    def from_dict(cls, d: dict) -> "PESTELAnalysis":
        factors = [PESTELFactor.from_dict(fd) for fd in d.get("factors", [])]
        return cls(factors=factors)
