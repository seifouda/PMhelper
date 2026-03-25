"""
Test script to verify Project Charter feature implementation.
Tests all Sprint 1-4 functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_sprint_1_foundation():
    """Test Sprint 1: Foundation & Setup"""
    print("\n=== Testing Sprint 1: Foundation & Setup ===")
    
    # Test 1.1: Template loading
    from pmhelper.gui.services.template_service import TemplateService
    template_service = TemplateService()
    template = template_service.load_template("standard_charter")
    assert template is not None, "Failed to load template"
    assert template.template_name == "Standard Project Charter", "Template name mismatch"
    assert len(template.sections) == 9, f"Expected 9 sections, got {len(template.sections)}"
    print("✅ Template loading works")
    
    # Test 1.2: Charter model
    from pmhelper.gui.models import Charter, CharterMetadata, CharterStatus
    from datetime import datetime
    import uuid
    
    metadata = CharterMetadata(
        charter_id=str(uuid.uuid4()),
        created_date=datetime.now().isoformat(),
        modified_date=datetime.now().isoformat(),
        status=CharterStatus.DRAFT.value,
        template_id="standard_charter",
        template_version="1.0.0"
    )
    charter = Charter(metadata=metadata)
    assert charter is not None, "Failed to create charter"
    print("✅ Charter model creation works")
    
    # Test 1.3: Field operations
    charter.set_field_value("identification", "project_name", "Test Project")
    value = charter.get_field_value("identification", "project_name")
    assert value == "Test Project", "Field set/get failed"
    print("✅ Field operations work")
    
    # Test 1.4: Completion percentage
    completion = charter.get_completion_percentage(template)
    assert isinstance(completion, (int, float)), "Completion percentage failed"
    assert 0 <= completion <= 100, "Completion percentage out of range"
    print(f"✅ Completion tracking works ({completion:.1f}%)")
    
    return charter, template

def test_sprint_2_form_generation(charter, template):
    """Test Sprint 2: Form Generation (components only, no GUI)"""
    print("\n=== Testing Sprint 2: Form Generation ===")
    
    # Test 2.1: Validators
    from pmhelper.gui.utils.validators import FieldValidator
    
    # Test required field validation
    is_valid, error = FieldValidator.validate_required("", "Test Field")
    assert not is_valid, "Required validation failed"
    is_valid, error = FieldValidator.validate_required("value", "Test Field")
    assert is_valid, "Required validation failed"
    print("✅ Required field validation works")
    
    # Test email validation
    is_valid, error = FieldValidator.validate_email("test@example.com", "Email")
    assert is_valid, "Email validation failed"
    is_valid, error = FieldValidator.validate_email("invalid", "Email")
    assert not is_valid, "Email validation failed"
    print("✅ Email validation works")
    
    # Test currency validation
    is_valid, error = FieldValidator.validate_currency("1000", "Budget")
    assert is_valid, "Currency validation failed"
    is_valid, error = FieldValidator.validate_currency("1000.50", "Budget")
    assert is_valid, "Currency validation failed"
    is_valid, error = FieldValidator.validate_currency("abc", "Budget")
    assert not is_valid, "Currency validation failed"
    print("✅ Currency validation works")
    
    # Test date validation
    is_valid, error = FieldValidator.validate_date("2024-01-01", "Start Date")
    assert is_valid, "Date validation failed"
    is_valid, error = FieldValidator.validate_date("invalid", "Start Date")
    assert not is_valid, "Date validation failed"
    print("✅ Date validation works")

def test_sprint_3_data_persistence(charter, template):
    """Test Sprint 3: Data Persistence"""
    print("\n=== Testing Sprint 3: Data Persistence ===")
    
    from pmhelper.gui.services.storage_service import StorageService
    import tempfile
    import os
    
    storage = StorageService()
    
    # Test 3.1: Save charter
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        success = storage.save_charter(charter, temp_file)
        assert success, "Save charter failed"
        assert os.path.exists(temp_file), "Charter file not created"
        print("✅ Save charter works")
        
        # Test 3.2: Load charter
        loaded_charter = storage.load_charter(temp_file)
        assert loaded_charter is not None, "Load charter failed"
        assert loaded_charter.metadata.charter_id == charter.metadata.charter_id, "Charter ID mismatch"
        print("✅ Load charter works")
        
        # Test 3.3: List charters
        charters = storage.list_charters()
        assert isinstance(charters, list), "List charters failed"
        print(f"✅ List charters works ({len(charters)} found)")
        
        # Test 3.4: Duplicate charter
        dup_file = storage.duplicate_charter(temp_file)
        if dup_file:
            assert os.path.exists(dup_file), "Duplicate file not created"
            print("✅ Duplicate charter works")
            os.unlink(dup_file)
        
        # Test 3.5: Delete charter
        success = storage.delete_charter(temp_file)
        assert success, "Delete charter failed"
        assert not os.path.exists(temp_file), "Charter file not deleted"
        print("✅ Delete charter works")
        
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def test_sprint_4_pdf_generation(charter, template):
    """Test Sprint 4: PDF Generation"""
    print("\n=== Testing Sprint 4: PDF Generation ===")
    
    from pmhelper.gui.services.pdf_generator import PDFGenerator
    import tempfile
    import os
    
    # Add some test data
    charter.set_field_value("identification", "project_name", "Test Charter Project")
    charter.set_field_value("identification", "project_description", "This is a test charter for PDF generation.")
    charter.set_field_value("identification", "start_date", "2024-01-01")
    charter.set_field_value("objectives", "business_objectives", "Increase efficiency by 25%")
    charter.set_field_value("budget", "total_budget", "100000")
    
    # Set table data
    stakeholders = [
        ["Name", "Role", "Contact"],
        ["John Doe", "Sponsor", "john@example.com"],
        ["Jane Smith", "Manager", "jane@example.com"]
    ]
    charter.set_field_value("stakeholders", "key_stakeholders", stakeholders)
    
    pdf_gen = PDFGenerator()
    
    # Test 4.1: Generate PDF
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        temp_pdf = f.name
    
    try:
        success = pdf_gen.generate_pdf(charter, template, temp_pdf)
        assert success, "PDF generation failed"
        assert os.path.exists(temp_pdf), "PDF file not created"
        
        # Check file size (should be > 0)
        size = os.path.getsize(temp_pdf)
        assert size > 0, "PDF file is empty"
        print(f"✅ PDF generation works (file size: {size:,} bytes)")
        
    finally:
        # Cleanup
        if os.path.exists(temp_pdf):
            os.unlink(temp_pdf)

def main():
    """Run all tests"""
    print("=" * 60)
    print("Project Charter Feature - Comprehensive Test")
    print("=" * 60)
    
    try:
        # Sprint 1: Foundation
        charter, template = test_sprint_1_foundation()
        
        # Sprint 2: Form Generation
        test_sprint_2_form_generation(charter, template)
        
        # Sprint 3: Data Persistence
        test_sprint_3_data_persistence(charter, template)
        
        # Sprint 4: PDF Generation
        test_sprint_4_pdf_generation(charter, template)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nProject Charter feature is fully functional!")
        print("- Sprint 1: Foundation & Setup ✅")
        print("- Sprint 2: Form Generation ✅")
        print("- Sprint 3: Data Persistence ✅")
        print("- Sprint 4: PDF Generation ✅")
        print("\nReady for Sprint 5: Polish & Testing")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
