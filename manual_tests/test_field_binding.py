"""
Quick test to check if field changes are being saved to charter data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pmhelper.gui.models.charter_model import Charter, CharterMetadata, CharterStatus
from pmhelper.gui.models.template_model import Template
from pmhelper.gui.services.template_service import TemplateService

print("Testing field data connections...")
print("=" * 60)

# Load template
template_service = TemplateService()
template = template_service.load_template("standard_charter_v1")

if not template:
    print("❌ Failed to load template")
    sys.exit(1)

print(f"✅ Template loaded: {template.template_name}")

# Create charter
charter = Charter(metadata=CharterMetadata(
    charter_id="test123",
    created_date="2024-01-01",
    modified_date="2024-01-01",
    status=CharterStatus.DRAFT.value,
    template_id="standard_charter_v1",
    template_version="1.0"
))

print(f"✅ Charter created")

# Test setting and getting values
print("\nTesting set_field_value and get_field_value:")
charter.set_field_value("identification", "project_name", "Test Project")
value = charter.get_field_value("identification", "project_name")
print(f"  Set: 'Test Project'")
print(f"  Get: '{value}'")
if value == "Test Project":
    print("  ✅ Data saved correctly")
else:
    print(f"  ❌ Data NOT saved! Got: {value}")

# Check charter data structure
print(f"\nCharter data: {charter.data}")

print("\n" + "=" * 60)
print("If the above test passed, the Charter model is working.")
print("The issue may be with widget bindings or event handlers.")
print("=" * 60)
