# PMHelper Quick Launch Guide

## 🚀 **How to Run PMHelper**

### **Method 1: GUI Application (Recommended)**

```bash
cd d:\PMhelper
python launch_app.py
```

**Expected Output:**

```
Starting PMHelper - Project Management Analysis Tool...
Features available:
- Deterministic (CPM) analysis
- Probabilistic (PERT) analysis
- Resource-Constrained Project Scheduling (RCPS)
- Project crashing optimization
- Network diagrams and Gantt charts
- Probability analysis for PERT
- Risk analysis and Monte Carlo simulation
- CSV/Excel import/export functionality
- Command-line interface available
--------------------------------------------------
Application launched successfully!
Close the application window to exit.
```

### **Method 2: VS Code Integration**

1. Open `launch_app.py` in VS Code
2. Press **F5** (Debug) or **Ctrl+F5** (Run without debug)
3. Or right-click → "Run Python File in Terminal"

### **Method 3: CLI Tools**

```bash
cd d:\PMhelper\src

# CPM Analysis CLI
python -m pmhelper.cli.cpm_cli --help

# PERT Analysis CLI
python -m pmhelper.cli.pert_cli --help

# Generate sample data
python -m pmhelper.cli.cpm_cli sample test_project.csv
```

### **Method 4: Standalone Executable**

```bash
cd d:\PMhelper\dist\PMHelper
.\PMHelper.exe
```

## 🔧 **Troubleshooting**

### **If you get import errors:**

```bash
pip install -r requirements.txt
```

### **If tkinter is missing (Linux):**

```bash
sudo apt-get install python3-tk
```

### **Check your Python version:**

```bash
python --version
# Should be 3.7 or higher
```

### **Test dependencies:**

```bash
python -c "import tkinter, matplotlib, pandas, networkx, numpy, scipy"
```

## 📁 **Project Structure**

```
PMhelper/
├── launch_app.py          # 🎯 Main launcher (start here)
├── src/pmhelper/          # Core application code
├── tests/                 # Test suites
├── data/                  # Sample data files
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
└── dist/PMHelper/         # Built executable
```

## ✅ **Verification**

**Application is working correctly if you see:**

- ✅ GUI window opens with multiple tabs
- ✅ Input tab allows file selection
- ✅ Results tab shows analysis outputs
- ✅ Network tab displays project diagrams
- ✅ Gantt tab shows timeline charts
- ✅ Probability tab handles PERT analysis

**Need Help?**

- Check the `AGENT_PROMPT.md` for detailed troubleshooting
- Run tests: `python -m pytest tests/`
- Open an issue if problems persist

---

**Status**: ✅ Application verified and working  
**Last Updated**: July 21, 2025
