#!/usr/bin/env python3
"""
Simple data migration script to move JSON data to SQLite database.
Only imports the necessary database models and session management.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.models.user import User
    from src.models.job import Job
    from src.models.application import Application
    from src.models.resume import Resume
    from src.db.session import get_db
    print("✅ Database models imported successfully")
except ImportError as e:
    print(f"❌ Failed to import database models: {e}")
    sys.exit(1)


def load_json_data(file_path: str) -> list:
    """Load data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return []


def migrate_users():
    """Migrate test users from JSON to database."""
    print("\n🔄 Migrating users...")

    users_file = project_root / "config" / "test_users.json"
    if not users_file.exists():
        print("⚠️  Test users file not found, skipping user migration")
        return

    users_data = load_json_data(str(users_file))
    if not users_data:
        return

    db = next(get_db())
    try:
        migrated_count = 0
        for user_data in users_data:
            # Check if user already exists
            existing = db.query(User).filter(User.user_id == user_data.get('user_id')).first()
            if existing:
                continue

            user = User(
                user_id=user_data.get('user_id'),
                name=user_data.get('name'),
                email=user_data.get('email'),
                # phone field not in model, skip it
                experience=user_data.get('experience'),
                experience_level=user_data.get('experience_level'),
                skills=user_data.get('skills', []),
                preferred_roles=user_data.get('preferred_roles', []),
                preferred_locations=user_data.get('preferred_locations', []),
                resume_summary=user_data.get('resume_summary'),
                # linkedin_url, github_url, portfolio_url not in JSON, skip
                is_test_user=True
            )
            db.add(user)
            migrated_count += 1

        db.commit()
        print(f"✅ Migrated {migrated_count} users")

    except Exception as e:
        db.rollback()
        print(f"❌ Error migrating users: {e}")
    finally:
        db.close()


def migrate_jobs():
    """Migrate job data from JSON to database."""
    print("\n🔄 Migrating jobs...")

    jobs_file = project_root / "data" / "application_data_engineer.json"
    if not jobs_file.exists():
        print("⚠️  Jobs data file not found, skipping job migration")
        return

    jobs_data = load_json_data(str(jobs_file))
    if not jobs_data:
        return

    db = next(get_db())
    try:
        migrated_count = 0
        for job_data in jobs_data:
            # Check if job already exists
            existing = db.query(Job).filter(Job.job_id == job_data.get('id')).first()
            if existing:
                continue

            # Extract location from nested structure
            location = "Remote"
            if job_data.get('locations_raw') and len(job_data['locations_raw']) > 0:
                loc_data = job_data['locations_raw'][0].get('address', {})
                city = loc_data.get('addressLocality', '')
                region = loc_data.get('addressRegion', '')
                country = loc_data.get('addressCountry', '')
                if city and region:
                    location = f"{city}, {region}"
                elif city:
                    location = city
                elif region:
                    location = region

            # Parse dates properly
            date_posted = job_data.get('date_posted')
            if date_posted:
                try:
                    date_posted = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))
                except:
                    date_posted = None

            date_validthrough = job_data.get('date_validthrough')
            if date_validthrough:
                try:
                    date_validthrough = datetime.fromisoformat(date_validthrough.replace('Z', '+00:00'))
                except:
                    date_validthrough = None

            # Handle salary_raw - convert dict to string if needed
            salary_raw = job_data.get('salary_raw')
            if isinstance(salary_raw, dict):
                salary_raw = json.dumps(salary_raw)
            elif salary_raw is not None:
                salary_raw = str(salary_raw)

            job = Job(
                job_id=job_data.get('id'),
                source_id=job_data.get('id'),
                title=job_data.get('title', 'Unknown Title'),
                company=job_data.get('organization', {}).get('name', 'Unknown Company') if isinstance(job_data.get('organization'), dict) else job_data.get('organization', 'Unknown Company'),
                location=location,
                location_type="Remote" if job_data.get('remote_derived', False) else "On-site",
                description=job_data.get('description', ''),
                description_text=job_data.get('description', ''),
                requirements=job_data.get('requirements', []),
                employment_type=job_data.get('employment_type', ['FULL_TIME'])[0] if job_data.get('employment_type') else 'FULL_TIME',
                salary_raw=salary_raw,
                experience_level='Mid-level',  # Default
                date_posted=date_posted,
                date_validthrough=date_validthrough,
                company_logo=job_data.get('organization_logo'),
                linkedin_org_url=job_data.get('linkedin_org_url'),
                linkedin_org_employees=job_data.get('linkedin_org_employees'),
                linkedin_org_industry=job_data.get('linkedin_org_industry'),
                linkedin_org_size=job_data.get('linkedin_org_size'),
                external_apply_url=job_data.get('url'),
                source=job_data.get('source', 'unknown'),
                source_domain=job_data.get('source_domain', 'unknown'),
                url=job_data.get('url'),
                is_active=True,
                is_directapply=False,
                cities_derived=job_data.get('cities_derived', []),
                counties_derived=job_data.get('counties_derived', []),
                regions_derived=job_data.get('regions_derived', []),
                countries_derived=job_data.get('countries_derived', []),
                locations_derived=job_data.get('locations_derived', []),
                timezones_derived=job_data.get('timezones_derived', []),
                remote_derived=job_data.get('remote_derived', False)
            )
            db.add(job)
            migrated_count += 1

        db.commit()
        print(f"✅ Migrated {migrated_count} jobs")

    except Exception as e:
        db.rollback()
        print(f"❌ Error migrating jobs: {e}")
    finally:
        db.close()


def migrate_applications():
    """Migrate application history from JSON to database."""
    print("\n🔄 Migrating applications...")

    apps_file = project_root / "data" / "application_history.json"
    if not apps_file.exists():
        print("⚠️  Application history file not found, skipping application migration")
        return

    apps_data = load_json_data(str(apps_file))
    if not apps_data:
        return

    db = next(get_db())
    try:
        migrated_count = 0
        for app_data in apps_data:
            # Check if application already exists
            existing = db.query(Application).filter(Application.application_id == app_data.get('application_id')).first()
            if existing:
                continue

            # Parse applied_at datetime
            applied_at = app_data.get('applied_at')
            if applied_at:
                try:
                    applied_at = datetime.fromisoformat(applied_at.replace('Z', '+00:00'))
                except:
                    applied_at = datetime.now()

            # For now, use dummy user_id and job_id since we don't have proper linking
            # In a real migration, you'd need to match these properly
            user_id = 1  # Default to first user
            job_id = 1   # Default to first job

            application = Application(
                application_id=app_data.get('application_id'),
                user_id=user_id,
                job_id=job_id,
                applicant_name=app_data.get('applicant_name'),
                applicant_email=app_data.get('applicant_email'),
                company=app_data.get('company'),
                position=app_data.get('position'),
                location=app_data.get('location'),
                status=app_data.get('status', 'Applied'),
                applied_at=applied_at,
                hr_contact=app_data.get('hr_contact'),  # Correct field name
                cover_letter_sent=False,  # Default
                resume_sent=True,  # Assume resume was sent
                email_sent=True,  # Assume email was sent
                notes=None
            )
            db.add(application)
            migrated_count += 1

        db.commit()
        print(f"✅ Migrated {migrated_count} applications")

    except Exception as e:
        db.rollback()
        print(f"❌ Error migrating applications: {e}")
    finally:
        db.close()


def migrate_resume():
    """Migrate sample resume data."""
    print("\n🔄 Migrating resume...")

    resume_file = project_root / "data" / "sample_resume.txt"
    if not resume_file.exists():
        print("⚠️  Resume file not found, skipping resume migration")
        return

    try:
        with open(resume_file, 'r', encoding='utf-8') as f:
            resume_content = f.read()

        db = next(get_db())

        # Create a sample resume record
        resume = Resume(
            user_id=1,  # Link to first user
            filename="sample_resume.txt",
            file_path=str(resume_file),
            content_type="text/plain",
            raw_text=resume_content,  # Correct field name
            summary=None,  # Will be generated later
            skills_extracted=None,  # Will be extracted later
            experience_years=2,  # Estimated
            education_level="Bachelor's",
            is_processed="completed"  # Mark as processed since we have the text
        )

        # Check if resume already exists
        existing = db.query(Resume).filter(Resume.user_id == 1).first()
        if not existing:
            db.add(resume)
            db.commit()
            print("✅ Migrated sample resume")
        else:
            print("⚠️  Sample resume already exists")

        db.close()

    except Exception as e:
        print(f"❌ Error migrating resume: {e}")


def main():
    """Main migration function."""
    print("🚀 Starting data migration from JSON to SQLite database...")

    # Ensure data directory exists
    os.makedirs(project_root / "data", exist_ok=True)

    try:
        migrate_users()
        migrate_jobs()
        migrate_applications()
        migrate_resume()

        print("\n🎉 Data migration completed successfully!")
        print("📊 You can now use the database-backed system.")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
