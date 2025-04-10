"""Core analytics logic for the task management system."""

from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

from repository import TaskRepository
from utils import parse_date, calculate_days_difference, group_by_attribute


class TaskAnalytics:
    """Analytics service for task data."""
    
    def __init__(self, repository: TaskRepository):
        """Initialize the analytics service.
        
        Args:
            repository: The task repository to use for data access.
        """
        self.repository = repository
        
    def get_completion_rate(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Calculate the task completion rate over a given time period.
        
        Args:
            time_period_days: Number of days to look back (default: 30)
            
        Returns:
            Dictionary with completion rate statistics
        """
        # Get all tasks
        tasks = self.repository.get_all_tasks()
        
        # Filter for tasks within the time period
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        
        # Filter and count tasks
        tasks_in_period = []
        completed_count = 0
        
        for task_id, task in tasks.items():
            if "created_at" not in task:
                continue
                
            created_at = parse_date(task["created_at"])
            if created_at >= cutoff_date:
                tasks_in_period.append({**task, "id": task_id})
                if task.get("completed", False):
                    completed_count += 1
        
        total_count = len(tasks_in_period)
        
        # Calculate stats
        completion_rate = (completed_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "time_period_days": time_period_days,
            "total_tasks": total_count,
            "completed_tasks": completed_count,
            "pending_tasks": total_count - completed_count,
            "completion_rate_percentage": round(completion_rate, 2)
        }
    
    def get_pending_work_analysis(self) -> Dict[str, Any]:
        """Analyze pending work items.
        
        Returns:
            Dictionary with pending work statistics
        """
        pending_tasks = self.repository.get_tasks_by_status(completed=False)
        
        # Group by priority
        priority_groups = group_by_attribute(pending_tasks, "priority")
        priority_counts = {k: len(v) for k, v in priority_groups.items()}
        
        # Calculate tasks past due date
        now = datetime.now()
        overdue_tasks = []
        for task in pending_tasks:
            if "due_date" in task:
                due_date = parse_date(task["due_date"])
                if due_date < now:
                    overdue_tasks.append(task)
        
        # Calculate average days pending
        total_days = 0
        for task in pending_tasks:
            if "created_at" in task:
                days = calculate_days_difference(task["created_at"])
                total_days += days
        
        avg_days_pending = total_days / len(pending_tasks) if pending_tasks else 0
        
        return {
            "total_pending": len(pending_tasks),
            "by_priority": priority_counts,
            "overdue_tasks": len(overdue_tasks),
            "overdue_percentage": round((len(overdue_tasks) / len(pending_tasks) * 100) if pending_tasks else 0, 2),
            "average_days_pending": round(avg_days_pending, 1)
        }
    
    def get_productivity_metrics(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Calculate productivity metrics.
        
        Args:
            time_period_days: Number of days to look back (default: 30)
            
        Returns:
            Dictionary with productivity statistics
        """
        # Get all tasks
        tasks = self.repository.get_all_tasks()
        
        # Filter for tasks within the time period
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        completed_tasks = []
        
        for task_id, task in tasks.items():
            if not (task.get("completed", False) and "created_at" in task):
                continue
                
            created_at = parse_date(task["created_at"])
            if created_at >= cutoff_date:
                completed_tasks.append({**task, "id": task_id})
        
        # Calculate metrics by day
        daily_counts = Counter()
        for task in completed_tasks:
            if "completed_at" in task:
                completed_date = parse_date(task["completed_at"]).date()
                daily_counts[str(completed_date)] += 1
            
        # Calculate completion time
        total_completion_time = 0
        tasks_with_completion_time = 0
        
        for task in completed_tasks:
            if "created_at" in task and "completed_at" in task:
                created_at = parse_date(task["created_at"])
                completed_at = parse_date(task["completed_at"])
                completion_time = (completed_at - created_at).total_seconds() / 3600  # hours
                total_completion_time += completion_time
                tasks_with_completion_time += 1
        
        avg_completion_time = round(total_completion_time / tasks_with_completion_time, 2) if tasks_with_completion_time > 0 else 0
        
        # Calculate weekly trends (completed tasks per week)
        weekly_counts = {}
        for task in completed_tasks:
            if "completed_at" in task:
                completed_date = parse_date(task["completed_at"])
                week_num = completed_date.isocalendar()[1]  # ISO week number
                year = completed_date.year
                week_key = f"{year}-W{week_num:02d}"
                if week_key not in weekly_counts:
                    weekly_counts[week_key] = 0
                weekly_counts[week_key] += 1
        
        return {
            "time_period_days": time_period_days,
            "tasks_completed": len(completed_tasks),
            "avg_completion_time_hours": avg_completion_time,
            "daily_completion": dict(daily_counts),
            "weekly_trends": weekly_counts,
            "average_daily_completion": round(len(completed_tasks) / min(time_period_days, 30), 2)
        }

    def get_complete_analytics_report(self) -> Dict[str, Any]:
        """Generate a complete analytics report combining all metrics.
        
        Returns:
            Dictionary with all analytics data
        """
        return {
            "completion_rate": self.get_completion_rate(),
            "pending_work": self.get_pending_work_analysis(),
            "productivity": self.get_productivity_metrics(),
            "generated_at": datetime.now().isoformat()
        }