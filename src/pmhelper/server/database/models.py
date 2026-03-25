"""
SQLAlchemy Database Models for PMHelper Server

Defines the database schema for projects and analysis jobs.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, VARCHAR
import json


# Custom UUID type for SQLite compatibility
class UUIDType(TypeDecorator):
    """Platform-independent UUID type."""
    impl = VARCHAR
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(VARCHAR(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, uuid.UUID):
            return str(value)
        else:
            return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


Base = declarative_base()


class Project(Base):
    """Model for storing project data."""
    
    __tablename__ = "projects"
    
    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    data = Column(JSON, nullable=False)  # Store activities and project data as JSON
    project_metadata = Column(JSON, nullable=True)  # Additional project metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship to analysis jobs
    analysis_jobs = relationship("AnalysisJob", back_populates="project", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "metadata": self.project_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AnalysisJob(Base):
    """Model for storing analysis job information and results."""
    
    __tablename__ = "analysis_jobs"
    
    job_id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    project_id = Column(UUIDType, ForeignKey("projects.id"), nullable=True, index=True)
    analysis_type = Column(String(50), nullable=False, index=True)  # 'cpm', 'pert', 'rcps'
    status = Column(String(20), nullable=False, default="pending", index=True)  # 'pending', 'running', 'completed', 'failed'
    input_data = Column(JSON, nullable=False)  # Input parameters and data
    results = Column(JSON, nullable=True)  # Analysis results
    error_message = Column(Text, nullable=True)  # Error details if failed
    progress = Column(String(10), nullable=True)  # Progress percentage (e.g., "45%")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationship to project
    project = relationship("Project", back_populates="analysis_jobs")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis job to dictionary."""
        return {
            "job_id": str(self.job_id),
            "project_id": str(self.project_id) if self.project_id else None,
            "analysis_type": self.analysis_type,
            "status": self.status,
            "input_data": self.input_data,
            "results": self.results,
            "error_message": self.error_message,
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def mark_started(self):
        """Mark the job as started."""
        self.status = "running"
        self.started_at = datetime.now(timezone.utc)
    
    def mark_completed(self, results: Dict[str, Any]):
        """Mark the job as completed with results."""
        self.status = "completed"
        self.results = results
        self.completed_at = datetime.now(timezone.utc)
        self.progress = "100%"
    
    def mark_failed(self, error_message: str):
        """Mark the job as failed with error message."""
        self.status = "failed"
        self.error_message = error_message
        self.completed_at = datetime.now(timezone.utc)


# Export all models for easy import
__all__ = ["Base", "Project", "AnalysisJob", "UUIDType"]