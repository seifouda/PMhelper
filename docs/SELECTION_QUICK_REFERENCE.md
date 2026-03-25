# PMHelper Selection - Quick Reference Card

## CLI Commands Cheat Sheet

### AHP Analysis

```bash
python -m pmhelper.cli.selection_cli ahp -c criteria.json -m matrix.csv -o results.json
```

### Linear Scoring

```bash
python -m pmhelper.cli.selection_cli score -d data.csv -w weights.json -o results.csv -s
```

### B/C Analysis

```bash
python -m pmhelper.cli.selection_cli bc -p projects.csv -m 0.12 -o results.json
```

### Portfolio Optimization

```bash
python -m pmhelper.cli.selection_cli portfolio -p projects.csv -b 3000000 -o results.json -s
```

### File Info

```bash
python -m pmhelper.cli.selection_cli info -f problem.pmsel
```

### Convert CSV to .pmsel

```bash
python -m pmhelper.cli.selection_cli convert -i data.csv -o problem.pmsel -m ahp -n "Name"
```

---

## API Endpoints

### Base URL

```
http://localhost:8000/api/selection
```

### Endpoints

| Endpoint          | Method | Purpose                |
| ----------------- | ------ | ---------------------- |
| `/ahp`            | POST   | AHP analysis           |
| `/linear-scoring` | POST   | Linear scoring         |
| `/benefit-cost`   | POST   | B/C analysis           |
| `/portfolio`      | POST   | Portfolio optimization |
| `/methods`        | GET    | List available methods |
| `/health`         | GET    | Health check           |

### Quick Example (Python)

```python
import requests

data = {"criteria": ["A", "B"], "comparisons": {"A": {"B": 2.0}}}
response = requests.post("http://localhost:8000/api/selection/ahp", json=data)
print(response.json())
```

---

## File Formats

### Criteria (JSON)

```json
[
  { "name": "Cost", "direction": "minimize" },
  { "name": "Quality", "direction": "maximize" }
]
```

### Comparison Matrix (CSV)

```csv
Criterion,A,B,C
A,1.0,2.0,3.0
B,0.5,1.0,2.0
C,0.333,0.5,1.0
```

### Projects (CSV)

```csv
name,cost,benefit
Project A,100000,40000
Project B,150000,60000
```

### Constraints (JSON)

```json
[
  { "type": "require", "projects": ["Project A"] },
  { "type": "exclude", "projects": ["Project B", "Project C"] },
  { "type": "dependency", "projects": ["Project A", "Project B"] }
]
```

---

## Method Selection Guide

| Method             | Best For                               | Inputs Needed               | Output                      |
| ------------------ | -------------------------------------- | --------------------------- | --------------------------- |
| **AHP**            | Subjective criteria, expert judgment   | Pairwise comparisons        | Weights & rankings          |
| **Linear Scoring** | Quantifiable criteria                  | Weights & scores            | Rankings                    |
| **B/C**            | Financial projects, long-term benefits | Costs, benefits, MARR, life | Optimal project, B/C ratios |
| **Portfolio**      | Multiple projects, budget constraints  | Costs, benefits, budget     | Selected projects           |

---

## Common Options

| Option          | Short | Description                  |
| --------------- | ----- | ---------------------------- |
| `--verbose`     | `-v`  | Enable detailed output       |
| `--sensitivity` | `-s`  | Perform sensitivity analysis |
| `--output`      | `-o`  | Output file path             |
| `--help`        |       | Show command help            |

---

## Constraint Types

| Type          | Description            | Example                   |
| ------------- | ---------------------- | ------------------------- |
| `require`     | Must select            | "Security is mandatory"   |
| `exclude`     | Cannot select together | "Only one cloud provider" |
| `dependency`  | Second needs first     | "Mobile app needs cloud"  |
| `at_most_one` | Max one from list      | "Only one AI project"     |

---

## Interpretation Guide

### AHP Consistency Ratio

- **< 0.10**: ✅ Excellent consistency
- **0.10 - 0.15**: ⚠️ Acceptable with caution
- **> 0.15**: ❌ Revise comparisons

### B/C Ratio

- **≥ 1.0**: ✅ Economically viable
- **< 1.0**: ❌ Not viable

### Portfolio Status

- **Optimal**: ✅ Best solution found
- **Not Solved**: ⚠️ Feasible solution found (not optimal)
- **Infeasible**: ❌ No solution (check constraints)
- **Unbounded**: ❌ Problem formulation error

---

## Troubleshooting

| Issue                          | Solution                                                |
| ------------------------------ | ------------------------------------------------------- |
| "Weights don't sum to 1.0"     | Adjust weights to sum exactly to 1.0                    |
| "Inconsistent AHP comparisons" | Review pairwise comparisons (CR > 0.1)                  |
| "Portfolio infeasible"         | Check constraints, increase budget                      |
| "Solver timeout"               | Reduce problem size or increase time limit              |
| "Module not found"             | Install dependencies: `pip install -r requirements.txt` |

---

## Resources

- **Full Documentation**: `docs/SELECTION_CLI_API_GUIDE.md`
- **Swagger UI**: http://localhost:8000/docs
- **Examples**: `assets/examples/cli/`
- **Tests**: `tests/test_selection_api.py`

---

## Support

For issues or questions:

1. Check the full documentation
2. Review example files
3. Run with `--verbose` flag
4. Check health endpoints

---

**PMHelper Selection Module v1.0.0**  
© 2024 PMHelper Team
