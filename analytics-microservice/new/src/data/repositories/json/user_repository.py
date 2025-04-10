"""JSON implementation of user repository."""

import os
from typing import Dict, List, Optional, Any

from src.core.domain.models import User
from src.core.ports.repositories import UserRepositoryPort
from src.data.datasource.json_connector import JsonConnector


class JsonUserRepository(UserRepositoryPort):
    """User repository implementation using JSON files."""
    
    def __init__(self, file_path: str):
        """Initialize the user repository.
        
        Args:
            file_path: Path to the users JSON file
        """
        self.connector = JsonConnector(file_path)
    
    def get_all_users(self) -> Dict[str, User]:
        """Get all users.
        
        Returns:
            Dictionary of users keyed by ID
        """
        raw_data = self.connector.read_data()
        users = {}
        
        for user_id, user_data in raw_data.items():
            try:
                # Add the ID to the user data
                user_data_with_id = {**user_data, 'id': user_id}
                users[user_id] = User.from_dict(user_data_with_id)
            except Exception as e:
                # Skip invalid users but log the error
                import logging
                logging.error(f"Error parsing user {user_id}: {str(e)}")
        
        return users
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User if found, None otherwise
        """
        raw_data = self.connector.read_data()
        
        if user_id not in raw_data:
            return None
        
        # Add the ID to the user data
        user_data = raw_data[user_id]
        user_data_with_id = {**user_data, 'id': user_id}
        return User.from_dict(user_data_with_id)
    
    def get_users_by_role(self, role: str) -> List[User]:
        """Get users by role.
        
        Args:
            role: Role to filter by
            
        Returns:
            List of users with the specified role
        """
        all_users = self.get_all_users()
        return [user for user in all_users.values() 
                if hasattr(user, 'role') and user.role == role]
    
    def get_team_members(self, team_id: str) -> List[User]:
        """Get members of a team.
        
        Args:
            team_id: ID of the team
            
        Returns:
            List of users belonging to the specified team
        """
        all_users = self.get_all_users()
        return [user for user in all_users.values() 
                if hasattr(user, 'teams') and team_id in user.teams]