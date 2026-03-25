"""Unit tests for Project Charter models."""

import sys
from pathlib import Path
import unittest
from datetime import datetime
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pmhelper.gui.models import Charter, CharterMetadata, CharterStatus
from pmhelper.gui.models.template_model import Template, TemplateSection, TemplateField


class TestCharterMetadata(unittest.TestCase):
    """Test CharterMetadata class."""
    
    def test_create_metadata(self):
        """Test creating charter metadata."""
        charter_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        metadata = CharterMetadata(
            charter_id=charter_id,
            created_date=now,
            modified_date=now,
            status=CharterStatus.DRAFT.value,
            template_id="test_template",
            template_version="1.0.0"
        )
        
        self.assertEqual(metadata.charter_id, charter_id)
        self.assertEqual(metadata.status, CharterStatus.DRAFT.value)
        self.assertEqual(metadata.template_id, "test_template")
    
    def test_metadata_to_dict(self):
        """Test metadata serialization."""
        metadata = CharterMetadata(
            charter_id="test-id",
            created_date="2024-01-01",
            modified_date="2024-01-02",
            status=CharterStatus.FINAL.value,
            template_id="template-1",
            template_version="1.0"
        )
        
        data = metadata.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['charter_id'], "test-id")
        self.assertEqual(data['status'], CharterStatus.FINAL.value)
    
    def test_metadata_from_dict(self):
        """Test metadata deserialization."""
        data = {
            'charter_id': 'test-123',
            'created_date': '2024-01-01',
            'modified_date': '2024-01-02',
            'status': 'draft',
            'template_id': 'std',
            'template_version': '1.0'
        }
        
        metadata = CharterMetadata.from_dict(data)
        self.assertEqual(metadata.charter_id, 'test-123')
        self.assertEqual(metadata.status, 'draft')


class TestCharter(unittest.TestCase):
    """Test Charter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.charter = Charter(
            metadata=CharterMetadata(
                charter_id=str(uuid.uuid4()),
                created_date=datetime.now().isoformat(),
                modified_date=datetime.now().isoformat(),
                status=CharterStatus.DRAFT.value,
                template_id="test",
                template_version="1.0"
            )
        )
    
    def test_set_and_get_field_value(self):
        """Test setting and getting field values."""
        self.charter.set_field_value("section1", "field1", "value1")
        value = self.charter.get_field_value("section1", "field1")
        self.assertEqual(value, "value1")
    
    def test_get_nonexistent_field(self):
        """Test getting non-existent field returns None."""
        value = self.charter.get_field_value("nonexistent", "field")
        self.assertIsNone(value)
    
    def test_to_dict(self):
        """Test charter serialization."""
        self.charter.set_field_value("test", "name", "Test Project")
        data = self.charter.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertIn('metadata', data)
        self.assertIn('data', data)
        self.assertEqual(data['data']['test']['name'], "Test Project")
    
    def test_from_dict(self):
        """Test charter deserialization."""
        data = {
            'metadata': {
                'charter_id': 'test-456',
                'created_date': '2024-01-01',
                'modified_date': '2024-01-01',
                'status': 'draft',
                'template_id': 'std',
                'template_version': '1.0'
            },
            'data': {
                'section1': {'field1': 'value1'}
            }
        }
        
        charter = Charter.from_dict(data)
        self.assertEqual(charter.metadata.charter_id, 'test-456')
        self.assertEqual(charter.get_field_value('section1', 'field1'), 'value1')
    
    def test_completion_percentage(self):
        """Test completion percentage calculation."""
        # Create mock template
        template = Template(
            template_id="test",
            template_name="Test",
            template_version="1.0",
            sections=[
                TemplateSection(
                    section_id="sec1",
                    section_title="Section 1",
                    section_order=1,
                    fields=[
                        TemplateField(
                            field_id="req1",
                            field_label="Required 1",
                            field_type="text",
                            required=True
                        ),
                        TemplateField(
                            field_id="req2",
                            field_label="Required 2",
                            field_type="text",
                            required=True
                        ),
                        TemplateField(
                            field_id="opt1",
                            field_label="Optional 1",
                            field_type="text",
                            required=False
                        )
                    ]
                )
            ]
        )
        
        # Empty charter
        completion = self.charter.get_completion_percentage(template)
        self.assertEqual(completion, 0.0)
        
        # Fill one required field
        self.charter.set_field_value("sec1", "req1", "value")
        completion = self.charter.get_completion_percentage(template)
        self.assertEqual(completion, 50.0)
        
        # Fill both required fields
        self.charter.set_field_value("sec1", "req2", "value")
        completion = self.charter.get_completion_percentage(template)
        self.assertEqual(completion, 100.0)
    
    def test_validate(self):
        """Test charter validation."""
        template = Template(
            template_id="test",
            template_name="Test",
            template_version="1.0",
            sections=[
                TemplateSection(
                    section_id="sec1",
                    section_title="Section 1",
                    section_order=1,
                    fields=[
                        TemplateField(
                            field_id="req1",
                            field_label="Required Field",
                            field_type="text",
                            required=True
                        )
                    ]
                )
            ]
        )
        
        # Empty charter should have errors
        errors = self.charter.validate(template)
        self.assertGreater(len(errors), 0)
        
        # Fill required field
        self.charter.set_field_value("sec1", "req1", "value")
        errors = self.charter.validate(template)
        self.assertEqual(len(errors), 0)


class TestTemplateField(unittest.TestCase):
    """Test TemplateField class."""
    
    def test_create_field(self):
        """Test creating a template field."""
        field = TemplateField(
            field_id="test_field",
            field_label="Test Field",
            field_type="text",
            required=True,
            max_length=100
        )
        
        self.assertEqual(field.field_id, "test_field")
        self.assertEqual(field.field_label, "Test Field")
        self.assertTrue(field.required)
        self.assertEqual(field.max_length, 100)
    
    def test_from_dict(self):
        """Test field deserialization."""
        data = {
            'field_id': 'email',
            'field_label': 'Email Address',
            'field_type': 'text',
            'required': True,
            'placeholder': 'user@example.com'
        }
        
        field = TemplateField.from_dict(data)
        self.assertEqual(field.field_id, 'email')
        self.assertEqual(field.placeholder, 'user@example.com')


class TestTemplateSection(unittest.TestCase):
    """Test TemplateSection class."""
    
    def test_create_section(self):
        """Test creating a template section."""
        section = TemplateSection(
            section_id="intro",
            section_title="Introduction",
            section_order=1,
            required=True
        )
        
        self.assertEqual(section.section_id, "intro")
        self.assertEqual(section.section_title, "Introduction")
        self.assertEqual(section.section_order, 1)
        self.assertTrue(section.required)
    
    def test_from_dict(self):
        """Test section deserialization."""
        data = {
            'section_id': 'objectives',
            'section_title': 'Objectives',
            'section_order': 2,
            'required': False,
            'fields': [
                {
                    'field_id': 'goal',
                    'field_label': 'Goal',
                    'field_type': 'textarea'
                }
            ]
        }
        
        section = TemplateSection.from_dict(data)
        self.assertEqual(section.section_id, 'objectives')
        self.assertEqual(len(section.fields), 1)
        self.assertEqual(section.fields[0].field_id, 'goal')


class TestTemplate(unittest.TestCase):
    """Test Template class."""
    
    def test_create_template(self):
        """Test creating a template."""
        template = Template(
            template_id="standard",
            template_name="Standard Charter",
            template_version="1.0.0",
            description="Standard project charter template"
        )
        
        self.assertEqual(template.template_id, "standard")
        self.assertEqual(template.template_name, "Standard Charter")
    
    def test_get_section(self):
        """Test getting section by ID."""
        section = TemplateSection(
            section_id="test_sec",
            section_title="Test Section",
            section_order=1
        )
        
        template = Template(
            template_id="test",
            template_name="Test",
            template_version="1.0",
            sections=[section]
        )
        
        found_section = template.get_section("test_sec")
        self.assertIsNotNone(found_section)
        self.assertEqual(found_section.section_id, "test_sec")
        
        missing_section = template.get_section("nonexistent")
        self.assertIsNone(missing_section)
    
    def test_get_field(self):
        """Test getting field by section and field ID."""
        field = TemplateField(
            field_id="test_field",
            field_label="Test",
            field_type="text"
        )
        
        section = TemplateSection(
            section_id="test_sec",
            section_title="Test",
            section_order=1,
            fields=[field]
        )
        
        template = Template(
            template_id="test",
            template_name="Test",
            template_version="1.0",
            sections=[section]
        )
        
        found_field = template.get_field("test_sec", "test_field")
        self.assertIsNotNone(found_field)
        self.assertEqual(found_field.field_id, "test_field")
        
        missing_field = template.get_field("test_sec", "nonexistent")
        self.assertIsNone(missing_field)
    
    def test_count_required_fields(self):
        """Test counting required fields."""
        template = Template(
            template_id="test",
            template_name="Test",
            template_version="1.0",
            sections=[
                TemplateSection(
                    section_id="sec1",
                    section_title="Section 1",
                    section_order=1,
                    fields=[
                        TemplateField("f1", "Field 1", "text", required=True),
                        TemplateField("f2", "Field 2", "text", required=False),
                        TemplateField("f3", "Field 3", "text", required=True),
                    ]
                )
            ]
        )
        
        count = template.count_required_fields()
        self.assertEqual(count, 2)


if __name__ == '__main__':
    unittest.main()
