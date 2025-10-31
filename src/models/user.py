"""
User model for storing user profiles and preferences.
"""
from typing import List, Optional
from sqlalchemy import Column, String, Text, Integer, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """User model representing job seekers."""

    __tablename__ = "users"

    # Basic user information
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Professional information
    experience = Column(String(100))  # e.g., "2 years", "5+ years"
    experience_level = Column(String(50))  # e.g., "Entry-level", "Mid-level", "Senior"

    # Skills and preferences
    skills = Column(JSON, default=list)  # List of skills
    preferred_roles = Column(JSON, default=list)  # List of preferred job roles
    preferred_locations = Column(JSON, default=list)  # List of preferred locations

    # Additional information
    resume_summary = Column(Text)  # Summary of resume/experience
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))

    # System flags
    is_active = Column(Boolean, default=True)
    is_test_user = Column(Boolean, default=False)

    # Relationships - will be set up after all models are imported
    # applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, user_id={self.user_id}, name={self.name}, email={self.email})>"

    @property
    def skills_list(self) -> List[str]:
        """Get skills as a list."""
        return self.skills or []

    @property
    def preferred_roles_list(self) -> List[str]:
        """Get preferred roles as a list."""
        return self.preferred_roles or []

    @property
    def preferred_locations_list(self) -> List[str]:
        """Get preferred locations as a list."""
        return self.preferred_locations or []

    def has_skill(self, skill: str) -> bool:
        """Check if user has a specific skill."""
        return skill.lower() in [s.lower() for s in self.skills_list]

    def matches_location(self, location: str) -> bool:
        """Check if location matches user preferences."""
        if not self.preferred_locations_list:
            return True  # No location preference means any location is fine

        location_lower = location.lower()
        for pref_loc in self.preferred_locations_list:
            if pref_loc.lower() in location_lower or location_lower in pref_loc.lower():
                return True
        return False

    @classmethod
    def create_from_dict(cls, data: dict) -> "User":
        """Create User instance from dictionary data."""
        # Handle skills, preferred_roles, preferred_locations as lists
        skills = data.get('skills', [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',')]

        preferred_roles = data.get('preferred_roles', [])
        if isinstance(preferred_roles, str):
            preferred_roles = [r.strip() for r in preferred_roles.split(',')]

        preferred_locations = data.get('preferred_locations', [])
        if isinstance(preferred_locations, str):
            preferred_locations = [l.strip() for l in preferred_locations.split(',')]

        return cls(
            user_id=data.get('user_id', f"user_{data.get('name', 'unknown').replace(' ', '_').lower()}"),
            name=data.get('name', ''),
            email=data.get('email', ''),
            experience=data.get('experience', ''),
            experience_level=data.get('experience_level', 'Mid-level'),
            skills=skills,
            preferred_roles=preferred_roles,
            preferred_locations=preferred_locations,
            resume_summary=data.get('resume_summary', ''),
            linkedin_url=data.get('linkedin_url'),
            github_url=data.get('github_url'),
            portfolio_url=data.get('portfolio_url'),
            is_test_user=data.get('is_test_user', False)
        )
