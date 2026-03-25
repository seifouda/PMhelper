"""Storage service for DPCI assessments."""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from ..models.dpci_model import DPCIAssessment


class DPCIService:
    """Service for managing DPCI assessment file storage."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize DPCI storage service."""
        if base_dir is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            base_dir = project_root / "data" / "dpci"
        
        self.base_dir = Path(base_dir)
        self.assessments_dir = self.base_dir / "assessments"
        self.exports_dir = self.base_dir / "exports"
        
        self.assessments_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    def save_assessment(self, assessment: DPCIAssessment, filepath: str) -> bool:
        """Save DPCI assessment to JSON file."""
        try:
            filepath = Path(filepath)
            assessment.modified_date = datetime.now().isoformat()
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            temp_filepath = filepath.with_suffix('.tmp')
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(assessment.to_dict(), f, indent=2, ensure_ascii=False)
            
            shutil.move(str(temp_filepath), str(filepath))
            return True
        except Exception as e:
            print(f"Error saving DPCI assessment: {e}")
            if 'temp_filepath' in locals() and temp_filepath.exists():
                temp_filepath.unlink()
            return False
    
    def load_assessment(self, filepath: str) -> Optional[DPCIAssessment]:
        """Load DPCI assessment from JSON file."""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return DPCIAssessment.from_dict(data)
        except Exception as e:
            print(f"Error loading DPCI assessment: {e}")
            return None
    
    def list_assessments(self) -> List[Dict[str, any]]:
        """List all DPCI assessments."""
        assessments = []
        
        for search_dir in [self.base_dir, self.assessments_dir]:
            if not search_dir.exists():
                continue
            
            for assessment_file in search_dir.rglob("*.json"):
                try:
                    assessment = self.load_assessment(str(assessment_file))
                    if not assessment:
                        continue
                    
                    info = {
                        'filepath': str(assessment_file),
                        'filename': assessment_file.name,
                        'assessment_id': assessment.assessment_id,
                        'project_name': assessment.project_name or 'Untitled',
                        'created_date': assessment.created_date,
                        'modified_date': assessment.modified_date,
                        'dpci_index': assessment.get_dpci_index(),
                        'risk_level': assessment.get_overall_risk_level().value,
                        'file_size': assessment_file.stat().st_size
                    }
                    assessments.append(info)
                except Exception as e:
                    print(f"Error reading assessment {assessment_file}: {e}")
                    continue
        
        assessments.sort(key=lambda x: x.get('modified_date', ''), reverse=True)
        return assessments
    
    def get_assessments_dir(self) -> Path:
        """Get the assessments directory path."""
        return self.assessments_dir
    
    def get_export_dir(self) -> Path:
        """Get the exports directory path."""
        return self.exports_dir
