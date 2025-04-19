import sqlite3
import os
from typing import List, Optional
from ..models.team import Team

# Update the database path to use a relative path
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(current_dir, "project_management.db")

class TeamDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_team(self, team_id: str) -> Optional[dict]:
        """Fetch a team by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_teams_by_project(self, project_id: str) -> List[dict]:
        """Fetch all teams for a project."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def add_team(self, team: dict):
        """Add a new team."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO teams (id, name, project_id, team_lead_id, type, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (team["id"], team["name"], team["project_id"], team["team_lead_id"], 
            team.get("type"), team.get("created_at"))
        )
        self.conn.commit()

    def update_team(self, team_id: str, updated_team: dict):
        """Update an existing team."""
        cursor = self.conn.cursor()
        cursor.execute(
            """UPDATE teams 
            SET name = ?, project_id = ?, team_lead_id = ?, type = ?, created_at = ? 
            WHERE id = ?""",
            (
                updated_team["name"], 
                updated_team["project_id"], 
                updated_team["team_lead_id"], 
                updated_team.get("type"),
                updated_team.get("created_at"),
                team_id
            ),
        )    
        self.conn.commit()

    def delete_team(self, team_id: str):
        """Delete a team by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        self.conn.commit()

    def addUserToTeam(self, user_id: str, team_id: str):
        """Add a user to a team."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO team_members (user_id, team_id) VALUES (?, ?)",
            (user_id, team_id),
        )
        self.conn.commit()
    
    def removeUserFromTeam(self , user_id: str, team_id: str):
        """Remove a user from a team."""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM team_members WHERE user_id = ? AND team_id = ?",
            (user_id, team_id),
        )
        self.conn.commit()

    def isUserInTeam(self, user_id: str, team_id: str) -> bool:
        """Check if a user is already in a team."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM team_members WHERE user_id = ? AND team_id = ?",
            (user_id, team_id),
        )
        count = cursor.fetchone()[0]
        return count > 0
        
    def getTeamMembers(self, team_id: str) -> List[dict]:
        """Get all members of a team."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT tm.user_id, u.email, u.name 
            FROM team_members tm
            JOIN users u ON tm.user_id = u.id
            WHERE tm.team_id = ?
            """,
            (team_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]