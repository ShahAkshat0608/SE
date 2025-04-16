# CLI Task Manager (Microservice Architecture)

A command-line task manager built with Python, using a microservice architecture.

## Architecture

- **CLI (`cli.py`, `task_manager.py`, etc.)**: The main command-line interface. It interacts with the User Management service for authentication and manages tasks locally (for now).
- **User Management Service (`user-management/`)**: A FastAPI microservice responsible for user registration, login validation, and providing user details. It uses SQLite for data storage.
- **Analytics Service (`analytics-microservice/`)**: (Existing) Handles analytics.
- **Project Management Service (`project-management-microservice/`)**: (Existing)

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
- User data is stored in `user-management/src/main/data/users.db`.
- Task data is stored locally by `storage.py` (e.g., `tasks.json`).

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

4.  **Run the User Management Microservice:**
    Open a terminal in the project root and run:
    ```bash
    # Default port is 8001
    uvicorn user_management.src.main.main:app --reload --port 8001
    ```
    *(Note: `--reload` is for development. Use a production server like Gunicorn for deployment.)*
    The service API documentation will be available at `http://127.0.0.1:8001/docs`.

5.  **(Optional) Run Other Microservices:**
    Start the analytics or project management services in separate terminals if needed.

## CLI Usage (`taskman`)

Ensure the User Management service is running before using user-related commands.

### User Management

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

### Task Management (Requires Login)

These commands require a valid login session (checked via `whoami` logic).

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

## File Structure Overview

- `cli.py`: Main CLI entry point (uses `requests` to call User service).
- `task_manager.py`, `storage.py`, `task.py`: Local task management logic.
- `user-management/`:
  - `src/main/`:
    - `main.py`: FastAPI app entry point.
    - `api/`: FastAPI routers and endpoints.
    - `services/`: Business logic (e.g., `auth_service.py`).
    - `models/`: Database interaction (e.g., `user_model.py`).
    - `schemas/`: Pydantic data models.
    - `core/`: Configuration.
    - `data/`: Contains `users.db`.
- `analytics-microservice/`: Existing analytics service.
- `project-management-microservice/`: Existing project service.
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