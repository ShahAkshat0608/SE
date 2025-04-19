import sqlite3
import os
from datetime import datetime

# Update to use relative path
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "project_management.db")

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def table_exists(table_name):
    """Check if a table exists in the database"""
    cursor.execute("""
    SELECT name FROM sqlite_master WHERE type='table' AND name=?;
    """, (table_name,))
    return cursor.fetchone() is not None

# Create tables
def create_tables():
    # Only create tables that don't exist
    if not table_exists("users"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            contact TEXT NOT NULL
        );
        """)
    
    if not table_exists("projects"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL, -- Enum: PLANNING, IN_PROGRESS, etc.
            start_date TEXT NOT NULL,
            target_end_date TEXT,
            project_manager_id TEXT NOT NULL,
            completion_percentage REAL DEFAULT 0.0,
            priority TEXT, -- Enum: LOW, MEDIUM, HIGH, CRITICAL
            client TEXT,
            department TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_manager_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

    if not table_exists("teams"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            project_id TEXT NOT NULL,
            team_lead_id TEXT NOT NULL,
            type TEXT, -- Enum: RESEARCH, ANALYSIS, etc.
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (team_lead_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

    if not table_exists("team_members"):
        # create table for team members
        cursor.execute("""
        CREATE TABLE team_members (
                user_id VARCHAR(36) NOT NULL,
                team_id VARCHAR(36) NOT NULL,
                joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, team_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
                );
                    """)

    if not table_exists("tasks"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            team_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL, -- Enum: BACKLOG, TO_DO, etc.
            priority TEXT NOT NULL, -- Enum: LOW, MEDIUM, HIGH, CRITICAL
            created_at TEXT NOT NULL,
            target_due_date TEXT,
            assigned_team_id TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
        );
        """)

    if not table_exists("subtasks"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtasks (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            project_id TEXT NOT NULL,
            priority TEXT NOT NULL, -- Enum: LOW, MEDIUM, HIGH
            due_date TEXT,
            completed INTEGER NOT NULL DEFAULT 0, -- 0 = False, 1 = True
            assigned INTEGER NOT NULL DEFAULT 0, -- 0 = False, 1 = True
            assigned_to TEXT,
            estimated_hours REAL DEFAULT 0.0,
            parent_subtask_id TEXT,
            tags TEXT, -- JSON array of tags
            milestone_id TEXT,
            is_completed INTEGER NOT NULL DEFAULT 0, -- 0 = False, 1 = True
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (milestone_id) REFERENCES milestones(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_subtask_id) REFERENCES subtasks(id) ON DELETE SET NULL
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

    if not table_exists("milestones"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS milestones (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            project_id TEXT NOT NULL,
            sequence_no INTEGER NOT NULL CHECK (sequence_no > 0),
            due_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

    if not table_exists("dependency_tree"):
        cursor.execute("""
                CREATE TABLE dependency_tree (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            root_subtask_id TEXT,
            dependencies TEXT, -- JSON object to store dependencies
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (root_subtask_id) REFERENCES subtasks(id) ON DELETE SET NULL
        );
        """)

    if not table_exists("roles"):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            role TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """)

# Insert sample data
def insert_sample_data():
    # Insert sample users
    cursor.executemany("""
    INSERT INTO users (id, name, email, contact) VALUES (?, ?, ?, ?);
    """, [
        ("user1", "Alice Johnson", "alice@example.com", "1234567890"),
        ("user2", "Bob Smith", "bob@example.com", "0987654321"),
        ("user3", "Charlie Brown", "charlie@example.com", "1122334455")
    ])

    # Insert sample projects
    cursor.executemany("""
    INSERT INTO projects (id, name, description, status, start_date, target_end_date, project_manager_id, completion_percentage, priority, client, department) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        ("project1", "Project Alpha", "Description of Project Alpha", "PLANNING", "2025-04-01", "2025-12-31", "user1", 0.0, "HIGH", "Client A", "IT"),
        ("project2", "Project Beta", "Description of Project Beta", "IN_PROGRESS", "2025-01-15", "2025-06-30", "user2", 50.0, "MEDIUM", "Client B", "Finance")
    ])

    # Insert sample teams
    cursor.executemany("""
    INSERT INTO teams (id, name, project_id, team_lead_id) VALUES (?, ?, ?, ?);
    """, [
        ("team1", "Alpha Team", "project1", "user1"),
        ("team2", "Beta Team", "project2", "user2")
    ])

    # Insert sample tasks
    cursor.executemany("""
    INSERT INTO tasks (id, project_id, team_id, name, description, status, priority, created_at, target_due_date, assigned_team_id) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        ("task1", "project1", "team1", "Task 1", "Description of Task 1", "TO_DO", "HIGH", "2025-04-10", "2025-05-01", "team1"),
        ("task2", "project2", "team2", "Task 2", "Description of Task 2", "IN_PROGRESS", "MEDIUM", "2025-03-01", "2025-04-30", "team2")
    ])

    # Insert sample subtasks
    cursor.executemany("""
    INSERT INTO subtasks (id, task_id, name, description, project_id, priority, due_date, completed, assigned, assigned_to, estimated_hours, parent_subtask_id, tags, milestone_id, is_completed) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        ("subtask1", "task1", "Subtask 1", "Description of Subtask 1", "project1", "HIGH", "2025-04-20", 0, 1, "user1", 5.0, None, '["tag1", "tag2"]', None, 0),
        ("subtask2", "task2", "Subtask 2", "Description of Subtask 2", "project2", "MEDIUM", "2025-04-25", 0, 1, "user2", 3.0, None, '["tag3"]', None, 0)
    ])

    # Insert sample milestones
    cursor.executemany("""
    INSERT INTO milestones (id, name, description, project_id, sequence_no, due_date) 
    VALUES (?, ?, ?, ?, ?, ?);
    """, [
        ("milestone1", "Milestone 1", "Description of Milestone 1", "project1", 1, "2025-05-01"),
        ("milestone2", "Milestone 2", "Description of Milestone 2", "project2", 2, "2025-06-01")
    ])

    # Insert sample dependency_tree
    cursor.executemany("""
    INSERT INTO dependency_tree (task_id, root_subtask_id, dependencies) 
    VALUES (?, ?, ?);
    """, [
        ("task1", "subtask1", '{"subtask2": "BLOCKED"}'),
        ("task2", "subtask2", '{"subtask1": "DEPENDENT"}')
    ])

    # Insert sample roles
    cursor.executemany("""
    INSERT INTO roles (id, user_id, project_id, role) 
    VALUES (?, ?, ?, ?);
    """, [
        ("role1", "user1", "project1", "Project Manager"),
        ("role2", "user2", "project2", "Team Lead")
    ])         

# Run the setup
# create_tables()

# Alter table team to add new columns created_at and updated_at
# cursor.execute("""
# ALTER TABLE teams ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;
# """)

# cursor.execute("""
# ALTER TABLE teams ADD COLUMN updated_at TEXT DEFAULT CURRENT_TIMESTAMP;
# """)

# get content of table roles
cursor.execute("""
SELECT * FROM subtasks;
""")
rows = cursor.fetchall()
# Print the content of the table
for row in rows:
    print(row)
    

# Commit the changes and close the connection
conn.commit()
conn.close()
print(f"Database setup complete at: {db_path}")