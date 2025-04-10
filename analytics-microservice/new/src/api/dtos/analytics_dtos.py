"""Data Transfer Objects for analytics API requests and responses."""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class CompletionRateResponseDto:
    """DTO for task completion rate response."""
    time_period_days: int
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate_percentage: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompletionRateResponseDto':
        """Create DTO from dictionary."""
        return cls(
            time_period_days=data.get('time_period_days', 0),
            total_tasks=data.get('total_tasks', 0),
            completed_tasks=data.get('completed_tasks', 0),
            pending_tasks=data.get('pending_tasks', 0),
            completion_rate_percentage=data.get('completion_rate_percentage', 0.0),
        )


@dataclass
class PendingWorkResponseDto:
    """DTO for pending work analysis response."""
    total_pending: int
    by_priority: Dict[str, int]
    overdue_tasks: int
    overdue_percentage: float
    average_days_pending: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PendingWorkResponseDto':
        """Create DTO from dictionary."""
        return cls(
            total_pending=data.get('total_pending', 0),
            by_priority=data.get('by_priority', {}),
            overdue_tasks=data.get('overdue_tasks', 0),
            overdue_percentage=data.get('overdue_percentage', 0.0),
            average_days_pending=data.get('average_days_pending', 0.0),
        )


@dataclass
class ProductivityMetricsResponseDto:
    """DTO for productivity metrics response."""
    time_period_days: int
    tasks_completed: int
    avg_completion_time_hours: float
    daily_completion: Dict[str, int]
    weekly_trends: Dict[str, int]
    average_daily_completion: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductivityMetricsResponseDto':
        """Create DTO from dictionary."""
        return cls(
            time_period_days=data.get('time_period_days', 0),
            tasks_completed=data.get('tasks_completed', 0),
            avg_completion_time_hours=data.get('avg_completion_time_hours', 0.0),
            daily_completion=data.get('daily_completion', {}),
            weekly_trends=data.get('weekly_trends', {}),
            average_daily_completion=data.get('average_daily_completion', 0.0),
        )


@dataclass
class TeamWorkloadResponseDto:
    """DTO for team workload response."""
    total_users: int
    total_tasks: int
    total_pending_tasks: int
    user_metrics: Dict[str, Dict[str, Any]]
    most_overloaded_user: Optional[str]
    least_loaded_user: Optional[str]
    workload_distribution: Dict[str, float]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamWorkloadResponseDto':
        """Create DTO from dictionary."""
        return cls(
            total_users=data.get('total_users', 0),
            total_tasks=data.get('total_tasks', 0),
            total_pending_tasks=data.get('total_pending_tasks', 0),
            user_metrics=data.get('user_metrics', {}),
            most_overloaded_user=data.get('most_overloaded_user'),
            least_loaded_user=data.get('least_loaded_user'),
            workload_distribution=data.get('workload_distribution', {}),
        )


@dataclass
class ProjectProgressResponseDto:
    """DTO for project progress response."""
    project_id: str
    project_name: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_percentage: float
    days_remaining: int
    milestone_status: Dict[str, Any]
    on_track: bool
    tasks_by_priority: Dict[str, int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectProgressResponseDto':
        """Create DTO from dictionary."""
        return cls(
            project_id=data.get('project_id', ''),
            project_name=data.get('project_name', ''),
            total_tasks=data.get('total_tasks', 0),
            completed_tasks=data.get('completed_tasks', 0),
            pending_tasks=data.get('pending_tasks', 0),
            completion_percentage=data.get('completion_percentage', 0.0),
            days_remaining=data.get('days_remaining', 0),
            milestone_status=data.get('milestone_status', {}),
            on_track=data.get('on_track', False),
            tasks_by_priority=data.get('tasks_by_priority', {}),
        )


@dataclass
class AnalyticsReportResponseDto:
    """DTO for complete analytics report response."""
    completion_rate: CompletionRateResponseDto
    pending_work: PendingWorkResponseDto
    productivity: ProductivityMetricsResponseDto
    team_workload: Optional[TeamWorkloadResponseDto]
    projects: Optional[Dict[str, Any]]
    generated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalyticsReportResponseDto':
        """Create DTO from dictionary."""
        completion_rate = CompletionRateResponseDto.from_dict(
            data.get('completion_rate', {})
        )
        pending_work = PendingWorkResponseDto.from_dict(
            data.get('pending_work', {})
        )
        productivity = ProductivityMetricsResponseDto.from_dict(
            data.get('productivity', {})
        )
        
        team_workload = None
        if 'team_workload' in data:
            team_workload = TeamWorkloadResponseDto.from_dict(data['team_workload'])
        
        return cls(
            completion_rate=completion_rate,
            pending_work=pending_work,
            productivity=productivity,
            team_workload=team_workload,
            projects=data.get('projects'),
            generated_at=data.get('generated_at', datetime.now().isoformat()),
        )