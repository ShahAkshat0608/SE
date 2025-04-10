"""Factory for creating service instances."""

import os
from typing import Dict, Any, Optional

from src.core.ports.services import AnalyticsServicePort
from src.core.services.analytics.service import AnalyticsService
from src.core.ports.repositories import TaskRepositoryPort, ProjectRepositoryPort, UserRepositoryPort
from src.common.config.settings import get_settings


class ServiceFactory:
    """Factory for creating service instances."""
    
    @staticmethod
    def create_analytics_service(
        task_repository: TaskRepositoryPort,
        project_repository: Optional[ProjectRepositoryPort] = None,
        user_repository: Optional[UserRepositoryPort] = None
    ) -> AnalyticsServicePort:
        """Create an analytics service instance.
        
        Args:
            task_repository: Repository for tasks
            project_repository: Repository for projects (optional)
            user_repository: Repository for users (optional)
            
        Returns:
            Configured analytics service
        """
        return AnalyticsService(
            task_repository=task_repository,
            project_repository=project_repository,
            user_repository=user_repository
        )
    
    @staticmethod
    def create_services_from_config() -> Dict[str, Any]:
        """Create services based on application configuration.
        
        Returns:
            Dictionary of service instances
        """
        from src.data.repositories.json.task_repository import JsonTaskRepository
        
        settings = get_settings()
        
        # Create repositories
        task_repository = JsonTaskRepository(settings.TASKS_FILE)
        
        project_repository = None
        if os.path.exists(settings.PROJECTS_FILE):
            from src.data.repositories.json.project_repository import JsonProjectRepository
            project_repository = JsonProjectRepository(settings.PROJECTS_FILE)
            
        user_repository = None
        if os.path.exists(settings.USERS_FILE):
            from src.data.repositories.json.user_repository import JsonUserRepository
            user_repository = JsonUserRepository(settings.USERS_FILE)
        
        # Create services
        analytics_service = ServiceFactory.create_analytics_service(
            task_repository=task_repository,
            project_repository=project_repository,
            user_repository=user_repository
        )
        
        return {
            "analytics_service": analytics_service
        }