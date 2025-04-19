from typing import Optional, Type
from pydantic import BaseModel
import time

from ..models.response_models import UserProgressResponse, UserWorkloadResponse, UserComprehensiveResponse
from ..utils.auth_utils import RolePermission
from .base_routes import BaseAnalyticsRoutes

class UserAnalyticsRoutes(BaseAnalyticsRoutes):
    """User analytics routes implementation"""
    
    def __init__(self):
        super().__init__("/users", RolePermission.USER_ANALYTICS)
    
    async def _generate_analytics(self, entity_id: str, project_id: Optional[str], report_type: str, visualize: bool):
        """Generate user analytics report"""
        # For users, project_id is not used
        return await self.facade.generate_user_analytics(entity_id, report_type, visualize)
    
    def get_progress_response_model(self) -> Type[BaseModel]:
        return UserProgressResponse
        
    def get_workload_response_model(self) -> Type[BaseModel]:
        return UserWorkloadResponse
        
    def get_comprehensive_response_model(self) -> Type[BaseModel]:
        return UserComprehensiveResponse

# Create an instance to expose the router
user_routes = UserAnalyticsRoutes()
router = user_routes.router