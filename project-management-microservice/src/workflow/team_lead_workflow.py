from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4
from .base_workflow import BaseWorkflow
from ..services.team_service import TeamService
from ..services.task_service import TaskService
from ..services.role_service import RoleService
from ..services.task_manager_service import TaskManagerService
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
        self.task_manager_service = TaskManagerService()
    
    def create_subtask(self, user_id: str, task_id: str, subtask_data: Dict) -> Dict:
        """Create a subtask for a task (team lead or Project Manager)"""
        # Get task details to get project_id
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Check user has TEAM_LEAD role in this project
        if not self.role_service.hasTeamLeadAccess(user_id, task.project_id) and not self.role_service.hasProjectManagerAccess(user_id, task.project_id):
            raise PermissionError("Only team leads or Project Managers can create subtasks")
        
        # Create subtask
        subtask = Subtask(
            name=subtask_data['name'],
            task_id=task_id,
            description=subtask_data['description'],
            project_id=task.project_id,
            priority=subtask_data.get('priority', 'MEDIUM'),
            due_date=datetime.fromisoformat(subtask_data['due_date']) if 'due_date' in subtask_data else None,
            milestone_id=subtask_data.get('milestone_id' , None),
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
            return {"success": True}
        else:
            # If adding the member failed, we should not assign a role
            return {"success": False , "message": "Team member could not be added"}
        
        
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
        if not self.role_service.hasTeamLeadAccess(user_id, subtask.project_id) and not self.role_service.hasProjectManagerAccess(user_id, subtask.project_id):
            raise PermissionError("Only team leads and project managers can assign subtasks")
        
        # Update the subtask
        self.subtask_dal.assign_subtask(subtask_id, assigned_user_id)
        return {"success": True}
    
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
    
    def get_task_details(self, task_id: str) -> Dict:
        """Get task details (team lead or project manager)"""
        # Get task details
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        return task.to_dict()

    def get_subtasks_details(self, task_id: str) -> Dict:
        """Get all subtasks for a task (team lead or project manager)"""
        # Get task details
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Get all subtasks for the task
        subtasks = self.subtask_dal.get_subtasks_by_task(task_id)
        return [subtask.to_dict() for subtask in subtasks]
    
    def update_subtask(self, user_id : str , subtask_id: str, update_data: Dict[str, Any]) -> Optional[Subtask]:
        """Update a subtask (team lead or project manager)"""
        # Get subtask details
        subtask = self.subtask_dal.get_subtask(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        # Check if user is team lead for this project
        if not self.role_service.hasTeamLeadAccess(user_id, subtask.project_id) and not self.role_service.hasProjectManagerAccess(user_id, subtask.project_id):
            raise PermissionError("Only team leads or project managers can update subtasks")
        
        # Update the subtask and check if the fields are present in the update_data and are not None
        if 'task_id' in update_data and update_data['task_id'] is not None:
            subtask.task_id = update_data['task_id']
        if 'name' in update_data and update_data['name'] is not None:
            subtask.name = update_data['name']
        if 'description' in update_data and update_data['description'] is not None:
            subtask.description = update_data['description']
        if 'priority' in update_data and update_data['priority'] is not None:
            subtask.priority = update_data['priority']
        if 'due_date' in update_data and update_data['due_date'] is not None:
            subtask.due_date = datetime.fromisoformat(update_data['due_date'])
        if 'is_completed' in update_data and update_data['is_completed'] is not None:
            subtask.is_completed = update_data['is_completed']
        
        # Update the subtask in the database
        self.subtask_dal.update_subtask(subtask_id, subtask)
        return subtask.to_dict()
        
    def delete_subtask(self, user_id , subtask_id: str) -> bool:
        """Delete a subtask (team lead or project manager)"""
        # Get subtask details
        subtask = self.subtask_dal.get_subtask(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is team lead for this project
        if not self.role_service.hasTeamLeadAccess(user_id, subtask.project_id) and not self.role_service.hasProjectManagerAccess(user_id, subtask.project_id):
            raise PermissionError("Only team leads or project managers can delete subtasks")
        
        # Delete the subtask
        self.subtask_dal.delete_subtask(subtask_id)
        return {"success": True}
    
    def add_dependency(self, subtask_id: str, depends_on_id: str) -> bool:
        pass

    def modify_dependency(self, subtask_id: str, depends_on_id: str) -> bool:
        pass

    def _unassign_user_subtasks(self, user_id: str, team_id: str) -> None:
        pass