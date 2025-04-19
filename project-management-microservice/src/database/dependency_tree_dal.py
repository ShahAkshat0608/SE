import sqlite3
import os
import json
from typing import Optional, Dict
from ..models.dependency_tree import DependencyTree
from uuid import uuid4

# Update the database path to use a relative path
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(current_dir, "project_management.db")

class DependencyTreeDAL:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def create_dependency_tree(self, task_id: str):
        unique_id = f"dependency_tree-{str(uuid4())[:8]}"
        root_subtask_id = unique_id
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO dependency_tree (id , task_id, root_subtask_id, dependencies)
            VALUES (?, ?, ?, ?)
            """,
            (unique_id , task_id, root_subtask_id, json.dumps({})),
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_dependency_tree(self, task_id: str) -> Optional[DependencyTree]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM dependency_tree WHERE task_id = ?
            """,
            (task_id,),
        )
        row = cursor.fetchone()
        if row:
            return DependencyTree.from_dict(dict(row))
        return None

    def update_dependency_tree(self, dependency_tree: DependencyTree):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE dependency_tree
            SET root_subtask_id = ?, dependencies = ?
            WHERE task_id = ?
            """,
            (dependency_tree.root_subtask_id, json.dumps(dependency_tree.dependencies), dependency_tree.task_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0

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