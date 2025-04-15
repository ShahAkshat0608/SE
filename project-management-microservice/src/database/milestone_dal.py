import sqlite3
from typing import List, Optional
from ..models.milestone import Milestone

class MilestoneDAL:
    def __init__(self, db_path="project_management.db"):
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
            INSERT INTO milestones (id, name, description, project_id, sequence)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                milestone.id,
                milestone.name,
                milestone.description,
                milestone.project_id,
                milestone.sequence,
            ),
        )
        self.conn.commit()

    def update_milestone(self, milestone_id: str, updated_milestone: Milestone):
        """Update an existing milestone."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE milestones
            SET name = ?, description = ?, project_id = ?, sequence = ?
            WHERE id = ?
            """,
            (
                updated_milestone.name,
                updated_milestone.description,
                updated_milestone.project_id,
                updated_milestone.sequence,
                milestone_id,
            ),
        )
        self.conn.commit()

    def delete_milestone(self, milestone_id: str):
        """Delete a milestone by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM milestones WHERE id = ?", (milestone_id,))
        self.conn.commit()