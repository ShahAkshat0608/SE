import sqlite3
from datetime import datetime

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("project_management.db")
cursor = conn.cursor()

# Create tables
def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        contact TEXT NOT NULL
    );
    """)
    
    cursor.execute("DROP TABLE IF EXISTS projects;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        status INTEGER NOT NULL, -- Enum: PLANNING=0, IN_PROGRESS=1, etc.
        start_date TEXT NOT NULL,
        end_date TEXT,
        project_manager_id TEXT NOT NULL,
        FOREIGN KEY (project_manager_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        project_id TEXT NOT NULL,
        team_lead_id TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (team_lead_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        team_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status INTEGER NOT NULL, -- Enum: BACKLOG=0, TO_DO=1, etc.
        priority INTEGER NOT NULL, -- Enum: LOW=0, MEDIUM=1, etc.
        created_at TEXT NOT NULL,
        target_due_date TEXT,
        assigned_team_id TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subtasks (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        priority INTEGER NOT NULL, -- Enum: LOW=0, MEDIUM=1, etc.
        due_date TEXT,
        is_completed INTEGER NOT NULL DEFAULT 0, -- 0 = False, 1 = True
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS milestones (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        project_id TEXT NOT NULL,
        sequence INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

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
    # Users
    cursor.execute("INSERT INTO users (id, name, email, contact) VALUES ('user-001', 'Alice', 'alice@example.com', '1234567890');")
    cursor.execute("INSERT INTO users (id, name, email, contact) VALUES ('user-002', 'Bob', 'bob@example.com', '0987654321');")

    # Projects
    cursor.execute("""
    INSERT INTO projects (id, name, description, status, start_date, end_date, project_manager_id)
    VALUES ('project-001', 'Website Redesign', 'Redesign the company website', 1, '2025-01-01', '2025-06-01', 'user-001');
    """)

    # Teams
    cursor.execute("""
    INSERT INTO teams (id, name, project_id, team_lead_id)
    VALUES ('team-001', 'Design Team', 'project-001', 'user-002');
    """)

    # Tasks
    cursor.execute("""
    INSERT INTO tasks (id, project_id, team_id, name, description, status, priority, created_at, target_due_date, assigned_team_id)
    VALUES ('task-001', 'project-001', 'team-001', 'Create Wireframes', 'Design wireframes for the new website', 1, 1, ?, '2025-03-01', 'team-001');
    """, (datetime.now().isoformat(),))

    # Subtasks
    cursor.execute("""
    INSERT INTO subtasks (id, task_id, name, description, priority, due_date, is_completed)
    VALUES ('subtask-001', 'task-001', 'Homepage Wireframe', 'Create wireframe for the homepage', 2, '2025-02-15', 0);
    """)

    # Milestones
    cursor.execute("""
    INSERT INTO milestones (id, name, description, project_id, sequence)
    VALUES ('milestone-001', 'Design Phase Complete', 'Complete all design tasks', 'project-001', 1);
    """)

    # Roles
    cursor.execute("""
    INSERT INTO roles (id, user_id, project_id, role)
    VALUES ('role-001', 'user-001', 'project-001', 'Project Manager');
    """)

# Run the setup

create_tables()
insert_sample_data()

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database setup complete with sample data!")