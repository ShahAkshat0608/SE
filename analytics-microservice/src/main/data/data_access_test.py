from typing import Dict, List, Optional, Any
import json
import os
import asyncio

class TestDataAccess:
    """Test data access implementation with mock data"""
    
    def __init__(self):
        # Initialize with test data
        self.data = self._load_test_data()
    
    def _load_test_data(self) -> Dict:
        """Load test data"""
        # Create mock data structure with relationships
        return {
            "users": [
                {
                    "id": "user-101",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "user",
                    "team_id": "team-101"
                },
                {
                    "id": "user-102",
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "role": "team_lead",
                    "team_id": "team-101"
                },
                {
                    "id": "user-103",
                    "name": "Michael Johnson",
                    "email": "michael@example.com",
                    "role": "project_manager",
                    "team_id": None
                },
                {
                    "id": "user-104",
                    "name": "Sarah Wilson",
                    "email": "sarah@example.com",
                    "role": "user",
                    "team_id": "team-101"
                }
            ],
            "teams": [
                {
                    "id": "team-101",
                    "name": "Frontend Team",
                    "project_id": "project-101",
                    "lead_id": "user-102"
                },
                {
                    "id": "team-102",
                    "name": "Backend Team",
                    "project_id": "project-101",
                    "lead_id": "user-105"
                }
            ],
            "projects": [
                {
                    "id": "project-101",
                    "name": "Web Application",
                    "description": "New company website",
                    "status": "in_progress",
                    "start_date": "2023-01-01T00:00:00Z",
                    "target_end_date": "2023-12-31T00:00:00Z",
                    "project_manager_id": "user-103"
                }
            ],
            "subtasks": [
                {
                    "id": "subtask-101",
                    "description": "Design homepage",
                    "priority": "high",
                    "estimated_hours": 8,
                    "assigned_to": "user-101",
                    "team_id": "team-101",
                    "project_id": "project-101",
                    "completed": True,
                    "due_date": "2023-03-15T00:00:00Z",
                    "milestone_id": "milestone-101"
                },
                {
                    "id": "subtask-102",
                    "description": "Implement user authentication",
                    "priority": "high",
                    "estimated_hours": 12,
                    "assigned_to": "user-101",
                    "team_id": "team-101",
                    "project_id": "project-101",
                    "completed": False,
                    "due_date": "2023-04-20T00:00:00Z",
                    "milestone_id": "milestone-101"
                },
                {
                    "id": "subtask-103",
                    "description": "Create product listing page",
                    "priority": "medium",
                    "estimated_hours": 6,
                    "assigned_to": "user-104",
                    "team_id": "team-101",
                    "project_id": "project-101",
                    "completed": False,
                    "due_date": "2023-04-30T00:00:00Z",
                    "milestone_id": "milestone-102"
                }
            ],
            "milestones": [
                {
                    "id": "milestone-101",
                    "name": "Initial Release",
                    "project_id": "project-101",
                    "due_date": "2023-06-30T00:00:00Z"
                },
                {
                    "id": "milestone-102",
                    "name": "Final Release",
                    "project_id": "project-101",
                    "due_date": "2023-12-15T00:00:00Z"
                }
            ]
        }
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        for user in self.data["users"]:
            if user["id"] == user_id:
                return user
        return None
    
    async def get_team_by_id(self, team_id: str) -> Optional[Dict]:
        """Get team by ID"""
        for team in self.data["teams"]:
            if team["id"] == team_id:
                return team
        return None
    
    async def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        for project in self.data["projects"]:
            if project["id"] == project_id:
                return project
        return None
    
    async def get_subtasks_by_user(self, user_id: str) -> List[Dict]:
        """Get all subtasks assigned to a user"""
        return [task for task in self.data["subtasks"] if task["assigned_to"] == user_id]
    
    async def get_subtasks_by_team(self, team_id: str, project_id: str = None) -> List[Dict]:
        """Get all subtasks for a team"""
        if project_id:
            return [task for task in self.data["subtasks"] 
                    if task["team_id"] == team_id and task["project_id"] == project_id]
        return [task for task in self.data["subtasks"] if task["team_id"] == team_id]
    
    async def get_subtasks_by_project(self, project_id: str) -> List[Dict]:
        """Get all subtasks for a project"""
        return [task for task in self.data["subtasks"] if task["project_id"] == project_id]
    
    async def get_team_members(self, team_id: str) -> List[Dict]:
        """Get all members of a team"""
        return [user for user in self.data["users"] if user.get("team_id") == team_id]
    
    async def get_teams_by_project(self, project_id: str) -> List[Dict]:
        """Get all teams in a project"""
        return [team for team in self.data["teams"] if team["project_id"] == project_id]
    
    async def get_milestones_by_project(self, project_id: str) -> List[Dict]:
        """Get all milestones for a project"""
        return [milestone for milestone in self.data["milestones"] if milestone["project_id"] == project_id]
    
    async def get_team_id_for_lead(self, user_id: str) -> Optional[str]:
        """Get team ID where user is a team lead"""
        for team in self.data["teams"]:
            if team["lead_id"] == user_id:
                return team["id"]
        return None
    
    async def get_project_id_for_manager(self, user_id: str) -> Optional[str]:
        """Get project ID where user is a project manager"""
        for project in self.data["projects"]:
            if project["project_manager_id"] == user_id:
                return project["id"]
        return None
    
    async def is_user_in_team(self, user_id: str, team_id: str) -> bool:
        """Check if a user is in a specific team"""
        user = await self.get_user_by_id(user_id)
        return user is not None and user.get("team_id") == team_id
    
    async def is_user_in_project(self, user_id: str, project_id: str) -> bool:
        """Check if a user is in a specific project"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        team_id = user.get("team_id")
        if not team_id:
            return False
        
        team = await self.get_team_by_id(team_id)
        return team is not None and team.get("project_id") == project_id
    
    async def is_user_team_lead(self, user_id: str, team_id: str) -> bool:
        """Check if a user is the team lead for a specific team"""
        team = await self.get_team_by_id(team_id)
        return team is not None and team.get("lead_id") == user_id
    
    async def is_user_project_manager(self, user_id: str, project_id: str) -> bool:
        """Check if a user is the project manager for a specific project"""
        project = await self.get_project_by_id(project_id)
        return project is not None and project.get("project_manager_id") == user_id