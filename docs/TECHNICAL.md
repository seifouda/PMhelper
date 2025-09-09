# PMHelper Technical Documentation

## Architecture Overview

PMHelper is a comprehensive project management analysis tool built with Python, featuring a modular architecture that separates concerns between analysis logic, user interface, and utility functions.

### System Architecture

```
PMHelper/
├── src/pmhelper/                 # Core Package
│   ├── core/                     # Analysis Engines
│   │   ├── cpm_analyzer.py       # Critical Path Method implementation
│   │   ├── pert_analyzer.py      # PERT probabilistic analysis
│   │   ├── network_builder.py    # Network graph construction
│   │   └── __init__.py
│   ├── gui/                      # User Interface Layer
│   │   ├── main_window.py        # Main application window
│   │   ├── tabs/                 # Individual feature tabs
│   │   │   ├── input_tab.py      # Data input interface
│   │   │   ├── results_tab.py    # Analysis results display
│   │   │   ├── network_tab.py    # Network diagram viewer
│   │   │   ├── gantt_tab.py      # Gantt chart visualization
│   │   │   ├── probability_tab.py # PERT probability analysis
│   │   │   └── project_crashing_core.py # Project crashing functionality
│   │   ├── widgets/              # Custom GUI components
│   │   └── __init__.py
│   ├── utils/                    # Utility Modules
│   │   ├── calculations.py       # Mathematical utilities
│   │   ├── file_handlers.py      # File I/O operations
│   │   ├── visualizations.py     # Chart and diagram creation
│   │   └── __init__.py
│   ├── cli/                      # Command Line Interface
│   │   ├── cmp_cli.py           # CPM command line tools
│   │   ├── pert_cli.py          # PERT command line tools
│   │   └── __init__.py
│   └── __init__.py               # Package initialization
└── main.py                       # Application entry point
```

### Design Patterns

#### 1. **Model-View-Controller (MVC)**

- **Model**: Core analysis modules (`cpm_analyzer`, `pert_analyzer`)
- **View**: GUI tabs and visualization components
- **Controller**: Main window manages state and coordinates between models and views

#### 2. **Observer Pattern**

- Analysis results trigger updates across multiple tabs
- Status bar updates reflect current application state

#### 3. **Strategy Pattern**

- Different analysis modes (CPM vs PERT) use interchangeable analyzers
- Visualization components adapt based on data type

## Core Modules Documentation

### Critical Path Method (CPM) Analyzer

**Location**: `src/pmhelper/core/cpm_analyzer.py`

The CPM analyzer handles deterministic project scheduling using the Critical Path Method.

**Key Features**:

- Forward and backward pass calculations
- Critical path identification
- Project crashing optimization
- Resource-constrained project scheduling (RCPS)

**Main Classes**:

- `CPMAnalyzer`: Core analysis engine

**Key Methods**:

```python
def analyze(self, activities_data) -> dict:
    """
    Perform complete CPM analysis

    Args:
        activities_data (list): List of activity dictionaries

    Returns:
        dict: Analysis results including critical path, durations, floats
    """

def crash_project(self, target_duration, max_budget=None) -> dict:
    """
    Optimize project duration through activity crashing

    Args:
        target_duration (float): Desired project completion time
        max_budget (float, optional): Maximum budget for crashing

    Returns:
        dict: Crashing results with cost analysis
    """
```

### PERT Analyzer

**Location**: `src/pmhelper/core/pert_analyzer.py`

Handles probabilistic project analysis using three-point estimates.

**Key Features**:

- Beta distribution calculations
- Project completion probability
- Monte Carlo simulation
- Risk analysis

**Main Classes**:

- `PERTAnalyzer`: Probabilistic analysis engine

**Key Methods**:

```python
def calculate_completion_probability(self, target_duration) -> float:
    """
    Calculate probability of completing project by target duration

    Args:
        target_duration (float): Target completion time

    Returns:
        float: Probability (0.0 to 1.0)
    """

def get_project_statistics(self) -> dict:
    """
    Get comprehensive project statistics

    Returns:
        dict: Expected duration, variance, standard deviation
    """
```

### Network Builder

**Location**: `src/pmhelper/core/network_builder.py`

Provides shared network construction and graph manipulation utilities.

**Key Features**:

- Network graph creation from activity data
- Forward/backward pass algorithms
- Float calculations
- Critical path identification

### GUI Components

#### Main Window

**Location**: `src/pmhelper/gui/main_window.py`

Central application controller managing all tabs and coordinating analysis.

**Key Responsibilities**:

- Application lifecycle management
- Tab coordination
- Menu and status bar management
- Analysis mode switching (CPM/PERT)

#### Tab System

Each analysis feature is implemented as a separate tab:

1. **Input Tab** (`input_tab.py`): Data entry and file operations
2. **Results Tab** (`results_tab.py`): Analysis results display
3. **Network Tab** (`network_tab.py`): Interactive network diagrams
4. **Gantt Tab** (`gantt_tab.py`): Timeline visualization
5. **Probability Tab** (`probability_tab.py`): PERT statistical analysis

### Utility Modules

#### File Handlers

**Location**: `src/pmhelper/utils/file_handlers.py`

Manages data import/export operations.

**Supported Formats**:

- CSV files (primary format)
- Excel workbooks (.xlsx)
- JSON data export

#### Visualizations

**Location**: `src/pmhelper/utils/visualizations.py`

Creates charts and diagrams using matplotlib.

**Visualization Types**:

- Network diagrams with node positioning
- Gantt charts with critical path highlighting
- Probability distribution curves
- Resource utilization charts

#### Calculations

**Location**: `src/pmhelper/utils/calculations.py`

Mathematical utilities for project management calculations.

**Function Categories**:

- Time calculations (PERT estimates, variance)
- Cost analysis (normal costs, crash costs)
- Resource calculations (utilization, leveling)
- Probability calculations (confidence intervals)

## Data Structures

### Activity Data Format

#### CPM Activities

```python
{
    'id': 'A',
    'activity': 'Design Phase',
    'duration': 5,
    'predecessors': '',
    'min_duration': 2,
    'crash_cost': 300,
    'normal_cost': 1000,
    'resource_demand': 2
}
```

#### PERT Activities

```python
{
    'id': 'A',
    'activity': 'Design Phase',
    'optimistic': 3,
    'most_likely': 5,
    'pessimistic': 8,
    'predecessors': ''
}
```

### Analysis Results Structure

```python
{
    'project_duration': 25,
    'critical_path': ['A', 'C', 'F', 'H'],
    'activities': {
        'A': {
            'ES': 0, 'EF': 5,
            'LS': 0, 'LF': 5,
            'float': 0,
            'critical': True
        }
    },
    'project_variance': 4.0,  # PERT only
    'project_std': 2.0        # PERT only
}
```

## API Reference

### Core Analysis APIs

#### CPM Analysis

```python
from pmhelper.core.cmp_analyzer import CPMAnalyzer

analyzer = CPMAnalyzer()
results = analyzer.analyze(activities_data)
crash_results = analyzer.crash_project(target_duration=20)
```

#### PERT Analysis

```python
from pmhelper.core.pert_analyzer import PERTAnalyzer

analyzer = PERTAnalyzer()
results = analyzer.analyze(activities_data)
probability = analyzer.calculate_completion_probability(25)
```

### GUI Integration

```python
from pmhelper.gui.main_window import MainWindow
import tkinter as tk

root = tk.Tk()
app = MainWindow(root)
root.mainloop()
```

### Command Line Interface

```bash
# CPM Analysis
python -m pmhelper.cli.cmp_cli analyze --file project.csv

# PERT Analysis
python -m pmhelper.cli.pert_cli analyze --file project.csv --probability 0.8
```

## Configuration

### Dependencies

**Core Requirements**:

- Python 3.8+
- tkinter (GUI framework)
- matplotlib (visualizations)
- networkx (graph operations)
- numpy (numerical calculations)
- scipy (statistical functions)
- pandas (data manipulation)

**Optional Dependencies**:

- openpyxl (Excel file support)
- pillow (image processing)

### Environment Variables

- `PMHELPER_DEBUG`: Enable debug logging
- `PMHELPER_DATA_DIR`: Default directory for data files
- `PMHELPER_EXPORT_DIR`: Default directory for exports

### File Formats

#### CSV Format

```csv
Activity,Duration,Predecessors,Min Duration,Crash Cost,Normal Cost
A,5,,2,300,1000
B,3,A,1,200,600
C,4,A,2,150,800
```

#### PERT CSV Format

```csv
Activity,Optimistic,Most Likely,Pessimistic,Predecessors
A,3,5,8,
B,2,3,5,A
C,3,4,6,A
```

## Performance Considerations

### Scalability

- Supports projects up to 1000 activities efficiently
- Network algorithms scale O(V + E) where V = activities, E = dependencies
- Visualization performance depends on network complexity

### Memory Usage

- Typical memory usage: 50-100 MB for medium projects (100-500 activities)
- Large projects (500+ activities) may require 200+ MB

### Optimization Tips

1. Use CSV format for faster loading
2. Limit concurrent visualizations for large projects
3. Close unused tabs to free memory
4. Use command-line interface for batch processing

## Extension Points

### Custom Analysis Modules

Extend the core package by implementing the analyzer interface:

```python
class CustomAnalyzer:
    def __init__(self):
        self.G = None

    def analyze(self, activities_data):
        # Custom analysis logic
        pass
```

### Custom Visualizations

Add new visualization types by extending the visualization utilities:

```python
from pmhelper.utils.visualizations import NetworkDiagramVisualizer

class CustomVisualizer(NetworkDiagramVisualizer):
    def create_custom_chart(self, data):
        # Custom chart implementation
        pass
```

### Custom Tab Integration

Add new tabs to the main interface:

```python
from pmhelper.gui.tabs import BaseTab

class CustomTab(BaseTab):
    def create_tab(self):
        # Custom tab implementation
        pass
```

## Testing Framework

### Unit Tests

Location: `tests/unit/`

**Test Categories**:

- Core algorithm tests
- Utility function tests
- Data validation tests

### Integration Tests

Location: `tests/integration/`

**Test Categories**:

- End-to-end workflow tests
- GUI integration tests
- File I/O tests

### Running Tests

```bash
# All tests
python -m pytest tests/

# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/
```

## Troubleshooting

### Common Issues

#### Import Errors

- Ensure all dependencies are installed: `pip install -r config/requirements.txt`
- Check Python version compatibility (3.8+)

#### GUI Issues

- Linux: Install tkinter separately (`sudo apt-get install python3-tk`)
- macOS: Ensure Xcode command line tools are installed

#### Performance Issues

- Reduce visualization complexity for large projects
- Use command-line interface for batch operations
- Increase system memory for very large projects

#### File Format Issues

- Verify CSV files use UTF-8 encoding
- Check for missing required columns
- Ensure numeric values are properly formatted

---

_This technical documentation is current as of PMHelper v1.0. For the latest updates, see the project repository._
