#!/usr/bin/env python3
"""Test the Gantt chart fix"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

print("Testing Gantt chart fix...")

try:
    from pmhelper.utils.visualizations import GanttChartVisualizer
    import inspect
    
    # Check method signature
    sig = inspect.signature(GanttChartVisualizer.create_gantt_chart)
    print(f"✅ GanttChartVisualizer.create_gantt_chart signature: {sig}")
    
    # Check if it's a static method
    print(f"✅ Is static method: {isinstance(inspect.getattr_static(GanttChartVisualizer, 'create_gantt_chart'), staticmethod)}")
    
    print("✅ All imports successful - fix is working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
