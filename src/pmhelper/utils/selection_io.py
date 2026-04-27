"""
File I/O Handler for Project Selection Module

Handles reading/writing .pmsel files (JSON format) for saving selection problems.

Author: PMHelper Team
Version: 1.0.0
"""

import json
from pathlib import Path
from datetime import datetime

from pmhelper.core.models import SelectionProblem, SelectionResult


class SelectionFileHandler:
    """
    Handler for .pmsel file format operations.

    .pmsel files are JSON files containing SelectionProblem data.
    """

    EXTENSION = ".pmsel"
    CURRENT_VERSION = "1.0"

    @staticmethod
    def save(problem: SelectionProblem, filepath: str | Path) -> None:
        """
        Save a SelectionProblem to a .pmsel file.

        Args:
            problem: SelectionProblem instance to save
            filepath: Path to save file (will add .pmsel extension if missing)

        Raises:
            IOError: If file cannot be written
            ValueError: If problem data is invalid
        """
        filepath = Path(filepath)

        # Ensure .pmsel extension
        if filepath.suffix != SelectionFileHandler.EXTENSION:
            filepath = filepath.with_suffix(SelectionFileHandler.EXTENSION)

        # Update timestamp
        problem.updated_at = datetime.now()

        # Convert to JSON
        try:
            data = problem.model_dump(mode='json')

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise IOError(f"Failed to save file: {e}")

    @staticmethod
    def load(filepath: str | Path) -> SelectionProblem:
        """
        Load a SelectionProblem from a .pmsel file.

        Args:
            filepath: Path to .pmsel file

        Returns:
            SelectionProblem instance

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
            ValueError: If file format is invalid
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Check extension
        if filepath.suffix != SelectionFileHandler.EXTENSION:
            raise ValueError(
                f"Invalid file extension. Expected {
                    SelectionFileHandler.EXTENSION}, " f"got {
                    filepath.suffix}")

        # Read file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise IOError(f"Failed to read file: {e}")

        # Check version
        version = data.get('version', '1.0')
        if version != SelectionFileHandler.CURRENT_VERSION:
            # Could implement version migration here if needed
            print(f"Warning: File version {version} may not be fully compatible "
                  f"with current version {SelectionFileHandler.CURRENT_VERSION}")

        # Parse into SelectionProblem
        try:
            problem = SelectionProblem(**data)
            return problem
        except Exception as e:
            raise ValueError(f"Invalid problem data: {e}")

    @staticmethod
    def export_to_json(
            problem: SelectionProblem,
            filepath: str | Path) -> None:
        """
        Export SelectionProblem to a generic JSON file.

        Args:
            problem: SelectionProblem instance
            filepath: Path to save JSON file
        """
        filepath = Path(filepath)

        try:
            data = problem.model_dump(mode='json')

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise IOError(f"Failed to export JSON: {e}")

    @staticmethod
    def import_from_json(filepath: str | Path) -> SelectionProblem:
        """
        Import SelectionProblem from a generic JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            SelectionProblem instance
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            problem = SelectionProblem(**data)
            return problem

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Failed to import JSON: {e}")

    @staticmethod
    def save_results(result: SelectionResult, filepath: str | Path) -> None:
        """
        Save SelectionResult to a JSON file.

        Args:
            result: SelectionResult instance
            filepath: Path to save file
        """
        filepath = Path(filepath)

        try:
            data = result.model_dump(mode='json')

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise IOError(f"Failed to save results: {e}")

    @staticmethod
    def load_results(filepath: str | Path) -> SelectionResult:
        """
        Load SelectionResult from a JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            SelectionResult instance
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            result = SelectionResult(**data)
            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load results: {e}")

    @staticmethod
    def validate_file(filepath: str | Path) -> dict:
        """
        Validate a .pmsel file without fully loading it.

        Args:
            filepath: Path to .pmsel file

        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'version': str,
                'method': str,
                'errors': List[str]
            }
        """
        filepath = Path(filepath)
        errors = []

        if not filepath.exists():
            return {
                'valid': False,
                'version': None,
                'method': None,
                'errors': ['File not found']
            }

        if filepath.suffix != SelectionFileHandler.EXTENSION:
            errors.append(f"Invalid extension: {filepath.suffix}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check required fields
            if 'version' not in data:
                errors.append("Missing 'version' field")

            if 'method' not in data:
                errors.append("Missing 'method' field")

            version = data.get('version', 'unknown')
            method = data.get('method', 'unknown')

            # Try to parse as SelectionProblem
            try:
                SelectionProblem(**data)
            except Exception as e:
                errors.append(f"Validation error: {str(e)}")

            return {
                'valid': len(errors) == 0,
                'version': version,
                'method': method,
                'errors': errors
            }

        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'version': None,
                'method': None,
                'errors': [f"Invalid JSON: {e}"]
            }
        except Exception as e:
            return {
                'valid': False,
                'version': None,
                'method': None,
                'errors': [f"Read error: {e}"]
            }


class SelectionExportHandler:
    """Handler for exporting selection data to various formats."""

    @staticmethod
    def to_csv(problem: SelectionProblem, filepath: str | Path) -> None:
        """
        Export selection problem to CSV format.

        Args:
            problem: SelectionProblem instance
            filepath: Path to save CSV file
        """
        import pandas as pd

        filepath = Path(filepath)

        try:
            if problem.alternatives:
                # Export alternatives with scores
                data = []
                for alt in problem.alternatives:
                    row = {'ID': alt.id, 'Name': alt.name}
                    row.update(alt.scores)
                    data.append(row)

                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False)

            elif problem.projects:
                # Export projects
                data = []
                for proj in problem.projects:
                    data.append({
                        'ID': proj.id,
                        'Name': proj.name,
                        'Cost': proj.cost,
                        'Benefit': proj.benefit,
                        'Life': proj.life or '',
                        'Annual O&M': proj.annual_om,
                        'Salvage': proj.salvage
                    })

                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False)
            else:
                raise ValueError("No alternatives or projects to export")

        except Exception as e:
            raise IOError(f"Failed to export CSV: {e}")

    @staticmethod
    def from_csv(filepath: str | Path, method: str) -> SelectionProblem:
        """
        Import selection problem from CSV format.

        Args:
            filepath: Path to CSV file
            method: Selection method ('ahp', 'linear_scoring', 'benefit_cost', 'portfolio')

        Returns:
            SelectionProblem instance
        """
        import pandas as pd
        from pmhelper.core.models import Alternative, Project, Criterion, CriterionDirection

        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        try:
            df = pd.read_csv(filepath)

            if method in ['ahp', 'linear_scoring']:
                # Parse as alternatives
                alternatives = []
                criteria = []

                # Extract criteria from columns (skip ID and Name)
                criterion_cols = [
                    col for col in df.columns if col not in [
                        'ID', 'Name']]

                for col in criterion_cols:
                    criteria.append(Criterion(
                        name=col,
                        weight=0.0,
                        direction=CriterionDirection.MAXIMIZE
                    ))

                for _, row in df.iterrows():
                    scores = {col: row[col]
                              for col in criterion_cols if pd.notna(row[col])}
                    alternatives.append(Alternative(
                        id=str(row['ID']),
                        name=str(row['Name']),
                        scores=scores
                    ))

                return SelectionProblem(
                    id=f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    name=f"Imported from {filepath.name}",
                    method=method,
                    criteria=criteria,
                    alternatives=alternatives
                )

            elif method in ['benefit_cost', 'portfolio']:
                # Parse as projects
                projects = []

                for _, row in df.iterrows():
                    projects.append(
                        Project(
                            id=str(
                                row['ID']), name=str(
                                row['Name']), cost=float(
                                row['Cost']), benefit=float(
                                row['Benefit']), life=int(
                                row['Life']) if pd.notna(
                                row.get('Life')) else None, annual_om=float(
                                    row.get(
                                        'Annual O&M', 0)), salvage=float(
                                            row.get(
                                                'Salvage', 0))))

                return SelectionProblem(
                    id=f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    name=f"Imported from {filepath.name}",
                    method=method,
                    projects=projects,
                    marr=0.12 if method == 'benefit_cost' else None,
                    budget=1000000.0 if method == 'portfolio' else None
                )
            else:
                raise ValueError(f"Unknown method: {method}")

        except Exception as e:
            raise ValueError(f"Failed to import CSV: {e}")
