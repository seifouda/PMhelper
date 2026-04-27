"""Data models for Project Charter feature."""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
from datetime import datetime
from enum import Enum
import json


class CharterStatus(Enum):
    """Charter status enumeration."""
    DRAFT = "draft"
    FINAL = "final"
    ARCHIVED = "archived"


@dataclass
class CharterMetadata:
    """Metadata for a project charter."""
    charter_id: str
    created_date: str
    modified_date: str
    status: str = CharterStatus.DRAFT.value
    version: str = "1.0"
    template_id: str = "standard_charter_v1"
    template_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharterMetadata':
        """Create metadata from dictionary."""
        return cls(**data)


@dataclass
class Charter:
    """Main charter data structure."""
    metadata: CharterMetadata
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert charter to dictionary for JSON serialization."""
        return {
            'metadata': self.metadata.to_dict(),
            'data': self.data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Charter':
        """Create charter from dictionary."""
        metadata = CharterMetadata.from_dict(data.get('metadata', {}))
        charter_data = data.get('data', {})
        return cls(metadata=metadata, data=charter_data)

    def to_json(self) -> str:
        """Convert charter to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Charter':
        """Create charter from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def get_field_value(self, section_id: str, field_id: str) -> Any:
        """Get value of a specific field."""
        section_data = self.data.get(section_id, {})
        return section_data.get(field_id)

    def set_field_value(
            self,
            section_id: str,
            field_id: str,
            value: Any) -> None:
        """Set value of a specific field."""
        if section_id not in self.data:
            self.data[section_id] = {}
        self.data[section_id][field_id] = value
        self.metadata.modified_date = datetime.now().isoformat()

    def get_completion_percentage(self, template) -> float:
        """Calculate completion percentage based on required fields."""
        total_required = 0
        filled_required = 0

        for section in template.sections:
            for field_def in section.fields:
                if field_def.required:
                    total_required += 1
                    value = self.get_field_value(
                        section.section_id, field_def.field_id)
                    if value and self._is_field_filled(
                            value, field_def.field_type):
                        filled_required += 1

        if total_required == 0:
            return 100.0

        return (filled_required / total_required) * 100.0

    def _is_field_filled(self, value: Any, field_type: str) -> bool:
        """Check if a field value is considered filled."""
        if value is None:
            return False

        if field_type in ['text', 'textarea', 'date', 'dropdown']:
            return bool(str(value).strip())

        if field_type in ['currency', 'number']:
            return value != 0 and value != ''

        if field_type == 'table':
            return isinstance(value, list) and len(value) > 0

        return bool(value)

    def validate(self, template) -> List[str]:
        """Validate charter against template and return list of errors."""
        errors = []

        for section in template.sections:
            for field_def in section.fields:
                if field_def.required:
                    value = self.get_field_value(
                        section.section_id, field_def.field_id)
                    if not value or not self._is_field_filled(
                            value, field_def.field_type):
                        errors.append(
                            f"{section.section_title} - {field_def.field_label}: Required field is empty"
                        )

        return errors
