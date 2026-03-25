"""
Project Service

Service layer for project CRUD operations, managing projects
and their data in the PMHelper server database.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
import logging

from ..database.models import Project, AnalysisJob
from ..api.models.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from ..database.connection import get_db_session

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for managing project data operations."""
    
    @staticmethod
    async def create_project(db: AsyncSession, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        try:
            # Prepare project data
            project_dict = {
                "name": project_data.name,
                "description": project_data.description,
                "data": {
                    "activities": project_data.activities,
                    "created_via": "api"
                },
                "project_metadata": project_data.metadata or {}
            }
            
            # Create project instance
            db_project = Project(**project_dict)
            
            # Add to database
            db.add(db_project)
            await db.commit()
            await db.refresh(db_project)
            
            logger.info(f"Created project: {db_project.id} - {db_project.name}")
            return db_project
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def get_project(db: AsyncSession, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        try:
            # Convert string to UUID
            project_uuid = UUID(project_id)
            
            # Query with analysis jobs
            query = select(Project).options(
                selectinload(Project.analysis_jobs)
            ).where(Project.id == project_uuid)
            
            result = await db.execute(query)
            project = result.scalar_one_or_none()
            
            if project:
                logger.debug(f"Retrieved project: {project.id} - {project.name}")
            else:
                logger.warning(f"Project not found: {project_id}")
            
            return project
            
        except ValueError as e:
            logger.error(f"Invalid project ID format: {project_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving project {project_id}: {e}")
            raise
    
    @staticmethod
    async def get_projects(db: AsyncSession, 
                          skip: int = 0, 
                          limit: int = 50,
                          search: Optional[str] = None) -> tuple[List[Project], int]:
        """Get a list of projects with pagination and optional search."""
        try:
            # Base query
            query = select(Project)
            count_query = select(func.count(Project.id))
            
            # Add search filter if provided
            if search:
                search_filter = Project.name.ilike(f"%{search}%")
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
            
            # Add pagination
            query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
            
            # Execute queries
            projects_result = await db.execute(query)
            count_result = await db.execute(count_query)
            
            projects = projects_result.scalars().all()
            total_count = count_result.scalar()
            
            logger.debug(f"Retrieved {len(projects)} projects (total: {total_count})")
            return projects, total_count
            
        except Exception as e:
            logger.error(f"Error retrieving projects: {e}")
            raise
    
    @staticmethod
    async def update_project(db: AsyncSession, 
                           project_id: str, 
                           project_data: ProjectUpdate) -> Optional[Project]:
        """Update a project."""
        try:
            # Convert string to UUID
            project_uuid = UUID(project_id)
            
            # Get existing project
            existing_project = await ProjectService.get_project(db, project_id)
            if not existing_project:
                return None
            
            # Prepare update data (only non-None fields)
            update_data = {}
            if project_data.name is not None:
                update_data["name"] = project_data.name
            if project_data.description is not None:
                update_data["description"] = project_data.description
            if project_data.activities is not None:
                # Update the data field
                new_data = existing_project.data.copy() if existing_project.data else {}
                new_data["activities"] = project_data.activities
                update_data["data"] = new_data
            if project_data.metadata is not None:
                update_data["project_metadata"] = project_data.metadata
            
            # Perform update if there are changes
            if update_data:
                query = update(Project).where(Project.id == project_uuid).values(**update_data)
                await db.execute(query)
                await db.commit()
                
                # Refresh and return updated project
                updated_project = await ProjectService.get_project(db, project_id)
                logger.info(f"Updated project: {project_id}")
                return updated_project
            else:
                logger.debug(f"No changes to update for project: {project_id}")
                return existing_project
                
        except ValueError as e:
            logger.error(f"Invalid project ID format: {project_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def delete_project(db: AsyncSession, project_id: str) -> bool:
        """Delete a project and all associated analysis jobs."""
        try:
            # Convert string to UUID
            project_uuid = UUID(project_id)
            
            # Check if project exists
            existing_project = await ProjectService.get_project(db, project_id)
            if not existing_project:
                logger.warning(f"Project not found for deletion: {project_id}")
                return False
            
            # Delete project (cascade will handle analysis_jobs)
            query = delete(Project).where(Project.id == project_uuid)
            result = await db.execute(query)
            await db.commit()
            
            deleted_count = result.rowcount
            if deleted_count > 0:
                logger.info(f"Deleted project: {project_id}")
                return True
            else:
                logger.warning(f"No project deleted for ID: {project_id}")
                return False
                
        except ValueError as e:
            logger.error(f"Invalid project ID format: {project_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def get_project_activities(db: AsyncSession, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get activities data for a specific project."""
        try:
            project = await ProjectService.get_project(db, project_id)
            if not project or not project.data:
                return None
            
            activities = project.data.get("activities", [])
            logger.debug(f"Retrieved {len(activities)} activities for project {project_id}")
            return activities
            
        except Exception as e:
            logger.error(f"Error retrieving activities for project {project_id}: {e}")
            raise
    
    @staticmethod
    async def add_analysis_job_to_project(db: AsyncSession, 
                                        project_id: str, 
                                        job_id: str) -> bool:
        """Associate an analysis job with a project."""
        try:
            # Verify project exists
            project = await ProjectService.get_project(db, project_id)
            if not project:
                logger.error(f"Project not found for job association: {project_id}")
                return False
            
            # The association is handled by the AnalysisJob model's project_id field
            # This method is for future use if additional logic is needed
            logger.debug(f"Analysis job {job_id} associated with project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error associating job {job_id} with project {project_id}: {e}")
            raise
    
    @staticmethod
    async def get_project_analysis_jobs(db: AsyncSession, project_id: str) -> List[AnalysisJob]:
        """Get all analysis jobs for a specific project."""
        try:
            # Convert string to UUID
            project_uuid = UUID(project_id)
            
            # Query analysis jobs for the project
            query = select(AnalysisJob).where(AnalysisJob.project_id == project_uuid)
            result = await db.execute(query)
            jobs = result.scalars().all()
            
            logger.debug(f"Retrieved {len(jobs)} analysis jobs for project {project_id}")
            return jobs
            
        except ValueError as e:
            logger.error(f"Invalid project ID format: {project_id}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving analysis jobs for project {project_id}: {e}")
            raise
    
    @staticmethod
    def validate_activities_data(activities: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """Validate activities data structure."""
        errors = []
        
        if not activities:
            errors.append("Activities list cannot be empty")
            return False, errors
        
        # Check for required fields in each activity
        required_fields = ['id', 'name', 'duration']
        activity_ids = set()
        
        for i, activity in enumerate(activities):
            # Check required fields
            for field in required_fields:
                if field not in activity:
                    errors.append(f"Activity {i}: Missing required field '{field}'")
            
            # Check for duplicate IDs
            activity_id = activity.get('id')
            if activity_id:
                if activity_id in activity_ids:
                    errors.append(f"Duplicate activity ID: {activity_id}")
                activity_ids.add(activity_id)
            
            # Validate duration
            try:
                duration = float(activity.get('duration', 0))
                if duration <= 0:
                    errors.append(f"Activity {activity_id}: Duration must be positive")
            except (ValueError, TypeError):
                errors.append(f"Activity {activity_id}: Invalid duration value")
            
            # Validate predecessors
            predecessors = activity.get('predecessors', [])
            if predecessors:
                for pred_id in predecessors:
                    if pred_id == activity_id:
                        errors.append(f"Activity {activity_id}: Cannot be its own predecessor")
        
        # Check for predecessor references
        for activity in activities:
            activity_id = activity.get('id')
            predecessors = activity.get('predecessors', [])
            for pred_id in predecessors:
                if pred_id not in activity_ids:
                    errors.append(f"Activity {activity_id}: References non-existent predecessor '{pred_id}'")
        
        return len(errors) == 0, errors


# Convenience functions
async def create_project(project_data: ProjectCreate) -> Project:
    """Create a project using dependency injection."""
    async with get_db_session() as db:
        return await ProjectService.create_project(db, project_data)


async def get_project(project_id: str) -> Optional[Project]:
    """Get a project using dependency injection."""
    async with get_db_session() as db:
        return await ProjectService.get_project(db, project_id)


__all__ = ["ProjectService", "create_project", "get_project"]