import sqlite3
from typing import List, Optional

class TeamDAL:
    def __init__(self, db_path="project_management.db"):
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
            "INSERT INTO teams (id, name, project_id, team_lead_id) VALUES (?, ?, ?, ?)",
            (team["id"], team["name"], team["project_id"], team["team_lead_id"]),
        )
        self.conn.commit()

    def update_team(self, team_id: str, updated_team: dict):
        """Update an existing team."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE teams SET name = ?, project_id = ?, team_lead_id = ? WHERE id = ?",
            (updated_team["name"], updated_team["project_id"], updated_team["team_lead_id"], team_id),
        )
        self.conn.commit()

    def delete_team(self, team_id: str):
        """Delete a team by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        self.conn.commit()