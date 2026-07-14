# Multi-Objective Optimization & NPV Guide

## Overview

The PMHelper Multi-Objective Optimization module provides advanced project scheduling capabilities that consider multiple competing objectives simultaneously. This includes Net Present Value (NPV) optimization, Pareto frontier analysis, and trade-off evaluation.

## Features

### 1. NPV Optimization

- **Time value of money calculations** with configurable discount rates
- **Automatic schedule optimization** to maximize project NPV
- **Cash flow scheduling** with activity completion milestones
- **Discount rate sensitivity analysis**

### 2. Multi-Objective Optimization

- **Pareto dominance checking** to identify non-dominated solutions
- **Pareto frontier generation** showing optimal trade-offs
- **Multiple objective support**: duration, cost, NPV, and custom objectives
- **Schedule generation** with sampling and heuristic strategies

### 3. Visualizations

- **2D and 3D Pareto frontier plots**
- **NPV sensitivity charts**
- **Trade-off analysis** with marginal rates of substitution
- **Parallel coordinates** for multi-objective comparison

## Quick Start

### Basic NPV Optimization

```python
from pmhelper.core.npv_optimization import NPVOptimizer, CashFlowActivity

# Define activities with cash flows
activities = [
    CashFlowActivity(
        id='Design',
        duration=5,
        cash_flow=20000,  # Revenue at completion
        es=0, ef=5, ls=0, lf=5,
        float=0,
        predecessors=[],
        successors=['Development']
    ),
    CashFlowActivity(
        id='Development',
        duration=10,
        cash_flow=-15000,  # Cost
        es=5, ef=15, ls=5, lf=15,
        float=0,
        predecessors=['Design'],
        successors=['Testing']
    )
]

# Create optimizer with 10% discount rate
optimizer = NPVOptimizer(activities, discount_rate=0.10)

# Optimize schedule
result = optimizer.maximize_npv()

print(f"NPV Improvement: ${result['improvement']:,.2f}")
print(f"Optimal NPV: ${result['optimal_npv']:,.2f}")
```

### Sensitivity Analysis

```python
# Test different discount rates
rates = [0.05, 0.10, 0.15, 0.20]
sensitivity = optimizer.sensitivity_analysis(rates)

print(sensitivity)

# Visualize sensitivity
from pmhelper.core.multi_objective_visualizations import plot_npv_sensitivity
fig = plot_npv_sensitivity(sensitivity, save_path='sensitivity.png')
```

### Multi-Objective Optimization

```python
from pmhelper.core.multi_objective import (
    MultiObjectiveOptimizer, ScheduleGenerator
)

# Define objective functions
def calculate_duration(schedule):
    # Return project duration
    return max_completion_time

def calculate_cost(schedule):
    # Return total cost
    return total_cost

def calculate_npv(schedule):
    # Return NPV
    return net_present_value

objectives = {
    'duration': calculate_duration,
    'cost': calculate_cost,
    'npv': lambda s: -calculate_npv(s)  # Negative to minimize
}

# Create optimizer
mo_optimizer = MultiObjectiveOptimizer(objectives)

# Generate candidate schedules
schedules = ScheduleGenerator.generate_sampled(activities, num_samples=100)

# Find Pareto frontier
frontier = mo_optimizer.generate_solutions_grid(
    schedules,
    minimize_objectives=['duration', 'cost', 'npv']
)

print(f"Pareto frontier: {len(frontier)} solutions")
```

### Visualize Pareto Frontier

```python
from pmhelper.core.multi_objective_visualizations import plot_pareto_frontier_2d

# Get solution summary
solutions_df = mo_optimizer.get_solution_summary()

# Plot 2D frontier
fig = plot_pareto_frontier_2d(
    solutions_df,
    obj1='duration',
    obj2='cost',
    minimize_obj1=True,
    minimize_obj2=True,
    save_path='pareto_frontier.png'
)
```

## Core Concepts

### Net Present Value (NPV)

NPV accounts for the time value of money by discounting future cash flows to present value:

$$NPV = \sum_{i=1}^{n} \frac{CF_i}{(1 + r)^{t_i}}$$

Where:

- $CF_i$ = Cash flow for activity $i$
- $r$ = Discount rate
- $t_i$ = Time of cash flow (activity completion)

**Optimization Strategy:**

- Activities with **positive cash flows** are scheduled **early** (less discounting)
- Activities with **negative cash flows** are scheduled **late** (more discounting reduces impact)

### Pareto Dominance

A solution **dominates** another if it is:

- At least as good in all objectives
- Strictly better in at least one objective

The **Pareto frontier** contains all non-dominated solutions - the optimal trade-off curve.

### Schedule Generation

Three strategies for generating candidate schedules:

1. **All Feasible**: Enumerates all possible schedules within activity float ranges

   ```python
   schedules = ScheduleGenerator.generate_all_feasible(activities)
   ```

2. **Sampling**: Random sampling for large search spaces

   ```python
   schedules = ScheduleGenerator.generate_sampled(activities, num_samples=1000)
   ```

3. **Heuristic**: Strategic schedules (early, late, middle, cash-flow-based)
   ```python
   schedules = ScheduleGenerator.generate_heuristic(
       activities,
       strategies=['early', 'late', 'cash_flow_early']
   )
   ```

## Integration with CPM

Convert CPM analysis results to cash flow activities:

```python
from pmhelper.core.npv_optimization import activities_from_cpm_with_cashflows
from pmhelper.analysis.cpm_analyzer import CPMAnalyzer

# Perform CPM analysis
cpm = CPMAnalyzer()
cpm.analyze(activity_data)

# Define cash flows for activities
cash_flows = {
    'Design': 20000,
    'Development': -15000,
    'Testing': 25000
}

# Convert to cash flow activities
activities = activities_from_cpm_with_cashflows(cpm, cash_flows)

# Optimize
optimizer = NPVOptimizer(activities, discount_rate=0.10)
result = optimizer.maximize_npv()
```

## Advanced Usage

### Custom Objectives

Define custom objective functions for specific project needs:

```python
def quality_metric(schedule):
    """Custom quality metric based on testing duration"""
    testing_start = schedule.get('Testing', 0)
    testing_duration = get_activity('Testing').duration
    # More testing time = higher quality
    return -(testing_duration + slack_time)  # Negative to minimize

objectives = {
    'duration': calculate_duration,
    'cost': calculate_cost,
    'quality': quality_metric
}
```

### Trade-off Analysis

Analyze marginal rates of substitution between objectives:

```python
# Find trade-offs between duration and cost
tradeoffs = mo_optimizer.find_tradeoffs('duration', 'cost')

print(tradeoffs[['delta_duration', 'delta_cost', 'marginal_rate']])

# Visualize
from pmhelper.core.multi_objective_visualizations import plot_tradeoff_analysis
fig = plot_tradeoff_analysis(tradeoffs, 'duration', 'cost')
```

### Export Results

Export Pareto frontier solutions in multiple formats:

```python
from pmhelper.core.multi_objective_visualizations import export_pareto_solutions

pareto_df = mo_optimizer.get_pareto_summary()
pareto_schedules = [sol.schedule for sol in mo_optimizer.pareto_frontier]

export_pareto_solutions(
    pareto_df,
    pareto_schedules,
    base_path='results/pareto',
    formats=['csv', 'json', 'excel']
)
```

## API Reference

### NPVOptimizer

**Constructor:**

```python
NPVOptimizer(activities: List[CashFlowActivity], discount_rate: float = 0.10)
```

**Methods:**

- `calculate_npv(schedule)` - Calculate NPV for a schedule
- `maximize_npv(max_iterations=1000)` - Find optimal schedule
- `sensitivity_analysis(rate_range)` - Test different discount rates
- `get_cash_flow_schedule(schedule)` - Get detailed cash flow schedule

### MultiObjectiveOptimizer

**Constructor:**

```python
MultiObjectiveOptimizer(objective_functions: Dict[str, Callable])
```

**Methods:**

- `evaluate_solution(schedule)` - Evaluate schedule against all objectives
- `add_solution(solution)` - Add solution to set
- `dominates(sol1, sol2, minimize_objectives)` - Check Pareto dominance
- `compute_pareto_frontier(minimize_objectives)` - Find Pareto frontier
- `generate_solutions_grid(schedules, minimize_objectives)` - Evaluate and find frontier
- `get_solution_summary()` - Get DataFrame of all solutions
- `get_pareto_summary()` - Get DataFrame of Pareto solutions
- `find_tradeoffs(obj1, obj2)` - Analyze trade-offs between objectives

### ScheduleGenerator

**Static Methods:**

- `generate_all_feasible(activities, max_combinations)` - All feasible schedules
- `generate_sampled(activities, num_samples)` - Random sample
- `generate_heuristic(activities, strategies)` - Strategic schedules

### Visualization Functions

- `plot_pareto_frontier_2d(solutions_df, obj1, obj2, ...)` - 2D frontier plot
- `plot_pareto_frontier_3d(solutions_df, obj1, obj2, obj3, ...)` - 3D frontier plot
- `plot_npv_sensitivity(sensitivity_df, ...)` - NPV sensitivity chart
- `plot_tradeoff_analysis(tradeoffs_df, obj1, obj2, ...)` - Trade-off analysis
- `plot_objective_comparison(solutions_df, objectives, ...)` - Parallel coordinates
- `generate_multi_objective_report(optimizer, pareto_df, objectives, ...)` - Text report
- `export_pareto_solutions(pareto_df, schedules, base_path, formats)` - Export data

## Examples

See [multi_objective_demo.py](../../examples/multi_objective_demo.py) for a comprehensive demonstration including:

- NPV optimization with 11% improvement
- Discount rate sensitivity analysis (5% to 20%)
- Multi-objective Pareto frontier with 100 candidate solutions
- Complete visualization suite (7 plots)
- Data export in multiple formats

## Performance Considerations

### Schedule Generation Limits

For projects with many non-critical activities, the number of possible schedules grows exponentially:

- **Small projects** (< 10,000 schedules): Use `generate_all_feasible()`
- **Medium projects** (10,000 - 100,000): Use `generate_sampled()` with 1,000-5,000 samples
- **Large projects** (> 100,000): Use `generate_heuristic()` or limited sampling

### Optimization Iterations

NPV optimization typically converges quickly:

- **Simple projects**: 1-5 iterations
- **Complex projects**: 10-50 iterations
- Use `max_iterations` to limit computation time

## Troubleshooting

**Issue: NPV shows no improvement**

- Check if all activities are critical (float = 0)
- Verify cash flows are non-zero
- Try different discount rates

**Issue: Pareto frontier is empty**

- Ensure solutions were added: `len(optimizer.solutions) > 0`
- Check objective function errors
- Verify minimize_objectives list is correct

**Issue: Too many schedules generated**

- Use sampling instead of exhaustive generation
- Reduce `num_samples` parameter
- Use heuristic strategies

## References

- **Time Value of Money**: Standard finance concept for NPV calculations
- **Pareto Efficiency**: Multi-objective optimization theory
- **Project Scheduling**: CPM integration with financial objectives

## Version History

- **v1.1.0**: Added multi-objective optimization and NPV analysis
- Includes: NPVOptimizer, MultiObjectiveOptimizer, comprehensive visualizations
- Tests: 51/51 passing (25 NPV + 26 multi-objective)
