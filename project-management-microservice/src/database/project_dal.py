import sqlite3
import os
from typing import List, Optional
from ..models.project import Project

# Update the database path to use a relative path
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(current_dir, "project_management.db")

class ProjectDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def get_project_by_name(self, project_name: str) -> Optional[dict]:
        """Fetch a project by name."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE name = ?", (project_name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_project(self, project_id: str) -> Optional[dict]:
        """Fetch a project by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_projects(self) -> List[dict]:
        """Fetch all projects."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def add_project(self, project: dict):
        """Add a new project."""
        cursor = self.conn.cursor()
        cursor.execute(
        """
        INSERT INTO projects (id, name, description, status, start_date, target_end_date, project_manager_id, 
                              completion_percentage, priority, client, department, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project["id"],
            project["name"],
            project["description"],
            project["status"],
            project["start_date"],
            project["target_end_date"],
            project["project_manager_id"],
            project["completion_percentage"],
            project["priority"],
            project["client"],
            project["department"],
            project["created_at"],
            project["updated_at"],
        ),
    )
        self.conn.commit()

    def update_project(self, project_id: str, updated_project: dict):
        """Update an existing project."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE projects
            SET name = ?, description = ?, status = ?, start_date = ?, end_date = ?, project_manager_id = ?
            WHERE id = ?
            """,
            (
                updated_project["name"],
                updated_project["description"],
                updated_project["status"],
                updated_project["start_date"],
                updated_project["end_date"],
                updated_project["project_manager_id"],
                project_id,
            ),
        )
        self.conn.commit()

    def delete_project(self, project_id: str):
        """Delete a project by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()