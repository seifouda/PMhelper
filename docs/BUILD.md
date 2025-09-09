# PMHelper Build Guide

This guide provides step-by-step instructions for building PMHelper into a standalone executable file that can be distributed to users without requiring Python installation.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Automated Build Process](#automated-build-process)
4. [Manual Build Process](#manual-build-process)
5. [Build Configuration](#build-configuration)
6. [Distribution Packaging](#distribution-packaging)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Build Options](#advanced-build-options)

## Overview

PMHelper can be built into standalone executables using PyInstaller, which packages the Python interpreter and all dependencies into a single file or directory. This allows distribution to users who don't have Python installed.

### Build Outputs

- **Single Executable**: One `.exe` file containing everything (Windows) or equivalent for other platforms
- **Directory Distribution**: Folder containing executable and supporting files
- **Installation Package**: Complete distribution with documentation and samples

## Prerequisites

### System Requirements

**Development Environment**:

- Python 3.8 or higher
- Windows, macOS, or Linux
- At least 2GB free disk space
- 4GB RAM recommended

**Required Tools**:

- PyInstaller (automatically installed by build script)
- Git (for version control)
- 7-Zip or equivalent (for distribution packaging)

### Install Dependencies

Before building, ensure all dependencies are installed:

```bash
# Install production dependencies
pip install -r config/requirements.txt

# Install build dependencies
pip install pyinstaller
pip install setuptools
```

### Verify Installation

Test that PMHelper runs correctly before building:

```bash
# Test the application
python src/main.py

# Run tests to ensure stability
python -m pytest tests/unit/
```

## Automated Build Process

The easiest way to build PMHelper is using the provided build script.

### Quick Build

```bash
# Run the automated build script
python scripts/build.py
```

This script will:

1. ✅ Clean previous builds
2. ✅ Install/update dependencies
3. ✅ Run basic tests
4. ✅ Build the executable
5. ✅ Create distribution package
6. ✅ Verify the build

### Build Script Options

```bash
# Build with specific options
python scripts/build.py --clean --test --package

# Debug build (includes console)
python scripts/build.py --debug

# Skip tests (faster build)
python scripts/build.py --no-test

# Custom output directory
python scripts/build.py --output-dir "C:\MyBuilds"
```

### Automated Build Output

After successful build, you'll find:

```
dist/
├── PMHelper.exe                    # Main executable
├── PMHelper-Package/               # Complete distribution
│   ├── PMHelper.exe                # Executable
│   ├── README.md                   # User documentation
│   ├── assets/                     # Sample data files
│   ├── docs/                       # Documentation
│   └── requirements.txt            # Dependencies list
└── build/                          # Temporary build files
```

## Manual Build Process

For more control over the build process, you can run PyInstaller manually.

### Step 1: Prepare Build Environment

```bash
# Clean previous builds
rm -rf dist/ build/ *.spec

# Ensure dependencies are current
pip install --upgrade -r config/requirements.txt
pip install --upgrade pyinstaller
```

### Step 2: Create Build Specification

Create a PyInstaller spec file for custom build configuration:

```python
# pmhelper.spec
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Project paths
project_root = Path.cwd()
src_path = project_root / "src"

block_cipher = None

a = Analysis(
    [str(src_path / "main.py")],
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        (str(project_root / "assets"), "assets"),
        (str(project_root / "config"), "config"),
        (str(project_root / "docs"), "docs"),
    ],
    hiddenimports=[
        'tkinter',
        'matplotlib.backends.backend_tkagg',
        'scipy.special._ufuncs_cxx',
        'scipy.sparse.csgraph._validation',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'jupyter',
        'IPython',
        'sphinx',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PMHelper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debug builds
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "icon.ico") if (project_root / "assets" / "icon.ico").exists() else None,
)
```

### Step 3: Build Executable

```bash
# Build using spec file
pyinstaller pmhelper.spec

# Or build directly (simpler)
pyinstaller --onefile --windowed --name PMHelper \
    --add-data "assets;assets" \
    --add-data "config;config" \
    --hidden-import tkinter \
    --hidden-import matplotlib.backends.backend_tkagg \
    src/main.py
```

### Step 4: Test the Executable

```bash
# Test the built executable
./dist/PMHelper.exe  # Windows
./dist/PMHelper      # Linux/macOS

# Test with sample data
./dist/PMHelper.exe --load assets/sample_project.csv
```

## Build Configuration

### PyInstaller Options Explained

**Essential Options**:

- `--onefile`: Create single executable file
- `--windowed`: Hide console window (GUI apps)
- `--name`: Specify executable name
- `--icon`: Set application icon

**Data and Dependencies**:

- `--add-data`: Include data files (format: "source;dest" on Windows, "source:dest" on Unix)
- `--hidden-import`: Force include modules not detected automatically
- `--exclude-module`: Exclude unnecessary modules

**Advanced Options**:

- `--upx-dir`: Path to UPX compressor for smaller files
- `--clean`: Clean build cache before building
- `--noconfirm`: Overwrite output without asking

### Hidden Imports

PMHelper requires these hidden imports for proper functionality:

```python
hidden_imports = [
    'tkinter',                          # GUI framework
    'tkinter.ttk',                      # Themed widgets
    'matplotlib.backends.backend_tkagg', # Matplotlib-Tkinter integration
    'scipy.special._ufuncs_cxx',        # SciPy functions
    'scipy.sparse.csgraph._validation', # Graph algorithms
    'pandas._libs.tslibs.timedeltas',   # Pandas time handling
    'networkx.algorithms.flow',         # Network flow algorithms
    'numpy.random._pickle',             # NumPy random state
]
```

### Data Files

Include these data files in the build:

```python
datas = [
    ('assets/*', 'assets'),           # Sample data and images
    ('config/*', 'config'),           # Configuration files
    ('docs/*.md', 'docs'),            # Documentation
    ('README.md', '.'),               # Main readme
]
```

## Distribution Packaging

### Create Complete Distribution

```bash
# Create distribution directory
mkdir PMHelper-v1.0-Distribution

# Copy essential files
cp dist/PMHelper.exe PMHelper-v1.0-Distribution/
cp README.md PMHelper-v1.0-Distribution/
cp -r assets/ PMHelper-v1.0-Distribution/
cp -r docs/ PMHelper-v1.0-Distribution/
cp config/requirements.txt PMHelper-v1.0-Distribution/

# Create installation guide
cat > PMHelper-v1.0-Distribution/INSTALL.txt << EOF
PMHelper v1.0 - Installation Instructions

1. Extract all files to a folder on your computer
2. Double-click PMHelper.exe to run the application
3. No additional installation required!

For help, see the User Guide in the docs/ folder.
EOF
```

### Create ZIP Archive

```bash
# Create compressed archive
zip -r PMHelper-v1.0-Windows.zip PMHelper-v1.0-Distribution/

# Or using 7-Zip
7z a PMHelper-v1.0-Windows.7z PMHelper-v1.0-Distribution/
```

### Windows Installer (Optional)

For professional distribution, create an installer using NSIS or Inno Setup:

```nsis
; Example NSIS installer script
!define APPNAME "PMHelper"
!define VERSION "1.0"

Name "${APPNAME} ${VERSION}"
OutFile "PMHelper-Setup-${VERSION}.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\PMHelper.exe"
    File "README.md"
    SetOutPath "$INSTDIR\assets"
    File /r "assets\*"
    SetOutPath "$INSTDIR\docs"
    File /r "docs\*"

    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\PMHelper.exe"
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\PMHelper.exe"
SectionEnd
```

## Troubleshooting

### Common Build Issues

#### 1. "Module not found" errors

**Problem**: PyInstaller can't find required modules
**Solution**: Add hidden imports

```bash
pyinstaller --hidden-import missing_module_name src/main.py
```

#### 2. Large executable size

**Problem**: Executable is too large (>100MB)
**Solutions**:

- Exclude unnecessary modules: `--exclude-module module_name`
- Use UPX compression: `--upx-dir /path/to/upx`
- Use directory distribution instead of `--onefile`

#### 3. "Failed to execute script" error

**Problem**: Runtime error in built executable
**Solutions**:

- Test with console enabled: Remove `--windowed` flag
- Check for missing data files
- Verify all dependencies are included

#### 4. Antivirus false positives

**Problem**: Antivirus software flags executable as malicious
**Solutions**:

- Use code signing certificate
- Submit to antivirus vendors for whitelisting
- Use directory distribution instead of single file

#### 5. Application won't start

**Problem**: Executable starts but crashes immediately
**Solutions**:

- Check for missing DLL files on target system
- Include Microsoft Visual C++ Redistributable
- Test on clean virtual machine

### Debug Build

For troubleshooting, create a debug build:

```bash
pyinstaller --onefile --console --debug all \
    --name PMHelper-Debug \
    src/main.py
```

Debug builds show:

- Import errors
- Missing files
- Runtime exceptions
- Performance information

### Build Log Analysis

PyInstaller creates detailed logs. Check these files:

```
build/PMHelper/warn-PMHelper.txt      # Warnings and issues
build/PMHelper/Analysis-00.toc       # Analyzed files
dist/PMHelper.exe.log                # Runtime log (debug builds)
```

## Advanced Build Options

### Cross-Platform Building

**Build for Windows on Linux** (using Wine):

```bash
# Install Wine and Windows Python
sudo apt install wine
# Download and install Python in Wine
# Then build normally
```

**Build for multiple platforms**:

```bash
# Use GitHub Actions or similar CI/CD
# See .github/workflows/build.yml example
```

### Optimization Techniques

#### 1. Reduce Size

```bash
# Exclude test modules
--exclude-module pytest
--exclude-module unittest

# Exclude development tools
--exclude-module IPython
--exclude-module jupyter

# Use UPX compression
--upx-dir /usr/bin
```

#### 2. Improve Startup Time

```bash
# Use directory distribution
# Remove --onefile flag for faster startup

# Lazy imports in code
# Import modules only when needed
```

#### 3. Memory Optimization

```python
# In your spec file
import sys
sys.modules['pywin32_system32'] = None  # Reduce Windows dependencies
```

### Custom Build Hooks

Create custom hooks for special requirements:

```python
# hooks/hook-pmhelper.py
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all pmhelper data
datas = collect_data_files('pmhelper')
hiddenimports = collect_submodules('pmhelper')
```

### Continuous Integration

Example GitHub Actions workflow:

```yaml
# .github/workflows/build.yml
name: Build PMHelper

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r config/requirements.txt
          pip install pyinstaller

      - name: Build executable
        run: python scripts/build.py

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: PMHelper-${{ matrix.os }}
          path: dist/
```

## Quality Assurance

### Pre-Build Checklist

- [ ] All tests pass: `python -m pytest tests/`
- [ ] Application runs correctly: `python src/main.py`
- [ ] Dependencies are current: `pip list --outdated`
- [ ] Documentation is updated
- [ ] Version numbers are correct

### Post-Build Testing

- [ ] Executable starts without errors
- [ ] All features work correctly
- [ ] Sample data loads properly
- [ ] Export/import functions work
- [ ] GUI displays correctly
- [ ] No missing file errors

### Distribution Testing

- [ ] Test on clean Windows machine
- [ ] Test with different user permissions
- [ ] Verify antivirus compatibility
- [ ] Check file associations work
- [ ] Validate installer (if used)

---

**Building PMHelper into an executable ensures easy distribution and professional deployment. Follow this guide for reliable, optimized builds suitable for end-user distribution.**
