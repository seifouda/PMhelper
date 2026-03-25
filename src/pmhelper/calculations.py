"""
PM calculation functions - SYNCHRONOUS (CPU-bound operations).

No async overhead - calculations are CPU-bound, not I/O-bound.
Keep it simple: pure functions that take input and return results.
"""

from typing import Dict, Any
import time
import logging

logger = logging.getLogger(__name__)


def validate_calculation_input(value: float, parameters: Dict[str, Any]) -> None:
    """
    Validate input data before calculation.

    Args:
        value: Input value
        parameters: Calculation parameters

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, (int, float)):
        raise ValueError("Value must be a number")

    if value < 0:
        raise ValueError("Value must be non-negative")

    if not isinstance(parameters, dict):
        raise ValueError("Parameters must be a dictionary")


def calculate_pm_value(value: float, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform PM calculation synchronously.

    This is a CPU-bound operation, so it's synchronous by design.
    Use ThreadPoolExecutor in API layer if you need concurrency.

    Args:
        value: Input value to calculate
        parameters: Calculation parameters (e.g., multiplier)

    Returns:
        Dictionary with result and metadata

    Raises:
        ValueError: If input is invalid
    """
    start = time.perf_counter()

    # Validate input
    validate_calculation_input(value, parameters)

    # TODO: Replace with actual PM calculation logic
    # This is a placeholder - implement your CPM/PERT/RCPS algorithms here
    multiplier = parameters.get("multiplier", 2)
    result = value * multiplier

    execution_time_ms = (time.perf_counter() - start) * 1000

    logger.debug(f"Calculated value={value}, result={result}, time={execution_time_ms:.2f}ms")

    return {
        "result": result,
        "execution_time_ms": execution_time_ms,
        "metadata": {
            "status": "success",
            "input_value": value,
            "parameters": parameters
        }
    }


# If you need async wrapper for API integration:
async def calculate_pm_value_async(value: float, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for heavy calculations.
    Runs calculation in thread pool to avoid blocking event loop.

    Only use this if calculations take >100ms. Otherwise, call sync version directly.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, calculate_pm_value, value, parameters)
