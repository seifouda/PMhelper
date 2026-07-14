"""
Project Selection API Routes

REST API endpoints for project selection and decision analysis.
Provides endpoints for AHP, Linear Scoring, B/C Analysis, and Portfolio Optimization.

Author: PMHelper Team
Version: 1.0.0
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
import logging
from datetime import datetime
import numpy as np

from pmhelper.core.selection import (
    AHPAnalyzer, LinearScoringAnalyzer, BenefitCostAnalyzer,
    PortfolioOptimizer, CriterionDirection
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/selection", tags=["selection"])


# Request/Response Models
class CriterionRequest(BaseModel):
    """Criterion definition for analysis."""
    name: str = Field(..., description="Criterion name",
                      min_length=1, max_length=100)
    direction: str = Field(...,
                           description="Optimization direction: 'maximize' or 'minimize'")
    weight: Optional[float] = Field(
        None, description="Criterion weight (0-1)", ge=0, le=1)

    @field_validator('direction')
    @classmethod
    def validate_direction(cls, v):
        if v not in ['maximize', 'minimize']:
            raise ValueError("direction must be 'maximize' or 'minimize'")
        return v


class AlternativeRequest(BaseModel):
    """Alternative with scores for each criterion."""
    name: str = Field(..., description="Alternative name",
                      min_length=1, max_length=100)
    scores: Dict[str, float] = Field(...,
                                     description="Scores for each criterion")


class ProjectRequest(BaseModel):
    """Project definition for portfolio or B/C analysis."""
    name: str = Field(..., description="Project name",
                      min_length=1, max_length=100)
    cost: float = Field(..., description="Project cost", gt=0)
    benefit: float = Field(..., description="Annual benefit", gt=0)
    life: Optional[int] = Field(
        None, description="Project life in years", gt=0)
    initial_cost: Optional[float] = Field(
        None, description="Initial investment cost", ge=0)
    annual_om: Optional[float] = Field(
        None, description="Annual O&M cost", ge=0)
    salvage: Optional[float] = Field(None, description="Salvage value", ge=0)


class AHPRequest(BaseModel):
    """Request model for AHP analysis."""
    criteria: List[str] = Field(...,
                                description="List of criterion names",
                                min_length=2)
    comparisons: Dict[str, Dict[str, float]] = Field(
        ...,
        description="Pairwise comparisons matrix: {criterion_i: {criterion_j: value}}"
    )
    alternatives: Optional[List[AlternativeRequest]] = Field(
        None,
        description="Alternatives to rank (optional)"
    )


class AHPResponse(BaseModel):
    """Response model for AHP analysis."""
    method: str = "AHP"
    consistency_ratio: float = Field(...,
                                     description="Consistency ratio (should be < 0.1)")
    is_consistent: bool = Field(..., description="True if CR < 0.1")
    weights: Dict[str, float] = Field(..., description="Criterion weights")
    ranked_alternatives: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Ranked alternatives with scores"
    )
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class LinearScoringRequest(BaseModel):
    """Request model for Linear Scoring analysis."""
    criteria: List[CriterionRequest] = Field(...,
                                             description="Criteria with weights and directions",
                                             min_length=1)
    alternatives: List[AlternativeRequest] = Field(
        ..., description="Alternatives to evaluate", min_length=2)
    sensitivity_analysis: bool = Field(
        False, description="Perform sensitivity analysis")


class LinearScoringResponse(BaseModel):
    """Response model for Linear Scoring analysis."""
    method: str = "LinearScoring"
    ranked_alternatives: List[Dict[str, Any]
                              ] = Field(..., description="Ranked alternatives")
    sensitivity_results: Optional[Dict[str, Any]] = Field(
        None, description="Sensitivity analysis results")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class BenefitCostRequest(BaseModel):
    """Request model for B/C analysis."""
    projects: List[ProjectRequest] = Field(...,
                                           description="Projects to analyze",
                                           min_length=1)
    marr: float = Field(...,
                        description="Minimum Attractive Rate of Return",
                        gt=0,
                        le=1)
    analysis_type: str = Field(
        "mutually_exclusive",
        description="Analysis type: 'independent' or 'mutually_exclusive'")

    @field_validator('analysis_type')
    @classmethod
    def validate_analysis_type(cls, v):
        if v not in ['independent', 'mutually_exclusive']:
            raise ValueError(
                "analysis_type must be 'independent' or 'mutually_exclusive'")
        return v


class BenefitCostResponse(BaseModel):
    """Response model for B/C analysis."""
    method: str = "BenefitCost"
    analysis_type: str = Field(..., description="Type of analysis performed")
    marr: float = Field(..., description="MARR used in analysis")
    optimal_project: Optional[Dict[str, Any]] = Field(
        None, description="Optimal project (for mutually exclusive)")
    viable_projects: Optional[List[Dict[str, Any]]] = Field(
        None, description="Viable projects (for independent)")
    comparisons: Optional[List[Dict[str, Any]]] = Field(
        None, description="Incremental analysis comparisons")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConstraintRequest(BaseModel):
    """Constraint for portfolio optimization."""
    type: str = Field(...,
                      description="Constraint type: 'require', 'exclude', 'dependency', 'at_most_one'")
    projects: List[str] = Field(...,
                                description="Projects involved in constraint",
                                min_length=1)
    description: Optional[str] = Field(
        None, description="Human-readable description")

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid_types = ['require', 'exclude', 'dependency', 'at_most_one']
        if v not in valid_types:
            raise ValueError(f"type must be one of: {', '.join(valid_types)}")
        return v


class PortfolioRequest(BaseModel):
    """Request model for Portfolio Optimization."""
    projects: List[ProjectRequest] = Field(...,
                                           description="Projects to consider",
                                           min_length=1)
    budget: float = Field(..., description="Total budget available", gt=0)
    constraints: Optional[List[ConstraintRequest]] = Field(
        None, description="Portfolio constraints")
    time_limit: int = Field(
        60,
        description="Solver time limit in seconds",
        gt=0,
        le=300)
    sensitivity_analysis: bool = Field(
        False, description="Perform budget sensitivity analysis")


class PortfolioResponse(BaseModel):
    """Response model for Portfolio Optimization."""
    method: str = "Portfolio"
    status: str = Field(..., description="Solver status")
    selected_projects: List[str] = Field(...,
                                         description="Selected project names")
    total_cost: float = Field(...,
                              description="Total cost of selected projects")
    total_benefit: float = Field(..., description="Total annual benefit")
    budget_utilization: float = Field(...,
                                      description="Percentage of budget used")
    objective_value: float = Field(...,
                                   description="Optimization objective value")
    shadow_price_budget: Optional[float] = Field(
        None, description="Marginal value of budget")
    sensitivity_results: Optional[List[Dict[str, Any]]] = Field(
        None, description="Budget sensitivity results")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


# Endpoints

@router.post("/ahp", response_model=AHPResponse,
             status_code=status.HTTP_200_OK)
async def analyze_ahp(request: AHPRequest):
    """
    Perform Analytic Hierarchy Process (AHP) analysis.

    Calculate criterion weights from pairwise comparisons and optionally rank alternatives.
    The consistency ratio (CR) should be < 0.1 for acceptable consistency.

    **Example Request:**
    ```json
    {
      "criteria": ["Cost", "Quality", "Speed"],
      "comparisons": {
        "Cost": {"Quality": 0.5, "Speed": 0.333},
        "Quality": {"Speed": 2.0}
      },
      "alternatives": [
        {
          "name": "Product A",
          "scores": {"Cost": 8.5, "Quality": 7.2, "Speed": 6.0}
        },
        {
          "name": "Product B",
          "scores": {"Cost": 7.0, "Quality": 8.5, "Speed": 8.0}
        }
      ]
    }
    ```
    """
    try:
        logger.info(
            f"Starting AHP analysis with {len(request.criteria)} criteria")

        # Create AHP analyzer
        ahp = AHPAnalyzer(request.criteria)

        # Set comparisons
        for criterion_i, comparisons in request.comparisons.items():
            for criterion_j, value in comparisons.items():
                ahp.set_comparison(criterion_i, criterion_j, value)

        # Calculate weights
        weights = ahp.calculate_weights()
        cr = ahp.calculate_consistency_ratio()

        # Prepare response
        response_data = {
            "consistency_ratio": float(cr),
            "is_consistent": cr < 0.1,
            "weights": {
                name: float(weight) for name,
                weight in zip(
                    request.criteria,
                    weights)}}

        # Rank alternatives if provided
        if request.alternatives:
            alternative_scores = {
                alt.name: alt.scores
                for alt in request.alternatives
            }

            ranked_df = ahp.rank_alternatives(alternative_scores)
            response_data["ranked_alternatives"] = ranked_df.to_dict('records')

        logger.info(
            f"AHP analysis completed. CR: {
                cr:.4f}, Consistent: {
                cr < 0.1}")
        return AHPResponse(**response_data)

    except Exception as e:
        logger.error(f"AHP analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AHP analysis failed: {str(e)}"
        )


@router.post("/linear-scoring",
             response_model=LinearScoringResponse,
             status_code=status.HTTP_200_OK)
async def analyze_linear_scoring(request: LinearScoringRequest):
    """
    Perform Linear Scoring analysis.

    Normalize criterion values and calculate weighted scores for each alternative.
    Optionally perform sensitivity analysis on criterion weights.

    **Example Request:**
    ```json
    {
      "criteria": [
        {"name": "Performance", "weight": 0.35, "direction": "maximize"},
        {"name": "Cost", "weight": 0.25, "direction": "minimize"},
        {"name": "Reliability", "weight": 0.40, "direction": "maximize"}
      ],
      "alternatives": [
        {
          "name": "Product A",
          "scores": {"Performance": 85, "Cost": 7500, "Reliability": 92}
        },
        {
          "name": "Product B",
          "scores": {"Performance": 78, "Cost": 6200, "Reliability": 88}
        }
      ],
      "sensitivity_analysis": true
    }
    ```
    """
    try:
        logger.info(
            f"Starting Linear Scoring analysis with {len(request.alternatives)} alternatives")

        # Validate weights sum to 1
        total_weight = sum(c.weight for c in request.criteria)
        if not np.isclose(total_weight, 1.0, atol=0.01):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Criterion weights must sum to 1.0 (current sum: {
                    total_weight:.4f})")

        # Prepare data
        criteria_names = [c.name for c in request.criteria]
        directions = {
            c.name: CriterionDirection.MAXIMIZE if c.direction == 'maximize'
            else CriterionDirection.MINIMIZE
            for c in request.criteria
        }
        weights = {c.name: c.weight for c in request.criteria}

        # Create DataFrame from alternatives
        import pandas as pd
        data_records = []
        for alt in request.alternatives:
            record = {"name": alt.name}
            record.update(alt.scores)
            data_records.append(record)

        data_df = pd.DataFrame(data_records)

        # Create analyzer and calculate scores
        analyzer = LinearScoringAnalyzer(criteria_names, directions)
        results_df = analyzer.calculate_scores(data_df, weights)

        response_data = {
            "ranked_alternatives": results_df.to_dict('records')
        }

        # Perform sensitivity analysis if requested
        if request.sensitivity_analysis:
            weight_ranges = {
                name: (max(0.0, weight - 0.2), min(1.0, weight + 0.2))
                for name, weight in weights.items()
            }

            sens_results = analyzer.sensitivity_analysis(
                data_df, weights, weight_ranges)
            response_data["sensitivity_results"] = sens_results

        logger.info(
            f"Linear Scoring analysis completed. Top alternative: {
                results_df.iloc[0]['name']}")
        return LinearScoringResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Linear Scoring analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Linear Scoring analysis failed: {str(e)}"
        )


@router.post("/benefit-cost",
             response_model=BenefitCostResponse,
             status_code=status.HTTP_200_OK)
async def analyze_benefit_cost(request: BenefitCostRequest):
    """
    Perform Benefit-to-Cost (B/C) analysis.

    Calculate B/C ratios and perform incremental analysis for mutually exclusive projects
    or identify all viable projects for independent analysis.

    **Example Request:**
    ```json
    {
      "projects": [
        {
          "name": "Project A",
          "cost": 100000,
          "benefit": 25000,
          "life": 10,
          "initial_cost": 100000,
          "annual_om": 3000,
          "salvage": 10000
        },
        {
          "name": "Project B",
          "cost": 150000,
          "benefit": 35000,
          "life": 10,
          "initial_cost": 150000,
          "annual_om": 5000,
          "salvage": 15000
        }
      ],
      "marr": 0.12,
      "analysis_type": "mutually_exclusive"
    }
    ```
    """
    try:
        logger.info(
            f"Starting B/C analysis with {len(request.projects)} projects")

        # Create DataFrame from projects
        import pandas as pd
        data_records = []
        for proj in request.projects:
            record = {
                "name": proj.name,
                "initial_cost": proj.initial_cost or proj.cost,
                "life": proj.life or 10,  # Default to 10 years if not specified
                "annual_benefits": proj.benefit,
                "annual_om": proj.annual_om or 0.0,
                "salvage": proj.salvage or 0.0
            }
            data_records.append(record)

        projects_df = pd.DataFrame(data_records)

        # Create analyzer
        analyzer = BenefitCostAnalyzer()

        # Perform analysis
        if request.analysis_type == "mutually_exclusive":
            results = analyzer.incremental_analysis(projects_df, request.marr)

            response_data = {
                "analysis_type": "mutually_exclusive",
                "marr": request.marr,
                "optimal_project": results.get("optimal_project"),
                "comparisons": results.get("comparisons", [])
            }
        else:
            # Independent analysis
            projects_df['CR'] = projects_df.apply(
                lambda row: analyzer.calculate_capital_recovery(
                    row['initial_cost'],
                    row['salvage'],
                    request.marr,
                    row['life']
                ),
                axis=1
            )

            projects_df['BC_Ratio'] = projects_df.apply(
                lambda row: analyzer.calculate_bc_ratio(
                    row['annual_benefits'],
                    row['CR'],
                    row['annual_om']
                ),
                axis=1
            )

            viable_projects = projects_df[projects_df['BC_Ratio'] >= 1.0].to_dict(
                'records')

            response_data = {
                "analysis_type": "independent",
                "marr": request.marr,
                "viable_projects": viable_projects
            }

        logger.info(
            f"B/C analysis completed. Analysis type: {request.analysis_type}")
        return BenefitCostResponse(**response_data)

    except Exception as e:
        logger.error(f"B/C analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"B/C analysis failed: {str(e)}"
        )


@router.post("/portfolio",
             response_model=PortfolioResponse,
             status_code=status.HTTP_200_OK)
async def optimize_portfolio(request: PortfolioRequest):
    """
    Optimize project portfolio using Integer Linear Programming.

    Select the optimal subset of projects to maximize total benefit while staying within budget
    and satisfying constraints.

    **Example Request:**
    ```json
    {
      "projects": [
        {"name": "AI Research", "cost": 1200000, "benefit": 450000},
        {"name": "Cloud Migration", "cost": 800000, "benefit": 320000},
        {"name": "Mobile App", "cost": 500000, "benefit": 180000}
      ],
      "budget": 2000000,
      "constraints": [
        {
          "type": "require",
          "projects": ["Cloud Migration"],
          "description": "Cloud Migration is mandatory"
        },
        {
          "type": "dependency",
          "projects": ["Cloud Migration", "Mobile App"],
          "description": "Mobile App requires Cloud Migration"
        }
      ],
      "time_limit": 60,
      "sensitivity_analysis": false
    }
    ```
    """
    try:
        logger.info(
            f"Starting Portfolio optimization with {len(request.projects)} projects")

        # Create DataFrame from projects
        import pandas as pd
        data_records = []
        for proj in request.projects:
            record = {
                "name": proj.name,
                "cost": proj.cost,
                "benefit": proj.benefit
            }
            data_records.append(record)

        projects_df = pd.DataFrame(data_records)

        # Convert constraints to dict format
        constraints = None
        if request.constraints:
            constraints = [
                {
                    "type": c.type,
                    "projects": c.projects,
                    "description": c.description
                }
                for c in request.constraints
            ]

        # Create optimizer and optimize
        optimizer = PortfolioOptimizer()
        results = optimizer.optimize(
            projects_df,
            request.budget,
            constraints,
            request.time_limit
        )

        response_data = {
            "status": results["status"],
            "selected_projects": results.get("selected_projects", []),
            "total_cost": results.get("total_cost", 0.0),
            "total_benefit": results.get("total_benefit", 0.0),
            "budget_utilization": results.get("budget_utilization", 0.0),
            "objective_value": results.get("objective_value", 0.0),
            "shadow_price_budget": results.get("shadow_price_budget")
        }

        # Perform sensitivity analysis if requested
        if request.sensitivity_analysis and results["status"] in [
                "Optimal", "Not Solved"]:
            budget_range = (request.budget * 0.5, request.budget * 1.5)
            sens_df = optimizer.sensitivity_budget(
                projects_df,
                request.budget,
                budget_range,
                steps=10,
                constraints=constraints
            )

            response_data["sensitivity_results"] = sens_df.to_dict('records')

        logger.info(
            f"Portfolio optimization completed. Status: {
                results['status']}, Selected: {
                len(
                    results.get(
                        'selected_projects',
                        []))}")
        return PortfolioResponse(**response_data)

    except Exception as e:
        logger.error(f"Portfolio optimization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio optimization failed: {str(e)}"
        )


@router.get("/methods", status_code=status.HTTP_200_OK)
async def get_available_methods():
    """
    Get list of available selection methods with descriptions.

    Returns information about all supported project selection methods.
    """
    methods = [{"id": "ahp",
                "name": "Analytic Hierarchy Process (AHP)",
                "description": "Multi-criteria decision analysis using pairwise comparisons",
                "best_for": "Complex decisions with subjective criteria",
                "requires": ["criteria",
                               "pairwise_comparisons"],
                "optional": ["alternatives"]},
               {"id": "linear_scoring",
                "name": "Linear Scoring",
                "description": "Weighted multi-criteria scoring with normalization",
                "best_for": "Quick evaluation with quantifiable criteria",
                "requires": ["criteria",
                             "weights",
                             "alternatives"],
                "optional": ["sensitivity_analysis"]},
               {"id": "benefit_cost",
                "name": "Benefit-to-Cost Analysis",
                "description": "Economic analysis comparing benefits to costs over project life",
                "best_for": "Projects with financial data and long-term benefits",
                "requires": ["projects",
                             "marr",
                             "life"],
                "optional": ["analysis_type"]},
               {"id": "portfolio",
                "name": "Portfolio Optimization",
                "description": "Integer programming to select optimal project subset within budget",
                "best_for": "Selecting multiple projects under budget constraints",
                "requires": ["projects",
                             "budget"],
                "optional": ["constraints",
                             "sensitivity_analysis"]}]

    return {
        "methods": methods,
        "total_methods": len(methods)
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for selection API.

    Returns the status of the selection module and available solvers.
    """
    try:
        # Check if PuLP solver is available
        from pulp import LpSolverDefault
        solver = LpSolverDefault

        return {
            "status": "healthy",
            "module": "selection",
            "version": "1.0.0",
            "solver_available": solver is not None,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "module": "selection",
            "version": "1.0.0",
            "solver_available": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
