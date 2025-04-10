"""Repository interfaces defining data access contracts."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.core.domain.models import Task, Project, User


class TaskRepositoryPort(ABC):
    """Interface for task data access."""
    
    @abstractmethod
    def get_all_tasks(self) -> Dict[str, Task]:
        """Get all tasks.
        
        Returns:
            Dictionary of tasks keyed by ID
        """
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Get tasks by completion status.
        
        Args:
            completed: True for completed tasks, False for pending
            
        Returns:
            List of matching tasks
        """
        pass
    
    @abstractmethod
    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Get tasks by project ID.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of tasks for the project
        """
        pass
    
    @abstractmethod
    def get_tasks_by_user(self, user_id: str) -> List[Task]:
        """Get tasks assigned to a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of tasks assigned to the user
        """
        pass
    
    @abstractmethod
    def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """Get tasks within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of tasks within the date range
        """
        pass


class ProjectRepositoryPort(ABC):
    """Interface for project data access."""
    
    @abstractmethod
    def get_all_projects(self) -> Dict[str, Project]:
        """Get all projects.
        
        Returns:
            Dictionary of projects keyed by ID
        """
        pass
    
    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID.
        
        Args:
            project_id: ID of the project to retrieve
            
        Returns:
            Project if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_projects_by_manager(self, manager_id: str) -> List[Project]:
        """Get projects by manager ID.
        
        Args:
            manager_id: ID of the manager
            
        Returns:
            List of projects managed by the manager
        """
        pass


class UserRepositoryPort(ABC):
    """Interface for user data access."""
    
    @abstractmethod
    def get_all_users(self) -> Dict[str, User]:
        """Get all users.
        
        Returns:
            Dictionary of users keyed by ID
        """
        pass
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_users_by_role(self, role: str) -> List[User]:
        """Get users by role.
        
        Args:
            role: User role to filter by
            
        Returns:
            List of users with the specified role
        """
        pass
    
    @abstractmethod
    def get_team_members(self, team_id: str) -> List[User]:
        """Get members of a team.
        
        Args:
            team_id: ID of the team
            
        Returns:
            List of users in the team
        """
        pass