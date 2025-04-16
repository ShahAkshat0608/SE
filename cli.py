import click
import os
import requests
from datetime import datetime
import getpass # For password input
import logging

from task_manager import TaskManager
# Import user management functions
from user_management.auth import (
    register_user,
    login_user,
    logout_user,
    get_current_user
)

# --- Configuration ---
USER_SERVICE_BASE_URL = os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:8001")
API_PREFIX = "/api/v1"
# Define path for session file relative to user's home or workspace
# For simplicity, placing it in the workspace root
SESSION_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '.logged_in_user'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a single instance of TaskManager
task_manager = TaskManager()

# --- Helper Functions for CLI Session ---

def save_login_session(user_id: int):
    """Saves the logged-in user ID to the session file."""
    try:
        with open(SESSION_FILE_PATH, 'w') as f:
            f.write(str(user_id))
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

def clear_login_session() -> bool:
    """Removes the session file."""
    if os.path.exists(SESSION_FILE_PATH):
        try:
            os.remove(SESSION_FILE_PATH)
            logging.info(f"Removed session file: {SESSION_FILE_PATH}")
            return True
        except IOError as e:
            click.echo(f"Error: Could not remove session file {SESSION_FILE_PATH}. {e}")
            logging.error(f"Failed to remove session file: {e}")
            return False
    return True # No file existed, so considered cleared

def get_current_user_details() -> dict | None:
    """Fetches details for the logged-in user from the user service."""
    user_id = get_logged_in_user_id()
    if not user_id:
        return None

    try:
        url = f"{USER_SERVICE_BASE_URL}{API_PREFIX}/auth/users/{user_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to user service: {e}")
        logging.error(f"Error fetching user details for ID {user_id}: {e}")
        # If user not found on server or connection error, invalidate local session
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
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
        response = requests.post(url, json=payload, timeout=10)
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
    """Log in to your account via the User Service."""
    url = f"{USER_SERVICE_BASE_URL}{API_PREFIX}/auth/login"
    payload = {"email": email, "password": password}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get('id')
            user_name = user_data.get('name', 'User')
            if user_id:
                save_login_session(user_id)
                click.echo(f"Welcome, {user_name}! You are now logged in.")
            else:
                click.echo("Login successful, but received invalid user data from server.")
                logging.error("Login API success but no user ID in response.")
        elif response.status_code == 401:
            click.echo(f"Error: {response.json().get('detail', 'Invalid email or password.')}")
        else:
            response.raise_for_status() # Raise for other errors
    except requests.exceptions.RequestException as e:
        click.echo(f"Login failed. Could not connect to user service: {e}")
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

if __name__ == '__main__':
    # Database initialization happens in the user service
    cli()
