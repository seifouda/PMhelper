# Resource Leveling Guide

## Overview

The Resource Leveling Module provides advanced algorithms to optimize resource utilization across project schedules. By intelligently shifting non-critical activities within their float, the module smooths resource usage while maintaining project duration and all precedence relationships.

## Key Concepts

### What is Resource Leveling?

Resource leveling is the process of adjusting the start and finish dates of activities to create a more balanced resource profile. The goals are:

1. **Reduce peaks and valleys** in resource usage
2. **Smooth resource demand** over time
3. **Avoid resource overallocation** (exceeding limits)
4. **Maintain project duration** (don't extend critical path)
5. **Preserve precedence relationships** (dependencies)

### Resource Moment

The **resource moment** measures the variability of resource usage:

```
Moment = Σ(usage_i - mean_usage)²
```

**Lower moment = Smoother resource usage**

### When to Use Resource Leveling

✅ **Use when:**

- Resource usage has large peaks and valleys
- You want to avoid hiring/firing cycles
- Equipment rental costs are high during peaks
- Overtime costs need to be reduced
- Resource capacity is limited

❌ **Don't use when:**

- All activities are critical (no float to work with)
- Resource usage is already smooth
- Project duration must be minimized at any cost

---

## Installation & Setup

The module is already integrated into PMHelper. No additional installation required.

---

## Quick Start

### Basic Example

```python
from src.pmhelper.core.resource_leveling import (
    Activity,
    MinimumMomentLeveling
)

# Create activities with resource demands
activities = [
    Activity(
        id='A',
        duration=4,
        resource_demand=6.0,  # Requires 6 units of resource
        es=0, ef=4,           # Early start/finish
        ls=0, lf=4,           # Late start/finish
        float=0,              # Total float (critical)
        predecessors=[],
        successors=['B']
    ),
    Activity(
        id='B',
        duration=3,
        resource_demand=4.0,
        es=4, ef=7,
        ls=5, lf=8,
        float=1,              # Has 1 day float (non-critical)
        predecessors=['A'],
        successors=[]
    )
]

# Apply minimum moment leveling
leveler = MinimumMomentLeveling(activities, resource_limit=10.0)
result = leveler.level()

# Check results
print(f"Improvement: {result['improvement_pct']:.1f}%")
print(f"Peak usage: {result['peak_usage_original']:.1f} → {result['peak_usage_leveled']:.1f}")
print(f"Feasible: {result['feasible']}")
```

### Integration with CPM

```python
from src.pmhelper.core.cpm_analyzer import CPMAnalyzer
from src.pmhelper.core.resource_leveling import (
    activities_from_cpm,
    ResourceLevelingFactory
)

# Step 1: Perform CPM analysis
cpm = CPMAnalyzer()
activity_data = [...]  # Your project data
cpm.analyze(activity_data)

# Step 2: Convert to resource leveling format
activities = activities_from_cpm(cpm)

# Step 3: Apply leveling
leveler = ResourceLevelingFactory.create(
    method='minimum_moment',
    activities=activities,
    resource_limit=10.0
)
result = leveler.level()
```

---

## Algorithms

### 1. Minimum Moment Method

**Best for:** General resource smoothing, reducing variability

**How it works:**

- Minimizes the sum of squared deviations from mean usage
- Shifts non-critical activities to reduce moment
- Iteratively finds better positions

**Usage:**

```python
from src.pmhelper.core.resource_leveling import MinimumMomentLeveling

leveler = MinimumMomentLeveling(activities, resource_limit=10.0)
result = leveler.level(max_iterations=1000)
```

**Parameters:**

- `activities`: List of Activity objects
- `resource_limit`: Optional resource constraint
- `max_iterations`: Maximum optimization iterations (default: 1000)

### 2. Burgess Method

**Best for:** Minimizing resource peaks, balancing load

**How it works:**

- Minimizes sum of squares of resource usage
- Similar to minimum moment but different objective
- Good for multiple resource types

**Usage:**

```python
from src.pmhelper.core.resource_leveling import BurgessLeveling

leveler = BurgessLeveling(activities, resource_limit=10.0)
result = leveler.level(max_iterations=1000)
```

### Factory Pattern (Recommended)

**Best for:** Switching between algorithms easily

```python
from src.pmhelper.core.resource_leveling import ResourceLevelingFactory

# Try minimum moment
leveler1 = ResourceLevelingFactory.create('minimum_moment', activities, 10.0)
result1 = leveler1.level()

# Try Burgess
leveler2 = ResourceLevelingFactory.create('burgess', activities, 10.0)
result2 = leveler2.level()

# Compare and choose best
if result1['improvement_pct'] > result2['improvement_pct']:
    best_result = result1
else:
    best_result = result2
```

---

## Visualization

### Resource Profile Plot

Shows before/after resource usage:

```python
from src.pmhelper.core.resource_visualizations import plot_resource_profile

# Get profiles from result
original_df = result['original_profile'].to_dataframe()
leveled_df = result['leveled_profile'].to_dataframe()

# Create plot
fig = plot_resource_profile(
    original_df,
    leveled_df,
    resource_limit=10.0,
    method_name="Minimum Moment"
)
fig.savefig('resource_profile.png', dpi=150)
```

**Output:** 2-panel chart showing original vs. leveled resource usage

### Metrics Dashboard

Shows performance metrics:

```python
from src.pmhelper.core.resource_visualizations import plot_leveling_metrics

fig = plot_leveling_metrics(result)
fig.savefig('metrics.png', dpi=150)
```

**Output:** 4-panel dashboard with:

- Moment/cost reduction
- Peak usage comparison
- Improvement percentage
- Feasibility status

### Gantt Chart Comparison

Shows schedule changes:

```python
from src.pmhelper.core.resource_visualizations import plot_gantt_comparison

fig = plot_gantt_comparison(
    result['original_schedule'],
    result['leveled_schedule'],
    activities,
    resource_limit=10.0
)
fig.savefig('gantt.png', dpi=150)
```

**Output:** Before/after Gantt charts with critical path highlighting

---

## Reporting

### Text Reports

```python
from src.pmhelper.core.resource_visualizations import generate_leveling_report

report = generate_leveling_report(result, "Minimum Moment Method")
print(report)

# Save to file
with open('report.txt', 'w', encoding='utf-8') as f:
    f.write(report)
```

**Output:**

```
======================================================================
            RESOURCE LEVELING REPORT - MINIMUM MOMENT METHOD
======================================================================

SUMMARY
-------
Method: Minimum Moment Method
Iterations: 15
Feasibility: FEASIBLE

ORIGINAL SCHEDULE (Early Start)
--------------------------------
  Peak Resource Usage: 12.00
  Moment: 145.60

LEVELED SCHEDULE (Optimized)
-----------------------------
  Peak Resource Usage: 9.50
  Moment: 89.20

IMPROVEMENT
-----------
  Moment Reduction: 56.40
  Percentage Improvement: 38.7%
  Peak Reduction: 2.50

ACTIVITY SCHEDULE CHANGES
--------------------------
  Activity | Original Start | Leveled Start | Shift
  ------------------------------------------------------
  C        |              4 |             6 |    +2
  D        |              7 |             9 |    +2

  Total activities moved: 2

======================================================================
```

### Data Export

```python
from src.pmhelper.core.resource_visualizations import export_leveling_results

# Export to CSV
export_leveling_results(result, 'results.csv', format='csv')

# Export to JSON
export_leveling_results(result, 'results.json', format='json')
```

---

## Result Dictionary

The `level()` method returns a dictionary with:

```python
{
    # Schedules
    'leveled_schedule': {'A': 0, 'B': 5, ...},  # Activity start times
    'original_schedule': {'A': 0, 'B': 4, ...}, # Original start times

    # Metrics
    'original_moment': 145.6,        # Original moment value
    'leveled_moment': 89.2,          # Leveled moment value
    'improvement_pct': 38.7,         # Improvement percentage
    'iterations': 15,                # Number of iterations

    # Resource usage
    'peak_usage_original': 12.0,     # Original peak
    'peak_usage_leveled': 9.5,       # Leveled peak

    # Profiles (for visualization)
    'original_profile': ResourceProfile(...),
    'leveled_profile': ResourceProfile(...),

    # Feasibility
    'feasible': True                 # Meets resource constraint
}
```

---

## Advanced Usage

### Custom Resource Profiles

```python
from src.pmhelper.core.resource_leveling import ResourceProfile

# Create custom schedule
schedule = {'A': 0, 'B': 5, 'C': 6}

# Calculate profile
profile = ResourceProfile(schedule, activities)

# Analyze
print(f"Peak: {profile.get_peak_usage()}")
print(f"Moment: {profile.calculate_moment()}")
print(f"Utilization: {profile.get_utilization(10.0):.1f}%")

# Check feasibility
if profile.is_feasible(10.0):
    print("✓ Schedule is feasible")
else:
    overutilized = profile.get_overutilized_periods(10.0)
    print(f"✗ Overutilized at periods: {overutilized}")
```

### Comparing Multiple Methods

```python
methods = ['minimum_moment', 'burgess']
results = {}

for method in methods:
    leveler = ResourceLevelingFactory.create(method, activities, 10.0)
    results[method] = leveler.level()

# Find best
best_method = max(results.keys(),
                  key=lambda m: results[m]['improvement_pct'])
print(f"Best method: {best_method}")
print(f"Improvement: {results[best_method]['improvement_pct']:.1f}%")
```

### Sensitivity Analysis

```python
# Test different resource limits
limits = [8, 10, 12, 15]
results = []

for limit in limits:
    leveler = MinimumMomentLeveling(activities, resource_limit=limit)
    result = leveler.level()
    results.append({
        'limit': limit,
        'feasible': result['feasible'],
        'peak': result['peak_usage_leveled'],
        'improvement': result['improvement_pct']
    })

# Analyze
import pandas as pd
df = pd.DataFrame(results)
print(df)
```

---

## Troubleshooting

### No Improvement Achieved

**Problem:** `improvement_pct` is 0%

**Possible Causes:**

1. All activities are critical (no float)
2. Schedule is already optimal
3. Resource limit is too tight

**Solutions:**

```python
# Check for non-critical activities
non_critical = [act for act in activities if act.float > 0]
print(f"Non-critical activities: {len(non_critical)}")

# If none, leveling can't help
if len(non_critical) == 0:
    print("All activities critical - cannot level")
```

### Resource Limit Exceeded

**Problem:** `feasible` is False

**Possible Causes:**

1. Resource limit too low for the project
2. Critical path has high resource demand

**Solutions:**

```python
# Check original profile
profile = ResourceProfile(early_start_schedule, activities)
min_required = profile.get_peak_usage()
print(f"Minimum required resources: {min_required}")

# Increase limit or crash activities
```

### Slow Convergence

**Problem:** Too many iterations

**Solutions:**

```python
# Reduce max iterations
result = leveler.level(max_iterations=100)

# Or use different algorithm
leveler = BurgessLeveling(activities)  # Often faster
```

---

## Best Practices

### 1. Always Start with CPM Analysis

```python
# ✓ Good
cpm.analyze(data)
activities = activities_from_cpm(cpm)
leveler = MinimumMomentLeveling(activities)

# ✗ Bad
# Creating activities manually without CPM
```

### 2. Visualize Results

```python
# ✓ Good - Always visualize to verify
fig = plot_resource_profile(original_df, leveled_df, limit)
fig.savefig('result.png')

# Review the plot before accepting results
```

### 3. Check Feasibility

```python
# ✓ Good
if not result['feasible']:
    print("Warning: Schedule exceeds resource limit!")
    # Take action
```

### 4. Document Assumptions

```python
# ✓ Good
"""
Resource leveling with assumptions:
- Resource limit: 10 workers
- All activities can use any worker
- No minimum crew sizes
- No multi-skilled requirements
"""
```

### 5. Compare Methods

```python
# ✓ Good - Try both and compare
mm_result = MinimumMomentLeveling(activities).level()
burgess_result = BurgessLeveling(activities).level()

# Choose based on objectives
```

---

## Real-World Example

### Construction Project

```python
# Project: Office building construction
activities = [
    Activity('Excavation', 3, 8.0, 0, 3, 0, 3, 0, [], ['Foundation']),
    Activity('Foundation', 5, 12.0, 3, 8, 3, 8, 0, ['Excavation'], ['Framing']),
    Activity('Plumbing', 4, 6.0, 3, 7, 5, 9, 2, ['Excavation'], ['Interior']),
    Activity('Electrical', 3, 5.0, 3, 6, 6, 9, 3, ['Excavation'], ['Interior']),
    Activity('Framing', 6, 10.0, 8, 14, 8, 14, 0, ['Foundation'], ['Roofing']),
    Activity('Roofing', 4, 7.0, 14, 18, 14, 18, 0, ['Framing'], ['Finishing']),
    Activity('Interior', 5, 8.0, 8, 13, 9, 14, 1, ['Plumbing', 'Electrical'], ['Finishing']),
    Activity('Finishing', 3, 6.0, 18, 21, 18, 21, 0, ['Roofing', 'Interior'], [])
]

# Resource constraint: 15 workers max
leveler = MinimumMomentLeveling(activities, resource_limit=15.0)
result = leveler.level()

# Generate report
report = generate_leveling_report(result, "Construction Project")
print(report)

# Visualize
original_df = result['original_profile'].to_dataframe()
leveled_df = result['leveled_profile'].to_dataframe()
fig = plot_resource_profile(original_df, leveled_df, 15.0)
fig.savefig('construction_leveling.png')
```

---

## API Reference Summary

### Classes

- `Activity` - Activity data structure
- `ResourceProfile` - Resource usage analyzer
- `MinimumMomentLeveling` - Minimum moment algorithm
- `BurgessLeveling` - Burgess algorithm
- `ResourceLevelingFactory` - Algorithm factory

### Functions

- `activities_from_cpm()` - Convert CPM to activities
- `plot_resource_profile()` - Resource profile visualization
- `plot_leveling_metrics()` - Metrics dashboard
- `plot_gantt_comparison()` - Gantt comparison
- `generate_leveling_report()` - Text report
- `export_leveling_results()` - Data export

---

## See Also

- [COST_OPTIMIZATION_GUIDE.md](COST_OPTIMIZATION_GUIDE.md) - Time-cost trade-offs
- [RESOURCE_LEVELING_IMPLEMENTATION_SUMMARY.md](../reports/RESOURCE_LEVELING_IMPLEMENTATION_SUMMARY.md) - Technical details
- [resource_leveling_demo.py](../../examples/resource_leveling_demo.py) - Complete example

---

## Support

For issues or questions:

- GitHub Issues: https://github.com/seifouda/PMhelper/issues
- See `resource_leveling_demo.py` for working examples

---

**Version:** 1.1.0  
**Last Updated:** December 20, 2025  
**Status:** Production Ready ✅
