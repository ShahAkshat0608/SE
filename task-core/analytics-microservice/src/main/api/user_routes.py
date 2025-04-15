from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPBearer
from typing import Dict, Optional
import time

from services.user_analytics.progress import UserProgressAnalytics
from services.user_analytics.workload import UserWorkloadAnalytics
from services.user_analytics.comprehensive import UserComprehensiveAnalytics
from models.response_models import UserProgressResponse, UserWorkloadResponse, UserComprehensiveResponse
from utils.auth_utils import verify_token, get_current_user, check_analytics_permission, RolePermission
from utils.analytics_utils import generate_visualization_data

router = APIRouter()
security = HTTPBearer()

# Initialize services
progress_service = UserProgressAnalytics()
workload_service = UserWorkloadAnalytics()
comprehensive_service = UserComprehensiveAnalytics()

@router.get("/{user_id}/progress", response_model=UserProgressResponse)
async def get_user_progress(
    request: Request,
    user_id: str,
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get progress analytics for a specific user
    
    Parameters:
    - user_id: ID of the user to analyze
    - visualize: Whether to include visualization data
    
    Returns:
    - User progress analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.USER_ANALYTICS, 
        user_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this user's analytics"
        )
    
    # Get analytics report
    start_time = time.time()
    report = await progress_service.get_progress_report(user_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("progress", report.dict())
    
    # Add processing time for debugging
    if hasattr(request.state, "process_time"):
        request.state.process_time = time.time() - start_time
    
    return report

@router.get("/{user_id}/workload", response_model=UserWorkloadResponse)
async def get_user_workload(
    request: Request,
    user_id: str,
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get workload analytics for a specific user
    
    Parameters:
    - user_id: ID of the user to analyze
    - visualize: Whether to include visualization data
    
    Returns:
    - User workload analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.USER_ANALYTICS, 
        user_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this user's analytics"
        )
    
    # Get analytics report
    report = await workload_service.get_workload_report(user_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("workload", report.dict())
    
    return report

@router.get("/{user_id}/comprehensive", response_model=UserComprehensiveResponse)
async def get_user_comprehensive(
    request: Request,
    user_id: str,
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a specific user
    
    Parameters:
    - user_id: ID of the user to analyze
    - visualize: Whether to include visualization data
    
    Returns:
    - User comprehensive analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.USER_ANALYTICS, 
        user_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this user's analytics"
        )
    
    # Get analytics report
    report = await comprehensive_service.get_comprehensive_report(user_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("comprehensive", report.dict())
    
    return report

@router.get("/{user_id}", response_model=UserComprehensiveResponse)
async def get_user_analytics(
    request: Request,
    user_id: str,
    report_type: str = Query("comprehensive", description="Type of report (progress, workload, comprehensive)"),
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get analytics for a specific user
    
    Parameters:
    - user_id: ID of the user to analyze
    - report_type: Type of report (progress, workload, comprehensive)
    - visualize: Whether to include visualization data
    
    Returns:
    - User analytics report
    """
    # Route to the appropriate endpoint based on report type
    if report_type == "progress":
        return await get_user_progress(request, user_id, visualize, current_user)
    elif report_type == "workload":
        return await get_user_workload(request, user_id, visualize, current_user)
    else:  # comprehensive or any other value
        return await get_user_comprehensive(request, user_id, visualize, current_user)