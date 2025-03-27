import json
import os
from task import Task

class TaskDatabase:
    def __init__(self, storage_path="tasks.json"):
        self.storage_path = storage_path
        self.tasks = {}
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from the storage file."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    tasks_data = json.load(f)
                    self.tasks = {
                        task_id: Task.from_dict(task_data)
                        for task_id, task_data in tasks_data.items()
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading tasks: {e}")
                self.tasks = {}
    
    def save_tasks(self):
        """Save tasks to the storage file."""
        tasks_data = {
            task_id: task.to_dict()
            for task_id, task in self.tasks.items()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(tasks_data, f, indent=2)
    
    def add_task(self, task):
        """Add a task to the database."""
        self.tasks[task.id] = task
        self.save_tasks()
        return task
    
    def get_task(self, task_id):
        """Get a task by its ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self):
        """Get all tasks."""
        return list(self.tasks.values())
    
    def update_task(self, task):
        """Update an existing task."""
        if task.id in self.tasks:
            self.tasks[task.id] = task
            self.save_tasks()
            return True
        return False
    
    def delete_task(self, task_id):
        """Delete a task by its ID."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            return True
        return False
    
    