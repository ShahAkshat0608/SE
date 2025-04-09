# CLI Project Manager

A command-line project management system built with Python, designed as a microservice for task management.

## Features

- Create and manage projects
- Add team members to projects
- Link tasks to projects
- Track project status (active, completed, archived)
- View project analytics
- Persist project data to JSON files
- Support for multiple project roles (owner, admin, member)

## Installation

1. Navigate to the project service directory:
```
cd services/project_service
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Create a symlink to make the CLI accessible globally (optional):
```
pip install -e .
```

## Usage

### Create a new project
```
python cli.py create "Website Redesign" "Redesign company website" --owner user123
```

### List all projects
```
python cli.py list
```

### List projects by status
```
python cli.py list --status active
```

### List projects by owner
```
python cli.py list --owner user123
```

### Add member to project
```
python cli.py add-member <project_id> <user_id>
```

### Add task to project
```
python cli.py add-task <project_id> <task_id>
```

### Update project status
```
python cli.py update-status <project_id> completed
```

### Show project details
```
python cli.py show <project_id>
```

### Remove project
```
python cli.py remove <project_id>
```

## File Structure

- `src/`
  - `models/project.py`: Project model class
  - `storage/project_storage.py`: Data persistence layer
  - `project_manager.py`: Business logic for managing projects
- `cli.py`: Command-line interface using Click
- `requirements.txt`: Project dependencies
- `setup.py`: Package configuration
- `projects.json`: Default storage file for projects

## Dependencies

- Python 3.6+
- Click: For building command-line interfaces

## Integration

This service integrates with the task management system by:
- Linking tasks to projects
- Sharing user information across services