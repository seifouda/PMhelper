# Quick Guide: Loading and Using Example Files

## Loading Examples in GUI

### Method 1: Load Example Button

1. Open PMHelper
2. Click **Project Selection** tab
3. Click **Load Example** button in toolbar
4. Select from menu:
   - AHP - Software Selection (4 criteria)
   - AHP - Simple 3 Criteria Example
   - Linear Scoring - Vendor Selection
   - B/C Analysis - Infrastructure Projects
   - Portfolio - R&D Projects
5. Application automatically:
   - Switches to correct tab
   - Loads all data
   - Shows expected results popup
6. Click appropriate button to run analysis
7. Compare your results with expected results

### Method 2: Load Problem Button

1. Click **Load Problem**
2. Navigate to `assets/examples/`
3. Select any `.pmsel` file
4. Data loads into GUI

## Example Files Quick Reference

| Example                        | Method         | Criteria/Projects          | Key Feature                                        |
| ------------------------------ | -------------- | -------------------------- | -------------------------------------------------- |
| `ahp_software_selection.pmsel` | AHP            | 4 criteria, 3 alternatives | Full AHP with Support weighted highest (46.59%)    |
| `ahp_simple_3criteria.pmsel`   | AHP            | 3 criteria, 3 alternatives | Beginner-friendly, classic textbook example        |
| `linear_scoring_vendor.pmsel`  | Linear Scoring | 4 criteria, 4 vendors      | Vendor selection with Performance/Cost/Reliability |
| `bc_infrastructure.pmsel`      | B/C Analysis   | 3 projects                 | Infrastructure with 12% MARR, incremental analysis |
| `portfolio_rd_projects.pmsel`  | Portfolio      | 7 projects, $3M budget     | R&D portfolio with constraints                     |

## Expected Results

### AHP Software Selection

- **CR**: 0.0115 (excellent consistency)
- **Winner**: Software B (7.721)
- **Weights**: Support (46.59%), Quality (27.72%), Speed (16.10%), Cost (9.59%)

### AHP Simple 3-Criteria

- **CR**: 0.08 (below 0.10 threshold)
- **Weights**: Cost (54%), Quality (30%), Speed (16%)

### Linear Scoring Vendor

- **Winner**: Vendor D (5.933)
- **Ranking**: D (5.933) > A (5.237) > B (4.467) > C (3.800)

### B/C Infrastructure

- **Optimal**: Project C
- **Projects**: A ($100K), B ($150K), C ($200K)
- **MARR**: 12%

### Portfolio R&D

- **Selected**: AI Research + Cloud Migration + Data Analytics
- **Total Benefit**: $1,120,000
- **Budget Used**: ~$2.9M of $3M (~97%)

## Running Analysis

### After Loading Example

1. **AHP Tab**:

   - Matrix is pre-filled with comparisons
   - Click "Calculate Weights" to see criterion weights and CR
   - Click "Rank Alternatives" to rank software/alternatives
   - Verify CR ≈ expected value
   - Verify rankings match expected order

2. **Linear Scoring Tab**:

   - Criteria and weights are loaded
   - Alternatives with scores are loaded
   - Click "Calculate Scores" to rank alternatives
   - Verify winner and scores match expected

3. **B/C Analysis Tab**:

   - Projects with costs, benefits, life, O&M, and salvage loaded
   - MARR is set (e.g., 12%)
   - Click "Analyze Projects" to calculate B/C ratios
   - Click "Incremental Analysis" for optimal selection
   - Verify optimal project matches expected

4. **Portfolio Tab**:
   - Projects with costs and benefits loaded
   - Budget is set
   - Constraints loaded (if any)
   - Click "Optimize Portfolio" to solve
   - Verify selected projects and total benefit match expected

## Verification Tips

### Check Your Results

- ✅ **AHP**: CR should be < 0.10 (< 0.10 is acceptable)
- ✅ **AHP**: Top-ranked alternative should match expected winner
- ✅ **Linear Scoring**: Scores should match to 3 decimal places
- ✅ **B/C**: Optimal project should have highest incremental B/C
- ✅ **Portfolio**: Selected projects should fit in budget with max benefit

### Common Issues

- **Wrong rankings**: Check that matrix comparisons loaded correctly
- **Different CR**: Ensure all matrix values are correct (reciprocals auto-filled)
- **Missing alternatives**: Verify alternatives loaded in second section
- **Budget exceeded**: Check constraint logic and project costs

## Modifying Examples

1. Load example as starting point
2. Click "Save Problem" to save modified version
3. Edit values in GUI:
   - Add/remove criteria
   - Change comparison values
   - Add/remove alternatives/projects
   - Adjust weights, costs, benefits
4. Re-run analysis
5. Save your custom problem for reuse

## Creating Your Own Examples

### Format Template

```json
{
  "version": "1.0",
  "id": "your_example_id",
  "name": "Your Example Name",
  "description": "What this example demonstrates",
  "method": "ahp", // or "linear_scoring", "benefit_cost", "portfolio"
  "metadata": {
    "author": "Your Name",
    "category": "Your Category",
    "difficulty": "Beginner|Intermediate|Advanced",
    "expected_results": {
      // Method-specific results for verification
    }
  },
  "criteria": [
    {
      "name": "Criterion 1",
      "weight": 0.0, // For AHP/BC, calculated by algorithm
      "direction": "maximize", // or "minimize"
      "description": "What this criterion measures"
    }
  ]
  // Add alternatives, projects, matrix, constraints as needed
}
```

### Save Location

- Save custom examples to `assets/examples/`
- Use `.pmsel` extension
- Name descriptively (e.g., `ahp_server_selection.pmsel`)

## Troubleshooting

### Example Won't Load

- Check JSON syntax (valid JSON format)
- Ensure all required fields present
- Verify file extension is `.pmsel`
- Check that criterion names match in matrix/scores

### Results Don't Match Expected

- Verify all comparison values loaded correctly
- Check that directions (maximize/minimize) are correct
- Ensure weights sum to 1.0 (for Linear Scoring)
- Confirm no rounding errors in input data

### GUI Doesn't Update

- Try clicking "Clear All" first, then reload
- Restart application if data seems stuck
- Check console for error messages

## Additional Resources

- **Full Documentation**: See `EXAMPLE_FILES_IMPLEMENTATION.md`
- **Test Script**: Run `python test_examples.py` to verify all examples
- **Model Reference**: See `src/pmhelper/core/models.py` for data structure
- **File Format**: See example files in `assets/examples/` for format details

## Support

If examples don't work as expected:

1. Check that PMHelper is up to date
2. Verify example files haven't been modified
3. Run test script: `python test_examples.py`
4. Check console output for error messages
5. Report issues with specific file name and error message

---

**Happy analyzing!** 🎯
