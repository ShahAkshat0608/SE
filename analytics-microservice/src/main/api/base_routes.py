from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPBearer
from typing import Dict, Any, Callable, Awaitable, Type, Optional
from pydantic import BaseModel
from abc import ABC, abstractmethod

from ..services.analytics_facade import AnalyticsFacade, ReportType
from ..utils.auth_utils import get_current_user, check_analytics_permission, RolePermission , verify_token

class BaseAnalyticsRoutes(ABC):
    """
    Abstract base class for analytics routes using Template Method pattern.
    Defines the skeleton of analytics route operations.
    """
    
    def __init__(self, prefix: str, permission_role: RolePermission):
        self.router = APIRouter()
        self.security = HTTPBearer()
        self.facade = AnalyticsFacade()
        self.prefix = prefix
        self.permission_role = permission_role
        
        # Register the routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all the necessary routes"""
        self.router.add_api_route(
            f"/{{entity_id}}/progress", 
            self.get_progress_analytics,
            methods=["GET"],
            response_model=self.get_progress_response_model()
        )
        
        self.router.add_api_route(
            f"/{{entity_id}}/workload", 
            self.get_workload_analytics,
            methods=["GET"],
            response_model=self.get_workload_response_model()
        )
        
        self.router.add_api_route(
            f"/{{entity_id}}/comprehensive", 
            self.get_comprehensive_analytics,
            methods=["GET"],
            response_model=self.get_comprehensive_response_model()
        )
        
        self.router.add_api_route(
            f"/{{entity_id}}", 
            self.get_analytics,
            methods=["GET"],
            response_model=self.get_comprehensive_response_model()
        )
    
    async def _check_permission(self, request: Request, entity_id: str, project_id: Optional[str], current_user: Dict):
        """Check if the user has permission to access the analytics"""
        has_permission = await check_analytics_permission(
            request, 
            self.permission_role, 
            entity_id,
            project_id=project_id,
            current_user=current_user
        )
        
        if not has_permission:
            entity_type = self.prefix.replace("/", "")
            raise HTTPException(
                status_code=403,
                detail=f"Not authorized to access this {entity_type}'s analytics"
            )
    
    @abstractmethod
    async def _generate_analytics(
        self, 
        entity_id: str, 
        project_id: Optional[str], 
        report_type: str, 
        visualize: bool
    ) -> Any:
        """Generate the analytics report. To be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_progress_response_model(self) -> Type[BaseModel]:
        """Get the response model for progress analytics"""
        pass
        
    @abstractmethod
    def get_workload_response_model(self) -> Type[BaseModel]:
        """Get the response model for workload analytics"""
        pass
        
    @abstractmethod
    def get_comprehensive_response_model(self) -> Type[BaseModel]:
        """Get the response model for comprehensive analytics"""
        pass
    
    # Template methods for the API endpoints
    async def get_progress_analytics(
        self,
        request: Request,
        entity_id: str,
        project_id: Optional[str] = None,
        visualize: bool = Query(False, description="Include visualization data"),
        # current_user: Dict = Depends(get_current_user)
    ):
        # print("Get progress analytics")
        # """Get progress analytics"""
        # access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJzYXJ0aGFrYmFuc2FsMzk1QGdtYWlsLmNvbSIsImV4cCI6MTc0NTE2MTc2My40MTA0NTR9.lI3DKUTAkmccBLkR9gxGxohzkr4vha4sTK5-OumXpco"
        # current_user_payload = await verify_token({"credentials": access_token})
        # print("Current user payload:", current_user_payload)
        # current_user = await get_current_user(current_user_payload)
        # print("Current user:", current_user)
        # await self._check_permission(request, entity_id, project_id, current_user)
        return await self._generate_analytics(entity_id, project_id, ReportType.PROGRESS, visualize)
    
    async def get_workload_analytics(
        self,
        request: Request,
        entity_id: str,
        project_id: Optional[str] = None,
        visualize: bool = Query(False, description="Include visualization data"),
        # current_user: Dict = Depends(get_current_user)
    ):
        """Get workload analytics"""
        # await self._check_permission(request, entity_id, project_id, current_user)
        return await self._generate_analytics(entity_id, project_id, ReportType.WORKLOAD, visualize)
    
    async def get_comprehensive_analytics(
        self,
        request: Request,
        entity_id: str,
        project_id: Optional[str] = None,
        visualize: bool = Query(False, description="Include visualization data"),
        # current_user: Dict = Depends(get_current_user)
    ):
        """Get comprehensive analytics"""
        # await self._check_permission(request, entity_id, project_id, current_user)
        return await self._generate_analytics(entity_id, project_id, ReportType.COMPREHENSIVE, visualize)
    
    async def get_analytics(
        self,
        request: Request,
        entity_id: str,
        project_id: Optional[str] = None,
        report_type: str = Query(ReportType.COMPREHENSIVE, description="Type of report (progress, workload, comprehensive)"),
        visualize: bool = Query(False, description="Include visualization data"),
        # current_user: Dict = Depends(get_current_user)
    ):
        """Get analytics with specified report type"""
        # await self._check_permission(request, entity_id, project_id, current_user)
        response = await self._generate_analytics(entity_id, project_id, report_type, visualize)
        return response