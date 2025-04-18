from typing import Dict
from .base_workflow import BaseWorkflow
from ..models.enums import RoleType
from ..services.clients.analytics_client import AnalyticsServiceClient
from ..services.task_manager_service import TaskManagerService

class TeamMemberWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.analytics_client = AnalyticsServiceClient()
        self.task_manager_service = TaskManagerService()
    
    def update_subtask_completion(self, user_id: str, subtask_id: str, is_completed: bool) -> Dict:
        """Update subtask completion status"""
        # Get subtask details
        subtask = self.task_manager_service.getSubtaskbyId(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is assigned to this subtask or is a project manager or team lead
        if not self.role_service.hasProjectManagerAccess(user_id, subtask.project_id) and not self.role_service.hasTeamLeadAccess(user_id, subtask.project_id):
            # Check if user is assigned to this subtask
            if subtask.assigned_to != user_id:
                raise PermissionError("You can only update subtasks assigned to you or if you are a project manager or team lead")
        

        self.task_manager_service.update_subtask_completion(subtask_id, is_completed)
        return subtask.to_dict()
    
    def update_subtask_milestone(self, user_id: str, subtask_id: str, milestone_id: str) -> Dict:
        """Update subtask milestone"""
        # Get subtask details
        subtask = self.task_manager_service.getSubtaskbyId(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is assigned to this subtask or is a project manager or team lead
        if not self.role_service.hasProjectManagerAccess(user_id, subtask.project_id) and not self.role_service.hasTeamLeadAccess(user_id, subtask.project_id):
            # Check if user is assigned to this subtask
            if subtask.assigned_to != user_id:
                raise PermissionError("You can only update subtasks assigned to you or if you are a project manager or team lead")
        
        self.task_manager_service.updateSubtaskMilestone(subtask_id, milestone_id)
        return subtask.to_dict()
    
    def view_user_analytics(self, user_id: str) -> Dict:
        """View analytics for the current user"""
        # No permission check needed as users can view their own analytics
        return self.analytics_client.get_user_comprehensive(user_id)
    
    def get_assigned_subtasks(self, user_id: str) -> Dict:
        """Get all subtasks assigned to the user"""
        return self.task_manager_service.get_assigned_subtasks(user_id)
    