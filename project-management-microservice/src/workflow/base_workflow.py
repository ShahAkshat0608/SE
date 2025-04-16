from ..services.role_service import RoleService
from ..models.enums import RoleType
from typing import List, Dict, Any, Optional

class BaseWorkflow:
    def __init__(self):
        self.role_service = RoleService()
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects where user has a role"""
        # Get all roles for the user
        user_roles = self.role_service.getUserRoles(user_id)
        
        # Extract unique project IDs
        project_ids = set(role.project_id for role in user_roles)
        
        # Fetch project details
        from ..services.project_service import ProjectService
        project_service = ProjectService()
        
        projects = []
        for project_id in project_ids:
            try:
                project = project_service.getProject(project_id)
                projects.append({
                    "id": project.id,
                    "name": project.name,
                    "role": next(role.role for role in user_roles if role.project_id == project_id)
                })
            except ValueError:
                # Project may have been deleted
                continue
        
        return projects
    
    def get_user_role_in_project(self, user_id: str, project_id: str) -> Optional[str]:
        """Get a user's role in a specific project"""
        role = self.role_service.role_dal.get_role_by_user_and_project(user_id, project_id)
        return role.role if role else None