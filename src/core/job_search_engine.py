from typing import List, Dict, Any
from api.linkedin_api import LinkedInAPI

class JobSearchEngine:
    def __init__(self):
        self.apis = {
            # Use LinkedIn (via RapidAPI proxy) as the primary source per user request
            'linkedin': LinkedInAPI(),
            # 'google': GoogleJobsAPI(),
            # 'indeed': IndeedAPI(),
        }
        
        # Fallback simulated jobs
        self.simulated_jobs = self._load_simulated_jobs()
    
    def search_jobs(self, query: str, location: str = None, skills: List[str] = None) -> List[Dict[str, Any]]:
        """Search jobs across all available APIs"""
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
        
        # Remove duplicates based on title and company
        unique_jobs = self._remove_duplicates(all_jobs)
        
        return unique_jobs
    
    def _get_simulated_jobs(self, query: str, location: str = None, skills: List[str] = None) -> List[Dict]:
        """Get simulated jobs based on query"""
        query_lower = query.lower()
        filtered_jobs = []
        
        for job in self.simulated_jobs:
            # Match by query in title or requirements
            title_match = query_lower in job['title'].lower()
            skills_match = any(skill.lower() in query_lower for skill in job.get('requirements', []))
            
            # Location matching
            location_match = True
            if location and job.get('location'):
                location_match = location.lower() in job['location'].lower()
            
            if (title_match or skills_match) and location_match:
                filtered_jobs.append(job)
        
        return filtered_jobs[:15]  # Limit results
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _load_simulated_jobs(self) -> List[Dict]:
        """Load comprehensive simulated job data"""
        return [
            {
                'id': '1', 'title': 'Senior Software Engineer', 'company': 'Tech Innovations Inc', 
                'location': 'Remote', 'description': 'Senior role for full-stack development.',
                'requirements': ['Python', 'JavaScript', 'React', 'AWS', 'Docker'],
                'salary_range': '$120,000 - $160,000',
                'hr_contact': {'email': '2004shakti@gmail.com', 'name': 'Sarah Kim'}
            },
            {
                'id': '2', 'title': 'Data Scientist', 'company': 'Data Corp', 
                'location': 'New York, NY', 'description': 'Machine learning and data analysis role.',
                'requirements': ['Python', 'Machine Learning', 'SQL', 'TensorFlow', 'Statistics'],
                'salary_range': '$100,000 - $140,000', 
                'hr_contact': {'email': 'hr@datacorp.com', 'name': 'Mike Chen'}
            },
            {
                'id': '3', 'title': 'Frontend Developer', 'company': 'Web Solutions', 
                'location': 'San Francisco, CA', 'description': 'React and TypeScript focused role.',
                'requirements': ['JavaScript', 'React', 'TypeScript', 'CSS', 'HTML'],
                'salary_range': '$90,000 - $130,000',
                'hr_contact': {'email': 'jobs@websolutions.com', 'name': 'Emily Davis'}
            },
            {
                'id': '4', 'title': 'DevOps Engineer', 'company': 'Cloud Systems', 
                'location': 'Remote', 'description': 'Cloud infrastructure and automation role.',
                'requirements': ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'Python'],
                'salary_range': '$110,000 - $150,000',
                'hr_contact': {'email': 'recruiting@cloudsystems.com', 'name': 'David Wilson'}
            },
            {
                'id': '5', 'title': 'Full Stack Developer', 'company': 'StartUp Ventures', 
                'location': 'Austin, TX', 'description': 'Early-stage startup full-stack role.',
                'requirements': ['Python', 'JavaScript', 'React', 'Node.js', 'MongoDB'],
                'salary_range': '$85,000 - $120,000',
                'hr_contact': {'email': 'team@startupventures.com', 'name': 'Alex Rodriguez'}
            },
            {
                'id': '6', 'title': 'Backend Engineer', 'company': 'API Masters', 
                'location': 'Remote', 'description': 'API development and microservices.',
                'requirements': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Docker'],
                'salary_range': '$95,000 - $135,000',
                'hr_contact': {'email': 'jobs@apimasters.com', 'name': 'Jessica Brown'}
            },
            {
                'id': '7', 'title': 'Machine Learning Engineer', 'company': 'AI Solutions', 
                'location': 'Boston, MA', 'description': 'ML model development and deployment.',
                'requirements': ['Python', 'PyTorch', 'TensorFlow', 'MLOps', 'Docker'],
                'salary_range': '$115,000 - $155,000',
                'hr_contact': {'email': 'careers@aisolutions.com', 'name': 'Robert Taylor'}
            },
            {
                'id': '8', 'title': 'Software Developer', 'company': 'Digital Creations', 
                'location': 'Chicago, IL', 'description': 'General software development role.',
                'requirements': ['Java', 'Spring Boot', 'SQL', 'JavaScript', 'AWS'],
                'salary_range': '$80,000 - $110,000',
                'hr_contact': {'email': 'hr@digitalcreations.com', 'name': 'Lisa Anderson'}
            }
        ]
