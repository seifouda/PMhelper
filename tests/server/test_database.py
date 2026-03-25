"""
Test Database Operations

Unit tests for database models, connections, and CRUD operations
for the PMHelper server.
"""

import pytest
import asyncio
from datetime import datetime
import tempfile
import uuid
import json
from pathlib import Path

# Import database components
try:
    from pmhelper.server.database.models import Base, Project, AnalysisJobModel
    from pmhelper.server.database.connection import (
        init_database, close_database, get_session, engine
    )
    from pmhelper.server.config import config
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    DATABASE_AVAILABLE = True
except ImportError as e:
    DATABASE_AVAILABLE = False
    pytest.skip(f"Database components not available: {e}", allow_module_level=True)


@pytest.fixture
async def db_session():
    """Create test database session."""
    if not DATABASE_AVAILABLE:
        pytest.skip("Database components not available")
    
    # Create temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        config.DATABASE_DIR = Path(temp_dir)
        config.DATABASE_URL = f"sqlite+aiosqlite:///{config.DATABASE_DIR / config.DATABASE_FILE}"
        
        await init_database()
        
        async with get_session() as session:
            yield session
        
        await close_database()


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project for unit testing",
        "data": {
            "activities": [
                {
                    "id": "A",
                    "name": "Activity A",
                    "duration": 5,
                    "predecessors": [],
                    "resource": "Team1"
                },
                {
                    "id": "B", 
                    "name": "Activity B",
                    "duration": 3,
                    "predecessors": ["A"],
                    "resource": "Team2"
                }
            ]
        },
        "metadata": {
            "created_by": "test_user",
            "project_type": "cpm"
        }
    }


@pytest.fixture
def sample_analysis_job_data():
    """Sample analysis job data for testing."""
    return {
        "analysis_type": "cpm",
        "status": "pending",
        "input_data": {
            "activities": [
                {
                    "id": "A",
                    "name": "Activity A",
                    "duration": 5,
                    "predecessors": []
                }
            ]
        },
        "metadata": {
            "submitted_by": "test_user"
        }
    }


class TestDatabaseConnection:
    """Test database connection and initialization."""
    
    @pytest.mark.asyncio
    async def test_database_initialization(self):
        """Test database initialization."""
        if not DATABASE_AVAILABLE:
            pytest.skip("Database components not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config.DATABASE_DIR = Path(temp_dir) 
            config.DATABASE_URL = f"sqlite+aiosqlite:///{config.DATABASE_DIR / config.DATABASE_FILE}"
            
            # Initialize database
            await init_database()
            
            # Check that database file was created
            db_file = config.DATABASE_DIR / config.DATABASE_FILE
            assert db_file.exists()
            
            # Check that tables were created by trying to connect
            async with get_session() as session:
                # Simple query to verify connection
                result = await session.execute(select(1))
                assert result.scalar() == 1
            
            await close_database()
    
    @pytest.mark.asyncio
    async def test_session_context_manager(self, db_session):
        """Test database session context manager."""
        assert isinstance(db_session, AsyncSession)
        
        # Test simple query
        result = await db_session.execute(select(1))
        assert result.scalar() == 1


class TestProjectModel:
    """Test Project model CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_project(self, db_session, sample_project_data):
        """Test creating a project."""
        project = Project(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
            data=sample_project_data["data"],
            metadata=sample_project_data["metadata"]
        )
        
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        assert project.id is not None
        assert isinstance(project.id, uuid.UUID)
        assert project.name == sample_project_data["name"]
        assert project.description == sample_project_data["description"]
        assert project.data == sample_project_data["data"]
        assert project.metadata == sample_project_data["metadata"]
        assert project.created_at is not None
        assert project.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_read_project(self, db_session, sample_project_data):
        """Test reading a project."""
        # Create project
        project = Project(**sample_project_data)
        db_session.add(project)
        await db_session.commit()
        project_id = project.id
        
        # Read project
        stmt = select(Project).where(Project.id == project_id)
        result = await db_session.execute(stmt)
        retrieved_project = result.scalar_one()
        
        assert retrieved_project.id == project_id
        assert retrieved_project.name == sample_project_data["name"]
        assert retrieved_project.data == sample_project_data["data"]
    
    @pytest.mark.asyncio
    async def test_update_project(self, db_session, sample_project_data):
        """Test updating a project."""
        # Create project
        project = Project(**sample_project_data)
        db_session.add(project)
        await db_session.commit()
        
        # Update project
        original_updated_at = project.updated_at
        await asyncio.sleep(0.01)  # Ensure timestamp changes
        
        project.name = "Updated Project Name"
        project.description = "Updated description"
        await db_session.commit()
        await db_session.refresh(project)
        
        assert project.name == "Updated Project Name"
        assert project.description == "Updated description"
        assert project.updated_at > original_updated_at
    
    @pytest.mark.asyncio
    async def test_delete_project(self, db_session, sample_project_data):
        """Test deleting a project."""
        # Create project
        project = Project(**sample_project_data)
        db_session.add(project)
        await db_session.commit()
        project_id = project.id
        
        # Delete project
        await db_session.delete(project)
        await db_session.commit()
        
        # Verify deletion
        stmt = select(Project).where(Project.id == project_id)
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None
    
    @pytest.mark.asyncio
    async def test_project_json_serialization(self, db_session, sample_project_data):
        """Test project JSON serialization."""
        project = Project(**sample_project_data)
        db_session.add(project)
        await db_session.commit()
        
        # Test data field (JSON)
        assert isinstance(project.data, dict)
        assert "activities" in project.data
        
        # Test metadata field (JSON)
        assert isinstance(project.metadata, dict)
        assert "created_by" in project.metadata
    
    @pytest.mark.asyncio
    async def test_list_projects_pagination(self, db_session):
        """Test listing projects with pagination."""
        # Create multiple projects
        projects = []
        for i in range(5):
            project = Project(
                name=f"Project {i}",
                description=f"Description {i}",
                data={"activities": []},
                metadata={"index": i}
            )
            projects.append(project)
            db_session.add(project)
        
        await db_session.commit()
        
        # Test pagination
        stmt = select(Project).limit(3).offset(0)
        result = await db_session.execute(stmt)
        page_1 = result.scalars().all()
        assert len(page_1) == 3
        
        stmt = select(Project).limit(3).offset(3)
        result = await db_session.execute(stmt)
        page_2 = result.scalars().all()
        assert len(page_2) == 2


class TestAnalysisJobModel:
    """Test AnalysisJobModel CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_analysis_job(self, db_session, sample_analysis_job_data):
        """Test creating an analysis job."""
        job = AnalysisJobModel(
            analysis_type=sample_analysis_job_data["analysis_type"],
            status=sample_analysis_job_data["status"],
            input_data=sample_analysis_job_data["input_data"],
            metadata=sample_analysis_job_data["metadata"]
        )
        
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        assert job.id is not None
        assert isinstance(job.id, uuid.UUID)
        assert job.analysis_type == "cpm"
        assert job.status == "pending"
        assert job.input_data == sample_analysis_job_data["input_data"]
        assert job.metadata == sample_analysis_job_data["metadata"]
        assert job.submitted_at is not None
        assert job.completed_at is None
        assert job.results is None
        assert job.error_message is None
    
    @pytest.mark.asyncio
    async def test_update_job_status(self, db_session, sample_analysis_job_data):
        """Test updating job status and completion."""
        # Create job
        job = AnalysisJobModel(**sample_analysis_job_data)
        db_session.add(job)
        await db_session.commit()
        
        # Update to running
        job.status = "running"
        await db_session.commit()
        assert job.status == "running"
        
        # Update to completed with results
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.results = {
            "critical_path": ["A"],
            "project_duration": 5
        }
        await db_session.commit()
        await db_session.refresh(job)
        
        assert job.status == "completed"
        assert job.completed_at is not None
        assert job.results is not None
        assert "critical_path" in job.results
    
    @pytest.mark.asyncio
    async def test_job_error_handling(self, db_session, sample_analysis_job_data):
        """Test job error status and messages."""
        job = AnalysisJobModel(**sample_analysis_job_data)
        db_session.add(job)
        await db_session.commit()
        
        # Set error status
        job.status = "failed"
        job.completed_at = datetime.utcnow()
        job.error_message = "Analysis failed due to invalid input"
        await db_session.commit()
        
        assert job.status == "failed"
        assert job.error_message == "Analysis failed due to invalid input"
        assert job.results is None
    
    @pytest.mark.asyncio
    async def test_job_relationships(self, db_session, sample_project_data, sample_analysis_job_data):
        """Test job-project relationships."""
        # Create project
        project = Project(**sample_project_data)
        db_session.add(project)
        await db_session.commit()
        
        # Create job linked to project
        job = AnalysisJobModel(
            project_id=project.id,
            **sample_analysis_job_data
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)
        
        assert job.project_id == project.id
        
        # Test relationship loading
        await db_session.refresh(job, ["project"])
        assert job.project is not None
        assert job.project.name == project.name
    
    @pytest.mark.asyncio
    async def test_list_jobs_by_status(self, db_session):
        """Test filtering jobs by status."""
        # Create jobs with different statuses
        statuses = ["pending", "running", "completed", "failed"]
        jobs = []
        
        for status in statuses:
            job = AnalysisJobModel(
                analysis_type="cpm",
                status=status,
                input_data={"activities": []},
                metadata={}
            )
            jobs.append(job)
            db_session.add(job)
        
        await db_session.commit()
        
        # Query by status
        stmt = select(AnalysisJobModel).where(AnalysisJobModel.status == "pending")
        result = await db_session.execute(stmt)
        pending_jobs = result.scalars().all()
        assert len(pending_jobs) == 1
        assert pending_jobs[0].status == "pending"
        
        # Query completed jobs
        stmt = select(AnalysisJobModel).where(AnalysisJobModel.status.in_(["completed", "failed"]))
        result = await db_session.execute(stmt)
        finished_jobs = result.scalars().all()
        assert len(finished_jobs) == 2


class TestDatabaseConstraints:
    """Test database constraints and validation."""
    
    @pytest.mark.asyncio
    async def test_project_name_required(self, db_session):
        """Test that project name is required."""
        project = Project(
            name=None,  # Should cause constraint error
            description="Test",
            data={},
            metadata={}
        )
        
        db_session.add(project)
        
        with pytest.raises(Exception):  # SQLAlchemy will raise an exception
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_job_analysis_type_required(self, db_session):
        """Test that analysis type is required."""
        job = AnalysisJobModel(
            analysis_type=None,  # Should cause constraint error
            status="pending",
            input_data={},
            metadata={}
        )
        
        db_session.add(job)
        
        with pytest.raises(Exception):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_uuid_uniqueness(self, db_session, sample_project_data):
        """Test UUID uniqueness constraints."""
        # Create first project
        project1 = Project(**sample_project_data)
        db_session.add(project1)
        await db_session.commit()
        
        # Try to create another project with same UUID
        project2 = Project(**sample_project_data)
        project2.id = project1.id  # Force same UUID
        db_session.add(project2)
        
        with pytest.raises(Exception):  # Should fail on unique constraint
            await db_session.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])