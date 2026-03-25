"""
Integration Tests for PMHelper Server

End-to-end integration tests for the complete server functionality
including API endpoints, database operations, and analysis processing.
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from httpx import AsyncClient
import time

# Import server components
try:
    from pmhelper.server.api.main import app
    from pmhelper.server.config import config
    from pmhelper.server.database.connection import init_database, close_database
    from pmhelper.server.services.analysis_service import AnalysisService
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    INTEGRATION_AVAILABLE = False
    pytest.skip(f"Integration components not available: {e}", allow_module_level=True)


@pytest.fixture
async def test_app():
    """Create test application with temporary database."""
    if not INTEGRATION_AVAILABLE:
        pytest.skip("Integration components not available")
    
    # Setup temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        config.DATABASE_DIR = Path(temp_dir)
        config.DATABASE_URL = f"sqlite+aiosqlite:///{config.DATABASE_DIR / config.DATABASE_FILE}"
        
        # Initialize database
        await init_database()
        
        # Create test client
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
        
        # Cleanup
        await close_database()


@pytest.fixture
def complete_project_data():
    """Complete project data for integration testing."""
    return {
        "name": "Integration Test Project",
        "description": "A complete project for testing full workflow",
        "activities": [
            {
                "id": "A",
                "name": "Project Planning",
                "duration": 5,
                "predecessors": [],
                "resource": "Project Manager",
                "cost": 500
            },
            {
                "id": "B", 
                "name": "Requirements Analysis",
                "duration": 8,
                "predecessors": ["A"],
                "resource": "Business Analyst",
                "cost": 800
            },
            {
                "id": "C",
                "name": "System Design",
                "duration": 12,
                "predecessors": ["B"],
                "resource": "System Architect",
                "cost": 1200
            },
            {
                "id": "D",
                "name": "Implementation Phase 1",
                "duration": 15,
                "predecessors": ["C"],
                "resource": "Development Team",
                "cost": 2000
            },
            {
                "id": "E",
                "name": "Implementation Phase 2", 
                "duration": 10,
                "predecessors": ["D"],
                "resource": "Development Team",
                "cost": 1500
            },
            {
                "id": "F",
                "name": "Testing",
                "duration": 7,
                "predecessors": ["E"],
                "resource": "QA Team",
                "cost": 700
            },
            {
                "id": "G",
                "name": "Deployment",
                "duration": 3,
                "predecessors": ["F"],
                "resource": "DevOps Team",
                "cost": 300
            }
        ],
        "metadata": {
            "created_by": "integration_test",
            "project_type": "software_development",
            "budget": 7000
        }
    }


class TestCompleteWorkflow:
    """Test complete project and analysis workflow."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_project_workflow(self, test_app, complete_project_data):
        """Test complete project lifecycle from creation to analysis."""
        
        # 1. Create a new project
        response = await test_app.post("/api/projects", json=complete_project_data)
        assert response.status_code == 201
        project_data = response.json()
        project_id = project_data["id"]
        
        assert project_data["name"] == complete_project_data["name"]
        assert len(project_data["data"]["activities"]) == 7
        
        # 2. Verify project was created
        response = await test_app.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        retrieved_project = response.json()
        assert retrieved_project["id"] == project_id
        
        # 3. Submit CPM analysis for the project
        cpm_data = {
            "activities": complete_project_data["activities"]
        }
        response = await test_app.post("/api/analyze/cpm", json=cpm_data)
        assert response.status_code == 202
        job_data = response.json()
        job_id = job_data["job_id"]
        
        # 4. Monitor job status
        max_attempts = 10
        for attempt in range(max_attempts):
            response = await test_app.get(f"/api/jobs/{job_id}/status")
            assert response.status_code == 200
            status = response.json()
            
            if status["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(0.1)  # Small delay
        
        # Job should eventually complete
        assert status["status"] == "completed"
        
        # 5. Get analysis results
        response = await test_app.get(f"/api/jobs/{job_id}/results")
        assert response.status_code == 200
        results = response.json()
        
        assert "critical_path" in results
        assert "project_duration" in results
        assert isinstance(results["critical_path"], list)
        assert isinstance(results["project_duration"], (int, float))
        
        # 6. List all projects (should include our project)
        response = await test_app.get("/api/projects")
        assert response.status_code == 200
        projects_list = response.json()
        
        project_ids = [p["id"] for p in projects_list["projects"]]
        assert project_id in project_ids
        
        # 7. List all jobs (should include our job)
        response = await test_app.get("/api/jobs")
        assert response.status_code == 200
        jobs_list = response.json()
        
        job_ids = [j["job_id"] for j in jobs_list["jobs"]]
        assert job_id in job_ids
    
    @pytest.mark.asyncio
    async def test_multiple_analysis_types(self, test_app):
        """Test running different analysis types on the same project."""
        
        # Project activities suitable for all analysis types
        activities = [
            {
                "id": "A",
                "name": "Activity A",
                "duration": 5,
                "predecessors": [],
                "resource": "Team1",
                "cost": 100,
                "optimistic_duration": 3,
                "most_likely_duration": 5,
                "pessimistic_duration": 8,
                "resource_quantity": 2
            },
            {
                "id": "B",
                "name": "Activity B",
                "duration": 4,
                "predecessors": ["A"],
                "resource": "Team2",
                "cost": 80,
                "optimistic_duration": 2,
                "most_likely_duration": 4,
                "pessimistic_duration": 7,
                "resource_quantity": 1
            }
        ]
        
        # Create project
        project_data = {
            "name": "Multi-Analysis Project",
            "description": "Project for testing multiple analysis types",
            "activities": activities,
            "metadata": {"test_type": "multi_analysis"}
        }
        
        response = await test_app.post("/api/projects", json=project_data)
        assert response.status_code == 201
        project = response.json()
        
        # Submit CPM analysis
        cpm_response = await test_app.post("/api/analyze/cpm", json={"activities": activities})
        assert cpm_response.status_code == 202
        cpm_job_id = cpm_response.json()["job_id"]
        
        # Submit PERT analysis
        pert_data = {
            "activities": activities,
            "target_duration": 10,
            "confidence_level": 0.95
        }
        pert_response = await test_app.post("/api/analyze/pert", json=pert_data)
        assert pert_response.status_code == 202
        pert_job_id = pert_response.json()["job_id"]
        
        # Submit RCPS analysis
        rcps_data = {
            "activities": activities,
            "resource_limits": {"Team1": 3, "Team2": 2}
        }
        rcps_response = await test_app.post("/api/analyze/rcps", json=rcps_data)
        assert rcps_response.status_code == 202
        rcps_job_id = rcps_response.json()["job_id"]
        
        # Wait for all jobs to complete
        job_ids = [cpm_job_id, pert_job_id, rcps_job_id]
        completed_jobs = {}
        
        max_wait_time = 5.0  # seconds
        start_time = time.time()
        
        while len(completed_jobs) < 3 and (time.time() - start_time) < max_wait_time:
            for job_id in job_ids:
                if job_id not in completed_jobs:
                    response = await test_app.get(f"/api/jobs/{job_id}/status")
                    status = response.json()
                    
                    if status["status"] in ["completed", "failed"]:
                        completed_jobs[job_id] = status
            
            if len(completed_jobs) < 3:
                await asyncio.sleep(0.1)
        
        # Verify all jobs completed successfully
        for job_id, status in completed_jobs.items():
            assert status["status"] == "completed", f"Job {job_id} failed: {status.get('error')}"
        
        # Get results for each analysis type
        for job_id in job_ids:
            response = await test_app.get(f"/api/jobs/{job_id}/results")
            assert response.status_code == 200
            results = response.json()
            assert results is not None
            assert isinstance(results, dict)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_project_creation(self, test_app):
        """Test creating invalid projects."""
        
        # Empty name
        invalid_data = {
            "name": "",
            "description": "Test",
            "activities": [],
            "metadata": {}
        }
        
        response = await test_app.post("/api/projects", json=invalid_data)
        assert response.status_code == 422
        
        # Missing required fields
        response = await test_app.post("/api/projects", json={"name": "Test"})
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_analysis_submission(self, test_app):
        """Test submitting invalid analysis data."""
        
        # Empty activities
        response = await test_app.post("/api/analyze/cmp", json={"activities": []})
        assert response.status_code in [400, 422]
        
        # Invalid analysis type
        response = await test_app.post("/api/analyze/invalid", json={"activities": [{"id": "A"}]})
        assert response.status_code == 404
        
        # Missing required data
        response = await test_app.post("/api/analyze/cmp", json={})
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_nonexistent_resource_access(self, test_app):
        """Test accessing non-existent resources."""
        import uuid
        
        fake_uuid = str(uuid.uuid4())
        
        # Non-existent project
        response = await test_app.get(f"/api/projects/{fake_uuid}")
        assert response.status_code == 404
        
        # Non-existent job
        response = await test_app.get(f"/api/jobs/{fake_uuid}/status")
        assert response.status_code == 404
        
        response = await test_app.get(f"/api/jobs/{fake_uuid}/results")
        assert response.status_code == 404


class TestPerformance:
    """Test performance and concurrency."""
    
    @pytest.mark.asyncio
    async def test_concurrent_project_creation(self, test_app):
        """Test creating multiple projects concurrently."""
        
        async def create_project(index):
            data = {
                "name": f"Concurrent Project {index}",
                "description": f"Project created concurrently - {index}",
                "activities": [
                    {
                        "id": f"A{index}",
                        "name": f"Activity {index}",
                        "duration": index + 1,
                        "predecessors": [],
                        "resource": "Team"
                    }
                ],
                "metadata": {"index": index}
            }
            
            response = await test_app.post("/api/projects", json=data)
            return response.status_code, response.json()
        
        # Create 5 projects concurrently
        tasks = [create_project(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for status_code, project_data in results:
            assert status_code == 201
            assert "id" in project_data
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_submission(self, test_app):
        """Test submitting multiple analyses concurrently."""
        
        activities = [
            {
                "id": "A",
                "name": "Concurrent Activity",
                "duration": 5,
                "predecessors": [],
                "resource": "Team"
            }
        ]
        
        async def submit_analysis(index):
            data = {"activities": activities}
            response = await test_app.post("/api/analyze/cpm", json=data)
            return response.status_code, response.json()
        
        # Submit 3 analyses concurrently
        tasks = [submit_analysis(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # All should be accepted
        for status_code, job_data in results:
            assert status_code == 202
            assert "job_id" in job_data


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    @pytest.mark.asyncio
    async def test_openapi_schema(self, test_app):
        """Test OpenAPI schema generation."""
        response = await test_app.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Check some expected endpoints
        paths = schema["paths"]
        assert "/api/projects" in paths
        assert "/api/analyze/cpm" in paths
        assert "/health" in paths
    
    @pytest.mark.asyncio 
    async def test_docs_endpoints(self, test_app):
        """Test documentation UI endpoints."""
        # Swagger UI
        response = await test_app.get("/docs")
        assert response.status_code == 200
        
        # ReDoc
        response = await test_app.get("/redoc")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])