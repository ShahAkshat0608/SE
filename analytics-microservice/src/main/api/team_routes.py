from typing import Optional, Type
from fastapi import Query, Request, Depends
from pydantic import BaseModel

from ..models.response_models import TeamProgressResponse, TeamWorkloadResponse, TeamComprehensiveResponse
from ..utils.auth_utils import RolePermission, get_current_user
from .base_routes import BaseAnalyticsRoutes
from fastapi import Response, status

class TeamAnalyticsRoutes(BaseAnalyticsRoutes):
    """Team analytics routes implementation"""
    
    def __init__(self):
        super().__init__("/teams", RolePermission.TEAM_ANALYTICS)
    
    async def _generate_analytics(self, entity_id: str, project_id: Optional[str], report_type: str, visualize: bool):
        """Generate team analytics report"""
        if not project_id:
            raise ValueError("Project ID is required for team analytics")
        
        result = await self.facade.generate_team_analytics(entity_id, project_id, report_type, visualize)
        if result:
            return Response(
                content=result.json(), 
                media_type="application/json",
                status_code=status.HTTP_200_OK
            )
        return result
    
    def get_progress_response_model(self) -> Type[BaseModel]:
        return TeamProgressResponse
        
    def get_workload_response_model(self) -> Type[BaseModel]:
        return TeamWorkloadResponse
        
    def get_comprehensive_response_model(self) -> Type[BaseModel]:
        return TeamComprehensiveResponse
    
    # Override the route methods to require project_id
    async def get_progress_analytics(
        self,
        request: Request,
        entity_id: str,
        project_id: str = Query(..., description="Project ID"),
        visualize: bool = Query(False, description="Include visualization data"),
        # current_user: dict = Depends(get_current_user)
    ):
        return await super().get_progress_analytics(request, entity_id, project_id, visualize)
    
    async def get_workload_analytics(
        self,
        request: Request,
        entity_id: str,
        project_id: str = Query(..., description="Project ID"),
        visualize: bool = Query(False, description="Include visualization data"),
        # current_user: dict = Depends(get_current_user)
    ):
        return await super().get_workload_analytics(request, entity_id, project_id, visualize)
    
    async def get_comprehensive_analytics(
        self,
        request: Request,
        entity_id: str,
        project_id: str = Query(..., description="Project ID"),
        visualize: bool = Query(False, description="Include visualization data"),
        # current_user: dict = Depends(get_current_user)
    ):
        return await super().get_comprehensive_analytics(request, entity_id, project_id, visualize)
    
    async def get_analytics(
        self,
        request: Request,
        entity_id: str,
        project_id: str = Query(..., description="Project ID"),
        report_type: str = Query("comprehensive", description="Type of report (progress, workload, comprehensive)"),
        visualize: bool = Query(False, description="Include visualization data"),
        # current_user: dict = Depends(get_current_user)
    ):
        return await super().get_analytics(request, entity_id, project_id, report_type, visualize)

# Create an instance to expose the router
team_routes = TeamAnalyticsRoutes()
router = team_routes.router