from typing import Dict, Any, List
from ...models.response_models import ProjectWorkloadResponse, TeamWorkload, ResourceAllocation
from ...utils.analytics_utils import identify_project_bottlenecks
from .project_analytics_strategy import ProjectAnalyticsStrategy

class WorkloadAnalyticsStrategy(ProjectAnalyticsStrategy[ProjectWorkloadResponse]):
    """Strategy for project workload analytics"""
    
    async def generate_report(self, project_id: str) -> ProjectWorkloadResponse:
        """Generate a workload report for a project"""
        # Try to get from cache
        cache_key = f"project_workload:{project_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return ProjectWorkloadResponse(**cached_report)
        
        # Get project data
        project = await self.data_access.get_project_by_id(project_id)
        if not project:
            return ProjectWorkloadResponse(
                success=False,
                message=f"Project with ID {project_id} not found",
                project_id=project_id,
                project_name=None,
                resource_allocation=ResourceAllocation()
            )
        
        # Get all subtasks for the project
        all_subtasks = await self.data_access.get_subtasks_by_project(project_id)
        
        # Filter for pending subtasks
        pending_subtasks = [task for task in all_subtasks if not task.get("completed", False)]
        
        # Get teams in the project
        project_teams = await self.data_access.get_teams_by_project(project_id)
        
        # Calculate project workload metrics
        total_estimated_hours = sum(task.get("estimated_hours", 0) for task in pending_subtasks)
        
        # Calculate team workloads
        team_workloads = {}
        teams_data = []  # For bottleneck analysis
        
        for team in project_teams:
            team_id = team.get("id")
            
            # Get team members
            team_members = await self.data_access.get_team_members(team_id)
            member_count = len(team_members)
            
            # Get subtasks for this team
            team_subtasks = [s for s in pending_subtasks if s.get("team_id") == team_id]
            team_pending = len(team_subtasks)
            team_hours = sum(s.get("estimated_hours", 0) for s in team_subtasks)
            
            # Calculate average hours per member
            avg_hours = team_hours / member_count if member_count > 0 else 0
            
            team_workloads[team_id] = TeamWorkload(
                pending_subtasks=team_pending,
                estimated_hours=team_hours,
                member_count=member_count,
                avg_hours_per_member=round(avg_hours, 2)
            )
            
            # Add team data for bottleneck analysis
            teams_data.append({
                "id": team_id,
                "name": team.get("name"),
                "members": team_members
            })
        
        # Identify resource allocation issues
        overallocated_teams = []
        underallocated_teams = []
        
        for team_id, workload in team_workloads.items():
            if workload.avg_hours_per_member > 40:  # Threshold for overallocation
                overallocated_teams.append(team_id)
            elif workload.avg_hours_per_member < 15 and workload.member_count > 0:  # Threshold for underallocation
                underallocated_teams.append(team_id)
        
        resource_allocation = ResourceAllocation(
            overallocated_teams=overallocated_teams,
            underallocated_teams=underallocated_teams
        )
        
        # Identify bottlenecks
        bottlenecks = identify_project_bottlenecks(teams_data, all_subtasks)
        
        # Create response
        response = ProjectWorkloadResponse(
            project_id=project_id,
            project_name=project.get("name"),
            pending_subtasks=len(pending_subtasks),
            total_estimated_hours=total_estimated_hours,
            team_workloads=team_workloads,
            resource_allocation=resource_allocation,
            bottlenecks=bottlenecks
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response