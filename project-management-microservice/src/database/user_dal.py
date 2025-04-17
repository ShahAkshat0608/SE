import sqlite3
from typing import List, Optional
DEFAULT_DB_PATH = "/Users/sarthak/Desktop/IIIT Course Work/Sem8/SE/project-3/SE/project-management-microservice/src/database/project_management.db"

class UserDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_user(self, user_id: str) -> Optional[dict]:
        """Fetch a user by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_users(self) -> List[dict]:
        """Fetch all users."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def add_user(self, user: dict):
        """Add a new user."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, contact) VALUES (?, ?, ?, ?)",
            (user["id"], user["name"], user["email"], user["contact"]),
        )
        self.conn.commit()

    def update_user(self, user_id: str, updated_user: dict):
        """Update an existing user."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE users SET name = ?, email = ?, contact = ? WHERE id = ?",
            (updated_user["name"], updated_user["email"], updated_user["contact"], user_id),
        )
        self.conn.commit()

    def delete_user(self, user_id: str):
        """Delete a user by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()