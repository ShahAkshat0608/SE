import asyncio
import sys
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the parent directory to the path so we can import the data_access module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main.data.data_access import DataAccess

async def test_task_analytics():
    """Test the DataAccess class by querying task analytics data"""
    print("Starting Task Analytics Test")
    print("=" * 50)
    
    # Create an instance of the DataAccess class
    data_access = DataAccess()
    
    # Test 1: Get project details
    print("\nTest 1: Get Project Details")
    print("-" * 30)
    # This assumes there's a project with ID "1" or adjust to a known project ID
    project_id = "project-0e690a3e" 
     # Replace with a known project ID
    project = await data_access.get_project_by_id(project_id)
    print(f"Project: {json.dumps(project, indent=2) if project else 'Not found'}")
    
    # Test 2: Get teams for a project
    print("\nTest 2: Get Teams for Project")
    print("-" * 30)
    teams = await data_access.get_teams_by_project(project_id)
    print(f"Found {len(teams)} teams for project {project_id}")
    for i, team in enumerate(teams):
        print(f"Team {i+1}: {team['name']} (ID: {team['id']})")
    
    # Use the first team for further tests if available
    team_id = teams[0]['id'] if teams else None
    
    # Test 3: Get team members
    print("\nTest 3: Get Team Members")
    print("-" * 30)
    if team_id:
        members = await data_access.get_team_members(team_id)
        print(f"Found {len(members)} members for team {team_id}")
        for i, member in enumerate(members):
            print(f"Member {i+1}: {member['name']} (ID: {member['id']})")
        
        # Use the first member for further tests if available
        user_id = members[0]['id'] if members else None
    else:
        print("No team available for testing")
        user_id = None
    
    # Test 4: Get subtasks by project
    print("\nTest 4: Get Subtasks by Project")
    print("-" * 30)
    subtasks = await data_access.get_subtasks_by_project(project_id)
    print(f"Found {len(subtasks)} subtasks for project {project_id}")
    for i, subtask in enumerate(subtasks[:5]):  # Show only first 5 subtasks
        print(f"Subtask {i+1}: {subtask.get('title', 'No title')} (ID: {subtask.get('id', 'No ID')})")
    
    # Test 5: Get subtasks by team
    print("\nTest 5: Get Subtasks by Team")
    print("-" * 30)
    if team_id:
        team_subtasks = await data_access.get_subtasks_by_team(team_id)
        print(f"Found {len(team_subtasks)} subtasks for team {team_id}")
        for i, subtask in enumerate(team_subtasks[:5]):  # Show only first 5 subtasks
            print(f"Subtask {i+1}: {subtask.get('title', 'No title')} (ID: {subtask.get('id', 'No ID')})")
    else:
        print("No team available for testing")
    
    # Test 6: Get subtasks by user
    print("\nTest 6: Get Subtasks by User")
    print("-" * 30)
    if user_id:
        user_subtasks = await data_access.get_subtasks_by_user(user_id)
        print(f"Found {len(user_subtasks)} subtasks assigned to user {user_id}")
        for i, subtask in enumerate(user_subtasks[:5]):  # Show only first 5 subtasks
            print(f"Subtask {i+1}: {subtask.get('title', 'No title')} (ID: {subtask.get('id', 'No ID')})")
    else:
        print("No user available for testing")
    
    # Test 7: Check user roles
    print("\nTest 7: Check User Roles")
    print("-" * 30)
    if user_id and team_id:
        is_team_lead = await data_access.is_user_team_lead(user_id, team_id)
        is_project_manager = await data_access.is_user_project_manager(user_id, project_id)
        is_in_team = await data_access.is_user_in_team(user_id, team_id)
        is_in_project = await data_access.is_user_in_project(user_id, project_id)
        
        print(f"User {user_id} roles:")
        print(f"- Team Lead of team {team_id}: {is_team_lead}")
        print(f"- Project Manager of project {project_id}: {is_project_manager}")
        print(f"- Member of team {team_id}: {is_in_team}")
        print(f"- Participant in project {project_id}: {is_in_project}")
    else:
        print("No user or team available for testing")
    
    # Test 8: Get milestones for a project
    print("\nTest 8: Get Milestones for Project")
    print("-" * 30)
    milestones = await data_access.get_milestones_by_project(project_id)
    print(f"Found {len(milestones)} milestones for project {project_id}")
    for i, milestone in enumerate(milestones):
        deadline = milestone.get('deadline', 'No deadline')
        print(f"Milestone {i+1}: {milestone.get('title', 'No title')} (Deadline: {deadline})")
    
    # Test 9: Get all projects
    print("\nTest 9: Get All Projects")
    print("-" * 30)
    try:
        all_projects = await get_all_projects(data_access)
        print(f"Found {len(all_projects)} projects in total")
        for i, proj in enumerate(all_projects[:5]):  # Show only first 5 projects
            print(f"Project {i+1}: {proj.get('name', 'No name')} (ID: {proj.get('id', 'No ID')})")
    except Exception as e:
        print(f"Error fetching all projects: {e}")
    
    # Test 10: Get all teams
    print("\nTest 10: Get All Teams")
    print("-" * 30)
    try:
        all_teams = await get_all_teams(data_access)
        print(f"Found {len(all_teams)} teams in total")
        for i, team in enumerate(all_teams[:5]):  # Show only first 5 teams
            print(f"Team {i+1}: {team.get('name', 'No name')} (ID: {team.get('id', 'No ID')})")
    except Exception as e:
        print(f"Error fetching all teams: {e}")
    
    # Test 11: Get all tasks
    print("\nTest 11: Get All Tasks")
    print("-" * 30)
    try:
        all_tasks = await get_all_tasks(data_access)
        print(f"Found {len(all_tasks)} tasks in total")
        for i, task in enumerate(all_tasks[:5]):  # Show only first 5 tasks
            print(f"Task {i+1}: {task.get('title', 'No title')} (ID: {task.get('id', 'No ID')})")
    except Exception as e:
        print(f"Error fetching all tasks: {e}")
    
    # Test 12: Get all subtasks
    print("\nTest 12: Get All Subtasks")
    print("-" * 30)
    try:
        all_subtasks = await get_all_subtasks(data_access)
        print(f"Found {len(all_subtasks)} subtasks in total")
        for i, subtask in enumerate(all_subtasks[:5]):  # Show only first 5 subtasks
            print(f"Subtask {i+1}: {subtask.get('title', 'No title')} (ID: {subtask.get('id', 'No ID')})")
    except Exception as e:
        print(f"Error fetching all subtasks: {e}")
    
    # Test 13: Get all users
    print("\nTest 13: Get All Users")
    print("-" * 30)
    try:
        all_users = await get_all_users(data_access)
        print(f"Found {len(all_users)} users in total")
        for i, user in enumerate(all_users[:5]):  # Show only first 5 users
            print(f"User {i+1}: {user.get('name', 'No name')} (ID: {user.get('id', 'No ID')})")
    except Exception as e:
        print(f"Error fetching all users: {e}")
    
    print("\nTask Analytics Test Completed")
    print("=" * 50)

# Helper functions to query all data from tables
async def get_all_projects(data_access):
    """Get all projects from the database"""
    conn = data_access._get_project_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logging.error(f"Error fetching all projects: {e}")
        return []
    finally:
        conn.close()

async def get_all_teams(data_access):
    """Get all teams from the database"""
    conn = data_access._get_project_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logging.error(f"Error fetching all teams: {e}")
        return []
    finally:
        conn.close()

async def get_all_tasks(data_access):
    """Get all tasks from the database"""
    conn = data_access._get_project_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logging.error(f"Error fetching all tasks: {e}")
        return []
    finally:
        conn.close()

async def get_all_subtasks(data_access):
    """Get all subtasks from the database"""
    conn = data_access._get_project_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subtasks")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logging.error(f"Error fetching all subtasks: {e}")
        return []
    finally:
        conn.close()

async def get_all_users(data_access):
    """Get all users from the database"""
    conn = data_access._get_user_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logging.error(f"Error fetching all users: {e}")
        return []
    finally:
        conn.close()

# Test databases existence
def check_database_paths():
    """Check if database files exist at expected locations"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    user_db_path = os.path.join(base_dir, "user-management", "src", "main", "data", "users.db")
    project_db_path = os.path.join(base_dir, "project-management-microservice", "src", "database", "project_management.db")
    
    print("\nDatabase Path Check:")
    print(f"User DB path: {user_db_path}")
    print(f"User DB exists: {os.path.exists(user_db_path)}")
    print(f"Project DB path: {project_db_path}")
    print(f"Project DB exists: {os.path.exists(project_db_path)}")
    
    # Search for database files in the project structure
    print("\nSearching for .db files in project:")
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.db'):
                print(f"Found: {os.path.join(root, file)}")

if __name__ == "__main__":
    # Check database paths first
    check_database_paths()
    
    # Run the async test function
    asyncio.run(test_task_analytics())