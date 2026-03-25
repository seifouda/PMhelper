# Risk Analysis Quick Reference

## Quick Start (30 seconds)

```python
from src.pmhelper.core.pert_analyzer import PERTAnalyzer

# 1. Run PERT analysis
analyzer = PERTAnalyzer()
network, paths, activities = analyzer.analyze(activities_data)

# 2. Analyze delay risk
risk = analyzer.analyze_delay_risk(contract_time=15.0, penalty_rate=1000.0)
print(f"Delay Risk: {risk['delay_probability']:.1%}")

# 3. Estimate contingency
buffer = analyzer.estimate_contingency(confidence_level=0.95)
print(f"Buffer: {buffer['time_buffer']:.2f} weeks")
```

## Core Functions

### Delay Risk

```python
risk = analyzer.analyze_delay_risk(
    contract_time=15.0,      # Deadline (weeks)
    penalty_rate=1000.0      # $ per week
)
# Returns: delay_probability, expected_delay, risk_cost
```

### Contingency

```python
buffer = analyzer.estimate_contingency(
    confidence_level=0.95,   # 95% confidence
    daily_cost_rate=5000.0   # Optional: $ per day
)
# Returns: time_buffer, completion_time, contingency_cost
```

### Strategies

```python
strategies = analyzer.analyze_variance_reduction_strategies(
    contract_time=15.0,
    penalty_rate=1000.0,
    time_reduction_cost=3000.0,      # $ per week
    variance_reduction_cost=2000.0,  # $ per variance unit
    max_budget=30000.0
)
# Returns: baseline, strategy_a, strategy_b, mixed_strategy, best_strategy
```

### Activity Risks

```python
risks = analyzer.prioritize_activity_risks()
# Returns: DataFrame with risk_score, recommendation for each activity

plan = analyzer.generate_risk_mitigation_plan()
# Returns: high_priority, medium_priority, low_priority, critical_path_risks
```

## Interpreting Results

### Delay Probability

- **< 10%**: ✅ Low risk
- **10-30%**: ⚠️ Moderate risk
- **> 30%**: 🔴 High risk

### Buffer Percentage

- **< 5%**: Very low uncertainty
- **5-15%**: Normal range
- **15-25%**: High uncertainty
- **> 25%**: Critical uncertainty

### ROI

- **> 150%**: Excellent
- **100-150%**: Good
- **50-100%**: Moderate
- **< 50%**: Consider alternatives

### Risk Score

- **> 0.6**: High priority (immediate action)
- **0.3-0.6**: Medium priority (monitor)
- **< 0.3**: Low priority (routine)

## Common Patterns

### Pattern 1: Risk Assessment

```python
# Quick risk check
risk = analyzer.analyze_delay_risk(contract_time=15.0, penalty_rate=1000.0)
if risk['delay_probability'] > 0.3:
    print("⚠️ High risk - mitigation needed")
    buffer = analyzer.estimate_contingency(0.95)
    print(f"Add {buffer['time_buffer']:.1f} weeks buffer")
```

### Pattern 2: Budget Optimization

```python
# Find best use of mitigation budget
strategies = analyzer.analyze_variance_reduction_strategies(
    contract_time=15.0,
    penalty_rate=1000.0,
    time_reduction_cost=3000.0,
    variance_reduction_cost=2000.0,
    max_budget=50000.0
)

best = strategies['best_strategy']
print(f"Invest ${best['investment']:,.0f} in {best['name']}")
print(f"Net benefit: ${best['net_benefit']:,.0f}")
```

### Pattern 3: Activity Focus

```python
# Identify critical activities
plan = analyzer.generate_risk_mitigation_plan()

print(f"Focus on {len(plan['high_priority'])} high-priority activities:")
for activity in plan['high_priority'][:5]:  # Top 5
    print(f"  - {activity['activity_id']}: {activity['recommendation']}")
```

## Confidence Levels

| Level | Use Case           | Z-Score | Buffer (σ) |
| ----- | ------------------ | ------- | ---------- |
| 80%   | Internal deadlines | 0.84    | 0.84σ      |
| 90%   | Standard projects  | 1.28    | 1.28σ      |
| 95%   | Firm deadlines     | 1.645   | 1.65σ      |
| 99%   | Critical contracts | 2.33    | 2.33σ      |

## Files & Locations

```
src/pmhelper/core/risk_analysis.py     # Core module
tests/test_risk_core.py                # Tests
docs/RISK_ANALYSIS_USER_GUIDE.md      # Full guide
risk_analysis_demo.py                  # Demo script
assets/risk_examples/*.csv             # Sample data
```

## Running Tests

```bash
# All tests
pytest tests/test_risk_core.py -v

# With coverage
pytest tests/test_risk_core.py --cov=src.pmhelper.core.risk_analysis

# Integration test
pytest tests/test_risk_integration.py -v

# Demo
python risk_analysis_demo.py
```

## Troubleshooting

| Issue                         | Solution                         |
| ----------------------------- | -------------------------------- |
| "No analysis results"         | Run `analyzer.analyze()` first   |
| Very high buffer (>25%)       | Check high-variance activities   |
| No variance reduction benefit | Contract time may be comfortable |
| All risk scores similar       | Focus on critical path           |

## Formula Reference

```python
# Delay Probability
P(T > Tc) = 1 - Φ((Tc - μ) / σ)

# Expected Delay
E[T | T > Tc] = μ + σ × φ(z) / (1 - Φ(z))

# Risk Cost
Risk = P(delay) × E[delay] × penalty_rate

# Buffer
Buffer = Zα × σ

# Risk Score
Score = 0.40×Crit + 0.30×Cruc + 0.20×Sched + 0.10×Uncert
```

---

**Version**: 1.0 | **Date**: December 19, 2025
