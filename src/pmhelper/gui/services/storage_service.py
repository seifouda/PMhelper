"""Storage service for saving and loading charters."""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from ..models import Charter


class StorageService:
    """Service for managing charter file storage."""

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize storage service.

        Args:
            base_dir: Base directory for charter storage. If None, uses default.
        """
        if base_dir is None:
            # Default to data/charters directory
            project_root = Path(__file__).parent.parent.parent.parent.parent
            base_dir = project_root / "data" / "charters"

        self.base_dir = Path(base_dir)
        self.drafts_dir = self.base_dir / "drafts"
        self.exports_dir = self.base_dir / "exports"

        # Ensure directories exist
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def save_charter(self, charter: Charter, filepath: str) -> bool:
        """
        Save charter to JSON file.

        Args:
            charter: Charter to save
            filepath: Full path to save file

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = Path(filepath)

            # Ensure parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Create temporary file for atomic write
            temp_filepath = filepath.with_suffix('.tmp')

            # Write to temp file
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(charter.to_dict(), f, indent=2, ensure_ascii=False)

            # Atomic rename (prevents corruption)
            shutil.move(str(temp_filepath), str(filepath))

            return True

        except Exception as e:
            print(f"Error saving charter: {e}")
            # Clean up temp file if it exists
            if temp_filepath.exists():
                temp_filepath.unlink()
            return False

    def load_charter(self, filepath: str) -> Optional[Charter]:
        """
        Load charter from JSON file.

        Args:
            filepath: Full path to charter file

        Returns:
            Charter object or None if error
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                print(f"Charter file not found: {filepath}")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            charter = Charter.from_dict(data)
            return charter

        except Exception as e:
            print(f"Error loading charter: {e}")
            return None

    def list_charters(
            self, directory: Optional[str] = None) -> List[Dict[str, any]]:
        """
        List all charters in a directory.

        Args:
            directory: Directory to search. If None, searches all charter directories.

        Returns:
            List of charter info dictionaries
        """
        charters = []

        if directory:
            search_dirs = [Path(directory)]
        else:
            search_dirs = [self.base_dir, self.drafts_dir]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for charter_file in search_dir.rglob("*.json"):
                try:
                    # Load the full charter to calculate completion
                    charter = self.load_charter(str(charter_file))
                    if not charter:
                        continue

                    # Get project name from charter data
                    project_name = charter.get_field_value(
                        'identification', 'project_name') or 'Untitled'

                    # Calculate completion percentage
                    completion = 0.0
                    try:
                        # Try to load template to calculate completion
                        from .template_service import TemplateService
                        template_service = TemplateService()
                        template = template_service.load_template(
                            charter.metadata.template_id)
                        if template:
                            completion = charter.get_completion_percentage(
                                template)
                    except Exception as e:
                        print(
                            f"Warning: Could not calculate completion for {charter_file}: {e}")

                    info = {
                        'filepath': str(charter_file),
                        'filename': charter_file.name,
                        'charter_id': charter.metadata.charter_id,
                        'title': project_name,  # Use 'title' to match CharterManager expectations
                        'project_name': project_name,  # Keep for backward compatibility
                        'created_date': charter.metadata.created_date,
                        'modified_date': charter.metadata.modified_date,
                        'status': charter.metadata.status,
                        'template_id': charter.metadata.template_id,
                        'completion': completion,  # Add completion percentage
                        'file_size': charter_file.stat().st_size
                    }

                    charters.append(info)

                except Exception as e:
                    print(f"Error reading charter {charter_file}: {e}")
                    continue

        # Sort by modified date (newest first)
        charters.sort(key=lambda x: x.get('modified_date', ''), reverse=True)

        return charters

    def delete_charter(self, filepath: str) -> bool:
        """
        Delete a charter file.

        Args:
            filepath: Full path to charter file

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                print(f"Charter file not found: {filepath}")
                return False

            # Move to trash or delete
            filepath.unlink()
            return True

        except Exception as e:
            print(f"Error deleting charter: {e}")
            return False

    def duplicate_charter(self, filepath: str) -> Optional[str]:
        """
        Duplicate a charter file.

        Args:
            filepath: Full path to charter file to duplicate

        Returns:
            Path to new charter file or None if error
        """
        try:
            # Load original charter
            charter = self.load_charter(filepath)
            if not charter:
                return None

            # Generate new charter ID
            import uuid
            charter.metadata.charter_id = str(uuid.uuid4())
            charter.metadata.created_date = datetime.now().isoformat()
            charter.metadata.modified_date = datetime.now().isoformat()

            # Update project name
            project_name = charter.get_field_value(
                'identification', 'project_name')
            if project_name:
                charter.set_field_value('identification', 'project_name',
                                        f"{project_name} (Copy)")

            # Generate new filepath
            original_path = Path(filepath)
            new_filename = f"{original_path.stem}_copy{original_path.suffix}"
            new_filepath = original_path.parent / new_filename

            # Ensure unique filename
            counter = 1
            while new_filepath.exists():
                new_filename = f"{
                    original_path.stem}_copy{counter}{
                    original_path.suffix}"
                new_filepath = original_path.parent / new_filename
                counter += 1

            # Save duplicated charter
            if self.save_charter(charter, str(new_filepath)):
                return str(new_filepath)

            return None

        except Exception as e:
            print(f"Error duplicating charter: {e}")
            return None

    def get_draft_filepath(self, charter_id: str) -> str:
        """
        Get the draft filepath for a charter ID.

        Args:
            charter_id: Charter ID

        Returns:
            Full path for draft file
        """
        filename = f"draft_{charter_id}.json"
        return str(self.drafts_dir / filename)

    def save_draft(self, charter: Charter) -> bool:
        """
        Save charter as draft.

        Args:
            charter: Charter to save

        Returns:
            True if successful
        """
        filepath = self.get_draft_filepath(charter.metadata.charter_id)
        return self.save_charter(charter, filepath)

    def get_export_filepath(
            self,
            charter: Charter,
            extension: str = ".json") -> str:
        """
        Generate export filepath for a charter.

        Args:
            charter: Charter to export
            extension: File extension

        Returns:
            Suggested filepath for export
        """
        # Get project name
        project_name = charter.get_field_value(
            'identification', 'project_name')
        if not project_name:
            project_name = "charter"

        # Clean filename
        clean_name = "".join(
            c for c in project_name if c.isalnum() or c in (
                ' ', '-', '_'))
        clean_name = clean_name.replace(' ', '_')

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{clean_name}_{timestamp}{extension}"

        return str(self.exports_dir / filename)

    def get_export_dir(self) -> str:
        """
        Get the exports directory path.

        Returns:
            Path to exports directory
        """
        return str(self.exports_dir)
