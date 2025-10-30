import json
from typing import List, Dict, Any

class UserManager:
    def __init__(self):
        self.users_file = 'config/test_users.json'
        self.users = self._load_users()
    
    def _load_users(self) -> List[Dict[str, Any]]:
        """Load test users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
            return []
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all test users"""
        return self.users
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID"""
        for user in self.users:
            if user['user_id'] == user_id:
                return user
        return {}
    
    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Add a new user"""
        try:
            user_data['user_id'] = f"user_{len(self.users) + 1:03d}"
            self.users.append(user_data)
            self._save_users()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    def _save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
