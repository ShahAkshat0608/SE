"""API route definitions."""

from flask import Blueprint, Flask

from src.api.controllers.analytics_controller import AnalyticsController
from src.core.ports.services import AnalyticsServicePort


def create_analytics_blueprint(analytics_service: AnalyticsServicePort) -> Blueprint:
    """Create blueprint for analytics routes.
    
    Args:
        analytics_service: Service for analytics operations
        
    Returns:
        Configured Flask blueprint
    """
    controller = AnalyticsController(analytics_service)
    blueprint = Blueprint('analytics', __name__, url_prefix='/api/analytics')
    
    # Register routes
    blueprint.route('/health')(controller.get_health)
    blueprint.route('/completion-rate')(controller.get_completion_rate)
    blueprint.route('/pending-work')(controller.get_pending_work)
    blueprint.route('/productivity')(controller.get_productivity_metrics)
    blueprint.route('/team-workload')(controller.get_team_workload)
    blueprint.route('/project/<project_id>')(controller.get_project_progress)
    blueprint.route('/projects')(controller.get_all_projects_progress)
    blueprint.route('/user/<user_id>')(controller.get_user_productivity)
    blueprint.route('/report')(controller.get_complete_report)
    
    return blueprint


def register_routes(app: Flask, analytics_service: AnalyticsServicePort) -> None:
    """Register all API routes with the Flask application.
    
    Args:
        app: Flask application instance
        analytics_service: Analytics service instance
    """
    # Create and register analytics blueprint
    analytics_blueprint = create_analytics_blueprint(analytics_service)
    app.register_blueprint(analytics_blueprint)
    
    # Register root route
    @app.route('/')
    def index():
        return {
            "service": "Task Analytics Microservice",
            "status": "running",
            "endpoints": [
                "/api/analytics/health",
                "/api/analytics/completion-rate",
                "/api/analytics/pending-work",
                "/api/analytics/productivity",
                "/api/analytics/team-workload",
                "/api/analytics/project/<project_id>",
                "/api/analytics/projects",
                "/api/analytics/user/<user_id>",
                "/api/analytics/report"
            ]
        }