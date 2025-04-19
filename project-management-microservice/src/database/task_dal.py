import sqlite3
import os
from typing import List, Optional
from ..models.task import Task

# Update the database path to use a relative path
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(current_dir, "project_management.db")

class TaskDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_task(self, task_id: str) -> Optional[dict]:
        """Fetch a task by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_tasks_by_project(self, project_id: str) -> List[dict]:
        """Fetch all tasks for a project."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_tasks_by_team(self, project_id: str , team_id: str) -> List[dict]:
        """Fetch all tasks for a specific team."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE project_id = ? AND team_id = ?", (project_id, team_id))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def add_task(self, task: dict):
        """Add a new task."""
        cursor = self.conn.cursor()
        cursor.execute(
        """
        INSERT INTO tasks (id, project_id, team_id, name, description, status, priority, created_at, target_due_date, assigned_team_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task["id"],
            task["project_id"],
            task["team_id"],
            task["name"],
            task["description"],
            task["status"],
            task["priority"],
            task["created_at"],
            task["target_due_date"],
            task["assigned_team_id"],
        ),
    )
        self.conn.commit()

    def update_task(self, task_id: str, updated_task: dict):
        """Update an existing task."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE tasks
            SET project_id = ?, team_id = ?, name = ?, description = ?, status = ?, priority = ?, created_at = ?, target_due_date = ?, assigned_team_id = ?
            WHERE id = ?
            """,
            (
                updated_task["project_id"],
                updated_task["team_id"],
                updated_task["name"],
                updated_task["description"],
                updated_task["status"],
                updated_task["priority"],
                updated_task["created_at"],
                updated_task["target_due_date"],
                updated_task["assigned_team_id"],
                task_id,
            ),
        )
        self.conn.commit()

    def delete_task(self, task_id: str):
        """Delete a task by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()