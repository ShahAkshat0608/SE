"""API endpoints for the analytics microservice."""

from flask import Flask, jsonify, request
import json

from analytics import TaskAnalytics
from repository import TaskRepository
import config


def create_api(analytics: TaskAnalytics = None):
    """Create and configure the Flask application.
    
    Args:
        analytics: The analytics service to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Create analytics service if not provided
    if analytics is None:
        repo = TaskRepository()
        analytics = TaskAnalytics(repo)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint."""
        return jsonify({"status": "healthy", "service": "analytics-microservice"})
    
    @app.route('/api/analytics/completion-rate', methods=['GET'])
    def get_completion_rate():
        """Get task completion rate statistics."""
        days = request.args.get('days', 30, type=int)
        return jsonify(analytics.get_completion_rate(days))
    
    @app.route('/api/analytics/pending-work', methods=['GET'])
    def get_pending_work():
        """Get pending work statistics."""
        return jsonify(analytics.get_pending_work_analysis())
    
    @app.route('/api/analytics/productivity', methods=['GET'])
    def get_productivity():
        """Get productivity metrics."""
        days = request.args.get('days', 30, type=int)
        return jsonify(analytics.get_productivity_metrics(days))
    
    @app.route('/api/analytics/report', methods=['GET'])
    def get_report():
        """Get complete analytics report."""
        return jsonify(analytics.get_complete_analytics_report())
    
    return app