"""
Updated JobSearchEngine to persist jobs in database.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.api.linkedin_api import LinkedInAPI
import re
from difflib import SequenceMatcher

from src.db.session import get_db_context
from src.models.job import Job


class JobSearchEngine:
    """Job search engine with database persistence."""

    def __init__(self):
        self.apis = {
            'linkedin': LinkedInAPI(),
        }

        self.simulated_jobs = self._load_simulated_jobs()

    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        skills: Optional[List[str]] = None,
        user_data: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search jobs across all available APIs with enhanced matching"""
        all_jobs = []

        print(f"🔍 Searching for '{query}' jobs..." + (f" in {location}" if location else ""))

        # Try each API
        for api_name, api in self.apis.items():
            try:
                if api.is_available():
                    print(f"   Checking {api_name}...")
                    jobs = api.search_jobs(query, location, skills)
                    all_jobs.extend(jobs)
                    print(f"   ✅ Found {len(jobs)} jobs from {api_name}")
            except Exception as e:
                print(f"   ❌ {api_name} search failed: {e}")

        # If no real jobs found, use simulated data
        if not all_jobs:
            print("   ⚠️  Using simulated job data")
            all_jobs = self._get_simulated_jobs(query, location, skills)

        # Remove duplicates
        unique_jobs = self._remove_duplicates(all_jobs)

        # Persist jobs to database
        self._persist_jobs(unique_jobs)

        # Score and rank jobs if user data is provided
        if user_data and skills:
            unique_jobs = self._rank_jobs(unique_jobs, user_data, skills)

        return unique_jobs

    def _persist_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        """Persist jobs to database."""
        try:
            with get_db_context() as db:
                for job_data in jobs:
                    # Check if job already exists
                    existing = db.query(Job).filter(Job.job_id == job_data.get('id')).first()
                    if existing:
                        continue

                    try:
                        # Convert job data to Job model format
                        job_dict = {
                            'job_id': job_data.get('id'),
                            'title': job_data.get('title', 'Unknown Title'),
                            'company': job_data.get('company', 'Unknown Company'),
                            'location': job_data.get('location', 'Remote'),
                            'description': job_data.get('description', ''),
                            'requirements': job_data.get('requirements', []),
                            'salary_raw': job_data.get('salary_range'),
                            'experience_level': job_data.get('experience_level', 'Mid-level'),
                            'hr_contact_email': job_data.get('hr_contact', {}).get('email'),
                            'hr_contact_name': job_data.get('hr_contact', {}).get('name'),
                            'url': job_data.get('url', ''),
                            'source': 'simulated' if 'id' in job_data and job_data['id'].isdigit() else 'api'
                        }

                        job = Job.create_from_dict(job_dict)
                        db.add(job)

                    except Exception as e:
                        print(f"   ⚠️  Failed to persist job {job_data.get('id')}: {e}")
                        continue

                db.commit()

        except SQLAlchemyError as e:
            print(f"Database error persisting jobs: {e}")

    def get_persisted_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get jobs from database with optional filtering."""
        try:
            with get_db_context() as db:
                jobs_query = db.query(Job).filter(Job.is_active == True)

                if query:
                    # Simple text search in title and company
                    search_term = f"%{query}%"
                    jobs_query = jobs_query.filter(
                        (Job.title.ilike(search_term)) |
                        (Job.company.ilike(search_term)) |
                        (Job.description.ilike(search_term))
                    )

                if location and location.lower() != 'remote':
                    location_term = f"%{location}%"
                    jobs_query = jobs_query.filter(Job.location.ilike(location_term))

                jobs = jobs_query.order_by(Job.created_at.desc()).limit(limit).all()
                return [job.to_dict() for job in jobs]

        except SQLAlchemyError as e:
            print(f"Database error getting persisted jobs: {e}")
            return []

    def _get_simulated_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        skills: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get simulated jobs with improved matching"""
        query_lower = query.lower()
        filtered_jobs = []

        for job in self.simulated_jobs:
            score = 0

            # Title matching (highest weight)
            if query_lower in job['title'].lower():
                score += 10
            elif self._fuzzy_match(query_lower, job['title'].lower(), threshold=0.6):
                score += 5

            # Skills matching
            if skills:
                job_requirements = [req.lower() for req in job.get('requirements', [])]
                user_skills_lower = [s.lower() for s in skills]

                matching_skills = set(job_requirements) & set(user_skills_lower)
                score += len(matching_skills) * 3

            # Query terms in requirements
            for requirement in job.get('requirements', []):
                if query_lower in requirement.lower():
                    score += 2

            # Location matching
            location_match = True
            if location and job.get('location'):
                job_location = job['location'].lower()
                location_lower = location.lower()

                # Exact match or contains
                if location_lower == job_location or location_lower in job_location:
                    score += 5
                    location_match = True
                # Remote preference
                elif 'remote' in location_lower and 'remote' in job_location:
                    score += 5
                    location_match = True
                else:
                    location_match = False
                    score -= 2  # Penalty for location mismatch

            # Only include jobs with positive scores
            if score > 0 or not location:
                job['match_score'] = score
                filtered_jobs.append(job)

        # Sort by match score
        filtered_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)

        return filtered_jobs[:20]  # Return top 20 matches

    def _rank_jobs(
        self,
        jobs: List[Dict],
        user_data: Dict,
        user_skills: List[str]
    ) -> List[Dict]:
        """Rank jobs based on user profile matching"""
        for job in jobs:
            if 'match_score' not in job:
                score = 0

                # Skills matching
                job_requirements = [req.lower() for req in job.get('requirements', [])]
                user_skills_lower = [s.lower() for s in user_skills]

                matching_skills = set(job_requirements) & set(user_skills_lower)
                total_required = len(job_requirements) if job_requirements else 1

                skill_match_rate = len(matching_skills) / total_required
                score += skill_match_rate * 100

                # Experience level matching
                experience = user_data.get('experience', '0 years')
                years_exp = self._extract_years(experience)

                if years_exp >= 5:
                    if 'senior' in job['title'].lower():
                        score += 20
                elif years_exp >= 2:
                    if 'mid' in job['title'].lower() or 'intermediate' in job['title'].lower():
                        score += 20
                else:
                    if 'junior' in job['title'].lower() or 'entry' in job['title'].lower():
                        score += 20

                # Location preference
                preferred_locations = user_data.get('preferred_locations', [])
                job_location = job.get('location', '').lower()

                for pref_loc in preferred_locations:
                    if pref_loc.lower() in job_location:
                        score += 15
                        break

                job['match_score'] = score

        # Sort by match score
        jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return jobs

    def _fuzzy_match(self, str1: str, str2: str, threshold: float = 0.7) -> bool:
        """Check if two strings are similar using fuzzy matching"""
        ratio = SequenceMatcher(None, str1, str2).ratio()
        return ratio >= threshold

    def _extract_years(self, experience_str: str) -> int:
        """Extract years from experience string"""
        match = re.search(r'(\d+)\s*year', experience_str.lower())
        return int(match.group(1)) if match else 0

    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs with improved detection"""
        seen = set()
        unique_jobs = []

        for job in jobs:
            # Create a more robust key
            title = job['title'].lower().strip()
            company = job['company'].lower().strip()
            location = job.get('location', '').lower().strip()

            key = (title, company, location)

            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs

    def _load_simulated_jobs(self) -> List[Dict]:
        """Load comprehensive simulated job data"""
        return [
            {
                'id': '1',
                'title': 'Senior Software Engineer',
                'company': 'Tech Innovations Inc',
                'location': 'Remote',
                'description': 'Senior role for full-stack development with 5+ years experience.',
                'requirements': ['Python', 'JavaScript', 'React', 'AWS', 'Docker'],
                'salary_range': '$120,000 - $160,000',
                'experience_level': 'Senior',
                'hr_contact': {'email': '2004shakti@gmail.com', 'name': 'Sarah Kim'}
            },
            {
                'id': '2',
                'title': 'Data Scientist',
                'company': 'Data Corp',
                'location': 'New York, NY',
                'description': 'Machine learning and data analysis role with statistical modeling.',
                'requirements': ['Python', 'Machine Learning', 'SQL', 'TensorFlow', 'Statistics'],
                'salary_range': '$100,000 - $140,000',
                'experience_level': 'Mid-level',
                'hr_contact': {'email': 'hr@datacorp.com', 'name': 'Mike Chen'}
            },
            {
                'id': '3',
                'title': 'Frontend Developer',
                'company': 'Web Solutions',
                'location': 'San Francisco, CA',
                'description': 'React and TypeScript focused role building modern web applications.',
                'requirements': ['JavaScript', 'React', 'TypeScript', 'CSS', 'HTML'],
                'salary_range': '$90,000 - $130,000',
                'experience_level': 'Mid-level',
                'hr_contact': {'email': 'jobs@websolutions.com', 'name': 'Emily Davis'}
            },
            {
                'id': '4',
                'title': 'DevOps Engineer',
                'company': 'Cloud Systems',
                'location': 'Remote',
                'description': 'Cloud infrastructure and automation with CI/CD pipelines.',
                'requirements': ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'Python'],
                'salary_range': '$110,000 - $150,000',
                'experience_level': 'Mid-level',
                'hr_contact': {'email': 'recruiting@cloudsystems.com', 'name': 'David Wilson'}
            },
            {
                'id': '5',
                'title': 'Full Stack Developer',
                'company': 'StartUp Ventures',
                'location': 'Austin, TX',
                'description': 'Early-stage startup full-stack role with equity options.',
                'requirements': ['Python', 'JavaScript', 'React', 'Node.js', 'MongoDB'],
                'salary_range': '$85,000 - $120,000',
                'experience_level': 'Mid-level',
                'hr_contact': {'email': 'team@startupventures.com', 'name': 'Alex Rodriguez'}
            },
            {
                'id': '6',
                'title': 'Backend Engineer',
                'company': 'API Masters',
                'location': 'Remote',
                'description': 'API development and microservices architecture.',
                'requirements': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Docker'],
                'salary_range': '$95,000 - $135,000',
                'experience_level': 'Mid-level',
                'hr_contact': {'email': 'jobs@apimasters.com', 'name': 'Jessica Brown'}
            },
            {
                'id': '7',
                'title': 'Machine Learning Engineer',
                'company': 'AI Solutions',
                'location': 'Boston, MA',
                'description': 'ML model development and deployment with MLOps practices.',
                'requirements': ['Python', 'PyTorch', 'TensorFlow', 'MLOps', 'Docker'],
                'salary_range': '$115,000 - $155,000',
                'experience_level': 'Senior',
                'hr_contact': {'email': 'careers@aisolutions.com', 'name': 'Robert Taylor'}
            },
            {
                'id': '8',
                'title': 'Junior Software Developer',
                'company': 'Digital Creations',
                'location': 'Chicago, IL',
                'description': 'Entry-level software development role with mentorship.',
                'requirements': ['Java', 'Spring Boot', 'SQL', 'JavaScript', 'AWS'],
                'salary_range': '$60,000 - $80,000',
                'experience_level': 'Entry-level',
                'hr_contact': {'email': 'hr@digitalcreations.com', 'name': 'Lisa Anderson'}
            },
            {
                'id': '9',
                'title': 'React Developer',
                'company': 'Mobile First',
                'location': 'Remote',
                'description': 'React and React Native development for mobile apps.',
                'requirements': ['React', 'React Native', 'JavaScript', 'TypeScript', 'Redux'],
                'salary_range': '$85,000 - $125,000',
                'experience_level': 'Mid-level',
                'hr_contact': {'email': 'jobs@mobilefirst.com', 'name': 'Tom Martinez'}
            },
            {
                'id': '10',
                'title': 'Python Developer',
                'company': 'Code Factory',
                'location': 'Seattle, WA',
                'description': 'Python backend development with Django framework.',
                'requirements': ['Python', 'Django', 'PostgreSQL', 'REST API', 'Docker'],
                'salary_range': '$90,000 - $130,000',
                'experience_level': 'Mid-level',
                'hr_contact': {'email': 'careers@codefactory.com', 'name': 'Anna Lee'}
            },
            {
                'id': '11',
                'title': 'Cloud Architect',
                'company': 'Enterprise Solutions',
                'location': 'Remote',
                'description': 'Design and implement cloud infrastructure solutions.',
                'requirements': ['AWS', 'Azure', 'Terraform', 'Kubernetes', 'Python'],
                'salary_range': '$140,000 - $180,000',
                'experience_level': 'Senior',
                'hr_contact': {'email': 'jobs@enterprisesolutions.com', 'name': 'Chris Johnson'}
            },
            {
                'id': '12',
                'title': 'QA Engineer',
                'company': 'Quality First',
                'location': 'Denver, CO',
                'description': 'Automated testing and quality assurance.',
                'requirements': ['Selenium', 'Python', 'JavaScript', 'CI/CD', 'Git'],
                'salary_range': '$75,000 - $105,000',
                'experience_level': 'Mid-level',
                'hr_contact': {'email': 'hr@qualityfirst.com', 'name': 'Maria Garcia'}
            }
        ]
