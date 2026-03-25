"""DPCI (Design-Complexity Project Index) data models."""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class RiskLevel(Enum):
    """Overall project risk level."""
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"
    CRITICAL = "Critical Risk"


@dataclass
class DPCIAssessment:
    """DPCI assessment data model."""
    
    # Metadata
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    assessed_by: str = ""
    organization: str = ""
    description: str = ""
    
    # Dimension scores (0-4 each, but each dimension has 4 criteria, so total is 0-16 per dimension)
    pdr_score: int = 0  # Project Definition Rating
    or_score: int = 0   # Organizational Rating
    tr_score: int = 0   # Technical Rating
    er_score: int = 0   # Environment Rating
    
    # Detailed scores for each dimension
    pdr_details: Dict[str, int] = field(default_factory=dict)
    or_details: Dict[str, int] = field(default_factory=dict)
    tr_details: Dict[str, int] = field(default_factory=dict)
    er_details: Dict[str, int] = field(default_factory=dict)
    
    # Notes
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DPCIAssessment':
        """Create from dictionary."""
        return cls(**data)
    
    def get_dpci_index(self) -> str:
        """Get the DPCI index in format: PDR-OR-TR-ER."""
        return f"{self.pdr_score}-{self.or_score}-{self.tr_score}-{self.er_score}"
    
    def get_average_score(self) -> float:
        """Get average score across all dimensions."""
        return (self.pdr_score + self.or_score + self.tr_score + self.er_score) / 4.0
    
    def get_total_score(self) -> int:
        """Get total score across all dimensions (0-64)."""
        return self.pdr_score + self.or_score + self.tr_score + self.er_score
    
    def get_max_score(self) -> int:
        """Get maximum score across all dimensions."""
        return max(self.pdr_score, self.or_score, self.tr_score, self.er_score)
    
    def get_overall_risk_level(self) -> RiskLevel:
        """Determine overall project risk level."""
        max_score = self.get_max_score()
        avg_score = self.get_average_score()
        
        if max_score >= 4:
            return RiskLevel.CRITICAL
        elif max_score >= 3 or avg_score >= 2.5:
            return RiskLevel.HIGH
        elif avg_score >= 1.5:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def is_complete(self) -> bool:
        """Check if assessment has all required data."""
        return bool(self.project_name and 
                   (self.pdr_score > 0 or self.or_score > 0 or 
                    self.tr_score > 0 or self.er_score > 0))
    
    def get_pm_recommendations(self) -> Dict[str, Any]:
        """Get PM recommendations as a structured dict."""
        risk_level = self.get_overall_risk_level()
        actions = []
        
        if risk_level == RiskLevel.CRITICAL:
            level = "Exceptional PM Required"
            description = "This project requires an exceptional project manager with extensive experience in complex, high-risk projects."
            actions.append("Consider splitting into smaller, manageable projects")
            actions.append("Implement extensive risk management protocols")
        elif risk_level == RiskLevel.HIGH:
            level = "Experienced PM Required"
            description = "This project requires an experienced project manager with proven success in complex projects."
            actions.append("Implement rigorous risk management")
            actions.append("Establish clear governance structure")
        elif risk_level == RiskLevel.MODERATE:
            level = "Competent PM Required"
            description = "This project requires a competent project manager with solid PM fundamentals."
            actions.append("Apply standard PM practices")
            actions.append("Monitor key risk areas")
        else:
            level = "Basic PM Experience"
            description = "This project can be managed by a PM with basic PM experience."
            actions.append("Lightweight PM approach suitable")
        
        if self.pdr_score >= 12:
            actions.append("📋 PDR: Invest significantly in requirements gathering")
        if self.or_score >= 12:
            actions.append("👥 OR: Focus heavily on stakeholder management")
        if self.tr_score >= 12:
            actions.append("🔧 TR: Conduct technical proof-of-concept")
        if self.er_score >= 12:
            actions.append("🌍 ER: Build in flexibility for environmental changes")
        
        avg_score = self.get_average_score()
        if avg_score >= 12.0:
            actions.append("📊 Methodology: Consider Agile/Adaptive approach")
        elif avg_score >= 8.0:
            actions.append("📊 Methodology: Hybrid approach recommended")
        else:
            actions.append("📊 Methodology: Predictive/Waterfall suitable")
        
        return {
            'level': level,
            'description': description,
            'actions': actions
        }
    
    def get_control_recommendations(self) -> Dict[str, str]:
        """Get control level recommendations as a structured dict."""
        max_score = self.get_max_score()
        
        if max_score >= 12:
            level = "Maximum Control"
            description = "Daily monitoring, extensive documentation, frequent stakeholder updates, and detailed change control processes required."
        elif max_score >= 8:
            level = "High Control"
            description = "Weekly monitoring, comprehensive documentation, regular stakeholder updates, and formal change control required."
        elif max_score >= 4:
            level = "Moderate Control"
            description = "Bi-weekly monitoring, standard documentation, periodic stakeholder updates, and basic change control required."
        else:
            level = "Light Control"
            description = "Monthly monitoring, minimal documentation, occasional stakeholder updates, and informal change control acceptable."
        
        return {
            'level': level,
            'description': description
        }


class DPCICalculator:
    """Calculator for DPCI scores and recommendations."""
    
    # Questionnaire structure
    QUESTIONNAIRE = {
        "PDR": {
            "title": "Project Definition Rating (PDR)",
            "description": "Evaluates how clearly the project is defined",
            "criteria": [
                {"id": "scope", "question": "How clear is the project scope?",
                 "levels": {0: "Crystal clear", 1: "Clear", 2: "Moderate", 3: "Unclear", 4: "Very vague"}},
                {"id": "requirements", "question": "How well documented are requirements?",
                 "levels": {0: "Fully documented", 1: "Mostly documented", 2: "Some gaps", 3: "Few documented", 4: "Unknown"}},
                {"id": "objectives", "question": "How clear are project objectives?",
                 "levels": {0: "SMART objectives", 1: "Clear objectives", 2: "Vague criteria", 3: "Unclear", 4: "No clear objectives"}},
                {"id": "constraints", "question": "How well understood are constraints?",
                 "levels": {0: "All identified", 1: "Major identified", 2: "Some uncertain", 3: "Many unclear", 4: "Undefined"}}
            ]
        },
        "OR": {
            "title": "Organizational Rating (OR)",
            "description": "Evaluates organizational and cultural factors",
            "criteria": [
                {"id": "culture", "question": "How supportive is organizational culture?",
                 "levels": {0: "Highly supportive", 1: "Supportive", 2: "Neutral", 3: "Resistant", 4: "Highly resistant"}},
                {"id": "authority", "question": "How clear is decision-making authority?",
                 "levels": {0: "Clear authority", 1: "Adequate", 2: "Limited", 3: "Unclear", 4: "No authority"}},
                {"id": "stakeholders", "question": "How aligned are stakeholders?",
                 "levels": {0: "Fully aligned", 1: "Key aligned", 2: "Some conflicts", 3: "Significant conflicts", 4: "Major conflicts"}},
                {"id": "resources", "question": "How available are resources?",
                 "levels": {0: "Dedicated", 1: "Available", 2: "Shared", 3: "Scarce", 4: "No resources"}}
            ]
        },
        "TR": {
            "title": "Technical Rating (TR)",
            "description": "Evaluates technical complexity and uncertainty",
            "criteria": [
                {"id": "technology", "question": "How mature is the technology?",
                 "levels": {0: "Mature/proven", 1: "Established", 2: "New", 3: "Cutting-edge", 4: "Unproven"}},
                {"id": "integration", "question": "How complex is integration?",
                 "levels": {0: "Standalone", 1: "Simple", 2: "Moderate", 3: "Complex", 4: "Extremely complex"}},
                {"id": "expertise", "question": "How available is technical expertise?",
                 "levels": {0: "In-house", 1: "Available", 2: "External help needed", 3: "Rare", 4: "Not available"}},
                {"id": "complexity", "question": "How complex is the solution?",
                 "levels": {0: "Simple", 1: "Moderately simple", 2: "Moderate", 3: "High", 4: "Extremely complex"}}
            ]
        },
        "ER": {
            "title": "Environment Rating (ER)",
            "description": "Evaluates external environmental factors",
            "criteria": [
                {"id": "market", "question": "How stable is the market?",
                 "levels": {0: "Very stable", 1: "Stable", 2: "Some volatility", 3: "Volatile", 4: "Extremely turbulent"}},
                {"id": "regulations", "question": "How complex are regulations?",
                 "levels": {0: "No requirements", 1: "Simple", 2: "Moderate", 3: "Complex", 4: "Highly complex"}},
                {"id": "customer", "question": "How demanding are customers?",
                 "levels": {0: "Minimal involvement", 1: "Reasonable", 2: "Frequent", 3: "Highly demanding", 4: "Unrealistic"}},
                {"id": "dependencies", "question": "How many external dependencies?",
                 "levels": {0: "None", 1: "Few reliable", 2: "Several", 3: "Many unreliable", 4: "Critical/unreliable"}}
            ]
        }
    }
    
    @staticmethod
    def calculate_dimension_score(detail_scores: Dict[str, int]) -> int:
        """Calculate overall dimension score from detailed scores."""
        if not detail_scores:
            return 0
        return round(sum(detail_scores.values()) / len(detail_scores))
    
    @staticmethod
    def get_pm_recommendations(assessment: DPCIAssessment) -> List[str]:
        """Get project management recommendations based on DPCI scores."""
        recommendations = []
        risk_level = assessment.get_overall_risk_level()
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("⚠️ CRITICAL: Requires exceptional PM expertise")
            recommendations.append("Consider splitting into smaller projects")
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("⚠️ HIGH RISK: Requires experienced PM")
            recommendations.append("Implement rigorous risk management")
        elif risk_level == RiskLevel.MODERATE:
            recommendations.append("✓ MODERATE: Requires competent PM")
            recommendations.append("Standard PM practices recommended")
        else:
            recommendations.append("✓ LOW RISK: Basic PM experience acceptable")
            recommendations.append("Lightweight approach suitable")
        
        if assessment.pdr_score >= 3:
            recommendations.append("📋 PDR: Invest in requirements gathering")
        if assessment.or_score >= 3:
            recommendations.append("👥 OR: Focus on stakeholder management")
        if assessment.tr_score >= 3:
            recommendations.append("🔧 TR: Conduct technical proof-of-concept")
        if assessment.er_score >= 3:
            recommendations.append("🌍 ER: Build in flexibility for changes")
        
        avg_score = assessment.get_average_score()
        if avg_score >= 3.0:
            recommendations.append("📊 Methodology: Consider Agile/Adaptive")
        elif avg_score >= 2.0:
            recommendations.append("📊 Methodology: Hybrid approach recommended")
        else:
            recommendations.append("📊 Methodology: Predictive/Waterfall suitable")
        
        return recommendations
    
    @staticmethod
    def get_control_level_recommendation(assessment: DPCIAssessment) -> str:
        """Get recommendation for project control level."""
        max_score = assessment.get_max_score()
        
        if max_score >= 4:
            return "MAXIMUM CONTROL: Daily monitoring, extensive documentation"
        elif max_score >= 3:
            return "HIGH CONTROL: Weekly monitoring, comprehensive documentation"
        elif max_score >= 2:
            return "MODERATE CONTROL: Bi-weekly monitoring, standard documentation"
        else:
            return "LIGHT CONTROL: Monthly monitoring, minimal documentation"
    
    @staticmethod
    def get_questionnaire_structure() -> Dict:
        """Get the complete questionnaire structure."""
        return DPCICalculator.QUESTIONNAIRE
    
    @staticmethod
    def get_dimension_risk_level(score: int) -> RiskLevel:
        """Get risk level for a single dimension score (0-16)."""
        if score >= 12:
            return RiskLevel.CRITICAL
        elif score >= 8:
            return RiskLevel.HIGH
        elif score >= 4:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
