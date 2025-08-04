#!/usr/bin/env python3
"""
Debug Mode Detection

Test script to verify that mode detection is working correctly
"""

import sys
from pathlib import Path

# Add code directory to path
project_root = Path(__file__).parent
code_path = project_root / "code"
sys.path.insert(0, str(code_path))

def test_mode_detection():
    """Test the automatic mode detection function"""
    from cpm_app import CPMDesktopApp
    import tkinter as tk
    
    # Create test application
    root = tk.Tk()
    root.withdraw()  # Hide the window for testing
    app = CPMDesktopApp(root)
    
    print("Testing Mode Detection Function")
    print("=" * 40)
    
    # Test CPM headers
    cpm_headers = ['id', 'activity', 'duration', 'predecessors', 'min_duration']
    detected_mode = app.auto_detect_mode(cpm_headers)
    print(f"CPM Headers: {cpm_headers}")
    print(f"Detected Mode: {detected_mode}")
    print(f"Expected: deterministic")
    print(f"✅ PASS" if detected_mode == 'deterministic' else "❌ FAIL")
    print()
    
    # Test PERT headers
    pert_headers = ['id', 'activity', 'optimistic', 'most_likely', 'pessimistic', 'predecessors']
    detected_mode = app.auto_detect_mode(pert_headers)
    print(f"PERT Headers: {pert_headers}")
    print(f"Detected Mode: {detected_mode}")
    print(f"Expected: probabilistic")
    print(f"✅ PASS" if detected_mode == 'probabilistic' else "❌ FAIL")
    print()
    
    # Test current application state
    print("Current Application State:")
    print(f"Analysis Mode: {app.analysis_mode}")
    print(f"Current Analyzer: {type(app.current_analyzer).__name__ if app.current_analyzer else 'None'}")
    print(f"Mode Label Text: {app.mode_label.cget('text')}")
    
    root.destroy()

if __name__ == "__main__":
    test_mode_detection()
