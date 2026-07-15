"""
Test Configuration

Configuration and fixtures for PMHelper server testing.
"""

import pytest
import asyncio
import logging
import tempfile
import os
from contextlib import contextmanager
from pathlib import Path

# Configure test environment
os.environ["PMHELPER_TEST_MODE"] = "true"
os.environ["PMHELPER_LOG_LEVEL"] = "WARNING"  # Reduce log noise during tests

# Import components if available
try:
    from pmhelper.server.config import config
    from pmhelper.server.database.connection import init_database, close_database
    SERVER_COMPONENTS_AVAILABLE = True
except ImportError:
    SERVER_COMPONENTS_AVAILABLE = False


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@contextmanager
def _temp_database_url():
    """Point config at a throwaway SQLite file for the duration of a test.

    ``Config`` exposes no public setter — ``get_database_url()`` reads the
    private ``_database_url``, so overriding that is the only seam available.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        original_url = config._database_url
        db_path = Path(temp_dir) / "pmhelper_test.db"
        config._database_url = f"sqlite+aiosqlite:///{db_path}"
        try:
            yield config._database_url
        finally:
            config._database_url = original_url


@pytest.fixture
def temp_database():
    """Create a temporary database for testing."""
    if not SERVER_COMPONENTS_AVAILABLE:
        pytest.skip("Server components not available")

    with _temp_database_url() as db_url:
        yield db_url


@pytest.fixture
async def initialized_database():
    """Initialize a temporary database for testing."""
    if not SERVER_COMPONENTS_AVAILABLE:
        pytest.skip("Server components not available")

    with _temp_database_url() as db_url:
        await init_database()
        try:
            yield db_url
        finally:
            await close_database()


# Test data fixtures
@pytest.fixture
def sample_activities_cpm():
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
        },
        {
            "id": "D",
            "name": "Activity D",
            "duration": 2,
            "predecessors": ["B", "C"],
            "resource": "Team3",
            "cost": 25
        }
    ]


@pytest.fixture
def sample_activities_pert():
    """Sample PERT activities for testing."""
    return [
        {
            "id": "A",
            "name": "Activity A",
            "duration": 5,
            "predecessors": [],
            "optimistic_duration": 3,
            "most_likely_duration": 5,
            "pessimistic_duration": 8
        },
        {
            "id": "B", 
            "name": "Activity B",
            "duration": 4,
            "predecessors": ["A"],
            "optimistic_duration": 2,
            "most_likely_duration": 4,
            "pessimistic_duration": 7
        },
        {
            "id": "C",
            "name": "Activity C",
            "duration": 3,
            "predecessors": ["A"],
            "optimistic_duration": 1,
            "most_likely_duration": 3,
            "pessimistic_duration": 6
        }
    ]


@pytest.fixture
def sample_activities_rcps():
    """Sample RCPS activities for testing."""
    return [
        {
            "id": "A",
            "name": "Activity A",
            "duration": 5,
            "predecessors": [],
            "resource": "Developer",
            "resource_quantity": 2
        },
        {
            "id": "B",
            "name": "Activity B", 
            "duration": 3,
            "predecessors": ["A"],
            "resource": "Developer",
            "resource_quantity": 1
        },
        {
            "id": "C",
            "name": "Activity C",
            "duration": 4,
            "predecessors": [],
            "resource": "Designer",
            "resource_quantity": 1
        },
        {
            "id": "D",
            "name": "Activity D",
            "duration": 2,
            "predecessors": ["B", "C"],
            "resource": "Tester",
            "resource_quantity": 1
        }
    ]


@pytest.fixture
def sample_project_minimal():
    """Minimal project data for testing."""
    return {
        "name": "Test Project",
        "description": "A minimal test project",
        "activities": [
            {
                "id": "A",
                "name": "Single Activity",
                "duration": 5,
                "predecessors": [],
                "resource": "Team"
            }
        ],
        "metadata": {"test": True}
    }


@pytest.fixture
def sample_project_complex():
    """Complex project data for testing."""
    return {
        "name": "Complex Test Project",
        "description": "A complex project with multiple activities and dependencies",
        "activities": [
            {
                "id": "A",
                "name": "Planning",
                "duration": 5,
                "predecessors": [],
                "resource": "PM",
                "cost": 500
            },
            {
                "id": "B",
                "name": "Analysis",
                "duration": 8,
                "predecessors": ["A"],
                "resource": "BA",
                "cost": 800
            },
            {
                "id": "C",
                "name": "Design",
                "duration": 12,
                "predecessors": ["B"],
                "resource": "Architect",
                "cost": 1200
            },
            {
                "id": "D",
                "name": "Development",
                "duration": 20,
                "predecessors": ["C"],
                "resource": "Developer",
                "cost": 2000
            },
            {
                "id": "E",
                "name": "Testing",
                "duration": 10,
                "predecessors": ["D"],
                "resource": "QA",
                "cost": 1000
            },
            {
                "id": "F",
                "name": "Deployment",
                "duration": 3,
                "predecessors": ["E"],
                "resource": "DevOps",
                "cost": 300
            }
        ],
        "metadata": {
            "budget": 5800,
            "priority": "high",
            "department": "IT"
        }
    }


# Test markers
def pytest_configure(config):
    """Configure pytest markers and quiet noisy loggers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "database: marks tests that require database")
    config.addinivalue_line("markers", "api: marks tests for API endpoints")

    logging.getLogger("pmhelper.server").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)


# Skip configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and skips."""
    for item in items:
        # Add markers based on test location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        if "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        
        if "test_database" in str(item.fspath):
            item.add_marker(pytest.mark.database)
        
        # Skip server tests if components not available
        if not SERVER_COMPONENTS_AVAILABLE:
            if any(marker in str(item.fspath) for marker in ["server", "api", "database", "integration"]):
                item.add_marker(pytest.mark.skip(reason="Server components not available"))
