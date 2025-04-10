# Task Analytics Microservice

This microservice provides analytics and insights on task completion rates, pending work, and team productivity.

## Features

- Task completion rate analysis
- Pending work statistics with priority breakdown
- Productivity metrics and trends
- Complete analytics report generation
- REST API for integration with other services
- Command-line interface for quick reports

## Usage

### Installation

```bash
pip install -r requirements.txt
```

### Run as API Server

```bash
python src/main.py --server
```

This will start the API server on http://0.0.0.0:5000 by default.

### Generate Analytics Report via CLI

```bash
python src/main.py --report
```

For JSON output:

```bash
python src/main.py --report --json
```

### API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/analytics/completion-rate` - Get task completion rate statistics
- `GET /api/analytics/pending-work` - Get pending work statistics
- `GET /api/analytics/productivity` - Get productivity metrics
- `GET /api/analytics/report` - Get complete analytics report

## Configuration

You can configure the following environment variables:

- `TASKS_FILE` - Path to the tasks JSON file
- `API_HOST` - Host for the API server
- `API_PORT` - Port for the API server
- `API_DEBUG` - Whether to run the API server in debug mode

## Running Tests

```bash
pytest tests/
```


### INITIAL TESTING
````python
data/sample_task.json
{
  "task1": {
    "id": "task1",
    "description": "Implement login feature",
    "priority": "high",
    "due_date": "2025-04-20T00:00:00",
    "completed": false,
    "created_at": "2025-04-01T10:00:00"
  },
  "task2": {
    "id": "task2",
    "description": "Fix homepage bug",
    "priority": "medium",
    "due_date": "2025-04-05T00:00:00",
    "completed": true,
    "created_at": "2025-04-02T14:30:00",
    "completed_at": "2025-04-04T16:45:00"
  },
  "task3": {
    "id": "task3",
    "description": "Update documentation",
    "priority": "low",
    "due_date": "2025-04-30T00:00:00",
    "completed": false,
    "created_at": "2025-04-03T09:15:00"
  },
  "task4": {
    "id": "task4",
    "description": "Code review for PR #42",
    "priority": "high",
    "due_date": "2025-04-08T00:00:00",
    "completed": true,
    "created_at": "2025-04-06T11:20:00",
    "completed_at": "2025-04-07T17:30:00"
  }
}

# Navigate to the project root
cd analytics-microservice

# Run CLI report with your sample data
python src/main.py --report --tasks-file data/sample_tasks.json

# For JSON output
python src/main.py --report --json --tasks-file data/sample_tasks.json

# Start the API server with your sample data
python src/main.py --server --tasks-file data/sample_tasks.json


# Health check
curl http://localhost:5000/health

# Get completion rate
curl http://localhost:5000/api/analytics/completion-rate

# Get pending work analysis
curl http://localhost:5000/api/analytics/pending-work

# Get productivity metrics
curl http://localhost:5000/api/analytics/productivity

# Get complete analytics report
curl http://localhost:5000/api/analytics/report

# From the project root
pytest tests/

or

python -m pytest tests/

#addd when error
$env:PYTHONPATH="C:\Users\123ad\OneDrive\Desktop\SE_Project-3\SE\analytics-microservice\src"
````