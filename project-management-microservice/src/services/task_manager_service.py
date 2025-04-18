from typing import List
from uuid import UUID
from typing import Dict
from ..database.subtask_dal import SubtaskDAL
from ..models.subtask import Subtask
from ..database.dependency_tree_dal import DependencyTreeDAL
from ..models.dependency_tree import DependencyTree
from ..models.subtask import Subtask

class TaskManagerService:
    def __init__(self, subtask_dal: SubtaskDAL = None):
        """Initialize the task manager service with a data access layer."""
        self.subtask_dal = subtask_dal or SubtaskDAL()
        self.dependency_tree_dal = DependencyTreeDAL()
    
    def initialiseTaskManager(self, taskId: UUID) -> bool:
        """Initialize the task manager for a specific task by creating a new dependency tree."""
        dependency_tree = self.dependency_tree_dal.create_dependency_tree(taskId)
        if not dependency_tree:
            raise ValueError(f"Failed to initialize task manager for task {taskId}")
        return True
    
    def getSubtaskbyId(self, subtaskId: UUID) -> dict:
        """Get subtask by ID"""
        subtask = self.subtask_dal.get_subtask(subtaskId)
        if not subtask:
            raise ValueError(f"Subtask with ID {subtaskId} not found")
        return subtask
    
    def updateSubtaskMilestone(self, subtask_id: UUID, milestone_id: UUID) -> dict:
        self.subtask_dal.update_milestone(subtask_id, milestone_id)
    

    def breakTaskIntoSubtasks(self, taskId: UUID, subtasks: List[dict]) -> List[dict]:
        created_subtasks = []
        for subtask in subtasks:
            subtask['task_id'] = str(taskId)
            subtask_obj = Subtask().from_dict(subtask)
            self.subtask_dal.add_subtask(subtask_obj)
            created_subtasks.append(subtask_obj.to_dict())
        return created_subtasks

    def addSubtask(self, subtask: Subtask) -> dict:
        # add subtask info to the database in subtask table
        self.subtask_dal.add_subtask(subtask)
        print(f"Subtask {subtask.id} added to the database")
        # add subtask to the dependency tree
        dependency_tree = self.dependency_tree_dal.get_dependency_tree(subtask.task_id) 
        if not dependency_tree:
            raise ValueError(f"Dependency tree for task {subtask.task_id} not found")
        print("Recieived dependency tree")
        dependency_tree.add_subtask(subtask.id)
        self.dependency_tree_dal.update_dependency_tree(dependency_tree)

    def removeSubtask(self, subtask_id: UUID) -> bool:
        self.subtask_dal.delete_subtask(subtask_id)

    def updateSubtask(self, subtask_id: UUID , subtask: dict) -> dict:
        self.subtask_dal.update_subtask(subtask_id, subtask)

    def assignSubtaskToUser(self, subtask_id: UUID, assigned_user_id: UUID) -> bool:
        self.subtask_dal.assign_subtask(subtask_id, assigned_user_id)

    def update_subtask_completion(self, subtask_id: UUID , is_completed: bool) -> bool:
        self.subtask_dal.markCompleted(subtask_id , is_completed)

    def defineDependency(self, task_id : str ,subtaskId: str, parentSubtaskId: str) -> bool:
        # get the dependency tree for the task
        dependency_tree = self.dependency_tree_dal.get_dependency_tree(task_id) # we got the dependency tree object
        if not dependency_tree:
            raise ValueError(f"Dependency tree for task {task_id} not found")
        
        # add the dependency to the dependency tree
        dependency_tree.add_dependency(parentSubtaskId, subtaskId)
        # update the dependency tree in the database
        self.dependency_tree_dal.update_dependency_tree(dependency_tree)
        return True
    
    def removeDependency(self, task_id: str, subtaskId: str, parentSubtaskId: str) -> bool:
        # get the dependency tree for the task
        dependency_tree = self.dependency_tree_dal.get_dependency_tree(task_id)
        if not dependency_tree:
            raise ValueError(f"Dependency tree for task {task_id} not found")
        
        # remove the dependency from the dependency tree
        dependency_tree.remove_dependency(parentSubtaskId, subtaskId)
        # update the dependency tree in the database
        self.dependency_tree_dal.update_dependency_tree(dependency_tree)
        return True

    def getDependencyTree(self, taskId: UUID) -> dict:
        """Build the dependency tree for a task"""
        dependency_tree = self.dependency_tree_dal.get_dependency_tree(taskId)
        if not dependency_tree:
            raise ValueError(f"Dependency tree for task {taskId} not found")
        return dependency_tree.to_dict()

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