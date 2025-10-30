from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class HRContact(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str]


class Job(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str]
    description: Optional[str]
    requirements: Optional[List[str]] = Field(default_factory=list)
    salary_range: Optional[str]
    hr_contact: Optional[HRContact]


class UserProfile(BaseModel):
    user_id: Optional[str]
    name: str
    email: Optional[EmailStr]
    phone: Optional[str]
    skills: List[str] = Field(default_factory=list)
    experience: Optional[str]
    education: Optional[List[str]] = Field(default_factory=list)
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=lambda: ["Remote"])
    experience_level: Optional[str] = "Mid-level"
    resume_path: Optional[str]
    resume_summary: Optional[str]


class JobRecommendation(BaseModel):
    job: Job
    match_score: int
    reason: Optional[str]


class SearchRequest(BaseModel):
    user_id: Optional[str]
    user_profile: Optional[UserProfile]
    query: Optional[str]
    location: Optional[str]


class ApplyRequest(BaseModel):
    user_id: Optional[str]
    user_profile: Optional[UserProfile]
    job: Job


class ApplicationRecord(BaseModel):
    application_id: str
    applicant_name: str
    applicant_email: Optional[EmailStr]
    company: str
    position: str
    applied_at: str
    status: str
    hr_contact: Optional[str]
    location: Optional[str]
