from typing import List
from uuid import UUID
from ..models.task import Task

class TaskService:
    def createTask(self, task: Task) -> Task:
        pass

    def getTask(self, taskId: UUID) -> Task:
        pass

    def updateTask(self, task: Task) -> Task:
        pass

    def deleteTask(self, taskId: UUID) -> bool:
        pass

    def getTasksByProject(self, projectId: UUID) -> List[Task]:
        pass

    def assignTaskToTeam(self, taskId: UUID, teamId: UUID) -> bool:
        pass