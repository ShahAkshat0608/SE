"""JSON implementation of project repository."""

import os
from typing import Dict, List, Optional, Any

from src.core.domain.models import Project
from src.core.ports.repositories import ProjectRepositoryPort
from src.data.datasource.json_connector import JsonConnector


class JsonProjectRepository(ProjectRepositoryPort):
    """Project repository implementation using JSON files."""
    
    def __init__(self, file_path: str):
        """Initialize the project repository.
        
        Args:
            file_path: Path to the projects JSON file
        """
        self.connector = JsonConnector(file_path)
    
    def get_all_projects(self) -> Dict[str, Project]:
        """Get all projects.
        
        Returns:
            Dictionary of projects keyed by ID
        """
        raw_data = self.connector.read_data()
        projects = {}
        
        for project_id, project_data in raw_data.items():
            try:
                # Add the ID to the project data if not present
                if 'id' not in project_data:
                    project_data['id'] = project_id
                    
                projects[project_id] = Project.from_dict(project_data)
            except Exception as e:
                # Skip invalid projects but log the error
                import logging
                logging.error(f"Error parsing project {project_id}: {str(e)}")
        
        return projects
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID.
        
        Args:
            project_id: ID of the project to retrieve
            
        Returns:
            Project if found, None otherwise
        """
        raw_data = self.connector.read_data()
        
        if project_id not in raw_data:
            return None
        
        # Add the ID to the project data
        project_data = raw_data[project_id]
        if 'id' not in project_data:
            project_data['id'] = project_id
            
        return Project.from_dict(project_data)
    
    def get_projects_by_manager(self, manager_id: str) -> List[Project]:
        """Get projects by manager ID.
        
        Args:
            manager_id: ID of the manager
            
        Returns:
            List of projects managed by the specified user
        """
        all_projects = self.get_all_projects()
        return [project for project in all_projects.values() 
                if project.manager_id == manager_id]
    
    def get_projects_by_team_member(self, user_id: str) -> List[Project]:
        """Get projects by team member.
        
        Args:
            user_id: ID of the team member
            
        Returns:
            List of projects the user is a member of
        """
        all_projects = self.get_all_projects()
        result = []
        
        for project in all_projects.values():
            # Check if user is a team member of this project
            for team_member in project.team_members:
                if team_member.user_id == user_id:
                    result.append(project)
                    break
                        
        return result