## Implementation Overview

### Core Features

**It provides a comprehensive CLI and application entry point that:**

#### CLI Interface: Provides commands for:
- Starting the API server
- Generating different types of analytics reports
- Accessing project-specific analytics
- Accessing user-specific analytics

#### Main Entry Point: Configures and runs:
- The Flask API server when requested
- Logging setup
- Error handling
- Command-line interface
- Configuration: A root configuration file for application-wide settings with reasonable defaults

### Sample Data Files

This directory contains sample JSON data files for the analytics microservice:

- `tasks.json`: Contains task data including descriptions, priorities, due dates, etc.
- `projects.json`: Contains project data including milestones, team members, etc.
- `users.json`: Contains user data including roles, skills, workload capacity, etc.
- `sample_tasks.json`: A copy of tasks.json for testing purposes.

#### File Format

All data files use a simple key-value format where:
- The key is the entity ID
- The value is an object containing the entity's properties

#### Data Relationships
- Tasks reference projects via `project_id`
- Tasks reference users via `assigned_to`
- Projects reference users via `manager_id` and `team_members`

#### Using Custom Data
To use your own data, simply replace these files with your own JSON files following the same format.

### Directory Structure

```bash
analytics-microservice/
├── src/                           # Source code root
│   ├── api/                       # API Layer
│   │   ├── controllers/           # Request handlers
│   │   │   └── analytics_controller.py
│   │   ├── middleware/            # Auth, logging, validation
│   │   │   └── error_handler.py
│   │   ├── dtos/                  # Data Transfer Objects
│   │   │   └── analytics_dtos.py
│   │   └── routes.py              # Route definitions
│   │
│   ├── core/                      # Domain Core (Hexagonal Architecture)
│   │   ├── domain/                # Domain models
│   │   │   ├── models.py          # Core domain entities
│   │   │   └── events.py          # Domain events
│   │   ├── ports/                 # Interface definitions
│   │   │   ├── repositories.py    # Repository interfaces
│   │   │   └── services.py        # Service interfaces
│   │   └── services/              # Business logic
│   │       ├── analytics/
│   │       │   ├── strategies.py  # Analysis algorithms
│   │       │   └── service.py     # Analytics service
│   │       └── factory.py         # Service factory
│   │
│   ├── data/                      # Data Layer (clearly separated)
│   │   ├── repositories/          # Repository implementations
│   │   │   ├── json/              # JSON implementations
│   │   │   │   ├── task_repository.py
│   │   │   │   ├── project_repository.py
│   │   │   │   └── user_repository.py
│   │   │   └── sql/               # SQL implementations (for future)
│   │   │       └── placeholder.md # Empty placeholder for now
│   │   ├── models/                # Data models
│   │   │   └── orm_models.py      # ORM models for DB (future)
│   │   └── datasource/            # Data source connectors
│   │       ├── json_connector.py  # JSON file handling
│   │       └── db_connector.py    # DB connection (for future)
│   │
│   ├── common/                    # Cross-cutting concerns
│   │   ├── logging/
│   │   │   └── logger.py
│   │   ├── errors/
│   │   │   └── exceptions.py
│   │   └── config/
│   │       └── settings.py        # Configuration management
│   │
│   ├── cli/                       # Command line interface
│   │   └── commands.py            # CLI commands
│   │
│   └── main.py                    # Application entry point
│
├── data/                          # Data storage directory
│   ├── sample_tasks.json          # Sample task data
│   ├── projects.json              # Project data
│   └── users.json                 # User data
│
├── tests/                         # Test directories
│   ├── unit/
│   │   ├── core/
│   │   └── data/
│   └── integration/
│       └── api/
│
├── config.py                      # Root configuration file
└── requirements.txt               # Dependencies
```

### Testing

#### Running and Testing the Analytics Microservice

Here's a step-by-step guide to set up, run, and test the analytics microservice using the provided sample data.

##### 1. Setup Environment

First, set up your Python environment:
```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

##### 2. Ensure Data Files

Make sure your sample data files are in the correct location:
```
analytics-microservice/data/
├── tasks.json
├── projects.json
└── users.json
```

##### 3. Running the Service

Starting the API Server:
```bash
# From the project root
python -m src.main server

# Or with specific host/port
python -m src.main server --host 127.0.0.1 --port 8000 --debug
```

##### 4. Testing API Endpoints

You can test the API endpoints using curl, Postman, or any HTTP client.

```bash
# Basic Health Check
curl http://localhost:5000/api/analytics/health

# Get Task Completion Rate
curl http://localhost:5000/api/analytics/completion-rate

# Get Pending Work Analysis
curl http://localhost:5000/api/analytics/pending-work

# Get Project Progress
curl http://localhost:5000/api/analytics/project/proj1

# Get Complete Analytics Report
curl http://localhost:5000/api/analytics/report
```

##### 5. Using the CLI

The microservice includes a CLI for generating reports without starting the web server:

```bash
# Get Help
python -m src.cli.commands --help

# Generate a Complete Report
python -m src.cli.commands report --type full

# Generate a Project Report
python -m src.cli.commands project proj1

# Generate a User Productivity Report
python -m src.cli.commands user user1 --days 30

# Output to JSON File
python -m src.cli.commands report --type full --json --output analytics_report.json
```

##### 6. Adding Test Data

To test with different data:
- Edit the JSON files in the data/ directory
- Make sure to maintain the structure:
    - Each object needs a unique ID as its key
    - Include all required properties (description, due date, etc.)
    - Maintain relationships (task.project_id should refer to an existing project)

##### 7. Testing Specific Analytics

Team Workload Analysis:
```bash
# API
curl http://localhost:5000/api/analytics/team-workload

# CLI
python -m src.cli.commands report --type team
```

Productivity Metrics:
```bash
# API
curl http://localhost:5000/api/analytics/productivity?days=14

# CLI
python -m src.cli.commands report --type productivity --days 14
```

### Testing Commands for Analytics Microservice CLI

Here are commands to test all the available functionality in the Analytics Microservice CLI:

#### Help Commands
```bash
# Show main help
python -m src.cli.commands

# Show help for a specific command
python -m src.cli.commands report --help
```

#### Version Command
```bash
# Check version information
python -m src.cli.commands version
```

#### Server Commands
```bash
# Start server with default settings
python -m src.cli.commands server

# Start server with custom host and port
python -m src.cli.commands server --host 127.0.0.1 --port 8080

# Start server in debug mode
python -m src.cli.commands server --debug
```

#### Report Commands - Basic Types
```bash
# Generate full analytics report
python -m src.cli.commands report --type full

# Generate completion rate report
python -m src.cli.commands report --type completion

# Generate pending work analysis
python -m src.cli.commands report --type pending

# Generate productivity metrics
python -m src.cli.commands report --type productivity

# Generate team workload report
python -m src.cli.commands report --type team

# Generate projects progress report
python -m src.cli.commands report --type projects
```

#### Report Commands - Advanced Options
```bash
# Custom time period (14 days)
python -m src.cli.commands report --type productivity --days 14

# Output in JSON format
python -m src.cli.commands report --type completion --json

# Save report to file
python -m src.cli.commands report --type full --output analytics_report.txt

# JSON output to file
python -m src.cli.commands report --type team --json --output team_report.json

# Debug mode for troubleshooting
python -m src.cli.commands report --type team --debug
```

#### Project Commands
```bash
# Get project analytics (for each project ID in your data)
python -m src.cli.commands project proj1
python -m src.cli.commands project proj2
python -m src.cli.commands project proj3

# Get project analytics in JSON format
python -m src.cli.commands project proj1 --json
```

#### User Commands
```bash
# Get user productivity metrics (for each user ID in your data)
python -m src.cli.commands user user1
python -m src.cli.commands user user2
python -m src.cli.commands user user3
python -m src.cli.commands user user4

# Get user productivity with custom time period
python -m src.cli.commands user user1 --days 7

# Get user productivity in JSON format
python -m src.cli.commands user user2 --json
```

#### Batch Testing Script
```batch
@echo off
REM Windows batch file for testing CLI commands
echo Testing Analytics CLI Commands...

echo.
echo === VERSION INFORMATION ===
python -m src.cli.commands version

echo.  
echo === COMPLETION RATE ===
python -m src.cli.commands report --type completion

echo.
echo === PENDING WORK ANALYSIS ===
python -m src.cli.commands report --type pending

echo.
echo === PRODUCTIVITY METRICS ===
python -m src.cli.commands report --type productivity

echo.
echo === TEAM WORKLOAD ===
python -m src.cli.commands report --type team

echo.
echo === PROJECT ANALYTICS: PROJ1 ===
python -m src.cli.commands project proj1

echo.
echo === USER ANALYTICS: USER1 ===
python -m src.cli.commands user user1

echo.
echo All tests completed!
```

Save this as test_cli.bat (Windows) or adapt it for shell script on Linux/macOS.