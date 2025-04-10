"""Error handling middleware for the API."""

from flask import jsonify, Blueprint, Flask, request
import traceback
import logging
from typing import Dict, Any, Callable, Optional

# Configure logging
logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Base class for API errors."""
    
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        """Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundError(ApiError):
    """Error for when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        """Initialize resource not found error.
        
        Args:
            resource_type: Type of resource (e.g., 'project', 'user')
            resource_id: ID of the resource that wasn't found
        """
        message = f"{resource_type.capitalize()} with ID '{resource_id}' not found"
        super().__init__(message=message, status_code=404, details={
            'resource_type': resource_type,
            'resource_id': resource_id
        })


class ValidationError(ApiError):
    """Error for request validation failures."""
    
    def __init__(self, message: str, validation_errors: Dict[str, str]):
        """Initialize validation error.
        
        Args:
            message: Error message
            validation_errors: Dictionary of field errors
        """
        super().__init__(message=message, status_code=400, details={
            'validation_errors': validation_errors
        })


class ConfigurationError(ApiError):
    """Error for service configuration issues."""
    
    def __init__(self, message: str):
        """Initialize configuration error.
        
        Args:
            message: Error message
        """
        super().__init__(message=message, status_code=500)


def register_error_handlers(app: Flask) -> None:
    """Register error handlers with the Flask application.
    
    Args:
        app: Flask application
    """
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        """Handle API errors."""
        response = {
            'error': error.message,
            'status_code': error.status_code
        }
        
        if error.details:
            response['details'] = error.details
            
        return jsonify(response), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(_):
        """Handle 404 not found errors."""
        return jsonify({
            'error': f"Endpoint not found: {request.path}",
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def handle_server_error(error):
        """Handle unexpected server errors."""
        # Log the error for debugging
        logger.error(f"Unexpected error: {str(error)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': "Internal server error",
            'status_code': 500
        }), 500