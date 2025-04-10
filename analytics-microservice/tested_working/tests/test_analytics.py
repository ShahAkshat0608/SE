"""Tests for the TaskAnalytics class."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.analytics import TaskAnalytics


class TestTaskAnalytics(unittest.TestCase):
    """Test cases for TaskAnalytics."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a mock repository
        self.mock_repo = Mock()
        
        # Sample test data with current dates
        now = datetime.now()
        yesterday = (now - timedelta(days=1)).isoformat()
        last_week = (now - timedelta(days=7)).isoformat()
        next_week = (now + timedelta(days=7)).isoformat()
        
        self.test_tasks = {
            "task1": {
                "id": "task1",
                "description": "Test task 1",
                "priority": "high",
                "due_date": next_week,
                "completed": False,
                "created_at": yesterday
            },
            "task2": {
                "id": "task2",
                "description": "Test task 2",
                "priority": "medium",
                "due_date": yesterday,  # Overdue
                "completed": False,
                "created_at": last_week
            },
            "task3": {
                "id": "task3",
                "description": "Test task 3",
                "priority": "low",
                "due_date": last_week,
                "completed": True,
                "created_at": last_week,
                "completed_at": yesterday
            }
        }
        
        # Configure the mock repository
        self.mock_repo.get_all_tasks.return_value = self.test_tasks
        self.mock_repo.get_tasks_by_status.side_effect = lambda completed: [
            {**task, "id": task_id} 
            for task_id, task in self.test_tasks.items() 
            if task.get("completed") == completed
        ]
        
        # Create analytics with mock repository
        self.analytics = TaskAnalytics(self.mock_repo)
    
    def test_get_completion_rate(self):
        """Test calculating completion rate."""
        result = self.analytics.get_completion_rate()
        
        # Verify basic structure
        self.assertIn("total_tasks", result)
        self.assertIn("completed_tasks", result)
        self.assertIn("pending_tasks", result)
        self.assertIn("completion_rate_percentage", result)
        
        # Check values
        self.assertEqual(result["total_tasks"], 3)
        self.assertEqual(result["completed_tasks"], 1)
        self.assertEqual(result["pending_tasks"], 2)
        self.assertEqual(result["completion_rate_percentage"], round((1/3) * 100, 2))
    
    def test_get_pending_work_analysis(self):
        """Test pending work analysis."""
        result = self.analytics.get_pending_work_analysis()
        
        # Verify structure
        self.assertIn("total_pending", result)
        self.assertIn("by_priority", result)
        self.assertIn("overdue_tasks", result)
        self.assertIn("average_days_pending", result)
        
        # Check values
        self.assertEqual(result["total_pending"], 2)
        self.assertEqual(result["by_priority"], {"high": 1, "medium": 1})
        self.assertEqual(result["overdue_tasks"], 1)  # task2 is overdue
    
    def test_get_productivity_metrics(self):
        """Test productivity metrics calculation."""
        result = self.analytics.get_productivity_metrics()
        
        # Verify structure
        self.assertIn("tasks_completed", result)
        self.assertIn("avg_completion_time_hours", result)
        self.assertIn("daily_completion", result)
        self.assertIn("average_daily_completion", result)
        
        # Check values
        self.assertEqual(result["tasks_completed"], 1)
        self.assertGreaterEqual(result["average_daily_completion"], 0)
    
    def test_get_complete_analytics_report(self):
        """Test generating a complete analytics report."""
        result = self.analytics.get_complete_analytics_report()
        
        # Verify structure
        self.assertIn("completion_rate", result)
        self.assertIn("pending_work", result)
        self.assertIn("productivity", result)
        self.assertIn("generated_at", result)


if __name__ == '__main__':
    unittest.main()