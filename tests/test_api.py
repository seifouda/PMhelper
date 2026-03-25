"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from pmhelper.server.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "PMHelper API"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "pmhelper"
    assert data["version"] == "1.0.0"


def test_calculate_endpoint_valid():
    """Test calculation endpoint with valid input."""
    response = client.post(
        "/api/calculations/calculate",
        json={"value": 42, "parameters": {}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"] == 84  # 42 * 2
    assert "execution_time_ms" in data
    assert "metadata" in data


def test_calculate_endpoint_custom_parameters():
    """Test calculation with custom parameters."""
    response = client.post(
        "/api/calculations/calculate",
        json={"value": 10, "parameters": {"multiplier": 5}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 50  # 10 * 5


def test_calculate_endpoint_invalid_value():
    """Test calculation with invalid value."""
    response = client.post(
        "/api/calculations/calculate",
        json={"value": -5, "parameters": {}}
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_calculate_endpoint_missing_value():
    """Test calculation with missing value."""
    response = client.post(
        "/api/calculations/calculate",
        json={"parameters": {}}  # Missing 'value'
    )
    assert response.status_code == 422  # Validation error


def test_calculations_health_check():
    """Test calculations API health check."""
    response = client.get("/api/calculations/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["api"] == "calculations"


def test_calculate_endpoint_zero_value():
    """Test calculation with zero value."""
    response = client.post(
        "/api/calculations/calculate",
        json={"value": 0, "parameters": {}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 0


def test_calculate_endpoint_float_value():
    """Test calculation with float value."""
    response = client.post(
        "/api/calculations/calculate",
        json={"value": 3.5, "parameters": {"multiplier": 2}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 7.0
