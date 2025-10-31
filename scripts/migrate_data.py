#!/usr/bin/env python3
"""
Data migration script to move from JSON files to PostgreSQL database.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.db.session import init_database
from src.data.user_manager import UserManager
from src.core.application_manager import ApplicationManager


def main():
    """Run data migration."""
    print("🚀 Starting database migration from JSON to PostgreSQL...")

    try:
        # Initialize database tables
        print("📋 Creating database tables...")
        init_database()
        print("✅ Database tables created successfully")

        # Migrate users
        print("\n👥 Migrating users...")
        user_manager = UserManager()
        users_migrated = user_manager.migrate_from_json()
        print(f"✅ Migrated {users_migrated} users")

        # Migrate applications
        print("\n📝 Migrating applications...")
        app_manager = ApplicationManager()
        apps_migrated = app_manager.migrate_from_json()
        print(f"✅ Migrated {apps_migrated} applications")

        print("\n🎉 Migration completed successfully!")
        print(f"Total records migrated: {users_migrated + apps_migrated}")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
