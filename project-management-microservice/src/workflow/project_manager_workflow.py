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
from ..services.clients.analytics_client import AnalyticsServiceClient
from ..models.enums import RoleType

class ProjectManagerWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.team_service = TeamService()
        self.milestone_service = MilestoneService()
        self.task_service = TaskService()
        self.analytics_client = AnalyticsServiceClient()
    
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
            type=team_data.get('type')
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
        return created_task.to_dict()
    
    def view_project_analytics(self, user_id: str, project_id: str) -> Dict:
        """View analytics for a project (project manager)"""
        # Check user has PROJECT_MANAGER role
        if not self.role_service.hasProjectManagerAccess(user_id, project_id):
            raise PermissionError("Only project managers can view project analytics")
        
        # Get comprehensive analytics
        return self.analytics_client.get_project_comprehensive(project_id)