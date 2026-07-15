# Cost Optimization User Guide - Phase 4 Complete

**PMHelper Cost Optimization Module** - Comprehensive user documentation for GUI, CLI, and API usage.

Version 1.0 | Updated: 2024

---

## Quick Start

**GUI:** Analysis → Cost Optimization tab → Choose panel (Time-Cost, Resource Leveling, or Multi-Objective)

**CLI:** `python -m pmhelper.cli.optimization_cli <command> project.csv [options]`

**API:** `from pmhelper.core import cost_optimization, resource_leveling, multi_objective`

---

## Part 1: GUI User Guide

### Accessing Cost Optimization Features

1. Launch PMHelper: `python launch_app.py`
2. Load a project (File → Open)
3. Navigate to **Cost Optimization** tab
4. Or use menu: Analysis → Cost Optimization

### Panel 1: Time-Cost Optimization

**Purpose:** Find the optimal project duration that minimizes total cost by balancing direct costs (activities) against indirect costs (overhead).

#### Input Fields

| Field           | Description                            | Default | Units |
| --------------- | -------------------------------------- | ------- | ----- |
| Facilities Cost | Daily cost for facilities (rent, etc.) | 500     | $/day |
| Equipment Cost  | Daily equipment rental/depreciation    | 300     | $/day |
| Utilities Cost  | Daily utilities (power, water, etc.)   | 200     | $/day |
| Overhead Cost   | Daily administrative overhead          | 1000    | $/day |

#### How to Use

1. Enter indirect cost rates for your project
2. Click **"Optimize"** button
3. Review results in text area:
   - Optimal duration
   - Cost breakdown (direct vs. indirect)
   - Recommended crashing sequence
4. View visualization showing:
   - Blue line: Direct costs (decreases with crashing)
   - Orange line: Indirect costs (increases with duration)
   - Green line: Total costs (U-shaped curve)
   - Red marker: Optimal point

#### Example Results

```
=== Time-Cost Optimization Results ===

Normal Project Duration: 14 days
Normal Total Cost: $48,000

Optimal Duration: 11 days
Optimal Total Cost: $42,200

Savings: $5,800 (12.1%)

Recommended Crashing:
  • Crash Activity B by 2 days (cost: +$600/day)
  • Crash Activity D by 1 day (cost: +$400/day)

Cost Breakdown at Optimal:
  Direct Cost: $26,200 (62%)
  Indirect Cost: $16,000 (38%)
```

### Panel 2: Resource Leveling

**Purpose:** Smooth resource usage across the project timeline to reduce peaks and improve resource utilization.

#### Input Fields

| Field           | Description                         | Options                               |
| --------------- | ----------------------------------- | ------------------------------------- |
| Leveling Method | Algorithm to use                    | Minimum Moment (recommended), Burgess |
| Resource Limit  | Max resources per period (optional) | Leave blank for no limit              |

#### Leveling Methods

- **Minimum Moment:** Minimizes resource usage peaks - best for reducing maximum resource requirements
- **Burgess:** Minimizes sum of squared usage - best for overall smoothness

#### How to Use

1. Select leveling method (Minimum Moment recommended for most cases)
2. Optionally enter resource limit (e.g., "6" if you can't exceed 6 workers/day)
3. Click **"Optimize"** button
4. Review metrics:
   - Peak reduction
   - Variance improvement
   - Activities shifted
5. Compare before/after charts

#### Example Results

```
=== Resource Leveling Results ===

Method: Minimum Moment
Resource Limit: None

Before Leveling:
  Peak:      9 workers
  Average:   5.2 workers
  Variance:  8.4

After Leveling:
  Peak:      7 workers (-22%)
  Average:   5.2 workers (0%)
  Variance:  3.1 (-63%)

Activities Shifted:
  • Activity C: Delayed 2 days (within float)
  • Activity F: Delayed 1 day (within float)

Project Duration: Unchanged (14 days)
```

### Panel 3: Multi-Objective Optimization

**Purpose:** Find trade-off solutions when optimizing multiple conflicting objectives simultaneously.

#### Input Fields

| Field               | Description                      | Default   |
| ------------------- | -------------------------------- | --------- |
| ☑ Minimize Duration | Include duration objective       | Checked   |
| ☑ Minimize Cost     | Include cost objective           | Checked   |
| ☐ Maximize NPV      | Include NPV objective            | Unchecked |
| Discount Rate       | Annual rate for NPV (if enabled) | 0.1 (10%) |
| Sample Size         | Number of solutions to generate  | 100       |

#### How to Use

1. Select at least 2 objectives (checkboxes)
2. If NPV selected, enter discount rate (0.05 = 5%, 0.10 = 10%, etc.)
3. Set sample size (more = better frontier, slower computation):
   - 50: Quick preview
   - 100: Normal quality
   - 500+: High quality
4. Click **"Optimize"** button
5. View Pareto frontier:
   - 2D plot for 2 objectives
   - 3D plot for 3 objectives
   - Blue dots: All sampled solutions
   - Red dots: Pareto-optimal (non-dominated) solutions
6. Review solution summary showing extremes and balanced options

#### Example Results

```
=== Multi-Objective Optimization Results ===

Objectives: Duration, Cost, NPV (discount rate: 10%)
Pareto Solutions Found: 18

Extreme Solutions:

1. Fastest (Duration-Optimal):
   Duration:  9 days
   Cost:      $55,000
   NPV:       $175,000

2. Cheapest (Cost-Optimal):
   Duration:  16 days
   Cost:      $42,000
   NPV:       $198,000

3. Best ROI (NPV-Optimal):
   Duration:  13 days
   Cost:      $46,500
   NPV:       $210,000

Recommended Balanced Solution (#8):
   Duration:  12 days
   Cost:      $48,200
   NPV:       $205,000

   Trade-offs vs. Extremes:
   • 33% longer than fastest, but $6,800 cheaper
   • 25% shorter than cheapest, $6,200 more expensive
   • Similar NPV to best ROI, faster delivery
```

---

## Part 2: CLI User Guide

Every command takes its project file via **`--input`** (not positionally), and
each writes its outputs under the base path given by `--output`.

```bash
python -m pmhelper.cli.optimization_cli <command> --input <project_file> [options]
```

Available commands: `time-cost`, `resources`, `npv`, `pareto`.
Run `--help` on any of them to see its exact flags:

```bash
python -m pmhelper.cli.optimization_cli --help
python -m pmhelper.cli.optimization_cli time-cost --help
```

### Command 1: time-cost

**Purpose:** Generate a time-cost optimization curve and find the optimal duration.

#### Usage

```bash
python -m pmhelper.cli.optimization_cli time-cost \
    --input project.csv \
    --indirect indirect_costs.json \
    --output timecost_results
```

#### Options

```
options:
  --input INPUT         Input project file (CSV/Excel)   [required]
  --indirect INDIRECT   Indirect costs JSON file         [required]
  --output OUTPUT       Output base path
```

`--indirect` is a **path to a JSON file**, not a number. The file maps cost
categories to their **daily rate**:

```json
{
  "facilities": 200.0,
  "equipment": 150.0,
  "utilities": 50.0,
  "overhead": 100.0
}
```

The category names are free-form — they are summed into a single daily indirect
rate — so a simplified model is just `{"indirect": 500.0}`.

#### Output Files

With `--output timecost_results`:

| File | Contents |
|---|---|
| `timecost_results_curve.png` | Direct / indirect / total cost curves with the optimum marked |
| `timecost_results_report.txt` | Text summary of the optimisation |
| `timecost_results.csv` | Curve data |
| `timecost_results.json` | Curve data + optimal point |

---

### Command 2: resources

**Purpose:** Level resource usage across the schedule.

#### Usage

```bash
# Unconstrained (minimise the resource moment)
python -m pmhelper.cli.optimization_cli resources \
    --input project.csv \
    --method minimum_moment \
    --output leveling_results

# Constrained to a resource limit
python -m pmhelper.cli.optimization_cli resources \
    --input project.csv \
    --method burgess \
    --limit 8 \
    --output leveling_constrained
```

#### Options

```
options:
  --input INPUT                     Input project file (CSV/Excel)   [required]
  --method {minimum_moment,burgess} Leveling method
  --limit LIMIT                     Resource limit (optional)
  --output OUTPUT                   Output base path
```

Your project file needs a `resource_demand` column for this command to be
meaningful (see Part 4).

#### Output Files

| File | Contents |
|---|---|
| `{base}_profile.png` | Before/after resource histograms |
| `{base}_report.txt` | Peak usage, moment, improvement %, and which activities moved |
| `{base}_schedule.csv` | The leveled start time per activity |

---

### Command 3: npv

**Purpose:** Maximise project NPV by scheduling cash flows.

#### Usage

```bash
python -m pmhelper.cli.optimization_cli npv \
    --input project.csv \
    --cash-flows cash_flows.json \
    --discount-rate 0.1 \
    --output npv_results

# With sensitivity analysis across discount rates
python -m pmhelper.cli.optimization_cli npv \
    --input project.csv \
    --cash-flows cash_flows.json \
    --sensitivity \
    --output npv_results
```

#### Options

```
options:
  --input INPUT                  Input project file (CSV/Excel)   [required]
  --cash-flows CASH_FLOWS        Cash flows JSON file             [required]
  --discount-rate DISCOUNT_RATE  Discount rate (default: 0.10)
  --sensitivity                  Run sensitivity analysis
  --output OUTPUT                Output base path
```

`--cash-flows` is a **required** JSON file mapping each activity id to its cash
flow:

```json
{
  "A": 5000.0,
  "B": -2000.0,
  "C": 8000.0
}
```

#### Output Files

| File | Contents |
|---|---|
| `{base}_schedule.csv` | NPV-optimal start times |
| `{base}_cashflows.csv` | Discounted cash flows per activity |
| `{base}_sensitivity.csv` / `.png` | Only with `--sensitivity` |

---

### Command 4: pareto

**Purpose:** Multi-objective optimisation — find the Pareto frontier.

#### Usage

```bash
python -m pmhelper.cli.optimization_cli pareto \
    --input project.csv \
    --objectives duration,cost \
    --samples 100 \
    --output pareto_results
```

#### Options

```
options:
  --input INPUT            Input project file (CSV/Excel)   [required]
  --objectives OBJECTIVES  Comma-separated objectives        [required]
  --samples SAMPLES        Number of candidate schedules (default: 100)
  --output OUTPUT          Output base path
```

`--objectives` takes **one comma-separated string** — `duration,cost` — not
space-separated values. There is no `--discount-rate` on this command.

#### Output Files

| File | Contents |
|---|---|
| `{base}_pareto.png` | The Pareto frontier plot |
| `{base}_report.txt` | Text summary of the non-dominated solutions |
| `{base}.csv` / `{base}.json` | The solution set |

---

## Part 3: API Reference

### Time-Cost Optimization API

```python
from pmhelper.core.cost_optimization import TimeCostOptimizer
from pmhelper.core.cpm_analyzer import CPMAnalyzer

# Load project
analyzer = CPMAnalyzer()
analyzer.load_from_csv('project.csv')
analyzer.calculate()

# Create optimizer
optimizer = TimeCostOptimizer(analyzer)

# Generate time-cost curve
indirect_costs = {
    'facilities': 500,
    'equipment': 300,
    'utilities': 200,
    'overhead': 1000,
    'total': 2000  # sum of above
}

curve = optimizer.generate_time_cost_curve(indirect_costs)

# Find optimal
optimal = optimizer.find_optimal_duration(curve)

print(f"Optimal duration: {optimal['duration']} days")
print(f"Optimal cost: ${optimal['cost']:,.0f}")
```

#### TimeCostOptimizer Class

**Constructor:**

- `TimeCostOptimizer(cpm_analyzer)` - Create optimizer from CPM analyzer

**Methods:**

- `generate_time_cost_curve(indirect_costs: dict) -> pd.DataFrame`
  - Returns DataFrame with columns: [duration, direct_cost, indirect_cost, total_cost]
- `find_optimal_duration(curve: pd.DataFrame) -> dict`

  - Returns dict with keys: [duration, cost, direct_cost, indirect_cost, savings]

- `get_crashing_sequence() -> list[(activity, amount)]`
  - Returns sequence of activities to crash

### Resource Leveling API

```python
from pmhelper.core.resource_leveling import ResourceLevelingFactory
from pmhelper.core.cpm_analyzer import CPMAnalyzer

# Load project
analyzer = CPMAnalyzer()
analyzer.load_from_csv('project.csv')
analyzer.calculate()

# Create leveler
leveler = ResourceLevelingFactory.create_leveler(
    method='minimum_moment',  # or 'burgess'
    cpm_analyzer=analyzer
)

# Level resources
result = leveler.level_resources(resource_limit=None)  # or set limit

# Access results
schedule = result['schedule']
metrics = result['metrics']

print(f"Peak reduced: {metrics['before']['peak']} → {metrics['after']['peak']}")
print(f"Variance reduced: {metrics['before']['variance']:.1f} → {metrics['after']['variance']:.1f}")
```

#### ResourceLevelingFactory Class

**Methods:**

- `create_leveler(method: str, cpm_analyzer) -> BaseLeveler`
  - method: 'minimum_moment' or 'burgess'
  - Returns leveler instance

#### BaseLeveler Interface

**Methods:**

- `level_resources(resource_limit: int = None) -> dict`
  - Returns dict with keys: [schedule, metrics, profile]
- `get_resource_profile(schedule: dict) -> dict`
  - Returns resource usage by period

### Multi-Objective Optimization API

```python
from pmhelper.core.multi_objective import MultiObjectiveOptimizer
from pmhelper.core.cpm_analyzer import CPMAnalyzer

# Load project
analyzer = CPMAnalyzer()
analyzer.load_from_csv('project.csv')
analyzer.calculate()

# Create optimizer
optimizer = MultiObjectiveOptimizer(analyzer)

# Generate Pareto frontier
frontier = optimizer.generate_pareto_frontier(
    objectives=['duration', 'cost', 'npv'],
    num_samples=200,
    discount_rate=0.1
)

# Find best solutions
fastest = frontier[frontier['duration'] == frontier['duration'].min()].iloc[0]
cheapest = frontier[frontier['cost'] == frontier['cost'].min()].iloc[0]
best_npv = frontier[frontier['npv'] == frontier['npv'].max()].iloc[0]

print(f"Fastest: {fastest['duration']} days, ${fastest['cost']:,.0f}")
print(f"Cheapest: {cheapest['duration']} days, ${cheapest['cost']:,.0f}")
print(f"Best NPV: {best_npv['duration']} days, NPV ${best_npv['npv']:,.0f}")
```

#### MultiObjectiveOptimizer Class

**Constructor:**

- `MultiObjectiveOptimizer(cpm_analyzer)` - Create optimizer

**Methods:**

- `generate_pareto_frontier(objectives: list, num_samples: int, discount_rate: float = 0.1) -> pd.DataFrame`
  - objectives: list of 'duration', 'cost', 'npv'
  - Returns DataFrame with Pareto-optimal solutions
- `evaluate_solution(schedule: dict, objectives: list) -> dict`
  - Evaluates a schedule against objectives
- `is_pareto_optimal(solution: dict, population: list) -> bool`
  - Checks Pareto optimality

---

## Part 4: Project File Format

Your project CSV must include these columns for cost optimization:

```csv
Activity,Duration,Predecessors,NormalCost,CrashCost,CrashTime,Resources
A,5,,5000,7000,3,Worker:2;Equipment:1
B,3,A,3000,4200,2,Worker:3
C,4,A,4000,5600,3,Worker:1;Equipment:2
D,2,"B,C",2000,2800,1,Worker:2
```

### Required Columns

- **Activity:** Unique activity ID
- **Duration:** Normal duration in days
- **Predecessors:** Comma-separated list (empty if none)

### Optional Columns (for specific features)

- **NormalCost:** Cost at normal duration (for time-cost)
- **CrashCost:** Cost when fully crashed (for time-cost)
- **CrashTime:** Minimum achievable duration (for time-cost)
- **Resources:** Resource requirements (for leveling) - Format: `Type:Amount;Type:Amount`

---

## Part 5: Troubleshooting

### Common Issues

**Q: "No crashable activities" error**

- Check that CrashTime < Duration for at least some activities
- Ensure CrashCost > NormalCost
- Verify CSV has required columns

**Q: Resource leveling has no effect**

- Project may be fully critical (no float)
- Try a different method (Burgess vs. Minimum Moment)
- Check if resource limit is too restrictive

**Q: Pareto frontier is empty or has only 1 point**

- Increase sample size (try 500+)
- Verify objectives conflict (if all align, only 1 optimal)
- Check that project has crashing flexibility

**Q: CLI command not recognized**

- Ensure you're in project root directory
- Use full module path: `python -m pmhelper.cli.optimization_cli`
- Check Python path includes src folder

**Q: GUI freezes during optimization**

- Large projects with high sample sizes can be slow
- Reduce sample size in multi-objective panel
- Use CLI for large batch optimizations
- Consider breaking project into phases

### Performance Tips

1. **Large Projects (>50 activities):**

   - Reduce multi-objective sample size to 50-100
   - Use CLI for faster batch processing
   - Close unused tabs in GUI

2. **Slow Visualizations:**

   - Reduce plot resolution
   - Use PNG instead of interactive plots
   - Clear previous results before new optimization

3. **Memory Issues:**
   - Restart application between large runs
   - Use generator-based approaches in API
   - Process projects in batches

---

## Part 6: Best Practices

### When to Use Each Feature

**Time-Cost Optimization:**

- Budget constraints require cost minimization
- Deadline flexibility exists
- Crashing costs are known
- Trade-off between speed and cost matters

**Resource Leveling:**

- Resource availability is limited
- Hiring/firing costs are high
- Smoother resource usage is desired
- Project has non-critical activities (float exists)

**Multi-Objective:**

- Multiple conflicting goals (speed vs. cost vs. ROI)
- Need to present trade-off options to stakeholders
- Decision involves multiple criteria
- Want to explore solution space

### Typical Workflow

1. **Initial Analysis**
   - Load project and run CPM
   - Review critical path and float
2. **Cost Optimization**
   - Start with time-cost to find cost-optimal duration
   - Note recommended crashing sequence
3. **Resource Analysis**
   - Check resource profile for peaks
   - If needed, apply resource leveling
   - Verify duration impact is acceptable
4. **Trade-Off Exploration**
   - Use multi-objective to explore alternatives
   - Present Pareto solutions to stakeholders
   - Choose solution based on priorities
5. **Implementation**
   - Export chosen schedule
   - Track actual vs. planned
   - Adjust as project progresses

---

## Summary

The Cost Optimization module provides three powerful tools:

1. **Time-Cost:** Minimize total cost by finding optimal duration
2. **Resources:** Smooth resource usage across timeline
3. **Multi-Objective:** Explore trade-offs between conflicting goals

All features are available via **GUI** (user-friendly), **CLI** (automation), and **API** (integration).

For examples, see the `examples/` folder. For technical details, see `docs/guides/COST_OPTIMIZATION_GUIDE.md`.

---

**Version:** 1.0.0 (Phase 4 Complete)  
**Last Updated:** 2024  
**Support:** Check documentation or raise an issue
