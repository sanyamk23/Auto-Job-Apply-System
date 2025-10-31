"""
Resume model for storing user resume information.
"""
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class Resume(BaseModel):
    """Resume model for storing user resume data."""

    __tablename__ = "resumes"

    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Resume metadata
    filename = Column(String(255))  # Original filename
    file_path = Column(String(500))  # Path to stored file
    content_type = Column(String(100))  # MIME type (e.g., "application/pdf")

    # Extracted content
    raw_text = Column(Text)  # Full text extracted from resume
    summary = Column(Text)  # AI-generated summary

    # Parsed information
    skills_extracted = Column(Text)  # JSON string of extracted skills
    experience_years = Column(Integer)  # Estimated years of experience
    education_level = Column(String(100))  # e.g., "Bachelor's", "Master's"

    # Processing status
    is_processed = Column(String(50), default="pending")  # pending, processing, completed, failed

    # Relationships
    user = relationship("User", backref="resumes")

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename={self.filename})>"

    @property
    def is_processing_complete(self) -> bool:
        """Check if resume processing is complete."""
        return self.is_processed == "completed"

    @property
    def has_failed_processing(self) -> bool:
        """Check if resume processing has failed."""
        return self.is_processed == "failed"

    def mark_processing_complete(self) -> None:
        """Mark resume processing as complete."""
        self.is_processed = "completed"

    def mark_processing_failed(self) -> None:
        """Mark resume processing as failed."""
        self.is_processed = "failed"

    @classmethod
    def create_from_upload(cls, user_id: int, filename: str, file_path: str, content_type: str) -> "Resume":
        """Create Resume instance from file upload."""
        return cls(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            content_type=content_type,
            is_processed="pending"
        )
