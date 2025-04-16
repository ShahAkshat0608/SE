from typing import Dict
from .base_workflow import BaseWorkflow
from ..models.enums import RoleType
from ..services.clients.analytics_client import AnalyticsServiceClient

class TeamMemberWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.analytics_client = AnalyticsServiceClient()
        # We'll need a SubtaskService
        from ..database.subtask_dal import SubtaskDAL
        self.subtask_dal = SubtaskDAL()
    
    def update_subtask_completion(self, user_id: str, subtask_id: str, is_completed: bool) -> Dict:
        """Update subtask completion status"""
        # Get subtask details
        subtask = self.subtask_dal.get_subtask(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is assigned to this subtask
        if subtask.assigned_to != user_id:
            raise PermissionError("You can only update subtasks assigned to you")
        
        # Update the subtask
        subtask.is_completed = is_completed
        self.subtask_dal.update_subtask(subtask_id, subtask)
        return subtask.to_dict()
    
    def update_subtask_milestone(self, user_id: str, subtask_id: str, milestone_id: str) -> Dict:
        """Update subtask milestone"""
        # Get subtask details
        subtask = self.subtask_dal.get_subtask(subtask_id)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtask_id} not found")
        
        # Check if user is assigned to this subtask
        if subtask.assigned_to != user_id:
            raise PermissionError("You can only update subtasks assigned to you")
        
        # Update the subtask
        subtask.milestone_id = milestone_id
        self.subtask_dal.update_subtask(subtask_id, subtask)
        return subtask.to_dict()
    
    def view_user_analytics(self, user_id: str) -> Dict:
        """View analytics for the current user"""
        # No permission check needed as users can view their own analytics
        return self.analytics_client.get_user_comprehensive(user_id)
        pass
    