from typing import Dict, Any, List
from ...models.response_models import TeamProgressResponse, MemberProgress, MilestoneProgress, MilestonesProgress
from ...utils.analytics_utils import calculate_completion_rate, calculate_milestone_completion
from .team_analytics_strategy import TeamAnalyticsStrategy

class ProgressAnalyticsStrategy(TeamAnalyticsStrategy[TeamProgressResponse]):
    """Strategy for team progress analytics"""
    
    async def generate_report(self, team_id: str, project_id: str) -> TeamProgressResponse:
        """Generate a progress report for a team"""
        # Try to get from cache
        cache_key = f"team_progress:{team_id}:{project_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return TeamProgressResponse(**cached_report)
        
        # Get team data
        team = await self.data_access.get_team_by_id(team_id)
        if not team:
            return TeamProgressResponse(
                success=False,
                message=f"Team with ID {team_id} not found",
                team_id=team_id,
                team_name=None,
                project_id=project_id,
                milestone_progress=MilestonesProgress()
            )
        
        # Get all subtasks for the team in this project
        subtasks = await self.data_access.get_subtasks_by_team(team_id, project_id)
        
        # Get team members
        team_members = await self.data_access.get_team_members(team_id)
        
        # Calculate team progress metrics
        total_subtasks = len(subtasks)
        completed_subtasks = sum(1 for task in subtasks if task.get("completed", False))
        pending_subtasks = total_subtasks - completed_subtasks
        completion_rate = calculate_completion_rate(completed_subtasks, total_subtasks)
        
        # Calculate member progress
        member_progress = {}
        # Add a check to prevent None values in user_id
        for member in team_members:
            user_id = member.get("user_id")
            user_name = member.get("name")
            
            # Skip if user_id is None
            if user_id is None:
                continue
            
            # Get subtasks assigned to this team member
            member_subtasks = [s for s in subtasks if s.get("assigned_to") == user_id]
            member_total = len(member_subtasks)
            member_completed = sum(1 for s in member_subtasks if s.get("completed", False))
            member_rate = calculate_completion_rate(member_completed, member_total)
            
            member_progress[user_id] = MemberProgress(
                user_id=user_id,
                user_name=user_name,
                total_subtasks=member_total,
                completed_subtasks=member_completed,
                completion_rate=member_rate
            )
        
        # Calculate milestone progress
        milestones = await self.data_access.get_milestones_by_project(project_id)
        milestone_completions = calculate_milestone_completion(milestones, subtasks)
        
        milestones_progress = MilestonesProgress(
            milestones=[
                MilestoneProgress(
                    id=m.get("id"),
                    name=m.get("name"),
                    completion_rate=m.get("completion_rate", 0)
                ) for m in milestone_completions
            ]
        )
        
        # Create response
        response = TeamProgressResponse(
            team_id=team_id,
            team_name=team.get("name"),
            project_id=project_id,
            total_subtasks=total_subtasks,
            completed_subtasks=completed_subtasks,
            pending_subtasks=pending_subtasks,
            completion_rate=completion_rate,
            member_progress=member_progress,
            milestone_progress=milestones_progress
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response