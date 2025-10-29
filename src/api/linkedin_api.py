import requests
from typing import List, Dict, Any
from config.api_config import APIConfig

class LinkedInAPI:
    def __init__(self):
        self.client_id = APIConfig.LINKEDIN_CLIENT_ID
        self.client_secret = APIConfig.LINKEDIN_CLIENT_SECRET
        self.access_token = None
        # Use RapidAPI LinkedIn Job Search proxy if configured
        self.rapidapi_key = APIConfig.RAPIDAPI_KEY
        # Host and endpoint for RapidAPI LinkedIn job search
        self.rapidapi_host = 'linkedin-job-search-api.p.rapidapi.com'
        self.endpoint = f'https://{self.rapidapi_host}/active-jb-7d'
    
    def is_available(self) -> bool:
        # If a RapidAPI key is present and the jsearch endpoint is configured,
        # we can use RapidAPI as a job source (acts as a LinkedIn proxy).
        if self.rapidapi_key:
            return True

        # Otherwise fall back to checking LinkedIn client credentials (not implemented)
        return bool(self.client_id and self.client_secret)

    def _format_salary(self, salary_raw: Dict) -> str:
        """Format salary information from salary_raw field"""
        if not salary_raw:
            return "Not specified"
            
        try:
            value = salary_raw.get('value', {})
            if not value:
                return "Not specified"
                
            currency = salary_raw.get('currency', 'USD')
            min_value = value.get('minValue')
            max_value = value.get('maxValue')
            unit = value.get('unitText', 'YEAR')
            
            if min_value and max_value:
                if unit == 'HOUR':
                    # Convert hourly to yearly (approximate)
                    min_yearly = min_value * 40 * 52
                    max_yearly = max_value * 40 * 52
                    return f"{currency} {min_yearly:,.0f} - {max_yearly:,.0f} /year (est. from hourly)"
                else:
                    return f"{currency} {min_value:,.0f} - {max_value:,.0f} /year"
            elif min_value:
                return f"{currency} {min_value:,.0f}+ /year"
            elif max_value:
                return f"Up to {currency} {max_value:,.0f} /year"
                
        except Exception as e:
            print(f"Error formatting salary: {e}")
            
        return "Not specified"
    
    def search_jobs(self, query: str, location: str = None, skills: List[str] = None) -> List[Dict[str, Any]]:
        """Search jobs using LinkedIn API (simulated for demo)"""
        # Prefer RapidAPI job search if available (acts as LinkedIn job source)
        if self.rapidapi_key:
            try:
                headers = {
                    'x-rapidapi-host': self.rapidapi_host,
                    'x-rapidapi-key': self.rapidapi_key
                }

                # Build filters to match the exact cURL request format
                params = {
                    'limit': 10,
                    'offset': 0,
                    'title_filter': f'"{query}"',
                    'location_filter': '"United States" OR "United Kingdom"' if not location else f'"{location}"',
                    'description_type': 'text'
                }

                resp = requests.get(self.endpoint, headers=headers, params=params, timeout=10)
                if resp.status_code != 200:
                    print(f"RapidAPI job search error: {resp.status_code}")
                    return []

                data = resp.json()
                # The API returns a list of jobs directly
                jobs_raw = data if isinstance(data, list) else []
                jobs = []
                
                for item in jobs_raw:
                    # Extract location from the locations_raw field
                    location_info = item.get('locations_raw', [{}])[0]
                    address = location_info.get('address', {})
                    location_parts = [
                        address.get('addressLocality'),
                        address.get('addressRegion'),
                        address.get('addressCountry')
                    ]
                    location_field = ", ".join([p for p in location_parts if p])

                    # Map the response fields exactly as they come from the API
                    jobs.append({
                        'id': item.get('id'),
                        'title': item.get('title'),
                        'company': item.get('organization'),
                        'location': location_field,
                        'description': item.get('description_text'),
                        'requirements': [],  # Will be extracted from description_text
                        'salary_range': self._format_salary(item.get('salary_raw')),
                        'hr_contact': {'email': '', 'name': 'See listing'},
                        'url': item.get('url'),
                        'source': 'linkedin',
                        'date_posted': item.get('date_posted'),
                        'employment_type': item.get('employment_type', []),
                        'organization_details': {
                            'logo_url': item.get('organization_logo'),
                            'company_size': item.get('linkedin_org_size'),
                            'industry': item.get('linkedin_org_industry'),
                            'company_type': item.get('linkedin_org_type'),
                            'founded': item.get('linkedin_org_foundeddate'),
                            'specialties': item.get('linkedin_org_specialties', []),
                            'company_url': item.get('linkedin_org_url')
                        }
                    })

                return jobs
            except Exception as e:
                print(f"RapidAPI LinkedIn proxy search failed: {e}")
                return []

        # If RapidAPI not configured, fall back to simulation
        if not self.is_available():
            return self._get_simulated_linkedin_jobs(query, location)

        # Placeholder for real LinkedIn API implementation (requires OAuth)
        try:
            return []
        except Exception as e:
            print(f"LinkedIn API error: {e}")
            return []
    
    def _get_simulated_linkedin_jobs(self, query: str, location: str = None) -> List[Dict]:
        """Get simulated LinkedIn jobs"""
        simulated_jobs = [
            {
                'id': 'linkedin_1',
                'title': f'Senior {query}',
                'company': 'Tech Company Inc',
                'location': location or 'Remote',
                'description': f'Senior {query} role at established tech company.',
                'requirements': ['Python', 'Cloud', 'Leadership'],
                'salary_range': '$110,000 - $150,000',
                'hr_contact': {'email': 'careers@techcompany.com', 'name': 'LinkedIn Recruiter'},
                'source': 'linkedin'
            },
            {
                'id': 'linkedin_2', 
                'title': f'{query} Specialist',
                'company': 'StartUp Co',
                'location': location or 'San Francisco, CA',
                'description': f'{query} specialist role at fast-growing startup.',
                'requirements': ['JavaScript', 'React', 'Startup Experience'],
                'salary_range': '$90,000 - $120,000',
                'hr_contact': {'email': 'hiring@startupco.com', 'name': 'Talent Acquisition'},
                'source': 'linkedin'
            }
        ]
        
        return simulated_jobs
