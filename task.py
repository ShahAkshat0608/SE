from datetime import datetime
import uuid

class Task:
    def __init__(self, description, priority="medium", due_date=None, completed=False):
        self.id = str(uuid.uuid4())[:8]  # Short unique ID
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.created_at = datetime.now()
    
    def __str__(self):
        status = "✓" if self.completed else "☐"
        due_str = f", due: {self.due_date.strftime('%Y-%m-%d')}" if self.due_date else ""
        priority_symbols = {"low": "↓", "medium": "→", "high": "↑"}
        return f"[{status}] [{priority_symbols[self.priority]}] {self.description}{due_str} (ID: {self.id})"
    
    def complete(self):
        self.completed = True
        
    def uncomplete(self):
        self.completed = False
        
    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(
            description=data["description"],
            priority=data["priority"],
            completed=data["completed"]
        )
        task.id = data["id"]
        task.created_at = datetime.fromisoformat(data["created_at"])
        if data["due_date"]:
            task.due_date = datetime.fromisoformat(data["due_date"])
        return task 