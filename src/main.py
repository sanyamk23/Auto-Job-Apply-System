from dotenv import load_dotenv
from core.ai_agent import JobSearchAgent
from data.user_manager import UserManager
from core.job_search_engine import JobSearchEngine
from core.application_manager import ApplicationManager

class JobRecommendationSystem:
    def __init__(self):
        load_dotenv()
        
        # Initialize components
        self.user_manager = UserManager()
        self.ai_agent = JobSearchAgent()
        self.job_engine = JobSearchEngine()
        self.application_manager = ApplicationManager()
        
        print("🚀 Advanced Job Recommendation System Started!")
        print("=" * 60)
    
    def run(self):
        """Main system loop"""
        while True:
            print("\n🎯 Options:")
            print("1. Use test user profiles")
            print("2. Enter custom user details")
            print("3. View application history")
            print("4. Run demo with all test users")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self.use_test_users()
            elif choice == "2":
                self.use_custom_user()
            elif choice == "3":
                self.view_application_history()
            elif choice == "4":
                self.run_demo()
            elif choice == "5":
                print("Goodbye! 👋")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def use_test_users(self):
        """Use pre-defined test users"""
        users = self.user_manager.get_all_users()
        
        print(f"\n👥 Available Test Users ({len(users)}):")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['name']} - {user['preferred_roles'][0]} ({user['experience_level']})")
        
        try:
            user_choice = int(input(f"\nSelect user (1-{len(users)}): ")) - 1
            if 0 <= user_choice < len(users):
                selected_user = users[user_choice]
                self.process_user_search(selected_user)
            else:
                print("❌ Invalid user selection.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    def use_custom_user(self):
        """Create a custom user profile"""
        print("\n👤 Enter your details:")
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        skills = input("Skills (comma-separated): ").strip().split(',')
        experience = input("Experience (e.g., '2 years'): ").strip()
        preferred_roles = input("Preferred roles (comma-separated): ").strip().split(',')
        
        custom_user = {
            'user_id': f'custom_{len(self.user_manager.get_all_users()) + 1}',
            'name': name,
            'email': email,
            'skills': [s.strip() for s in skills],
            'experience': experience,
            'preferred_roles': [r.strip() for r in preferred_roles],
            'preferred_locations': ['Remote'],  # Default
            'experience_level': 'Mid-level',  # Default
            'resume_summary': f"Custom profile for {name} with skills in {', '.join(skills)}"
        }
        
        self.process_user_search(custom_user)
    
    def process_user_search(self, user_profile):
        """Process job search for a user"""
        print(f"\n🔍 Searching jobs for {user_profile['name']}...")
        print(f"   Skills: {', '.join(user_profile['skills'][:5])}")
        print(f"   Preferred Roles: {', '.join(user_profile['preferred_roles'])}")
        
        # Use AI agent to enhance search strategy
        search_strategy = self.ai_agent.create_search_strategy(user_profile)
        print(f"\n🤖 AI Search Strategy: {search_strategy.get('strategy', 'Standard search')}")
        
        # Search for jobs
        jobs = self.job_engine.search_jobs(
            query=user_profile['preferred_roles'][0],
            location=user_profile['preferred_locations'][0] if user_profile['preferred_locations'] else None,
            skills=user_profile['skills']
        )
        
        print(f"\n✅ Found {len(jobs)} potential jobs")
        
        # Use AI to rank and filter jobs
        ranked_jobs = self.ai_agent.rank_jobs(user_profile, jobs)
        
        # Show top recommendations
        self.show_recommendations(user_profile, ranked_jobs)
    
    def show_recommendations(self, user_profile, ranked_jobs):
        """Show job recommendations and handle applications"""
        print(f"\n🏆 Top Job Recommendations for {user_profile['name']}:")
        print("=" * 70)
        
        for i, job_data in enumerate(ranked_jobs[:5], 1):
            job = job_data['job']
            match_score = job_data['match_score']
            reason = job_data['reason']
            
            print(f"\n{i}. 🏢 {job['title']} at {job['company']}")
            print(f"   📍 Location: {job.get('location', 'Not specified')}")
            print(f"   ⭐ Match Score: {match_score}/10")
            print(f"   💡 Reason: {reason}")
            
            if job.get('hr_contact', {}).get('email'):
                print(f"   📧 HR Email: {job['hr_contact']['email']}")
            
            # Show application options
            apply_choice = input(f"\n   Apply for this position? (y/n/skip): ").lower()
            
            if apply_choice == 'y':
                success = self.application_manager.apply_to_job(job, user_profile)
                if success:
                    print("   ✅ Application processed successfully!")
                else:
                    print("   ❌ Application failed.")
            elif apply_choice == 'skip':
                print("   ⏭️  Skipping to next job...")
                continue
            else:
                print("   💤 Job skipped.")
            
            print("-" * 70)
    
    def view_application_history(self):
        """View application history"""
        history = self.application_manager.get_application_history()
        
        if not history:
            print("\n📝 No applications sent yet.")
            return
        
        print(f"\n📋 Application History ({len(history)} applications):")
        print("=" * 60)
        
        for i, app in enumerate(history, 1):
            print(f"{i}. {app['position']} at {app['company']}")
            print(f"   Applicant: {app['applicant_name']}")
            print(f"   Applied: {app['applied_at']}")
            print(f"   Status: {app['status']}")
            print("-" * 40)
    
    def run_demo(self):
        """Run demo with all test users"""
        print("\n🎭 Running Demo with All Test Users...")
        print("=" * 50)
        
        users = self.user_manager.get_all_users()
        
        for user in users:
            print(f"\n👤 Processing: {user['name']}")
            print(f"   Role: {user['preferred_roles'][0]}")
            print(f"   Skills: {', '.join(user['skills'][:3])}...")
            
            # Simulate search and show top match without applying
            jobs = self.job_engine.search_jobs(
                query=user['preferred_roles'][0],
                skills=user['skills']
            )
            
            if jobs:
                ranked_jobs = self.ai_agent.rank_jobs(user, jobs)
                top_job = ranked_jobs[0] if ranked_jobs else None
                
                if top_job:
                    job = top_job['job']
                    print(f"   🏆 Top Match: {job['title']} at {job['company']}")
                    print(f"   📍 Location: {job.get('location', 'Remote')}")
                    print(f"   ⭐ Score: {top_job['match_score']}/10")
            
            print("-" * 50)

def main():
    try:
        system = JobRecommendationSystem()
        system.run()
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        print("💡 Make sure you have set up your .env file with API keys")

if __name__ == "__main__":
    main()
