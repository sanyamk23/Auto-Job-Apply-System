import json
import os
from datetime import datetime
from typing import List, Dict, Any
from app_email.email_service import EmailService
from core.ai_agent import JobSearchAgent

class ApplicationManager:
    def __init__(self):
        self.ai_agent = JobSearchAgent()
        self.email_service = EmailService()
        self.application_history = []
        self.load_application_history()
    
    def apply_to_job(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> bool:
        """Process job application"""
        print(f"\n📝 Processing application for {job['title']} at {job['company']}...")
        
        try:
            # Generate cover letter
            cover_letter = self.ai_agent.generate_cover_letter(user_profile, job)
            
            # Generate application email
            email_data = self.ai_agent.generate_application_email(user_profile, job, cover_letter)
            
            # Send email if HR contact available
            email_sent = False
            hr_contact = job.get('hr_contact', {})
            
            if hr_contact.get('email'):
                # Include resume attachment if provided in user profile
                attachments = None
                resume_path = user_profile.get('resume_path')
                if resume_path:
                    attachments = [resume_path]

                email_sent = self.email_service.send_application(
                    to_email=hr_contact['email'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    applicant_name=user_profile.get('name', 'Candidate'),
                    attachments=attachments
                )
            else:
                print("   ⚠️  No HR email available - simulating application")
                email_sent = True  # Simulate success for jobs without HR contact
            
            # Record application
            if email_sent:
                application_record = {
                    'application_id': f"app_{len(self.application_history) + 1}",
                    'applicant_name': user_profile.get('name', 'Candidate'),
                    'applicant_email': user_profile.get('email', 'N/A'),
                    'company': job['company'],
                    'position': job['title'],
                    'applied_at': datetime.now().isoformat(),
                    'status': 'Applied',
                    'hr_contact': hr_contact.get('email', 'Not available'),
                    'location': job.get('location', 'Not specified')
                }
                
                self.application_history.append(application_record)
                self.save_application_history()
                
                # Show application summary
                self._show_application_summary(application_record, email_sent)
                return True
            else:
                print("   ❌ Failed to send application email")
                return False
                
        except Exception as e:
            print(f"   ❌ Application failed: {e}")
            return False
    
    def _show_application_summary(self, application: Dict, email_sent: bool):
        """Show application summary"""
        print(f"\n✅ APPLICATION SUMMARY:")
        print(f"   👤 Applicant: {application['applicant_name']}")
        print(f"   🏢 Company: {application['company']}")
        print(f"   💼 Position: {application['position']}")
        print(f"   📅 Applied: {application['applied_at'][:16]}")
        print(f"   📧 HR Contact: {application['hr_contact']}")
        print(f"   📮 Email Status: {'Sent' if email_sent else 'Simulated'}")
    
    def get_application_history(self) -> List[Dict]:
        """Get application history"""
        return self.application_history
    
    def load_application_history(self):
        """Load application history from file"""
        try:
            if os.path.exists('data/application_history.json'):
                with open('data/application_history.json', 'r') as f:
                    self.application_history = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load application history: {e}")
            self.application_history = []
    
    def save_application_history(self):
        """Save application history to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/application_history.json', 'w') as f:
                json.dump(self.application_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save application history: {e}")
