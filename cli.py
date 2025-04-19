import click
import os
import requests
from datetime import datetime
import getpass # For password input
import logging
import json

from task_manager import TaskManager

# --- Configuration ---
USER_SERVICE_BASE_URL = os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:8001")
PROJECT_SERVICE_BASE_URL = os.environ.get("PROJECT_SERVICE_URL", "http://127.0.0.1:8002")
ANALYTICS_SERVICE_BASE_URL = os.environ.get("ANALYTICS_SERVICE_URL", "http://127.0.0.1:8003")
NOTIFICATION_SERVICE_BASE_URL = os.environ.get("NOTIFICATION_SERVICE_URL", "http://127.0.0.1:8004")
API_PREFIX = "/api/v1"
ANALYTICS_API_PREFIX = "/api/analytics"
# Define path for session file relative to user's home or workspace
# For simplicity, placing it in the workspace root
SESSION_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '.logged_in_user'))
TOKEN_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '.auth_token'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a single instance of TaskManager
task_manager = TaskManager()

# --- Helper Functions for CLI Session ---

def save_login_session(user_id: int, token: str):
    """Saves the logged-in user ID to the session file and token."""
    try:
        with open(SESSION_FILE_PATH, 'w') as f:
            f.write(str(user_id))
        with open(TOKEN_FILE_PATH, 'w') as f:
            f.write(token)
        logging.info(f"Saved login session for user ID {user_id} to {SESSION_FILE_PATH}")
    except IOError as e:
        click.echo(f"Error: Could not save login session to {SESSION_FILE_PATH}. {e}")
        logging.error(f"Failed to write session file: {e}")

def get_logged_in_user_id() -> int | None:
    """Gets the user ID from the session file."""
    if not os.path.exists(SESSION_FILE_PATH):
        return None
    try:
        with open(SESSION_FILE_PATH, 'r') as f:
            user_id_str = f.read().strip()
            if user_id_str:
                return int(user_id_str)
            else:
                # Clean up empty file
                clear_login_session()
                return None
    except (IOError, ValueError) as e:
        logging.error(f"Failed to read or parse session file {SESSION_FILE_PATH}: {e}")
        clear_login_session() # Clean up corrupted file
        return None

def get_auth_token() -> str | None:
    """Gets the authentication token."""
    if not os.path.exists(TOKEN_FILE_PATH):
        return None
    try:
        with open(TOKEN_FILE_PATH, 'r') as f:
            token = f.read().strip()
            return token if token else None
    except IOError as e:
        logging.error(f"Failed to read token file {TOKEN_FILE_PATH}: {e}")
        return None

def clear_login_session() -> bool:
    """Removes the session file and token file."""
    success = True
    if os.path.exists(SESSION_FILE_PATH):
        try:
            os.remove(SESSION_FILE_PATH)
            logging.info(f"Removed session file: {SESSION_FILE_PATH}")
        except IOError as e:
            click.echo(f"Error: Could not remove session file {SESSION_FILE_PATH}. {e}")
            logging.error(f"Failed to remove session file: {e}")
            success = False
    
    if os.path.exists(TOKEN_FILE_PATH):
        try:
            os.remove(TOKEN_FILE_PATH)
            logging.info(f"Removed token file: {TOKEN_FILE_PATH}")
        except IOError as e:
            click.echo(f"Error: Could not remove token file {TOKEN_FILE_PATH}. {e}")
            logging.error(f"Failed to remove token file: {e}")
            success = False
            
    return success

def get_current_user_details() -> dict | None:
    """Fetches details for the logged-in user from the project management service."""
    token = get_auth_token()
    
    if not token:
        return None

    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/auth/me"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=5)
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to project management service: {e}")
        logging.error(f"Error fetching user details: {e}")
        # If user not found on server or connection error, invalidate local session
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code in (401, 404):
            click.echo("Your login session seems invalid. Please log in again.")
            clear_login_session()
        return None
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")
        logging.error(f"Unexpected error fetching user details: {e}")
        return None

@click.group()
def cli():
    """Task Manager CLI - Manage your tasks and user account via microservices."""
    pass

# --- User Management Commands (using API) ---

@cli.command()
@click.option('--name', prompt=True, help='Your full name')
@click.option('--email', prompt=True, help='Your email address')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Your password')
@click.option('--contact', prompt=True, required=False, default=None, help='Your contact number (optional)')
def register(name, email, password, contact):
    """Register a new user account via the User Service."""
    url = f"{USER_SERVICE_BASE_URL}{API_PREFIX}/auth/register"
    payload = {"name": name, "email": email, "password": password, "contact": contact}
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 201:
            user_data = response.json()
            click.echo(f"User '{user_data.get('name')}' registered successfully with ID: {user_data.get('id')}.")
        elif response.status_code == 409:
            click.echo(f"Error: {response.json().get('detail', 'Email already registered.')}")
        else:
            response.raise_for_status() # Raise for other errors
    except requests.exceptions.RequestException as e:
        click.echo(f"Registration failed. Could not connect to user service: {e}")
        logging.error(f"Registration API call failed: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred during registration: {e}")
        logging.error(f"Unexpected registration error: {e}")

@cli.command()
@click.option('--email', prompt=True, help='Your email address')
@click.option('--password', prompt=True, hide_input=True, help='Your password')
def login(email, password):
    """Log in to your account via the Project Management Service."""
    url = f"{PROJECT_SERVICE_BASE_URL}/api/auth/login"
    try:
        response = requests.post(url, params={"email": email, "password": password}, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            access_token = user_data.get('access_token')
            user = user_data.get('user', {})
            user_id = user.get('id')
            user_name = user.get('name', 'User')
            if user_id and access_token:
                save_login_session(user_id, access_token)
                click.echo(f"Welcome, {user_name}! You are now logged in.")
            else:
                click.echo("Login successful, but received invalid user data from server.")
                logging.error("Login API success but no user ID or token in response.")
        elif response.status_code == 401:
            click.echo(f"Error: {response.json().get('detail', 'Invalid email or password.')}")
        else:
            response.raise_for_status() # Raise for other errors
    except requests.exceptions.RequestException as e:
        click.echo(f"Login failed. Could not connect to project management service: {e}")
        logging.error(f"Login API call failed: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred during login: {e}")
        logging.error(f"Unexpected login error: {e}")

@cli.command()
def logout():
    """Log out of your account (clears local session)."""
    user_id = get_logged_in_user_id()
    if user_id:
        # Optionally call a logout endpoint on the service if it manages server-side sessions
        # For now, just clear the local file
        if clear_login_session():
            click.echo("You have been logged out.")
        else:
            click.echo("Logout failed. Could not clear local session.")
    else:
        click.echo("You are not currently logged in.")

@cli.command()
def whoami():
    """Show the currently logged-in user by checking the service."""
    user = get_current_user_details()
    if user:
        click.echo(f"Logged in as: {user.get('name')} ({user.get('email')}) ID: {user.get('id')}")
    else:
        # Check if a session file exists but fetching failed
        if get_logged_in_user_id() is not None:
             click.echo("Login session is present but couldn't verify with the user service.")
        else:
            click.echo("Not logged in.")

# --- Task Management Commands (grouped, requires login check) ---

@click.group(name='task')
def task_group():
    """Manage tasks (requires login)."""
    # Check login status by verifying with the user service
    if not get_current_user_details(): # This now calls the API
        click.echo("Error: You must be logged in to manage tasks. Use 'taskman login' first.")
        exit(1) # Exit if not logged in or session invalid
    pass

@task_group.command(name='add')
@click.argument('description')
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high"]), default="medium", help="Task priority level")
@click.option("--due", "-d", type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%d %H:%M"]), help="Due date (YYYY-MM-DD)")
def add_task(description, priority, due):
    """Add a new task with description, priority and due date."""
    result = task_manager.add_task(description, priority, due)
    click.echo(result)

@task_group.command(name='list')
@click.option("--all", "-a", is_flag=True, help="Show all tasks including completed ones")
@click.option("--completed", "-c", is_flag=True, help="Show only completed tasks")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high"]), help="Filter by priority")
def list_tasks(all, completed, priority):
    """List tasks with optional filtering."""
    filter_completed = None
    if not all:
        filter_completed = True if completed else False
    
    tasks = task_manager.get_tasks(filter_completed, priority)
    
    if not tasks:
        click.echo("No tasks found.")
        return
    
    click.echo(f"\nFound {len(tasks)} tasks:")
    click.echo("=" * 50)
    for i, task in enumerate(tasks, 1):
        click.echo(f"{i}. {task}")
    click.echo("=" * 50)

@task_group.command(name='complete')
@click.argument('task_id')
def complete_task(task_id):
    """Mark a task as completed."""
    result = task_manager.complete_task(task_id)
    click.echo(result)

@task_group.command(name='uncomplete')
@click.argument('task_id')
def uncomplete_task(task_id):
    """Mark a task as not completed."""
    result = task_manager.uncomplete_task(task_id)
    click.echo(result)

@task_group.command(name='remove')
@click.argument('task_id')
def remove_task(task_id):
    """Remove a task by its ID."""
    result = task_manager.remove_task(task_id)
    click.echo(result)

@task_group.command(name='update')
@click.argument('task_id')
@click.option('--description', '-d', help="New task description")
@click.option('--priority', '-p', type=click.Choice(["low", "medium", "high"]), help="New priority")
@click.option('--due', type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%d %H:%M"]), help="New due date (YYYY-MM-DD)")
@click.option('--clear-due', is_flag=True, help="Clear the due date")
def update_task(task_id, description, priority, due, clear_due):
    """Update task details."""
    if clear_due:
        due = None
    elif due is None:
        # Keep the existing due date if not specified
        pass
        
    result = task_manager.update_task(task_id, description, priority, due)
    click.echo(result)

@task_group.command(name='show')
@click.argument('task_id')
def show_task(task_id):
    """Show details of a specific task."""
    task = task_manager.get_task(task_id)
    if task:
        click.echo(f"\nTask Details:")
        click.echo("=" * 50)
        click.echo(f"ID: {task.id}")
        click.echo(f"Description: {task.description}")
        click.echo(f"Priority: {task.priority}")
        click.echo(f"Status: {'Completed' if task.completed else 'Pending'}")
        if task.due_date:
            click.echo(f"Due date: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
        click.echo(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        click.echo("=" * 50)
    else:
        click.echo(f"Error: Task with ID '{task_id}' not found")

# Add task commands under the main cli group
cli.add_command(task_group)

# --- Project Management Commands ---
@cli.group(name='project')
def project_group():
    """Manage projects (requires login)."""
    # Check login status by verifying with the user service
    token = get_auth_token()
    if not get_current_user_details() or not token:
        click.echo("Error: You must be logged in to manage projects. Use 'taskman login' first.")
        exit(1)
    pass

@project_group.command(name='create')
@click.option('--name', required=True, help='Project name')
@click.option('--description', required=False, default="", help='Project description')
def create_project(name, description):
    """Create a new project."""
    user = get_current_user_details()
    token = get_auth_token()
    if not user or not token:
        click.echo("Failed to retrieve user information.")
        return
    
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects"
        payload = {"name": name, "description": description, "owner_id": user["id"]}
        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 201:
            project_data = response.json()
            click.echo(f"Project '{project_data.get('name')}' created successfully with ID: {project_data.get('id')}.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Project creation failed: {e}")
        logging.error(f"Project creation API call failed: {e}")

@project_group.command(name='list')
def list_projects():
    """List all projects for the current user."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            projects = response.json()
            
            if not projects:
                click.echo("No projects found.")
                return
            
            click.echo("\nYour projects:")
            click.echo("=" * 50)
            for i, project in enumerate(projects, 1):
                click.echo(f"{i}. ID: {project['id']}, Name: {project['name']}")
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve projects: {e}")
        logging.error(f"Project list API call failed: {e}")

@project_group.command(name='show')
@click.argument('project_identifier')
def show_project(project_identifier):
    """Get details of a specific project."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
    
    # First, try to get all projects to handle numeric indexes
    project_id = project_identifier
    try:
        # Check if the identifier is a numeric index
        if project_identifier.isdigit():
            # Get the list of projects first
            list_url = f"{PROJECT_SERVICE_BASE_URL}/api/projects"
            list_response = requests.get(list_url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            
            if list_response.status_code == 200:
                projects = list_response.json()
                idx = int(project_identifier) - 1  # Convert to 0-based index
                
                if 0 <= idx < len(projects):
                    project_id = projects[idx]["id"]
                else:
                    click.echo(f"Invalid project index: {project_identifier}. Please use a valid project ID or index.")
                    return
            else:
                # If we can't get the list, fall back to using the identifier as is
                pass
                
        # Now use the project_id to get details
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            project_data = response.json()
            click.echo("\nProject Details:")
            click.echo("=" * 50)
            click.echo(f"ID: {project_data.get('id')}")
            click.echo(f"Name: {project_data.get('name')}")
            click.echo(f"Description: {project_data.get('description', 'No description')}")
            click.echo(f"Owner ID: {project_data.get('owner_id')}")
            click.echo(f"Created At: {project_data.get('created_at')}")
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve project details: {e}")
        logging.error(f"Project details API call failed: {e}")

# --- Project Milestone Commands ---
@project_group.group(name='milestone')
def milestone_group():
    """Manage project milestones."""
    pass

@milestone_group.command(name='add')
@click.argument('project_id')
@click.option('--name', required=True, help='Milestone name')
@click.option('--description', required=True, help='Milestone description')
@click.option('--sequence', required=True, type=int, help='Milestone sequence number')
@click.option('--due', help='Due date (YYYY-MM-DD)')
def add_milestone(project_id, name, description, sequence, due):
    """Add a milestone to a project."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}/milestones"
        payload = {
            "milestone_name": name,
            "milestone_description": description,
            "milestone_sequence_no": sequence
        }
        if due:
            payload["milestone_due_date"] = due
            
        response = requests.post(url, params=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            milestone_data = response.json()
            click.echo(f"Milestone '{milestone_data.get('name')}' added successfully with ID: {milestone_data.get('id')}.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to add milestone: {e}")
        logging.error(f"Milestone creation API call failed: {e}")

@milestone_group.command(name='list')
@click.argument('project_id')
def list_milestones(project_id):
    """List all milestones for a project."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}/milestones"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            milestones = response.json()
            
            if not milestones:
                click.echo("No milestones found.")
                return
            
            click.echo("\nProject Milestones:")
            click.echo("=" * 50)
            for i, milestone in enumerate(milestones, 1):
                due_date = milestone.get('due_date', 'No due date')
                click.echo(f"{i}. ID: {milestone['id']}, Name: {milestone['name']}, Sequence: {milestone['sequence_no']}, Due: {due_date}")
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve milestones: {e}")
        logging.error(f"Milestone list API call failed: {e}")

# --- Project Team Commands ---
@project_group.group(name='team')
def team_group():
    """Manage project teams."""
    pass

@team_group.command(name='create')
@click.argument('project_id')
@click.option('--name', required=True, help='Team name')
@click.option('--lead-id', required=True, help='User ID of team lead')
@click.option('--type', required=False, help='Team type')
def create_team(project_id, name, lead_id, type):
    """Create a team in a project."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}/teams"
        payload = {
            "team_name": name,
            "team_lead_id": lead_id
        }
        if type:
            payload["team_type"] = type
            
        response = requests.post(url, params=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            team_data = response.json()
            click.echo(f"Team '{team_data.get('name')}' created successfully with ID: {team_data.get('id')}.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to create team: {e}")
        logging.error(f"Team creation API call failed: {e}")

@team_group.command(name='list')
@click.argument('project_id')
def list_teams(project_id):
    """List all teams for a project."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}/teams"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            teams = response.json()
            
            if not teams:
                click.echo("No teams found.")
                return
            
            click.echo("\nProject Teams:")
            click.echo("=" * 50)
            for i, team in enumerate(teams, 1):
                click.echo(f"{i}. ID: {team['id']}, Name: {team['name']}, Lead ID: {team['team_lead_id']}")
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve teams: {e}")
        logging.error(f"Team list API call failed: {e}")

# --- Team Member Commands ---
@cli.group(name='team')
def team_operations_group():
    """Team operations (requires login)."""
    # Check login status by verifying with the user service
    if not get_current_user_details():
        click.echo("Error: You must be logged in to manage teams. Use 'taskman login' first.")
        exit(1)
    pass

@team_operations_group.group(name='member')
def team_member_group():
    """Manage team members."""
    pass

@team_member_group.command(name='add')
@click.argument('team_id')
@click.option('--user-id', required=True, help='User ID to add to team')
def add_team_member(team_id, user_id):
    """Add a user to a team."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/teams/{team_id}/members"
        payload = {"member_id": user_id}
        response = requests.post(url, params=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            click.echo(f"User {user_id} added to team successfully.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to add team member: {e}")
        logging.error(f"Team member addition API call failed: {e}")

@team_member_group.command(name='remove')
@click.argument('team_id')
@click.option('--user-id', required=True, help='User ID to remove from team')
def remove_team_member(team_id, user_id):
    """Remove a user from a team."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/teams/{team_id}/members/{user_id}"
        response = requests.delete(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            click.echo(f"User {user_id} removed from team successfully.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to remove team member: {e}")
        logging.error(f"Team member removal API call failed: {e}")

# --- Team Task Commands ---
@team_operations_group.group(name='task')
def team_task_group():
    """Manage team tasks."""
    pass

@team_task_group.command(name='create')
@click.argument('project_id')
@click.argument('team_id')
@click.option('--name', required=True, help='Task name')
@click.option('--description', required=True, help='Task description')
@click.option('--priority', type=click.Choice(['LOW', 'MEDIUM', 'HIGH']), default='MEDIUM', help='Task priority')
@click.option('--due', help='Due date (YYYY-MM-DD)')
def create_team_task(project_id, team_id, name, description, priority, due):
    """Create a task for a team."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}/teams/{team_id}/tasks"
        payload = {
            "task_name": name,
            "task_description": description,
            "task_priority": priority
        }
        if due:
            payload["task_due_date"] = due
            
        response = requests.post(url, params=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            task_data = response.json()
            click.echo(f"Task '{task_data.get('name')}' created successfully with ID: {task_data.get('id')}.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to create task: {e}")
        logging.error(f"Task creation API call failed: {e}")

@team_task_group.command(name='list')
@click.argument('project_id')
@click.argument('team_id')
def list_team_tasks(project_id, team_id):
    """List all tasks for a team."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}/teams/{team_id}/tasks"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            tasks = response.json()
            
            if not tasks:
                click.echo("No tasks found.")
                return
            
            click.echo("\nTeam Tasks:")
            click.echo("=" * 50)
            for i, task in enumerate(tasks, 1):
                click.echo(f"{i}. ID: {task['id']}, Name: {task['name']}, Status: {task['status']}, Priority: {task['priority']}")
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve tasks: {e}")
        logging.error(f"Task list API call failed: {e}")

# --- Task Subtask Commands ---
@cli.group(name='task')
def task_operations_group():
    """Task operations (requires login)."""
    # Check login status by verifying with the user service
    if not get_current_user_details():
        click.echo("Error: You must be logged in to manage tasks. Use 'taskman login' first.")
        exit(1)
    pass

@task_operations_group.group(name='subtask')
def subtask_group():
    """Manage subtasks."""
    pass

@subtask_group.command(name='add')
@click.argument('task_id')
@click.option('--name', required=True, help='Subtask name')
@click.option('--description', required=True, help='Subtask description')
@click.option('--priority', type=click.Choice(['LOW', 'MEDIUM', 'HIGH']), default='MEDIUM', help='Subtask priority')
@click.option('--due', help='Due date (YYYY-MM-DD)')
@click.option('--milestone-id', help='Milestone ID')
@click.option('--tags', help='Comma-separated tags')
def add_subtask(task_id, name, description, priority, due, milestone_id, tags):
    """Add a subtask to a task."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/tasks/{task_id}/subtasks"
        payload = {
            "subtask_name": name,
            "subtask_description": description,
            "subtask_priority": priority
        }
        if due:
            payload["subtask_due_date"] = due
        if milestone_id:
            payload["subtask_milestone_id"] = milestone_id
        if tags:
            payload["subtask_tags"] = tags.split(',')
            
        response = requests.post(url, params=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            subtask_data = response.json()
            click.echo(f"Subtask '{subtask_data.get('name')}' added successfully with ID: {subtask_data.get('id')}.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to add subtask: {e}")
        logging.error(f"Subtask creation API call failed: {e}")

@subtask_group.command(name='list')
@click.argument('task_id')
def list_subtasks(task_id):
    """List all subtasks for a task."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/tasks/{task_id}/subtasks"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            subtasks = response.json()
            
            if not subtasks:
                click.echo("No subtasks found.")
                return
            
            click.echo("\nTask Subtasks:")
            click.echo("=" * 50)
            for i, subtask in enumerate(subtasks, 1):
                # Use .get() method with default values to avoid KeyError
                subtask_id = subtask.get('id', 'N/A')
                name = subtask.get('name', 'N/A')
                status = subtask.get('status', 'N/A')
                priority = subtask.get('priority', 'N/A')
                click.echo(f"{i}. ID: {subtask_id}, Name: {name}, Status: {status}, Priority: {priority}")
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve subtasks: {e}")
        logging.error(f"Subtask list API call failed: {e}")

@cli.command(name='subtask')
@click.argument('subtask_id')
@click.argument('command', type=click.Choice(['complete', 'assign']))
@click.option('--undo', is_flag=True, help='Undo completion (for complete command)')
@click.option('--user-id', help='User ID to assign subtask to (for assign command)')
def subtask_operations(subtask_id, command, undo, user_id):
    """Perform operations on a subtask."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
    
    try:
        if command == "complete":
            url = f"{PROJECT_SERVICE_BASE_URL}/api/subtasks/{subtask_id}/completion"
            payload = {"isCompleted": not undo}
            response = requests.put(url, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            success_msg = "marked as complete" if not undo else "marked as incomplete"
        
        elif command == "assign" and user_id:
            url = f"{PROJECT_SERVICE_BASE_URL}/api/subtasks/{subtask_id}/assign"
            payload = {"assign_user_id": user_id}
            response = requests.put(url, params=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            success_msg = f"assigned to user {user_id}"
        else:
            click.echo("Error: For 'assign' command, you must provide a user-id.")
            return
        
        if response.status_code == 200:
            click.echo(f"Subtask {success_msg} successfully.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to perform subtask operation: {e}")
        logging.error(f"Subtask operation API call failed: {e}")

# --- Subtask Dependency Commands ---
@subtask_group.group(name='dependency')
def dependency_group():
    """Manage subtask dependencies."""
    pass

@dependency_group.command(name='add')
@click.argument('task_id')
@click.argument('subtask_id')
@click.argument('parent_subtask_id')
def add_dependency(task_id, subtask_id, parent_subtask_id):
    """Add a dependency between subtasks."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/subtasks/{subtask_id}/dependencies"
        params = {"task_id": task_id, "parent_subtask_id": parent_subtask_id}
        response = requests.post(url, params=params, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            click.echo(f"Dependency added successfully.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to add dependency: {e}")
        logging.error(f"Dependency creation API call failed: {e}")

@dependency_group.command(name='remove')
@click.argument('task_id')
@click.argument('subtask_id')
@click.argument('parent_subtask_id')
def remove_dependency(task_id, subtask_id, parent_subtask_id):
    """Remove a dependency between subtasks."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/subtasks/{subtask_id}/{parent_subtask_id}/dependencies"
        params = {"task_id": task_id}
        response = requests.delete(url, params=params, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            click.echo(f"Dependency removed successfully.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to remove dependency: {e}")
        logging.error(f"Dependency removal API call failed: {e}")

@task_operations_group.command(name='dependency-tree')
@click.argument('task_id')
def dependency_tree(task_id):
    """View dependency tree for a task."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/tasks/{task_id}/dependency-tree"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            tree_data = response.json()
            click.echo("\nTask Dependency Tree:")
            click.echo("=" * 50)
            # Pretty print the tree (simplified for now)
            click.echo(tree_data)
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve dependency tree: {e}")
        logging.error(f"Dependency tree API call failed: {e}")

# --- Project Role Commands ---
@project_group.command(name='role')
@click.argument('command', type=click.Choice(['list', 'update']))
@click.argument('project_id')
@click.option('--team-id', help='Team ID (for update command)')
@click.option('--new-lead', help='New team lead user ID (for update command)')
def project_roles(command, project_id, team_id, new_lead):
    """Manage project roles."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
    
    try:
        if command == "list":
            url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}/roles"
            response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            
            if response.status_code == 200:
                roles = response.json()
                
                if not roles:
                    click.echo("No roles found for this project.")
                    return
                
                click.echo("\nProject Roles:")
                click.echo("=" * 50)
                for i, role in enumerate(roles, 1):
                    click.echo(f"{i}. User ID: {role['user_id']}, Role: {role['role']}")
                click.echo("=" * 50)
            else:
                response.raise_for_status()
                
        elif command == "update":
            if not team_id or not new_lead:
                click.echo("Error: Both team-id and new-lead must be provided for the update command.")
                return
                
            url = f"{PROJECT_SERVICE_BASE_URL}/api/projects/{project_id}/roles"
            payload = {
                "team_id": team_id,
                "new_team_lead_id": new_lead
            }
            response = requests.post(url, params=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
            
            if response.status_code == 200:
                click.echo(f"Team lead updated successfully.")
            else:
                response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to perform role operation: {e}")
        logging.error(f"Role operation API call failed: {e}")

# --- Analytics Commands ---
@cli.group(name='analytics')
def analytics_group():
    """View analytics for projects, teams, and users."""
    token = get_auth_token()
    if not get_current_user_details() or not token:
        click.echo("Error: You must be logged in to view analytics. Use 'taskman login' first.")
        exit(1)
    pass

@analytics_group.command(name='project')
@click.argument('project_id')
@click.option('--type', type=click.Choice(['progress', 'workload', 'comprehensive']), default='comprehensive', help='Report type')
@click.option('--visualize', is_flag=True, help='Include visualization data')
def project_analytics(project_id, type, visualize):
    """View project analytics."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{ANALYTICS_SERVICE_BASE_URL}{ANALYTICS_API_PREFIX}/project/{project_id}"
        params = {"report_type": type, "visualize": visualize}
        response = requests.get(url, params=params, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            analytics_data = response.json()
            click.echo("\nProject Analytics:")
            click.echo("=" * 50)
            click.echo(json.dumps(analytics_data, indent=2))
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve project analytics: {e}")
        logging.error(f"Project analytics API call failed: {e}")

@analytics_group.command(name='team')
@click.argument('team_id')
@click.option('--project-id', help='Project ID')
@click.option('--type', type=click.Choice(['progress', 'workload', 'comprehensive']), default='comprehensive', help='Report type')
@click.option('--visualize', is_flag=True, help='Include visualization data')
def team_analytics(team_id, project_id, type, visualize):
    """View team analytics."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{ANALYTICS_SERVICE_BASE_URL}{ANALYTICS_API_PREFIX}/team/{team_id}"
        params = {"report_type": type, "visualize": visualize}
        if project_id:
            params["project_id"] = project_id
            
        response = requests.get(url, params=params, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            analytics_data = response.json()
            click.echo("\nTeam Analytics:")
            click.echo("=" * 50)
            click.echo(json.dumps(analytics_data, indent=2))
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve team analytics: {e}")
        logging.error(f"Team analytics API call failed: {e}")

@analytics_group.command(name='user')
@click.option('--type', type=click.Choice(['progress', 'workload', 'comprehensive']), default='comprehensive', help='Report type')
@click.option('--visualize', is_flag=True, help='Include visualization data')
def user_analytics(type, visualize):
    """View user analytics."""
    token = get_auth_token()
    user = get_current_user_details()
    if not token or not user:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{ANALYTICS_SERVICE_BASE_URL}{ANALYTICS_API_PREFIX}/user/{user['id']}"
        params = {"report_type": type, "visualize": visualize}
        response = requests.get(url, params=params, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        
        if response.status_code == 200:
            analytics_data = response.json()
            click.echo("\nUser Analytics:")
            click.echo("=" * 50)
            click.echo(json.dumps(analytics_data, indent=2))
            click.echo("=" * 50)
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to retrieve user analytics: {e}")
        logging.error(f"User analytics API call failed: {e}")

# --- Notification Commands ---
@cli.group(name='notify')
def notification_group():
    """Send notifications and schedule calendar events."""
    if not get_current_user_details():
        click.echo("Error: You must be logged in to send notifications. Use 'taskman login' first.")
        exit(1)
    pass

@notification_group.group(name='email')
def email_group():
    """Email notification operations."""
    pass

@email_group.command(name='send')
@click.option('--user-id', required=True, help='User ID to send email to')
@click.option('--email', required=True, help='Email address')
@click.option('--subject', required=True, help='Email subject')
@click.option('--body', required=True, help='Email body')
def send_email(user_id, email, subject, body):
    """Send an email notification."""
    try:
        url = f"{NOTIFICATION_SERVICE_BASE_URL}/notifications/email"
        payload = {
            "user_id": user_id,
            "email": email,
            "subject": subject,
            "body": body
        }
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 201:
            notification_data = response.json()
            click.echo(f"Email notification sent successfully with ID: {notification_data.get('id')}.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to send email notification: {e}")
        logging.error(f"Email notification API call failed: {e}")

@email_group.command(name='process')
def process_email_queue():
    """Process pending email notifications."""
    try:
        url = f"{NOTIFICATION_SERVICE_BASE_URL}/notifications/email/process"
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            click.echo(result.get("message", "Processed email queue successfully."))
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to process email queue: {e}")
        logging.error(f"Email queue processing API call failed: {e}")

@notification_group.group(name='calendar')
def calendar_group():
    """Calendar event operations."""
    pass

@calendar_group.command(name='schedule')
@click.option('--user-id', required=True, help='User ID to schedule event for')
@click.option('--email', required=True, help='Email address')
@click.option('--summary', required=True, help='Event summary')
@click.option('--description', required=True, help='Event description')
@click.option('--start', required=True, help='Start time (YYYY-MM-DD HH:MM)')
@click.option('--end', required=True, help='End time (YYYY-MM-DD HH:MM)')
def schedule_calendar_event(user_id, email, summary, description, start, end):
    """Schedule a calendar event."""
    try:
        url = f"{NOTIFICATION_SERVICE_BASE_URL}/notifications/calendar"
        payload = {
            "user_id": user_id,
            "email": email,
            "summary": summary,
            "description": description,
            "start_time": start,
            "end_time": end
        }
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 201:
            event_data = response.json()
            click.echo(f"Calendar event scheduled successfully with ID: {event_data.get('id')}.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to schedule calendar event: {e}")
        logging.error(f"Calendar event API call failed: {e}")

@calendar_group.command(name='process')
def process_calendar_queue():
    """Process pending calendar events."""
    try:
        url = f"{NOTIFICATION_SERVICE_BASE_URL}/notifications/calendar/process"
        response = requests.post(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            click.echo(result.get("message", "Processed calendar queue successfully."))
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to process calendar queue: {e}")
        logging.error(f"Calendar queue processing API call failed: {e}")

@subtask_group.command(name='auto-generate')
@click.argument('task_id')
@click.option('--description', required=True, help='Main task description to generate subtasks from')
@click.option('--priority', type=click.Choice(['LOW', 'MEDIUM', 'HIGH']), default='MEDIUM', help='Default priority for generated subtasks')
@click.option('--due', help='Due date for generated subtasks (YYYY-MM-DD)')
@click.option('--milestone-id', help='Milestone ID for generated subtasks')
@click.option('--tags', help='Comma-separated tags for generated subtasks')
def auto_generate_subtasks(task_id, description, priority, due, milestone_id, tags):
    """Use AI to automatically generate 3-6 subtasks for a task."""
    token = get_auth_token()
    if not token:
        click.echo("You must be logged in to use this command.")
        return
        
    try:
        url = f"{PROJECT_SERVICE_BASE_URL}/api/tasks/{task_id}/subtasks_auto"
        
        # Build request parameters
        payload = {
            "main_task_description": description,
            "subtask_priority": priority
        }
        
        if due:
            payload["subtask_due_date"] = due
        if milestone_id:
            payload["subtask_milestone_id"] = milestone_id
        if tags:
            payload["subtask_tags"] = tags.split(',')
            
        response = requests.post(url, params=payload, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Check if the response has the expected structure
            if not response_data or "subtasks" not in response_data:
                click.echo("No subtasks were generated or unexpected response format.")
                return
                
            results = response_data["subtasks"]
            if not results:
                click.echo("No subtasks were generated.")
                return
                
            click.echo("\nAI-generated subtasks:")
            click.echo("=" * 50)
            for i, subtask in enumerate(results, 1):
                # Check if the subtask is a dictionary before using .get()
                if isinstance(subtask, dict):
                    name = subtask.get('name', 'No name')
                    description = subtask.get('description', 'No description')
                    priority = subtask.get('priority', 'No priority')
                    subtask_id = subtask.get('id', 'No ID')
                    click.echo(f"{i}. {name}: {description}")
                    click.echo(f"   Priority: {priority}, ID: {subtask_id}")
                else:
                    # Handle the case where subtask might be a string
                    click.echo(f"{i}. {subtask}")
            click.echo("=" * 50)
            click.echo(f"Successfully generated {len(results)} subtasks!")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.echo(f"Failed to generate subtasks: {e}")
        logging.error(f"Subtask AI generation API call failed: {e}")

@cli.command(name='my-subtasks')
def get_my_subtasks():
    """List all subtasks assigned to the current user."""
    # Check login status
    current_user = get_current_user_details()
    if not current_user:
        click.echo("Error: You must be logged in to view your subtasks. Use 'login' command first.")
        return
    
    token = get_auth_token()
    url = f"{PROJECT_SERVICE_BASE_URL}/api/user/subtasks"
    
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=5)
        response.raise_for_status()
        
        subtasks = response.json()
        
        if not subtasks:
            click.echo("You have no assigned subtasks.")
            return
        
        click.echo("\nYour assigned subtasks:")
        click.echo("=" * 80)
        for i, subtask in enumerate(subtasks, 1):
            status = "✓" if subtask.get("is_completed") else "□"
            priority = subtask.get("priority", "MEDIUM")
            name = subtask.get("name", "Unnamed subtask")
            id = subtask.get("id", "unknown")
            due_date = subtask.get("due_date", "No due date")
            
            # Format priority with color if available
            if priority == "HIGH":
                priority_text = click.style(f"[{priority}]", fg="red", bold=True)
            elif priority == "MEDIUM":
                priority_text = click.style(f"[{priority}]", fg="yellow")
            else:
                priority_text = click.style(f"[{priority}]", fg="green")
            
            # Format status with color
            status_text = click.style(status, fg="green" if status == "✓" else "yellow")
            
            click.echo(f"{i}. {status_text} {priority_text} {name} (ID: {id})")
            click.echo(f"   Due: {due_date}")
            if "description" in subtask:
                description = subtask["description"]
                # Truncate long descriptions
                if len(description) > 60:
                    description = description[:57] + "..."
                click.echo(f"   {description}")
            click.echo("-" * 80)
        
        click.echo("\nTip: Use 'subtask <subtask_id> complete' to mark a subtask as completed.")
        
    except requests.exceptions.RequestException as e:
        click.echo(f"Error fetching your subtasks: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

# Entry point for the CLI
if __name__ == "__main__":
    cli()
