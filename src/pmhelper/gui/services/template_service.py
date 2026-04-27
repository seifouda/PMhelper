"""Template service for loading and managing charter templates."""

import json
from typing import Dict, List, Optional
from pathlib import Path

from ..models.template_model import Template


class TemplateService:
    """Service for managing charter templates."""

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize template service.

        Args:
            templates_dir: Directory containing template files.
                          If None, uses default location.
        """
        if templates_dir is None:
            # Default to templates/charter directory
            project_root = Path(__file__).parent.parent.parent.parent.parent
            templates_dir = project_root / "templates" / "charter"

        self.templates_dir = Path(templates_dir)
        self._template_cache: Dict[str, Template] = {}

    def get_available_templates(self) -> List[Dict[str, str]]:
        """
        Get list of available templates.

        Returns:
            List of dictionaries with template info (id, name, version, description)
        """
        templates = []

        if not self.templates_dir.exists():
            return templates

        for template_file in self.templates_dir.glob("*.json"):
            # Skip schema files
            if template_file.name.endswith("_schema.json"):
                continue

            try:
                info = self.get_template_info(template_file.stem)
                if info:
                    templates.append(info)
            except Exception as e:
                print(f"Error loading template {template_file.name}: {e}")
                continue

        return templates

    def get_template_info(self, template_id: str) -> Optional[Dict[str, str]]:
        """
        Get template metadata without loading full template.

        Args:
            template_id: Template identifier (filename without .json)

        Returns:
            Dictionary with template info or None if not found
        """
        template_path = self.templates_dir / f"{template_id}.json"

        if not template_path.exists():
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return {
                'id': data.get('template_id', template_id),
                'name': data.get('template_name', 'Unknown'),
                'version': data.get('template_version', '1.0'),
                'description': data.get('description', '')
            }
        except Exception as e:
            print(f"Error reading template info: {e}")
            return None

    def load_template(self, template_id: str) -> Optional[Template]:
        """
        Load a template by ID.

        Args:
            template_id: Template identifier (filename without .json)

        Returns:
            Template object or None if not found
        """
        # Check cache first
        if template_id in self._template_cache:
            return self._template_cache[template_id]

        template_path = self.templates_dir / f"{template_id}.json"

        if not template_path.exists():
            print(f"Template not found: {template_path}")
            return None

        try:
            template = Template.from_file(str(template_path))
            # Cache the template
            self._template_cache[template_id] = template
            return template
        except Exception as e:
            print(f"Error loading template: {e}")
            return None

    def validate_template(self, template_id: str) -> tuple[bool, List[str]]:
        """
        Validate a template file.

        Args:
            template_id: Template identifier

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        template_path = self.templates_dir / f"{template_id}.json"

        if not template_path.exists():
            return False, [f"Template file not found: {template_path}"]

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Basic validation
            if 'template_id' not in data:
                errors.append("Missing 'template_id' field")

            if 'template_name' not in data:
                errors.append("Missing 'template_name' field")

            if 'sections' not in data:
                errors.append("Missing 'sections' field")
            elif not isinstance(data['sections'], list):
                errors.append("'sections' must be an array")
            elif len(data['sections']) == 0:
                errors.append("'sections' array is empty")
            else:
                # Validate sections
                for i, section in enumerate(data['sections']):
                    if 'section_id' not in section:
                        errors.append(f"Section {i}: Missing 'section_id'")
                    if 'section_title' not in section:
                        errors.append(f"Section {i}: Missing 'section_title'")
                    if 'fields' not in section:
                        errors.append(f"Section {i}: Missing 'fields'")
                    elif not isinstance(section['fields'], list):
                        errors.append(
                            f"Section {i}: 'fields' must be an array")

            if errors:
                return False, errors

            # Try to load as Template object
            Template.from_dict(data)
            return True, []

        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except Exception as e:
            return False, [f"Error validating template: {e}"]

    def clear_cache(self):
        """Clear the template cache."""
        self._template_cache.clear()
