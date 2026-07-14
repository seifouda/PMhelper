# Risk Analysis Module - User Guide

## Overview

The Risk Analysis Module extends PMHelper's PERT capabilities with comprehensive project delay risk assessment, contingency planning, variance reduction strategies, and activity risk prioritization.

**Based on**: IM 738 Advanced Project Management - Risk Analysis methodologies

## Features

### 1. Delay Risk Analysis

Calculate the probability and expected cost of project delays using statistical methods.

**Key Metrics:**

- **Delay Probability**: P(T > contract_time) using normal distribution
- **Expected Delay**: Conditional expected delay period using truncated normal distribution
- **Risk Cost**: Expected financial impact of delay penalties
- **Z-Score**: Standardized measure of schedule tightness

**Example:**

```python
from src.pmhelper.core.pert_analyzer import PERTAnalyzer

# Run PERT analysis first
analyzer = PERTAnalyzer()
network, paths, activities = analyzer.analyze(activities_data)

# Calculate delay risk
risk = analyzer.analyze_delay_risk(
    contract_time=15.0,        # Contracted deadline
    penalty_rate=1000.0,       # $1000 per week delay
    max_penalty_percent=0.20   # Cap at 20% of contract value
)

print(f"Delay Probability: {risk['delay_probability']:.1%}")
print(f"Expected Delay: {risk['expected_delay']:.2f} weeks")
print(f"Risk Cost: ${risk['risk_cost']:,.2f}")
```

### 2. Contingency Planning

Estimate time buffers and contingency budgets for different confidence levels.

**Key Metrics:**

- **Time Buffer**: Additional time needed for desired confidence level
- **Buffer Percentage**: Buffer as % of expected duration
- **Completion Time**: Expected duration + buffer
- **Contingency Cost**: Cost of buffer period

**Example:**

```python
# Estimate contingency for 95% confidence
contingency = analyzer.estimate_contingency(
    confidence_level=0.95,     # 95% confidence
    daily_cost_rate=5000.0     # $5000 per day
)

print(f"Time Buffer: {contingency['time_buffer']:.2f} weeks")
print(f"Completion Time: {contingency['completion_time']:.2f} weeks")
print(f"Contingency Cost: ${contingency['contingency_cost']:,.2f}")
print(f"Recommendation: {contingency['recommendation']}")
```

**Confidence Level Guidelines:**

- **80%**: Low-risk projects, internal deadlines
- **90%**: Standard projects, moderate external commitments
- **95%**: Important projects, firm external deadlines
- **99%**: Critical projects, contractual commitments

### 3. Variance Reduction Strategies

Compare strategies for reducing project risk through time and/or variance reduction.

**Three Strategies:**

- **Strategy A**: Reduce expected time (keep variance constant)
- **Strategy B**: Reduce variance (keep expected time constant)
- **Mixed Strategy**: Optimal combination of both

**Example:**

```python
strategies = analyzer.analyze_variance_reduction_strategies(
    contract_time=15.0,
    penalty_rate=1000.0,
    time_reduction_cost=3000.0,      # Cost per week reduced
    variance_reduction_cost=2000.0,   # Cost per variance unit reduced
    max_budget=30000.0                # Maximum investment
)

# View best strategy
best = strategies['best_strategy']
print(f"Recommended: {best['name']}")
print(f"Investment: ${best['investment']:,.2f}")
print(f"Benefit: ${best['benefit']:,.2f}")
print(f"Net Benefit: ${best['net_benefit']:,.2f}")
print(f"ROI: {best['roi']:.1f}%")
```

**When to Use:**

- **Strategy A**: When schedule is tight, need to finish earlier
- **Strategy B**: When uncertainty is high, need more predictability
- **Mixed**: When budget allows, optimize combination

### 4. Activity Risk Prioritization

Identify and prioritize high-risk activities for focused mitigation.

**Risk Score Components:**

- **Criticality** (40%): On critical path (0 or 1)
- **Cruciality** (30%): Variance contribution to project
- **Schedule Sensitivity** (20%): Inverse of total float
- **Uncertainty** (10%): Coefficient of variation (σ/μ)

**Example:**

```python
# Get risk scores for all activities
risk_scores = analyzer.prioritize_activity_risks()

# View top 5 risks
print(risk_scores.head(5)[['activity_id', 'risk_score', 'recommendation']])

# Generate mitigation plan
plan = analyzer.generate_risk_mitigation_plan()

print(f"High Priority: {len(plan['high_priority'])} activities")
print(f"Critical Path Risks: {len(plan['critical_path_risks'])} activities")
```

## Complete Workflow Example

```python
from src.pmhelper.core.pert_analyzer import PERTAnalyzer

# Step 1: Load and analyze project
activities = [
    {'id': 'A', 'predecessors': '', 'optimistic': 2, 'most_likely': 3, 'pessimistic': 4},
    {'id': 'B', 'predecessors': 'A', 'optimistic': 3, 'most_likely': 4, 'pessimistic': 5},
    # ... more activities
]

analyzer = PERTAnalyzer()
network, paths, activities = analyzer.analyze(activities)

# Step 2: Assess delay risk
risk = analyzer.analyze_delay_risk(contract_time=15.0, penalty_rate=1000.0)
print(f"Risk Assessment: {risk['delay_probability']:.1%} chance of delay")

# Step 3: Plan contingency
contingency = analyzer.estimate_contingency(confidence_level=0.95)
print(f"Recommended Buffer: {contingency['time_buffer']:.2f} weeks")

# Step 4: Evaluate mitigation strategies
strategies = analyzer.analyze_variance_reduction_strategies(
    contract_time=15.0,
    penalty_rate=1000.0,
    time_reduction_cost=3000.0,
    variance_reduction_cost=2000.0,
    max_budget=30000.0
)
print(f"Best Strategy: {strategies['best_strategy']['name']}")

# Step 5: Prioritize activities for mitigation
risk_scores = analyzer.prioritize_activity_risks()
plan = analyzer.generate_risk_mitigation_plan()
print(f"Focus on {len(plan['high_priority'])} high-priority activities")
```

## Sample Datasets

Located in `assets/risk_examples/`:

1. **delay_analysis_simple.csv**: Basic project for delay risk calculation
2. **contingency_planning.csv**: Project for buffer estimation
3. **variance_reduction.csv**: Project with cost data for strategy comparison

## Mathematical Formulas

### Delay Probability

```
P(T > Tc) = 1 - Φ((Tc - μ) / σ)
```

where Φ is the standard normal CDF

### Expected Delay (Truncated Normal)

```
E[T | T > Tc] = μ + σ × φ(z) / (1 - Φ(z))
```

where z = (Tc - μ) / σ, φ is PDF, Φ is CDF

### Risk Cost

```
Risk Cost = P(delay) × E[delay | delay occurs] × penalty_rate
```

### Contingency Buffer

```
Buffer = Zα × σ
```

where Zα is the z-score for confidence level α

### Activity Risk Score

```
Risk Score = 0.40×Criticality + 0.30×Cruciality +
             0.20×Schedule_Sensitivity + 0.10×Uncertainty
```

## Best Practices

### 1. When to Use Each Feature

- **Delay Risk Analysis**: Before committing to contract deadlines
- **Contingency Planning**: During project planning phase
- **Variance Reduction**: When facing tight deadlines with budget flexibility
- **Activity Prioritization**: For ongoing risk monitoring and mitigation

### 2. Interpreting Results

**Delay Probability:**

- < 10%: Low risk
- 10-30%: Moderate risk, monitor closely
- > 30%: High risk, mitigation required

**Buffer Percentage:**

- < 5%: Very low uncertainty
- 5-15%: Normal range for most projects
- 15-25%: High uncertainty, consider risk reduction
- > 25%: Very high uncertainty, critical issue

**ROI on Strategies:**

- > 150%: Excellent investment
- 100-150%: Good investment
- 50-100%: Moderate benefit
- < 50%: Consider alternatives

### 3. Common Pitfalls

❌ **Don't:**

- Use delay analysis without first running PERT analysis
- Set contract time too close to expected duration without buffer
- Ignore high-risk activities on critical path
- Apply variance reduction when there's no meaningful delay risk

✓ **Do:**

- Update risk analysis as project progresses
- Combine multiple risk mitigation strategies
- Focus on high cruciality activities for variance reduction
- Document assumptions (penalty rates, cost estimates)

## API Reference

### Core Classes

#### DelayRiskAnalyzer

```python
from src.pmhelper.core.risk_analysis import DelayRiskAnalyzer

analyzer = DelayRiskAnalyzer(pert_results)
analyzer.calculate_delay_probability(contract_time)
analyzer.calculate_expected_delay(contract_time)
analyzer.calculate_risk_cost(contract_time, penalty_rate)
```

#### ContingencyPlanner

```python
from src.pmhelper.core.risk_analysis import ContingencyPlanner

planner = ContingencyPlanner(pert_results)
planner.calculate_contingency(confidence_level, daily_cost_rate)
```

#### VarianceReductionAnalyzer

```python
from src.pmhelper.core.risk_analysis import VarianceReductionAnalyzer

analyzer = VarianceReductionAnalyzer(pert_results)
analyzer.analyze_strategies(contract_time, penalty_rate,
                           time_reduction_cost, variance_reduction_cost, max_budget)
```

#### ActivityRiskPrioritizer

```python
from src.pmhelper.core.risk_analysis import ActivityRiskPrioritizer

prioritizer = ActivityRiskPrioritizer(pert_results)
prioritizer.calculate_risk_scores()
prioritizer.get_top_risks(n=10)
prioritizer.generate_mitigation_plan(budget_available)
```

## Testing

Run the comprehensive test suite:

```bash
# All risk analysis tests
pytest tests/test_risk_core.py -v

# Integration with PERT
pytest tests/test_risk_integration.py -v

# With coverage report
pytest tests/test_risk_core.py --cov=src.pmhelper.core.risk_analysis --cov-report=html
```

## Demo Script

Run the demonstration:

```bash
python risk_analysis_demo.py
```

## Technical Notes

### Dependencies

- **numpy**: Numerical computations
- **pandas**: Data structures and analysis
- **scipy** (optional): Statistical distributions (falls back to approximations if unavailable)

### Performance

- Delay probability: < 10ms
- Contingency estimation: < 20ms
- Strategy comparison: < 500ms (includes optimization)
- Activity prioritization: < 100ms for 100 activities

### Assumptions

1. **Normal Distribution**: Project completion time follows normal distribution (Central Limit Theorem)
2. **Independence**: Activity durations are independent
3. **PERT Estimates**: Three-point estimates (optimistic, most likely, pessimistic) are accurate
4. **Linear Penalties**: Delay penalties are linear (can be capped)

## Troubleshooting

**Issue**: "No analysis results available" error

- **Solution**: Run `analyzer.analyze()` before using risk analysis methods

**Issue**: Very high buffer requirements (>25%)

- **Solution**: Investigate high-variance activities, improve estimates, or reduce critical path variance

**Issue**: No variance reduction benefit

- **Solution**: Check if contract time already provides comfortable margin (no delay risk)

**Issue**: All risk scores are similar

- **Solution**: Project may have uniform risk; focus on critical path activities

## References

1. **Course Material**: IM 738 Advanced Project Management

   - Risk Analysis and Contingency Planning
   - PERT and Project Delay
   - Variance Reduction Strategies

2. **Statistical Methods**:
   - Truncated Normal Distribution
   - Normal Distribution Approximation (Central Limit Theorem)
   - Z-score calculations

## Support

For questions or issues:

- Review sample datasets in `assets/risk_examples/`
- Run demo script: `python risk_analysis_demo.py`
- Check test examples: `tests/test_risk_core.py`

---

**Version**: 1.0  
**Last Updated**: December 19, 2025  
**Module**: Risk Analysis for PMHelper
