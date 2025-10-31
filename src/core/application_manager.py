"""
Updated ApplicationManager to use PostgreSQL database instead of JSON files.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.app_email.email_service import EmailService
from src.core.ai_agent import JobSearchAgent
from src.db.session import get_db_context
from src.models.application import Application
from src.models.user import User
from src.models.job import Job


class ApplicationManager:
    """Manager for job application operations using database."""

    def __init__(self):
        self.ai_agent = JobSearchAgent()
        self.email_service = EmailService()
        # Keep JSON file path for backward compatibility during migration
        self.application_history_file = 'data/application_history.json'

    def apply_to_job(self, job: Dict[str, Any], user_profile: Dict[str, Any]) -> bool:
        """Process job application and store in database."""
        print(f"\n📝 Processing application for {job['title']} at {job['company']}...")

        try:
            with get_db_context() as db:
                # Get or create user
                user = db.query(User).filter(User.user_id == user_profile.get('user_id')).first()
                if not user:
                    # Create user if doesn't exist
                    user = User.create_from_dict(user_profile)
                    db.add(user)
                    db.flush()  # Get user ID

                # Get or create job
                job_obj = db.query(Job).filter(Job.job_id == job.get('id', job.get('job_id'))).first()
                if not job_obj:
                    # Create job if doesn't exist
                    job_obj = Job.create_from_dict(job)
                    db.add(job_obj)
                    db.flush()  # Get job ID

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

                # Create application record
                application_data = {
                    'application_id': f"app_{int(datetime.utcnow().timestamp() * 1000)}",
                    'applicant_name': user_profile.get('name', 'Candidate'),
                    'applicant_email': user_profile.get('email', 'N/A'),
                    'company': job['company'],
                    'position': job['title'],
                    'applied_at': datetime.utcnow().isoformat(),
                    'status': 'Applied',
                    'hr_contact': hr_contact.get('email', 'Not available'),
                    'location': job.get('location', 'Not specified'),
                    'cover_letter_sent': bool(cover_letter),
                    'email_sent': email_sent
                }

                application = Application.create_from_dict(application_data, user.id, job_obj.id)
                db.add(application)

                # Show application summary
                self._show_application_summary(application_data, email_sent)
                return True

        except SQLAlchemyError as e:
            print(f"   ❌ Database error during application: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Application failed: {e}")
            return False

    def _show_application_summary(self, application: Dict, email_sent: bool):
        """Show application summary."""
        print(f"\n✅ APPLICATION SUMMARY:")
        print(f"   👤 Applicant: {application['applicant_name']}")
        print(f"   🏢 Company: {application['company']}")
        print(f"   💼 Position: {application['position']}")
        print(f"   📅 Applied: {application['applied_at'][:16]}")
        print(f"   📧 HR Contact: {application['hr_contact']}")
        print(f"   📮 Email Status: {'Sent' if email_sent else 'Simulated'}")

    def get_application_history(self) -> List[Dict]:
        """Get application history from database."""
        try:
            with get_db_context() as db:
                applications = db.query(Application).order_by(Application.applied_at.desc()).all()
                return [app.to_dict() for app in applications]
        except SQLAlchemyError as e:
            print(f"Database error getting application history: {e}")
            # Fallback to JSON file during migration
            return self._load_application_history_from_json()

    def get_applications_by_user(self, user_id: str) -> List[Dict]:
        """Get applications for a specific user."""
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    return []

                applications = db.query(Application).filter(
                    Application.user_id == user.id
                ).order_by(Application.applied_at.desc()).all()

                return [app.to_dict() for app in applications]
        except SQLAlchemyError as e:
            print(f"Database error getting applications for user {user_id}: {e}")
            return []

    def get_applications_by_job(self, job_id: str) -> List[Dict]:
        """Get applications for a specific job."""
        try:
            with get_db_context() as db:
                job = db.query(Job).filter(Job.job_id == job_id).first()
                if not job:
                    return []

                applications = db.query(Application).filter(
                    Application.job_id == job.id
                ).order_by(Application.applied_at.desc()).all()

                return [app.to_dict() for app in applications]
        except SQLAlchemyError as e:
            print(f"Database error getting applications for job {job_id}: {e}")
            return []

    def update_application_status(self, application_id: str, new_status: str) -> bool:
        """Update application status."""
        try:
            with get_db_context() as db:
                application = db.query(Application).filter(
                    Application.application_id == application_id
                ).first()

                if not application:
                    return False

                application.update_status(new_status)
                return True

        except SQLAlchemyError as e:
            print(f"Database error updating application {application_id}: {e}")
            return False

    def migrate_from_json(self) -> int:
        """Migrate applications from JSON file to database."""
        json_applications = self._load_application_history_from_json()
        migrated_count = 0

        for app_data in json_applications:
            try:
                with get_db_context() as db:
                    # Find or create user
                    user = db.query(User).filter(User.email == app_data.get('applicant_email')).first()
                    if not user:
                        # Create minimal user record
                        user_data = {
                            'user_id': f"migrated_{app_data.get('applicant_email', 'unknown')}",
                            'name': app_data.get('applicant_name', 'Unknown'),
                            'email': app_data.get('applicant_email', 'unknown@example.com'),
                            'is_test_user': False
                        }
                        user = User.create_from_dict(user_data)
                        db.add(user)
                        db.flush()

                    # Find or create job
                    job = db.query(Job).filter(Job.title == app_data.get('position')).first()
                    if not job:
                        # Create minimal job record
                        job_data = {
                            'job_id': f"migrated_job_{migrated_count}",
                            'title': app_data.get('position', 'Unknown Position'),
                            'company': app_data.get('company', 'Unknown Company'),
                            'location': app_data.get('location', 'Remote')
                        }
                        job = Job.create_from_dict(job_data)
                        db.add(job)
                        db.flush()

                    # Create application
                    application = Application.create_from_dict(app_data, user.id, job.id)
                    db.add(application)
                    migrated_count += 1

            except Exception as e:
                print(f"Error migrating application {app_data.get('application_id')}: {e}")
                continue

        print(f"Migrated {migrated_count} applications from JSON to database")
        return migrated_count

    def _load_application_history_from_json(self) -> List[Dict]:
        """Load application history from JSON file (fallback method)."""
        try:
            if os.path.exists(self.application_history_file):
                with open(self.application_history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load application history from JSON: {e}")
        return []
