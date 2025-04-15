from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from .enums import ProjectStatus, TaskPriority

@dataclass
class Project:
    name: str
    description: str
    status: ProjectStatus
    start_date: datetime
    target_end_date: Optional[datetime]
    project_manager_id: str  # Necessary user id
    priority: TaskPriority
    client: Optional[str] = None
    department: Optional[str] = None
    id: str = None
    completion_percentage: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if not self.id:
            self.id = f"project-{str(uuid4())[:8]}"
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = datetime.now()
            
        # Convert string to enum if needed
        if isinstance(self.status, str):
            self.status = ProjectStatus(self.status)
        if isinstance(self.priority, str):
            self.priority = TaskPriority(self.priority)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "start_date": self.start_date.isoformat(),
            "target_end_date": self.target_end_date.isoformat() if self.target_end_date else None,
            "project_manager_id": self.project_manager_id,
            "completion_percentage": self.completion_percentage,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "priority": self.priority.value,
            "client": self.client,
            "department": self.department
        }
        
    @staticmethod
    def from_dict(data):
        return Project(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            status=ProjectStatus(data.get("status")),
            start_date=datetime.fromisoformat(data.get("start_date")),
            target_end_date=datetime.fromisoformat(data.get("target_end_date")) if data.get("target_end_date") else None,
            project_manager_id=data.get("project_manager_id"),
            priority=TaskPriority(data.get("priority")),
            client=data.get("client"),
            department=data.get("department"),
            completion_percentage=data.get("completion_percentage", 0.0),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data.get("updated_at")) if data.get("updated_at") else None
        )