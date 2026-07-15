"""
Test API Endpoints

Integration tests for PMHelper REST API endpoints including
projects, analysis, and job management.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import tempfile
import os
from pathlib import Path

# Imported at module scope on purpose. This used to sit in a try/except
# ImportError + module-level pytest.skip, which silently disabled the whole
# file for months while it imported names the server no longer had.
from pmhelper.server.main import app
from pmhelper.server.config import config
from pmhelper.server.database.connection import (
    db_manager, init_database, close_database,
)


@pytest.fixture
async def client():
    """Create a test client backed by a throwaway database."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"

        # Config has no DATABASE_URL attribute; the engine reads
        # get_database_url(), which returns _database_url when set.
        original_url = config._database_url
        config._database_url = f"sqlite+aiosqlite:///{db_path}"

        # db_manager is a module-level singleton guarded by _initialized, so
        # without closing first it would keep an engine from an earlier test.
        await close_database()
        await init_database()

        try:
            yield TestClient(app)
        finally:
            await close_database()
            config._database_url = original_url
            db_manager._initialized = False


@pytest.fixture
def sample_cpm_activities():
    """Sample CPM activities for testing."""
    return [
        {
            "id": "A",
            "name": "Activity A",
            "duration": 5,
            "predecessors": [],
            "resource": "Team1",
            "cost": 100
        },
        {
            "id": "B", 
            "name": "Activity B",
            "duration": 3,
            "predecessors": ["A"],
            "resource": "Team2",
            "cost": 50
        },
        {
            "id": "C",
            "name": "Activity C", 
            "duration": 4,
            "predecessors": ["A"],
            "resource": "Team1",
            "cost": 75
        }
    ]


@pytest.fixture
def sample_pert_activities():
    """Sample PERT activities for testing."""
    return [
        {
            "id": "A",
            "name": "Activity A",
            "duration": 5,
            "predecessors": [],
            "optimistic_duration": 3,
            "most_likely_duration": 5,
            "pessimistic_duration": 7
        },
        {
            "id": "B",
            "name": "Activity B", 
            "duration": 4,
            "predecessors": ["A"],
            "optimistic_duration": 2,
            "most_likely_duration": 4,
            "pessimistic_duration": 6
        }
    ]


class TestHealthEndpoints:
    """Test health and basic endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "PMHelper API" in data["message"]
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "server" in data
        assert "version" in data
    
    def test_api_version_endpoint(self, client):
        """Test API version endpoint."""
        response = client.get("/api/version")
        assert response.status_code == 200
        data = response.json()
        assert "api_version" in data
        assert "supported_analyses" in data
        assert "cpm" in data["supported_analyses"]
        assert "pert" in data["supported_analyses"]
        assert "rcps" in data["supported_analyses"]


class TestProjectEndpoints:
    """Test project management endpoints."""
    
    def test_create_project(self, client, sample_cpm_activities):
        """Test project creation."""
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "activities": sample_cpm_activities,
            "metadata": {"created_by": "test"}
        }
        
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"
        assert "id" in data
        assert len(data["data"]["activities"]) == 3
    
    def test_get_projects(self, client):
        """Test listing projects."""
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["projects"], list)
    
    def test_get_project_not_found(self, client):
        """Test getting non-existent project."""
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        response = client.get(f"/api/projects/{fake_uuid}")
        assert response.status_code == 404
    
    def test_invalid_project_data(self, client):
        """Test creating project with invalid data."""
        invalid_data = {
            "name": "",  # Empty name should fail
            "activities": []  # Empty activities should fail
        }
        
        response = client.post("/api/projects", json=invalid_data)
        assert response.status_code == 422


class TestAnalysisEndpoints:
    """Test analysis endpoints."""
    
    def test_cpm_analysis_submission(self, client, sample_cpm_activities):
        """Test CPM analysis submission."""
        analysis_data = {
            "activities": sample_cpm_activities
        }
        
        response = client.post("/api/analyze/cpm", json=analysis_data)
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["analysis_type"] == "cpm"
        assert data["status"] == "pending"
    
    def test_pert_analysis_submission(self, client, sample_pert_activities):
        """Test PERT analysis submission."""
        analysis_data = {
            "activities": sample_pert_activities,
            "target_duration": 10,
            "confidence_level": 0.95
        }
        
        response = client.post("/api/analyze/pert", json=analysis_data)
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["analysis_type"] == "pert"
        assert data["status"] == "pending"
    
    def test_rcps_analysis_submission(self, client):
        """Test RCPS analysis submission."""
        rcps_activities = [
            {
                "id": "A",
                "name": "Activity A",
                "duration": 5,
                "predecessors": [],
                "resource": "Developer",
                "resource_quantity": 2
            }
        ]
        
        analysis_data = {
            "activities": rcps_activities,
            "resource_limits": {"Developer": 3}
        }
        
        response = client.post("/api/analyze/rcps", json=analysis_data)
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["analysis_type"] == "rcps"
        assert data["status"] == "pending"
    
    def test_get_jobs_list(self, client):
        """Test getting jobs list."""
        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert isinstance(data["jobs"], list)
    
    def test_invalid_analysis_data(self, client):
        """Test analysis with invalid data."""
        invalid_data = {
            "activities": []  # Empty activities should fail
        }
        
        # NB: this used to POST to "/api/analyze/cmp" (typo), so it asserted
        # validation behaviour while only ever exercising a 404.
        response = client.post("/api/analyze/cpm", json=invalid_data)
        # Should fail validation
        assert response.status_code in [400, 422]


class TestJobManagement:
    """Test analysis job management."""
    
    def test_job_lifecycle(self, client, sample_cpm_activities):
        """Test complete job lifecycle."""
        # Submit analysis
        analysis_data = {"activities": sample_cpm_activities}
        response = client.post("/api/analyze/cpm", json=analysis_data)
        assert response.status_code == 202
        job_data = response.json()
        job_id = job_data["job_id"]
        
        # Check job status
        response = client.get(f"/api/jobs/{job_id}/status")
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["job_id"] == job_id
        assert status_data["status"] in ["pending", "running", "completed"]
        
        # Note: In real tests, you might need to wait for job completion
        # or mock the analysis service
    
    def test_job_not_found(self, client):
        """Test getting non-existent job."""
        fake_uuid = "12345678-1234-5678-9012-123456789012"
        response = client.get(f"/api/jobs/{fake_uuid}/status")
        assert response.status_code == 404
    
    def test_job_results_not_ready(self, client):
        """Fetching results for a job that hasn't completed returns 409.

        This used to POST an analysis and immediately GET its results,
        assuming the job would still be running. FastAPI's BackgroundTasks
        run synchronously under TestClient, so the job was always already
        COMPLETED and the endpoint correctly returned 200 -- the test could
        never exercise the 409 path. Insert a pending job directly instead.
        """
        import asyncio
        from pmhelper.server.database.connection import db_manager
        from pmhelper.server.database.models import AnalysisJob

        async def _insert_pending_job():
            async with db_manager.get_session() as session:
                job = AnalysisJob(analysis_type="cpm", status="pending",
                                  input_data={"activities": []})
                session.add(job)
                await session.flush()
                return str(job.job_id)

        job_id = asyncio.get_event_loop().run_until_complete(
            _insert_pending_job())

        response = client.get(f"/api/jobs/{job_id}/results")
        assert response.status_code == 409
        assert "not completed" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])