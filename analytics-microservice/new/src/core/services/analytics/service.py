"""Core analytics service implementations."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from src.core.domain.models import Task, Project, User
from src.core.ports.repositories import TaskRepositoryPort, ProjectRepositoryPort, UserRepositoryPort
from src.core.services.analytics.strategies import (
    AnalyticsStrategy,
    TaskCompletionRateStrategy,
    PendingWorkAnalysisStrategy,
    ProductivityMetricsStrategy,
    TeamWorkloadStrategy,
    ProjectProgressStrategy
)
from src.core.ports.services import AnalyticsServicePort


class AnalyticsService(AnalyticsServicePort):
    """Service for performing analytics on task and project data."""
    
    def __init__(
        self, 
        task_repository: TaskRepositoryPort,
        project_repository: Optional[ProjectRepositoryPort] = None,
        user_repository: Optional[UserRepositoryPort] = None
    ):
        """Initialize the analytics service.
        
        Args:
            task_repository: Repository for accessing task data
            project_repository: Repository for accessing project data
            user_repository: Repository for accessing user data
        """
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.user_repository = user_repository
        
        # Initialize analytics strategies
        self.completion_rate_strategy = TaskCompletionRateStrategy()
        self.pending_work_strategy = PendingWorkAnalysisStrategy()
        self.productivity_strategy = ProductivityMetricsStrategy()
        self.team_workload_strategy = TeamWorkloadStrategy()
        self.project_progress_strategy = ProjectProgressStrategy()
    
    def get_completion_rate(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Calculate task completion rate over time.
        
        Args:
            time_period_days: Number of days to look back
            
        Returns:
            Dict with completion rate statistics
        """
        tasks = list(self.task_repository.get_all_tasks().values())
        return self.completion_rate_strategy.calculate(tasks=tasks, time_period_days=time_period_days)
    
    def get_pending_work_analysis(self) -> Dict[str, Any]:
        """Analyze pending work items.
        
        Returns:
            Dict with pending work statistics
        """
        tasks = list(self.task_repository.get_all_tasks().values())
        return self.pending_work_strategy.calculate(tasks=tasks)
    
    def get_productivity_metrics(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Calculate productivity metrics.
        
        Args:
            time_period_days: Number of days to look back
            
        Returns:
            Dict with productivity metrics
        """
        tasks = list(self.task_repository.get_all_tasks().values())
        return self.productivity_strategy.calculate(tasks=tasks, time_period_days=time_period_days)
    
    def get_team_workload(self) -> Dict[str, Any]:
        """Analyze team workload distribution.
        
        Returns:
            Dict with team workload metrics or error information
        """
        if not self.user_repository:
            return {"error": "User repository not available"}
            
        tasks = list(self.task_repository.get_all_tasks().values())
        users = self.user_repository.get_all_users()
        return self.team_workload_strategy.calculate(tasks=tasks, users=users)
    
    def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get progress metrics for a specific project.
        
        Args:
            project_id: ID of the project to analyze
            
        Returns:
            Dict with project progress metrics or error information
        """
        if not self.project_repository:
            return {"error": "Project repository not available"}
            
        project = self.project_repository.get_project(project_id)
        if not project:
            return {"error": f"Project with ID {project_id} not found"}
            
        project_tasks = self.task_repository.get_tasks_by_project(project_id)
        return self.project_progress_strategy.calculate(project=project, tasks=project_tasks)
    
    def get_all_projects_progress(self) -> Dict[str, Any]:
        """Get progress metrics for all projects.
        
        Returns:
            Dict with progress metrics for all projects or error information
        """
        if not self.project_repository:
            return {"error": "Project repository not available"}
            
        projects = self.project_repository.get_all_projects()
        
        results = {}
        for project_id, project in projects.items():
            project_tasks = self.task_repository.get_tasks_by_project(project_id)
            results[project_id] = self.project_progress_strategy.calculate(
                project=project, 
                tasks=project_tasks
            )
        
        return {
            "project_count": len(projects),
            "projects": results
        }
    
    def get_user_productivity(self, user_id: str, time_period_days: int = 30) -> Dict[str, Any]:
        """Get productivity metrics for a specific user.
        
        Args:
            user_id: ID of the user to analyze
            time_period_days: Number of days to look back
            
        Returns:
            Dict with user productivity metrics or error information
        """
        if not self.user_repository:
            return {"error": "User repository not available"}
            
        user = self.user_repository.get_user(user_id)
        if not user:
            return {"error": f"User with ID {user_id} not found"}
            
        # Get tasks assigned to this user
        user_tasks = self.task_repository.get_tasks_by_user(user_id)
        
        # Use the productivity strategy for user-specific metrics
        productivity_metrics = self.productivity_strategy.calculate(
            tasks=user_tasks, 
            time_period_days=time_period_days
        )
        
        # Add user info
        return {
            "user_id": user_id,
            "user_name": user.name,
            "user_role": getattr(user, 'role', 'Unknown'),
            **productivity_metrics
        }
    
    def get_complete_analytics_report(self) -> Dict[str, Any]:
        """Generate a complete analytics report.
        
        Returns:
            Dict with all analytics data
        """
        report = {
            "completion_rate": self.get_completion_rate(),
            "pending_work": self.get_pending_work_analysis(),
            "productivity": self.get_productivity_metrics(),
            "generated_at": datetime.now().isoformat()
        }
        
        # Add project and team analytics if repositories are available
        if self.project_repository:
            report["projects"] = self.get_all_projects_progress()
            
        if self.user_repository:
            report["team_workload"] = self.get_team_workload()
        
        return report