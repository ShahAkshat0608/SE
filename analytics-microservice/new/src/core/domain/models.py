"""Domain models for the analytics microservice."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a date string into a datetime object."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def format_date(date_obj: Optional[datetime]) -> Optional[str]:
    """Format a datetime object into an ISO string."""
    if not date_obj:
        return None
    return date_obj.isoformat()


@dataclass
class User:
    """User entity representing a team member."""
    
    id: str
    name: str
    email: str = ""
    role: str = "user"
    workload_capacity: float = 40.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User from a dictionary."""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            role=data.get('role', 'user'),
            workload_capacity=data.get('workload_capacity', 40.0)
        )


@dataclass
class Task:
    """Task entity representing a work item."""
    
    id: str
    description: str
    project_id: str
    created_at: datetime
    priority: str = "medium"
    due_date: Optional[datetime] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a Task from a dictionary."""
        created_at = parse_date(data.get('created_at'))
        due_date = parse_date(data.get('due_date'))
        completed_at = parse_date(data.get('completed_at'))
        
        return cls(
            id=data.get('id', ''),
            description=data.get('description', ''),
            project_id=data.get('project_id', ''),
            created_at=created_at or datetime.now(),
            priority=data.get('priority', 'medium'),
            due_date=due_date,
            completed=data.get('completed', False),
            completed_at=completed_at,
            assigned_to=data.get('assigned_to'),
            estimated_hours=data.get('estimated_hours'),
            tags=data.get('tags', [])
        )


@dataclass
class Milestone:
    """Milestone entity representing a project checkpoint."""
    
    id: str
    name: str
    description: str
    due_date: datetime
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Milestone':
        """Create a Milestone from a dictionary."""
        due_date = parse_date(data.get('due_date'))
        created_at = parse_date(data.get('created_at'))
        updated_at = parse_date(data.get('updated_at'))
        
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            due_date=due_date or datetime.now(),
            completed=data.get('completed', False),
            created_at=created_at or datetime.now(),
            updated_at=updated_at
        )


@dataclass
class ProjectTask:
    """Task reference within a project."""
    
    project_id: str
    id: str
    order: int
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectTask':
        """Create a ProjectTask from a dictionary."""
        created_at = parse_date(data.get('created_at'))
        
        return cls(
            project_id=data.get('project_id', ''),
            id=data.get('id', ''),
            order=data.get('order', 0),
            created_at=created_at or datetime.now()
        )


@dataclass
class Dependency:
    """Dependency relationship between tasks or milestones."""
    
    id: str
    source_id: str
    target_id: str
    source_type: str = "task"
    target_type: str = "task"
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dependency':
        """Create a Dependency from a dictionary."""
        created_at = parse_date(data.get('created_at'))
        
        return cls(
            id=data.get('id', ''),
            source_id=data.get('source_id', ''),
            target_id=data.get('target_id', ''),
            source_type=data.get('source_type', 'task'),
            target_type=data.get('target_type', 'task'),
            created_at=created_at or datetime.now()
        )


@dataclass
class TeamMember:
    """Team member assignment to a project."""
    
    id: str
    user_id: str
    role: str = "team_member"
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeamMember':
        """Create a TeamMember from a dictionary."""
        created_at = parse_date(data.get('created_at'))
        
        return cls(
            id=data.get('id', ''),
            user_id=data.get('user_id', ''),
            role=data.get('role', 'team_member'),
            created_at=created_at or datetime.now()
        )


@dataclass
class Team:
    """Team entity representing a group of team members."""
    
    id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    team_members: List[TeamMember] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Team':
        """Create a Team from a dictionary."""
        created_at = parse_date(data.get('created_at'))
        
        # Parse team member data
        team_members = []
        for member_data in data.get('team_members', []):
            try:
                team_members.append(TeamMember.from_dict(member_data))
            except Exception as e:
                import logging
                logging.error(f"Error parsing team member: {str(e)}")
                continue
                
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            created_at=created_at or datetime.now(),
            team_members=team_members
        )


@dataclass
class Project:
    """Project entity representing a collection of tasks."""
    
    id: str
    name: str
    description: str
    status: str
    start_date: datetime
    target_end_date: datetime
    manager_id: str
    completion_percentage: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    milestones: List[Milestone] = field(default_factory=list)
    tasks: List[ProjectTask] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    teams: List[Team] = field(default_factory=list)  # Changed from team_members to teams
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create a Project from a dictionary."""
        start_date = parse_date(data.get('start_date'))
        target_end_date = parse_date(data.get('target_end_date'))
        created_at = parse_date(data.get('created_at'))
        updated_at = parse_date(data.get('updated_at'))
        
        # Parse milestone data
        milestones = []
        for milestone_data in data.get('milestones', []):
            try:
                milestones.append(Milestone.from_dict(milestone_data))
            except Exception as e:
                import logging
                logging.error(f"Error parsing milestone: {str(e)}")
                continue
        
        # Parse task reference data
        tasks = []
        for task_data in data.get('tasks', []):
            try:
                tasks.append(ProjectTask.from_dict(task_data))
            except Exception as e:
                import logging
                logging.error(f"Error parsing project task: {str(e)}")
                continue
        
        # Parse dependency data
        dependencies = []
        for dep_data in data.get('dependencies', []):
            try:
                dependencies.append(Dependency.from_dict(dep_data))
            except Exception as e:
                import logging
                logging.error(f"Error parsing dependency: {str(e)}")
                continue
        
        # Parse teams data
        teams = []
        for team_data in data.get('teams', []):
            try:
                teams.append(Team.from_dict(team_data))
            except Exception as e:
                import logging
                logging.error(f"Error parsing team: {str(e)}")
                continue
        
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            status=data.get('status', 'active'),
            start_date=start_date or datetime.now(),
            target_end_date=target_end_date or datetime.now(),
            manager_id=data.get('manager_id', ''),
            completion_percentage=data.get('completion_percentage', 0.0),
            created_at=created_at or datetime.now(),
            updated_at=updated_at,
            milestones=milestones,
            tasks=tasks,
            dependencies=dependencies,
            teams=teams,
            metadata=data.get('metadata', {})
        )
        
    def get_all_team_members(self) -> List[TeamMember]:
        """Get all team members across all teams in this project.
        
        Returns:
            List of all team members
        """
        all_members = []
        for team in self.teams:
            all_members.extend(team.team_members)
        return all_members