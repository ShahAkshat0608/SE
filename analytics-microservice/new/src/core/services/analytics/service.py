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
    
    def _filter_tasks_by_project_and_team(
        self, 
        tasks: List[Task], 
        project_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> List[Task]:
        """Filter tasks by project and/or team.
        
        Args:
            tasks: List of tasks to filter
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Filtered list of tasks
        """
        if not tasks:
            return []
            
        filtered_tasks = tasks
        
        # Filter by project if specified
        if project_id:
            filtered_tasks = [task for task in filtered_tasks if task.project_id == project_id]
        
        # Filter by team if specified
        if team_id and self.project_repository:
            # Find all projects with this team
            team_projects = [
                p.id for p in self.project_repository.get_all_projects().values() 
                if hasattr(p, 'teams') and team_id in getattr(p, 'teams', [])
            ]
            
            # Filter tasks for these projects
            if team_projects:
                filtered_tasks = [task for task in filtered_tasks if task.project_id in team_projects]
        
        return filtered_tasks
    
    def get_completion_rate(
        self, 
        time_period_days: int = 30, 
        project_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate task completion rate over time.
        
        Args:
            time_period_days: Number of days to look back
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with completion rate statistics
        """
        tasks = list(self.task_repository.get_all_tasks().values())
        
        # Apply filtering
        tasks = self._filter_tasks_by_project_and_team(tasks, project_id, team_id)
        
        result = self.completion_rate_strategy.calculate(tasks=tasks, time_period_days=time_period_days)
        
        # Add filter information
        if project_id or team_id:
            result["filters"] = {}
            if project_id:
                result["filters"]["project_id"] = project_id
            if team_id:
                result["filters"]["team_id"] = team_id
                
        return result
    
    def get_pending_work_analysis(
        self, 
        project_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze pending work items.
        
        Args:
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with pending work statistics
        """
        tasks = list(self.task_repository.get_all_tasks().values())
        
        # Apply filtering
        tasks = self._filter_tasks_by_project_and_team(tasks, project_id, team_id)
        
        result = self.pending_work_strategy.calculate(tasks=tasks)
        
        # Add filter information
        if project_id or team_id:
            result["filters"] = {}
            if project_id:
                result["filters"]["project_id"] = project_id
            if team_id:
                result["filters"]["team_id"] = team_id
                
        return result
    
    def get_productivity_metrics(
        self, 
        time_period_days: int = 30,
        project_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate productivity metrics.
        
        Args:
            time_period_days: Number of days to look back
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with productivity metrics
        """
        tasks = list(self.task_repository.get_all_tasks().values())
        
        # Apply filtering
        tasks = self._filter_tasks_by_project_and_team(tasks, project_id, team_id)
        
        result = self.productivity_strategy.calculate(tasks=tasks, time_period_days=time_period_days)
        
        # Add filter information
        if project_id or team_id:
            result["filters"] = {}
            if project_id:
                result["filters"]["project_id"] = project_id
            if team_id:
                result["filters"]["team_id"] = team_id
                
        return result
    
    def get_team_workload(
        self,
        project_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze team workload distribution.
        
        Args:
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with team workload metrics or error information
        """
        if not self.user_repository:
            return {"error": "User repository not available"}
        
        tasks = list(self.task_repository.get_all_tasks().values())
        
        # Apply filtering
        tasks = self._filter_tasks_by_project_and_team(tasks, project_id, team_id)
        
        users = self.user_repository.get_all_users()
        
        # If team_id is specified, filter users by team
        if team_id and hasattr(users[next(iter(users))], 'team_id'):
            users = {uid: user for uid, user in users.items() if getattr(user, 'team_id', None) == team_id}
        
        result = self.team_workload_strategy.calculate(tasks=tasks, users=users)
        
        # Add filter information
        if project_id or team_id:
            result["filters"] = {}
            if project_id:
                result["filters"]["project_id"] = project_id
            if team_id:
                result["filters"]["team_id"] = team_id
                
        return result
    
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
    
    def get_user_productivity(
        self, 
        user_id: str, 
        time_period_days: int = 30,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get productivity metrics for a specific user.
        
        Args:
            user_id: ID of the user to analyze
            time_period_days: Number of days to look back
            project_id: Optional project ID to filter by
            
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
        
        # Apply project filtering if needed
        if project_id:
            user_tasks = [task for task in user_tasks if task.project_id == project_id]
        
        # Use the productivity strategy for user-specific metrics
        productivity_metrics = self.productivity_strategy.calculate(
            tasks=user_tasks, 
            time_period_days=time_period_days
        )
        
        # Add user info and filter information
        result = {
            "user_id": user_id,
            "user_name": user.name,
            "user_role": getattr(user, 'role', 'Unknown'),
            **productivity_metrics
        }
        
        if project_id:
            result["filters"] = {"project_id": project_id}
            
        return result
    
    def get_complete_analytics_report(
        self, 
        project_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete analytics report.
        
        Args:
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with all analytics data
        """
        report = {
            "completion_rate": self.get_completion_rate(project_id=project_id, team_id=team_id),
            "pending_work": self.get_pending_work_analysis(project_id=project_id, team_id=team_id),
            "productivity": self.get_productivity_metrics(project_id=project_id, team_id=team_id),
            "generated_at": datetime.now().isoformat()
        }
        
        # Add filter information
        if project_id or team_id:
            report["filters"] = {}
            if project_id:
                report["filters"]["project_id"] = project_id
                
                # Add project name if available
                if self.project_repository:
                    project = self.project_repository.get_project(project_id)
                    if project:
                        report["filters"]["project_name"] = project.name
            
            if team_id:
                report["filters"]["team_id"] = team_id
        
        # Add project and team analytics if repositories are available
        if self.project_repository:
            if project_id:
                report["project"] = self.get_project_progress(project_id)
            else:
                report["projects"] = self.get_all_projects_progress()
            
        if self.user_repository:
            report["team_workload"] = self.get_team_workload(project_id=project_id, team_id=team_id)
        
        return report