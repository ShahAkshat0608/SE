import sqlite3
import json
from typing import Optional
DEFAULT_DB_PATH = "/Users/sarthak/Desktop/IIIT Course Work/Sem8/SE/project-3/SE/project-management-microservice/src/database/project_management.db"

class DependencyTreeDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def add_dependency_tree(self, task_id: str, root_subtask_id: Optional[str], dependencies: dict):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO dependency_tree (task_id, root_subtask_id, dependencies)
            VALUES (?, ?, ?)
            """,
            (task_id, root_subtask_id, json.dumps(dependencies)),
        )
        self.conn.commit()