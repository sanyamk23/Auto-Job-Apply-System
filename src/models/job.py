"""
Job model for storing job listings and related information.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, Integer, JSON, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class Job(BaseModel):
    """Job model representing job listings."""

    __tablename__ = "jobs"

    # Job identification
    job_id = Column(String(100), unique=True, index=True, nullable=False)  # External job ID
    source_id = Column(String(50), index=True)  # e.g., "linkedin", "indeed"

    # Basic job information
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    location_type = Column(String(50))  # e.g., "remote", "hybrid", "onsite"

    # Job details
    description = Column(Text)
    description_text = Column(Text)  # Clean text version
    requirements = Column(JSON, default=list)  # List of required skills
    employment_type = Column(JSON, default=list)  # e.g., ["FULL_TIME"], ["CONTRACTOR"]

    # Compensation and level
    salary_raw = Column(String(200))
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10), default="USD")
    experience_level = Column(String(50))  # e.g., "Entry level", "Mid-Senior level"

    # Dates
    date_posted = Column(DateTime)
    date_validthrough = Column(DateTime)

    # Company information
    company_logo = Column(String(500))
    linkedin_org_url = Column(String(500))
    linkedin_org_employees = Column(Integer)
    linkedin_org_industry = Column(String(200))
    linkedin_org_size = Column(String(100))  # e.g., "1,001-5,000 employees"

    # Contact information
    hr_contact_email = Column(String(255))
    hr_contact_name = Column(String(100))
    external_apply_url = Column(String(500))

    # Additional metadata
    source = Column(String(50))  # e.g., "linkedin", "indeed"
    source_domain = Column(String(100))  # e.g., "linkedin.com"
    url = Column(String(500))  # Job posting URL

    # System flags
    is_active = Column(Boolean, default=True)
    is_directapply = Column(Boolean, default=False)

    # Derived/location data
    cities_derived = Column(JSON, default=list)
    counties_derived = Column(JSON, default=list)
    regions_derived = Column(JSON, default=list)
    countries_derived = Column(JSON, default=list)
    locations_derived = Column(JSON, default=list)
    timezones_derived = Column(JSON, default=list)
    remote_derived = Column(Boolean, default=False)

    # Relationships - will be set up after all models are imported
    # applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, job_id={self.job_id}, title={self.title}, company={self.company})>"

    @property
    def requirements_list(self) -> List[str]:
        """Get requirements as a list."""
        return self.requirements or []

    @property
    def employment_types_list(self) -> List[str]:
        """Get employment types as a list."""
        return self.employment_type or []

    @property
    def cities_list(self) -> List[str]:
        """Get derived cities as a list."""
        return self.cities_derived or []

    @property
    def locations_list(self) -> List[str]:
        """Get derived locations as a list."""
        return self.locations_derived or []

    def has_requirement(self, skill: str) -> bool:
        """Check if job requires a specific skill."""
        return skill.lower() in [r.lower() for r in self.requirements_list]

    def matches_skills(self, user_skills: List[str]) -> int:
        """Count matching skills between job requirements and user skills."""
        if not user_skills or not self.requirements_list:
            return 0

        user_skills_lower = [s.lower() for s in user_skills]
        job_reqs_lower = [r.lower() for r in self.requirements_list]

        return len(set(user_skills_lower) & set(job_reqs_lower))

    def is_remote(self) -> bool:
        """Check if job is remote."""
        return (self.remote_derived or
                self.location_type == "remote" or
                "remote" in (self.location or "").lower())

    def is_expired(self) -> bool:
        """Check if job posting has expired."""
        if not self.date_validthrough:
            return False
        return datetime.utcnow() > self.date_validthrough

    @classmethod
    def create_from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Create Job instance from dictionary data (e.g., from API responses)."""
        # Handle dates
        date_posted = None
        if data.get('date_posted'):
            if isinstance(data['date_posted'], str):
                date_posted = datetime.fromisoformat(data['date_posted'].replace('Z', '+00:00'))
            else:
                date_posted = data['date_posted']

        date_validthrough = None
        if data.get('date_validthrough'):
            if isinstance(data['date_validthrough'], str):
                date_validthrough = datetime.fromisoformat(data['date_validthrough'].replace('Z', '+00:00'))
            else:
                date_validthrough = data['date_validthrough']

        # Handle salary parsing (basic implementation)
        salary_min = None
        salary_max = None
        salary_currency = "USD"

        if data.get('salary_raw'):
            salary_str = data['salary_raw']
            # Simple parsing - could be enhanced
            if '$' in salary_str:
                salary_currency = "USD"
            # Extract numbers - basic implementation
            import re
            numbers = re.findall(r'\d+', salary_str.replace(',', ''))
            if len(numbers) >= 2:
                salary_min = float(numbers[0])
                salary_max = float(numbers[1])
            elif len(numbers) == 1:
                salary_min = float(numbers[0])

        # Handle HR contact
        hr_contact = data.get('hr_contact', {})
        if isinstance(hr_contact, dict):
            hr_email = hr_contact.get('email')
            hr_name = hr_contact.get('name')
        else:
            hr_email = None
            hr_name = None

        return cls(
            job_id=data.get('id', data.get('job_id', f"job_{datetime.utcnow().timestamp()}")),
            source_id=data.get('source_id'),
            title=data.get('title', ''),
            company=data.get('company', ''),
            location=data.get('location'),
            location_type=data.get('location_type'),
            description=data.get('description'),
            description_text=data.get('description_text'),
            requirements=data.get('requirements', []),
            employment_type=data.get('employment_type', []),
            salary_raw=data.get('salary_raw'),
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=salary_currency,
            experience_level=data.get('seniority', data.get('experience_level')),
            date_posted=date_posted,
            date_validthrough=date_validthrough,
            company_logo=data.get('organization_logo', data.get('company_logo')),
            linkedin_org_url=data.get('linkedin_org_url'),
            linkedin_org_employees=data.get('linkedin_org_employees'),
            linkedin_org_industry=data.get('linkedin_org_industry'),
            linkedin_org_size=data.get('linkedin_org_size'),
            hr_contact_email=hr_email,
            hr_contact_name=hr_name,
            external_apply_url=data.get('external_apply_url'),
            source=data.get('source'),
            source_domain=data.get('source_domain'),
            url=data.get('url'),
            is_directapply=data.get('directapply', False),
            cities_derived=data.get('cities_derived', []),
            counties_derived=data.get('counties_derived', []),
            regions_derived=data.get('regions_derived', []),
            countries_derived=data.get('countries_derived', []),
            locations_derived=data.get('locations_derived', []),
            timezones_derived=data.get('timezones_derived', []),
            remote_derived=data.get('remote_derived', False)
        )
