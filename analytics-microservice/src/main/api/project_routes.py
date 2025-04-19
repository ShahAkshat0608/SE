from typing import Optional, Type
from pydantic import BaseModel

from ..models.response_models import ProjectProgressResponse, ProjectWorkloadResponse, ProjectComprehensiveResponse
from ..utils.auth_utils import RolePermission
from .base_routes import BaseAnalyticsRoutes
from fastapi import Response, status

class ProjectAnalyticsRoutes(BaseAnalyticsRoutes):
    """Project analytics routes implementation"""
    
    def __init__(self):
        super().__init__("/projects", RolePermission.PROJECT_ANALYTICS)
    
    async def _generate_analytics(self, entity_id: str, project_id: Optional[str], report_type: str, visualize: bool):
        """Generate project analytics report"""
        # For projects, the entity_id is the project_id
        print(f"Generating {report_type} analytics for project {entity_id} with visualize={visualize}")
        result = await self.facade.generate_project_analytics(entity_id, report_type, visualize)
        if result:
            return Response(
                content=result.json(), 
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
        return result
    
    def get_progress_response_model(self) -> Type[BaseModel]:
        return ProjectProgressResponse
        
    def get_workload_response_model(self) -> Type[BaseModel]:
        return ProjectWorkloadResponse
        
    def get_comprehensive_response_model(self) -> Type[BaseModel]:
        return ProjectComprehensiveResponse

# Create an instance to expose the router
project_routes = ProjectAnalyticsRoutes()
router = project_routes.router