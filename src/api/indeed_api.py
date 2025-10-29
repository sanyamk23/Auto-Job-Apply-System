import requests
from typing import List, Dict, Any
from config.api_config import APIConfig

class IndeedAPI:
    def __init__(self):
        self.api_key = APIConfig.INDEED_API_KEY
        self.publisher_id = APIConfig.INDEED_PUBLISHER_ID
        self.base_url = APIConfig.INDEED_BASE_URL
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.publisher_id)
    
    def search_jobs(self, query: str, location: str = None, skills: List[str] = None) -> List[Dict[str, Any]]:
        """Search jobs using Indeed API"""
        if not self.is_available():
            return []
        
        params = {
            'publisher': self.publisher_id,
            'q': query,
            'l': location or '',
            'sort': 'date',
            'format': 'json',
            'v': '2',
            'limit': 10
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_jobs(data.get('results', []))
            else:
                print(f"Indeed API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Indeed API request failed: {e}")
            return []
    
    def _parse_jobs(self, raw_jobs: List[Dict]) -> List[Dict[str, Any]]:
        """Parse Indeed API response"""
        jobs = []
        
        for job in raw_jobs:
            parsed_job = {
                'id': f"indeed_{job.get('jobkey')}",
                'title': job.get('jobtitle', ''),
                'company': job.get('company', ''),
                'location': job.get('formattedLocation', ''),
                'description': job.get('snippet', ''),
                'requirements': [],  # Indeed doesn't provide structured requirements
                'salary_range': job.get('formattedRelativeTime', ''),
                'hr_contact': {'email': '', 'name': 'HR Department'},  # Not available in free API
                'url': job.get('url', ''),
                'source': 'indeed'
            }
            jobs.append(parsed_job)
        
        return jobs
