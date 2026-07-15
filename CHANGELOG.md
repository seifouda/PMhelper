# Changelog

All notable changes to PMHelper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-27

### Initial Release

This is the first public release of PMHelper, a comprehensive project management analysis tool.

### Added

#### Core Analysis Features

- **Critical Path Method (CPM)**: Complete implementation with forward/backward pass calculations
- **PERT Analysis**: Program Evaluation and Review Technique with three-point estimates
- **Project Crashing**: Cost-optimized schedule compression algorithms
- **Resource-Constrained Project Scheduling (RCPS)**: Multi-resource optimization
- **Monte Carlo Simulation**: Statistical project completion probability analysis
- **Sensitivity Analysis**: Impact assessment of parameter variations

#### User Interface

- **Multi-Tab GUI**: Input, Results, Network, Gantt, and Probability analysis tabs
- **Interactive Network Diagrams**: Dynamic project network visualization with critical path highlighting
- **Gantt Charts**: Professional timeline views with resource allocation
- **Data Grid**: Spreadsheet-like interface for activity data editing
- **Real-time Updates**: Automatic recalculation when data changes

#### Data Management

- **CSV Import/Export**: Full support for comma-separated value files
- **Excel Integration**: Read and write .xlsx files with openpyxl
- **Sample Projects**: Pre-loaded examples for different industries
- **Data Validation**: Comprehensive input validation and error handling
- **Project Templates**: Industry-standard project structures

#### Command Line Interface

- **pmhelper-cpm**: Command-line CPM analysis tool
- **pmhelper-pert**: Command-line PERT analysis tool
- **Batch Processing**: Support for automated analysis workflows
- **JSON Output**: Machine-readable results format

#### Visualization

- **Network Graphs**: Professional project network diagrams
- **Critical Path Highlighting**: Visual identification of critical activities
- **Probability Distributions**: Statistical charts for PERT analysis
- **Customizable Charts**: Adjustable styling and export options
- **Multiple Formats**: Export to PNG, SVG, PDF formats

#### Distribution

- **Python Package**: Installable via pip from PyPI
- **Windows Executable**: Standalone .exe file with all dependencies
- **Cross-Platform**: Support for Windows, macOS, and Linux
- **No Installation Required**: Portable Windows application

### Technical Details

#### Architecture

- **Modular Design**: Separate core analysis engines, GUI components, and utilities
- **Error Recovery**: Graceful handling of invalid inputs and edge cases
- **Performance Optimized**: Efficient algorithms for large project analysis

#### Dependencies

- **NumPy**: Numerical computing foundation
- **Pandas**: Data manipulation and analysis
- **SciPy**: Scientific computing for statistical analysis
- **NetworkX**: Graph theory and network analysis
- **Matplotlib**: Static plotting and visualization
- **Plotly**: Interactive visualization capabilities
- **Tkinter**: GUI framework (standard library)
- **openpyxl**: Excel file support

#### Testing

- **Unit Tests**: Comprehensive test coverage >90%
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Benchmarking for large projects
- **Cross-Platform Tests**: Validation on multiple operating systems

### Known Issues

#### Limitations

- **Large Projects**: Performance may degrade for projects with >1000 activities
- **Memory Usage**: High memory consumption for complex Monte Carlo simulations
- **Export Formats**: Limited customization options for exported visualizations

#### Platform-Specific Issues

- **Windows Defender**: May flag standalone executable as potentially unwanted software (false positive)
- **macOS Gatekeeper**: Unsigned application warning (workaround: use Python version)
- **Linux Dependencies**: Some distributions may require manual tkinter installation

### Migration Guide

This is the initial release, so no migration is required. For users upgrading from development versions:

1. Uninstall any development versions
2. Install from PyPI: `pip install pmhelper`
3. Update any scripts using the new command-line interface names

### Contributors

- PMHelper Team - Core development
- Beta testers - Quality assurance and feedback
- Academic advisors - Algorithm validation and testing

---

## [Unreleased]

### Built but not yet cut as a release

These are in the tree on `EDU_PROD` and were previously listed below as "planned":

- **Educational edition (PMHelper Edu)** — the app the project now ships
  (`python -m pmhelper.edu_main`). A 10-lecture guided workflow with worked
  solutions: WBS, CPM/AOA, three-point/PERT, probability, crashing, RCPS,
  resource leveling, EVM, Monte Carlo, risk, RACI, SWOT/PESTEL, charter, and
  project selection. Note the `pmhelper-gui` console script still launches the
  legacy v1 window.
- **Web Interface** — Angular app in `web/`, served by the FastAPI app.
- **API Integration** — REST API under `src/pmhelper/server/` (`/api/web/*`,
  `/api/calculations/*`, `/api/projects/*`, `/api/analyze/*`, `/api/selection/*`)
  plus a WebSocket endpoint.
- **Risk analysis, cost optimization, multi-objective/Pareto, NPV, and project
  selection (AHP, linear scoring, benefit-cost, portfolio)** — with CLIs
  (`risk_cli`, `optimization_cli`, `selection_cli`) and user guides in `docs/guides/`.

See `docs/releases/RELEASE_NOTES_v1.1.0.md`, which describes v1.1.0 as a release
candidate.

### Planned Features

#### Version 1.1.0 (Next Minor Release)

- **Enhanced Reporting**: Export to PowerPoint and Word formats
- **Performance Improvements**: Faster loading for large projects

#### Version 2.0.0 (Next Major Release)

- **Machine Learning**: Predictive duration estimation based on historical data
- **Portfolio Management**: Multi-project dashboard and optimization
- **Collaborative Features**: Multi-user project editing and sharing
- **Mobile Applications**: iOS and Android companion apps

### Development Roadmap

- ~~**Q1 2026**: Web interface~~ — built (`web/`); enhanced reporting still open
- ~~**Q2 2026**: API development and integrations~~ — built (`src/pmhelper/server/`)
- **Q3 2026**: Machine learning features
- **Q4 2026**: Mobile applications and collaboration tools

---

_For more information about upcoming features and development progress, see the [project roadmap](https://github.com/seifouda/PMhelper/projects) on GitHub._
