"""
Debug test - Shows what happens when fields are changed
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import ttk
from pmhelper.gui.models.charter_model import Charter, CharterMetadata, CharterStatus
from pmhelper.gui.models.template_model import Template
from pmhelper.gui.services.template_service import TemplateService
from pmhelper.gui.tabs.charter_form import CharterForm

print("Creating test window...")

root = tk.Tk()
root.title("Field Binding Test")
root.geometry("800x600")

# Load template
template_service = TemplateService()
template = template_service.load_template("standard_charter_v1")

if not template:
    print("ERROR: Could not load template")
    sys.exit(1)

print(f"Template loaded: {template.template_name}")

# Create charter
charter = Charter(metadata=CharterMetadata(
    charter_id="test123",
    created_date="2024-01-01",
    modified_date="2024-01-01",
    status=CharterStatus.DRAFT.value,
    template_id="standard_charter_v1",
    template_version="1.0"
))

print("Charter created")

# Change callback to see when fields change
def on_change():
    print("\n" + "="*60)
    print("FIELD CHANGED!")
    print("Charter data:")
    for section_id, fields in charter.data.items():
        print(f"  Section: {section_id}")
        for field_id, value in fields.items():
            print(f"    {field_id}: {value}")
    print("="*60 + "\n")

# Create form
print("Creating form...")
form = CharterForm(root, charter, template, on_change=on_change)
form.pack(fill="both", expand=True)

print("\n" + "="*60)
print("TEST INSTRUCTIONS:")
print("="*60)
print("1. Type something in the 'Project Name' field")
print("2. Watch the console for debug output")
print("3. If you see 'FIELD CHANGED!' output, bindings are working")
print("4. If you don't see output, bindings are broken")
print("="*60 + "\n")

root.mainloop()
