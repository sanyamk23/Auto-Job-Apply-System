"""
Updated UserManager to use PostgreSQL database instead of JSON files.
"""
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.db.session import get_db_context
from src.models.user import User


class UserManager:
    """Manager for user operations using database."""

    def __init__(self):
        # Keep JSON file path for backward compatibility during migration
        self.users_file = 'config/test_users.json'

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from database."""
        try:
            with get_db_context() as db:
                users = db.query(User).filter(User.is_active == True).all()
                return [user.to_dict() for user in users]
        except SQLAlchemyError as e:
            print(f"Database error getting users: {e}")
            # Fallback to JSON file during migration
            return self._load_users_from_json()

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from database."""
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.user_id == user_id, User.is_active == True).first()
                return user.to_dict() if user else None
        except SQLAlchemyError as e:
            print(f"Database error getting user {user_id}: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from database."""
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.email == email, User.is_active == True).first()
                return user.to_dict() if user else None
        except SQLAlchemyError as e:
            print(f"Database error getting user by email {email}: {e}")
            return None

    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Add a new user to database."""
        try:
            with get_db_context() as db:
                # Check if user already exists
                existing = db.query(User).filter(
                    (User.user_id == user_data.get('user_id')) |
                    (User.email == user_data.get('email'))
                ).first()

                if existing:
                    print(f"User already exists: {existing.user_id}")
                    return False

                user = User.create_from_dict(user_data)
                db.add(user)
                db.commit()
                db.refresh(user)
                return True

        except SQLAlchemyError as e:
            print(f"Database error adding user: {e}")
            return False

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Update user in database."""
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    return False

                user.update_from_dict(user_data)
                db.commit()
                return True

        except SQLAlchemyError as e:
            print(f"Database error updating user {user_id}: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """Soft delete user (mark as inactive)."""
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    return False

                user.is_active = False
                db.commit()
                return True

        except SQLAlchemyError as e:
            print(f"Database error deleting user {user_id}: {e}")
            return False

    def migrate_from_json(self) -> int:
        """Migrate users from JSON file to database."""
        json_users = self._load_users_from_json()
        migrated_count = 0

        for user_data in json_users:
            if self.add_user(user_data):
                migrated_count += 1

        print(f"Migrated {migrated_count} users from JSON to database")
        return migrated_count

    def _load_users_from_json(self) -> List[Dict[str, Any]]:
        """Load test users from JSON file (fallback method)."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users from JSON: {e}")
            return []

    def get_test_users(self) -> List[Dict[str, Any]]:
        """Get only test users."""
        try:
            with get_db_context() as db:
                users = db.query(User).filter(User.is_test_user == True, User.is_active == True).all()
                return [user.to_dict() for user in users]
        except SQLAlchemyError as e:
            print(f"Database error getting test users: {e}")
            return []
