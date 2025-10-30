import json
import google.generativeai as genai
from typing import List, Dict, Any
from config.api_config import APIConfig
from src.api.linkedin_api import LinkedInAPI

class JobSearchAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        genai.configure(api_key=APIConfig.GEMINI_API_KEY)
    
    def create_search_strategy(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create an AI-powered job search strategy"""
        prompt = f"""
        Create a targeted job search strategy for this candidate:
        
        Candidate Profile:
        - Name: {user_profile.get('name', 'N/A')}
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Experience: {user_profile.get('experience', 'N/A')}
        - Preferred Roles: {', '.join(user_profile.get('preferred_roles', []))}
        - Experience Level: {user_profile.get('experience_level', 'N/A')}
        - Preferred Industries: {', '.join(user_profile.get('preferred_industries', []))}
        
        Provide a JSON response with:
        1. strategy: Overall search approach
        2. keywords: List of search keywords
        3. job_titles: List of specific job titles to search for
        4. companies: List of target companies (if any)
        5. search_tips: Specific tips for this candidate
        
        Return ONLY valid JSON:
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_str = self._extract_json(response.text)
            return json.loads(json_str)
        except Exception as e:
            print(f"AI strategy creation failed: {e}")
            return self._default_search_strategy(user_profile)
    
    def rank_jobs(self, user_profile: Dict[str, Any], jobs: List[Dict]) -> List[Dict]:
        """Rank jobs based on user profile using AI"""
        if not jobs:
            return []
        
        # Limit jobs for token efficiency
        jobs_sample = jobs[:10]
        
        prompt = f"""
        Rank these jobs for the candidate based on suitability (1-10 score).
        
        Candidate Profile:
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Experience: {user_profile.get('experience', 'N/A')}
        - Preferred Roles: {', '.join(user_profile.get('preferred_roles', []))}
        - Experience Level: {user_profile.get('experience_level', 'N/A')}
        
        Jobs to Rank:
        {json.dumps(jobs_sample, indent=2)}
        
        For each job, provide:
        - match_score: 1-10 based on fit
        - reason: Brief explanation of match
        
        Return JSON format:
        {{
            "ranked_jobs": [
                {{
                    "job_id": "job_id",
                    "match_score": 8,
                    "reason": "Explanation"
                }}
            ]
        }}
        
        Return ONLY valid JSON:
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_str = self._extract_json(response.text)
            result = json.loads(json_str)
            
            # Map back to original job objects
            ranked_jobs = []
            for ranked_job in result.get('ranked_jobs', []):
                original_job = next((j for j in jobs_sample if j.get('id') == ranked_job.get('job_id')), None)
                if original_job:
                    ranked_jobs.append({
                        'job': original_job,
                        'match_score': ranked_job.get('match_score', 5),
                        'reason': ranked_job.get('reason', 'Good match based on skills')
                    })
            
            # Sort by match score
            ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)
            return ranked_jobs
            
        except Exception as e:
            print(f"AI job ranking failed: {e}")
            return self._default_ranking(jobs)
    
    def generate_cover_letter(self, user_profile: Dict, job: Dict) -> str:
        """Generate personalized cover letter"""
        prompt = f"""
        Generate a professional cover letter for this job application.
        
        Applicant:
        - Name: {user_profile.get('name', 'Candidate')}
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Experience: {user_profile.get('experience', 'N/A')}
        - Education: {', '.join(user_profile.get('education', ['Not specified']))}
        
        Job:
        - Position: {job.get('title', 'N/A')}
        - Company: {job.get('company', 'N/A')}
        - Requirements: {', '.join(job.get('requirements', []))}
        
        Create a compelling, professional cover letter that highlights relevant experience and skills.
        Keep it concise (150-200 words) and tailored to the specific job.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Cover letter generation failed: {e}")
            return self._default_cover_letter(user_profile, job)
    
    def generate_application_email(self, user_profile: Dict, job: Dict, cover_letter: str) -> Dict[str, str]:
        """Generate professional application email"""
        prompt = f"""
        Create a professional job application email with cover letter.
        
        Applicant: {user_profile.get('name', 'Candidate')}
        Position: {job.get('title', 'Position')}
        Company: {job.get('company', 'Company')}
        
        Cover Letter Content:
        {cover_letter}
        
        Create:
        - Subject line: Professional and attention-grabbing
        - Email body: Include cover letter and contact information
        
        Return as JSON:
        {{
            "subject": "Email subject",
            "body": "Email body with cover letter"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_str = self._extract_json(response.text)
            return json.loads(json_str)
        except Exception as e:
            print(f"Email generation failed: {e}")
            return self._default_email(user_profile, job, cover_letter)
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from model response"""
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        return json_match.group() if json_match else text
    
    def _default_search_strategy(self, user_profile: Dict) -> Dict[str, Any]:
        """Default search strategy fallback"""
        return {
            "strategy": "Standard keyword-based search",
            "keywords": user_profile.get('skills', []) + user_profile.get('preferred_roles', []),
            "job_titles": user_profile.get('preferred_roles', []),
            "companies": [],
            "search_tips": ["Focus on skills matching", "Highlight relevant experience"]
        }
    
    def _default_ranking(self, jobs: List[Dict]) -> List[Dict]:
        """Default job ranking fallback"""
        return [{'job': job, 'match_score': 7, 'reason': 'Skills match'} for job in jobs[:5]]
    
    def _default_cover_letter(self, user_profile: Dict, job: Dict) -> str:
        """Default cover letter fallback"""
        return f"""
        Dear Hiring Manager,
        
        I am excited to apply for the {job.get('title', 'position')} role at {job.get('company', 'your company')}. 
        With my background in {', '.join(user_profile.get('skills', ['software development']))} and {user_profile.get('experience', 'professional experience')}, 
        I am confident in my ability to contribute to your team.
        
        My skills align well with your requirements, and I am eager to bring my expertise to this role.
        
        Thank you for considering my application.
        
        Sincerely,
        {user_profile.get('name', 'Candidate')}
        """
    
    def _default_email(self, user_profile: Dict, job: Dict, cover_letter: str) -> Dict[str, str]:
        """Default email fallback"""
        return {
            "subject": f"Application for {job.get('title', 'Position')} - {user_profile.get('name', 'Candidate')}",
            "body": f"""
            Dear Hiring Team,
            
            {cover_letter}
            
            Please find my application attached. I look forward to the opportunity to discuss how I can contribute to {job.get('company', 'your company')}.
            
            Best regards,
            {user_profile.get('name', 'Candidate')}
            {user_profile.get('email', '')}
            {user_profile.get('phone', '')}
            """
        }
