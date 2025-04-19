from typing import Dict, Any, Optional
from enum import Enum

from ..services.project_analytics.project_analytics_strategy import ProjectAnalyticsContext
from ..services.project_analytics.progress_strategy import ProgressAnalyticsStrategy as ProjectProgressStrategy
from ..services.project_analytics.workload_strategy import WorkloadAnalyticsStrategy as ProjectWorkloadStrategy
from ..services.project_analytics.comprehensive_strategy import ComprehensiveAnalyticsStrategy as ProjectComprehensiveStrategy

from ..services.team_analytics.team_analytics_strategy import TeamAnalyticsContext
from ..services.team_analytics.progress_strategy import ProgressAnalyticsStrategy as TeamProgressStrategy
from ..services.team_analytics.workload_strategy import WorkloadAnalyticsStrategy as TeamWorkloadStrategy
from ..services.team_analytics.comprehensive_strategy import ComprehensiveAnalyticsStrategy as TeamComprehensiveStrategy

from ..services.user_analytics.user_analytics_strategy import UserAnalyticsContext
from ..services.user_analytics.progress_strategy import ProgressAnalyticsStrategy as UserProgressStrategy
from ..services.user_analytics.workload_strategy import WorkloadAnalyticsStrategy as UserWorkloadStrategy
from ..services.user_analytics.comprehensive_strategy import ComprehensiveAnalyticsStrategy as UserComprehensiveStrategy

from ..utils.analytics_utils import generate_visualization_data


class ReportType(str, Enum):
    """Enum representing the different types of analytics reports"""
    PROGRESS = "progress"
    WORKLOAD = "workload"
    COMPREHENSIVE = "comprehensive"


class AnalyticsFacade:
    """
    Facade that provides a simplified interface for generating analytics across
    different entity types (projects, teams, users)
    """
    
    def __init__(self):
        # Initialize contexts
        self.project_context = ProjectAnalyticsContext(None)
        self.team_context = TeamAnalyticsContext(None)
        self.user_context = UserAnalyticsContext(None)
    
    async def generate_project_analytics(
        self, 
        project_id: str, 
        report_type: str = ReportType.COMPREHENSIVE, 
        visualize: bool = False
    ):
        """Generate analytics for a project"""
        # Select and apply the appropriate strategy
        if report_type == ReportType.PROGRESS:
            self.project_context.set_strategy(ProjectProgressStrategy())
        elif report_type == ReportType.WORKLOAD:
            self.project_context.set_strategy(ProjectWorkloadStrategy())
        else:  # Default to comprehensive
            self.project_context.set_strategy(ProjectComprehensiveStrategy())
        
        # Generate the report
        report = await self.project_context.generate_report(project_id)
       
        # Add visualizations if requested
        if visualize and hasattr(report, "dict"):
            report.visualizations = generate_visualization_data(report_type, report.dict())

        return report
    
    async def generate_team_analytics(
        self, 
        team_id: str, 
        project_id: str, 
        report_type: str = ReportType.COMPREHENSIVE, 
        visualize: bool = False
    ):
        """Generate analytics for a team"""
        # Select and apply the appropriate strategy
        if report_type == ReportType.PROGRESS:
            self.team_context.set_strategy(TeamProgressStrategy())
        elif report_type == ReportType.WORKLOAD:
            self.team_context.set_strategy(TeamWorkloadStrategy())
        else:  # Default to comprehensive
            self.team_context.set_strategy(TeamComprehensiveStrategy())
        
        # Generate the report
        report = await self.team_context.generate_report(team_id, project_id)
        
        # Add visualizations if requested
        if visualize and hasattr(report, "dict"):
            report.visualizations = generate_visualization_data(report_type, report.dict())
        
        return report
    
    async def generate_user_analytics(
        self, 
        user_id: str, 
        report_type: str = ReportType.COMPREHENSIVE, 
        visualize: bool = False
    ):
        """Generate analytics for a user"""
        # Select and apply the appropriate strategy
        if report_type == ReportType.PROGRESS:
            self.user_context.set_strategy(UserProgressStrategy())
        elif report_type == ReportType.WORKLOAD:
            self.user_context.set_strategy(UserWorkloadStrategy())
        else:  # Default to comprehensive
            self.user_context.set_strategy(UserComprehensiveStrategy())
        
        # Generate the report
        report = await self.user_context.generate_report(user_id)
        
        # Add visualizations if requested
        if visualize and hasattr(report, "dict"):
            report.visualizations = generate_visualization_data(report_type, report.dict())
        
        return report