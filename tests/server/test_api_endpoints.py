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

# Import the FastAPI app
try:
    from pmhelper.server.api.main import app
    from pmhelper.server.config import config
    from pmhelper.server.database.connection import init_database, close_database
    SERVER_AVAILABLE = True
except ImportError as e:
    SERVER_AVAILABLE = False
    pytest.skip(f"Server components not available: {e}", allow_module_level=True)


@pytest.fixture
async def client():
    """Create test client with temporary database."""
    if not SERVER_AVAILABLE:
        pytest.skip("Server components not available")
    
    # Create temporary database for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        config.DATABASE_DIR = Path(temp_dir)
        config.DATABASE_URL = f"sqlite+aiosqlite:///{config.DATABASE_DIR / config.DATABASE_FILE}"
        
        # Initialize test database
        await init_database()
        
        # Create test client
        client = TestClient(app)
        
        try:
            yield client
        finally:
            # Cleanup
            await close_database()


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
        
        response = client.post("/api/analyze/cmp", json=invalid_data)
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
    
    def test_job_results_not_ready(self, client, sample_cpm_activities):
        """Test getting results for incomplete job."""
        # Submit analysis
        analysis_data = {"activities": sample_cpm_activities}
        response = client.post("/api/analyze/cpm", json=analysis_data)
        job_id = response.json()["job_id"]
        
        # Try to get results immediately (should not be ready)
        response = client.get(f"/api/jobs/{job_id}/results")
        # Should return conflict status since job is not completed
        assert response.status_code == 409


if __name__ == "__main__":
    pytest.main([__file__, "-v"])