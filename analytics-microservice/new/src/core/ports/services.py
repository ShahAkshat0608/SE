"""Service interfaces for the analytics microservice."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AnalyticsServicePort(ABC):
    """Interface for analytics service."""
    
    @abstractmethod
    def get_completion_rate(self, time_period_days: int = 30, project_id: Optional[str] = None, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate task completion rate over time.
        
        Args:
            time_period_days: Number of days to look back
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with completion rate statistics
        """
        pass
    
    @abstractmethod
    def get_pending_work_analysis(self, project_id: Optional[str] = None, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze pending work items.
        
        Args:
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with pending work statistics
        """
        pass
    
    @abstractmethod
    def get_productivity_metrics(self, time_period_days: int = 30, project_id: Optional[str] = None, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate productivity metrics.
        
        Args:
            time_period_days: Number of days to look back
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with productivity metrics
        """
        pass
    
    @abstractmethod
    def get_team_workload(self, project_id: Optional[str] = None, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze team workload distribution.
        
        Args:
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with team workload metrics
        """
        pass
    
    @abstractmethod
    def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get progress metrics for a specific project.
        
        Args:
            project_id: ID of the project to analyze
            
        Returns:
            Dict with project progress metrics
        """
        pass
    
    @abstractmethod
    def get_all_projects_progress(self) -> Dict[str, Any]:
        """Get progress metrics for all projects.
        
        Returns:
            Dict with progress metrics for all projects
        """
        pass
    
    @abstractmethod
    def get_user_productivity(self, user_id: str, time_period_days: int = 30, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get productivity metrics for a specific user.
        
        Args:
            user_id: ID of the user to analyze
            time_period_days: Number of days to look back
            project_id: Optional project ID to filter by
            
        Returns:
            Dict with user productivity metrics
        """
        pass
    
    @abstractmethod
    def get_complete_analytics_report(self, project_id: Optional[str] = None, team_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete analytics report.
        
        Args:
            project_id: Optional project ID to filter by
            team_id: Optional team ID to filter by
            
        Returns:
            Dict with all analytics data
        """
        pass


class AnalyticsEventPublisherPort(ABC):
    """Interface for publishing analytics events."""
    
    @abstractmethod
    def publish_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Publish an analytics event.
        
        Args:
            event_name: Name of the event
            event_data: Event data
        """
        pass