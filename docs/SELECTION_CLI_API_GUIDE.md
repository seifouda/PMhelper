# CLI & API Usage Guide - Project Selection Module

## Command Line Interface (CLI)

The PMHelper Selection CLI provides command-line tools for project selection and decision analysis.

### Installation & Setup

```bash
# Install PMHelper with selection module dependencies
pip install -r requirements.txt

# Verify installation
python -m pmhelper.cli.selection_cli --version
```

### Available Commands

```bash
pmhelper selection --help
```

#### 1. AHP Analysis (`ahp`)

Perform Analytic Hierarchy Process analysis with pairwise comparisons.

**Syntax:**

```bash
python -m pmhelper.cli.selection_cli ahp \
  --criteria CRITERIA.json \
  --matrix MATRIX.csv \
  [--alternatives ALTERNATIVES.csv] \
  --output RESULTS.json \
  [--verbose]
```

**Example:**

```bash
python -m pmhelper.cli.selection_cli ahp \
  -c assets/examples/cli/ahp_criteria.json \
  -m assets/examples/cli/ahp_matrix.csv \
  -a assets/examples/cli/ahp_alternatives.csv \
  -o results/ahp_results.json \
  -v
```

**File Formats:**

_criteria.json:_

```json
[
  { "name": "Cost", "direction": "minimize" },
  { "name": "Quality", "direction": "maximize" },
  { "name": "Speed", "direction": "maximize" }
]
```

_matrix.csv:_

```csv
Criterion,Cost,Quality,Speed
Cost,1.0,0.333,0.5
Quality,3.0,1.0,2.0
Speed,2.0,0.5,1.0
```

_alternatives.csv (optional):_

```csv
name,Cost,Quality,Speed
Product A,8.5,7.2,8.0
Product B,7.0,8.5,6.0
Product C,6.5,6.0,9.0
```

**Output:**

- Criterion weights with consistency ratio
- Ranked alternatives (if provided)
- Visual bar chart of weights

#### 2. Linear Scoring (`score`)

Multi-criteria scoring with normalization and optional sensitivity analysis.

**Syntax:**

```bash
python -m pmhelper.cli.selection_cli score \
  --data DATA.csv \
  --weights WEIGHTS.json \
  --output RESULTS.csv \
  [--sensitivity] \
  [--verbose]
```

**Example:**

```bash
python -m pmhelper.cli.selection_cli score \
  -d assets/examples/cli/linear_scoring_data.csv \
  -w assets/examples/cli/linear_scoring_weights.json \
  -o results/linear_scoring_results.csv \
  -s -v
```

**File Formats:**

_data.csv:_

```csv
name,Performance,Cost,Reliability,Ease_of_Use
Product A,85,7500,92,78
Product B,78,6200,88,85
Product C,92,8900,85,72
```

_weights.json:_

```json
{
  "criteria": {
    "Performance": { "weight": 0.35, "direction": "maximize" },
    "Cost": { "weight": 0.25, "direction": "minimize" },
    "Reliability": { "weight": 0.25, "direction": "maximize" },
    "Ease_of_Use": { "weight": 0.15, "direction": "maximize" }
  }
}
```

**Output:**

- Ranked alternatives with normalized scores
- Total weighted scores
- Sensitivity analysis results (if --sensitivity flag used)

#### 3. B/C Analysis (`bc`)

Benefit-to-Cost analysis with incremental comparisons.

**Syntax:**

```bash
python -m pmhelper.cli.selection_cli bc \
  --projects PROJECTS.csv \
  --marr MARR \
  --output RESULTS.json \
  [--analysis-type {independent|mutually_exclusive}] \
  [--verbose]
```

**Example:**

```bash
python -m pmhelper.cli.selection_cli bc \
  -p assets/examples/cli/bc_projects.csv \
  -m 0.12 \
  -o results/bc_results.json \
  -t mutually_exclusive \
  -v
```

**File Format:**

_projects.csv:_

```csv
name,initial_cost,life,annual_benefits,annual_om,salvage
Project A,100000,10,25000,3000,10000
Project B,150000,10,35000,5000,15000
Project C,200000,10,48000,8000,20000
```

**Output:**

- B/C ratios for all projects
- Optimal project (for mutually exclusive)
- Incremental analysis comparisons
- Capital recovery calculations

#### 4. Portfolio Optimization (`portfolio`)

Integer programming for optimal project portfolio selection.

**Syntax:**

```bash
python -m pmhelper.cli.selection_cli portfolio \
  --projects PROJECTS.csv \
  --budget BUDGET \
  [--constraints CONSTRAINTS.json] \
  --output RESULTS.json \
  [--time-limit SECONDS] \
  [--sensitivity] \
  [--verbose]
```

**Example:**

```bash
python -m pmhelper.cli.selection_cli portfolio \
  -p assets/examples/cli/portfolio_projects.csv \
  -b 3000000 \
  -c assets/examples/cli/portfolio_constraints.json \
  -o results/portfolio_results.json \
  -t 60 -s -v
```

**File Formats:**

_projects.csv:_

```csv
name,cost,benefit
AI Research,1200000,450000
Cloud Migration,800000,320000
Mobile App,500000,180000
Data Analytics,900000,350000
```

_constraints.json (optional):_

```json
[
  {
    "type": "require",
    "projects": ["Security Upgrade"],
    "description": "Security Upgrade is mandatory"
  },
  {
    "type": "exclude",
    "projects": ["AI Research", "Blockchain POC"],
    "description": "Cannot select both"
  },
  {
    "type": "dependency",
    "projects": ["Cloud Migration", "Mobile App"],
    "description": "Mobile App requires Cloud Migration"
  }
]
```

**Constraint Types:**

- `require`: Projects must be selected
- `exclude`: Projects cannot be selected together (at most one)
- `dependency`: Second project requires first project
- `at_most_one`: At most one project from the list

**Output:**

- Selected projects
- Total cost and benefit
- Budget utilization percentage
- Shadow price (marginal value of budget)
- Budget sensitivity analysis (if --sensitivity flag used)

#### 5. File Information (`info`)

Display information about a .pmsel file.

**Syntax:**

```bash
python -m pmhelper.cli.selection_cli info \
  --file FILE.pmsel \
  [--verbose]
```

**Example:**

```bash
python -m pmhelper.cli.selection_cli info \
  -f assets/examples/ahp_software_selection.pmsel \
  -v
```

#### 6. File Conversion (`convert`)

Convert CSV data to .pmsel format.

**Syntax:**

```bash
python -m pmhelper.cli.selection_cli convert \
  --input INPUT.csv \
  --output OUTPUT.pmsel \
  --method {ahp|linear_scoring|benefit_cost|portfolio} \
  --name "Problem Name" \
  [--description "Description"]
```

**Example:**

```bash
python -m pmhelper.cli.selection_cli convert \
  -i data/projects.csv \
  -o problems/portfolio.pmsel \
  -m portfolio \
  -n "R&D Portfolio 2024" \
  -d "Research and Development project portfolio for 2024"
```

---

## REST API

The PMHelper Selection API provides REST endpoints for all selection methods.

### Starting the API Server

```bash
# Start the server
python -m pmhelper.server.main

# Or use uvicorn directly
uvicorn pmhelper.server.api.main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Base Endpoints

#### Health Check

```http
GET /api/selection/health
```

**Response:**

```json
{
  "status": "healthy",
  "module": "selection",
  "version": "1.0.0",
  "solver_available": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Available Methods

```http
GET /api/selection/methods
```

**Response:**

```json
{
  "methods": [
    {
      "id": "ahp",
      "name": "Analytic Hierarchy Process (AHP)",
      "description": "Multi-criteria decision analysis using pairwise comparisons",
      "best_for": "Complex decisions with subjective criteria",
      "requires": ["criteria", "pairwise_comparisons"],
      "optional": ["alternatives"]
    },
    ...
  ],
  "total_methods": 4
}
```

### AHP Analysis

```http
POST /api/selection/ahp
Content-Type: application/json
```

**Request Body:**

```json
{
  "criteria": ["Cost", "Quality", "Speed", "Support"],
  "comparisons": {
    "Cost": { "Quality": 0.333, "Speed": 0.5, "Support": 0.25 },
    "Quality": { "Speed": 2.0, "Support": 0.5 },
    "Speed": { "Support": 0.333 }
  },
  "alternatives": [
    {
      "name": "Software A",
      "scores": { "Cost": 8.5, "Quality": 7.2, "Speed": 8.0, "Support": 6.5 }
    },
    {
      "name": "Software B",
      "scores": { "Cost": 7.0, "Quality": 8.5, "Speed": 6.0, "Support": 8.0 }
    }
  ]
}
```

**Response (200 OK):**

```json
{
  "method": "AHP",
  "consistency_ratio": 0.0115,
  "is_consistent": true,
  "weights": {
    "Cost": 0.0959,
    "Quality": 0.2772,
    "Speed": 0.161,
    "Support": 0.4659
  },
  "ranked_alternatives": [
    {
      "Rank": 1,
      "Alternative": "Software B",
      "Total Score": 7.720635
    },
    {
      "Rank": 2,
      "Alternative": "Software A",
      "Total Score": 7.127408
    }
  ],
  "analysis_timestamp": "2024-01-15T10:30:00"
}
```

### Linear Scoring

```http
POST /api/selection/linear-scoring
Content-Type: application/json
```

**Request Body:**

```json
{
  "criteria": [
    { "name": "Performance", "weight": 0.35, "direction": "maximize" },
    { "name": "Cost", "weight": 0.25, "direction": "minimize" },
    { "name": "Reliability", "weight": 0.4, "direction": "maximize" }
  ],
  "alternatives": [
    {
      "name": "Product A",
      "scores": { "Performance": 85, "Cost": 7500, "Reliability": 92 }
    },
    {
      "name": "Product B",
      "scores": { "Performance": 78, "Cost": 6200, "Reliability": 88 }
    }
  ],
  "sensitivity_analysis": true
}
```

**Response (200 OK):**

```json
{
  "method": "LinearScoring",
  "ranked_alternatives": [
    {
      "Rank": 1,
      "name": "Product A",
      "Total Score": 5.237037
    },
    {
      "Rank": 2,
      "name": "Product B",
      "Total Score": 4.466667
    }
  ],
  "sensitivity_results": {
    "variations": {
      "Performance": [...],
      "Cost": [...],
      "Reliability": [...]
    }
  },
  "analysis_timestamp": "2024-01-15T10:30:00"
}
```

### B/C Analysis

```http
POST /api/selection/benefit-cost
Content-Type: application/json
```

**Request Body:**

```json
{
  "projects": [
    {
      "name": "Project A",
      "cost": 100000,
      "benefit": 25000,
      "life": 10,
      "initial_cost": 100000,
      "annual_om": 3000,
      "salvage": 10000
    },
    {
      "name": "Project B",
      "cost": 150000,
      "benefit": 35000,
      "life": 10,
      "initial_cost": 150000,
      "annual_om": 5000,
      "salvage": 15000
    }
  ],
  "marr": 0.12,
  "analysis_type": "mutually_exclusive"
}
```

**Response (200 OK):**

```json
{
  "method": "BenefitCost",
  "analysis_type": "mutually_exclusive",
  "marr": 0.12,
  "optimal_project": {
    "name": "Project B",
    "BC_Ratio": 1.089,
    "initial_cost": 150000,
    "annual_benefits": 35000
  },
  "comparisons": [
    {
      "current": "Project A",
      "challenger": "Project B",
      "incremental_bc": 1.025,
      "decision": "Accept challenger"
    }
  ],
  "analysis_timestamp": "2024-01-15T10:30:00"
}
```

### Portfolio Optimization

```http
POST /api/selection/portfolio
Content-Type: application/json
```

**Request Body:**

```json
{
  "projects": [
    { "name": "AI Research", "cost": 1200000, "benefit": 450000 },
    { "name": "Cloud Migration", "cost": 800000, "benefit": 320000 },
    { "name": "Mobile App", "cost": 500000, "benefit": 180000 }
  ],
  "budget": 2000000,
  "constraints": [
    {
      "type": "require",
      "projects": ["Cloud Migration"],
      "description": "Cloud Migration is mandatory"
    }
  ],
  "time_limit": 60,
  "sensitivity_analysis": false
}
```

**Response (200 OK):**

```json
{
  "method": "Portfolio",
  "status": "Optimal",
  "selected_projects": ["AI Research", "Cloud Migration"],
  "total_cost": 2000000,
  "total_benefit": 770000,
  "budget_utilization": 100.0,
  "objective_value": 770000,
  "shadow_price_budget": 0.35,
  "analysis_timestamp": "2024-01-15T10:30:00"
}
```

### Error Responses

**400 Bad Request:**

```json
{
  "detail": "Criterion weights must sum to 1.0 (current sum: 0.95)"
}
```

**500 Internal Server Error:**

```json
{
  "detail": "Portfolio optimization failed: Solver timed out"
}
```

### Python Client Example

```python
import requests

# AHP Analysis
ahp_data = {
    "criteria": ["Cost", "Quality", "Speed"],
    "comparisons": {
        "Cost": {"Quality": 0.5, "Speed": 0.333},
        "Quality": {"Speed": 2.0}
    }
}

response = requests.post(
    "http://localhost:8000/api/selection/ahp",
    json=ahp_data
)

if response.status_code == 200:
    result = response.json()
    print(f"CR: {result['consistency_ratio']:.4f}")
    print(f"Weights: {result['weights']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### cURL Examples

**AHP:**

```bash
curl -X POST "http://localhost:8000/api/selection/ahp" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": ["Cost", "Quality"],
    "comparisons": {"Cost": {"Quality": 0.5}}
  }'
```

**Portfolio:**

```bash
curl -X POST "http://localhost:8000/api/selection/portfolio" \
  -H "Content-Type: application/json" \
  -d '{
    "projects": [
      {"name": "Project A", "cost": 100000, "benefit": 40000},
      {"name": "Project B", "cost": 150000, "benefit": 55000}
    ],
    "budget": 200000
  }'
```

## Testing

### CLI Testing

```bash
# Test all CLI commands with examples
cd d:\PMhelper

# AHP
python -m pmhelper.cli.selection_cli ahp \
  -c assets/examples/cli/ahp_criteria.json \
  -m assets/examples/cli/ahp_matrix.csv \
  -o test_ahp.json -v

# Linear Scoring
python -m pmhelper.cli.selection_cli score \
  -d assets/examples/cli/linear_scoring_data.csv \
  -w assets/examples/cli/linear_scoring_weights.json \
  -o test_linear.csv -s -v

# B/C Analysis
python -m pmhelper.cli.selection_cli bc \
  -p assets/examples/cli/bc_projects.csv \
  -m 0.12 -o test_bc.json -v

# Portfolio
python -m pmhelper.cli.selection_cli portfolio \
  -p assets/examples/cli/portfolio_projects.csv \
  -b 3000000 -o test_portfolio.json -s -v
```

### API Testing

```bash
# Start server in one terminal
python -m pmhelper.server.main

# Run API tests in another terminal
python tests/test_selection_api.py
```

Or use the interactive Swagger UI at http://localhost:8000/docs

## Best Practices

### CLI

1. **Always use verbose mode (`-v`)** during initial testing
2. **Validate input files** before running analysis
3. **Save results to JSON** for reproducibility
4. **Use sensitivity analysis** for critical decisions

### API

1. **Check health endpoint** before making requests
2. **Validate input data** on client side
3. **Handle timeout errors** for large problems
4. **Use async clients** for parallel requests
5. **Cache results** when appropriate

### General

1. **Document assumptions** in file descriptions
2. **Version control** input files and results
3. **Review consistency ratio** for AHP (should be < 0.1)
4. **Test with sample data** before production use
5. **Monitor solver performance** for portfolio optimization
