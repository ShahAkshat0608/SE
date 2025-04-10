"""JSON implementation of task repository."""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.core.domain.models import Task
from src.core.ports.repositories import TaskRepositoryPort
from src.data.datasource.json_connector import JsonConnector


class JsonTaskRepository(TaskRepositoryPort):
    """Task repository implementation using JSON files."""
    
    def __init__(self, file_path: str):
        """Initialize the task repository.
        
        Args:
            file_path: Path to the tasks JSON file
        """
        self.connector = JsonConnector(file_path)
    
    def get_all_tasks(self) -> Dict[str, Task]:
        """Get all tasks.
        
        Returns:
            Dictionary of tasks keyed by ID
        """
        raw_data = self.connector.read_data()
        tasks = {}
        
        for task_id, task_data in raw_data.items():
            try:
                # Add the ID to the task data
                task_data_with_id = {**task_data, 'id': task_id}
                tasks[task_id] = Task.from_dict(task_data_with_id)
            except Exception as e:
                # Skip invalid tasks but log the error
                import logging
                logging.error(f"Error parsing task {task_id}: {str(e)}")
        
        return tasks
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task if found, None otherwise
        """
        raw_data = self.connector.read_data()
        
        if task_id not in raw_data:
            return None
        
        # Add the ID to the task data
        task_data = raw_data[task_id]
        task_data_with_id = {**task_data, 'id': task_id}
        return Task.from_dict(task_data_with_id)
    
    def get_tasks_by_status(self, completed: bool = False) -> List[Task]:
        """Get tasks by completion status.
        
        Args:
            completed: True for completed tasks, False for pending tasks
            
        Returns:
            List of tasks with the specified completion status
        """
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks.values() if task.completed == completed]
    
    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Get tasks by project ID.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of tasks belonging to the project
        """
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks.values() 
                if hasattr(task, 'project_id') and task.project_id == project_id]
    
    def get_tasks_by_user(self, user_id: str) -> List[Task]:
        """Get tasks assigned to a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of tasks assigned to the user
        """
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks.values() 
                if hasattr(task, 'assigned_to') and task.assigned_to == user_id]
    
    def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """Get tasks within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of tasks created within the date range
        """
        all_tasks = self.get_all_tasks()
        result = []
        
        for task in all_tasks.values():
            if not task.created_at:
                continue
                
            if start_date <= task.created_at <= end_date:
                result.append(task)
        
        return result