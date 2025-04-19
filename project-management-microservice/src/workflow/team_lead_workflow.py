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
import logging

# Configure logger
logger = logging.getLogger(__name__)

class TeamLeadWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.team_service = TeamService()
        self.task_service = TaskService()
        self.analytics_client = AnalyticsServiceClient()
        self.task_manager_service = TaskManagerService()
    
    def create_subtask(self, user_id: str, task_id: str, subtask_data: Dict) -> Dict:
        """Create a subtask for a task (team lead or Project Manager)"""
        # Get task details to get project_id
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        print(f"Task details: {task.to_dict()}")
        # Check user has TEAM_LEAD role in this project
        if not self.role_service.hasTeamLeadAccess(user_id, task.project_id) and not self.role_service.hasProjectManagerAccess(user_id, task.project_id):
            raise PermissionError("Only team leads or Project Managers can create subtasks")
        
        # Handle due_date properly - ensure it's a string before conversion
        due_date = None
        if 'due_date' in subtask_data and subtask_data['due_date'] is not None:
            try:
                if isinstance(subtask_data['due_date'], str):
                    due_date = datetime.fromisoformat(subtask_data['due_date'])
                else:
                    logger.warning(f"due_date is not a string: {type(subtask_data['due_date'])}")
                    # Convert to string if possible, otherwise use None
                    try:
                        due_date = datetime.fromisoformat(str(subtask_data['due_date']))
                    except (ValueError, TypeError):
                        logger.error(f"Could not convert due_date to valid datetime: {subtask_data['due_date']}")
                        due_date = None
            except ValueError as e:
                logger.error(f"Invalid date format for due_date: {subtask_data['due_date']} - {str(e)}")
                due_date = None
        
        # Create subtask
        subtask = Subtask(
            name=subtask_data['name'],
            task_id=task_id,
            description=subtask_data['description'],
            project_id=task.project_id,
            priority=subtask_data.get('priority', 'MEDIUM'),
            due_date=due_date,
            milestone_id=subtask_data.get('milestone_id', None),
            estimated_hours=subtask_data.get('estimated_hours', 0),
            tags=subtask_data.get('tags', [])
        )
        
        # Add subtask
        self.task_manager_service.addSubtask(subtask)
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
        subtask = self.task_manager_service.getSubtaskbyId(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is team lead for this project
        if not self.role_service.hasTeamLeadAccess(user_id, subtask.project_id) and not self.role_service.hasProjectManagerAccess(user_id, subtask.project_id):
            raise PermissionError("Only team leads and project managers can assign subtasks")
        
        # Update the subtask
        self.task_manager_service.assignSubtaskToUser(subtask_id, assigned_user_id)
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
        return self.task_manager_service.getSubtasksByTask(task_id)
    
    def update_subtask(self, user_id : str , subtask_id: str, update_data: Dict[str, Any]) -> Optional[Subtask]:
        """Update a subtask (team lead or project manager)"""
        # Get subtask details
        subtask = self.task_manager_service.getSubtaskbyId(subtask_id)
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
            try:
                if isinstance(update_data['due_date'], str):
                    subtask.due_date = datetime.fromisoformat(update_data['due_date'])
                else:
                    logger.warning(f"due_date is not a string in update: {type(update_data['due_date'])}")
                    # Convert to string if possible, otherwise leave unchanged
                    try:
                        subtask.due_date = datetime.fromisoformat(str(update_data['due_date']))
                    except (ValueError, TypeError):
                        logger.error(f"Could not convert due_date to valid datetime: {update_data['due_date']}")
            except ValueError as e:
                logger.error(f"Invalid date format for due_date in update: {update_data['due_date']} - {str(e)}")
        if 'is_completed' in update_data and update_data['is_completed'] is not None:
            subtask.is_completed = update_data['is_completed']
        
        # Update the subtask in the database
        self.task_manager_service.updateSubtask(subtask_id , subtask)
        return subtask.to_dict()
        
    def delete_subtask(self, user_id , subtask_id: str) -> bool:
        """Delete a subtask (team lead or project manager)"""
        # Get subtask details
        subtask = self.task_manager_service.getSubtaskbyId(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is team lead for this project
        if not self.role_service.hasTeamLeadAccess(user_id, subtask.project_id) and not self.role_service.hasProjectManagerAccess(user_id, subtask.project_id):
            raise PermissionError("Only team leads or project managers can delete subtasks")
        
        # Delete the subtask
        self.task_manager_service.removeSubtask(subtask_id)
        return {"success": True}
    
    def add_dependency(self, user_id: str , task_id:str , subtask_id: str, parent_subtask_id: str) -> bool:
        """Add a dependency to a subtask (team lead or project manager)"""
        # Get task details
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # get parent subtask details
        parent_subtask = self.task_manager_service.getSubtaskbyId(parent_subtask_id) # 
        if not parent_subtask:
            raise ValueError(f"Parent subtask with ID {parent_subtask_id} not found")
        # get subtask details
        subtask = self.task_manager_service.getSubtaskbyId(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is team lead for this project
        if not self.role_service.hasTeamLeadAccess(user_id, task.project_id) and not self.role_service.hasProjectManagerAccess(user_id, task.project_id):
            raise PermissionError("Only team leads or project managers can add dependencies")
        
        # add dependency to the subtask 
        self.task_manager_service.defineDependency(task_id , subtask_id, parent_subtask_id)

        if parent_subtask.assigned_to is not None and subtask.assigned_to is None:
            self.task_manager_service.assignSubtaskToUser(subtask_id, parent_subtask.assigned_to)

        
        return {"success": True}

    def remove_dependency(self, user_id: str , task_id:str , subtask_id: str, parent_subtask_id: str) -> bool:
        """Remove a dependency from a subtask (team lead or project manager)"""
        # Get task details
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Check if user is team lead for this project
        if not self.role_service.hasTeamLeadAccess(user_id, task.project_id) and not self.role_service.hasProjectManagerAccess(user_id, task.project_id):
            raise PermissionError("Only team leads or project managers can remove dependencies")
        
        # remove dependency from the subtask 
        self.task_manager_service.removeDependency(task_id , subtask_id, parent_subtask_id)
        
        return {"success": True}
    
    def get_dependency_tree(self, task_id: str) -> Dict:
        """Get the dependency tree for a task (team lead or project manager)"""
        # Get task details
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Get the dependency tree
        return self.task_manager_service.getDependencyTree(task_id)
    
    def fix_assignments(self, user_id: str, task_id: str) -> None:
        """Fix assignments for all subtasks in a team (team lead only)"""
        # Get task details
        task = self.task_service.getTask(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Check if user is team lead for this project
        if not self.role_service.hasTeamLeadAccess(user_id, task.project_id) and not self.role_service.hasProjectManagerAccess(user_id, task.project_id):
            raise PermissionError("Only team leads or project managers can fix assignments")
        
        # Get the dependency tree
        dependency_tree = self.task_manager_service.getDependencyTree(task_id)
        if not dependency_tree:
            raise ValueError(f"Dependency tree for task {task_id} not found")
        
        dependencies = dependency_tree.dependencies # dictionary of type Dict[str, List[str]]
        for subtask_id, dependent_subtasks in dependencies.items():
            # Get the subtask details
            subtask = self.task_manager_service.getSubtaskbyId(subtask_id)
            if not subtask:
                raise ValueError(f"Subtask with ID {subtask_id} not found")
            
            # Check if the subtask is assigned to a user
            if subtask.assigned_to is not None:
                # if any of the child subtasks are not assigned to a user, assign the subtask to the user
                for dependent_subtask_id in dependent_subtasks:
                    dependent_subtask = self.task_manager_service.getSubtaskbyId(dependent_subtask_id)
                    if not dependent_subtask:
                        raise ValueError(f"Dependent subtask with ID {dependent_subtask_id} not found")
                    
                    # Check if the dependent subtask is assigned to a user
                    if dependent_subtask.assigned_to is None:
                        # Assign the dependent subtask to the user
                        self.task_manager_service.assignSubtaskToUser(dependent_subtask_id, subtask.assigned_to)
        
        return {"success": True}
        
    def modify_dependency(self, subtask_id: str, depends_on_id: str) -> bool:
        pass

    def _unassign_user_subtasks(self, user_id: str, team_id: str) -> None:
        pass