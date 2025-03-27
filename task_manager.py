from storage import TaskDatabase
from task import Task

class TaskManager:
    def __init__(self, storage_path="tasks.json"):
        self.db = TaskDatabase(storage_path)
        
    def add_task(self, description, priority="medium", due_date=None):
        """Add a new task and return confirmation message."""
        task = Task(description=description, priority=priority, due_date=due_date)
        self.db.add_task(task)
        return f"Task added: {task}"
    
    def remove_task(self, task_id):
        """Remove a task by ID and return confirmation message."""
        task = self.db.get_task(task_id)
        if task:
            self.db.delete_task(task_id)
            return f"Task removed: {task}"
        return f"Error: Task with ID '{task_id}' not found"
    
    def get_tasks(self, filter_completed=None, priority=None):
        """Get tasks with optional filtering."""
        tasks = self.db.get_all_tasks()
        
        # Apply filters if specified
        if filter_completed is not None:
            tasks = [t for t in tasks if t.completed == filter_completed]
        
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
            
        # Sort by priority and creation date
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: (priority_order[t.priority], t.created_at))
    
    def get_task(self, task_id):
        """Get a specific task by ID."""
        return self.db.get_task(task_id)
    
    def complete_task(self, task_id):
        """Mark a task as completed."""
        task = self.db.get_task(task_id)
        if task:
            task.complete()
            self.db.update_task(task)
            return f"Task completed: {task}"
        return f"Error: Task with ID '{task_id}' not found"
    
    def uncomplete_task(self, task_id):
        """Mark a task as not completed."""
        task = self.db.get_task(task_id)
        if task:
            task.uncomplete()
            self.db.update_task(task)
            return f"Task marked as not completed: {task}"
        return f"Error: Task with ID '{task_id}' not found"
    
    def update_task(self, task_id, description=None, priority=None, due_date=None):
        """Update a task's details."""
        task = self.db.get_task(task_id)
        if not task:
            return f"Error: Task with ID '{task_id}' not found"
        
        if description:
            task.description = description
        if priority:
            task.priority = priority
        if due_date is not None:  # Allow setting to None
            task.due_date = due_date
            
        self.db.update_task(task)
        return f"Task updated: {task}"
    
    
