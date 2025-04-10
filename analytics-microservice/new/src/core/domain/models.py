"""Core domain models and value objects."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Task:
    """Task entity representing a single work item."""
    
    id: str
    description: str
    priority: str
    due_date: Optional[datetime] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    project_id: Optional[str] = None
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a Task from a dictionary.
        
        Args:
            data: Dictionary containing task data
            
        Returns:
            Task object
        """
        # Process date fields
        created_at = data.get('created_at')
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()
        
        completed_at = data.get('completed_at')
        if completed_at and isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)
            
        due_date = data.get('due_date')
        if due_date and isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)
            
        # Create Task object
        return cls(
            id=data.get('id', ''),
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            due_date=due_date,
            completed=data.get('completed', False),
            created_at=created_at,
            completed_at=completed_at,
            project_id=data.get('project_id'),
            assigned_to=data.get('assigned_to'),
            estimated_hours=data.get('estimated_hours'),
            actual_hours=data.get('actual_hours'),
            dependencies=data.get('dependencies', []),
            tags=data.get('tags', [])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Task to a dictionary.
        
        Returns:
            Dictionary representation of task
        """
        result = {
            'id': self.id,
            'description': self.description,
            'priority': self.priority,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }
        
        # Add optional fields if present
        if self.due_date:
            result['due_date'] = self.due_date.isoformat()
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        if self.project_id:
            result['project_id'] = self.project_id
        if self.assigned_to:
            result['assigned_to'] = self.assigned_to
        if self.estimated_hours is not None:
            result['estimated_hours'] = self.estimated_hours
        if self.actual_hours is not None:
            result['actual_hours'] = self.actual_hours
        if self.dependencies:
            result['dependencies'] = self.dependencies
        if self.tags:
            result['tags'] = self.tags
            
        return result


@dataclass
class Milestone:
    """Milestone representing a significant point in a project timeline."""
    
    id: str
    name: str
    due_date: datetime
    completed: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Milestone':
        """Create a Milestone from a dictionary."""
        due_date = data.get('due_date')
        if due_date and isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)
        else:
            due_date = datetime.now()
            
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            due_date=due_date,
            completed=data.get('completed', False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Milestone to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'due_date': self.due_date.isoformat(),
            'completed': self.completed
        }


@dataclass
class Project:
    """Project entity representing a collection of related tasks."""
    
    id: str
    name: str
    description: str = ''
    start_date: Optional[datetime] = None
    target_end_date: Optional[datetime] = None
    status: str = 'in_progress'
    manager_id: Optional[str] = None
    team_members: List[str] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create a Project from a dictionary."""
        # Process date fields
        start_date = data.get('start_date')
        if start_date and isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
            
        target_end_date = data.get('target_end_date')
        if target_end_date and isinstance(target_end_date, str):
            target_end_date = datetime.fromisoformat(target_end_date)
            
        # Process milestones
        milestones = []
        for milestone_data in data.get('milestones', []):
            milestones.append(Milestone.from_dict(milestone_data))
            
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            start_date=start_date,
            target_end_date=target_end_date,
            status=data.get('status', 'in_progress'),
            manager_id=data.get('manager_id'),
            team_members=data.get('team_members', []),
            milestones=milestones,
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Project to a dictionary."""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'team_members': self.team_members,
            'milestones': [m.to_dict() for m in self.milestones],
            'metadata': self.metadata
        }
        
        # Add optional fields if present
        if self.start_date:
            result['start_date'] = self.start_date.isoformat()
        if self.target_end_date:
            result['target_end_date'] = self.target_end_date.isoformat()
        if self.manager_id:
            result['manager_id'] = self.manager_id
            
        return result


@dataclass
class User:
    """User entity representing a team member."""
    
    id: str
    name: str
    email: str
    role: str = 'user'
    skills: List[str] = field(default_factory=list)
    teams: List[str] = field(default_factory=list)
    workload_capacity: float = 40.0  # Default to 40 hours/week capacity
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User from a dictionary."""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            role=data.get('role', 'user'),
            skills=data.get('skills', []),
            teams=data.get('teams', []),
            workload_capacity=data.get('workload_capacity', 40.0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'skills': self.skills,
            'teams': self.teams,
            'workload_capacity': self.workload_capacity
        }