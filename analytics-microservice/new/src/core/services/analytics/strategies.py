"""Strategy pattern implementations for different analytics calculations."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from src.core.domain.models import Task, Project, User


class AnalyticsStrategy(ABC):
    """Base strategy interface for analytics calculations."""
    
    @abstractmethod
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate analytics metrics."""
        pass


class TaskCompletionRateStrategy(AnalyticsStrategy):
    """Strategy for calculating task completion rates."""
    
    def calculate(self, tasks: List[Task], time_period_days: int = 30) -> Dict[str, Any]:
        """Calculate the task completion rate over a given time period.
        
        Args:
            tasks: List of tasks to analyze
            time_period_days: Number of days to look back
            
        Returns:
            Dict with completion rate statistics
        """
        # Filter for tasks within the time period
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        
        # Filter and count tasks
        tasks_in_period = [task for task in tasks if task.created_at and task.created_at >= cutoff_date]
        completed_tasks = [task for task in tasks_in_period if task.completed]
        
        total_count = len(tasks_in_period)
        completed_count = len(completed_tasks)
        
        # Calculate stats
        completion_rate = (completed_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "time_period_days": time_period_days,
            "total_tasks": total_count,
            "completed_tasks": completed_count,
            "pending_tasks": total_count - completed_count,
            "completion_rate_percentage": round(completion_rate, 2)
        }


class PendingWorkAnalysisStrategy(AnalyticsStrategy):
    """Strategy for analyzing pending work."""
    
    def calculate(self, tasks: List[Task]) -> Dict[str, Any]:
        """Analyze pending work items.
        
        Args:
            tasks: List of tasks to analyze
            
        Returns:
            Dict with pending work statistics
        """
        # Filter for pending tasks
        pending_tasks = [task for task in tasks if not task.completed]
        
        if not pending_tasks:
            return {
                "total_pending": 0,
                "by_priority": {},
                "overdue_tasks": 0,
                "overdue_percentage": 0,
                "average_days_pending": 0
            }
        
        # Group by priority
        priority_counts = {}
        for task in pending_tasks:
            if task.priority:
                if task.priority not in priority_counts:
                    priority_counts[task.priority] = 0
                priority_counts[task.priority] += 1
        
        # Calculate tasks past due date
        now = datetime.now()
        overdue_tasks = [task for task in pending_tasks 
                        if task.due_date and task.due_date < now]
        
        # Calculate average days pending
        total_days = sum((datetime.now() - task.created_at).days for task in pending_tasks if task.created_at)
        avg_days_pending = total_days / len(pending_tasks) if pending_tasks else 0
        
        overdue_percentage = (len(overdue_tasks) / len(pending_tasks) * 100) if pending_tasks else 0
        
        return {
            "total_pending": len(pending_tasks),
            "by_priority": priority_counts,
            "overdue_tasks": len(overdue_tasks),
            "overdue_percentage": round(overdue_percentage, 2),
            "average_days_pending": round(avg_days_pending, 1)
        }


class ProductivityMetricsStrategy(AnalyticsStrategy):
    """Strategy for calculating productivity metrics."""
    
    def calculate(self, tasks: List[Task], time_period_days: int = 30) -> Dict[str, Any]:
        """Calculate productivity metrics.
        
        Args:
            tasks: List of tasks to analyze
            time_period_days: Number of days to look back
            
        Returns:
            Dict with productivity metrics
        """
        # Filter for completed tasks within time period
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        completed_tasks = [task for task in tasks 
                          if task.completed and task.created_at and task.created_at >= cutoff_date]
        
        if not completed_tasks:
            return {
                "time_period_days": time_period_days,
                "tasks_completed": 0,
                "avg_completion_time_hours": 0,
                "daily_completion": {},
                "weekly_trends": {},
                "average_daily_completion": 0
            }
        
        # Calculate metrics by day
        daily_counts = {}
        for task in completed_tasks:
            if not task.completed_at:
                continue
                
            completed_date = task.completed_at.date()
            date_str = completed_date.isoformat()
            if date_str not in daily_counts:
                daily_counts[date_str] = 0
            daily_counts[date_str] += 1
            
        # Calculate completion time
        completion_times = []
        for task in completed_tasks:
            if not (task.created_at and task.completed_at):
                continue
                
            # Calculate hours to complete
            completion_time = (task.completed_at - task.created_at).total_seconds() / 3600
            completion_times.append(completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Calculate weekly trends
        weekly_counts = {}
        for task in completed_tasks:
            if not task.completed_at:
                continue
                
            completed_date = task.completed_at
            week_num = completed_date.isocalendar()[1]  # ISO week number
            year = completed_date.year
            week_key = f"{year}-W{week_num:02d}"
            if week_key not in weekly_counts:
                weekly_counts[week_key] = 0
            weekly_counts[week_key] += 1
        
        # Calculate average daily completion
        avg_daily = len(completed_tasks) / min(time_period_days, 30)
        
        return {
            "time_period_days": time_period_days,
            "tasks_completed": len(completed_tasks),
            "avg_completion_time_hours": round(avg_completion_time, 2),
            "daily_completion": daily_counts,
            "weekly_trends": weekly_counts,
            "average_daily_completion": round(avg_daily, 2)
        }


class TeamWorkloadStrategy(AnalyticsStrategy):
    """Strategy for analyzing team workload distribution."""
    
    def calculate(self, tasks: List[Task], users: Dict[str, User]) -> Dict[str, Any]:
        """Analyze workload distribution among team members.
        
        Args:
            tasks: List of tasks to analyze
            users: Dict of users keyed by user ID
            
        Returns:
            Dict with workload metrics
        """
        # Group tasks by assigned user
        user_tasks = {}
        for task in tasks:
            if not task.assigned_to:
                continue
                
            user_id = task.assigned_to
            if user_id not in user_tasks:
                user_tasks[user_id] = []
            user_tasks[user_id].append(task)
        
        # Calculate workload metrics for each user
        user_metrics = {}
        for user_id, user_task_list in user_tasks.items():
            # Skip users not in the provided users dict
            if user_id not in users:
                continue
                
            user = users[user_id]
            completed = [t for t in user_task_list if t.completed]
            pending = [t for t in user_task_list if not t.completed]
            
            # Calculate estimated remaining hours
            estimated_remaining_hours = sum(t.estimated_hours or 0 for t in pending)
            
            # Calculate workload percentage based on capacity
            workload_capacity = getattr(user, 'workload_capacity', 40)  # Default to 40 hours if not specified
            workload_percentage = (estimated_remaining_hours / workload_capacity * 100) if workload_capacity > 0 else 0
            
            # Calculate completion rate
            completion_rate = (len(completed) / len(user_task_list) * 100) if user_task_list else 0
            
            user_metrics[user_id] = {
                "name": user.name,
                "role": getattr(user, 'role', 'Unknown'),
                "total_tasks": len(user_task_list),
                "completed_tasks": len(completed),
                "pending_tasks": len(pending),
                "estimated_remaining_hours": estimated_remaining_hours,
                "workload_percentage": round(workload_percentage, 2),
                "completion_rate": round(completion_rate, 2)
            }
        
        # Calculate overall metrics
        total_tasks = sum(len(tasks) for tasks in user_tasks.values())
        total_pending = sum(m["pending_tasks"] for m in user_metrics.values())
        
        # Find most overloaded and underutilized team members
        sorted_by_workload = sorted(
            user_metrics.items(), 
            key=lambda x: x[1]["workload_percentage"], 
            reverse=True
        )
        
        most_overloaded = sorted_by_workload[0][0] if sorted_by_workload else None
        least_loaded = sorted_by_workload[-1][0] if len(sorted_by_workload) > 1 else None
        
        return {
            "total_users": len(user_metrics),
            "total_tasks": total_tasks,
            "total_pending_tasks": total_pending,
            "user_metrics": user_metrics,
            "most_overloaded_user": most_overloaded,
            "least_loaded_user": least_loaded,
            "workload_distribution": {
                user_id: metrics["workload_percentage"] 
                for user_id, metrics in user_metrics.items()
            }
        }


class ProjectProgressStrategy(AnalyticsStrategy):
    """Strategy for analyzing project progress."""
    
    def calculate(self, project: Project, tasks: List[Task]) -> Dict[str, Any]:
        """Analyze project progress.
        
        Args:
            project: The project to analyze
            tasks: List of tasks related to the project
            
        Returns:
            Dict with project progress metrics
        """
        if not tasks:
            return {
                "project_id": project.id,
                "project_name": project.name,
                "total_tasks": 0,
                "completion_percentage": 0,
                "days_remaining": 0,
                "milestone_status": {},
                "on_track": False
            }
        
        # Calculate task completion metrics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.completed)
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate days remaining until target end date
        days_remaining = 0
        on_track = False
        
        if project.target_end_date:
            days_remaining = (project.target_end_date - datetime.now()).days
            
            # Calculate a simple "on track" metric
            # Project is on track if completion percentage >= expected percentage based on timeline
            if project.start_date:
                total_project_days = (project.target_end_date - project.start_date).days
                days_elapsed = (datetime.now() - project.start_date).days
                
                if total_project_days > 0:
                    expected_completion = (days_elapsed / total_project_days * 100)
                    on_track = completion_percentage >= expected_completion
        
        # Calculate milestone status
        milestone_status = {}
        for milestone in project.milestones:
            if not milestone.due_date:
                continue
                
            milestone_status[milestone.id] = {
                "name": milestone.name,
                "completed": milestone.completed,
                "due_date": milestone.due_date.isoformat(),
                "overdue": milestone.due_date < datetime.now() and not milestone.completed
            }
        
        # Collect tasks by priority
        tasks_by_priority = {}
        for task in tasks:
            if task.priority not in tasks_by_priority:
                tasks_by_priority[task.priority] = 0
            tasks_by_priority[task.priority] += 1
        
        return {
            "project_id": project.id,
            "project_name": project.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": total_tasks - completed_tasks,
            "completion_percentage": round(completion_percentage, 2),
            "days_remaining": max(0, days_remaining),
            "milestone_status": milestone_status,
            "on_track": on_track,
            "tasks_by_priority": tasks_by_priority
        }