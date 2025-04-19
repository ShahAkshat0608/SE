from typing import Dict, Any, List
from ...models.response_models import UserProgressResponse, UserSubtaskDetail
from ...utils.analytics_utils import calculate_completion_rate
from .user_analytics_strategy import UserAnalyticsStrategy
from datetime import datetime

class ProgressAnalyticsStrategy(UserAnalyticsStrategy[UserProgressResponse]):
    """Strategy for user progress analytics"""
    
    async def generate_report(self, user_id: str) -> UserProgressResponse:
        """Generate a progress report for a user"""
        # Try to get from cache
        cache_key = f"user_progress:{user_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return UserProgressResponse(**cached_report)
        
        # Get user data
        user = await self.data_access.get_user_by_id(user_id)
        if not user:
            return UserProgressResponse(
                success=False,
                message=f"User with ID {user_id} not found",
                user_id=user_id,
                user_name=None
            )
        
        # Get all subtasks assigned to the user
        subtasks = await self.data_access.get_subtasks_by_user(user_id)
        
        # Calculate progress metrics
        total_subtasks = len(subtasks)
        completed_subtasks = sum(1 for task in subtasks if task.get("completed", False))
        pending_subtasks = total_subtasks - completed_subtasks
        completion_rate = calculate_completion_rate(completed_subtasks, total_subtasks)
        
        # Calculate on-time vs late completions
        # Note: This is a simplified implementation as example.json doesn't have completion_date
        on_time_completions = completed_subtasks  # Placeholder
        late_completions = 0  # Placeholder
        
        # Create subtask details
        subtask_details = []
        for subtask in subtasks:
            # Handle ISO datetime format
            due_date_str = subtask.get("due_date", "")
            try:
                if due_date_str:
                    # Handle 'Z' in ISO format by replacing with '+00:00'
                    if due_date_str.endswith('Z'):
                        due_date_str = due_date_str[:-1] + '+00:00'
                    due_date = datetime.fromisoformat(due_date_str)
                else:
                    due_date = datetime.now()
            except ValueError:
                due_date = datetime.now()
                
            subtask_details.append(
                UserSubtaskDetail(
                    id=subtask.get("id"),
                    description=subtask.get("description"),
                    priority=subtask.get("priority"),
                    due_date=due_date,
                    completed=subtask.get("completed", False),
                    estimated_hours=subtask.get("estimated_hours", 0),
                    tags=[]
                )
            )
        
        # Create response
        response = UserProgressResponse(
            user_id=user_id,
            user_name=user.get("name"),
            total_subtasks=total_subtasks,
            completed_subtasks=completed_subtasks,
            pending_subtasks=pending_subtasks,
            completion_rate=completion_rate,
            on_time_completions=on_time_completions,
            late_completions=late_completions,
            subtask_details=subtask_details
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response