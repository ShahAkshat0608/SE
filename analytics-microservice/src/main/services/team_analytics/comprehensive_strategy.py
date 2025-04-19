from typing import Dict, Any, List
from ...models.response_models import TeamComprehensiveResponse, Recommendation
from ...utils.analytics_utils import generate_team_recommendations
from .team_analytics_strategy import TeamAnalyticsStrategy
from .progress_strategy import ProgressAnalyticsStrategy
from .workload_strategy import WorkloadAnalyticsStrategy

class ComprehensiveAnalyticsStrategy(TeamAnalyticsStrategy[TeamComprehensiveResponse]):
    """Strategy for comprehensive team analytics"""
    
    def __init__(self):
        super().__init__()
        self.progress_strategy = ProgressAnalyticsStrategy()
        self.workload_strategy = WorkloadAnalyticsStrategy()
    
    async def generate_report(self, team_id: str, project_id: str) -> TeamComprehensiveResponse:
        """Generate a comprehensive report for a team"""
        # Try to get from cache
        cache_key = f"team_comprehensive:{team_id}:{project_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return TeamComprehensiveResponse(**cached_report)
        
        # Get team data
        team = await self.data_access.get_team_by_id(team_id)
        if not team:
            return TeamComprehensiveResponse(
                success=False,
                message=f"Team with ID {team_id} not found",
                team_id=team_id,
                team_name=None,
                project_id=project_id,
                progress_stats={},
                workload_stats={}
            )
        
        # Get progress and workload reports using their respective strategies
        progress_report = await self.progress_strategy.generate_report(team_id, project_id)
        workload_report = await self.workload_strategy.generate_report(team_id, project_id)
        
        # Generate member reports
        member_reports = {}
        for user_id, member_progress in progress_report.member_progress.items():
            if user_id in workload_report.member_workloads:
                member_workload = workload_report.member_workloads[user_id]
                member_reports[user_id] = {
                    "name": member_progress.user_name,
                    "progress": {
                        "completion_rate": member_progress.completion_rate,
                        "completed_tasks": member_progress.completed_subtasks,
                        "total_tasks": member_progress.total_subtasks
                    },
                    "workload": {
                        "pending_tasks": member_workload.pending_subtasks,
                        "estimated_hours": member_workload.estimated_hours,
                        "high_priority_tasks": member_workload.high_priority_tasks
                    }
                }
        
        # Generate risk assessment
        risk_assessment = []
        
        # Check for overallocated members
        for user_id, workload in workload_report.member_workloads.items():
            if workload.estimated_hours > 40:  # Threshold for overallocation
                risk_assessment.append({
                    "type": "overallocation",
                    "description": f"{workload.user_name} is overallocated with {workload.estimated_hours} hours of work"
                })
        
        # Check for low progress
        if progress_report.completion_rate < 30:
            risk_assessment.append({
                "type": "low_progress",
                "description": f"Team has low completion rate ({progress_report.completion_rate}%)"
            })
        
        # Generate recommendations
        team_recommendations = generate_team_recommendations(
            progress_report.dict(),
            workload_report.dict()
        )
        
        # Create response
        response = TeamComprehensiveResponse(
            team_id=team_id,
            team_name=team.get("name"),
            project_id=project_id,
            progress_stats={
                "completion_rate": progress_report.completion_rate,
                "completed_subtasks": progress_report.completed_subtasks,
                "pending_subtasks": progress_report.pending_subtasks,
                "milestone_progress": progress_report.milestone_progress.dict()
            },
            workload_stats={
                "pending_subtasks": workload_report.pending_subtasks,
                "total_estimated_hours": workload_report.total_estimated_hours,
                "workload_balance": workload_report.workload_balance,
                "workload_distribution": workload_report.workload_distribution.dict()
            },
            member_reports=member_reports,
            risk_assessment=risk_assessment,
            recommended_actions=[Recommendation(**rec) for rec in team_recommendations]
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response