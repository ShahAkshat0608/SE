import sqlite3
import os
from typing import List, Optional
from ..models.role import Role

# Update the database path to use a relative path 
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(current_dir, "project_management.db")

class RoleDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_role(self, role_id: str) -> Optional[Role]:
        """Fetch a role by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
        row = cursor.fetchone()
        return Role.from_dict(dict(row)) if row else None
    
    def get_role_by_user_and_project(self, user_id: str, project_id: str) -> Optional[Role]:
        """Fetch a role by user ID and project ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM roles WHERE user_id = ? AND project_id = ?",
            (user_id, project_id),
        )
        row = cursor.fetchone()
        return Role.from_dict(dict(row)) if row else None   

    def get_roles_by_project(self, project_id: str) -> List[Role]:
        """Fetch all roles for a project."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM roles WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        return [Role.from_dict(dict(row)) for row in rows]

    def get_roles_by_user(self, user_id: str) -> List[Role]:
        """Fetch all roles for a user."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM roles WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        return [Role.from_dict(dict(row)) for row in rows]

    def add_role(self, role: Role):
        """Add a new role."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO roles (id, user_id, project_id, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                role.id,
                role.user_id,
                role.project_id,
                role.role,
            ),
        )
        self.conn.commit()

    def update_role(self, role_id: str, updated_role: Role):
        """Update an existing role."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE roles
            SET user_id = ?, project_id = ?, role = ?
            WHERE id = ?
            """,
            (
                updated_role.user_id,
                updated_role.project_id,
                updated_role.role,
                role_id,
            ),
        )
        self.conn.commit()

    def delete_role(self, role_id: str):
        """Delete a role by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
        self.conn.commit()