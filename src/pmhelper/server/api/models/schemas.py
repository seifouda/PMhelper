"""
Pydantic Schemas for PMHelper API

Request and response models for API endpoints using Pydantic for validation and serialization.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, validator


# Enums for validation
class AnalysisType(str, Enum):
    """Supported analysis types."""
    CPM = "cpm"
    PERT = "pert" 
    RCPS = "rcps"


class JobStatus(str, Enum):
    """Analysis job status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Activity models
class ActivityBase(BaseModel):
    """Base activity model with common fields."""
    id: str = Field(..., description="Unique activity identifier")
    name: str = Field(..., description="Activity name", min_length=1, max_length=200)
    duration: float = Field(..., description="Activity duration", ge=0)
    predecessors: List[str] = Field(default=[], description="List of predecessor activity IDs")


class CPMActivity(ActivityBase):
    """Activity model for CPM analysis."""
    resource: Optional[str] = Field(None, description="Resource assigned to activity")
    cost: Optional[float] = Field(None, description="Activity cost", ge=0)
    crash_duration: Optional[float] = Field(None, description="Minimum duration if crashed", ge=0)
    crash_cost: Optional[float] = Field(None, description="Cost to crash to minimum duration", ge=0)
    
    @validator('crash_duration')
    def crash_duration_valid(cls, v, values):
        if v is not None and 'duration' in values and v > values['duration']:
            raise ValueError('crash_duration must be less than or equal to normal duration')
        return v


class PERTActivity(ActivityBase):
    """Activity model for PERT analysis."""
    optimistic_duration: Optional[float] = Field(None, description="Optimistic duration estimate", ge=0)
    pessimistic_duration: Optional[float] = Field(None, description="Pessimistic duration estimate", ge=0)
    most_likely_duration: Optional[float] = Field(None, description="Most likely duration estimate", ge=0)
    
    @validator('pessimistic_duration')
    def pessimistic_valid(cls, v, values):
        if v is not None and 'optimistic_duration' in values and values['optimistic_duration'] is not None:
            if v < values['optimistic_duration']:
                raise ValueError('pessimistic_duration must be >= optimistic_duration')
        return v


class RCPSActivity(ActivityBase):
    """Activity model for RCPS analysis."""
    resource: str = Field(..., description="Resource type required")
    resource_quantity: float = Field(..., description="Quantity of resource required", ge=0)


# Project models
class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., description="Project name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Project description", max_length=1000)
    activities: List[Dict[str, Any]] = Field(..., description="List of project activities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional project metadata")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, description="Project name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Project description", max_length=1000)
    activities: Optional[List[Dict[str, Any]]] = Field(None, description="List of project activities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional project metadata")


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: str = Field(..., description="Project UUID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    data: Dict[str, Any] = Field(..., description="Project data including activities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Project metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ProjectList(BaseModel):
    """Schema for project list response."""
    projects: List[ProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
    page: int = Field(1, description="Current page number", ge=1)
    page_size: int = Field(50, description="Number of items per page", ge=1, le=100)


# Analysis request models
class CPMAnalysisRequest(BaseModel):
    """Schema for CPM analysis request."""
    activities: List[CPMActivity] = Field(..., description="List of activities for CPM analysis")
    project_id: Optional[str] = Field(None, description="Optional project ID to associate with analysis")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional analysis options")


class PERTAnalysisRequest(BaseModel):
    """Schema for PERT analysis request."""
    activities: List[PERTActivity] = Field(..., description="List of activities for PERT analysis")
    project_id: Optional[str] = Field(None, description="Optional project ID to associate with analysis")
    target_duration: Optional[float] = Field(None, description="Target project duration for probability analysis", gt=0)
    confidence_level: Optional[float] = Field(0.95, description="Confidence level for analysis", ge=0.5, le=0.99)
    options: Optional[Dict[str, Any]] = Field(None, description="Additional analysis options")


class RCPSAnalysisRequest(BaseModel):
    """Schema for RCPS analysis request."""
    activities: List[RCPSActivity] = Field(..., description="List of activities for RCPS analysis")
    resource_limits: Dict[str, float] = Field(..., description="Resource availability limits")
    project_id: Optional[str] = Field(None, description="Optional project ID to associate with analysis")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional analysis options")


# Analysis response models
class AnalysisJobResponse(BaseModel):
    """Schema for analysis job response."""
    job_id: str = Field(..., description="Analysis job UUID")
    project_id: Optional[str] = Field(None, description="Associated project UUID")
    analysis_type: AnalysisType = Field(..., description="Type of analysis")
    status: JobStatus = Field(..., description="Current job status")
    progress: Optional[str] = Field(None, description="Job progress percentage")
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if job failed")


class AnalysisResultResponse(BaseModel):
    """Schema for analysis results response."""
    job_id: str = Field(..., description="Analysis job UUID")
    project_id: Optional[str] = Field(None, description="Associated project UUID")
    analysis_type: AnalysisType = Field(..., description="Type of analysis performed")
    status: JobStatus = Field(..., description="Job status")
    results: Optional[Dict[str, Any]] = Field(None, description="Analysis results")
    duration_seconds: Optional[float] = Field(None, description="Analysis duration in seconds")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")


class JobListResponse(BaseModel):
    """Schema for job list response."""
    jobs: List[AnalysisJobResponse] = Field(..., description="List of analysis jobs")
    total: int = Field(..., description="Total number of jobs")
    page: int = Field(1, description="Current page number", ge=1)
    page_size: int = Field(50, description="Number of items per page", ge=1, le=100)


# Error response models
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    error: str = Field(default="Validation Error", description="Error type")
    message: str = Field(..., description="Error message")
    errors: List[Dict[str, Any]] = Field(..., description="Detailed validation errors")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


# Health check response
class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(..., description="Health status")
    timestamp: float = Field(..., description="Response timestamp")
    server: Dict[str, Any] = Field(..., description="Server information")
    database: str = Field(..., description="Database status")
    version: str = Field(..., description="API version")


__all__ = [
    # Enums
    "AnalysisType", "JobStatus",
    # Activity models
    "ActivityBase", "CPMActivity", "PERTActivity", "RCPSActivity",
    # Project models
    "ProjectCreate", "ProjectUpdate", "ProjectResponse", "ProjectList",
    # Analysis models
    "CPMAnalysisRequest", "PERTAnalysisRequest", "RCPSAnalysisRequest",
    "AnalysisJobResponse", "AnalysisResultResponse", "JobListResponse",
    # Error models
    "ErrorResponse", "ValidationErrorResponse",
    # Health model
    "HealthResponse"
]