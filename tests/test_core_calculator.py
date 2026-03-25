"""Tests for core calculator logic."""

import pytest
from pmhelper.calculations import (
    calculate_pm_value,
    calculate_pm_value_async,
    validate_calculation_input
)


def test_validate_calculation_input_valid():
    """Test validation with valid input."""
    validate_calculation_input(42.0, {"multiplier": 2})
    # Should not raise an exception


def test_validate_calculation_input_invalid_value():
    """Test validation with invalid value type."""
    with pytest.raises(ValueError, match="Value must be a number"):
        validate_calculation_input("not a number", {})


def test_validate_calculation_input_negative():
    """Test validation with negative value."""
    with pytest.raises(ValueError, match="Value must be non-negative"):
        validate_calculation_input(-5, {})


def test_validate_calculation_input_invalid_parameters():
    """Test validation with invalid parameters."""
    with pytest.raises(ValueError, match="Parameters must be a dictionary"):
        validate_calculation_input(42, "not a dict")


def test_calculate_pm_value_basic():
    """Test basic calculation."""
    result = calculate_pm_value(42, {})
    
    assert result["result"] == 84  # 42 * 2 (default multiplier)
    assert result["execution_time_ms"] >= 0
    assert result["metadata"]["status"] == "success"
    assert result["metadata"]["input_value"] == 42


def test_calculate_pm_value_custom_multiplier():
    """Test calculation with custom multiplier."""
    result = calculate_pm_value(10, {"multiplier": 5})
    
    assert result["result"] == 50  # 10 * 5
    assert result["metadata"]["parameters"]["multiplier"] == 5


def test_calculate_pm_value_invalid_input():
    """Test calculation with invalid input."""
    with pytest.raises(ValueError):
        calculate_pm_value(-1, {})


@pytest.mark.asyncio
async def test_calculate_pm_value_async():
    """Test async calculation wrapper."""
    result = await calculate_pm_value_async(42, {"multiplier": 3})
    
    assert result["result"] == 126  # 42 * 3
    assert result["execution_time_ms"] >= 0
    assert result["metadata"]["status"] == "success"


@pytest.mark.asyncio
async def test_calculate_pm_value_async_invalid():
    """Test async calculation with invalid input."""
    with pytest.raises(ValueError):
        await calculate_pm_value_async(-10, {})
