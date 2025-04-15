from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from .enums import TeamType

@dataclass
class Team:
    name: str
    project_id: str
    team_lead_id: str
    id: str = None
    type: TeamType = None
    created_at: datetime = None
    
    def __post_init__(self):
        if not self.id:
            self.id = f"team-{str(uuid4())[:8]}"
        if not self.created_at:
            self.created_at = datetime.now()
            
        # Convert string to enum if needed
        if isinstance(self.type, str) and self.type is not None:
            self.type = TeamType(self.type)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "team_lead_id": self.team_lead_id,
            "type": self.type.value if self.type else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def from_dict(data):
        team = Team(
            id=data.get("id"),
            name=data.get("name"),
            project_id=data.get("project_id"),
            team_lead_id=data.get("team_lead_id")
        )
        
        if data.get("type"):
            team.type = TeamType(data.get("type"))
            
        if data.get("created_at"):
            team.created_at = datetime.fromisoformat(data.get("created_at"))
            
        return team