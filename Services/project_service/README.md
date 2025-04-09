# CLI Task Manager

A simple command-line task manager built with Python.

## Features

- Add, remove, and update tasks
- Mark tasks as complete/incomplete
- Filter tasks by status and priority
- Persist tasks to a JSON file
- Prioritize tasks (low, medium, high)
- Set due dates

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/cli-task-manager.git
cd cli-task-manager
```

2. Install dependencies:
```
pip install click
```

3. Create a symlink to make the CLI accessible from anywhere (optional):
```
pip install -e .
```

## Usage

### Add a task
```
python cli.py add "Complete homework assignment" --priority high --due "2023-05-15"
```

### List all tasks
```
python cli.py list
```

### List only completed tasks
```
python cli.py list --completed
```

### List tasks by priority
```
python cli.py list --priority high
```

### Mark a task as completed
```
python cli.py complete <task_id>
```

### Mark a task as not completed
```
python cli.py uncomplete <task_id>
```

### Show task details
```
python cli.py show <task_id>
```

### Update a task
```
python cli.py update <task_id> --description "New description" --priority medium --due "2023-06-01"
```

### Remove a task
```
python cli.py remove <task_id>
```

## File Structure

- `cli.py`: Command-line interface using Click
- `task_manager.py`: Business logic for managing tasks
- `storage.py`: Data persistence layer
- `task.py`: Task model class
- `tasks.json`: Default storage file for tasks

## Dependencies

- Python 3.6+
- Click: For building command-line interfaces 