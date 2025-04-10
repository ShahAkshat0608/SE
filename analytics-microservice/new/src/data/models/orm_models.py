"""ORM models for database storage."""

# Note: This file is a placeholder for future SQL database implementation
# It will define SQLAlchemy or other ORM models for database storage

# Example SQLAlchemy models (commented out since not currently used)
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationships
team_members = Table(
    'team_members',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('team_id', String, ForeignKey('teams.id'))
)

class TaskORM(Base):
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    priority = Column(String)
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    project_id = Column(String, ForeignKey('projects.id'))
    assigned_to = Column(String, ForeignKey('users.id'))
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    milestone_id = Column(String)
    tags = Column(JSONB)
    
    # Relationships
    project = relationship("ProjectORM", back_populates="tasks")
    assignee = relationship("UserORM", back_populates="assigned_tasks")

class ProjectORM(Base):
    __tablename__ = 'projects'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(DateTime)
    target_end_date = Column(DateTime)
    status = Column(String)
    manager_id = Column(String, ForeignKey('users.id'))
    milestones = Column(JSONB)
    metadata = Column(JSONB)
    
    # Relationships
    tasks = relationship("TaskORM", back_populates="project")
    manager = relationship("UserORM", back_populates="managed_projects")

class UserORM(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String)
    skills = Column(JSONB)
    workload_capacity = Column(Integer, default=40)
    
    # Relationships
    assigned_tasks = relationship("TaskORM", back_populates="assignee")
    managed_projects = relationship("ProjectORM", back_populates="manager")
    teams = relationship("TeamORM", secondary=team_members, back_populates="members")

class TeamORM(Base):
    __tablename__ = 'teams'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    lead_id = Column(String, ForeignKey('users.id'))
    
    # Relationships
    members = relationship("UserORM", secondary=team_members, back_populates="teams")
    lead = relationship("UserORM")
"""