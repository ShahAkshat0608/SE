"""Domain events for analytics functionality."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    
    event_id: str
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now()


@dataclass
class TaskCreatedEvent(DomainEvent):
    """Event fired when a new task is created."""
    
    task_id: str
    project_id: Optional[str]
    user_id: Optional[str]


@dataclass
class TaskCompletedEvent(DomainEvent):
    """Event fired when a task is marked as completed."""
    
    task_id: str
    project_id: Optional[str]
    user_id: Optional[str]
    completion_time: float  # Time in hours to complete


@dataclass
class ProjectProgressUpdatedEvent(DomainEvent):
    """Event fired when project progress is updated."""
    
    project_id: str
    completion_percentage: float
    on_track: bool


@dataclass
class AnalyticsReportGeneratedEvent(DomainEvent):
    """Event fired when an analytics report is generated."""
    
    report_type: str
    parameters: Dict[str, Any]
    generation_time: float  # Time in seconds to generate the report