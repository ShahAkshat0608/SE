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
    
    def _is_team_valid(self, project_id: str, team_id: str) -> bool:
        """Check if a team ID exists in a specific project.
        
        Args:
            project_id: Project ID to check in
            team_id: Team ID to validate
            
        Returns:
            True if team exists in the project, False otherwise
        """
        if not self.project_repository:
            return False
            
        project = self.project_repository.get_project(project_id)
        if not project:
            return False
            
        for team in project.teams:
            if team.id == team_id:
                return True
                
        return False
    
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
        if team_id and project_id and self.project_repository:
            project = self.project_repository.get_project(project_id)
            if not project:
                return []
                
            # Find the specified team in the project
            team_members = []
            for team in project.teams:
                if team.id == team_id:
                    team_members = [member.user_id for member in team.team_members]
                    break
                    
            if not team_members:
                return []  # Team not found or empty
                
            # Filter tasks assigned to these users
            filtered_tasks = [task for task in filtered_tasks 
                             if task.assigned_to in team_members]
        
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
        users = self.user_repository.get_all_users()
        
        # Filter by project if specified
        if project_id and self.project_repository:
            project = self.project_repository.get_project(project_id)
            if not project:
                return {"error": f"Project with ID {project_id} not found"}
            
            # Filter tasks by project
            tasks = [task for task in tasks if task.project_id == project_id]
            
            # Get all user IDs from all teams in the project
            project_user_ids = []
            for team in project.teams:
                for member in team.team_members:
                    project_user_ids.append(member.user_id)
                    
            # Further filter by specific team if requested
            if team_id:
                team_found = False
                team_user_ids = []
                
                # Find the specific team and get its members
                for team in project.teams:
                    if team.id == team_id:
                        team_found = True
                        team_user_ids = [member.user_id for member in team.team_members]
                        break
                        
                if not team_found:
                    return {"error": f"Team with ID {team_id} not found in project {project_id}"}
                    
                project_user_ids = team_user_ids
                
            # Filter users to just those in the project/team
            users = {user_id: user for user_id, user in users.items() 
                    if user_id in project_user_ids}
        
        # Filter tasks to only those assigned to these users
        user_ids = list(users.keys())
        tasks = [task for task in tasks if task.assigned_to in user_ids]
        
        result = self.team_workload_strategy.calculate(tasks=tasks, users=users)
        
        # Add filter information
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
            "user_role": user.role,
            **productivity_metrics
        }
        
        if project_id:
            result["filters"] = {"project_id": project_id}
            
        return result
    
    def get_team_analytics(
        self,
        project_id: str,
        team_id: str,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for a specific team in a project.
        
        Args:
            project_id: ID of the project
            team_id: ID of the team
            time_period_days: Number of days to look back
            
        Returns:
            Dict with team analytics data or error information
        """
        if not self.project_repository:
            return {"error": "Project repository not available"}
            
        project = self.project_repository.get_project(project_id)
        if not project:
            return {"error": f"Project with ID {project_id} not found"}
            
        # Find the team in the project
        team = None
        for t in project.teams:
            if t.id == team_id:
                team = t
                break
                
        if not team:
            return {"error": f"Team with ID {team_id} not found in project {project_id}"}
            
        # Get all user IDs in this team
        team_user_ids = [member.user_id for member in team.team_members]
        
        # Get tasks for this project
        project_tasks = self.task_repository.get_tasks_by_project(project_id)
        
        # Filter tasks assigned to team members
        team_tasks = [task for task in project_tasks if task.assigned_to in team_user_ids]
        
        # Gather analytics for the team
        return {
            "team_id": team.id,
            "team_name": team.name,
            "member_count": len(team.team_members),
            "completion_rate": self.completion_rate_strategy.calculate(
                tasks=team_tasks, 
                time_period_days=time_period_days
            ),
            "pending_work": self.pending_work_strategy.calculate(tasks=team_tasks),
            "productivity": self.productivity_strategy.calculate(
                tasks=team_tasks,
                time_period_days=time_period_days
            ),
            "workload": self.team_workload_strategy.calculate(
                tasks=team_tasks,
                users={user_id: self.user_repository.get_user(user_id) 
                      for user_id in team_user_ids 
                      if self.user_repository.get_user(user_id)}
            ) if self.user_repository else {"error": "User repository not available"}
        }
    
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
                        
                        # Add team name if available
                        if team_id:
                            for team in project.teams:
                                if team.id == team_id:
                                    report["filters"]["team_id"] = team_id
                                    report["filters"]["team_name"] = team.name
                                    break
            elif team_id:
                report["filters"]["team_id"] = team_id
        
        # Add project and team analytics if repositories are available
        if self.project_repository:
            if project_id:
                report["project"] = self.get_project_progress(project_id)
                
                # Add specific team analytics if requested
                if team_id and self._is_team_valid(project_id, team_id):
                    report["team"] = self.get_team_analytics(project_id, team_id)
            else:
                report["projects"] = self.get_all_projects_progress()
            
        if self.user_repository:
            report["team_workload"] = self.get_team_workload(project_id=project_id, team_id=team_id)
        
        return report