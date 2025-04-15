from typing import Dict, Any, List, Optional
from data.data_access_test import TestDataAccess
from data.cache import SimpleMemoryCache
from models.response_models import UserComprehensiveResponse, HistoricalPerformance, Recommendation
from utils.analytics_utils import generate_recommendations
from .progress import UserProgressAnalytics
from .workload import UserWorkloadAnalytics

class UserComprehensiveAnalytics:
    """Service for comprehensive user analytics"""
    
    def __init__(self):
        self.data_access = TestDataAccess()
        self.cache = SimpleMemoryCache()
        self.progress_analytics = UserProgressAnalytics()
        self.workload_analytics = UserWorkloadAnalytics()
    
    async def get_comprehensive_report(self, user_id: str) -> UserComprehensiveResponse:
        """Generate a comprehensive report for a user"""
        # Try to get from cache
        cache_key = f"user_comprehensive:{user_id}"
        cached_report = await self.cache.get(cache_key)
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
        
        # Get progress and workload reports
        progress_report = await self.progress_analytics.get_progress_report(user_id)
        workload_report = await self.workload_analytics.get_workload_report(user_id)
        
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
        await self.cache.set(cache_key, response.dict(), 300)  # Cache for 5 minutes
        
        return response