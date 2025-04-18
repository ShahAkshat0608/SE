from typing import List
from uuid import UUID
from typing import Dict
from ..database.subtask_dal import SubtaskDAL

class TaskManagerService:
    def __init__(self, subtask_dal: SubtaskDAL = None):
        """Initialize the task manager service with a data access layer."""
        self.subtask_dal = subtask_dal or SubtaskDAL()
    
    def getSubtaskbyId(self, subtaskId: UUID) -> dict:
        """Get subtask by ID"""
        subtask = self.subtask_dal.get_subtask(subtaskId)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtaskId} not found")
        return subtask
    
    def updateSubtaskMilestone(self, subtask_id: UUID, milestone_id: UUID) -> dict:
        self.subtask_dal.update_milestone(subtask_id, milestone_id)
    

    def breakTaskIntoSubtasks(self, taskId: UUID, subtasks: List[dict]) -> List[dict]:
        pass

    def addSubtask(self, subtask: dict) -> dict:
        self.subtask_dal.add_subtask(subtask)

    def removeSubtask(self, subtask_id: UUID) -> bool:
        self.subtask_dal.delete_subtask(subtask_id)

    def updateSubtask(self, subtask_id: UUID , subtask: dict) -> dict:
        self.subtask_dal.update_subtask(subtask_id, subtask)

    def assignSubtaskToUser(self, subtask_id: UUID, assigned_user_id: UUID) -> bool:
        self.subtask_dal.assign_subtask(subtask_id, assigned_user_id)

    def update_subtask_completion(self, subtask_id: UUID , is_completed: bool) -> bool:
        self.subtask_dal.markCompleted(subtask_id , is_completed)

    def defineDependency(self, subtaskId: UUID, parentSubtaskId: UUID) -> bool:
        pass

    def buildDependencyTree(self, taskId: UUID) -> dict:
        pass

    def getSubtasksByTask(self, taskId: UUID) -> List[dict]:
        """Get all subtasks for a task"""
        subtasks = self.subtask_dal.get_subtasks_by_task(taskId)
        return [subtask.to_dict() for subtask in subtasks]

    def can_complete_subtask(self, subtask_id):
        """Check if all dependencies are satisfied, subtask cannot be at the milestone which is ahead of the milestone of child subtasks"""
        pass   

    def get_assigned_subtasks(self, user_id: str) -> Dict:
        """Get all subtasks assigned to the user"""
        # Get all subtasks assigned to the user
        subtasks = self.subtask_dal.get_subtasks_by_user(user_id)
        return [subtask.to_dict() for subtask in subtasks]