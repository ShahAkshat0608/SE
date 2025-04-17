from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4
from .base_workflow import BaseWorkflow
from ..services.project_service import ProjectService
from ..services.role_service import RoleService
from ..models.project import Project
from ..models.role import Role
from ..models.enums import ProjectStatus, TaskPriority, RoleType

class UserWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.project_service = ProjectService()
        
    def create_project(self, user_id: str, project_data: Dict, role_type: str = RoleType.PROJECT_MANAGER.value) -> Dict:
        """
        Create a new project and assign role to the creator
        
        Args:
            user_id: The user creating the project
            project_data: Project details
            role_type: Role to assign to creator (default: PROJECT_MANAGER)
            
        Returns:
            Created project details
        """
        # Create the project
        project = Project(
            id=f"project-{str(uuid4())[:8]}",
            name=project_data['name'] if 'name' in project_data else 'sample_project',
            description=project_data.get('description', '') ,
            status=ProjectStatus(project_data.get('status', 'PLANNING')),
            start_date=datetime.fromisoformat(project_data.get('start_date', datetime.now().isoformat())),
            target_end_date=datetime.fromisoformat(project_data['target_end_date']) if 'target_end_date' in project_data else None,
            project_manager_id=project_data.get('project_manager_id', user_id),
            priority=TaskPriority(project_data.get('priority', 'MEDIUM')),
            client=project_data.get('client') if 'client' in project_data else None,
            department=project_data.get('department') if 'department' in project_data else None,
        )
        
        created_project = self.project_service.createProject(project)
        
        # If the creator should have a role, assign it
        if role_type and user_id:
            role_id = f"role-{str(uuid4())[:8]}"
            role = Role(id=role_id, user_id=user_id, project_id=created_project.id, role=role_type)
            self.role_service.assignRole(role)
        
        return created_project.to_dict()
    
    def get_initial_options(self, user_id: str) -> Dict:
        """
        Get the initial options for a user - create project or view existing projects
        
        Returns dict with:
        - has_projects: bool
        - projects: list of projects user has roles in (if any)
        """
        user_projects = self.get_user_projects(user_id)
        
        return {
            "has_projects": len(user_projects) > 0,
            "projects": user_projects
        }