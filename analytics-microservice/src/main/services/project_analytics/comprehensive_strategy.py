from typing import Dict, Any, List
from datetime import datetime
from ...models.response_models import ProjectComprehensiveResponse, TeamReport, ProjectHealth, Recommendation
from ...utils.analytics_utils import assess_project_health
from .project_analytics_strategy import ProjectAnalyticsStrategy
from .progress_strategy import ProgressAnalyticsStrategy
from .workload_strategy import WorkloadAnalyticsStrategy

class ComprehensiveAnalyticsStrategy(ProjectAnalyticsStrategy[ProjectComprehensiveResponse]):
    """Strategy for comprehensive project analytics"""
    
    def __init__(self):
        super().__init__()
        self.progress_strategy = ProgressAnalyticsStrategy()
        self.workload_strategy = WorkloadAnalyticsStrategy()
    
    async def generate_report(self, project_id: str) -> ProjectComprehensiveResponse:
        """Generate a comprehensive report for a project"""
        # Try to get from cache
        cache_key = f"project_comprehensive:{project_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return ProjectComprehensiveResponse(**cached_report)
        
        # Get project data
        project = await self.data_access.get_project_by_id(project_id)
        if not project:
            return ProjectComprehensiveResponse(
                success=False,
                message=f"Project with ID {project_id} not found",
                project_id=project_id,
                project_name=None,
                project_manager="Unknown",
                status="unknown",
                start_date=None,
                target_end_date=None,
                progress_stats={},
                workload_stats={},
                project_health=ProjectHealth(status="unknown")
            )
        
        # Get project manager details
        project_manager_id = project.get("project_manager_id")
        project_manager = await self.data_access.get_user_by_id(project_manager_id)
        project_manager_name = project_manager.get("name", "Unknown") if project_manager else "Unknown"
        
        # Get progress and workload reports using their respective strategies
        progress_report = await self.progress_strategy.generate_report(project_id)
        workload_report = await self.workload_strategy.generate_report(project_id)
        
        # Get teams in the project
        project_teams = await self.data_access.get_teams_by_project(project_id)
        
        # Generate team reports
        team_reports = {}
        for team in project_teams:
            team_id = team.get("id")
            team_name = team.get("name")
            
            if team_id in progress_report.team_stats and team_id in workload_report.team_workloads:
                team_progress = progress_report.team_stats[team_id]
                team_workload = workload_report.team_workloads[team_id]
                
                team_reports[team_id] = TeamReport(
                    name=team_name,
                    progress={
                        "completion_rate": team_progress.completion_rate,
                        "completed_tasks": team_progress.completed_subtasks,
                        "total_tasks": team_progress.total_subtasks
                    },
                    workload={
                        "pending_tasks": team_workload.pending_subtasks,
                        "estimated_hours": team_workload.estimated_hours,
                        "avg_hours_per_member": team_workload.avg_hours_per_member
                    }
                )
        
        # Assess project health
        project_health_assessment = assess_project_health(
            progress_report.dict(),
            workload_report.dict(),
            project
        )
        
        project_health = ProjectHealth(
            status=project_health_assessment.get("status"),
            issues=project_health_assessment.get("issues", [])
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(progress_report, workload_report, project)
        
        # Create response
        try:
            start_date = datetime.fromisoformat(project.get("start_date").replace('Z', '+00:00')) if project.get("start_date") else None
            target_end_date = datetime.fromisoformat(project.get("target_end_date").replace('Z', '+00:00')) if project.get("target_end_date") else None
        except (ValueError, AttributeError):
            start_date = None
            target_end_date = None
            
        response = ProjectComprehensiveResponse(
            project_id=project_id,
            project_name=project.get("name"),
            project_manager=project_manager_name,
            status=project.get("status"),
            start_date=datetime.now() if start_date is None else start_date,
            target_end_date=datetime.now() if target_end_date is None else target_end_date,
            progress_stats={
                "completion_rate": progress_report.completion_rate,
                "completed_subtasks": progress_report.completed_subtasks,
                "pending_subtasks": progress_report.pending_subtasks,
                "milestone_progress": progress_report.milestone_progress.dict(),
                "estimated_completion": progress_report.estimated_completion
            },
            workload_stats={
                "pending_subtasks": workload_report.pending_subtasks,
                "total_estimated_hours": workload_report.total_estimated_hours,
                "resource_allocation": workload_report.resource_allocation.dict(),
                "bottlenecks_count": len(workload_report.bottlenecks)
            },
            team_reports=team_reports,
            project_health=project_health,
            recommendations=recommendations
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response
        
    def _generate_recommendations(self, progress_report, workload_report, project) -> List[Recommendation]:
        """Generate recommendations based on project analytics"""
        recommendations = []
        
        # Check for resource allocation issues
        resource_allocation = workload_report.resource_allocation
        if resource_allocation.overallocated_teams:
            recommendations.append(Recommendation(
                type="resource",
                description=f"{len(resource_allocation.overallocated_teams)} teams are overallocated. Consider redistributing work or adding resources.",
                priority="high"
            ))
        
        if resource_allocation.underallocated_teams:
            recommendations.append(Recommendation(
                type="efficiency",
                description=f"{len(resource_allocation.underallocated_teams)} teams are underallocated. Consider optimizing resource allocation.",
                priority="medium"
            ))
        
        # Check completion rate
        if progress_report.completion_rate < 25 and project.get("status") != "planned":
            recommendations.append(Recommendation(
                type="progress",
                description=f"Project completion rate is only {progress_report.completion_rate}%. Consider reviewing timeline and resources.",
                priority="high"
            ))
        
        # Check for bottlenecks
        if workload_report.bottlenecks:
            high_severity = sum(1 for b in workload_report.bottlenecks if b.get("severity") == "high")
            if high_severity > 0:
                recommendations.append(Recommendation(
                    type="bottleneck",
                    description=f"Found {high_severity} high-severity bottlenecks. Address these to improve project flow.",
                    priority="high"
                ))
                
        return recommendations