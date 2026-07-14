"""
Test script for Sprint 1 - Project Charter Feature
Tests basic functionality without launching the full GUI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pmhelper.gui.models import Charter, CharterMetadata, CharterStatus, Template
from pmhelper.gui.services import TemplateService
from datetime import datetime
import uuid

def test_models():
    """Test data models"""
    print("\n=== Testing Data Models ===")
    
    # Test CharterMetadata
    meta = CharterMetadata(
        charter_id=str(uuid.uuid4()),
        created_date=datetime.now().isoformat(),
        modified_date=datetime.now().isoformat()
    )
    print(f"✓ CharterMetadata created: {meta.charter_id[:8]}...")
    
    # Test Charter
    charter = Charter(metadata=meta)
    charter.set_field_value('test_section', 'test_field', 'test_value')
    value = charter.get_field_value('test_section', 'test_field')
    assert value == 'test_value', "Field value mismatch"
    print(f"✓ Charter field get/set working")
    
    # Test JSON serialization
    json_str = charter.to_json()
    charter2 = Charter.from_json(json_str)
    assert charter2.get_field_value('test_section', 'test_field') == 'test_value'
    print(f"✓ Charter JSON serialization working")

def test_template_service():
    """Test template service"""
    print("\n=== Testing Template Service ===")
    
    service = TemplateService()
    
    # Test template discovery
    templates = service.get_available_templates()
    print(f"✓ Found {len(templates)} template(s)")
    
    for template_info in templates:
        print(f"  - {template_info['name']} (v{template_info['version']})")
    
    # Test template loading
    template = service.load_template('standard_charter')
    assert template is not None, "Failed to load template"
    print(f"✓ Template loaded: {template.template_name}")
    print(f"  - Sections: {len(template.sections)}")
    print(f"  - Required fields: {template.count_required_fields()}")
    
    # Test template structure
    for section in template.sections:
        field_count = len(section.fields)
        req_count = sum(1 for f in section.fields if f.required)
        print(f"  - {section.section_title}: {field_count} fields ({req_count} required)")

def test_charter_with_template():
    """Test charter with template integration"""
    print("\n=== Testing Charter with Template ===")
    
    service = TemplateService()
    template = service.load_template('standard_charter')
    
    # Create new charter
    meta = CharterMetadata(
        charter_id=str(uuid.uuid4()),
        created_date=datetime.now().isoformat(),
        modified_date=datetime.now().isoformat(),
        template_id=template.template_id,
        template_version=template.template_version
    )
    charter = Charter(metadata=meta)
    
    # Check initial completion
    completion = charter.get_completion_percentage(template)
    print(f"✓ New charter completion: {completion}%")
    assert completion == 0.0, "Empty charter should be 0%"
    
    # Fill in some required fields
    charter.set_field_value('identification', 'project_name', 'Test Project')
    charter.set_field_value('identification', 'project_manager', 'John Doe')
    charter.set_field_value('identification', 'sponsor', 'Jane Smith')
    
    completion = charter.get_completion_percentage(template)
    print(f"✓ After filling 3 fields: {completion:.1f}%")
    assert completion > 0, "Completion should increase"
    
    # Test validation
    errors = charter.validate(template)
    print(f"✓ Validation errors: {len(errors)}")
    print(f"  - Sample error: {errors[0] if errors else 'None'}")

def test_field_types():
    """Test different field types in template"""
    print("\n=== Testing Field Types ===")
    
    service = TemplateService()
    template = service.load_template('standard_charter')
    
    field_types = {}
    for section in template.sections:
        for field in section.fields:
            field_types[field.field_type] = field_types.get(field.field_type, 0) + 1
    
    print("✓ Field type distribution:")
    for field_type, count in sorted(field_types.items()):
        print(f"  - {field_type}: {count} fields")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Project Charter Feature - Sprint 1 Test Suite")
    print("=" * 60)
    
    try:
        test_models()
        test_template_service()
        test_charter_with_template()
        test_field_types()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
