from typing import Dict, Any, List
from ...models.response_models import ProjectProgressResponse, TeamStat, MilestoneProgress, MilestonesProgress
from ...utils.analytics_utils import calculate_completion_rate, calculate_milestone_completion, calculate_estimated_completion_date
from .project_analytics_strategy import ProjectAnalyticsStrategy
from datetime import datetime

class ProgressAnalyticsStrategy(ProjectAnalyticsStrategy[ProjectProgressResponse]):
    """Strategy for project progress analytics"""
    
    async def generate_report(self, project_id: str) -> ProjectProgressResponse:
        """Generate a progress report for a project"""
        # Try to get from cache
        
        cache_key = f"project_progress:{project_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return ProjectProgressResponse(**cached_report)
        
        
        # Get project data
        project = await self.data_access.get_project_by_id(project_id)
        if not project:
            return ProjectProgressResponse(
                success=False,
                message=f"Project with ID {project_id} not found",
                project_id=project_id,
                project_name=None,
                milestone_progress=MilestonesProgress()
            )
        
        # Get all subtasks for the project
        subtasks = await self.data_access.get_subtasks_by_project(project_id)
        
        # Get teams in the project
        project_teams = await self.data_access.get_teams_by_project(project_id)
        
        # Calculate project progress metrics
        total_subtasks = len(subtasks)
        completed_subtasks = sum(1 for task in subtasks if task.get("completed", False))
        pending_subtasks = total_subtasks - completed_subtasks
        completion_rate = calculate_completion_rate(completed_subtasks, total_subtasks)
        
        # Calculate team stats
        team_stats = {}
        for team in project_teams:
            team_id = team.get("id")
            
            # Get subtasks for this team
            team_subtasks = [s for s in subtasks if s.get("team_id") == team_id]
            team_total = len(team_subtasks)
            team_completed = sum(1 for s in team_subtasks if s.get("completed", False))
            team_completion = calculate_completion_rate(team_completed, team_total)
            
            team_stats[team_id] = TeamStat(
                total_subtasks=team_total,
                completed_subtasks=team_completed,
                completion_rate=team_completion
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
        
        # Calculate estimated completion
        estimated_completion = calculate_estimated_completion_date(project, completed_subtasks, total_subtasks)
        
        # Create response
        response = ProjectProgressResponse(
            project_id=project_id,
            project_name=project.get("name"),
            total_subtasks=total_subtasks,
            completed_subtasks=completed_subtasks,
            pending_subtasks=pending_subtasks,
            completion_rate=completion_rate,
            team_stats=team_stats,
            milestone_progress=milestones_progress,
            estimated_completion=estimated_completion
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response