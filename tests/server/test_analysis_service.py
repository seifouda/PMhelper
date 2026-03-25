"""
Test Analysis Service

Unit tests for the analysis service wrapper that handles 
CPM, PERT, and RCPS analysis job processing.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime
import tempfile
from pathlib import Path

# Import the service
try:
    from pmhelper.server.services.analysis_service import AnalysisService, AnalysisJob
    from pmhelper.server.database.models import AnalysisJobModel
    from pmhelper.server.database.connection import init_database, close_database
    from pmhelper.server.config import config
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    pytest.skip(f"Analysis service not available: {e}", allow_module_level=True)


@pytest.fixture
async def analysis_service():
    """Create analysis service with temporary database."""
    if not SERVICE_AVAILABLE:
        pytest.skip("Analysis service not available")
    
    # Create temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        config.DATABASE_DIR = Path(temp_dir)
        config.DATABASE_URL = f"sqlite+aiosqlite:///{config.DATABASE_DIR / config.DATABASE_FILE}"
        
        await init_database()
        
        service = AnalysisService()
        
        try:
            yield service
        finally:
            await close_database()


@pytest.fixture
def sample_cpm_data():
    """Sample CPM analysis data."""
    return {
        "activities": [
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
            }
        ]
    }


@pytest.fixture
def sample_pert_data():
    """Sample PERT analysis data."""
    return {
        "activities": [
            {
                "id": "A",
                "name": "Activity A",
                "duration": 5,
                "predecessors": [],
                "optimistic_duration": 3,
                "most_likely_duration": 5,
                "pessimistic_duration": 7
            }
        ],
        "target_duration": 10,
        "confidence_level": 0.95
    }


@pytest.fixture
def sample_rcps_data():
    """Sample RCPS analysis data."""
    return {
        "activities": [
            {
                "id": "A",
                "name": "Activity A",
                "duration": 5,
                "predecessors": [],
                "resource": "Developer",
                "resource_quantity": 2
            }
        ],
        "resource_limits": {"Developer": 3}
    }


class TestAnalysisService:
    """Test analysis service functionality."""
    
    @pytest.mark.asyncio
    async def test_submit_cpm_analysis(self, analysis_service, sample_cpm_data):
        """Test CPM analysis submission."""
        job = await analysis_service.submit_analysis("cpm", sample_cpm_data)
        
        assert isinstance(job, AnalysisJob)
        assert job.analysis_type == "cpm"
        assert job.status == "pending"
        assert job.job_id is not None
        assert job.submitted_at is not None
        assert job.input_data == sample_cpm_data
    
    @pytest.mark.asyncio
    async def test_submit_pert_analysis(self, analysis_service, sample_pert_data):
        """Test PERT analysis submission."""
        job = await analysis_service.submit_analysis("pert", sample_pert_data)
        
        assert isinstance(job, AnalysisJob)
        assert job.analysis_type == "pert"
        assert job.status == "pending"
        assert job.input_data == sample_pert_data
    
    @pytest.mark.asyncio 
    async def test_submit_rcps_analysis(self, analysis_service, sample_rcps_data):
        """Test RCPS analysis submission."""
        job = await analysis_service.submit_analysis("rcps", sample_rcps_data)
        
        assert isinstance(job, AnalysisJob)
        assert job.analysis_type == "rcps"
        assert job.status == "pending"
        assert job.input_data == sample_rcps_data
    
    @pytest.mark.asyncio
    async def test_invalid_analysis_type(self, analysis_service, sample_cmp_data):
        """Test submitting invalid analysis type."""
        with pytest.raises(ValueError, match="Unsupported analysis type"):
            await analysis_service.submit_analysis("invalid", sample_cmp_data)
    
    @pytest.mark.asyncio
    async def test_get_job_status(self, analysis_service, sample_cpm_data):
        """Test getting job status."""
        # Submit job
        job = await analysis_service.submit_analysis("cpm", sample_cpm_data)
        
        # Get status
        status = await analysis_service.get_job_status(job.job_id)
        assert status["job_id"] == str(job.job_id)
        assert status["status"] == "pending"
        assert status["analysis_type"] == "cpm"
        assert "submitted_at" in status
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_job_status(self, analysis_service):
        """Test getting status for non-existent job."""
        import uuid
        fake_job_id = uuid.uuid4()
        
        status = await analysis_service.get_job_status(fake_job_id)
        assert status is None
    
    @pytest.mark.asyncio
    async def test_get_job_results_not_ready(self, analysis_service, sample_cpm_data):
        """Test getting results for incomplete job."""
        # Submit job
        job = await analysis_service.submit_analysis("cpm", sample_cpm_data)
        
        # Try to get results (should not be ready)
        results = await analysis_service.get_job_results(job.job_id)
        assert results is None
    
    @pytest.mark.asyncio
    async def test_list_jobs(self, analysis_service, sample_cpm_data, sample_pert_data):
        """Test listing jobs."""
        # Submit multiple jobs
        job1 = await analysis_service.submit_analysis("cpm", sample_cpm_data)
        job2 = await analysis_service.submit_analysis("pert", sample_pert_data)
        
        # List jobs
        jobs = await analysis_service.list_jobs()
        
        assert len(jobs) >= 2
        job_ids = [job["job_id"] for job in jobs]
        assert str(job1.job_id) in job_ids
        assert str(job2.job_id) in job_ids


class TestAnalysisProcessing:
    """Test analysis processing with mocked analyzers."""
    
    @pytest.mark.asyncio
    @patch('pmhelper.server.services.analysis_service.CPMAnalyzer')
    async def test_process_cpm_analysis_success(self, mock_cpm_analyzer, analysis_service, sample_cpm_data):
        """Test successful CPM analysis processing."""
        # Mock the analyzer
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = {
            "critical_path": ["A", "B"],
            "project_duration": 8,
            "activities": {
                "A": {"early_start": 0, "early_finish": 5, "slack": 0},
                "B": {"early_start": 5, "early_finish": 8, "slack": 0}
            }
        }
        mock_cpm_analyzer.return_value = mock_analyzer_instance
        
        # Submit and process job
        job = await analysis_service.submit_analysis("cpm", sample_cpm_data)
        
        # Manually trigger processing (normally done in background)
        await analysis_service._process_job(job.job_id)
        
        # Check results
        results = await analysis_service.get_job_results(job.job_id)
        assert results is not None
        assert "critical_path" in results
        assert results["critical_path"] == ["A", "B"]
        assert results["project_duration"] == 8
        
        # Check job status
        status = await analysis_service.get_job_status(job.job_id)
        assert status["status"] == "completed"
    
    @pytest.mark.asyncio
    @patch('pmhelper.server.services.analysis_service.PERTAnalyzer')
    async def test_process_pert_analysis_success(self, mock_pert_analyzer, analysis_service, sample_pert_data):
        """Test successful PERT analysis processing."""
        # Mock the analyzer
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = {
            "expected_duration": 5.0,
            "variance": 0.44,
            "probability": 0.95,
            "activities": {
                "A": {"expected_duration": 5.0, "variance": 0.44}
            }
        }
        mock_pert_analyzer.return_value = mock_analyzer_instance
        
        # Submit and process job
        job = await analysis_service.submit_analysis("pert", sample_pert_data)
        await analysis_service._process_job(job.job_id)
        
        # Check results
        results = await analysis_service.get_job_results(job.job_id)
        assert results is not None
        assert "expected_duration" in results
        assert results["expected_duration"] == 5.0
    
    @pytest.mark.asyncio
    @patch('pmhelper.server.services.analysis_service.CPMAnalyzer')
    async def test_process_analysis_error(self, mock_cpm_analyzer, analysis_service, sample_cpm_data):
        """Test analysis processing with error."""
        # Mock analyzer to raise an exception
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.side_effect = Exception("Analysis failed")
        mock_cpm_analyzer.return_value = mock_analyzer_instance
        
        # Submit and process job
        job = await analysis_service.submit_analysis("cpm", sample_cpm_data)
        await analysis_service._process_job(job.job_id)
        
        # Check status
        status = await analysis_service.get_job_status(job.job_id)
        assert status["status"] == "failed"
        assert "error" in status
        assert "Analysis failed" in status["error"]
        
        # Results should be None
        results = await analysis_service.get_job_results(job.job_id)
        assert results is None


class TestAnalysisJob:
    """Test AnalysisJob data class."""
    
    def test_analysis_job_creation(self):
        """Test AnalysisJob creation.""" 
        import uuid
        from datetime import datetime
        
        job_id = uuid.uuid4()
        now = datetime.utcnow()
        input_data = {"test": "data"}
        
        job = AnalysisJob(
            job_id=job_id,
            analysis_type="cpm",
            status="pending", 
            input_data=input_data,
            submitted_at=now
        )
        
        assert job.job_id == job_id
        assert job.analysis_type == "cpm"
        assert job.status == "pending"
        assert job.input_data == input_data
        assert job.submitted_at == now
        assert job.completed_at is None
        assert job.results is None
        assert job.error_message is None
    
    def test_analysis_job_to_dict(self):
        """Test AnalysisJob to_dict method."""
        import uuid
        from datetime import datetime
        
        job = AnalysisJob(
            job_id=uuid.uuid4(),
            analysis_type="pert",
            status="completed",
            input_data={"activities": []},
            submitted_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            results={"result": "data"}
        )
        
        job_dict = job.to_dict()
        
        assert "job_id" in job_dict
        assert job_dict["analysis_type"] == "pert"
        assert job_dict["status"] == "completed"
        assert "submitted_at" in job_dict
        assert "completed_at" in job_dict
        assert job_dict["results"] == {"result": "data"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])