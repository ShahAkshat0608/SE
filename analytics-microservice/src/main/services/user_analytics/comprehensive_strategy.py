from typing import Dict, Any, List
from ...models.response_models import UserComprehensiveResponse, HistoricalPerformance, Recommendation
from ...utils.analytics_utils import generate_recommendations
from .user_analytics_strategy import UserAnalyticsStrategy
from .progress_strategy import ProgressAnalyticsStrategy
from .workload_strategy import WorkloadAnalyticsStrategy

class ComprehensiveAnalyticsStrategy(UserAnalyticsStrategy[UserComprehensiveResponse]):
    """Strategy for comprehensive user analytics"""
    
    def __init__(self):
        super().__init__()
        self.progress_strategy = ProgressAnalyticsStrategy()
        self.workload_strategy = WorkloadAnalyticsStrategy()
    
    async def generate_report(self, user_id: str) -> UserComprehensiveResponse:
        """Generate a comprehensive report for a user"""
        # Try to get from cache
        cache_key = f"user_comprehensive:{user_id}"
        cached_report = await self.get_cached_report(cache_key)
        if cached_report:
            return UserComprehensiveResponse(**cached_report)
        
        # Get user data
        user = await self.data_access.get_user_by_id(user_id)
        if not user:
            return UserComprehensiveResponse(
                success=False,
                message=f"User with ID {user_id} not found",
                user_id=user_id,
                user_name=None,
                progress_stats={},
                workload_stats={}
            )
        
        # Get progress and workload reports using their respective strategies
        progress_report = await self.progress_strategy.generate_report(user_id)
        workload_report = await self.workload_strategy.generate_report(user_id)
        
        # Calculate historical performance (simplified for now)
        historical_performance = HistoricalPerformance(
            avg_completion_time=3.5,  # Placeholder value
            on_time_percentage=80.0,  # Placeholder value
            tasks_completed_per_week=4.2  # Placeholder value
        )
        
        # Generate recommendations based on data
        recommendations = generate_recommendations(user, progress_report.dict(), workload_report.dict())
        
        # Create response
        response = UserComprehensiveResponse(
            user_id=user_id,
            user_name=user.get("name"),
            progress_stats={
                "completion_rate": progress_report.completion_rate,
                "completed_subtasks": progress_report.completed_subtasks,
                "pending_subtasks": progress_report.pending_subtasks,
                "on_time_completions": progress_report.on_time_completions,
                "late_completions": progress_report.late_completions
            },
            workload_stats={
                "pending_subtasks": workload_report.pending_subtasks,
                "estimated_hours": workload_report.total_estimated_hours,
                "priority_distribution": workload_report.priority_distribution.dict(),
                "upcoming_deadlines": {
                    "this_week": workload_report.due_this_week,
                    "this_month": workload_report.due_this_month,
                    "later": workload_report.due_later
                }
            },
            historical_performance=historical_performance,
            recommendations=[Recommendation(**rec) for rec in recommendations]
        )
        
        # Cache the response
        await self.cache_report(cache_key, response.dict())
        
        return response