from typing import List
from uuid import UUID

class TaskManagerService:
    def breakTaskIntoSubtasks(self, taskId: UUID, subtasks: List[dict]) -> List[dict]:
        pass

    def addSubtask(self, taskId: UUID, subtask: dict) -> dict:
        pass

    def removeSubtask(self, subtaskId: UUID) -> bool:
        pass

    def updateSubtask(self, subtask: dict) -> dict:
        pass

    def assignSubtaskToUser(self, subtaskId: UUID, userId: UUID) -> bool:
        pass

    def markSubtaskAsCompleted(self, subtaskId: UUID) -> bool:
        pass

    def defineDependency(self, subtaskId: UUID, parentSubtaskId: UUID) -> bool:
        pass

    def buildDependencyTree(self, taskId: UUID) -> dict:
        pass

    def getSubtasksByTask(self, taskId: UUID) -> List[dict]:
        pass

    def can_complete_subtask(self, subtask_id):
        """Check if all dependencies are satisfied, subtask cannot be at the milestone which is ahead of the milestone of child subtasks"""
        pass    