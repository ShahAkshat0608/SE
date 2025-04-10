"""Logging configuration for the analytics microservice."""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
    """Set up logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs to console only)
        log_format: Format string for log messages
    """
    # Convert string log level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory if log_file is specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)
    
    # File handler if log_file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format=log_format
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Name for the logger (typically __name__ of the calling module)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LoggerContext:
    """Context manager for logging operations with timing info."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        """Initialize the logger context.
        
        Args:
            logger: Logger instance
            operation: Name of the operation being performed
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        """Enter the context and log the start of the operation."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and log the completion of the operation."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is not None:
            # Log exception if one occurred
            self.logger.error(f"{self.operation} failed after {duration:.2f} seconds: {exc_val}")
        else:
            # Log successful completion
            self.logger.info(f"Completed {self.operation} in {duration:.2f} seconds")
        
        # Don't suppress exceptions
        return False