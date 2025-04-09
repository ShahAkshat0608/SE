from datetime import datetime
import uuid

class Project:
    def __init__(self, name, description, owner_id):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.members = []  # List of user IDs
        self.task_ids = []  # List of task IDs
        self.status = "active"  # active, completed, archived
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def __str__(self):
        status_symbols = {"active": "◉", "completed": "✓", "archived": "⌂"}
        return f"[{status_symbols[self.status]}] {self.name} (ID: {self.id})"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "members": self.members,
            "task_ids": self.task_ids,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        project = cls(
            name=data["name"],
            description=data["description"],
            owner_id=data["owner_id"]
        )
        project.id = data["id"]
        project.members = data["members"]
        project.task_ids = data["task_ids"]
        project.status = data["status"]
        project.created_at = datetime.fromisoformat(data["created_at"])
        project.updated_at = datetime.fromisoformat(data["updated_at"])
        return project