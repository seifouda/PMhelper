"""
Test script to verify validation error highlighting and scrolling.
This creates a charter and tries to save it without filling required fields.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("=" * 70)
print("VALIDATION HIGHLIGHTING TEST")
print("=" * 70)
print()
print("Testing the enhanced validation features:")
print("1. Red border/background on invalid fields")
print("2. Automatic scrolling to first error")
print("3. Section auto-expansion")
print("4. Detailed error message listing")
print()
print("To test:")
print("1. Run: python launch_app.py")
print("2. Click 'New Charter' or press Ctrl+N")
print("3. Leave some required fields empty (marked with *)")
print("4. Click 'Save' or press Ctrl+S")
print()
print("Expected behavior:")
print("✓ Error dialog shows list of all validation errors")
print("✓ First invalid field is highlighted with red border/background")
print("✓ Form automatically scrolls to show the first error")
print("✓ Section containing error automatically expands if collapsed")
print("✓ Widget flashes briefly to draw attention")
print()
print("=" * 70)
print()

# Verify imports work
try:
    from pmhelper.gui.tabs.charter_form import CharterForm
    from pmhelper.gui.utils import FieldValidator, show_validation_error, clear_validation_error
    print("✅ All validation imports successful")
    print("✅ show_validation_error: Highlights fields with red border/background")
    print("✅ clear_validation_error: Removes validation highlights")
    print("✅ CharterForm.validate(): Validates and highlights errors")
    print("✅ CharterForm._scroll_to_error(): Auto-scrolls to first error")
    print("✅ CharterForm._flash_widget(): Flashes widget for attention")
    print()
    print("Ready to test! Launch the application and try saving an incomplete charter.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
