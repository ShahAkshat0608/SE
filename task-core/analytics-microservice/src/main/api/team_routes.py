from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.security import HTTPBearer
from typing import Dict, Optional

from services.team_analytics.progress import TeamProgressAnalytics
from services.team_analytics.workload import TeamWorkloadAnalytics
from services.team_analytics.comprehensive import TeamComprehensiveAnalytics
from models.response_models import TeamProgressResponse, TeamWorkloadResponse, TeamComprehensiveResponse
from utils.auth_utils import verify_token, get_current_user, check_analytics_permission, RolePermission
from utils.analytics_utils import generate_visualization_data

router = APIRouter()
security = HTTPBearer()

# Initialize services
progress_service = TeamProgressAnalytics()
workload_service = TeamWorkloadAnalytics()
comprehensive_service = TeamComprehensiveAnalytics()

@router.get("/{team_id}/progress", response_model=TeamProgressResponse)
async def get_team_progress(
    request: Request,
    team_id: str,
    project_id: str = Query(..., description="Project ID"),
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get progress analytics for a specific team
    
    Parameters:
    - team_id: ID of the team to analyze
    - project_id: ID of the project (required for team analytics)
    - visualize: Whether to include visualization data
    
    Returns:
    - Team progress analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.TEAM_ANALYTICS, 
        team_id,
        project_id=project_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this team's analytics"
        )
    
    # Get analytics report
    report = await progress_service.get_progress_report(team_id, project_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("progress", report.dict())
    
    return report

@router.get("/{team_id}/workload", response_model=TeamWorkloadResponse)
async def get_team_workload(
    request: Request,
    team_id: str,
    project_id: str = Query(..., description="Project ID"),
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get workload analytics for a specific team
    
    Parameters:
    - team_id: ID of the team to analyze
    - project_id: ID of the project (required for team analytics)
    - visualize: Whether to include visualization data
    
    Returns:
    - Team workload analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.TEAM_ANALYTICS, 
        team_id,
        project_id=project_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this team's analytics"
        )
    
    # Get analytics report
    report = await workload_service.get_workload_report(team_id, project_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("workload", report.dict())
    
    return report

@router.get("/{team_id}/comprehensive", response_model=TeamComprehensiveResponse)
async def get_team_comprehensive(
    request: Request,
    team_id: str,
    project_id: str = Query(..., description="Project ID"),
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a specific team
    
    Parameters:
    - team_id: ID of the team to analyze
    - project_id: ID of the project (required for team analytics)
    - visualize: Whether to include visualization data
    
    Returns:
    - Team comprehensive analytics report
    """
    # Check permissions
    has_permission = await check_analytics_permission(
        request, 
        RolePermission.TEAM_ANALYTICS, 
        team_id,
        project_id=project_id,
        current_user=current_user
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this team's analytics"
        )
    
    # Get analytics report
    report = await comprehensive_service.get_comprehensive_report(team_id, project_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("comprehensive", report.dict())
    
    return report

@router.get("/{team_id}", response_model=TeamComprehensiveResponse)
async def get_team_analytics(
    request: Request,
    team_id: str,
    project_id: str = Query(..., description="Project ID"),
    report_type: str = Query("comprehensive", description="Type of report (progress, workload, comprehensive)"),
    visualize: bool = Query(False, description="Include visualization data"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get analytics for a specific team
    
    Parameters:
    - team_id: ID of the team to analyze
    - project_id: ID of the project (required for team analytics)
    - report_type: Type of report (progress, workload, comprehensive)
    - visualize: Whether to include visualization data
    
    Returns:
    - Team analytics report
    """
    # Route to the appropriate endpoint based on report type
    if report_type == "progress":
        return await get_team_progress(request, team_id, project_id, visualize, current_user)
    elif report_type == "workload":
        return await get_team_workload(request, team_id, project_id, visualize, current_user)
    else:  # comprehensive or any other value
        return await get_team_comprehensive(request, team_id, project_id, visualize, current_user)