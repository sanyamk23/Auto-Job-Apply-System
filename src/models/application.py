"""
Application model for storing job application records.
"""
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class Application(BaseModel):
    """Application model representing job applications."""

    __tablename__ = "applications"

    # Application identification
    application_id = Column(String(100), unique=True, index=True, nullable=False)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)

    # Application details
    applicant_name = Column(String(100), nullable=False)
    applicant_email = Column(String(255), nullable=False)

    # Job information (denormalized for quick access)
    company = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    location = Column(String(200))

    # Application status and tracking
    status = Column(String(50), default="Applied")  # Applied, Interviewing, Rejected, Accepted, etc.
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Contact information
    hr_contact = Column(String(255))  # HR email or contact info

    # Application metadata
    cover_letter_sent = Column(Boolean, default=False)
    resume_sent = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)

    # Additional notes
    notes = Column(Text)

    # Relationships - will be set up after all models are imported
    # user = relationship("User", back_populates="applications")
    # job = relationship("Job", back_populates="applications")

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, application_id={self.application_id}, user_id={self.user_id}, job_id={self.job_id}, status={self.status})>"

    @property
    def is_successful(self) -> bool:
        """Check if application was successful."""
        return self.status.lower() in ["accepted", "hired", "offer"]

    @property
    def is_pending(self) -> bool:
        """Check if application is still pending."""
        return self.status.lower() in ["applied", "interviewing", "reviewing"]

    @property
    def is_rejected(self) -> bool:
        """Check if application was rejected."""
        return self.status.lower() in ["rejected", "declined"]

    def update_status(self, new_status: str) -> None:
        """Update application status."""
        valid_statuses = [
            "Applied", "Reviewing", "Interviewing", "Offer", "Accepted",
            "Rejected", "Declined", "Withdrawn", "Expired"
        ]

        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {valid_statuses}")

        self.status = new_status
        self.updated_at = datetime.utcnow()

    @classmethod
    def create_from_dict(cls, data: dict, user_id: int, job_id: int) -> "Application":
        """Create Application instance from dictionary data."""
        applied_at = data.get('applied_at')
        if isinstance(applied_at, str):
            applied_at = datetime.fromisoformat(applied_at.replace('Z', '+00:00'))

        return cls(
            application_id=data.get('application_id', f"app_{datetime.utcnow().timestamp()}"),
            user_id=user_id,
            job_id=job_id,
            applicant_name=data.get('applicant_name', ''),
            applicant_email=data.get('applicant_email', ''),
            company=data.get('company', ''),
            position=data.get('position', ''),
            location=data.get('location'),
            status=data.get('status', 'Applied'),
            applied_at=applied_at or datetime.utcnow(),
            hr_contact=data.get('hr_contact'),
            cover_letter_sent=data.get('cover_letter_sent', False),
            resume_sent=data.get('resume_sent', False),
            email_sent=data.get('email_sent', False),
            notes=data.get('notes')
        )
