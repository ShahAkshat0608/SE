from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4
from .base_workflow import BaseWorkflow
from ..services.team_service import TeamService
from ..services.task_service import TaskService
from ..services.clients.analytics_client import AnalyticsServiceClient
from ..models.subtask import Subtask
from ..models.role import Role
from ..models.enums import RoleType

class TeamLeadWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.team_service = TeamService()
        self.task_service = TaskService()
        self.analytics_client = AnalyticsServiceClient()
        # We'll need a SubtaskService that isn't fully implemented in the provided code
        from ..database.subtask_dal import SubtaskDAL
        self.subtask_dal = SubtaskDAL()
    
    def create_subtask(self, user_id: str, task_id: str, subtask_data: Dict) -> Dict:
        """Create a subtask for a task (team lead only)"""
        # Get task details to get project_id
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Check user has TEAM_LEAD role in this project
        if not self.role_service.hasTeamLeadAccess(user_id, task.project_id):
            raise PermissionError("Only team leads can create subtasks")
        
        # Create subtask
        subtask = Subtask(
            name=subtask_data['name'],
            task_id=task_id,
            description=subtask_data['description'],
            project_id=task.project_id,
            priority=subtask_data.get('priority', 'MEDIUM'),
            due_date=datetime.fromisoformat(subtask_data['due_date']) if 'due_date' in subtask_data else None,
            milestone_id=subtask_data.get('milestone_id'),
            estimated_hours=subtask_data.get('estimated_hours', 0),
            tags=subtask_data.get('tags', [])
        )
        
        # Add subtask
        self.subtask_dal.add_subtask(subtask)
        return subtask.to_dict()
    
    def add_team_member(self, user_id: str, team_id: str, member_user_id: str) -> bool:
        """Add a member to a team (team lead only)"""
        # Get team details
        team = self.team_service.getTeam(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        # Check if user is team lead for this team
        if team.team_lead_id != user_id and not self.role_service.hasProjectManagerAccess(user_id, team.project_id):
            raise PermissionError("Only team leads or project managers can add team members")
        
        # Add the member
        result = self.team_service.addTeamMember(team_id, member_user_id)
        
        # If successful, also assign TEAM_MEMBER role in the project
        if result:
            try:
                role_id = f"role-{str(uuid4())[:8]}"
                role = Role(
                    id=role_id, 
                    user_id=member_user_id, 
                    project_id=team.project_id, 
                    role=RoleType.TEAM_MEMBER.value
                )
                self.role_service.assignRole(role)
            except ValueError:
                # User may already have a role in this project
                pass
        
        return result
    
    def remove_team_member(self, user_id: str, team_id: str, member_user_id: str) -> bool:
        """Remove a member from a team (team lead only)"""
        # Get team details
        team = self.team_service.getTeam(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        # Check if user is team lead for this team
        if team.team_lead_id != user_id and not self.role_service.hasProjectManagerAccess(user_id, team.project_id):
            raise PermissionError("Only team leads or project managers can remove team members")
        
        # Remove the member
        return self.team_service.removeTeamMember(team_id, member_user_id)
    
    def assign_subtask(self, user_id: str, subtask_id: str, assigned_user_id: str) -> bool:
        """Assign a subtask to a user (team lead only)"""
        # Get subtask details
        subtask = self.subtask_dal.get_subtask(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is team lead for this project
        if not self.role_service.hasTeamLeadAccess(user_id, subtask.project_id):
            raise PermissionError("Only team leads can assign subtasks")
        
        # Update the subtask
        subtask.assigned = True
        subtask.assigned_to = assigned_user_id
        self.subtask_dal.update_subtask(subtask_id, subtask)
        return True
    
    def view_team_analytics(self, user_id: str, team_id: str) -> Dict:
        """View analytics for a team (team lead)"""
        # Get team details
        team = self.team_service.getTeam(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        # Check if user is team lead for this team
        if team.team_lead_id != user_id and not self.role_service.hasProjectManagerAccess(user_id, team.project_id):
            raise PermissionError("Only team leads or project managers can view team analytics")
        
        # Get comprehensive analytics
        return self.analytics_client.get_team_comprehensive(team_id, team.project_id)
        
    
    def update_subtask(self, subtask_id: str, update_data: Dict[str, Any]) -> Optional[Subtask]:
        pass
        
    def delete_subtask(self, subtask_id: str) -> bool:
        pass
    
    def add_dependency(self, subtask_id: str, depends_on_id: str) -> bool:
        pass

    def modify_dependency(self, subtask_id: str, depends_on_id: str) -> bool:
        pass

    def _unassign_user_subtasks(self, user_id: str, team_id: str) -> None:
        pass