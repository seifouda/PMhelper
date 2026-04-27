"""
PMhelper Edu — SWOT Extractor.
Auto-populate SWOT factors from Charter, Risk Register, and EVM KPIs.
All methods are static / pure functions — no side effects.
"""

from __future__ import annotations
from typing import List, Optional, Any

from pmhelper.core.swot_models_edu import (
    SWOTFactor, SWOTCategory, SWOTSource, SWOTAnalysis,
)


class SWOTExtractor:
    """Static methods to extract SWOT factors from project data sources."""

    # ------------------------------------------------------------------
    # Charter → SWOT
    # ------------------------------------------------------------------

    @staticmethod
    def from_charter(charter_data: dict) -> List[SWOTFactor]:
        """Extract SWOT factors from Charter tab data.

        Args:
            charter_data: dict with keys like 'business_case',
                          'strategic_alignment', 'constraints',
                          'assumptions', 'dependencies',
                          'high_level_requirements', 'stakeholders', etc.

        Returns:
            List of SWOTFactor objects.
        """
        factors: List[SWOTFactor] = []

        # Business case → Opportunity
        bc = charter_data.get("business_case", "").strip()
        if bc:
            factors.append(SWOTFactor(
                text=f"Strategic opportunity: {bc[:120]}",
                category=SWOTCategory.OPPORTUNITY,
                source=SWOTSource.CHARTER,
                weight=0.8,
                linked_to="business_case",
            ))

        # Strategic alignment → Opportunity
        sa = charter_data.get("strategic_alignment", "").strip()
        if sa:
            factors.append(SWOTFactor(
                text=f"Strategic alignment: {sa[:120]}",
                category=SWOTCategory.OPPORTUNITY,
                source=SWOTSource.CHARTER,
                weight=0.7,
                linked_to="strategic_alignment",
            ))

        # High-level requirements → Strength (capability building)
        hlr = charter_data.get("high_level_requirements", "").strip()
        if hlr:
            factors.append(SWOTFactor(
                text=f"Delivers key capability: {hlr[:120]}",
                category=SWOTCategory.STRENGTH,
                source=SWOTSource.CHARTER,
                weight=0.7,
                linked_to="high_level_requirements",
            ))

        # Constraints → Weakness
        constraints = charter_data.get("constraints", [])
        if isinstance(constraints, str) and constraints.strip():
            constraints = [constraints]
        for i, c in enumerate(constraints[:3]):  # max 3 to avoid clutter
            text = c if isinstance(c, str) else str(c)
            if text.strip():
                factors.append(SWOTFactor(
                    text=f"Constraint: {text.strip()[:120]}",
                    category=SWOTCategory.WEAKNESS,
                    source=SWOTSource.CHARTER,
                    weight=0.6,
                    linked_to=f"constraint_{i}",
                ))

        # Assumptions → Threat (high-risk if they prove false)
        assumptions = charter_data.get("assumptions", [])
        if isinstance(assumptions, str) and assumptions.strip():
            assumptions = [assumptions]
        for i, a in enumerate(assumptions[:3]):
            text = a if isinstance(a, str) else str(a)
            if text.strip():
                factors.append(SWOTFactor(
                    text=f"Assumption risk: {text.strip()[:120]}",
                    category=SWOTCategory.THREAT,
                    source=SWOTSource.CHARTER,
                    weight=0.5,
                    linked_to=f"assumption_{i}",
                ))

        # Dependencies → Threat (external blockers)
        deps = charter_data.get("dependencies", [])
        if isinstance(deps, str) and deps.strip():
            deps = [deps]
        for i, d in enumerate(deps[:3]):
            text = d if isinstance(d, str) else str(d)
            if text.strip():
                factors.append(SWOTFactor(
                    text=f"External dependency: {text.strip()[:120]}",
                    category=SWOTCategory.THREAT,
                    source=SWOTSource.CHARTER,
                    weight=0.6,
                    linked_to=f"dependency_{i}",
                ))

        # Stakeholders → can be Strength (high support) or Weakness (conflicts)
        stakeholders = charter_data.get("stakeholders", [])
        if isinstance(stakeholders, list):
            for sh in stakeholders[:3]:
                if isinstance(sh, dict):
                    name = sh.get("name", "Unknown")
                    influence = sh.get("influence", "")
                    if str(influence).lower() in (
                            "high", "sponsor", "champion"):
                        factors.append(SWOTFactor(
                            text=f"Strong sponsor: {name}",
                            category=SWOTCategory.STRENGTH,
                            source=SWOTSource.CHARTER,
                            weight=0.8,
                            linked_to=f"stakeholder_{name}",
                        ))

        return factors

    # ------------------------------------------------------------------
    # Risk Register → SWOT Threats
    # ------------------------------------------------------------------

    @staticmethod
    def from_risk_register(
            risk_register: Any,
            bac: float = 0.0) -> List[SWOTFactor]:
        """Extract SWOT Threats from high-exposure risks.

        Args:
            risk_register: RiskRegister instance with .risks list and .flag_high_exposure()
            bac: Budget at completion for threshold calculation

        Returns:
            List of SWOTFactor objects (always Threats).
        """
        factors: List[SWOTFactor] = []

        if risk_register is None:
            return factors

        # Use the register's flag method if available
        try:
            high_risks = risk_register.flag_high_exposure()
        except Exception:
            high_risks = []

        # Fallback: manual filtering if flag_high_exposure not available
        if not high_risks and hasattr(risk_register, 'risks'):
            threshold = bac * 0.05 if bac > 0 else 0
            high_risks = [
                r for r in risk_register.risks
                if getattr(r, 'exposure', 0) > threshold
            ]

        for risk in high_risks[:5]:  # max 5
            name = getattr(risk, 'name', 'Unknown risk')
            exposure = getattr(risk, 'exposure', 0)
            risk_id = getattr(risk, 'id', '')
            weight = min(1.0, exposure / bac) if bac > 0 else 0.5

            factors.append(SWOTFactor(
                text=f"Risk: {name} (exposure ${exposure:,.0f})",
                category=SWOTCategory.THREAT,
                source=SWOTSource.RISK_REGISTER,
                weight=round(weight, 2),
                linked_to=risk_id,
            ))

        return factors

    # ------------------------------------------------------------------
    # EVM KPIs → SWOT Strengths/Weaknesses
    # ------------------------------------------------------------------

    @staticmethod
    def from_evm(kpis: dict, bac: float = 0.0) -> List[SWOTFactor]:
        """Extract SWOT factors from EVM KPI values.

        Args:
            kpis: dict with keys like 'cpi', 'spi', 'cv', 'sv', 'eac1', etc.
            bac: Budget at completion

        Returns:
            List of SWOTFactor objects (Strengths if healthy, Weaknesses if unhealthy).
        """
        factors: List[SWOTFactor] = []

        cpi = kpis.get("cpi")
        spi = kpis.get("spi")

        if cpi is not None:
            if cpi >= 1.0:
                factors.append(SWOTFactor(
                    text=f"Cost efficiency: CPI = {cpi:.2f} (under budget)",
                    category=SWOTCategory.STRENGTH,
                    source=SWOTSource.EVM,
                    weight=min(1.0, cpi - 0.9),
                    linked_to="cpi",
                ))
            elif cpi < 0.95:
                factors.append(SWOTFactor(
                    text=f"Cost overrun: CPI = {cpi:.2f} (overspending)",
                    category=SWOTCategory.WEAKNESS,
                    source=SWOTSource.EVM,
                    weight=min(1.0, 1.0 - cpi),
                    linked_to="cpi",
                ))

        if spi is not None:
            if spi >= 1.0:
                factors.append(
                    SWOTFactor(
                        text=f"Schedule efficiency: SPI = {
                            spi:.2f} (ahead of schedule)",
                        category=SWOTCategory.STRENGTH,
                        source=SWOTSource.EVM,
                        weight=min(
                            1.0,
                            spi - 0.9),
                        linked_to="spi",
                    ))
            elif spi < 0.95:
                factors.append(SWOTFactor(
                    text=f"Schedule delay: SPI = {spi:.2f} (behind schedule)",
                    category=SWOTCategory.WEAKNESS,
                    source=SWOTSource.EVM,
                    weight=min(1.0, 1.0 - spi),
                    linked_to="spi",
                ))

        # EAC overrun → Weakness
        eac = kpis.get("eac1") or kpis.get("eac")
        if eac is not None and bac > 0:
            overrun_pct = (eac - bac) / bac
            if overrun_pct > 0.10:
                factors.append(
                    SWOTFactor(
                        text=f"Forecast overrun: EAC ${
                            eac:,.0f} exceeds BAC by {
                            overrun_pct:.0%}",
                        category=SWOTCategory.WEAKNESS,
                        source=SWOTSource.EVM,
                        weight=min(
                            1.0,
                            overrun_pct),
                        linked_to="eac",
                    ))

        return factors

    # ------------------------------------------------------------------
    # Convenience: extract from all sources at once
    # ------------------------------------------------------------------

    @staticmethod
    def extract_all(
        charter_data: Optional[dict] = None,
        risk_register: Any = None,
        kpis: Optional[dict] = None,
        bac: float = 0.0,
    ) -> SWOTAnalysis:
        """Extract SWOT factors from all available data sources.

        Returns:
            SWOTAnalysis populated with auto-extracted factors.
        """
        analysis = SWOTAnalysis()

        if charter_data:
            for f in SWOTExtractor.from_charter(charter_data):
                analysis.add_factor(f)

        if risk_register is not None:
            for f in SWOTExtractor.from_risk_register(risk_register, bac):
                analysis.add_factor(f)

        if kpis:
            for f in SWOTExtractor.from_evm(kpis, bac):
                analysis.add_factor(f)

        return analysis
