# PMHelper User Guide

Welcome to PMHelper - your comprehensive project management analysis tool! This guide will help you get started and make the most of PMHelper's powerful features.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Interface](#understanding-the-interface)
3. [CPM Analysis Workflow](#cpm-analysis-workflow)
4. [PERT Analysis Workflow](#pert-analysis-workflow)
5. [Project Crashing](#project-crashing)
6. [Data Import/Export](#data-importexport)
7. [Visualization Features](#visualization-features)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### What is PMHelper?

PMHelper is a desktop application that helps you analyze and optimize project schedules using two powerful methods:

- **CPM (Critical Path Method)**: For projects with fixed activity durations
- **PERT (Program Evaluation and Review Technique)**: For projects with uncertain activity durations

### Installation and Setup

1. **Prerequisites**: Ensure you have Python 3.8 or higher installed
2. **Install Dependencies**: Run `pip install -r config/requirements.txt`
3. **Launch Application**: Run `python src/main.py`

### First Time Setup

When you first open PMHelper, you'll see the main interface with several tabs. The application starts with sample data to help you explore the features immediately.

## Understanding the Interface

### Main Window Layout

PMHelper features a tabbed interface with the following sections:

#### 1. **Input Tab** 📝

- Enter or edit project activities
- Import data from CSV/Excel files
- Switch between CPM and PERT modes
- Add, delete, and modify activities

#### 2. **Results Tab** 📊

- View analysis results
- See critical path activities
- Review project statistics
- Export results to files

#### 3. **Network Tab** 🔗

- Interactive network diagrams
- Visual representation of activity dependencies
- Critical path highlighting
- Export network diagrams

#### 4. **Gantt Tab** 📅

- Timeline visualization
- Activity bars with start/end dates
- Critical path highlighting
- Resource utilization display

#### 5. **Probability Tab** 📈 (PERT mode only)

- Completion probability calculations
- Risk analysis charts
- Monte Carlo simulation results
- Statistical distributions

#### 6. **Crashing Tab** ⚡

- Project duration optimization
- Cost-benefit analysis
- What-if scenarios
- Crashing strategies

### Menu Bar

- **File**: Open, save, import/export data
- **Analysis**: Run different types of analysis
- **View**: Switch between analysis modes
- **Tools**: Access utilities and settings
- **Help**: User guide and about information

### Status Bar

The bottom status bar shows:

- Current analysis mode (CPM/PERT)
- Project status
- Number of activities
- Analysis completion status

## CPM Analysis Workflow

### Step 1: Prepare Your Data

For CPM analysis, you need the following information for each activity:

- **Activity ID**: Unique identifier (e.g., A, B, C or 1, 2, 3)
- **Activity Name**: Descriptive name
- **Duration**: Time to complete the activity
- **Predecessors**: Activities that must finish before this one starts
- **Min Duration**: Minimum possible duration (for crashing)
- **Crash Cost**: Cost per unit time to reduce duration
- **Normal Cost**: Standard cost of the activity

### Step 2: Enter Data

**Option A: Manual Entry**

1. Go to the **Input** tab
2. Ensure **CPM mode** is selected
3. Click **Add Row** to add activities
4. Fill in the required information
5. Use **Delete Row** to remove activities

**Option B: Import from File**

1. Click **File → Load CPM Data**
2. Select your CSV or Excel file
3. Verify the data appears correctly

### Step 3: Run Analysis

1. Click **Analysis → Run CPM Analysis** or use the **Analyze Project** button
2. The analysis will calculate:
   - Earliest Start (ES) and Earliest Finish (EF) times
   - Latest Start (LS) and Latest Finish (LF) times
   - Total Float for each activity
   - Critical path activities
   - Project duration

### Step 4: Review Results

**Results Tab**:

- **Project Summary**: Total duration, critical path length
- **Activities Table**: Detailed timing for all activities
- **Critical Path**: Sequence of activities with zero float

**Network Tab**:

- Visual network diagram
- Critical path highlighted in red
- Non-critical activities in blue
- Activity details on hover

**Gantt Tab**:

- Timeline view of all activities
- Critical path activities highlighted
- Resource utilization (if specified)

### Step 5: Optimize (Optional)

Use the **Crashing Tab** to:

- Reduce project duration
- Analyze cost implications
- Compare different strategies
- Find optimal time-cost trade-offs

## PERT Analysis Workflow

### Step 1: Prepare PERT Data

For PERT analysis, you need three time estimates for each activity:

- **Optimistic Time (O)**: Best-case scenario
- **Most Likely Time (M)**: Most realistic estimate
- **Pessimistic Time (P)**: Worst-case scenario
- **Predecessors**: Activity dependencies

### Step 2: Enter PERT Data

1. Switch to **PERT mode** in the Input tab
2. The table will automatically adjust to show PERT columns
3. Enter your three-point estimates
4. Specify predecessor relationships

### Step 3: Run PERT Analysis

1. Click **Analysis → Run PERT Analysis**
2. PERT calculations include:
   - Expected duration: (O + 4M + P) / 6
   - Activity variance: ((P - O) / 6)²
   - Project variance (sum of critical path variances)
   - Project standard deviation

### Step 4: Analyze Probabilities

**Probability Tab**:

- **Completion Probability**: Calculate probability of finishing by a specific date
- **Target Duration**: Find duration for a desired confidence level
- **Risk Analysis**: Assess project risk factors
- **Monte Carlo**: Run simulations for better estimates

**Example Questions You Can Answer**:

- "What's the probability we'll finish by December 31st?"
- "What duration gives us 80% confidence?"
- "How much risk are we taking with our current schedule?"

## Project Crashing

Project crashing is the process of reducing project duration by allocating additional resources to activities, typically at increased cost.

### When to Use Crashing

- Project is behind schedule
- Client requests earlier completion
- Market opportunities require faster delivery
- Penalty costs make acceleration profitable

### Crashing Process

1. **Go to Crashing Tab**
2. **Set Target Duration**: Enter desired project completion time
3. **Choose Strategy**:
   - **Lowest Cost**: Minimize total crashing cost
   - **Best Efficiency**: Maximize time saved per dollar
   - **Critical Path Focus**: Prioritize critical activities
4. **Set Budget** (optional): Maximum amount to spend on crashing
5. **Run Analysis**: Click "Run Crashing Analysis"

### Understanding Crashing Results

**Cost-Benefit Analysis**:

- Total crash cost
- Time saved
- Cost per unit time saved
- Activities to crash and by how much

**Visualization**:

- Before/after network diagrams
- Cost curves
- Crashing progression charts

### Crashing Tips

- Only critical path activities reduce project duration
- Start with activities having lowest crash cost per time unit
- Consider resource availability and practical constraints
- Balance time savings with budget limitations

## Data Import/Export

### Supported File Formats

**Import Formats**:

- CSV files (Comma-Separated Values)
- Excel workbooks (.xlsx)
- Tab-delimited text files

**Export Formats**:

- CSV (analysis results)
- Excel workbooks (comprehensive reports)
- PNG/PDF (charts and diagrams)
- JSON (data interchange)

### CSV File Structure

**CPM Format**:

```csv
Activity,Duration,Predecessors,Min Duration,Crash Cost,Normal Cost
A,5,,2,300,1000
B,3,A,1,200,600
C,4,"A,B",2,150,800
```

**PERT Format**:

```csv
Activity,Optimistic,Most Likely,Pessimistic,Predecessors
A,3,5,8,
B,2,3,5,A
C,3,4,6,"A,B"
```

### Import Tips

1. **Headers**: Ensure column headers match exactly
2. **Predecessors**: Use comma-separated values for multiple predecessors
3. **Encoding**: Save files as UTF-8 for special characters
4. **Numbers**: Use dots (.) for decimal points, not commas

### Export Options

**From Results Tab**:

- Export complete analysis results
- Include activity details and summary statistics
- Choose between CSV and Excel formats

**From Visualization Tabs**:

- Save charts as PNG images
- Export high-resolution versions for presentations
- Include data tables with charts

## Visualization Features

### Network Diagrams

**Features**:

- Automatic layout optimization
- Critical path highlighting
- Activity timing information
- Dependency arrows
- Zoom and pan capabilities

**Customization**:

- Show/hide activity details
- Adjust node sizes
- Change color schemes
- Export for presentations

### Gantt Charts

**Features**:

- Timeline visualization
- Activity bars with durations
- Critical path highlighting
- Resource utilization (if data available)
- Today line indicator

**Interactive Elements**:

- Hover for activity details
- Zoom timeline
- Export to various formats

### Probability Charts (PERT)

**Chart Types**:

- **Distribution Curve**: Shows project completion probability distribution
- **Cumulative Probability**: Probability of completion by specific dates
- **Sensitivity Analysis**: Impact of individual activities on project risk
- **Monte Carlo Results**: Simulation-based probability estimates

## Tips and Best Practices

### Data Entry Tips

1. **Use Consistent IDs**: Keep activity IDs short and logical (A, B, C or 1, 2, 3)
2. **Meaningful Names**: Use descriptive activity names
3. **Realistic Estimates**: Base durations on historical data when possible
4. **Check Dependencies**: Verify predecessor relationships are correct

### Analysis Best Practices

1. **Start Simple**: Begin with a basic project structure
2. **Validate Results**: Check if critical path makes logical sense
3. **Use Multiple Views**: Compare network, Gantt, and results views
4. **Document Assumptions**: Keep notes about your estimates and assumptions

### PERT Estimation Guidelines

1. **Optimistic**: True best case (90% probability of beating this time)
2. **Pessimistic**: True worst case (90% probability of finishing before this time)
3. **Most Likely**: Single best estimate if you had to pick one number
4. **Be Realistic**: Avoid overly optimistic or pessimistic estimates

### Performance Tips

1. **Large Projects**: For 500+ activities, use network view sparingly
2. **File Size**: Keep imported files under 10MB for best performance
3. **Memory**: Close unused tabs for large projects
4. **Exports**: Use CSV for large datasets, Excel for formatted reports

## Troubleshooting

### Common Issues and Solutions

#### "Cannot import data" Error

**Problem**: File format not recognized
**Solution**:

- Check file extension (.csv, .xlsx)
- Verify column headers match required format
- Ensure no special characters in activity IDs

#### Network diagram doesn't display

**Problem**: Missing dependencies or circular references
**Solution**:

- Check for circular dependencies (A→B→C→A)
- Ensure all predecessor activities exist
- Verify no activity depends on itself

#### Incorrect critical path

**Problem**: Logic errors in data
**Solution**:

- Verify predecessor relationships
- Check duration estimates
- Look for missing dependencies

#### Crashing analysis fails

**Problem**: Invalid crash data
**Solution**:

- Ensure crash costs are positive numbers
- Verify minimum durations are less than normal durations
- Check that crashable activities exist on critical path

#### Slow performance

**Problem**: Large project or system limitations
**Solution**:

- Reduce visualization complexity
- Close unused tabs
- Use command-line interface for very large projects
- Consider breaking large projects into phases

### Error Messages

#### "Invalid file format"

Your file doesn't match the expected CSV or Excel structure. Check the format requirements in the Data Import/Export section.

#### "Circular dependency detected"

Your project has activities that depend on each other in a loop. Review your predecessor relationships.

#### "No critical path found"

This usually indicates missing or incorrect dependency information. Verify your project logic.

### Getting Help

1. **Built-in Help**: Check the Help menu for quick reference
2. **Sample Data**: Use File → Load Sample Data to see proper format
3. **Documentation**: Refer to this user guide and technical documentation
4. **Error Details**: Copy error messages for troubleshooting

### Performance Guidelines

**Small Projects** (1-50 activities):

- All features work smoothly
- Real-time updates
- Complex visualizations supported

**Medium Projects** (50-200 activities):

- Minor delays in visualization updates
- Export operations may take a few seconds
- Recommended to close unused tabs

**Large Projects** (200+ activities):

- Use simplified visualizations
- Consider using command-line interface
- Break into smaller sub-projects if possible

---

## Next Steps

Congratulations! You now have a comprehensive understanding of PMHelper. Here are some suggested next steps:

1. **Practice**: Try the sample data and experiment with different features
2. **Import Your Data**: Start with a small project from your work
3. **Explore Advanced Features**: Experiment with project crashing and PERT analysis
4. **Share Results**: Export visualizations for team presentations
5. **Optimize Workflows**: Develop templates for common project types

Remember: PMHelper is a powerful tool, but the quality of your analysis depends on the quality of your input data. Take time to develop good estimates and validate your project logic.

Happy project managing! 🚀
