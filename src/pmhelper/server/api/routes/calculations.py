"""
API endpoints for calculations.
This is the server layer that uses the core application logic.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any

from ...database.connection import get_db_session
from ....calculations import calculate_pm_value_async

router = APIRouter(prefix="/api/calculations", tags=["calculations"])


class CalculationRequest(BaseModel):
    """API request model."""
    value: float
    parameters: Dict[str, Any] = {}


class CalculationResponse(BaseModel):
    """API response model."""
    result: float
    execution_time_ms: float
    metadata: Dict[str, Any]


@router.post("/calculate", response_model=CalculationResponse)
async def calculate(
    request: CalculationRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Perform a calculation.

    This endpoint is server infrastructure that calls core business logic.
    """
    try:
        result = await calculate_pm_value_async(
            value=request.value,
            parameters=request.parameters
        )

        return CalculationResponse(
            result=result["result"],
            execution_time_ms=result["execution_time_ms"],
            metadata=result["metadata"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """API health check."""
    return {"status": "healthy", "api": "calculations"}
