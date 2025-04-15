from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

@dataclass
class Milestone:
    name: str
    project_id: str
    description: str
    sequence_no: int
    id: str = None
    due_date: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if not self.id:
            self.id = f"milestone-{str(uuid4())[:8]}"
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "description": self.description,
            "sequence_no": self.sequence_no,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def from_dict(data):
        milestone = Milestone(
            id=data.get("id"),
            name=data.get("name"),
            project_id=data.get("project_id"),
            description=data.get("description"),
            sequence_no=data.get("sequence_no")
        )
        
        if data.get("created_at"):
            milestone.created_at = datetime.fromisoformat(data.get("created_at"))
        
        if data.get("updated_at"):
            milestone.updated_at = datetime.fromisoformat(data.get("updated_at"))
        
        if data.get("due_date"):
            milestone.due_date = datetime.fromisoformat(data.get("due_date"))
            
        return milestone