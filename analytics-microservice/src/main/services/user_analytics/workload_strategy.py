from typing import Dict, Any, List
from ...models.response_models import UserWorkloadResponse, UserSubtaskDetail, PriorityDistribution
from ...utils.analytics_utils import group_subtasks_by_priority, calculate_due_dates_distribution
from .user_analytics_strategy import UserAnalyticsStrategy
from datetime import datetime

class WorkloadAnalyticsStrategy(UserAnalyticsStrategy[UserWorkloadResponse]):
    """Strategy for user workload analytics"""
    
    async def generate_report(self, user_id: str) -> UserWorkloadResponse:
        """Generate a workload report for a user"""
        # Try to get from cache
        cache_key = f"user_workload:{user_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return UserWorkloadResponse(**cached_report)
        
        # Get user data
        user = await self.data_access.get_user_by_id(user_id)
        if not user:
            return UserWorkloadResponse(
                success=False,
                message=f"User with ID {user_id} not found",
                user_id=user_id,
                user_name=None,
                priority_distribution=PriorityDistribution()
            )
        
        # Get all subtasks assigned to the user
        all_subtasks = await self.data_access.get_subtasks_by_user(user_id)
        
        # Filter for pending subtasks
        pending_subtasks = [task for task in all_subtasks if not task.get("completed", False)]
        
        # Calculate workload metrics
        total_estimated_hours = sum(task.get("estimated_hours", 0) for task in pending_subtasks)
        priority_distribution_dict = group_subtasks_by_priority(pending_subtasks)
        priority_distribution = PriorityDistribution(**priority_distribution_dict)
        
        # Calculate due date distribution
        due_dates = calculate_due_dates_distribution(pending_subtasks)
        
        # Create subtask details
        workload_details = []
        for subtask in pending_subtasks:
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
                
            workload_details.append(
                UserSubtaskDetail(
                    id=subtask.get("id"),
                    description=subtask.get("description"),
                    priority=subtask.get("priority"),
                    due_date=due_date,
                    completed=False,
                    estimated_hours=subtask.get("estimated_hours", 0),
                    tags=[]
                )
            )
        
        # Create response
        response = UserWorkloadResponse(
            user_id=user_id,
            user_name=user.get("name"),
            pending_subtasks=len(pending_subtasks),
            total_estimated_hours=total_estimated_hours,
            priority_distribution=priority_distribution,
            due_this_week=due_dates["this_week"],
            due_this_month=due_dates["this_month"],
            due_later=due_dates["later"],
            workload_details=workload_details
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response