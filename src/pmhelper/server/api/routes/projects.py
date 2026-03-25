"""
Project API Routes

REST API endpoints for project management operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..models.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectList,
    ErrorResponse, ValidationErrorResponse
)
from ...database.connection import get_db_session
from ...services.project_service import ProjectService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new project with activities and metadata."
)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new project."""
    try:
        # Validate activities data
        is_valid, validation_errors = ProjectService.validate_activities_data(project.activities)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Validation Error",
                    "message": "Invalid activities data",
                    "errors": validation_errors
                }
            )
        
        # Create project
        db_project = await ProjectService.create_project(db, project)
        
        # Convert to response format
        return ProjectResponse(
            id=str(db_project.id),
            name=db_project.name,
            description=db_project.description,
            data=db_project.data,
            metadata=db_project.project_metadata,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to create project",
                "detail": str(e)
            }
        )


@router.get(
    "/projects",
    response_model=ProjectList,
    summary="List projects",
    description="Retrieve a paginated list of projects with optional search."
)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search term for project names"),
    db: AsyncSession = Depends(get_db_session)
):
    """List projects with pagination and search."""
    try:
        skip = (page - 1) * page_size
        projects, total_count = await ProjectService.get_projects(
            db, skip=skip, limit=page_size, search=search
        )
        
        # Convert to response format
        project_responses = [
            ProjectResponse(
                id=str(project.id),
                name=project.name,
                description=project.description,
                data=project.data,
                metadata=project.project_metadata,
                created_at=project.created_at,
                updated_at=project.updated_at
            )
            for project in projects
        ]
        
        return ProjectList(
            projects=project_responses,
            total=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to retrieve projects",
                "detail": str(e)
            }
        )


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project",
    description="Retrieve a specific project by ID."
)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a project by ID."""
    try:
        db_project = await ProjectService.get_project(db, project_id)
        
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Project with ID {project_id} not found"
                }
            )
        
        return ProjectResponse(
            id=str(db_project.id),
            name=db_project.name,
            description=db_project.description,
            data=db_project.data,
            metadata=db_project.project_metadata,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to retrieve project",
                "detail": str(e)
            }
        )


@router.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
    description="Update a project's information, activities, or metadata."
)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update a project."""
    try:
        # Validate activities if provided
        if project_update.activities is not None:
            is_valid, validation_errors = ProjectService.validate_activities_data(project_update.activities)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": "Validation Error",
                        "message": "Invalid activities data",
                        "errors": validation_errors
                    }
                )
        
        # Update project
        updated_project = await ProjectService.update_project(db, project_id, project_update)
        
        if not updated_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Project with ID {project_id} not found"
                }
            )
        
        return ProjectResponse(
            id=str(updated_project.id),
            name=updated_project.name,
            description=updated_project.description,
            data=updated_project.data,
            metadata=updated_project.project_metadata,
            created_at=updated_project.created_at,
            updated_at=updated_project.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to update project",
                "detail": str(e)
            }
        )


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description="Delete a project and all associated analysis jobs."
)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a project."""
    try:
        success = await ProjectService.delete_project(db, project_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Project with ID {project_id} not found"
                }
            )
        
        # Return 204 No Content on successful deletion
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error", 
                "message": "Failed to delete project",
                "detail": str(e)
            }
        )


@router.get(
    "/projects/{project_id}/activities",
    summary="Get project activities",
    description="Retrieve the activities data for a specific project."
)
async def get_project_activities(
    project_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get activities for a specific project."""
    try:
        activities = await ProjectService.get_project_activities(db, project_id)
        
        if activities is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Project with ID {project_id} not found or has no activities"
                }
            )
        
        return {
            "project_id": project_id,
            "activities": activities,
            "count": len(activities)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving activities for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to retrieve project activities",
                "detail": str(e)
            }
        )


@router.get(
    "/projects/{project_id}/analysis-jobs",
    summary="Get project analysis jobs",
    description="Retrieve all analysis jobs associated with a specific project."
)
async def get_project_analysis_jobs(
    project_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get analysis jobs for a specific project."""
    try:
        # First verify project exists
        project = await ProjectService.get_project(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Not Found",
                    "message": f"Project with ID {project_id} not found"
                }
            )
        
        jobs = await ProjectService.get_project_analysis_jobs(db, project_id)
        
        # Convert jobs to response format
        job_responses = []
        for job in jobs:
            job_responses.append({
                "job_id": str(job.job_id),
                "analysis_type": job.analysis_type,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "error_message": job.error_message
            })
        
        return {
            "project_id": project_id,
            "analysis_jobs": job_responses,
            "count": len(job_responses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analysis jobs for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to retrieve project analysis jobs",
                "detail": str(e)
            }
        )


__all__ = ["router"]