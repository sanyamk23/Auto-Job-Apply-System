import json
import re
from typing import Any, Dict

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text response"""
    try:
        return json.loads(text)
    except:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
    return {}

def safe_json_parse(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except:
        return default

def validate_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def format_salary_range(salary: str) -> str:
    """Format salary range for display"""
    if not salary or salary == 'Not specified':
        return '💵 Salary: Not specified'
    return f'💵 Salary: {salary}'

def format_application_status(status: str) -> str:
    """Format application status with emoji"""
    status_emojis = {
        'applied': '📝',
        'interview': '🎯', 
        'rejected': '❌',
        'offer': '✅',
        'accepted': '🎉'
    }
    emoji = status_emojis.get(status.lower(), '📄')
    return f'{emoji} {status.title()}'
