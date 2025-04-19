import sqlite3
import os
from typing import List, Optional
from ..models.milestone import Milestone

# Update the database path to use a relative path
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(current_dir, "project_management.db")

class MilestoneDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Fetch a milestone by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM milestones WHERE id = ?", (milestone_id,))
        row = cursor.fetchone()
        return Milestone.from_dict(dict(row)) if row else None

    def get_milestones_by_project(self, project_id: str) -> List[Milestone]:
        """Fetch all milestones for a project."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM milestones WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [Milestone.from_dict(dict(row)) for row in rows]

    def add_milestone(self, milestone: Milestone):
        """Add a new milestone."""
        cursor = self.conn.cursor()
        cursor.execute(
        """
        INSERT INTO milestones (id, name, description, project_id, sequence_no, due_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            milestone.id,
            milestone.name,
            milestone.description,
            milestone.project_id,
            milestone.sequence_no,
            milestone.due_date.isoformat() if milestone.due_date else None,
            milestone.created_at.isoformat() if milestone.created_at else None,
            milestone.updated_at.isoformat() if milestone.updated_at else None,
        ),
    )
        self.conn.commit()

    def update_milestone(self, milestone_id: str, updated_milestone: Milestone):
        """Update an existing milestone."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE milestones
            SET name = ?, 
                description = ?, 
                project_id = ?, 
                sequence_no = ?, 
                due_date = ?, 
                updated_at = ?
            WHERE id = ?
            """,
            (
                updated_milestone.name,
                updated_milestone.description,
                updated_milestone.project_id,
                updated_milestone.sequence_no,
                updated_milestone.due_date.isoformat() if updated_milestone.due_date else None,
                updated_milestone.updated_at.isoformat() if updated_milestone.updated_at else None,
                milestone_id,
            ),
        )
        self.conn.commit()

    def delete_milestone(self, milestone_id: str):
        """Delete a milestone by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM milestones WHERE id = ?", (milestone_id,))
        self.conn.commit()