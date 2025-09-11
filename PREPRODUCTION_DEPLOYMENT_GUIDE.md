# PMHelper Preproduction Branch - Deployment Guide

## Overview

The `preproduction` branch contains only the essential files needed to run the PMHelper application, making it ready for production deployment with a minimal footprint.

## What's Included

### Core Application Files

- **`launch_app.py`** - Main application launcher
- **`README.md`** - User documentation and setup guide
- **`.gitignore`** - Git configuration for version control

### Source Code (`src/` directory)

- **Complete PMHelper package** with all GUI and core functionality
- **39 Python files** including:
  - Core analyzers (CPM, PERT, RCPS)
  - GUI components and tabs
  - Utilities and calculations
  - CLI interfaces

### Configuration (`config/` directory)

- **`requirements.txt`** - Python dependencies
- **`pyproject.toml`** - Project configuration
- **`pytest.ini`** - Testing configuration (for future development)

### Assets (`assets/` directory)

- **Sample CSV files** for testing and demonstration
- **26 files total** including various project examples

### Documentation (`docs/` directory)

- **API documentation**
- **Build instructions**
- **Changelog**
- **Development notes**

## What Was Removed (309 files)

### Development and Debug Files

- All `debug_*.py`, `test_*.py`, `analyze_*.py` files
- Quick test scripts and investigation tools
- Validation and verification scripts

### Documentation (Markdown Files)

- 86 markdown files with implementation reports
- Phase completion summaries
- Fix and improvement logs
- Technical analysis documents

### Build Artifacts and Cache

- `build/`, `dist/`, `htmlcov/` directories
- `__pycache__/` directories
- `.pytest_cache/`, `.coverage` files
- Virtual environment (`.venv/`)

### Development Directories

- `tests/` - Complete test suite (18,000+ files)
- `code/` - Legacy code backup
- `extensions/` - Development extensions
- `templates/` - Code templates
- `scripts/` - Build and maintenance scripts

## Deployment Instructions

### 1. Clone the Preproduction Branch

```bash
git clone -b preproduction https://github.com/seifouda/PMhelper.git
cd PMhelper
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r config/requirements.txt
```

### 3. Launch the Application

```bash
python launch_app.py
```

## Key Dependencies

- **Python 3.8+**
- **tkinter** (usually included with Python)
- **numpy** >= 1.21.0
- **pandas** >= 1.3.0
- **matplotlib** >= 3.4.0
- **networkx** >= 2.6
- **scipy** >= 1.7.0
- **plotly** >= 5.0.0

## Application Features

- ✅ **CPM Analysis** - Critical Path Method with float calculations
- ✅ **PERT Analysis** - Probabilistic scheduling with three-point estimates
- ✅ **RCPS** - Resource-Constrained Project Scheduling
- ✅ **Project Crashing** - Cost-optimized schedule compression
- ✅ **Network Diagrams** - Visual project network representation
- ✅ **Gantt Charts** - Timeline visualization
- ✅ **CSV/Excel Import/Export** - Data interchange capabilities
- ✅ **Probability Analysis** - Risk assessment and Monte Carlo simulation

## Production Readiness

- ✅ **Minimal Footprint** - Only essential files included
- ✅ **No Development Artifacts** - Clean codebase
- ✅ **Tested Core Functionality** - Application launches and runs
- ✅ **Complete Documentation** - User and API guides included
- ✅ **Sample Data** - Example projects for demonstration

## Branch Statistics

- **Files Removed**: 309 (including 18,980 total items)
- **Files Remaining**: ~88 essential files
- **Directories Cleaned**: 17 removed
- **Size Reduction**: Significant (removed build artifacts, tests, documentation)

## Maintenance

- The preproduction branch should be kept synchronized with stable releases from the main development branch
- Only production-ready, tested features should be merged
- This branch is ideal for deployment, distribution, and end-user installations

---

**Note**: This preproduction branch is ready for immediate deployment and contains everything needed to run the PMHelper application without any development overhead.
