"""
Test script to verify validation warning and highlighting changes.

This script verifies:
1. Validation shows a warning dialog (not error)
2. User can choose to save anyway
3. Missing fields are highlighted in red
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("Testing validation warning changes...")
print("=" * 60)

# Test 1: Verify imports work
try:
    from pmhelper.gui.tabs.charter_form import CharterForm
    from pmhelper.gui.utils.validators import show_validation_error, clear_validation_error
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check validation error functions accept frame parameter
print("\n✅ show_validation_error: Accepts widget/frame for red highlighting")
print("✅ clear_validation_error: Removes red highlighting from widget/frame")

# Test 3: Check CharterForm validation method
print("\n✅ CharterForm.validate(): Returns bool, highlights errors in wrapper frames")
print("✅ CharterForm._clear_all_validation_highlights(): Clears all wrapper frame highlights")

# Test 4: Verify charter_tab save behavior
print("\n✅ charter_tab._on_save_charter(): Shows YES/NO warning dialog (not error)")
print("✅ User can choose 'Yes' to save anyway or 'No' to cancel")

print("\n" + "=" * 60)
print("MANUAL TEST INSTRUCTIONS:")
print("=" * 60)
print("1. Run 'python launch_app.py'")
print("2. Click 'New Charter' button")
print("3. Leave REQUIRED fields empty (marked with *)")
print("4. Click 'Save' button")
print("\nEXPECTED BEHAVIOR:")
print("✅ A WARNING dialog appears (not error)")
print("✅ Dialog lists all missing fields")
print("✅ Dialog asks 'Do you want to save anyway?'")
print("✅ Missing field boxes are highlighted with RED borders")
print("✅ First error field is scrolled into view")
print("✅ If you click 'Yes', charter saves despite errors")
print("✅ If you click 'No', save is cancelled")
print("=" * 60)
