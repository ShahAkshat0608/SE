from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime

class AnalyticsLevel(str, Enum):
    USER = "user"
    TEAM = "team"
    PROJECT = "project"

class AnalyticsType(str, Enum):
    PROGRESS = "progress"
    WORKLOAD = "workload"
    COMPREHENSIVE = "comprehensive"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ProjectStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class SubtaskModel:
    def __init__(
        self,
        id: str,
        task_id: str,
        description: str,
        priority: str,
        due_date: datetime,
        completed: bool,
        created_at: datetime,
        assigned: bool,
        assigned_to: str,
        project_id: str,
        estimated_hours: float,
        tags: List[str],
        dependency_parent_id: Optional[str] = None,
        milestone_id: Optional[str] = None
    ):
        self.id = id
        self.task_id = task_id
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.created_at = created_at
        self.assigned = assigned
        self.assigned_to = assigned_to
        self.project_id = project_id
        self.estimated_hours = estimated_hours
        self.tags = tags
        self.dependency_parent_id = dependency_parent_id
        self.milestone_id = milestone_id

class UserModel:
    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        contact: str
    ):
        self.id = id
        self.name = name
        self.email = email
        self.contact = contact

class TeamMemberModel:
    def __init__(
        self,
        team_id: str,
        user_id: str,
        joined_at: datetime
    ):
        self.team_id = team_id
        self.user_id = user_id
        self.joined_at = joined_at

class TeamModel:
    def __init__(
        self,
        id: str,
        name: str,
        project_id: str,
        team_lead_id: str,
        created_at: datetime
    ):
        self.id = id
        self.name = name
        self.project_id = project_id
        self.team_lead_id = team_lead_id
        self.created_at = created_at

class TaskModel:
    def __init__(
        self,
        id: str,
        project_id: str,
        team_id: str,
        created_at: datetime,
        target_due_date: datetime
    ):
        self.id = id
        self.project_id = project_id
        self.team_id = team_id
        self.created_at = created_at
        self.target_due_date = target_due_date

class MilestoneModel:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        project_id: str,
        due_date: datetime,
        sequence_no: int,
        created_at: datetime,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.project_id = project_id
        self.due_date = due_date
        self.sequence_no = sequence_no
        self.created_at = created_at
        self.updated_at = updated_at

class ProjectModel:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        status: str,
        start_date: datetime,
        target_end_date: datetime,
        project_manager_id: str,
        completion_percentage: float,
        created_at: datetime,
        updated_at: datetime,
        priority: str,
        client: str,
        department: str
    ):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.start_date = start_date
        self.target_end_date = target_end_date
        self.project_manager_id = project_manager_id
        self.completion_percentage = completion_percentage
        self.created_at = created_at
        self.updated_at = updated_at
        self.priority = priority
        self.client = client
        self.department = department