from typing import Dict, Any, List
from ...models.response_models import TeamWorkloadResponse, MemberWorkload, WorkloadDistribution
from ...utils.analytics_utils import calculate_workload_balance, calculate_workload_distribution
from .team_analytics_strategy import TeamAnalyticsStrategy

class WorkloadAnalyticsStrategy(TeamAnalyticsStrategy[TeamWorkloadResponse]):
    """Strategy for team workload analytics"""
    
    async def generate_report(self, team_id: str, project_id: str) -> TeamWorkloadResponse:
        """Generate a workload report for a team"""
        # Try to get from cache
        cache_key = f"team_workload:{team_id}:{project_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return TeamWorkloadResponse(**cached_report)
        
        # Get team data
        team = await self.data_access.get_team_by_id(team_id)
        if not team:
            return TeamWorkloadResponse(
                success=False,
                message=f"Team with ID {team_id} not found",
                team_id=team_id,
                team_name=None,
                project_id=project_id,
                workload_distribution=WorkloadDistribution()
            )
        
        # Get all subtasks for the team in this project
        subtasks = await self.data_access.get_subtasks_by_team(team_id, project_id)
        
        # Filter for pending subtasks
        pending_subtasks = [task for task in subtasks if not task.get("completed", False)]
        
        # Get team members
        team_members = await self.data_access.get_team_members(team_id)
        
        # Calculate team workload metrics
        total_estimated_hours = sum(task.get("estimated_hours", 0) for task in pending_subtasks)
        
        # Calculate member workloads
        member_workloads = {}
        # Add a check to prevent None values in user_id
        for member in team_members:
            user_id = member.get("user_id")
            user_name = member.get("name")
            
            # Skip if user_id is None
            if user_id is None:
                continue
            
            # Get subtasks assigned to this team member
            member_subtasks = [s for s in pending_subtasks if s.get("assigned_to") == user_id]
            member_pending = len(member_subtasks)
            member_hours = sum(s.get("estimated_hours", 0) for s in member_subtasks)
            member_high_priority = sum(1 for s in member_subtasks if s.get("priority") == "high")
            
            member_workloads[user_id] = MemberWorkload(
                user_id=user_id,
                user_name=user_name,
                pending_subtasks=member_pending,
                estimated_hours=member_hours,
                high_priority_tasks=member_high_priority
            )
        
        # Calculate workload distribution and balance
        workload_distribution_dict = calculate_workload_distribution(team_members, pending_subtasks)
        workload_distribution = WorkloadDistribution(**workload_distribution_dict)
        
        workload_balance = calculate_workload_balance(member_workloads)
        
        # Create response
        response = TeamWorkloadResponse(
            team_id=team_id,
            team_name=team.get("name"),
            project_id=project_id,
            pending_subtasks=len(pending_subtasks),
            total_estimated_hours=total_estimated_hours,
            member_workloads=member_workloads,
            workload_distribution=workload_distribution,
            workload_balance=workload_balance
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response