from typing import Dict, List
from datetime import datetime
from uuid import uuid4
from .base_workflow import BaseWorkflow
from ..models.team import Team
from ..models.milestone import Milestone
from ..models.task import Task
from ..models.role import Role
from ..services.team_service import TeamService
from ..services.milestone_service import MilestoneService
from ..services.task_service import TaskService
from ..services.project_service import ProjectService
from ..services.task_manager_service import TaskManagerService
from ..services.clients.analytics_client import AnalyticsServiceClient
from ..models.enums import RoleType

class ProjectManagerWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.team_service = TeamService()
        self.milestone_service = MilestoneService()
        self.task_service = TaskService()
        self.analytics_client = AnalyticsServiceClient()
        self.project_service =  ProjectService() # Assuming this is set in the base class
        self.task_manager_service = TaskManagerService() # Assuming this is set in the base class
    
    def get_project_details(self, project_id: str) -> Dict:
        """Get just the project details by ID using the project service"""
        project_service = self.project_service
        project = project_service.getProject(project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found.")
        return project.to_dict()
    
    def get_project_details_by_name(self, project_name: str) -> Dict:
        """Get just the project details by name using the project service"""
        project_service = self.project_service
        project = project_service.getProjectByName(project_name)
        if not project:
            raise ValueError(f"Project with name {project_name} not found.")
        return project.to_dict()
    
    def create_milestone(self, user_id: str, project_id: str, milestone_data: Dict) -> Dict:
        """Create a milestone in a project (project manager only)"""
        # Check user has PROJECT_MANAGER role
        if not self.role_service.hasProjectManagerAccess(user_id, project_id):
            raise PermissionError("Only project managers can create milestones")
        
        # Create milestone
        milestone = Milestone(
            name=milestone_data['name'],
            project_id=project_id,
            description=milestone_data.get('description', ''),
            sequence_no=milestone_data['sequence_no'],
            due_date=datetime.fromisoformat(milestone_data['due_date']) if 'due_date' in milestone_data else None
        )
        
        created_milestone = self.milestone_service.createMilestone(milestone)
        return created_milestone.to_dict()

    def get_milestones(self, project_id: str) -> List[Dict]:
        """Get all milestones for a project (any team member only)"""
        # Get milestones
        milestones = self.milestone_service.getMilestonesByProject(project_id)
        return [milestone.to_dict() for milestone in milestones]

    def create_team(self, user_id: str, project_id: str, team_data: Dict) -> Dict:
        """Create a team for a project (project manager only)"""
        # Check user has PROJECT_MANAGER role
        if not self.role_service.hasProjectManagerAccess(user_id, project_id):
            raise PermissionError("Only project managers can create teams")
        
        team_lead_id = team_data['team_lead_id']
        
        # First, ensure team lead has a TEAM_LEAD role
        role_id = f"role-{str(uuid4())[:8]}"
        team_lead_role = Role(
            id=role_id, 
            user_id=team_lead_id, 
            project_id=project_id, 
            role=RoleType.TEAM_LEAD.value
        )
        
        # Create the team
        team = Team(
            name=team_data['name'],
            project_id=project_id,
            team_lead_id=team_lead_id,
            type=team_data.get('type') or 'DEFAULT',
        )
        
        try:
            # Try to assign the role (will fail if user already has a role)
            self.role_service.assignRole(team_lead_role)
        except ValueError:
            # If user already has a role, update it if needed
            existing_role = self.role_service.getRoleInProject(team_lead_id, project_id)
            if existing_role != RoleType.PROJECT_MANAGER.value:  # Don't downgrade PROJECT_MANAGER
                self.role_service.modifyRole(existing_role.id, RoleType.TEAM_LEAD.value)
        
        created_team = self.team_service.createTeam(team)
        return created_team.to_dict()
    
    def get_teams(self, project_id: str) -> List[Dict]:
        """Get all teams for a project (any team member only)"""
        # Get teams
        teams = self.team_service.getTeamsByProject(project_id)
        return [team.to_dict() for team in teams]

    def create_task(self, user_id: str, project_id: str, team_id: str, task_data: Dict) -> Dict:
        """Create a task for a team (project manager only)"""
        # Check user has PROJECT_MANAGER role
        if not self.role_service.hasProjectManagerAccess(user_id, project_id):
            raise PermissionError("Only project managers can create tasks")
        
        # Create task
        task = Task(
            project_id=project_id,
            team_id=team_id,
            name=task_data['name'],
            description=task_data.get('description', ''),
            status=task_data.get('status', 'TO_DO'),
            priority=task_data.get('priority', 'MEDIUM'),
            target_due_date=datetime.fromisoformat(task_data['target_due_date']) if 'target_due_date' in task_data else None,
        )
        
        created_task = self.task_service.createTask(task)
        self.task_manager_service.initialiseTaskManager(created_task.id)
        return created_task.to_dict()
    
    def get_tasks(self, project_id: str) -> List[Dict]:
        """Get all tasks for a project (any team member only)"""
        # Get tasks
        tasks = self.task_service.getTasksByProject(project_id)
        return [task.to_dict() for task in tasks]
    
    def get_tasks_by_team(self, project_id: str, team_id: str) -> List[Dict]:
        """Get all tasks for a specific team in a project (any team member only)"""
        # Get tasks
        tasks = self.task_service.getTasksByProject(project_id)
        return [task.to_dict() for task in tasks if task.team_id == team_id]

    def view_project_analytics(self, user_id: str, project_id: str) -> Dict:
        """View analytics for a project (project manager)"""
        # Check user has PROJECT_MANAGER role
        if not self.role_service.hasProjectManagerAccess(user_id, project_id):
            raise PermissionError("Only project managers can view project analytics")
        
        # Get comprehensive analytics
        return self.analytics_client.get_project_comprehensive(project_id)

    def get_project_roles(self, user_id: str, project_id: str) -> List[Dict]:
        """Get all roles for a project (project manager only)"""
        # Check user has PROJECT_MANAGER role
        if not self.role_service.hasProjectManagerAccess(user_id, project_id):
            raise PermissionError("Only project managers can view project roles")
        
        # Get roles
        roles = self.role_service.getProjectRoles(project_id)
        return [role.to_dict() for role in roles]

    def replace_team_lead(self, user_id: str, project_id: str, team_id: str, new_team_lead_id: str) -> Dict:
        """Replace the team lead of a team (project manager only)"""
        # Check user has PROJECT_MANAGER role
        if not self.role_service.hasProjectManagerAccess(user_id, project_id):
            raise PermissionError("Only project managers can replace team leads")
        
        # Get the team
        team = self.team_service.getTeam(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        if team.project_id != project_id:
            raise ValueError(f"Team with ID {team_id} does not belong to project {project_id}")
        
        old_team_id = team.team_lead_id
        # Update the team lead
        team.team_lead_id = new_team_lead_id
        self.team_service.updateTeam(team)

        # update the role of the new team lead
        role_id = f"role-{str(uuid4())[:8]}"
        new_team_lead_role = Role(
            id=role_id, 
            user_id=new_team_lead_id, 
            project_id=project_id, 
            role=RoleType.TEAM_LEAD.value
        )
        try:
            # Try to assign the role (will fail if user already has a role)
            self.role_service.assignRole(new_team_lead_role)
        except ValueError:
            # If user already has a role, update it if needed
            existing_role = self.role_service.getRoleInProject(new_team_lead_id, project_id)
            if existing_role != RoleType.PROJECT_MANAGER.value:
                self.role_service.modifyRole(existing_role.id, RoleType.TEAM_LEAD.value)

        # update the role of the old team lead
        old_team_lead_role = self.role_service.getRoleInProject(old_team_id, project_id)
        if old_team_lead_role:
            self.role_service.modifyRole(old_team_lead_role.id, RoleType.TEAM_MEMBER.value)
        # Return the updated team
        team = self.team_service.getTeam(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        if team.project_id != project_id:
            raise ValueError(f"Team with ID {team_id} does not belong to project {project_id}")

        return team.to_dict()
    