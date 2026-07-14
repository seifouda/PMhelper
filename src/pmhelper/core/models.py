"""
Data Models for Project Selection Module

Defines Pydantic models for criteria, alternatives, projects, and selection problems.
Supports serialization to/from JSON format (.pmsel files).

Author: PMHelper Team
Version: 1.0.0
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class CriterionDirection(str, Enum):
    """Direction for criterion optimization"""
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


class SelectionMethod(str, Enum):
    """Available selection methods"""
    AHP = "ahp"
    LINEAR_SCORING = "linear_scoring"
    BENEFIT_COST = "benefit_cost"
    PORTFOLIO = "portfolio"


class Criterion(BaseModel):
    """
    Represents a decision criterion.
    
    Attributes:
        name: Criterion name
        weight: Criterion weight (0.0 to 1.0)
        direction: Optimization direction (maximize or minimize)
        description: Optional description
    """
    name: str = Field(..., min_length=1, max_length=100)
    weight: float = Field(default=0.0, ge=0.0, le=1.0)
    direction: CriterionDirection
    description: Optional[str] = Field(default=None, max_length=500)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure criterion name is not just whitespace"""
        if not v.strip():
            raise ValueError("Criterion name cannot be empty or whitespace")
        return v.strip()
    
    model_config = ConfigDict(use_enum_values=True)


class Alternative(BaseModel):
    """
    Represents a decision alternative.
    
    Attributes:
        id: Unique identifier
        name: Alternative name
        scores: Dictionary mapping criterion names to scores
        metadata: Optional additional data
    """
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    scores: Dict[str, float] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('id', 'name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure fields are not empty or whitespace"""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()
    
    model_config = ConfigDict(use_enum_values=True)


class Project(BaseModel):
    """
    Represents a project for portfolio optimization or B/C analysis.
    
    Attributes:
        id: Unique identifier
        name: Project name
        cost: Initial cost
        benefit: Annual benefit
        life: Project life in years
        annual_om: Annual operations & maintenance cost
        salvage: Salvage value at end of life
        scores: Optional criterion scores for multi-criteria analysis
        metadata: Optional additional data
    """
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    cost: float = Field(..., gt=0)
    benefit: float = Field(..., ge=0)
    life: Optional[int] = Field(default=None, gt=0)
    annual_om: float = Field(default=0.0, ge=0)
    salvage: float = Field(default=0.0, ge=0)
    scores: Optional[Dict[str, float]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('id', 'name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure fields are not empty or whitespace"""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()
    
    @field_validator('cost', 'benefit')
    @classmethod
    def validate_financial(cls, v: float) -> float:
        """Ensure financial values are reasonable"""
        if v < 0:
            raise ValueError(f"Value cannot be negative")
        return v
    
    model_config = ConfigDict(use_enum_values=True)


class AHPMatrix(BaseModel):
    """
    Represents an AHP pairwise comparison matrix.
    
    Attributes:
        criteria: List of criterion names
        matrix: 2D list representing comparison matrix
        consistency_ratio: Calculated CR value
    """
    criteria: List[str] = Field(..., min_length=2)
    matrix: List[List[float]] = Field(...)
    consistency_ratio: Optional[float] = Field(default=None, ge=0.0)
    
    @field_validator('matrix')
    @classmethod
    def validate_matrix(cls, v: List[List[float]], info) -> List[List[float]]:
        """Ensure matrix is square and matches criteria count"""
        if info.data and 'criteria' in info.data:
            n = len(info.data['criteria'])
            if len(v) != n:
                raise ValueError(f"Matrix must have {n} rows, got {len(v)}")
            for i, row in enumerate(v):
                if len(row) != n:
                    raise ValueError(f"Row {i} must have {n} columns, got {len(row)}")
        return v


class PortfolioConstraint(BaseModel):
    """
    Represents a constraint for portfolio optimization.
    
    Attributes:
        type: Constraint type (mutually_exclusive, dependency, resource)
        projects: List of project IDs involved
        requires: For dependency constraints, the required project ID
        capacity: For resource constraints, the capacity limit
        demands: For resource constraints, demands by project
    """
    type: str = Field(..., pattern="^(mutually_exclusive|dependency|resource)$")
    projects: Optional[List[str]] = Field(default=None)
    requires: Optional[str] = Field(default=None)
    capacity: Optional[float] = Field(default=None, gt=0)
    demands: Optional[Dict[str, float]] = Field(default=None)
    
    @field_validator('projects')
    @classmethod
    def validate_mutually_exclusive(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """Validate mutually exclusive constraints"""
        if info.data and info.data.get('type') == 'mutually_exclusive':
            if not v or len(v) < 2:
                raise ValueError("Mutually exclusive constraint requires at least 2 projects")
        return v
    
    @field_validator('requires')
    @classmethod
    def validate_dependency(cls, v: Optional[str], info) -> Optional[str]:
        """Validate dependency constraints"""
        if info.data and info.data.get('type') == 'dependency':
            if not v:
                raise ValueError("Dependency constraint requires 'requires' field")
            if info.data.get('projects') and len(info.data['projects']) != 1:
                raise ValueError("Dependency constraint requires exactly 1 project")
        return v


class SelectionProblem(BaseModel):
    """
    Represents a complete project selection problem.
    
    Attributes:
        id: Unique identifier
        name: Problem name
        description: Problem description
        method: Selection method to use
        criteria: List of criteria
        alternatives: List of alternatives (for AHP/Linear Scoring)
        projects: List of projects (for B/C/Portfolio)
        ahp_matrix: AHP comparison matrix (if method is AHP)
        budget: Budget constraint (for portfolio optimization)
        marr: Minimum Attractive Rate of Return (for B/C analysis)
        constraints: List of constraints (for portfolio optimization)
        results: Stored results from previous analysis
        created_at: Creation timestamp
        updated_at: Last update timestamp
        version: File format version
    """
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    method: SelectionMethod
    criteria: List[Criterion] = Field(default_factory=list)
    alternatives: Optional[List[Alternative]] = Field(default=None)
    projects: Optional[List[Project]] = Field(default=None)
    ahp_matrix: Optional[AHPMatrix] = Field(default=None)
    budget: Optional[float] = Field(default=None, gt=0)
    marr: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    constraints: Optional[List[PortfolioConstraint]] = Field(default=None)
    results: Optional[Dict[str, Any]] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0")
    
    @field_validator('id', 'name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure fields are not empty or whitespace"""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()
    
    @field_validator('criteria')
    @classmethod
    def validate_criteria_weights(cls, v: List[Criterion]) -> List[Criterion]:
        """Validate that criterion weights sum to approximately 1.0 if all set"""
        if v:
            weights = [c.weight for c in v if c.weight > 0]
            if weights and len(weights) == len(v):
                total = sum(weights)
                if not (0.99 <= total <= 1.01):
                    raise ValueError(f"Criterion weights must sum to 1.0, got {total:.3f}")
        return v
    
    @field_validator('alternatives')
    @classmethod
    def validate_alternatives_method(cls, v: Optional[List[Alternative]], info) -> Optional[List[Alternative]]:
        """Ensure alternatives are provided for appropriate methods"""
        if info.data:
            method = info.data.get('method')
            if method in [SelectionMethod.AHP, SelectionMethod.LINEAR_SCORING]:
                if not v:
                    raise ValueError(f"Method {method} requires alternatives")
        return v
    
    @field_validator('projects')
    @classmethod
    def validate_projects_method(cls, v: Optional[List[Project]], info) -> Optional[List[Project]]:
        """Ensure projects are provided for appropriate methods"""
        if info.data:
            method = info.data.get('method')
            if method in [SelectionMethod.BENEFIT_COST, SelectionMethod.PORTFOLIO]:
                if not v:
                    raise ValueError(f"Method {method} requires projects")
        return v
    
    @field_validator('budget')
    @classmethod
    def validate_budget_method(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure budget is provided for portfolio optimization"""
        if info.data:
            method = info.data.get('method')
            if method == SelectionMethod.PORTFOLIO and v is None:
                raise ValueError("Portfolio optimization requires budget")
        return v
    
    @field_validator('marr')
    @classmethod
    def validate_marr_method(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure MARR is provided for B/C analysis"""
        if info.data:
            method = info.data.get('method')
            if method == SelectionMethod.BENEFIT_COST and v is None:
                raise ValueError("B/C analysis requires MARR")
        return v
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class SelectionResult(BaseModel):
    """
    Represents the results of a selection analysis.
    
    Attributes:
        problem_id: ID of the problem analyzed
        method: Method used
        timestamp: Analysis timestamp
        ranked_items: Ranked list of alternatives/projects
        optimal_item: Optimal choice (if applicable)
        total_score: Total score/benefit
        details: Additional analysis details
        warnings: Any warnings generated during analysis
    """
    problem_id: str
    method: SelectionMethod
    timestamp: datetime = Field(default_factory=datetime.now)
    ranked_items: List[Dict[str, Any]] = Field(default_factory=list)
    optimal_item: Optional[Dict[str, Any]] = Field(default=None)
    total_score: Optional[float] = Field(default=None)
    details: Optional[Dict[str, Any]] = Field(default=None)
    warnings: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )
