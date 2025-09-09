# PMHelper API Documentation

This document provides comprehensive API reference for PMHelper's programmatic interfaces, suitable for developers who want to integrate PMHelper into their own applications or extend its functionality.

## Core Analysis APIs

### CPM Analyzer

The `CPMAnalyzer` class provides deterministic project scheduling analysis using the Critical Path Method.

#### Class: `pmhelper.core.cmp_analyzer.CPMAnalyzer`

##### Constructor

```python
def __init__(self):
    """
    Initialize CPM analyzer.

    Attributes:
        G (networkx.DiGraph): Project network graph
        critical_path (list): List of critical activities
        project_duration (float): Total project duration
    """
```

##### Methods

```python
def analyze(self, activities_data: List[Dict]) -> Dict:
    """
    Perform complete CPM analysis.

    Args:
        activities_data (List[Dict]): List of activity dictionaries containing:
            - id (str): Activity identifier
            - activity (str): Activity name
            - duration (float): Activity duration
            - predecessors (str): Comma-separated predecessor IDs
            - min_duration (float, optional): Minimum duration for crashing
            - crash_cost (float, optional): Cost per unit time reduction
            - normal_cost (float, optional): Normal activity cost
            - resource_demand (int, optional): Resource units required

    Returns:
        Dict: Analysis results containing:
            - project_duration (float): Total project duration
            - critical_path (List[str]): Critical path activity IDs
            - activities (Dict): Activity details with timing information
            - network_metrics (Dict): Additional network statistics

    Raises:
        ValueError: If activity data is invalid
        NetworkError: If circular dependencies detected

    Example:
        >>> analyzer = CPMAnalyzer()
        >>> activities = [
        ...     {'id': 'A', 'activity': 'Design', 'duration': 5, 'predecessors': ''},
        ...     {'id': 'B', 'activity': 'Code', 'duration': 8, 'predecessors': 'A'}
        ... ]
        >>> results = analyzer.analyze(activities)
        >>> print(f"Project duration: {results['project_duration']}")
    """

def crash_project(self, target_duration: float, max_budget: float = None,
                 strategy: str = 'lowest_cost') -> Dict:
    """
    Optimize project duration through activity crashing.

    Args:
        target_duration (float): Desired project completion time
        max_budget (float, optional): Maximum budget for crashing
        strategy (str): Crashing strategy ('lowest_cost', 'best_efficiency')

    Returns:
        Dict: Crashing results containing:
            - original_duration (float): Initial project duration
            - final_duration (float): Duration after crashing
            - total_crash_cost (float): Total cost of crashing
            - crashed_activities (List[Dict]): Details of crashed activities
            - cost_benefit_analysis (Dict): Economic analysis

    Raises:
        ValueError: If target duration is invalid
        InsufficientDataError: If crash data is missing

    Example:
        >>> crash_results = analyzer.crash_project(target_duration=20, max_budget=5000)
        >>> print(f"Cost to crash: ${crash_results['total_crash_cost']}")
    """

def build_cmp_schedule_table(self) -> List[Dict]:
    """
    Generate detailed schedule table for CPM analysis.

    Returns:
        List[Dict]: Schedule table with activity timing details
    """

def rcps_heuristic_schedule_table(self, resource_limit: int,
                                 priority_rule: str = 'minimum_slack') -> Dict:
    """
    Generate resource-constrained project schedule.

    Args:
        resource_limit (int): Maximum available resources per time unit
        priority_rule (str): Priority rule for resource allocation

    Returns:
        Dict: RCPS schedule with resource utilization details
    """
```

### PERT Analyzer

The `PERTAnalyzer` class handles probabilistic project analysis using three-point estimates.

#### Class: `pmhelper.core.pert_analyzer.PERTAnalyzer`

##### Constructor

```python
def __init__(self):
    """
    Initialize PERT analyzer.

    Attributes:
        G (networkx.DiGraph): Project network graph
        critical_paths (List[List[str]]): All critical paths
        project_variance (float): Total project variance
        project_std (float): Project standard deviation
    """
```

##### Methods

```python
def analyze(self, activities_data: List[Dict]) -> Dict:
    """
    Perform PERT analysis with probabilistic calculations.

    Args:
        activities_data (List[Dict]): List of activity dictionaries containing:
            - id (str): Activity identifier
            - activity (str): Activity name
            - optimistic (float): Optimistic time estimate
            - most_likely (float): Most likely time estimate
            - pessimistic (float): Pessimistic time estimate
            - predecessors (str): Comma-separated predecessor IDs

    Returns:
        Dict: PERT analysis results containing:
            - expected_duration (float): Expected project duration
            - project_variance (float): Project variance
            - project_std (float): Project standard deviation
            - critical_path (List[str]): Critical path activities
            - activities (Dict): Activity details with PERT calculations

    Example:
        >>> analyzer = PERTAnalyzer()
        >>> activities = [
        ...     {'id': 'A', 'optimistic': 3, 'most_likely': 5, 'pessimistic': 8, 'predecessors': ''}
        ... ]
        >>> results = analyzer.analyze(activities)
    """

def calculate_completion_probability(self, target_duration: float) -> float:
    """
    Calculate probability of completing project by target duration.

    Args:
        target_duration (float): Target completion time

    Returns:
        float: Probability of completion (0.0 to 1.0)

    Example:
        >>> probability = analyzer.calculate_completion_probability(25.0)
        >>> print(f"Probability: {probability:.2%}")
    """

def calculate_duration_for_probability(self, probability: float) -> float:
    """
    Calculate duration for desired completion probability.

    Args:
        probability (float): Desired probability (0.0 to 1.0)

    Returns:
        float: Duration for specified probability

    Example:
        >>> duration_80_percent = analyzer.calculate_duration_for_probability(0.8)
    """

def get_project_statistics(self) -> Dict:
    """
    Get comprehensive project statistics.

    Returns:
        Dict: Project statistics including:
            - expected_duration (float): Expected completion time
            - variance (float): Project variance
            - std_deviation (float): Standard deviation
            - confidence_intervals (Dict): 68%, 95%, 99% intervals
    """
```

### Network Builder

Utility class for network construction and graph operations.

#### Class: `pmhelper.core.network_builder.NetworkBuilder`

```python
def build_network(self, activities_data: List[Dict]) -> networkx.DiGraph:
    """
    Build project network from activity data.

    Args:
        activities_data (List[Dict]): Activity definitions

    Returns:
        networkx.DiGraph: Project network graph
    """

def forward_pass(self, G: networkx.DiGraph) -> networkx.DiGraph:
    """
    Calculate Early Start and Early Finish times.

    Args:
        G (networkx.DiGraph): Project network

    Returns:
        networkx.DiGraph: Network with ES/EF calculations
    """

def backward_pass(self, G: networkx.DiGraph) -> networkx.DiGraph:
    """
    Calculate Late Start and Late Finish times.

    Args:
        G (networkx.DiGraph): Project network with ES/EF

    Returns:
        networkx.DiGraph: Network with LS/LF calculations
    """

def calculate_float(self, G: networkx.DiGraph) -> networkx.DiGraph:
    """
    Calculate total float for all activities.

    Args:
        G (networkx.DiGraph): Network with timing calculations

    Returns:
        networkx.DiGraph: Network with float calculations
    """
```

## Utility APIs

### File Handlers

#### Class: `pmhelper.utils.file_handlers.FileHandler`

```python
@staticmethod
def load_csv(filepath: str) -> List[Dict]:
    """
    Load project data from CSV file.

    Args:
        filepath (str): Path to CSV file

    Returns:
        List[Dict]: Activity data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValidationError: If file format is invalid
    """

@staticmethod
def save_csv(data: List[Dict], filepath: str) -> None:
    """
    Save project data to CSV file.

    Args:
        data (List[Dict]): Activity data to save
        filepath (str): Output file path
    """

@staticmethod
def load_excel(filepath: str, sheet_name: str = None) -> List[Dict]:
    """
    Load project data from Excel file.

    Args:
        filepath (str): Path to Excel file
        sheet_name (str, optional): Specific sheet to load

    Returns:
        List[Dict]: Activity data
    """
```

### Calculation Utilities

#### Time Calculations

```python
from pmhelper.utils.calculations import TimeCalculations

def calculate_pert_estimates(optimistic: float, most_likely: float,
                           pessimistic: float) -> Tuple[float, float]:
    """
    Calculate PERT expected time and variance.

    Args:
        optimistic (float): Optimistic time estimate
        most_likely (float): Most likely time estimate
        pessimistic (float): Pessimistic time estimate

    Returns:
        Tuple[float, float]: (expected_time, variance)

    Example:
        >>> expected, variance = calculate_pert_estimates(3, 5, 8)
        >>> print(f"Expected: {expected}, Variance: {variance}")
    """
```

#### Cost Calculations

```python
from pmhelper.utils.calculations import CostCalculations

def calculate_crash_efficiency(crash_cost: float, time_saved: float) -> float:
    """
    Calculate crashing efficiency (cost per unit time saved).

    Args:
        crash_cost (float): Cost of crashing
        time_saved (float): Time reduction achieved

    Returns:
        float: Efficiency ratio (cost/time)
    """
```

### Visualization APIs

#### Network Diagram Visualizer

```python
from pmhelper.utils.visualizations import NetworkDiagramVisualizer

class NetworkDiagramVisualizer:
    def create_network_diagram(self, G: networkx.DiGraph,
                             highlight_critical: bool = True) -> matplotlib.figure.Figure:
        """
        Create network diagram visualization.

        Args:
            G (networkx.DiGraph): Project network
            highlight_critical (bool): Whether to highlight critical path

        Returns:
            matplotlib.figure.Figure: Network diagram figure
        """
```

#### Gantt Chart Visualizer

```python
from pmhelper.utils.visualizations import GanttChartVisualizer

class GanttChartVisualizer:
    def create_gantt_chart(self, activities: Dict,
                          show_critical: bool = True) -> matplotlib.figure.Figure:
        """
        Create Gantt chart visualization.

        Args:
            activities (Dict): Activity timing data
            show_critical (bool): Whether to highlight critical path

        Returns:
            matplotlib.figure.Figure: Gantt chart figure
        """
```

## GUI Integration APIs

### Main Window

```python
from pmhelper.gui.main_window import MainWindow
import tkinter as tk

# Basic GUI integration
root = tk.Tk()
app = MainWindow(root)

# Access current analyzer
analyzer = app.analyzer

# Get current analysis mode
mode = app.analysis_mode  # 'cpm' or 'pert'

# Get activities data
activities = app.get_activities_data()

# Run analysis programmatically
app.analyze_project()
```

### Tab Integration

```python
# Access specific tabs
input_tab = app.input_tab
results_tab = app.results_tab
network_tab = app.network_tab

# Update visualizations
network_tab.update_network(analyzer.G)
results_tab.update_results(analysis_results)
```

## Command Line Interface

### CPM CLI

```bash
# Basic CPM analysis
python -m pmhelper.cli.cmp_cli analyze --file project.csv

# CPM with crashing
python -m pmhelper.cli.cmp_cli crash --file project.csv --target 20 --budget 5000

# Export results
python -m pmhelper.cli.cmp_cli analyze --file project.csv --output results.csv
```

### PERT CLI

```bash
# Basic PERT analysis
python -m pmhelper.cli.pert_cli analyze --file project.csv

# Probability calculation
python -m pmhelper.cli.pert_cli probability --file project.csv --target 25

# Risk analysis
python -m pmhelper.cli.pert_cli risk --file project.csv --confidence 0.8
```

### CLI API (Programmatic)

```python
from pmhelper.cli.cmp_cli import analyze_project, crash_optimization
from pmhelper.cli.pert_cli import analyze_project as pert_analyze

# CPM analysis
cpm_results = analyze_project('project.csv')

# Project crashing
crash_results = crash_optimization('project.csv', target_duration=20)

# PERT analysis
pert_results = pert_analyze('project.csv')
```

## Error Handling

### Custom Exceptions

```python
from pmhelper.exceptions import (
    PMHelperError,
    ValidationError,
    NetworkError,
    AnalysisError,
    FileFormatError
)

try:
    results = analyzer.analyze(activities)
except ValidationError as e:
    print(f"Data validation failed: {e}")
except NetworkError as e:
    print(f"Network construction failed: {e}")
except AnalysisError as e:
    print(f"Analysis failed: {e}")
```

### Error Codes

- `VALIDATION_ERROR`: Invalid input data
- `NETWORK_ERROR`: Network construction failed
- `ANALYSIS_ERROR`: Analysis calculation failed
- `FILE_ERROR`: File I/O operation failed
- `RESOURCE_ERROR`: Insufficient system resources

## Extension Points

### Custom Analyzers

```python
from pmhelper.core.base_analyzer import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def analyze(self, activities_data):
        # Custom analysis implementation
        pass

    def get_results(self):
        # Return custom results format
        pass
```

### Custom Visualizations

```python
from pmhelper.utils.visualizations import BaseVisualizer

class CustomVisualizer(BaseVisualizer):
    def create_custom_chart(self, data):
        # Custom visualization implementation
        pass
```

### Plugin System

```python
from pmhelper.plugins import register_plugin

@register_plugin('custom_feature')
class CustomFeature:
    def execute(self, *args, **kwargs):
        # Custom feature implementation
        pass
```

## Configuration

### Environment Variables

```python
import os

# Set configuration
os.environ['PMHELPER_DEBUG'] = 'true'
os.environ['PMHELPER_DATA_DIR'] = '/path/to/data'
os.environ['PMHELPER_EXPORT_DIR'] = '/path/to/exports'
```

### Configuration File

```python
from pmhelper.config import PMHelperConfig

config = PMHelperConfig()
config.set('visualization.default_layout', 'hierarchical')
config.set('analysis.max_iterations', 1000)
config.save()
```

## Performance Optimization

### Batch Processing

```python
from pmhelper.batch import BatchProcessor

processor = BatchProcessor()
results = processor.process_multiple_projects([
    'project1.csv',
    'project2.csv',
    'project3.csv'
])
```

### Memory Management

```python
# For large projects, use streaming analysis
from pmhelper.streaming import StreamingAnalyzer

analyzer = StreamingAnalyzer()
for chunk in analyzer.analyze_streaming(large_project_data):
    process_chunk(chunk)
```

## Testing Integration

### Unit Testing Support

```python
from pmhelper.testing import TestHelper

class TestMyProject(unittest.TestCase):
    def setUp(self):
        self.helper = TestHelper()
        self.sample_data = self.helper.get_sample_cpm_data()

    def test_analysis(self):
        analyzer = CPMAnalyzer()
        results = analyzer.analyze(self.sample_data)
        self.assertIsNotNone(results)
```

### Mock Data Generation

```python
from pmhelper.testing import MockDataGenerator

generator = MockDataGenerator()
test_project = generator.create_random_project(
    num_activities=50,
    complexity='medium'
)
```

## Version Information

```python
import pmhelper

# Get version information
print(pmhelper.__version__)
print(pmhelper.__author__)
print(pmhelper.__license__)

# Check feature availability
print(pmhelper.features.has_excel_support())
print(pmhelper.features.has_advanced_visualization())
```

---

_This API documentation is current as of PMHelper v1.0. For the latest updates and examples, see the project repository and test files._
