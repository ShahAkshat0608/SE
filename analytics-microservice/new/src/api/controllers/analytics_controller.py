"""Controllers for analytics API endpoints."""

from flask import request, jsonify, Blueprint
from typing import Dict, Any, Optional

from src.core.ports.services import AnalyticsServicePort
from src.api.middleware.error_handler import ResourceNotFoundError, ValidationError


class AnalyticsController:
    """Controller for analytics-related endpoints."""
    
    def __init__(self, analytics_service: AnalyticsServicePort):
        """Initialize analytics controller.
        
        Args:
            analytics_service: Service for performing analytics
        """
        self.analytics_service = analytics_service
    
    def get_health(self):
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "analytics-microservice"
        })
    
    def get_completion_rate(self):
        """Get task completion rate statistics."""
        days = self._parse_days_param()
        result = self.analytics_service.get_completion_rate(days)
        return jsonify(result)
    
    def get_pending_work(self):
        """Get pending work statistics."""
        result = self.analytics_service.get_pending_work_analysis()
        return jsonify(result)
    
    def get_productivity_metrics(self):
        """Get productivity metrics."""
        days = self._parse_days_param()
        result = self.analytics_service.get_productivity_metrics(days)
        return jsonify(result)
    
    def get_team_workload(self):
        """Get team workload distribution."""
        result = self.analytics_service.get_team_workload()
        if "error" in result:
            raise ValidationError("Failed to get team workload", {"reason": result["error"]})
        return jsonify(result)
    
    def get_project_progress(self, project_id: str):
        """Get progress metrics for a specific project.
        
        Args:
            project_id: ID of the project to analyze
        """
        result = self.analytics_service.get_project_progress(project_id)
        if "error" in result:
            raise ResourceNotFoundError("project", project_id)
        return jsonify(result)
    
    def get_all_projects_progress(self):
        """Get progress metrics for all projects."""
        result = self.analytics_service.get_all_projects_progress()
        if "error" in result:
            raise ValidationError("Failed to get project progress", {"reason": result["error"]})
        return jsonify(result)
    
    def get_user_productivity(self, user_id: str):
        """Get productivity metrics for a specific user.
        
        Args:
            user_id: ID of the user to analyze
        """
        days = self._parse_days_param()
        result = self.analytics_service.get_user_productivity(user_id, days)
        if "error" in result:
            raise ResourceNotFoundError("user", user_id)
        return jsonify(result)
    
    def get_complete_report(self):
        """Get complete analytics report."""
        result = self.analytics_service.get_complete_analytics_report()
        return jsonify(result)
    
    def _parse_days_param(self) -> int:
        """Parse and validate days parameter from request.
        
        Returns:
            Days parameter as integer
        """
        try:
            days = request.args.get('days', default=30, type=int)
            if days <= 0:
                raise ValidationError("Invalid time period", {"days": "Must be positive"})
            return days
        except ValueError:
            raise ValidationError("Invalid time period", {"days": "Must be an integer"})