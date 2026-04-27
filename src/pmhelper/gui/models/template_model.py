"""Template data model."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json


@dataclass
class TemplateField:
    """Individual field definition in a template."""
    field_id: str
    field_label: str
    field_type: str  # text, textarea, date, currency, number, dropdown, table
    required: bool = False
    placeholder: Optional[str] = None
    max_length: Optional[int] = None
    rows: Optional[int] = None
    help_text: Optional[str] = None
    options: Optional[List[str]] = None
    default: Optional[Any] = None
    columns: Optional[List[Dict[str, Any]]] = None  # For table fields

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateField':
        """Create field from dictionary."""
        return cls(
            field_id=data.get('field_id', ''),
            field_label=data.get('field_label', ''),
            field_type=data.get('field_type', 'text'),
            required=data.get('required', False),
            placeholder=data.get('placeholder'),
            max_length=data.get('max_length'),
            rows=data.get('rows'),
            help_text=data.get('help_text'),
            options=data.get('options'),
            default=data.get('default'),
            columns=data.get('columns')
        )


@dataclass
class TemplateSection:
    """Section with fields in a template."""
    section_id: str
    section_title: str
    section_order: int
    required: bool = False
    fields: List[TemplateField] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateSection':
        """Create section from dictionary."""
        fields_data = data.get('fields', [])
        fields = [TemplateField.from_dict(f) for f in fields_data]

        return cls(
            section_id=data.get('section_id', ''),
            section_title=data.get('section_title', ''),
            section_order=data.get('section_order', 0),
            required=data.get('required', False),
            fields=fields
        )


@dataclass
class Template:
    """Complete template structure."""
    template_id: str
    template_name: str
    template_version: str
    description: Optional[str] = None
    sections: List[TemplateSection] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """Create template from dictionary."""
        sections_data = data.get('sections', [])
        sections = [TemplateSection.from_dict(s) for s in sections_data]
        # Sort sections by order
        sections.sort(key=lambda s: s.section_order)

        return cls(
            template_id=data.get('template_id', ''),
            template_name=data.get('template_name', ''),
            template_version=data.get('template_version', '1.0'),
            description=data.get('description'),
            sections=sections
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Template':
        """Create template from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, filepath: str) -> 'Template':
        """Load template from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_section(self, section_id: str) -> Optional[TemplateSection]:
        """Get section by ID."""
        for section in self.sections:
            if section.section_id == section_id:
                return section
        return None

    def get_field(
            self,
            section_id: str,
            field_id: str) -> Optional[TemplateField]:
        """Get field by section ID and field ID."""
        section = self.get_section(section_id)
        if section:
            for field_def in section.fields:
                if field_def.field_id == field_id:
                    return field_def
        return None

    def count_required_fields(self) -> int:
        """Count total number of required fields."""
        count = 0
        for section in self.sections:
            for field_def in section.fields:
                if field_def.required:
                    count += 1
        return count
