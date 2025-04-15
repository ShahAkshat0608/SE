from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from .analytics_models import AnalyticsType, AnalyticsLevel, Priority, ProjectStatus

# Base response models
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None

# User Analytics Response Models
class UserSubtaskDetail(BaseModel):
    id: str
    description: str
    priority: str
    due_date: datetime
    completed: bool
    estimated_hours: float
    tags: List[str]

class UserProgressResponse(BaseResponse):
    user_id: str
    user_name: Optional[str]
    total_subtasks: int = 0
    completed_subtasks: int = 0
    pending_subtasks: int = 0
    completion_rate: float = 0
    on_time_completions: int = 0
    late_completions: int = 0
    subtask_details: List[UserSubtaskDetail] = []
    visualizations: Optional[Dict[str, Any]] = None

class PriorityDistribution(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0

class UserWorkloadResponse(BaseResponse):
    user_id: str
    user_name: Optional[str]
    pending_subtasks: int = 0
    total_estimated_hours: float = 0
    priority_distribution: PriorityDistribution
    due_this_week: int = 0
    due_this_month: int = 0
    due_later: int = 0
    workload_details: List[UserSubtaskDetail] = []
    visualizations: Optional[Dict[str, Any]] = None

class HistoricalPerformance(BaseModel):
    avg_completion_time: float = 0
    on_time_percentage: float = 0
    tasks_completed_per_week: float = 0

class Recommendation(BaseModel):
    type: str
    description: str
    priority: str

class UserComprehensiveResponse(BaseResponse):
    user_id: str
    user_name: Optional[str]
    progress_stats: Dict[str, Any]
    workload_stats: Dict[str, Any]
    historical_performance: Optional[HistoricalPerformance] = None
    recommendations: List[Recommendation] = []
    visualizations: Optional[Dict[str, Any]] = None

# Team Analytics Response Models
class MilestoneProgress(BaseModel):
    id: str
    name: str
    completion_rate: float

class MilestonesProgress(BaseModel):
    milestones: List[MilestoneProgress] = []

class MemberProgress(BaseModel):
    user_id: str
    user_name: Optional[str]
    total_subtasks: int = 0
    completed_subtasks: int = 0
    completion_rate: float = 0

class TeamProgressResponse(BaseResponse):
    team_id: str
    team_name: Optional[str]
    project_id: str
    total_subtasks: int = 0
    completed_subtasks: int = 0
    pending_subtasks: int = 0
    completion_rate: float = 0
    member_progress: Dict[str, MemberProgress] = {}
    milestone_progress: MilestonesProgress
    visualizations: Optional[Dict[str, Any]] = None

class MemberWorkload(BaseModel):
    user_id: str
    user_name: Optional[str]
    pending_subtasks: int = 0
    estimated_hours: float = 0
    high_priority_tasks: int = 0

class WorkloadDistribution(BaseModel):
    overallocated: int = 0
    balanced: int = 0
    underallocated: int = 0

class TeamWorkloadResponse(BaseResponse):
    team_id: str
    team_name: Optional[str]
    project_id: str
    pending_subtasks: int = 0
    total_estimated_hours: float = 0
    member_workloads: Dict[str, MemberWorkload] = {}
    workload_distribution: WorkloadDistribution
    workload_balance: float = 0.0
    visualizations: Optional[Dict[str, Any]] = None

class TeamComprehensiveResponse(BaseResponse):
    team_id: str
    team_name: Optional[str]
    project_id: str
    progress_stats: Dict[str, Any]
    workload_stats: Dict[str, Any]
    member_reports: Dict[str, Dict[str, Any]] = {}
    risk_assessment: List[Dict[str, str]] = []
    recommended_actions: List[Recommendation] = []
    visualizations: Optional[Dict[str, Any]] = None

# Project Analytics Response Models
class TeamStat(BaseModel):
    total_subtasks: int = 0
    completed_subtasks: int = 0
    completion_rate: float = 0

class ProjectProgressResponse(BaseResponse):
    project_id: str
    project_name: Optional[str]
    total_subtasks: int = 0
    completed_subtasks: int = 0
    pending_subtasks: int = 0
    completion_rate: float = 0
    team_stats: Dict[str, TeamStat] = {}
    milestone_progress: MilestonesProgress
    estimated_completion: Optional[datetime] = None
    visualizations: Optional[Dict[str, Any]] = None

class TeamWorkload(BaseModel):
    pending_subtasks: int = 0
    estimated_hours: float = 0
    member_count: int = 0
    avg_hours_per_member: float = 0

class ResourceAllocation(BaseModel):
    overallocated_teams: List[str] = []
    underallocated_teams: List[str] = []

class ProjectWorkloadResponse(BaseResponse):
    project_id: str
    project_name: Optional[str]
    pending_subtasks: int = 0
    total_estimated_hours: float = 0
    team_workloads: Dict[str, TeamWorkload] = {}
    resource_allocation: ResourceAllocation
    bottlenecks: List[Dict[str, str]] = []
    visualizations: Optional[Dict[str, Any]] = None

class ProjectHealth(BaseModel):
    status: str
    issues: List[str] = []

class TeamReport(BaseModel):
    name: str
    progress: Dict[str, Any]
    workload: Dict[str, Any]

class ProjectComprehensiveResponse(BaseResponse):
    project_id: str
    project_name: Optional[str]
    project_manager: str
    status: str
    start_date: datetime
    target_end_date: datetime
    progress_stats: Dict[str, Any]
    workload_stats: Dict[str, Any]
    team_reports: Dict[str, TeamReport] = {}
    project_health: ProjectHealth
    recommendations: List[Recommendation] = []
    visualizations: Optional[Dict[str, Any]] = None