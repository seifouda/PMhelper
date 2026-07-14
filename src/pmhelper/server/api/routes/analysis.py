"""
Analysis API Routes

REST API endpoints for running CPM, PERT, and RCPS analyses and managing analysis jobs.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging
from datetime import datetime, timezone

from ..models.schemas import (
    AnalysisType, JobStatus,
    CPMAnalysisRequest, PERTAnalysisRequest, RCPSAnalysisRequest,
    AnalysisJobResponse, AnalysisResultResponse, JobListResponse
)
from ...database.connection import get_db_session
from ...database.models import AnalysisJob
from ...services.analysis_service import analysis_service
from ...services.project_service import ProjectService

logger = logging.getLogger(__name__)

router = APIRouter()


async def create_analysis_job(db: AsyncSession,
                              analysis_type: AnalysisType,
                              input_data: dict,
                              project_id: Optional[str] = None) -> AnalysisJob:
    """Create a new analysis job in the database."""
    job = AnalysisJob(
        analysis_type=analysis_type.value,
        input_data=input_data,
        project_id=UUID(project_id) if project_id else None,
        status=JobStatus.PENDING.value
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    return job


async def update_job_status(db: AsyncSession,
                            job_id: str,
                            status: JobStatus,
                            results: Optional[dict] = None,
                            error_message: Optional[str] = None):
    """Update analysis job status and results."""
    try:
        job_uuid = UUID(job_id)

        # Get the job
        from sqlalchemy import select, update
        query = select(AnalysisJob).where(AnalysisJob.job_id == job_uuid)
        result = await db.execute(query)
        job = result.scalar_one_or_none()

        if not job:
            logger.error(f"Job not found for status update: {job_id}")
            return

        # Update job based on status
        update_data = {"status": status.value}

        if status == JobStatus.RUNNING:
            update_data["started_at"] = datetime.now(timezone.utc)
        elif status == JobStatus.COMPLETED:
            update_data["completed_at"] = datetime.now(timezone.utc)
            update_data["results"] = results
            update_data["progress"] = "100%"
        elif status == JobStatus.FAILED:
            update_data["completed_at"] = datetime.now(timezone.utc)
            update_data["error_message"] = error_message

        # Perform update
        update_query = update(AnalysisJob).where(
            AnalysisJob.job_id == job_uuid).values(
            **update_data)
        await db.execute(update_query)
        await db.commit()

    except Exception as e:
        logger.error(f"Error updating job status for {job_id}: {e}")
        await db.rollback()


async def run_analysis_background(job_id: str, analysis_type: AnalysisType):
    """Background task to run analysis and update job status."""
    async with get_db_session() as db:
        try:
            # Mark job as running
            await update_job_status(db, job_id, JobStatus.RUNNING)

            # Get job details
            job_uuid = UUID(job_id)
            from sqlalchemy import select
            query = select(AnalysisJob).where(AnalysisJob.job_id == job_uuid)
            result = await db.execute(query)
            job = result.scalar_one_or_none()

            if not job:
                logger.error(f"Job not found for analysis: {job_id}")
                return

            # Run the appropriate analysis
            input_data = job.input_data

            if analysis_type == AnalysisType.CPM:
                from ..models.schemas import CPMActivity
                activities = [CPMActivity(**activity)
                              for activity in input_data["activities"]]
                results = await analysis_service._run_cpm_analysis({
                    "activities": input_data["activities"],
                    "options": input_data.get("options", {})
                })

            elif analysis_type == AnalysisType.PERT:
                from ..models.schemas import PERTActivity
                activities = [PERTActivity(**activity)
                              for activity in input_data["activities"]]
                results = await analysis_service._run_pert_analysis({
                    "activities": input_data["activities"],
                    "target_duration": input_data.get("target_duration"),
                    "confidence_level": input_data.get("confidence_level", 0.95),
                    "options": input_data.get("options", {})
                })

            elif analysis_type == AnalysisType.RCPS:
                from ..models.schemas import RCPSActivity
                activities = [RCPSActivity(**activity)
                              for activity in input_data["activities"]]
                results = await analysis_service._run_rcps_analysis({
                    "activities": input_data["activities"],
                    "resource_limits": input_data["resource_limits"],
                    "options": input_data.get("options", {})
                })

            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")

            # Mark job as completed with results
            await update_job_status(db, job_id, JobStatus.COMPLETED, results=results)

        except Exception as e:
            logger.error(f"Analysis failed for job {job_id}: {e}")
            await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))


@router.post(
    "/analyze/cpm",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit CPM analysis",
    description="Submit a Critical Path Method analysis job."
)
async def analyze_cpm(
    request: CPMAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Submit a CPM analysis job."""
    try:
        # Validate project exists if provided
        if request.project_id:
            project = await ProjectService.get_project(db, request.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project {request.project_id} not found"
                )

        # Create job in database
        input_data = {
            "activities": [activity.dict() for activity in request.activities],
            "options": request.options or {}
        }

        job = await create_analysis_job(
            db, AnalysisType.CPM, input_data, request.project_id
        )

        # Add background task
        background_tasks.add_task(
            run_analysis_background,
            str(job.job_id),
            AnalysisType.CPM
        )

        return AnalysisJobResponse(
            job_id=str(job.job_id),
            project_id=str(job.project_id) if job.project_id else None,
            analysis_type=AnalysisType.CPM,
            status=JobStatus.PENDING,
            progress=None,
            created_at=job.created_at,
            started_at=None,
            completed_at=None,
            error_message=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting CPM analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit CPM analysis: {str(e)}"
        )


@router.post(
    "/analyze/pert",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit PERT analysis",
    description="Submit a Program Evaluation and Review Technique analysis job."
)
async def analyze_pert(
    request: PERTAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Submit a PERT analysis job."""
    try:
        # Validate project exists if provided
        if request.project_id:
            project = await ProjectService.get_project(db, request.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project {request.project_id} not found"
                )

        # Create job in database
        input_data = {
            "activities": [activity.dict() for activity in request.activities],
            "target_duration": request.target_duration,
            "confidence_level": request.confidence_level,
            "options": request.options or {}
        }

        job = await create_analysis_job(
            db, AnalysisType.PERT, input_data, request.project_id
        )

        # Add background task
        background_tasks.add_task(
            run_analysis_background,
            str(job.job_id),
            AnalysisType.PERT
        )

        return AnalysisJobResponse(
            job_id=str(job.job_id),
            project_id=str(job.project_id) if job.project_id else None,
            analysis_type=AnalysisType.PERT,
            status=JobStatus.PENDING,
            progress=None,
            created_at=job.created_at,
            started_at=None,
            completed_at=None,
            error_message=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting PERT analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit PERT analysis: {str(e)}"
        )


@router.post(
    "/analyze/rcps",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit RCPS analysis",
    description="Submit a Resource-Constrained Project Scheduling analysis job."
)
async def analyze_rcps(
    request: RCPSAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """Submit an RCPS analysis job."""
    try:
        # Validate project exists if provided
        if request.project_id:
            project = await ProjectService.get_project(db, request.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project {request.project_id} not found"
                )

        # Create job in database
        input_data = {
            "activities": [activity.dict() for activity in request.activities],
            "resource_limits": request.resource_limits,
            "options": request.options or {}
        }

        job = await create_analysis_job(
            db, AnalysisType.RCPS, input_data, request.project_id
        )

        # Add background task
        background_tasks.add_task(
            run_analysis_background,
            str(job.job_id),
            AnalysisType.RCPS
        )

        return AnalysisJobResponse(
            job_id=str(job.job_id),
            project_id=str(job.project_id) if job.project_id else None,
            analysis_type=AnalysisType.RCPS,
            status=JobStatus.PENDING,
            progress=None,
            created_at=job.created_at,
            started_at=None,
            completed_at=None,
            error_message=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting RCPS analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit RCPS analysis: {str(e)}"
        )


@router.get(
    "/jobs/{job_id}/status",
    response_model=AnalysisJobResponse,
    summary="Get job status",
    description="Get the current status of an analysis job."
)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get analysis job status."""
    try:
        job_uuid = UUID(job_id)

        from sqlalchemy import select
        query = select(AnalysisJob).where(AnalysisJob.job_id == job_uuid)
        result = await db.execute(query)
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        return AnalysisJobResponse(
            job_id=str(job.job_id),
            project_id=str(job.project_id) if job.project_id else None,
            analysis_type=AnalysisType(job.analysis_type),
            status=JobStatus(job.status),
            progress=job.progress,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job ID format: {job_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job status for {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job status: {str(e)}"
        )


@router.get(
    "/jobs/{job_id}/results",
    response_model=AnalysisResultResponse,
    summary="Get job results",
    description="Get the results of a completed analysis job."
)
async def get_job_results(
    job_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get analysis job results."""
    try:
        job_uuid = UUID(job_id)

        from sqlalchemy import select
        query = select(AnalysisJob).where(AnalysisJob.job_id == job_uuid)
        result = await db.execute(query)
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        if job.status != JobStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Job {job_id} is not completed (status: {job.status})"
            )

        return AnalysisResultResponse(
            job_id=str(job.job_id),
            project_id=str(job.project_id) if job.project_id else None,
            analysis_type=AnalysisType(job.analysis_type),
            status=JobStatus(job.status),
            results=job.results,
            duration_seconds=job.duration_seconds,
            created_at=job.created_at,
            completed_at=job.completed_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job ID format: {job_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job results for {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job results: {str(e)}"
        )


@router.get(
    "/jobs",
    response_model=JobListResponse,
    summary="List analysis jobs",
    description="List analysis jobs with optional filtering."
)
async def list_jobs(
        page: int = Query(
            1,
            ge=1,
            description="Page number"),
    page_size: int = Query(
            50,
            ge=1,
            le=100,
            description="Number of items per page"),
        status: Optional[JobStatus] = Query(
            None,
            description="Filter by job status"),
        analysis_type: Optional[AnalysisType] = Query(
            None,
            description="Filter by analysis type"),
        project_id: Optional[str] = Query(
            None,
            description="Filter by project ID"),
        db: AsyncSession = Depends(get_db_session)):
    """List analysis jobs with filtering and pagination."""
    try:
        from sqlalchemy import select, func, and_

        # Build base queries
        query = select(AnalysisJob)
        count_query = select(func.count(AnalysisJob.job_id))

        # Apply filters
        filters = []
        if status:
            filters.append(AnalysisJob.status == status.value)
        if analysis_type:
            filters.append(AnalysisJob.analysis_type == analysis_type.value)
        if project_id:
            try:
                project_uuid = UUID(project_id)
                filters.append(AnalysisJob.project_id == project_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid project ID format: {project_id}"
                )

        if filters:
            filter_condition = and_(*filters)
            query = query.where(filter_condition)
            count_query = count_query.where(filter_condition)

        # Add pagination and ordering
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size).order_by(
            AnalysisJob.created_at.desc())

        # Execute queries
        jobs_result = await db.execute(query)
        count_result = await db.execute(count_query)

        jobs = jobs_result.scalars().all()
        total_count = count_result.scalar()

        # Convert to response format
        job_responses = [
            AnalysisJobResponse(
                job_id=str(job.job_id),
                project_id=str(job.project_id) if job.project_id else None,
                analysis_type=AnalysisType(job.analysis_type),
                status=JobStatus(job.status),
                progress=job.progress,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                error_message=job.error_message
            )
            for job in jobs
        ]

        return JobListResponse(
            jobs=job_responses,
            total=total_count,
            page=page,
            page_size=page_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )


__all__ = ["router"]
