from dataclasses import dataclass
from typing import Optional

@dataclass
class Role:
    id: str
    user_id: str
    project_id: str
    role: str  # PROJECT_MANAGER, TEAM_LEAD, TEAM_MEMBER
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "role": self.role
        }
    
    @staticmethod
    def from_dict(data):
        return Role(
            id=data.get("id"),
            user_id=data.get("user_id"),
            project_id=data.get("project_id"),
            role=data.get("role")
        )