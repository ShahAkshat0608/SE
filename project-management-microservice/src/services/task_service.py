from typing import List, Optional
from uuid import UUID
from ..models.task import Task
from ..database.task_dal import TaskDAL

class TaskService:
    def __init__(self, task_dal: TaskDAL = None):
        self.task_dal = task_dal or TaskDAL()

    def createTask(self, task: Task) -> Task:
        """Create a new task."""
        task_dict = task.to_dict()
        self.task_dal.add_task(task_dict)
        return task

    def getTask(self, taskId: UUID) -> Optional[Task]:
        """Fetch a task by its ID."""
        task_data = self.task_dal.get_task(str(taskId))
        if task_data:
            return Task(**task_data)  # Convert dictionary to Task object
        return None

    def updateTask(self, task: Task) -> Optional[Task]:
        """Update an existing task."""
        existing_task = self.getTask(task.id)
        if not existing_task:
            return None  # Task not found
        updated_task_dict = task.dict()
        self.task_dal.update_task(str(task.id), updated_task_dict)
        return task

    def deleteTask(self, taskId: UUID) -> bool:
        """Delete a task by its ID."""
        existing_task = self.getTask(taskId)
        if not existing_task:
            return False  # Task not found
        self.task_dal.delete_task(str(taskId))
        return True

    def getTasksByProject(self, projectId: UUID) -> List[Task]:
        """Fetch all tasks for a specific project."""
        tasks_data = self.task_dal.get_tasks_by_project(str(projectId))
        return [Task(**task_data) for task_data in tasks_data]

    def getTasksByTeam(self, projectId : UUID , teamId: UUID) -> List[Task]:
        """Fetch all tasks for a specific team."""
        tasks_data = self.task_dal.get_tasks_by_team(str(teamId))
        return [Task(**task_data) for task_data in tasks_data]

    def assignTaskToTeam(self, taskId: UUID, teamId: UUID) -> bool:
        """Assign a task to a specific team."""
        task = self.getTask(taskId)
        if not task:
            return False  # Task not found
        task.assigned_team_id = str(teamId)
        self.updateTask(task)
        return True