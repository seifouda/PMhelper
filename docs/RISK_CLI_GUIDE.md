# Risk Analysis CLI Guide

## Overview

The PMHelper Risk Analysis CLI provides command-line access to all risk analysis features, enabling automation, scripting, and integration with other tools. All functionality available in the GUI is accessible via CLI commands.

## Installation

The CLI is included with PMHelper. Ensure you have the required dependencies:

```bash
pip install numpy pandas scipy
```

## Quick Start

```bash
# Basic delay risk analysis
python src/pmhelper/cli/risk_cli.py delay \
  -i assets/risk_examples/delay_analysis_simple.csv \
  -c 15 -p 1000

# Contingency planning
python src/pmhelper/cli/risk_cli.py contingency \
  -i assets/risk_examples/delay_analysis_simple.csv \
  -c 0.95

# Activity prioritization
python src/pmhelper/cli/risk_cli.py prioritize \
  -i assets/risk_examples/delay_analysis_simple.csv

# Comprehensive report
python src/pmhelper/cli/risk_cli.py report \
  -i assets/risk_examples/delay_analysis_simple.csv \
  -c 15 -p 1000
```

## Input File Format

All commands require a CSV file with PERT data in one of these formats:

**Format 1** (lowercase with underscores):

```csv
activity,predecessor,optimistic,most_likely,pessimistic
A,,2,3,4
B,A,3,4,5
C,A,4,5,9
```

**Format 2** (capitalized):

```csv
Activity,Predecessors,Optimistic,Most Likely,Pessimistic
A,,2,3,4
B,A,3,4,5
C,A,4,5,9
```

The CLI automatically handles both formats and various column name variations.

## Commands Reference

### 1. `delay` - Delay Risk Analysis

Calculate probability of project delay, expected delay period, and risk cost.

**Syntax**:

```bash
python src/pmhelper/cli/risk_cli.py delay [OPTIONS]
```

**Required Arguments**:

- `-i, --input FILE` - Input PERT data CSV file
- `-c, --contract-time WEEKS` - Contract completion time (weeks)
- `-p, --penalty-rate RATE` - Penalty rate per time unit ($/week)

**Optional Arguments**:

- `-m, --max-penalty PERCENT` - Maximum penalty as percentage (default: no cap)
- `-f, --format FORMAT` - Output format: text, json, csv (default: text)

**Examples**:

```bash
# Basic analysis
python src/pmhelper/cli/risk_cli.py delay \
  -i project.csv -c 20 -p 500

# With maximum penalty cap
python src/pmhelper/cli/risk_cli.py delay \
  -i project.csv -c 20 -p 500 -m 15

# JSON output for integration
python src/pmhelper/cli/risk_cli.py delay \
  -i project.csv -c 20 -p 500 -f json > delay_risk.json
```

**Output (Text Format)**:

```
======================================================================
DELAY RISK ANALYSIS
======================================================================

Input Parameters:
  Contract Time: 20.0 weeks
  Penalty Rate: $500.0/week

Results:
delay_probability: 0.3524
expected_delay: 0.87
risk_cost: 153.42
capped_risk_cost: 153.42
max_penalty: None
z_score: -0.3852

[!] RISK LEVEL: MODERATE (35.2%)
```

**Output (JSON Format)**:

```json
{
  "delay_probability": 0.35236094,
  "expected_delay": 0.87234,
  "risk_cost": 153.42,
  "capped_risk_cost": 153.42,
  "max_penalty": null,
  "z_score": -0.3852
}
```

**Risk Level Indicators**:

- `[OK]` - Low risk (<10% delay probability)
- `[!]` - Moderate risk (10-30%)
- `[!!]` - High risk (>30%)

---

### 2. `contingency` - Contingency Planning

Estimate time buffers and contingency costs for target confidence levels.

**Syntax**:

```bash
python src/pmhelper/cli/risk_cli.py contingency [OPTIONS]
```

**Required Arguments**:

- `-i, --input FILE` - Input PERT data CSV file

**Optional Arguments**:

- `-c, --confidence LEVEL` - Confidence level 0.80-0.999 (default: 0.95)
- `-d, --daily-cost RATE` - Daily cost rate for budget estimation ($/day)
- `-f, --format FORMAT` - Output format: text, json, csv (default: text)

**Common Confidence Levels**:

- 0.80 (80%) - Minimal buffer, high risk tolerance
- 0.90 (90%) - Standard for most projects
- 0.95 (95%) - Recommended for important projects
- 0.99 (99%) - Maximum safety, critical projects

**Examples**:

```bash
# Standard 95% confidence
python src/pmhelper/cli/risk_cli.py contingency \
  -i project.csv -c 0.95

# With daily cost estimation
python src/pmhelper/cli/risk_cli.py contingency \
  -i project.csv -c 0.90 -d 10000

# High confidence for critical project
python src/pmhelper/cli/risk_cli.py contingency \
  -i project.csv -c 0.99
```

**Output**:

```
======================================================================
CONTINGENCY PLANNING
======================================================================

Input Parameters:
  Confidence Level: 95%
  Daily Cost Rate: $10000/day

Results:
confidence_level: 0.9500
z_score: 1.64
time_buffer: 1.92 weeks
buffer_percentage: 12.38%
completion_time: 17.42 weeks
contingency_cost: $134,400

Recommendation: Moderate buffer (12.4%) - Typical for most projects.
```

---

### 3. `strategies` - Variance Reduction Strategies

Compare strategies for reducing project risk through time or variance reduction.

**Syntax**:

```bash
python src/pmhelper/cli/risk_cli.py strategies [OPTIONS]
```

**Required Arguments**:

- `-i, --input FILE` - Input PERT data CSV file
- `-c, --contract-time WEEKS` - Contract completion time
- `-p, --penalty-rate RATE` - Penalty rate per time unit ($/week)
- `-t, --time-cost COST` - Cost per unit time reduction ($/week)
- `-v, --variance-cost COST` - Cost per unit variance reduction ($/unit)
- `-b, --budget AMOUNT` - Maximum budget for variance reduction ($)

**Optional Arguments**:

- `-f, --format FORMAT` - Output format: text, json, csv (default: text)

**Strategy Types**:

- **Strategy A**: Reduce expected time (keep variance constant)
- **Strategy B**: Reduce variance (keep time constant)
- **Mixed Strategy**: Optimal combination of both

**Examples**:

```bash
# Compare all strategies
python src/pmhelper/cli/risk_cli.py strategies \
  -i project.csv \
  -c 20 -p 1000 \
  -t 3000 -v 2000 \
  -b 50000

# Export for analysis
python src/pmhelper/cli/risk_cli.py strategies \
  -i project.csv \
  -c 20 -p 1000 \
  -t 3000 -v 2000 \
  -b 50000 \
  -f json > strategy_comparison.json
```

**Output**:

```
======================================================================
VARIANCE REDUCTION STRATEGY COMPARISON
======================================================================

Input Parameters:
  Contract Time: 20.0 weeks
  Penalty Rate: $1000.0/week
  Time Reduction Cost: $3000.0/week
  Variance Reduction Cost: $2000.0/unit
  Max Budget: $50000.0

Baseline:
  Risk Cost: $5,234.00

Strategy A (Reduce Time):
  Time Reduction: 2.50 weeks
  Investment: $7,500.00
  Benefit: $3,200.00
  Net Benefit: -$4,300.00
  ROI: -57.3%

Strategy B (Reduce Variance):
  Variance Reduction: 1.80
  Investment: $3,600.00
  Benefit: $4,800.00
  Net Benefit: $1,200.00
  ROI: 33.3%

Mixed Strategy:
  Time Reduction: 1.50 weeks
  Variance Reduction: 1.20
  Investment: $6,900.00
  Benefit: $5,100.00
  Net Benefit: -$1,800.00
  ROI: -26.1%

[BEST] RECOMMENDED STRATEGY: Strategy B (Reduce Variance)
  Best Net Benefit: $1,200.00
```

---

### 4. `prioritize` - Activity Risk Prioritization

Identify and prioritize high-risk activities for mitigation.

**Syntax**:

```bash
python src/pmhelper/cli/risk_cli.py prioritize [OPTIONS]
```

**Required Arguments**:

- `-i, --input FILE` - Input PERT data CSV file

**Optional Arguments**:

- `-r, --show-recommendations` - Show detailed recommendations for each activity
- `-f, --format FORMAT` - Output format: text, json, csv (default: text)

**Risk Score Components**:

- Criticality (40%) - Is activity on critical path?
- Cruciality (30%) - Variance contribution to project
- Schedule Sensitivity (20%) - Total float availability
- Uncertainty (10%) - Coefficient of variation

**Examples**:

```bash
# Basic prioritization
python src/pmhelper/cli/risk_cli.py prioritize \
  -i project.csv

# With recommendations
python src/pmhelper/cli/risk_cli.py prioritize \
  -i project.csv -r

# Export to CSV for spreadsheet
python src/pmhelper/cli/risk_cli.py prioritize \
  -i project.csv -f csv > activity_risks.csv

# Export to JSON for API
python src/pmhelper/cli/risk_cli.py prioritize \
  -i project.csv -f json > activity_risks.json
```

**Output (Text Format)**:

```
======================================================================
ACTIVITY RISK PRIORITIZATION
======================================================================

Total Activities: 8
High Risk (≥0.6): 3
Medium Risk (0.3-0.6): 2
Low Risk (<0.3): 3

Activity Details:
Activity     Risk Score   Exp.Time     Variance     Float
----------------------------------------------------------------------
C            0.768        5.50         0.694        0.00
E            0.711        5.00         0.444        0.00
F            0.641        2.00         0.111        0.00
A            0.636        3.00         0.111        0.00
B            0.450        4.00         0.111        1.00
D            0.380        3.00         0.111        1.00
G            0.236        3.50         0.083        2.50
H            0.180        2.50         0.056        3.00
```

**Output (CSV Format)**:

```csv
activity_id,risk_score,expected_time,variance,total_float,recommendation
C,0.768,5.50,0.694,0.00,"CRITICAL PATH - Monitor closely; High variance"
E,0.711,5.00,0.444,0.00,"CRITICAL PATH - Monitor closely; High variance"
...
```

---

### 5. `report` - Comprehensive Risk Report

Generate a complete risk analysis report with all features.

**Syntax**:

```bash
python src/pmhelper/cli/risk_cli.py report [OPTIONS]
```

**Required Arguments**:

- `-i, --input FILE` - Input PERT data CSV file
- `-c, --contract-time WEEKS` - Contract completion time
- `-p, --penalty-rate RATE` - Penalty rate per time unit ($/week)

**Optional Arguments**:

- `--confidence LEVEL` - Confidence level for contingency (default: 0.95)
- `-m, --max-penalty PERCENT` - Maximum penalty percentage
- `-d, --daily-cost RATE` - Daily cost rate
- `-t, --time-cost COST` - Cost per unit time reduction (optional)
- `-v, --variance-cost COST` - Cost per unit variance reduction (optional)
- `-b, --budget AMOUNT` - Maximum budget for strategies (optional)

**Note**: If time-cost, variance-cost, and budget are not provided, the strategies section will be skipped.

**Examples**:

```bash
# Basic comprehensive report
python src/pmhelper/cli/risk_cli.py report \
  -i project.csv -c 20 -p 1000

# Full report with all features
python src/pmhelper/cli/risk_cli.py report \
  -i project.csv \
  -c 20 -p 1000 \
  --confidence 0.95 \
  -d 10000 \
  -t 3000 -v 2000 -b 50000

# Save to file
python src/pmhelper/cli/risk_cli.py report \
  -i project.csv -c 20 -p 1000 > risk_report.txt
```

**Output Structure**:

```
1. DELAY RISK ANALYSIS
   - Delay probability
   - Expected delay
   - Risk cost

2. CONTINGENCY PLANNING
   - Time buffer
   - Completion time
   - Contingency cost

3. VARIANCE REDUCTION STRATEGIES
   - Strategy comparison
   - ROI analysis
   - Recommendation

4. ACTIVITY RISK PRIORITIZATION
   - High-risk activities
   - Medium-risk activities
   - Activity recommendations

5. OVERALL RECOMMENDATIONS
   - Risk level assessment
   - Action items
   - Priority guidance
```

---

## Output Formats

### Text Format (Default)

Human-readable output suitable for console viewing and reports.

**Characteristics**:

- Formatted tables and sections
- Risk level indicators
- Recommendations included
- Best for: Console output, text reports

### JSON Format

Machine-readable output for integration and automation.

**Characteristics**:

- Valid JSON structure
- All numeric values preserved
- No formatting or indicators
- Best for: APIs, scripting, data processing

**Example**:

```json
{
  "delay_probability": 0.35236094,
  "expected_delay": 0.87234,
  "risk_cost": 153.42
}
```

### CSV Format

Spreadsheet-compatible output.

**Characteristics**:

- Comma-separated values
- Header row included
- Compatible with Excel, Google Sheets
- Best for: Spreadsheet analysis, data import

**Example**:

```csv
activity_id,risk_score,expected_time,variance,total_float
A,0.636,3.00,0.111,0.00
B,0.450,4.00,0.111,1.00
```

---

## Common Workflows

### Workflow 1: Quick Risk Assessment

```bash
# 1. Calculate delay risk
python src/pmhelper/cli/risk_cli.py delay \
  -i project.csv -c 20 -p 1000

# 2. Estimate contingency
python src/pmhelper/cli/risk_cli.py contingency \
  -i project.csv -c 0.95

# 3. Identify high-risk activities
python src/pmhelper/cli/risk_cli.py prioritize \
  -i project.csv
```

### Workflow 2: Complete Analysis with Export

```bash
# Generate comprehensive report
python src/pmhelper/cli/risk_cli.py report \
  -i project.csv -c 20 -p 1000 \
  --confidence 0.90 -d 10000 \
  -t 3000 -v 2000 -b 50000 > report.txt

# Export activity risks to CSV
python src/pmhelper/cli/risk_cli.py prioritize \
  -i project.csv -f csv > activities.csv

# Export all data as JSON
python src/pmhelper/cli/risk_cli.py delay \
  -i project.csv -c 20 -p 1000 -f json > delay.json
python src/pmhelper/cli/risk_cli.py contingency \
  -i project.csv -c 0.95 -f json > contingency.json
```

### Workflow 3: Batch Processing Multiple Projects

```bash
#!/bin/bash
# Process all projects in directory

for project in projects/*.csv; do
  name=$(basename "$project" .csv)

  echo "Analyzing $name..."

  python src/pmhelper/cli/risk_cli.py report \
    -i "$project" -c 20 -p 1000 \
    > "reports/${name}_report.txt"

  python src/pmhelper/cli/risk_cli.py prioritize \
    -i "$project" -f csv \
    > "reports/${name}_activities.csv"
done
```

### Workflow 4: Integration with Other Tools

```python
# Python script using CLI output
import subprocess
import json

# Run risk analysis
result = subprocess.run([
    'python', 'src/pmhelper/cli/risk_cli.py', 'delay',
    '-i', 'project.csv',
    '-c', '20', '-p', '1000',
    '-f', 'json'
], capture_output=True, text=True)

# Parse JSON output
risk_data = json.loads(result.stdout)

# Use in application
if risk_data['delay_probability'] > 0.3:
    print("HIGH RISK - Take action!")
    send_alert(risk_data)
```

---

## Error Handling

### Common Errors

**1. File Not Found**

```
Error: File not found: project.csv
```

**Solution**: Check file path and ensure file exists.

**2. Invalid CSV Format**

```
Error: CSV is missing required columns: ['optimistic']
Found columns: ['Activity', 'Predecessor', 'Expected']
```

**Solution**: Ensure CSV has required columns (activity, optimistic, most_likely, pessimistic).

**3. Invalid Parameters**

```
Error: Invalid input: could not convert string to float: 'abc'
```

**Solution**: Check all numeric parameters are valid numbers.

**4. PERT Analysis Failed**

```
Error in PERT analysis: Network has cycle
```

**Solution**: Check predecessor relationships for circular dependencies.

### Exit Codes

- `0` - Success
- `1` - Error (see error message)

---

## Performance Characteristics

| Command     | Small (<10) | Medium (10-50) | Large (50-100) | Very Large (100+) |
| ----------- | ----------- | -------------- | -------------- | ----------------- |
| delay       | <10ms       | <10ms          | <20ms          | <50ms             |
| contingency | <10ms       | <10ms          | <20ms          | <50ms             |
| strategies  | <50ms       | <200ms         | <500ms         | <2s               |
| prioritize  | <20ms       | <50ms          | <100ms         | <200ms            |
| report      | <100ms      | <300ms         | <700ms         | <3s               |

---

## Tips and Best Practices

### 1. Always Validate Input Data First

```bash
# Check if PERT data is valid before risk analysis
python -c "import pandas as pd; print(pd.read_csv('project.csv'))"
```

### 2. Start with Simple Analysis

```bash
# Begin with delay risk to understand project risk level
python src/pmhelper/cli/risk_cli.py delay -i project.csv -c 20 -p 1000
```

### 3. Use Appropriate Confidence Levels

- 90% - Standard projects
- 95% - Important projects
- 99% - Critical/high-stakes projects

### 4. Save Output for Documentation

```bash
# Timestamp reports
python src/pmhelper/cli/risk_cli.py report \
  -i project.csv -c 20 -p 1000 \
  > "report_$(date +%Y%m%d).txt"
```

### 5. Combine with Other Tools

```bash
# Chain with other analysis
python src/pmhelper/cli/risk_cli.py prioritize \
  -i project.csv -f csv | \
  sort -t',' -k2 -rn | \
  head -n 5
```

---

## Troubleshooting

### Issue: Unicode Characters Not Displaying

**Windows PowerShell/CMD**:

```powershell
# Set console to UTF-8
chcp 65001
```

**Solution**: The CLI now uses ASCII-safe characters `[OK]`, `[!]`, `[!!]` instead of Unicode symbols.

### Issue: Slow Performance

**Cause**: Large projects or strategy optimization
**Solution**:

- Use `--format json` for faster parsing
- Consider simplifying project structure
- Strategies command is O(n²), expected for large projects

### Issue: Incorrect Results

**Verify**:

1. Check input data format
2. Ensure predecessor relationships are correct
3. Verify time estimates are reasonable
4. Compare with GUI results for consistency

---

## API Reference

For programmatic use:

```python
from pmhelper.cli.risk_cli import RiskCLI

cli = RiskCLI()

# Load PERT data
success = cli.load_pert_data('project.csv')

if success:
    # Create mock args for delay analysis
    class Args:
        input = 'project.csv'
        contract_time = 20
        penalty_rate = 1000
        max_penalty = None
        format = 'json'

    # Run analysis
    exit_code = cli.cmd_delay(Args())
```

---

## Support and Resources

- **User Guide**: `docs/RISK_ANALYSIS_USER_GUIDE.md`
- **Quick Reference**: `docs/RISK_ANALYSIS_QUICK_REFERENCE.md`
- **GUI Guide**: `docs/RISK_GUI_IMPLEMENTATION.md`
- **Sample Data**: `assets/risk_examples/`
- **Demo Script**: `risk_analysis_demo.py`

---

## Changelog

### Version 1.0.0 (December 2025)

- Initial CLI implementation
- All 5 commands (delay, contingency, strategies, prioritize, report)
- Multiple output formats (text, JSON, CSV)
- Comprehensive error handling
- Cross-platform compatibility

---

**Last Updated**: December 19, 2025  
**Version**: 1.0.0  
**Status**: Production Ready
