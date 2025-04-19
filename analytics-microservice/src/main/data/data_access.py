from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import sqlite3
import logging

class DataAccess:
    """
    Data access class that connects to both user-management and project-management databases.
    Provides a unified interface for analytics data needs.
    """
    def __init__(self):
        base_dir = "/Users/sarthak/Desktop/IIIT Course Work/Sem8/SE/project-3/SE"
        
        # Path to the user management database
        self.user_db_path = os.path.join(base_dir, "user-management", "src", "main", "data", "users.db")
        print("User db manger path: ", self.user_db_path)
        # Path to the project management database
        pm_dir = os.path.join(base_dir, "project-management-microservice", "src", "database")
        self.project_db_path = os.path.join(pm_dir, "project_management.db")
        print("Project db manager path: ", self.project_db_path)
        
        # Ensure the database files exist
        if not os.path.exists(self.user_db_path):
            logging.warning(f"User database file not found at: {self.user_db_path}")
        
        if not os.path.exists(self.project_db_path):
            logging.warning(f"Project database file not found at: {self.project_db_path}")
    
    def _get_user_db_connection(self):
        """Get a connection to the user SQLite database with row factory"""
        try:
            conn = sqlite3.connect(self.user_db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logging.error(f"User database connection error: {e}")
            raise
    
    def _get_project_db_connection(self):
        """Get a connection to the project SQLite database with row factory"""
        try:
            conn = sqlite3.connect(self.project_db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logging.error(f"Project database connection error: {e}")
            raise
        
    async def get_user_by_id(self, user_id: str):
        """Get user details from the user management database"""
        conn = self._get_user_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, name, contact FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error fetching user by ID: {e}")
            return None
        finally:
            conn.close()
        
    async def get_team_by_id(self, team_id: str):
        """Get team details from the project management database"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error fetching team by ID: {e}")
            return None
        finally:
            conn.close()
        
    async def get_project_by_id(self, project_id: str):
        """Get project details from the project management database"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error fetching project by ID: {e}")
            return None
        finally:
            conn.close()
        
    async def get_subtasks_by_user(self, user_id: str):
        """Get all subtasks assigned to a specific user"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subtasks WHERE assigned_to = ?", (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error fetching subtasks by user: {e}")
            return []
        finally:
            conn.close()
        
    async def get_subtasks_by_team(self, team_id: str, project_id: str = None):
        """Get all subtasks for a team, optionally filtered by project"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            if project_id:
                cursor.execute("""
                    SELECT s.* FROM subtasks s
                    JOIN tasks t ON s.task_id = t.id
                    WHERE t.team_id = ? AND s.project_id = ?
                """, (team_id, project_id))
            else:
                cursor.execute("""
                    SELECT s.* FROM subtasks s
                    JOIN tasks t ON s.task_id = t.id
                    WHERE t.team_id = ?
                """, (team_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error fetching subtasks by team: {e}")
            return []
        finally:
            conn.close()
        
    async def get_subtasks_by_project(self, project_id: str):
        """Get all subtasks for a specific project"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subtasks WHERE project_id = ?", (project_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error fetching subtasks by project: {e}")
            return []
        finally:
            conn.close()
        
    async def get_team_members(self, team_id: str):
        """Get all team members for a team by joining project and user databases"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            # First get the team member user IDs
            cursor.execute("SELECT user_id FROM team_members WHERE team_id = ?", (team_id,))
            user_ids = [row['user_id'] for row in cursor.fetchall()]
            
            # Collect the user details
            members = []
            user_conn = self._get_user_db_connection()
            try:
                for user_id in user_ids:
                    cursor = user_conn.cursor()
                    cursor.execute("SELECT id, email, name, contact FROM users WHERE id = ?", (user_id,))
                    user = cursor.fetchone()
                    if user:
                        members.append(dict(user))
            finally:
                user_conn.close()
                
            return members
        except sqlite3.Error as e:
            logging.error(f"Error fetching team members: {e}")
            return []
        finally:
            conn.close()
        
    async def get_teams_by_project(self, project_id: str):
        """Get all teams working on a specific project"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams WHERE project_id = ?", (project_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error fetching teams by project: {e}")
            return []
        finally:
            conn.close()
        
    async def get_milestones_by_project(self, project_id: str):
        """Get all milestones for a specific project"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM milestones WHERE project_id = ?", (project_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error fetching milestones by project: {e}")
            return []
        finally:
            conn.close()
        
    async def is_user_team_lead(self, user_id: str, team_id: str) -> bool:
        """Check if a user is the team lead for a specific team"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM teams WHERE team_lead_id = ? AND id = ?", (user_id, team_id))
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            logging.error(f"Error checking if user is team lead: {e}")
            return False
        finally:
            conn.close()
        
    async def is_user_project_manager(self, user_id: str, project_id: str) -> bool:
        """Check if a user is the project manager for a specific project"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects WHERE project_manager_id = ? AND id = ?", (user_id, project_id))
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            logging.error(f"Error checking if user is project manager: {e}")
            return False
        finally:
            conn.close()
        
    async def is_user_in_team(self, user_id: str, team_id: str) -> bool:
        """Check if a user is a member of a specific team"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM team_members WHERE user_id = ? AND team_id = ?", (user_id, team_id))
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            logging.error(f"Error checking if user is in team: {e}")
            return False
        finally:
            conn.close()
        
    async def is_user_in_project(self, user_id: str, project_id: str) -> bool:
        """Check if a user is working on a specific project by being in a team for that project"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM team_members tm
                JOIN teams t ON tm.team_id = t.id
                WHERE tm.user_id = ? AND t.project_id = ?
            """, (user_id, project_id))
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            logging.error(f"Error checking if user is in project: {e}")
            return False
        finally:
            conn.close()
        
    async def get_team_id_for_lead(self, user_id: str) -> Optional[str]:
        """Get team ID where user is a team lead"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM teams WHERE team_lead_id = ?", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting team ID for lead: {e}")
            return None
        finally:
            conn.close()
        
    async def get_project_id_for_manager(self, user_id: str) -> Optional[str]:
        """Get project ID where user is a project manager"""
        conn = self._get_project_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM projects WHERE project_manager_id = ?", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting project ID for manager: {e}")
            return None
        finally:
            conn.close()