"""Data access layer for the analytics microservice."""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

import config


class TaskRepository:
    """Repository for accessing and managing task data."""

    def __init__(self, file_path: Optional[str] = None):
        """Initialize the task repository.
        
        Args:
            file_path: Optional path to the tasks file. If not provided,
                       the path from config will be used.
        """
        self.file_path = file_path or config.TASKS_FILE

    def get_all_tasks(self) -> Dict[str, Any]:
        """Get all tasks from the data store.
        
        Returns:
            Dict containing all tasks.
        
        Raises:
            FileNotFoundError: If the tasks file doesn't exist.
            json.JSONDecodeError: If the tasks file contains invalid JSON.
        """
        try:
            if not os.path.exists(self.file_path):
                return {}
                
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If the file exists but is empty or has invalid JSON, return empty dict
            return {}

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID.
        
        Args:
            task_id: The ID of the task to retrieve.
            
        Returns:
            Task data as a dictionary or None if task doesn't exist.
        """
        tasks = self.get_all_tasks()
        return tasks.get(task_id)

    def get_tasks_by_status(self, completed: bool = False) -> List[Dict[str, Any]]:
        """Get tasks filtered by completion status.
        
        Args:
            completed: True to get completed tasks, False for pending tasks.
            
        Returns:
            List of tasks matching the completion status.
        """
        tasks = self.get_all_tasks()
        return [
            {**task, "id": task_id} 
            for task_id, task in tasks.items() 
            if task.get("completed") == completed
        ]