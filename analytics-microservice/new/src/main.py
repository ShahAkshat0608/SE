"""Main entry point for the analytics microservice."""

import sys
import os
from typing import Optional, Dict, Any

from flask import Flask
import logging

# Configure paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import application components
from src.common.logging.logger import setup_logging, get_logger
from src.common.config.settings import get_settings
from src.core.services.factory import ServiceFactory
from src.api.middleware.error_handler import register_error_handlers
from src.api.routes import register_routes
from src.cli.commands import main as cli_main


# Initialize logger
logger = get_logger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Get settings and services
    settings = get_settings()
    services = ServiceFactory.create_services_from_config()
    
    # Configure error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app, services['analytics_service'])
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """Run the Flask server.
    
    Args:
        host: Host to bind
        port: Port to bind
        debug: Whether to enable debug mode
    """
    app = create_app()
    logger.info(f"Starting server on {host}:{port}, debug={debug}")
    app.run(host=host, port=port, debug=debug)


def main() -> int:
    """Main entry point for the application.
    
    Returns:
        Exit code
    """
    try:
        # Load settings
        settings = get_settings()
        
        # Set up logging
        setup_logging(
            log_level=settings.LOG_LEVEL,
            log_file=settings.LOG_FILE
        )
        
        # Run CLI
        return cli_main()
        
    except Exception as e:
        # Log unhandled exceptions
        if logging.getLogger().isEnabledFor(logging.ERROR):
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())