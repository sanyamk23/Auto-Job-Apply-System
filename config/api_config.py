import os
from dotenv import load_dotenv

load_dotenv()

class APIConfig:
    # Google AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Indeed API
    INDEED_API_KEY = os.getenv('INDEED_API_KEY')
    INDEED_PUBLISHER_ID = os.getenv('INDEED_PUBLISHER_ID')
    INDEED_BASE_URL = "http://api.indeed.com/ads/apisearch"
    
    # LinkedIn API (Note: LinkedIn API access is restricted)
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
    LINKEDIN_BASE_URL = "https://api.linkedin.com/v2"
    
    # Google Custom Search API (for job search fallback)
    GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
    GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    
    # RapidAPI endpoints (alternative job APIs)
    JOB_SEARCH_API_URL = "https://jsearch.p.rapidapi.com/search"
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'd57fdc85ecmsh08ed9f3309fd20cp188d19jsn511a0e593848')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    @classmethod
    def validate_config(cls):
        """Validate that required API keys are present"""
        missing = []
        
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        
        # Warn about missing job API keys but don't fail
        job_apis = []
        if not cls.INDEED_API_KEY:
            job_apis.append("Indeed API")
        if not cls.LINKEDIN_CLIENT_ID:
            job_apis.append("LinkedIn API") 
        if not cls.GOOGLE_SEARCH_API_KEY:
            job_apis.append("Google Search API")
        if not cls.RAPIDAPI_KEY:
            job_apis.append("RapidAPI")
            
        if job_apis:
            print(f"⚠️  Missing job APIs: {', '.join(job_apis)}. Using simulated data.")
        
        if missing:
            raise ValueError(f"Missing required API keys: {', '.join(missing)}")
        
        return True
