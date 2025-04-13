"""Strategy pattern implementations for different analytics calculations."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import calendar

from src.core.domain.models import Task, Project, User


class AnalyticsStrategy(ABC):
    """Abstract base class for analytics strategies."""
    
    @abstractmethod
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Perform analytics calculation."""
        pass


class TaskCompletionRateStrategy(AnalyticsStrategy):
    """Strategy for calculating task completion rate."""
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate task completion rate.
        
        Args:
            tasks: List of tasks
            time_period_days: Number of days to look back
            
        Returns:
            Dict with completion rate statistics
        """
        tasks = kwargs.get('tasks', [])
        time_period_days = kwargs.get('time_period_days', 30)
        
        if not tasks:
            return self._create_empty_result(time_period_days)
            
        # Calculate time period
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        
        # Filter tasks created within time period
        recent_tasks = [t for t in tasks if t.created_at >= cutoff_date]
        
        total_tasks = len(recent_tasks)
        completed_tasks = len([t for t in recent_tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        
        # Calculate completion rate percentage
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "time_period_days": time_period_days,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate_percentage": round(completion_rate, 2)
        }
    
    def _create_empty_result(self, time_period_days: int) -> Dict[str, Any]:
        """Create an empty result structure."""
        return {
            "time_period_days": time_period_days,
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_rate_percentage": 0
        }


class PendingWorkAnalysisStrategy(AnalyticsStrategy):
    """Strategy for analyzing pending work."""
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate pending work metrics.
        
        Args:
            tasks: List of tasks
            
        Returns:
            Dict with pending work metrics
        """
        tasks = kwargs.get('tasks', [])
        
        if not tasks:
            return self._create_empty_result()
            
        # Filter for pending tasks
        pending_tasks = [t for t in tasks if not t.completed]
        total_pending = len(pending_tasks)
        
        if total_pending == 0:
            return self._create_empty_result()
        
        # Group by priority
        by_priority = defaultdict(int)
        for task in pending_tasks:
            by_priority[task.priority] += 1
        
        # Calculate overdue tasks
        now = datetime.now()
        overdue_tasks = [t for t in pending_tasks if t.due_date and t.due_date < now]
        overdue_count = len(overdue_tasks)
        
        # Calculate overdue percentage
        overdue_percentage = (overdue_count / total_pending * 100) if total_pending > 0 else 0
        
        # Calculate average days pending
        days_pending_sum = sum((now - t.created_at).days for t in pending_tasks)
        avg_days_pending = days_pending_sum / total_pending if total_pending > 0 else 0
        
        return {
            "total_pending": total_pending,
            "by_priority": dict(by_priority),
            "overdue_tasks": overdue_count,
            "overdue_percentage": round(overdue_percentage, 2),
            "average_days_pending": round(avg_days_pending, 2)
        }
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create an empty result structure."""
        return {
            "total_pending": 0,
            "by_priority": {},
            "overdue_tasks": 0,
            "overdue_percentage": 0,
            "average_days_pending": 0
        }


class ProductivityMetricsStrategy(AnalyticsStrategy):
    """Strategy for calculating productivity metrics."""
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate productivity metrics.
        
        Args:
            tasks: List of tasks
            time_period_days: Number of days to look back
            
        Returns:
            Dict with productivity metrics
        """
        tasks = kwargs.get('tasks', [])
        time_period_days = kwargs.get('time_period_days', 30)
        
        if not tasks:
            return self._create_empty_result(time_period_days)
            
        # Calculate time period
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        
        # Filter for completed tasks within time period
        completed_tasks = [
            t for t in tasks 
            if t.completed and t.completed_at and t.completed_at >= cutoff_date
        ]
        
        tasks_completed = len(completed_tasks)
        
        if tasks_completed == 0:
            return self._create_empty_result(time_period_days)
        
        # Calculate average completion time
        completion_times = []
        for task in completed_tasks:
            if task.created_at and task.completed_at:
                diff = task.completed_at - task.created_at
                hours = diff.total_seconds() / 3600
                completion_times.append(hours)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Group by day
        daily_completion = defaultdict(int)
        for task in completed_tasks:
            if task.completed_at:
                day_key = task.completed_at.date().isoformat()
                daily_completion[day_key] += 1
        
        # Group by week
        weekly_trends = defaultdict(int)
        for task in completed_tasks:
            if task.completed_at:
                year, week_num, _ = task.completed_at.isocalendar()
                week_key = f"{year}-W{week_num:02d}"
                weekly_trends[week_key] += 1
        
        # Calculate average daily completion
        days_in_period = min(time_period_days, len(daily_completion) or 1)
        avg_daily = tasks_completed / days_in_period
        
        return {
            "time_period_days": time_period_days,
            "tasks_completed": tasks_completed,
            "avg_completion_time_hours": round(avg_completion_time, 2),
            "daily_completion": dict(daily_completion),
            "weekly_trends": dict(weekly_trends),
            "average_daily_completion": round(avg_daily, 2)
        }
    
    def _create_empty_result(self, time_period_days: int) -> Dict[str, Any]:
        """Create an empty result structure."""
        return {
            "time_period_days": time_period_days,
            "tasks_completed": 0,
            "avg_completion_time_hours": 0,
            "daily_completion": {},
            "weekly_trends": {},
            "average_daily_completion": 0
        }


class TeamWorkloadStrategy(AnalyticsStrategy):
    """Strategy for analyzing team workload distribution."""
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate team workload metrics.
        
        Args:
            tasks: List of tasks
            users: Dictionary of users keyed by ID
            
        Returns:
            Dict with team workload metrics
        """
        tasks = kwargs.get('tasks', [])
        users = kwargs.get('users', {})
        
        if not tasks or not users:
            return self._create_empty_result()
            
        result = {
            "total_users": len(users),
            "total_tasks": len(tasks),
            "total_pending_tasks": len([t for t in tasks if not t.completed]),
            "user_metrics": {},
            "most_overloaded_user": None,
            "least_loaded_user": None,
            "workload_distribution": {}
        }
        
        # Calculate per-user metrics
        max_workload = 0
        min_workload = float('inf')
        
        for user_id, user in users.items():
            # Get tasks assigned to this user
            user_tasks = [t for t in tasks if t.assigned_to == user_id]
            
            if not user_tasks:
                continue
                
            user_completed_tasks = [t for t in user_tasks if t.completed]
            user_pending_tasks = [t for t in user_tasks if not t.completed]
            
            # Calculate workload using estimated_hours if available
            estimated_hours = sum(getattr(t, 'estimated_hours', 0) or 0 for t in user_pending_tasks)
            workload_capacity = getattr(user, 'workload_capacity', 40.0)
            workload_percentage = (estimated_hours / workload_capacity * 100) if workload_capacity > 0 else 0
            
            # Calculate completion rate
            completion_rate = (len(user_completed_tasks) / len(user_tasks) * 100) if user_tasks else 0
            
            # Store user metrics
            result["user_metrics"][user_id] = {
                "name": user.name,
                "role": getattr(user, 'role', 'Unknown'),
                "total_tasks": len(user_tasks),
                "completed_tasks": len(user_completed_tasks),
                "pending_tasks": len(user_pending_tasks),
                "estimated_remaining_hours": estimated_hours,
                "workload_percentage": round(workload_percentage, 2),
                "completion_rate": round(completion_rate, 2)
            }
            
            # Track workload distribution
            result["workload_distribution"][user_id] = round(workload_percentage, 2)
            
            # Track most/least loaded users
            if workload_percentage > max_workload and len(user_tasks) > 0:
                max_workload = workload_percentage
                result["most_overloaded_user"] = user_id
                
            if workload_percentage < min_workload and len(user_tasks) > 0:
                min_workload = workload_percentage
                result["least_loaded_user"] = user_id
                
        return result
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create an empty result structure."""
        return {
            "total_users": 0,
            "total_tasks": 0,
            "total_pending_tasks": 0,
            "user_metrics": {},
            "most_overloaded_user": None,
            "least_loaded_user": None,
            "workload_distribution": {}
        }


class ProjectProgressStrategy(AnalyticsStrategy):
    """Strategy for analyzing project progress."""
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate project progress metrics.
        
        Args:
            project: Project object
            tasks: List of tasks for the project
            
        Returns:
            Dict with project progress metrics
        """
        project = kwargs.get('project')
        tasks = kwargs.get('tasks', [])
        
        if not project or not tasks:
            return self._create_empty_result(
                project_id=getattr(project, 'id', '') if project else '',
                project_name=getattr(project, 'name', '') if project else ''
            )
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate days remaining until target end date
        days_remaining = 0
        if hasattr(project, 'target_end_date'):
            date_diff = project.target_end_date - datetime.now()
            days_remaining = max(0, date_diff.days)
        
        # Analyze milestone status
        milestone_status = {}
        for milestone in project.milestones:
            is_overdue = not milestone.completed and milestone.due_date < datetime.now()
            milestone_status[milestone.id] = {
                "name": milestone.name,
                "description": milestone.description,
                "completed": milestone.completed,
                "due_date": milestone.due_date.isoformat() if milestone.due_date else None,
                "overdue": is_overdue
            }
        
        # Determine if project is on track
        on_track = True
        if hasattr(project, 'start_date') and hasattr(project, 'target_end_date'):
            total_project_days = (project.target_end_date - project.start_date).days
            days_elapsed = (datetime.now() - project.start_date).days
            
            if total_project_days > 0 and days_elapsed > 0:
                expected_completion = (days_elapsed / total_project_days) * 100
                on_track = completion_percentage >= (expected_completion * 0.9)  # 10% buffer
        
        # Group tasks by priority
        tasks_by_priority = defaultdict(int)
        for task in tasks:
            tasks_by_priority[task.priority] += 1
        
        # Get teams information
        teams_info = []
        for team in project.teams:
            team_info = {
                "id": team.id,
                "name": team.name,
                "member_count": len(team.team_members),
                "members": [
                    {
                        "id": member.id,
                        "user_id": member.user_id,
                        "role": member.role
                    }
                    for member in team.team_members
                ]
            }
            teams_info.append(team_info)
        
        return {
            "project_id": project.id,
            "project_name": project.name,
            "description": project.description,
            "status": project.status,
            "manager_id": project.manager_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_percentage": round(completion_percentage, 2),
            "days_remaining": days_remaining,
            "milestone_status": milestone_status,
            "on_track": on_track,
            "tasks_by_priority": dict(tasks_by_priority),
            "teams": teams_info,
            "metadata": project.metadata
        }
    
    def _create_empty_result(self, project_id: str, project_name: str) -> Dict[str, Any]:
        """Create an empty result structure."""
        return {
            "project_id": project_id,
            "project_name": project_name,
            "description": "",
            "status": "unknown",
            "manager_id": "",
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_percentage": 0,
            "days_remaining": 0,
            "milestone_status": {},
            "on_track": True,
            "tasks_by_priority": {},
            "teams": [],
            "metadata": {}
        }