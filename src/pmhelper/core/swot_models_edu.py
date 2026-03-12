"""
PMhelper Edu — SWOT Analysis Data Model.
SWOTFactor and SWOTAnalysis dataclasses with to_dict()/from_dict() round-trip.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from enum import Enum


class SWOTCategory(str, Enum):
    """The four SWOT quadrants."""
    STRENGTH = "Strength"
    WEAKNESS = "Weakness"
    OPPORTUNITY = "Opportunity"
    THREAT = "Threat"


class SWOTSource(str, Enum):
    """Where a SWOT factor was extracted from."""
    CHARTER = "Charter"
    RISK_REGISTER = "Risk Register"
    EVM = "EVM"
    MANUAL = "Manual"


@dataclass
class SWOTFactor:
    """A single SWOT factor (one item in one quadrant)."""
    text: str
    category: SWOTCategory
    source: SWOTSource = SWOTSource.MANUAL
    weight: float = 0.5        # 0.0–1.0 importance weight
    linked_to: str = ""       # e.g. "risk_id_42", "business_case"

    def validate(self) -> List[str]:
        """Validate factor data. Returns list of error messages."""
        errors: List[str] = []
        if not self.text.strip():
            errors.append("SWOT factor text is required.")
        if not 0.0 <= self.weight <= 1.0:
            errors.append(f"Weight must be 0.0–1.0, got {self.weight}.")
        return errors

    def to_dict(self) -> dict:
        """Serialise to JSON-safe dict."""
        return {
            "text": self.text,
            "category": self.category.value,
            "source": self.source.value,
            "weight": self.weight,
            "linked_to": self.linked_to,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SWOTFactor:
        """Reconstruct from dict."""
        return cls(
            text=data["text"],
            category=SWOTCategory(data["category"]),
            source=SWOTSource(data.get("source", "Manual")),
            weight=data.get("weight", 1.0),
            linked_to=data.get("linked_to"),
        )


@dataclass
class SWOTAnalysis:
    """Complete SWOT analysis containing factors in all four quadrants."""
    factors: List[SWOTFactor] = field(default_factory=list)

    @property
    def strengths(self) -> List[SWOTFactor]:
        """All Strength factors."""
        return [f for f in self.factors if f.category == SWOTCategory.STRENGTH]

    @property
    def weaknesses(self) -> List[SWOTFactor]:
        """All Weakness factors."""
        return [f for f in self.factors if f.category == SWOTCategory.WEAKNESS]

    @property
    def opportunities(self) -> List[SWOTFactor]:
        """All Opportunity factors."""
        return [f for f in self.factors if f.category == SWOTCategory.OPPORTUNITY]

    @property
    def threats(self) -> List[SWOTFactor]:
        """All Threat factors."""
        return [f for f in self.factors if f.category == SWOTCategory.THREAT]

    def add_factor(self, factor: SWOTFactor) -> None:
        """Add a factor to the analysis."""
        self.factors.append(factor)

    def remove_factor(self, factor: SWOTFactor) -> bool:
        """Remove a factor from the analysis."""
        try:
            self.factors.remove(factor)
            return True
        except ValueError:
            return False

    def clear_category(self, category: SWOTCategory) -> None:
        """Remove all factors in a given category."""
        self.factors = [f for f in self.factors if f.category != category]

    def clear(self) -> None:
        """Remove all factors."""
        self.factors.clear()

    def clear_by_source(self, source: SWOTSource) -> None:
        """Remove all factors from a specific source."""
        self.factors = [f for f in self.factors if f.source != source]

    def factor_count(self) -> int:
        """Total number of factors."""
        return len(self.factors)

    def count_by_category(self) -> dict:
        """Count factors per category."""
        return {
            SWOTCategory.STRENGTH: len(self.strengths),
            SWOTCategory.WEAKNESS: len(self.weaknesses),
            SWOTCategory.OPPORTUNITY: len(self.opportunities),
            SWOTCategory.THREAT: len(self.threats),
        }

    def to_dict(self) -> dict:
        """Serialise to JSON-safe dict."""
        return {
            "factors": [f.to_dict() for f in self.factors],
        }

    @classmethod
    def from_dict(cls, data: dict) -> SWOTAnalysis:
        """Reconstruct from dict."""
        factors = []
        # Support flat format
        for item in data.get("factors", []):
            factors.append(SWOTFactor.from_dict(item))
        # Legacy: support by-category format
        if not factors:
            for cat_key, cat_enum in [
                ("strengths", SWOTCategory.STRENGTH),
                ("weaknesses", SWOTCategory.WEAKNESS),
                ("opportunities", SWOTCategory.OPPORTUNITY),
                ("threats", SWOTCategory.THREAT),
            ]:
                for item in data.get(cat_key, []):
                    item["category"] = cat_enum.value
                    factors.append(SWOTFactor.from_dict(item))
        return cls(factors=factors)
