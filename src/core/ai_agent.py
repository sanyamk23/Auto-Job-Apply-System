"""
Mock AI Agent for job application system - provides basic functionality without AI dependencies.
"""
import json
from typing import List, Dict, Any


class JobSearchAgent:
    """Mock AI agent that provides basic job search and application functionality."""

    def __init__(self):
        # No AI initialization needed
        pass

    def create_search_strategy(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic job search strategy"""
        skills = user_profile.get('skills', [])
        preferred_roles = user_profile.get('preferred_roles', [])

        return {
            "strategy": "Keyword-based search using user skills and preferred roles",
            "keywords": skills + preferred_roles,
            "job_titles": preferred_roles if preferred_roles else skills,
            "companies": [],
            "search_tips": ["Focus on skills matching", "Highlight relevant experience"]
        }

    def rank_jobs(self, user_profile: Dict[str, Any], jobs: List[Dict]) -> List[Dict]:
        """Basic job ranking based on skills matching"""
        user_skills = set(user_profile.get('skills', []))
        ranked_jobs = []

        for job in jobs[:10]:  # Limit to first 10
            job_skills = set(job.get('requirements', []))
            matching_skills = len(user_skills & job_skills)
            total_skills = len(job_skills) if job_skills else 1

            # Simple scoring: percentage of matching skills
            match_score = min(10, int((matching_skills / total_skills) * 10))

            ranked_jobs.append({
                'job': job,
                'match_score': max(1, match_score),  # Minimum score of 1
                'reason': f'{matching_skills} matching skills out of {total_skills}'
            })

        # Sort by match score
        ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        return ranked_jobs

    def generate_cover_letter(self, user_profile: Dict, job: Dict) -> str:
        """Generate a basic cover letter template"""
        name = user_profile.get('name', 'Candidate')
        skills = ', '.join(user_profile.get('skills', ['various skills']))
        experience = user_profile.get('experience', 'professional experience')

        job_title = job.get('title', 'Position')
        company = job.get('company', 'Company')
        requirements = ', '.join(job.get('requirements', ['required skills']))

        return f"""
Dear Hiring Manager,

I am excited to apply for the {job_title} role at {company}. With my background in {skills} and {experience}, I am confident in my ability to contribute to your team.

My skills align well with your requirements for {requirements}, and I am eager to bring my expertise to this role.

Thank you for considering my application.

Sincerely,
{name}
"""

    def generate_application_email(self, user_profile: Dict, job: Dict, cover_letter: str) -> Dict[str, str]:
        """Generate a basic application email"""
        name = user_profile.get('name', 'Candidate')
        email = user_profile.get('email', 'candidate@email.com')
        job_title = job.get('title', 'Position')
        company = job.get('company', 'Company')

        return {
            "subject": f"Application for {job_title} - {name}",
            "body": f"""
Dear Hiring Team,

{cover_letter.strip()}

Please find my resume attached. I look forward to the opportunity to discuss how I can contribute to {company}.

Best regards,
{name}
{email}
"""
        }
