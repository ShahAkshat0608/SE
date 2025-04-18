from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from .enums import TaskStatus, TaskPriority

@dataclass
class Task:
    project_id: str
    team_id: str
    id: str = None
    name: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.TO_DO
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = None
    target_due_date: datetime = None
    assigned_team_id: str = None
    requirements: List[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = f"task-{str(uuid4())[:8]}"
        if not self.created_at:
            self.created_at = datetime.now()
        if self.requirements is None:
            self.requirements = []
            
        # Convert string to enum if needed
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)
        if isinstance(self.priority, str):
            self.priority = TaskPriority(self.priority)
        
    
    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "team_id": self.team_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at if self.created_at else None,
            "target_due_date": self.target_due_date if self.target_due_date else None,
            "assigned_team_id": self.assigned_team_id,
            "requirements": self.requirements
        }
    
    @staticmethod
    def from_dict(data):
        task = Task(
            id=data.get("id"),
            project_id=data.get("project_id"),
            team_id=data.get("team_id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            requirements=data.get("requirements", []),
            assigned_team_id=data.get("assigned_team_id"),
        )
        
        if data.get("status"):
            task.status = TaskStatus(data.get("status"))
            
        if data.get("priority"):
            task.priority = TaskPriority(data.get("priority"))
        
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data.get("created_at"))
        
        if data.get("target_due_date"):
            task.target_due_date = datetime.fromisoformat(data.get("target_due_date"))
            
        return task