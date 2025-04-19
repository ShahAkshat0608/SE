# CLI Task Manager (Microservice Architecture)

A command-line task manager built with Python, using a microservice architecture.

## Architecture

- **CLI (`cli.py`, `task_manager.py`, etc.)**: The main command-line interface. It interacts with all microservices and manages local tasks.
- **User Management Service (`user-management/`)**: A FastAPI microservice responsible for user registration, login validation, and providing user details. It uses SQLite for data storage.
- **Project Management Service (`project-management-microservice/`)**: Handles project creation, team management, milestones, and tasks.
- **Analytics Service (`analytics-microservice/`)**: Provides analytics and reporting functionality for projects, teams, and users.
- **Notification Service (`notification-microservice/`)**: Handles email notifications and calendar events.

## Features

- **User Management (via Microservice):**
  - Register new user accounts.
  - Login/Logout functionality (CLI manages local session state based on service responses).
  - Secure password storage (hashing) within the user service.
- **Task Management (CLI-local, requires login):**
  - Add, remove, and update tasks.
  - Mark tasks as complete/incomplete.
  - Filter tasks by status and priority.
  - Set due dates.
- **Project Management (via Microservice):**
  - Create and manage projects.
  - Create teams and assign team leads.
  - Create milestones and track progress.
  - Create tasks and subtasks with dependencies.
- **Analytics (via Microservice):**
  - View project, team, and user analytics.
  - Generate progress and workload reports.
  - Visualize data with charts.
- **Notifications (via Microservice):**
  - Send email notifications.
  - Schedule calendar events.

## Setup & Running

1.  **Clone Repository:**
    ```bash
    git clone <your-repo-url> # Replace with your repo URL
    cd <repo-folder-name>
    ```

2.  **Install Dependencies:**
    Install all dependencies for the CLI and services:
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Optional) Install CLI Tool:**
    Make the `taskman` command available system-wide:
    ```bash
    pip install -e .
    ```

4.  **Run the Microservices:**
    
    **Option 1: Start all services at once (recommended):**
    
    Use one of the provided scripts to start all services simultaneously:
    
    ```bash
    # Using Python script (cross-platform)
    python start_services.py
    
    # OR using Bash script (Linux/Mac)
    # First make it executable
    chmod +x start_services.sh
    ./start_services.sh
    ```
    
    To stop all services:
    ```bash
    # If using the Python script, press Ctrl+C in the terminal
    
    # OR if using the Bash script
    chmod +x stop_services.sh
    ./stop_services.sh
    ```
    
    The services will be available at the following URLs:
    - User Management: http://127.0.0.1:8001/docs
    - Project Management: http://127.0.0.1:8002/docs
    - Analytics: http://127.0.0.1:8003/docs
    - Notification: http://127.0.0.1:8004/docs
    
    All log files will be saved to the `logs` directory.
    
    **Option 2: Start services manually in separate terminals:**
    ```bash
    # User Management Service (port 8001)
    uvicorn user-management.src.main.main:app --reload --port 8001
    
    # Project Management Service (port 8002)
    uvicorn project-management-microservice.src.main:app --reload --port 8002
    
    # Analytics Service (port 8003)
    uvicorn analytics-microservice.src.main.main:app --reload --port 8003
    
    # Notification Service (port 8004)
    python notification-microservice/run.py
    ```
    *(Note: `--reload` is for development. Use a production server like Gunicorn for deployment.)*
    The service API documentation will be available at `http://127.0.0.1:[port]/docs`.

## Testing

The project includes a comprehensive test suite that tests all microservices. To run the tests:

1. **Start the microservices** using one of the methods described above.

2. **Run the test suite:**
   ```bash
   python run_tests.py
   ```
   
   This script will:
   - Check if all services are running
   - Offer to start services if they're not running
   - Run all tests for each microservice
   - Display a summary of the test results

3. **Run individual test files:**
   ```bash
   # Test user management service
   python -m tests.test_user_service
   
   # Test project management service
   python -m tests.test_project_service
   
   # Test analytics service  
   python -m tests.test_analytics_service
   
   # Test notification service
   python -m tests.test_notification_service
   ```

The test suite covers core functionality of each microservice, including:
- User registration and authentication
- Project creation and management
- Analytics data retrieval 
- Email notifications and calendar events

## CLI Usage Commands

Ensure all required microservices are running before using related commands.

### User Management Commands

```bash
# Register a new user (prompts for details, calls user service)
taskman register

# Log in (prompts for email/password, calls user service, saves session locally)
taskman login

# See who is logged in (reads local session, verifies with user service)
taskman whoami

# Log out (clears local session)
taskman logout
```

### Task Management Commands (Local, Requires Login)

```bash
# Add a task
taskman task add "Plan microservice integration" --priority high

# List all tasks
taskman task list

# List only completed tasks
taskman task list --completed

# List tasks by priority
taskman task list --priority high

# Mark a task as completed
taskman task complete <task_id>

# Mark a task as not completed
taskman task uncomplete <task_id>

# Show task details
taskman task show <task_id>

# Update a task
taskman task update <task_id> --description "New description" --priority medium --due "2024-06-01"

# Remove a task
taskman task remove <task_id>
```

### Project Management Commands

```bash
# Create a new project
taskman project create --name "New Project" --description "Project description"

# List all projects
taskman project list

# Get project details
taskman project show <project_id>

# Create a milestone
taskman project milestone add <project_id> --name "Milestone 1" --description "Description" --sequence 1 --due "2024-06-30"

# List project milestones
taskman project milestone list <project_id>

# Create a team
taskman project team create <project_id> --name "Team A" --lead-id <user_id> --type "DEVELOPMENT"

# List teams in a project
taskman project team list <project_id>

# Add team member
taskman team member add <team_id> --user-id <user_id>

# Remove team member
taskman team member remove <team_id> --user-id <user_id>

# Create a task for a team
taskman team task create <project_id> <team_id> --name "Task name" --description "Description" --priority high --due "2024-06-01"

# List team tasks
taskman team task list <project_id> <team_id>

# Create a subtask
taskman task subtask add <task_id> --name "Subtask name" --description "Description" --priority medium --due "2024-06-01"

# List subtasks
taskman task subtask list <task_id>

# Mark subtask as completed/uncompleted
taskman subtask complete <subtask_id> [--undo]

# Assign subtask to user
taskman subtask assign <subtask_id> --user-id <user_id>

# Define dependency between subtasks
taskman subtask dependency add <task_id> <subtask_id> <parent_subtask_id>

# View dependency tree
taskman task dependency-tree <task_id>

# Remove dependency
taskman subtask dependency remove <task_id> <subtask_id> <parent_subtask_id>

# Replace team lead
taskman project role update <project_id> <team_id> --new-lead <user_id>
```

### Analytics Commands

```bash
# View project analytics
taskman analytics project <project_id> [--type progress|workload|comprehensive] [--visualize]

# View team analytics
taskman analytics team <team_id> [--project-id <project_id>] [--type progress|workload|comprehensive] [--visualize]

# View user analytics
taskman analytics user [--type progress|workload|comprehensive] [--visualize]
```

### Notification Commands

```bash
# Send email notification
taskman notify email send --user-id <user_id> --email <email> --subject "Subject" --body "Message body"

# Process pending email notifications
taskman notify email process

# Schedule calendar event
taskman notify calendar schedule --user-id <user_id> --email <email> --summary "Meeting" --description "Description" --start "2024-06-01 10:00" --end "2024-06-01 11:00"

# Process pending calendar events
taskman notify calendar process
```

## File Structure Overview

- `cli.py`: Main CLI entry point (uses `requests` to call microservices).
- `task_manager.py`, `storage.py`, `task.py`: Local task management logic.
- `start_services.py`: Python script to start all microservices at once.
- `start_services.sh`: Bash script to start all microservices at once.
- `stop_services.sh`: Bash script to stop all microservices.
- `run_tests.py`: Python script to run all tests for the microservices.
- `tests/`: Directory containing test files for each microservice.
  - `test_user_service.py`: Tests for user management service.
  - `test_project_service.py`: Tests for project management service.
  - `test_analytics_service.py`: Tests for analytics service.
  - `test_notification_service.py`: Tests for notification service.
- `user-management/`:
  - `src/main/`:
    - `main.py`: FastAPI app entry point.
    - `api/`: FastAPI routers and endpoints.
    - `services/`: Business logic (e.g., `auth_service.py`).
    - `models/`: Database interaction (e.g., `user_model.py`).
    - `schemas/`: Pydantic data models.
    - `core/`: Configuration.
    - `data/`: Contains `users.db`.
- `project-management-microservice/`:
  - `src/`:
    - `main.py`: FastAPI app entry point.
    - `api/`: API routes and controllers.
    - `models/`: Data models.
    - `services/`: Business logic.
    - `database/`: Database management.
    - `workflow/`: Business workflows.
- `analytics-microservice/`:
  - `src/main/`:
    - `main.py`: FastAPI app entry point.
    - `api/`: API routes for analytics.
    - `services/`: Analytics services.
    - `models/`: Data models.
- `notification-microservice/`:
  - `src/main/`:
    - `main.py`: FastAPI app entry point.
    - `api/`: API endpoints for notifications.
    - `services/`: Email and calendar services.
    - `schemas/`: Data models.
- `requirements.txt`: All Python dependencies.
- `setup.py`: Project setup script.

## Dependencies

- Python 3.8+
- Click
- FastAPI
- Uvicorn
- Requests
- Werkzeug
- Pydantic
- Pydantic-Settings 