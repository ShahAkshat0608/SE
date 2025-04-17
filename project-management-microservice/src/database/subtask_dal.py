import sqlite3
from typing import List, Optional
from datetime import datetime
from ..models.subtask import Subtask
import json
DEFAULT_DB_PATH = "/Users/sarthak/Desktop/IIIT Course Work/Sem8/SE/project-3/SE/project-management-microservice/src/database/project_management.db"

class SubtaskDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_subtask(self, subtask_id: str) -> Optional[Subtask]:
        """Fetch a subtask by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM subtasks WHERE id = ?", (subtask_id,))
        row = cursor.fetchone()
        return Subtask.from_dict(dict(row)) if row else None

    def get_subtasks_by_task(self, task_id: str) -> List[Subtask]:
        """Fetch all subtasks for a task."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM subtasks WHERE task_id = ?", (task_id,))
        rows = cursor.fetchall()
        return [Subtask.from_dict(dict(row)) for row in rows]

    def add_subtask(self, subtask: Subtask):
        """Add a new subtask."""
        cursor = self.conn.cursor()
        cursor.execute(
        """
        INSERT INTO subtasks (id, task_id, name, description, project_id , priority, due_date, completed, assigned, assigned_to, 
                              estimated_hours, parent_subtask_id, tags, milestone_id, is_completed, created_at)
        VALUES (?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            subtask.id,
            subtask.task_id,
            subtask.name,
            subtask.description,
            subtask.project_id,
            subtask.priority.value,
            subtask.due_date.isoformat() if subtask.due_date else None,
            int(subtask.completed),
            int(subtask.assigned),
            subtask.assigned_to,
            subtask.estimated_hours,
            subtask.parent_subtask_id,
            json.dumps(subtask.tags),
            subtask.milestone_id,
            int(subtask.is_completed),
            subtask.created_at.isoformat() if subtask.created_at else None,
        ),
    )
        self.conn.commit()

    def update_subtask(self, subtask_id: str, updated_subtask: Subtask):
        """Update an existing subtask."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE subtasks
            SET task_id = ?, name = ?, description = ?, priority = ?, due_date = ?, is_completed = ?
            WHERE id = ?
            """,
            (
                updated_subtask.task_id,
                updated_subtask.name,
                updated_subtask.description,
                updated_subtask.priority,
                updated_subtask.due_date.isoformat() if updated_subtask.due_date else None,
                int(updated_subtask.is_completed),
                subtask_id,
            ),
        )
        self.conn.commit()

    def delete_subtask(self, subtask_id: str):
        """Delete a subtask by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
        self.conn.commit()