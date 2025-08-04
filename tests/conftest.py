#!/usr/bin/env python3
"""
Test Configuration

pytest configuration and common test utilities.
Provides fixtures and configuration for comprehensive testing of PMHelper.
"""

import pytest
import sys
import tempfile
import os
import matplotlib
import warnings
from pathlib import Path

# Use non-interactive matplotlib backend for testing
matplotlib.use('Agg')

# Suppress warnings during testing
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# Add src to Python path for testing
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


# Test Configuration
def pytest_configure(config):
    """Configure pytest with custom options"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "gui: marks tests as GUI tests (require display)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Test Data Fixtures
@pytest.fixture
def sample_cpm_data():
    """Sample CPM data for testing"""
    return [
        {
            'id': 'A',
            'activity': 'Start Activity',
            'duration': 3,
            'min_duration': 2,
            'crash_cost': 100,
            'predecessors': '',
            'resource_demand': 2,
            'normal_cost': 200
        },
        {
            'id': 'B',
            'activity': 'Second Activity',
            'duration': 5,
            'min_duration': 3,
            'crash_cost': 150,
            'predecessors': 'A',
            'resource_demand': 3,
            'normal_cost': 300
        },
        {
            'id': 'C',
            'activity': 'Third Activity',
            'duration': 4,
            'min_duration': 2,
            'crash_cost': 200,
            'predecessors': 'A',
            'resource_demand': 1,
            'normal_cost': 250
        },
        {
            'id': 'D',
            'activity': 'Final Activity',
            'duration': 2,
            'min_duration': 1,
            'crash_cost': 80,
            'predecessors': 'B,C',
            'resource_demand': 2,
            'normal_cost': 150
        }
    ]


@pytest.fixture
def sample_pert_data():
    """Sample PERT data for testing"""
    return [
        {
            'id': 'A',
            'activity': 'Start Activity',
            'optimistic': 2,
            'most_likely': 3,
            'pessimistic': 5,
            'predecessors': ''
        },
        {
            'id': 'B',
            'activity': 'Second Activity',
            'optimistic': 3,
            'most_likely': 5,
            'pessimistic': 8,
            'predecessors': 'A'
        },
        {
            'id': 'C',
            'activity': 'Third Activity',
            'optimistic': 1,
            'most_likely': 4,
            'pessimistic': 6,
            'predecessors': 'A'
        },
        {
            'id': 'D',
            'activity': 'Final Activity',
            'optimistic': 1,
            'most_likely': 2,
            'pessimistic': 4,
            'predecessors': 'B,C'
        }
    ]


# Analyzer Fixtures
@pytest.fixture
def cpm_analyzer():
    """CPM analyzer instance for testing"""
    try:
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        return CPMAnalyzer()
    except ImportError:
        pytest.skip("CPM analyzer not available")


@pytest.fixture
def pert_analyzer():
    """PERT analyzer instance for testing"""
    try:
        from pmhelper.core.pert_analyzer import PERTAnalyzer
        return PERTAnalyzer()
    except ImportError:
        pytest.skip("PERT analyzer not available")


@pytest.fixture
def network_builder():
    """Network builder instance for testing"""
    try:
        from pmhelper.core.network_builder import NetworkBuilder
        return NetworkBuilder()
    except ImportError:
        pytest.skip("Network builder not available")


@pytest.fixture
def file_handler():
    """File handler instance for testing"""
    try:
        from pmhelper.utils.file_handlers import FileHandler
        return FileHandler()
    except ImportError:
        pytest.skip("File handler not available")


# File System Fixtures
@pytest.fixture
def temp_dir():
    """Temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except:
        pass


# Cleanup Hooks
@pytest.fixture(autouse=True)
def cleanup_matplotlib():
    """Cleanup matplotlib figures after each test"""
    yield
    import matplotlib.pyplot as plt
    plt.close('all')
