# import requests
# from typing import List, Dict, Any
# from config.api_config import APIConfig

# class LinkedInAPI:
#     def __init__(self):
#         self.access_token = None
#         # Use RapidAPI LinkedIn Job Search proxy if configured
#         self.rapidapi_key = APIConfig.RAPIDAPI_KEY
#         # Host and endpoint for RapidAPI LinkedIn job search
#         self.rapidapi_host = 'linkedin-job-search-api.p.rapidapi.com'
#         self.endpoint = f'https://{self.rapidapi_host}/active-jb-7d'
    
#     def is_available(self) -> bool:
#         # If a RapidAPI key is present and the jsearch endpoint is configured,
#         # we can use RapidAPI as a job source (acts as a LinkedIn proxy).
#         if self.rapidapi_key:
#             return True

#         # Otherwise fall back to checking LinkedIn client credentials (not implemented)
#         return bool(self.client_id and self.client_secret)

#     def _format_salary(self, salary_raw: Dict) -> str:
#         """Format salary information from salary_raw field"""
#         if not salary_raw:
#             return "Not specified"
            
#         try:
#             value = salary_raw.get('value', {})
#             if not value:
#                 return "Not specified"
                
#             currency = salary_raw.get('currency', 'USD')
#             min_value = value.get('minValue')
#             max_value = value.get('maxValue')
#             unit = value.get('unitText', 'YEAR')
            
#             if min_value and max_value:
#                 if unit == 'HOUR':
#                     # Convert hourly to yearly (approximate)
#                     min_yearly = min_value * 40 * 52
#                     max_yearly = max_value * 40 * 52
#                     return f"{currency} {min_yearly:,.0f} - {max_yearly:,.0f} /year (est. from hourly)"
#                 else:
#                     return f"{currency} {min_value:,.0f} - {max_value:,.0f} /year"
#             elif min_value:
#                 return f"{currency} {min_value:,.0f}+ /year"
#             elif max_value:
#                 return f"Up to {currency} {max_value:,.0f} /year"
                
#         except Exception as e:
#             print(f"Error formatting salary: {e}")
            
#         return "Not specified"
    
#     def search_jobs(self, query: str, location: str = None, skills: List[str] = None) -> List[Dict[str, Any]]:
#         """Search jobs using LinkedIn API (simulated for demo)"""
#         # Prefer RapidAPI job search if available (acts as LinkedIn job source)
#         if self.rapidapi_key:
#             try:
#                 headers = {
#                     'x-rapidapi-host': self.rapidapi_host,
#                     'x-rapidapi-key': self.rapidapi_key
#                 }

#                 # Build filters to match the exact cURL request format
#                 params = {
#                     'limit': 10,
#                     'offset': 0,
#                     'title_filter': f'"{query}"',
#                     'location_filter': '"United States" OR "United Kingdom"' if not location else f'"{location}"',
#                     'description_type': 'text'
#                 }

#                 resp = requests.get(self.endpoint, headers=headers, params=params, timeout=10)
#                 if resp.status_code != 200:
#                     print(f"RapidAPI job search error: {resp.status_code}")
#                     return []

#                 data = resp.json()
#                 # The API returns a list of jobs directly
#                 jobs_raw = data if isinstance(data, list) else []
#                 jobs = []
                
#                 for item in jobs_raw:
#                     # Extract location from the locations_raw field
#                     location_info = item.get('locations_raw', [{}])[0]
#                     address = location_info.get('address', {})
#                     location_parts = [
#                         address.get('addressLocality'),
#                         address.get('addressRegion'),
#                         address.get('addressCountry')
#                     ]
#                     location_field = ", ".join([p for p in location_parts if p])

#                     # Map the response fields exactly as they come from the API
#                     jobs.append({
#                         'id': item.get('id'),
#                         'title': item.get('title'),
#                         'company': item.get('organization'),
#                         'location': location_field,
#                         'description': item.get('description_text'),
#                         'requirements': [],  # Will be extracted from description_text
#                         'salary_range': self._format_salary(item.get('salary_raw')),
#                         'hr_contact': {'email': '', 'name': 'See listing'},
#                         'url': item.get('url'),
#                         'source': 'linkedin',
#                         'date_posted': item.get('date_posted'),
#                         'employment_type': item.get('employment_type', []),
#                         'organization_details': {
#                             'logo_url': item.get('organization_logo'),
#                             'company_size': item.get('linkedin_org_size'),
#                             'industry': item.get('linkedin_org_industry'),
#                             'company_type': item.get('linkedin_org_type'),
#                             'founded': item.get('linkedin_org_foundeddate'),
#                             'specialties': item.get('linkedin_org_specialties', []),
#                             'company_url': item.get('linkedin_org_url')
#                         }
#                     })

#                 return jobs
#             except Exception as e:
#                 print(f"RapidAPI LinkedIn proxy search failed: {e}")
#                 return []

#         # If RapidAPI not configured, fall back to simulation
#         if not self.is_available():
#             return self._get_simulated_linkedin_jobs(query, location)

#         # Placeholder for real LinkedIn API implementation (requires OAuth)
#         try:
#             return []
#         except Exception as e:
#             print(f"LinkedIn API error: {e}")
#             return []
    
#     def _get_simulated_linkedin_jobs(self, query: str, location: str = None) -> List[Dict]:
#         """Get simulated LinkedIn jobs"""
#         simulated_jobs = [
#             {
#                 'id': 'linkedin_1',
#                 'title': f'Senior {query}',
#                 'company': 'Tech Company Inc',
#                 'location': location or 'Remote',
#                 'description': f'Senior {query} role at established tech company.',
#                 'requirements': ['Python', 'Cloud', 'Leadership'],
#                 'salary_range': '$110,000 - $150,000',
#                 'hr_contact': {'email': 'careers@techcompany.com', 'name': 'LinkedIn Recruiter'},
#                 'source': 'linkedin'
#             },
#             {
#                 'id': 'linkedin_2', 
#                 'title': f'{query} Specialist',
#                 'company': 'StartUp Co',
#                 'location': location or 'San Francisco, CA',
#                 'description': f'{query} specialist role at fast-growing startup.',
#                 'requirements': ['JavaScript', 'React', 'Startup Experience'],
#                 'salary_range': '$90,000 - $120,000',
#                 'hr_contact': {'email': 'hiring@startupco.com', 'name': 'Talent Acquisition'},
#                 'source': 'linkedin'
#             }
#         ]
        
#         return simulated_jobs

import requests
from typing import List, Dict, Any
from config.api_config import APIConfig

class LinkedInAPI:
    def __init__(self):
        self.access_token = None
        # Use RapidAPI LinkedIn Job Search proxy
        self.rapidapi_key = APIConfig.RAPIDAPI_KEY
        # Host and endpoint for RapidAPI LinkedIn job search
        self.rapidapi_host = 'linkedin-job-search-api.p.rapidapi.com'
        self.endpoint = f'https://{self.rapidapi_host}/active-jb-7d'
    
    def is_available(self) -> bool:
        """Check if RapidAPI key is configured"""
        return bool(self.rapidapi_key)
    
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
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract common tech skills from job description"""
        if not description:
            return []
        
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Angular', 'Vue',
            'Node.js', 'Django', 'Flask', 'SQL', 'MongoDB', 'PostgreSQL',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git',
            'Machine Learning', 'AI', 'Data Science', 'DevOps',
            'TypeScript', 'Ruby', 'Go', 'Rust', 'PHP', 'Swift',
            'REST API', 'GraphQL', 'Redis', 'Elasticsearch'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limit to top 10 skills
    
    def search_jobs(self, query: str, location: str = None, skills: List[str] = None) -> List[Dict[str, Any]]:
        """Search jobs using RapidAPI LinkedIn Job Search"""
        
        if not self.is_available():
            print("⚠️  RapidAPI key not configured, returning empty results")
            return []
        
        try:
            headers = {
                'x-rapidapi-host': self.rapidapi_host,
                'x-rapidapi-key': self.rapidapi_key
            }
            
            # Build location filter
            if location:
                # Handle "Remote" as a special case
                if location.lower() == 'remote':
                    location_filter = '"United States" OR "United Kingdom" OR "Remote"'
                else:
                    location_filter = f'"{location}"'
            else:
                location_filter = '"United States" OR "United Kingdom"'
            
            # Build params to match the exact cURL request format
            params = {
                'limit': 20,  # Get more results
                'offset': 0,
                'title_filter': f'"{query}"',
                'location_filter': location_filter,
                'description_type': 'text'
            }
            
            print(f"📡 Making RapidAPI request with params: {params}")
            
            resp = requests.get(self.endpoint, headers=headers, params=params, timeout=15)
            
            if resp.status_code != 200:
                print(f"❌ RapidAPI job search error: {resp.status_code}")
                print(f"Response: {resp.text[:200]}")
                return []
            
            data = resp.json()
            
            # The API returns a list of jobs directly
            jobs_raw = data if isinstance(data, list) else []
            
            if not jobs_raw:
                print("⚠️  No jobs returned from API")
                return []
            
            print(f"✅ Found {len(jobs_raw)} jobs from LinkedIn API")
            
            jobs = []
            
            for item in jobs_raw:
                try:
                    # Extract location from the locations_raw field
                    location_info = item.get('locations_raw', [{}])[0] if item.get('locations_raw') else {}
                    address = location_info.get('address', {})
                    location_parts = [
                        address.get('addressLocality'),
                        address.get('addressRegion'),
                        address.get('addressCountry')
                    ]
                    location_field = ", ".join([p for p in location_parts if p]) or "Location not specified"
                    
                    # Extract skills from description
                    description = item.get('description_text', '')
                    extracted_skills = self._extract_skills_from_description(description)
                    
                    # Format employment type
                    employment_types = item.get('employment_type', [])
                    employment_type_str = ", ".join(employment_types) if employment_types else "Not specified"
                    
                    # Map the response fields
                    job = {
                        'id': item.get('id', f"linkedin_{hash(item.get('title', ''))}"),
                        'title': item.get('title', 'Title not available'),
                        'company': item.get('organization', 'Company not specified'),
                        'location': location_field,
                        'description': description[:500] + "..." if len(description) > 500 else description,  # Truncate long descriptions
                        'full_description': description,
                        'requirements': extracted_skills,
                        'salary_range': self._format_salary(item.get('salary_raw')),
                        'hr_contact': {'email': '', 'name': 'See listing for contact'},
                        'url': item.get('url', ''),
                        'source': 'linkedin',
                        'date_posted': item.get('date_posted', ''),
                        'employment_type': employment_type_str,
                        'organization_details': {
                            'logo_url': item.get('organization_logo'),
                            'company_size': item.get('linkedin_org_size'),
                            'industry': item.get('linkedin_org_industry'),
                            'company_type': item.get('linkedin_org_type'),
                            'founded': item.get('linkedin_org_foundeddate'),
                            'specialties': item.get('linkedin_org_specialties', []),
                            'company_url': item.get('linkedin_org_url')
                        }
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    print(f"⚠️  Error parsing job item: {e}")
                    continue
            
            return jobs
            
        except requests.exceptions.Timeout:
            print("❌ RapidAPI request timed out")
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ RapidAPI request failed: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error in LinkedIn API: {e}")
            return []