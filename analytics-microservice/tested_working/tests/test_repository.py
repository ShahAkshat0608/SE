"""Tests for the TaskRepository class."""

import json
import os
import tempfile
import unittest

from src.repository import TaskRepository


class TestTaskRepository(unittest.TestCase):
    """Test cases for TaskRepository."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Sample test data
        self.test_tasks = {
            "task1": {
                "id": "task1",
                "description": "Test task 1",
                "priority": "high",
                "due_date": "2023-06-01T00:00:00",
                "completed": False,
                "created_at": "2023-05-01T10:00:00"
            },
            "task2": {
                "id": "task2",
                "description": "Test task 2",
                "priority": "medium",
                "due_date": "2023-05-15T00:00:00",
                "completed": True,
                "created_at": "2023-04-15T14:30:00"
            }
        }
        
        # Write test data to temp file
        with open(self.temp_file_path, 'w') as f:
            json.dump(self.test_tasks, f)
            
        # Create repository with temp file
        self.repo = TaskRepository(self.temp_file_path)
    
    def tearDown(self):
        """Clean up after each test."""
        self.temp_file.close()
        os.unlink(self.temp_file_path)
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks."""
        tasks = self.repo.get_all_tasks()
        self.assertEqual(tasks, self.test_tasks)
    
    def test_get_task(self):
        """Test retrieving a specific task."""
        task = self.repo.get_task("task1")
        self.assertEqual(task, self.test_tasks["task1"])
        
        # Test non-existent task
        task = self.repo.get_task("non_existent")
        self.assertIsNone(task)
    
    def test_get_tasks_by_status(self):
        """Test getting tasks filtered by completion status."""
        # Get completed tasks
        completed = self.repo.get_tasks_by_status(completed=True)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0]["id"], "task2")
        
        # Get pending tasks
        pending = self.repo.get_tasks_by_status(completed=False)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["id"], "task1")
    
    def test_handle_empty_file(self):
        """Test handling an empty file."""
        # Create empty file
        empty_file = tempfile.NamedTemporaryFile(delete=False)
        empty_repo = TaskRepository(empty_file.name)
        
        # Should return empty dict, not error
        tasks = empty_repo.get_all_tasks()
        self.assertEqual(tasks, {})
        
        empty_file.close()
        os.unlink(empty_file.name)
    
    def test_handle_nonexistent_file(self):
        """Test handling a non-existent file."""
        non_existent_repo = TaskRepository("nonexistent_file.json")
        tasks = non_existent_repo.get_all_tasks()
        self.assertEqual(tasks, {})


if __name__ == '__main__':
    unittest.main()