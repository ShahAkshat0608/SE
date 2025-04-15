from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPBearer
from typing import Dict, Optional

from services.project_analytics.progress import ProjectProgressAnalytics
from services.project_analytics.workload import ProjectWorkloadAnalytics
from services.project_analytics.comprehensive import ProjectComprehensiveAnalytics
from models.response_models import ProjectProgressResponse, ProjectWorkloadResponse, ProjectComprehensiveResponse
from utils.auth_utils import verify_token, get_current_user, check_analytics_permission, RolePermission
from utils.analytics_utils import generate_visualization_data

router = APIRouter()
security = HTTPBearer()

# Initialize services
progress_service = ProjectProgressAnalytics()
workload_service = ProjectWorkloadAnalytics()
comprehensive_service = ProjectComprehensiveAnalytics()

@router.get("/{project_id}/progress", response_model=ProjectProgressResponse)
async def get_project_progress(
    request: Request,
    project_id: str,
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get progress analytics for a specific project
    
    Parameters:
    - project_id: ID of the project to analyze
    - visualize: Whether to include visualization data
    
    Returns:
    - Project progress analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.PROJECT_ANALYTICS, 
        project_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this project's analytics"
        )
    
    # Get analytics report
    report = await progress_service.get_progress_report(project_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("progress", report.dict())
    
    return report

@router.get("/{project_id}/workload", response_model=ProjectWorkloadResponse)
async def get_project_workload(
    request: Request,
    project_id: str,
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get workload analytics for a specific project
    
    Parameters:
    - project_id: ID of the project to analyze
    - visualize: Whether to include visualization data
    
    Returns:
    - Project workload analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.PROJECT_ANALYTICS, 
        project_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this project's analytics"
        )
    
    # Get analytics report
    report = await workload_service.get_workload_report(project_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("workload", report.dict())
    
    return report

@router.get("/{project_id}/comprehensive", response_model=ProjectComprehensiveResponse)
async def get_project_comprehensive(
    request: Request,
    project_id: str,
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a specific project
    
    Parameters:
    - project_id: ID of the project to analyze
    - visualize: Whether to include visualization data
    
    Returns:
    - Project comprehensive analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.PROJECT_ANALYTICS, 
        project_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this project's analytics"
        )
    
    # Get analytics report
    report = await comprehensive_service.get_comprehensive_report(project_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("comprehensive", report.dict())
    
    return report

@router.get("/{project_id}", response_model=ProjectComprehensiveResponse)
async def get_project_analytics(
    request: Request,
    project_id: str,
    report_type: str = Query("comprehensive", description="Type of report (progress, workload, comprehensive)"),
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get analytics for a specific project
    
    Parameters:
    - project_id: ID of the project to analyze
    - report_type: Type of report (progress, workload, comprehensive)
    - visualize: Whether to include visualization data
    
    Returns:
    - Project analytics report
    """
    # Route to the appropriate endpoint based on report type
    if report_type == "progress":
        return await get_project_progress(request, project_id, visualize, current_user)
    elif report_type == "workload":
        return await get_project_workload(request, project_id, visualize, current_user)
    else:  # comprehensive or any other value
        return await get_project_comprehensive(request, project_id, visualize, current_user)