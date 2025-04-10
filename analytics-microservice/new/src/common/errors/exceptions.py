"""Custom exceptions for the analytics microservice."""

from typing import Dict, Any, Optional


class AnalyticsError(Exception):
    """Base class for all analytics exceptions."""
    
    def __init__(self, message: str):
        """Initialize the exception.
        
        Args:
            message: Error message
        """
        self.message = message
        super().__init__(self.message)


class RepositoryError(AnalyticsError):
    """Exception raised for errors in the repository layer."""
    
    def __init__(self, message: str, repository_name: str, operation: str):
        """Initialize the repository error.
        
        Args:
            message: Error message
            repository_name: Name of the repository where the error occurred
            operation: Operation that caused the error
        """
        self.repository_name = repository_name
        self.operation = operation
        super().__init__(f"Repository error in {repository_name} during {operation}: {message}")


class DataSourceError(AnalyticsError):
    """Exception raised for errors in the data source."""
    
    def __init__(self, message: str, source_name: str, source_path: Optional[str] = None):
        """Initialize the data source error.
        
        Args:
            message: Error message
            source_name: Name of the data source
            source_path: Path to the data source (if applicable)
        """
        self.source_name = source_name
        self.source_path = source_path
        source_info = f" at {source_path}" if source_path else ""
        super().__init__(f"Data source error in {source_name}{source_info}: {message}")


class ConfigurationError(AnalyticsError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        """Initialize the configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error (if applicable)
        """
        self.config_key = config_key
        key_info = f" for key '{config_key}'" if config_key else ""
        super().__init__(f"Configuration error{key_info}: {message}")


class ValidationError(AnalyticsError):
    """Exception raised for data validation errors."""
    
    def __init__(self, message: str, invalid_fields: Optional[Dict[str, str]] = None):
        """Initialize the validation error.
        
        Args:
            message: Error message
            invalid_fields: Dictionary of field names and validation errors
        """
        self.invalid_fields = invalid_fields or {}
        super().__init__(message)


class EntityNotFoundError(AnalyticsError):
    """Exception raised when an entity is not found."""
    
    def __init__(self, entity_type: str, entity_id: str):
        """Initialize the entity not found error.
        
        Args:
            entity_type: Type of entity (e.g., 'task', 'project')
            entity_id: ID of the entity that wasn't found
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type.capitalize()} with ID '{entity_id}' not found")


class ServiceError(AnalyticsError):
    """Exception raised for errors in service layer."""
    
    def __init__(self, message: str, service_name: str):
        """Initialize the service error.
        
        Args:
            message: Error message
            service_name: Name of the service where the error occurred
        """
        self.service_name = service_name
        super().__init__(f"Service error in {service_name}: {message}")