from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from .enums import SubtaskPriority

@dataclass
class Subtask:
    name: str
    task_id: str
    description: str
    project_id: str
    priority: SubtaskPriority = SubtaskPriority.MEDIUM
    id: str = None
    due_date: Optional[datetime] = None
    completed: bool = False
    created_at: datetime = None
    assigned: bool = False
    assigned_to: Optional[str] = None
    estimated_hours: float = 0
    parent_subtask_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    milestone_id: Optional[str] = None
    is_completed: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = f"subtask-{str(uuid4())[:8]}"
        if not self.created_at:
            self.created_at = datetime.now()
            
        # Convert string to enum if needed
        if isinstance(self.priority, str):
            self.priority = SubtaskPriority(self.priority)
    
    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "assigned": self.assigned,
            "assigned_to": self.assigned_to,
            "estimated_hours": self.estimated_hours,
            "parent_subtask_id": self.parent_subtask_id,
            "tags": self.tags,
            "milestone_id": self.milestone_id,
            "is_completed": self.is_completed
        }
    
    @staticmethod
    def from_dict(data):
        subtask = Subtask(
            id=data.get("id"),
            name = data.get("name"),
            task_id=data.get("task_id"),
            description=data.get("description"),
            project_id=data.get("project_id"),
            completed=data.get("completed", False),
            assigned=data.get("assigned", False),
            assigned_to=data.get("assigned_to"),
            estimated_hours=data.get("estimated_hours", 0),
            parent_subtask_id=data.get("parent_subtask_id"),
            tags=data.get("tags", []),
            milestone_id=data.get("milestone_id"),
            is_completed=data.get("is_completed", False)
        )
        
        if data.get("priority"):
            subtask.priority = SubtaskPriority(data.get("priority"))
        
        if data.get("created_at"):
            subtask.created_at = datetime.fromisoformat(data.get("created_at"))
        
        if data.get("due_date"):
            subtask.due_date = datetime.fromisoformat(data.get("due_date"))
            
        return subtask