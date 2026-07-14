# Calculations Migration Guide

## 📋 Overview

This guide explains how to migrate your PM calculation logic (CPM, PERT, Crashing, RCPS) from the GUI application to the centralized `calculations.py` module so both the GUI and API can use the same code.

---

## ✅ YES! You Need to Migrate

You need to **migrate the calculation logic** from your GUI application to `src/pmhelper/calculations.py` so both the GUI and API can use the same code.

---

## 🎯 Current Situation

```
┌─────────────────────────────────────────────────────┐
│  GUI Application (Tkinter)                          │
│  ├── CPM calculations (embedded in GUI code)        │
│  ├── PERT calculations (embedded in GUI code)       │
│  └── Crashing calculations (embedded in GUI code)   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  calculations.py                                    │
│  └── Placeholder: result = value * multiplier       │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Target Architecture

```
┌──────────────────────────────────────────────────────┐
│  calculations.py (Shared Logic)                      │
│  ├── calculate_cpm(activities, dependencies)         │
│  ├── calculate_pert(activities, probabilities)       │
│  ├── calculate_crashing(activities, cost_data)       │
│  └── calculate_rcps(activities, resources)           │
└────────────────┬─────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ↓                 ↓
┌────────────┐    ┌──────────────┐
│ GUI (Tkinter)│    │ FastAPI Server│
│ - Calls      │    │ - Exposes via │
│   directly   │    │   REST API    │
└────────────┘    └──────────────┘
```

---

## 📋 Migration Steps

### Step 1: Find Your Current Calculation Code

Let me help you locate where your CPM/PERT/Crashing calculations currently live:

```powershell
# Search for calculation logic in GUI
Get-ChildItem -Path "src/pmhelper/gui" -Recurse -Filter "*.py" |
    Select-String -Pattern "(cpm|pert|crash|critical.*path)" -CaseSensitive:$false
```

**Common locations:**

- `src/pmhelper/gui/tabs/cpm_tab.py`
- `src/pmhelper/gui/tabs/pert_tab.py`
- `src/pmhelper/core/cpm_analyzer.py`
- `src/pmhelper/core/pert_analyzer.py`
- `src/pmhelper/core/crashing_step_generator.py`

### Step 2: Extract to `calculations.py`

Here's the recommended structure for `src/pmhelper/calculations.py`:

```python
"""
PM calculation functions - SYNCHRONOUS (CPU-bound operations).

Centralized calculation logic used by both GUI and API.
"""

from typing import Dict, Any, List, Tuple
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes for Type Safety
# ============================================================================

@dataclass
class Activity:
    """Represents a project activity."""
    id: str
    name: str
    duration: float
    predecessors: List[str] = None

    def __post_init__(self):
        if self.predecessors is None:
            self.predecessors = []


@dataclass
class PERTActivity(Activity):
    """Activity with PERT time estimates."""
    optimistic: float = None
    most_likely: float = None
    pessimistic: float = None


# ============================================================================
# CPM (Critical Path Method) Calculations
# ============================================================================

def calculate_cpm(activities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate Critical Path Method analysis.

    Args:
        activities: List of activity dictionaries with:
            - id: Activity identifier
            - name: Activity name
            - duration: Activity duration
            - predecessors: List of predecessor IDs

    Returns:
        Dictionary containing:
            - critical_path: List of activity IDs on critical path
            - project_duration: Total project duration
            - activities: Enhanced activities with ES, EF, LS, LF, slack
            - execution_time_ms: Calculation time

    Example:
        >>> activities = [
        ...     {"id": "A", "name": "Task A", "duration": 5, "predecessors": []},
        ...     {"id": "B", "name": "Task B", "duration": 3, "predecessors": ["A"]}
        ... ]
        >>> result = calculate_cpm(activities)
        >>> result["project_duration"]
        8
    """
    start = time.perf_counter()

    # TODO: Paste your CPM algorithm here from GUI code
    # Example structure:
    # 1. Forward pass (calculate ES, EF)
    # 2. Backward pass (calculate LS, LF)
    # 3. Calculate slack
    # 4. Identify critical path

    # Placeholder - replace with your actual CPM logic
    critical_path = []
    project_duration = 0
    enhanced_activities = []

    execution_time_ms = (time.perf_counter() - start) * 1000

    return {
        "critical_path": critical_path,
        "project_duration": project_duration,
        "activities": enhanced_activities,
        "execution_time_ms": execution_time_ms,
        "metadata": {
            "status": "success",
            "method": "CPM",
            "activity_count": len(activities)
        }
    }


# ============================================================================
# PERT (Program Evaluation and Review Technique) Calculations
# ============================================================================

def calculate_pert(activities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate PERT analysis with three-point estimates.

    Args:
        activities: List of activity dictionaries with:
            - id: Activity identifier
            - name: Activity name
            - optimistic: Optimistic duration
            - most_likely: Most likely duration
            - pessimistic: Pessimistic duration
            - predecessors: List of predecessor IDs

    Returns:
        Dictionary containing:
            - expected_duration: Expected project duration
            - variance: Project variance
            - standard_deviation: Project standard deviation
            - activities: Activities with expected time and variance
            - execution_time_ms: Calculation time

    Example:
        >>> activities = [
        ...     {"id": "A", "optimistic": 2, "most_likely": 4, "pessimistic": 6, "predecessors": []}
        ... ]
        >>> result = calculate_pert(activities)
    """
    start = time.perf_counter()

    # TODO: Paste your PERT algorithm here from GUI code
    # Example structure:
    # 1. Calculate expected time: (O + 4M + P) / 6
    # 2. Calculate variance: ((P - O) / 6)²
    # 3. Find critical path using expected times
    # 4. Sum variances along critical path

    # Placeholder - replace with your actual PERT logic
    expected_duration = 0
    variance = 0
    standard_deviation = 0

    execution_time_ms = (time.perf_counter() - start) * 1000

    return {
        "expected_duration": expected_duration,
        "variance": variance,
        "standard_deviation": standard_deviation,
        "activities": [],
        "execution_time_ms": execution_time_ms,
        "metadata": {
            "status": "success",
            "method": "PERT",
            "activity_count": len(activities)
        }
    }


# ============================================================================
# Crashing Analysis
# ============================================================================

def calculate_crashing(
    activities: List[Dict[str, Any]],
    target_duration: float = None,
    budget_limit: float = None
) -> Dict[str, Any]:
    """
    Calculate optimal project crashing strategy.

    Args:
        activities: List of activity dictionaries with:
            - id: Activity identifier
            - name: Activity name
            - normal_duration: Normal duration
            - crash_duration: Minimum crash duration
            - normal_cost: Normal cost
            - crash_cost: Maximum crash cost
            - predecessors: List of predecessor IDs
        target_duration: Desired project duration (optional)
        budget_limit: Maximum budget for crashing (optional)

    Returns:
        Dictionary containing:
            - original_duration: Original project duration
            - crashed_duration: Duration after crashing
            - total_cost: Total crashing cost
            - crashed_activities: List of activities to crash
            - crash_plan: Step-by-step crashing recommendations
            - execution_time_ms: Calculation time

    Example:
        >>> activities = [
        ...     {"id": "A", "normal_duration": 10, "crash_duration": 8,
        ...      "normal_cost": 100, "crash_cost": 200, "predecessors": []}
        ... ]
        >>> result = calculate_crashing(activities, target_duration=9)
    """
    start = time.perf_counter()

    # TODO: Paste your Crashing algorithm here from GUI code
    # Example structure:
    # 1. Calculate initial CPM
    # 2. For each critical activity, calculate cost slope
    # 3. Select activity with lowest cost slope
    # 4. Crash by 1 time unit
    # 5. Recalculate CPM
    # 6. Repeat until target met or budget exhausted

    # Placeholder - replace with your actual Crashing logic
    original_duration = 0
    crashed_duration = 0
    total_cost = 0
    crashed_activities = []
    crash_plan = []

    execution_time_ms = (time.perf_counter() - start) * 1000

    return {
        "original_duration": original_duration,
        "crashed_duration": crashed_duration,
        "total_cost": total_cost,
        "crashed_activities": crashed_activities,
        "crash_plan": crash_plan,
        "execution_time_ms": execution_time_ms,
        "metadata": {
            "status": "success",
            "method": "Crashing",
            "activity_count": len(activities)
        }
    }


# ============================================================================
# RCPS (Resource-Constrained Project Scheduling)
# ============================================================================

def calculate_rcps(
    activities: List[Dict[str, Any]],
    resources: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculate resource-constrained project schedule.

    Args:
        activities: List of activity dictionaries with:
            - id: Activity identifier
            - name: Activity name
            - duration: Activity duration
            - predecessors: List of predecessor IDs
            - resources: Dict of resource requirements (e.g., {"workers": 3})
        resources: Available resources (e.g., {"workers": 10, "machines": 5})

    Returns:
        Dictionary containing:
            - schedule: List of activities with start/finish times
            - project_duration: Total project duration
            - resource_profile: Resource usage over time
            - conflicts: List of resource conflicts found
            - execution_time_ms: Calculation time
    """
    start = time.perf_counter()

    # TODO: Paste your RCPS algorithm here from GUI code
    # Example structure:
    # 1. Create activity list sorted by priority
    # 2. Schedule activities respecting predecessors
    # 3. Check resource availability
    # 4. Delay activities if resources unavailable
    # 5. Generate resource profile

    # Placeholder - replace with your actual RCPS logic
    schedule = []
    project_duration = 0
    resource_profile = {}
    conflicts = []

    execution_time_ms = (time.perf_counter() - start) * 1000

    return {
        "schedule": schedule,
        "project_duration": project_duration,
        "resource_profile": resource_profile,
        "conflicts": conflicts,
        "execution_time_ms": execution_time_ms,
        "metadata": {
            "status": "success",
            "method": "RCPS",
            "activity_count": len(activities)
        }
    }


# ============================================================================
# Unified Calculation Entry Point
# ============================================================================

def calculate_pm_value(value: float, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unified entry point for PM calculations.
    Routes to specific calculation method based on parameters.

    Args:
        value: Not used (kept for backward compatibility)
        parameters: Must contain:
            - method: "CPM", "PERT", "Crashing", or "RCPS"
            - activities: List of activity data
            - [method-specific parameters]

    Returns:
        Result from the specific calculation method
    """
    method = parameters.get("method", "").upper()
    activities = parameters.get("activities", [])

    if method == "CPM":
        return calculate_cpm(activities)
    elif method == "PERT":
        return calculate_pert(activities)
    elif method == "CRASHING":
        target_duration = parameters.get("target_duration")
        budget_limit = parameters.get("budget_limit")
        return calculate_crashing(activities, target_duration, budget_limit)
    elif method == "RCPS":
        resources = parameters.get("resources", {})
        return calculate_rcps(activities, resources)
    else:
        raise ValueError(f"Unknown calculation method: {method}")


# ============================================================================
# Async Wrapper (for API use)
# ============================================================================

async def calculate_pm_value_async(value: float, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for heavy calculations.
    Runs calculation in thread pool to avoid blocking event loop.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, calculate_pm_value, value, parameters)
```

---

## 🔧 Step 3: Update Your GUI to Use Shared Code

### Before (GUI with embedded logic):

```python
# src/pmhelper/gui/tabs/cpm_tab.py
class CPMTab:
    def calculate(self):
        # CPM logic embedded here
        for activity in self.activities:
            # Calculate ES, EF, LS, LF...
            pass
```

### After (GUI using shared module):

```python
# src/pmhelper/gui/tabs/cpm_tab.py
from pmhelper.calculations import calculate_cpm

class CPMTab:
    def calculate(self):
        # Prepare data
        activities = [
            {"id": act.id, "duration": act.duration, "predecessors": act.predecessors}
            for act in self.activities
        ]

        # Call shared calculation
        result = calculate_cpm(activities)

        # Display result
        self.display_result(result)
```

---

## 📊 Step 4: Update API Endpoints

The API automatically gets all methods:

```python
# src/pmhelper/server/api/routes/calculations.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from pmhelper.calculations import calculate_pm_value_async

router = APIRouter(prefix="/api/calculations", tags=["calculations"])


@router.post("/cpm")
async def calculate_cpm_endpoint(activities: List[Dict]):
    """Calculate CPM via API."""
    result = await calculate_pm_value_async(
        0,  # Not used
        {"method": "CPM", "activities": activities}
    )
    return result


@router.post("/pert")
async def calculate_pert_endpoint(activities: List[Dict]):
    """Calculate PERT via API."""
    result = await calculate_pm_value_async(
        0,
        {"method": "PERT", "activities": activities}
    )
    return result


@router.post("/crashing")
async def calculate_crashing_endpoint(
    activities: List[Dict],
    target_duration: float = None,
    budget_limit: float = None
):
    """Calculate project crashing via API."""
    result = await calculate_pm_value_async(
        0,
        {
            "method": "Crashing",
            "activities": activities,
            "target_duration": target_duration,
            "budget_limit": budget_limit
        }
    )
    return result


@router.post("/rcps")
async def calculate_rcps_endpoint(
    activities: List[Dict],
    resources: Dict[str, float]
):
    """Calculate RCPS via API."""
    result = await calculate_pm_value_async(
        0,
        {
            "method": "RCPS",
            "activities": activities,
            "resources": resources
        }
    )
    return result
```

---

## ✅ Benefits of This Approach

1. **Single Source of Truth** - One calculation implementation
2. **Easy Testing** - Test calculations independently
3. **API Gets Everything** - Any calculation in GUI automatically available via API
4. **Maintainability** - Fix bugs in one place
5. **Performance** - No duplication of logic
6. **Type Safety** - Clear input/output contracts

---

## 🧪 Testing the Migration

### Test calculations directly:

```python
# test_calculations.py
from pmhelper.calculations import calculate_cpm

activities = [
    {"id": "A", "name": "Task A", "duration": 5, "predecessors": []},
    {"id": "B", "name": "Task B", "duration": 3, "predecessors": ["A"]},
    {"id": "C", "name": "Task C", "duration": 4, "predecessors": ["A"]},
    {"id": "D", "name": "Task D", "duration": 2, "predecessors": ["B", "C"]}
]

result = calculate_cpm(activities)
print(f"Project Duration: {result['project_duration']}")
print(f"Critical Path: {result['critical_path']}")
```

### Test via API:

```bash
# Start server
python -m pmhelper.server.main

# Test CPM endpoint
curl -X POST http://localhost:8000/api/calculations/cpm \
  -H "Content-Type: application/json" \
  -d '{
    "activities": [
      {"id": "A", "duration": 5, "predecessors": []},
      {"id": "B", "duration": 3, "predecessors": ["A"]}
    ]
  }'
```

### Test in GUI:

```python
# The GUI should work exactly as before
# but now uses the centralized calculations.py
```

---

## 📋 Migration Checklist

- [ ] **Step 1**: Locate current calculation code in GUI

  - [ ] Find CPM logic
  - [ ] Find PERT logic
  - [ ] Find Crashing logic
  - [ ] Find RCPS logic

- [ ] **Step 2**: Copy logic to `calculations.py`

  - [ ] Implement `calculate_cpm()`
  - [ ] Implement `calculate_pert()`
  - [ ] Implement `calculate_crashing()`
  - [ ] Implement `calculate_rcps()`

- [ ] **Step 3**: Update GUI to use shared module

  - [ ] Update CPM tab
  - [ ] Update PERT tab
  - [ ] Update Crashing tab
  - [ ] Update RCPS tab

- [ ] **Step 4**: Add API endpoints

  - [ ] Create `/api/calculations/cpm` endpoint
  - [ ] Create `/api/calculations/pert` endpoint
  - [ ] Create `/api/calculations/crashing` endpoint
  - [ ] Create `/api/calculations/rcps` endpoint

- [ ] **Step 5**: Testing

  - [ ] Test calculations directly
  - [ ] Test GUI functionality
  - [ ] Test API endpoints
  - [ ] Write unit tests

- [ ] **Step 6**: Documentation
  - [ ] Update API documentation
  - [ ] Update README
  - [ ] Add examples

---

## 🎯 What You Need to Do Now

1. **Find your current calculation code** in the GUI

   ```powershell
   # Search for existing calculation files
   Get-ChildItem -Path "src/pmhelper" -Recurse -Filter "*cpm*.py"
   Get-ChildItem -Path "src/pmhelper" -Recurse -Filter "*pert*.py"
   Get-ChildItem -Path "src/pmhelper" -Recurse -Filter "*crash*.py"
   ```

2. **Copy the logic** to `src/pmhelper/calculations.py` (use the structure provided above)

3. **Update GUI tabs** to call `calculations.py` instead of embedded logic

4. **Test everything** works the same

5. **API automatically** exposes all calculations

---

## 📞 Need Help?

If you need assistance with:

- Locating your current CPM/PERT/Crashing code
- Creating a migration script to move the logic
- Updating specific GUI tabs to use the shared module
- Writing tests for the new structure

Just ask!

---

**Last Updated**: November 1, 2025  
**Version**: 1.0.0  
**Status**: Ready for implementation
