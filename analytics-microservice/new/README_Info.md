# Analytics Microservice: Logic and Implementation

## Overview

The Analytics Microservice is designed to process task, project, and user data to generate actionable insights and metrics. The service follows a clean architecture pattern with ports and adapters, allowing for extensible and maintainable code while providing valuable project management analytics.

## Analytics Microservice Supports Both

### 1. Project-Specific Analytics
The microservice is fully capable of providing project-specific analytics:

- **API Access**: `GET /api/analytics/project/{project_id}`
- **CLI Access**: `python -m src.cli.commands project <project_id>`

What you'll get:
- Project completion percentage
- Number of completed vs. total tasks
- Days remaining until deadline
- Whether the project is on track
- Progress metrics specific to that project

**Example output:**
```
PROJECT: User Authentication System
    Progress: 66.67% complete
    Tasks: 2/3
    Days Remaining: 14
    On Track: Yes
```

### 2. User-Specific Analytics
The microservice provides comprehensive user-specific analytics across all projects:

- **API Access**: `GET /api/analytics/user/{user_id}?days=30`
- **CLI Access**: `python -m src.cli.commands user <user_id> --days 30`

What you'll get:
- Tasks completed by the specific user
- Average task completion time
- Daily completion rate
- Workload analysis
- The analysis includes ALL tasks assigned to this user across MULTIPLE projects

**Example output:**
```
USER: John Smith (Senior Developer)
    Tasks Completed: 2
    Average Completion Time: 68.5 hours
```

Both analytics types are core features of the microservice, designed to work across your entire data set. The microservice will automatically aggregate relevant tasks across projects for user analytics and focus on specific project tasks for project analytics.

### Testing Examples for Analytics Microservice

Here are practical examples to test both the API endpoints (via curl) and CLI commands:

### Project-Specific Analytics

#### 1. Get analytics for Project 1

**API (curl):**
```bash
curl http://localhost:5000/api/analytics/project/proj1
```

**CLI:**
```bash
python -m src.cli.commands project proj1
```

#### 2. Get analytics for Project 2 in JSON format

**API (curl):**
```bash
curl http://localhost:5000/api/analytics/project/proj2
```

**CLI:**
```bash
python -m src.cli.commands project proj2 --json
```

#### 3. Get analytics for all projects

**API (curl):**
```bash
curl http://localhost:5000/api/analytics/projects
```

**CLI:**
```bash
python -m src.cli.commands report --type projects
```

### User-Specific Analytics

#### 1. Get analytics for User 1 (default 30 days)

**API (curl):**
```bash
curl http://localhost:5000/api/analytics/user/user1
```

**CLI:**
```bash
python -m src.cli.commands user user1
```

#### 2. Get analytics for User 2 with 14-day time period

**API (curl):**
```bash
curl http://localhost:5000/api/analytics/user/user2?days=14
```

**CLI:**
```bash
python -m src.cli.commands user user2 --days 14
```

#### 3. Get analytics for User 3 in JSON format

**API (curl):**
```bash
curl http://localhost:5000/api/analytics/user/user3
```

**CLI:**
```bash
python -m src.cli.commands user user3 --json
```
### Advanced Usage

#### 1. Save report to file

**CLI:**
```bash
python -m src.cli.commands report --type productivity --output productivity_report.txt
```

#### 2. Debug mode with data file checking

**CLI:**
```bash
python -m src.cli.commands report --type team --debug
```

#### 3. Start API server on custom port

**CLI:**
```bash
python -m src.cli.commands server --host 127.0.0.1 --port 8080 --debug
```

These examples cover all the major functionality of the microservice and can be used to verify that both the API and CLI interfaces are working correctly.


## Data Model

The microservice operates on three primary data entities:

- **Tasks**: Work items with attributes like description, priority, due date, completion status, assigned user, and project association
- **Projects**: Collections of tasks with milestones, team members, and timeline information
- **Users**: Team members with roles, skills, and workload capacity

## Core Analytics Features

### 1. Task Completion Rate

**Description**: Analyzes task completion efficiency over a specified time period.

**Inputs**:
- `time_period_days` (optional, default: 30): Number of days to analyze

**Processing Logic**:
- Retrieves all tasks from the repository
- Filters tasks created within the specified time period
- Counts total tasks, completed tasks
- Calculates completion rate percentage (completed tasks / total tasks)

**Output**:
```json
{
    "total_tasks": 8,
    "completed_tasks": 4,
    "completion_rate_percentage": 50.0,
    "time_period_days": 30,
    "pending_tasks": 4
}
```

### 2. Pending Work Analysis

**Description**: Provides insights into outstanding tasks that require attention.

**Inputs**: None

**Processing Logic**:
- Retrieves all tasks from the repository
- Filters for incomplete tasks
- Groups by priority (high, medium, low)
- Identifies overdue tasks (due date before current date)
- Calculates average days pending

**Output**:
```json
{
    "total_pending": 4,
    "by_priority": {
        "high": 1,
        "medium": 2,
        "low": 1
    },
    "overdue_tasks": 1,
    "overdue_percentage": 25.0,
    "average_days_pending": 5.75
}
```

### 3. Productivity Metrics

**Description**: Measures team productivity based on task completion data.

**Inputs**:
- `time_period_days` (optional, default: 30): Number of days to analyze

**Processing Logic**:
- Retrieves all tasks from the repository
- Filters for completed tasks within the specified time period
- Calculates average completion time (hours between task creation and completion)
- Tracks daily completion counts
- Aggregates weekly completion trends

**Output**:
```json
{
    "tasks_completed": 4,
    "avg_completion_time_hours": 82.94,
    "average_daily_completion": 0.29,
    "time_period_days": 14,
    "daily_completion": {
        "2025-04-04": 1,
        "2025-04-07": 1,
        "2025-04-08": 1,
        "2025-04-09": 1
    },
    "weekly_trends": {
        "2025-W14": 1,
        "2025-W15": 3
    }
}
```

### 4. Team Workload Analysis

**Description**: Analyzes workload distribution across team members.

**Inputs**: None

**Processing Logic**:
- Retrieves all tasks and users
- Maps tasks to assigned users
- Calculates per-user metrics:
    - Pending tasks count
    - Workload percentage based on estimated hours and capacity
    - Completion rate
- Identifies most overloaded and least loaded team members

**Output**:
```json
{
    "total_users": 5,
    "total_tasks": 8,
    "total_pending_tasks": 4,
    "user_metrics": {
        "user1": {
            "name": "John Smith",
            "pending_tasks": 1,
            "workload_percentage": 20.0,
            "completion_rate": 66.67
        },
        "user2": { ... },
        "user3": { ... },
        "user4": { ... }
    },
    "most_overloaded_user": "user3",
    "least_loaded_user": "user4"
}
```

### 5. Project Progress

**Description**: Tracks progress for a specific project.

**Inputs**:
- `project_id`: Identifier for the project to analyze

**Processing Logic**:
- Retrieves project details and associated tasks
- Calculates completion percentage
- Estimates days remaining until target completion
- Determines if the project is on track based on velocity and remaining work

**Output**:
```json
{
    "project_id": "proj1",
    "project_name": "User Authentication System",
    "total_tasks": 3,
    "completed_tasks": 2,
    "completion_percentage": 66.67,
    "days_elapsed": 17,
    "days_remaining": 14,
    "on_track": true
}
```

### 6. User Productivity

**Description**: Analyzes productivity metrics for a specific user.

**Inputs**:
- `user_id`: Identifier for the user to analyze
- `time_period_days` (optional, default: 30): Number of days to analyze

**Processing Logic**:
- Retrieves user details and their assigned tasks
- Filters for tasks completed within specified time period
- Calculates completion time metrics and efficiency

**Output**:
```json
{
    "user_id": "user1",
    "user_name": "John Smith",
    "user_role": "Senior Developer",
    "tasks_completed": 2,
    "avg_completion_time_hours": 68.5,
    "average_daily_completion": 0.14,
    "time_period_days": 30
}
```

### 7. Complete Analytics Report

**Description**: Generates a comprehensive report combining multiple analytics metrics.

**Inputs**: None

**Processing Logic**:
- Collects data from all individual analytics services
- Combines into a single comprehensive report

**Output**:
```json
{
    "completion_rate": { ... },
    "pending_work": { ... },
    "productivity": { ... },
    "team_workload": { ... },
    "projects": { ... },
    "generated_at": "2025-04-11T09:30:00"
}
```

## Implementation Architecture

### Core Components

**Service Layer**:
- `AnalyticsService` implements the `AnalyticsServicePort` interface
- Uses strategy pattern for different analytical calculations

**Repositories**:
- `TaskRepositoryPort`, `ProjectRepositoryPort`, `UserRepositoryPort`
- JSON implementations for data storage and retrieval

**Strategy Pattern**:
- Separate strategy classes for each type of analytics:
    - `TaskCompletionRateStrategy`
    - `PendingWorkAnalysisStrategy`
    - `ProductivityMetricsStrategy`
    - `TeamWorkloadStrategy`
    - `ProjectProgressStrategy`

### Interface Methods

```python
class AnalyticsServicePort:
        def get_completion_rate(self, time_period_days: int = 30) -> Dict[str, Any]: ...
        def get_pending_work_analysis(self) -> Dict[str, Any]: ...
        def get_productivity_metrics(self, time_period_days: int = 30) -> Dict[str, Any]: ...
        def get_team_workload(self) -> Dict[str, Any]: ...
        def get_project_progress(self, project_id: str) -> Dict[str, Any]: ...
        def get_all_projects_progress(self) -> Dict[str, Any]: ...
        def get_user_productivity(self, user_id: str, time_period_days: int = 30) -> Dict[str, Any]: ...
        def get_complete_analytics_report(self) -> Dict[str, Any]: ...
```

## Client Interfaces

The analytics microservice exposes two client interfaces:

### 1. REST API

**Endpoints**:
- `/api/analytics/completion-rate`
- `/api/analytics/pending-work`
- `/api/analytics/productivity`
- `/api/analytics/team-workload`
- `/api/analytics/project/{project_id}`
- `/api/analytics/report`

### 2. Command Line Interface

**Commands**:
- `report` - Generate various types of reports
- `project` - Get analytics for a specific project
- `user` - Get productivity metrics for a specific user
- `server` - Start the API server
- `version` - Display version information

## Data Processing Flow

1. **Data Source**: JSON files containing tasks, projects, and users
2. **Repositories**: Interface with data sources to provide domain objects
3. **Service Layer**: Uses repositories to fetch data and applies analytics strategies
4. **Presentation Layer**: Formats results as CLI output or API responses

The architecture follows dependency inversion principles by having the service layer depend on abstractions (repository ports) rather than concrete implementations, enabling easy testing and maintenance.


### **Analytics Report Scope for Global Analytics**

The five analytics reports you mentioned operate on the entire dataset by default. Let me clarify their scope and filtering options:

---

### **Global Analytics Reports**

#### **Team Workload Analysis**
- Analyzes workload distribution across all team members  
- Includes all tasks from all projects  
- No built-in project filtering in the current implementation  

#### **Completion Rate**
- Calculated across all tasks in the system  
- Only filter is the time period (e.g., 7 days)  
- No project-specific or team-specific filtering  

#### **Pending Work Analysis**
- Examines all pending tasks across the entire system  
- No project or team filtering parameters available  

#### **Productivity Metrics**
- Analyzes all completed tasks in the system  
- Only filter is the time period (e.g., 14 days)  
- No project or team filtering  

#### **Complete Analytics Report**
- Combines all the above analytics in one comprehensive report  
- No filtering parameters available  

---

### **For Project-Specific or User-Specific Analytics**

If you need analytics for specific projects or team members, you should use:

- **Projects:**  
  `/api/analytics/project/{project_id}` endpoint or  
  `analytics project <project_id>` CLI command  

- **Users:**  
  `/api/analytics/user/{user_id}` endpoint or  
  `analytics user <user_id>` CLI command  

---

### **Enhancement Possibilities**

To support filtering by project or user in global reports, you would need to enhance the microservice by:

- Adding query parameters to the API endpoints (e.g., `?project_id=proj1`)
- Adding filter options to the CLI commands (e.g., `--project proj1`)
- Modifying the service layer to support these filters

> These would be reasonable extensions to the current functionality but aren't implemented in the current version of the microservice.


### **Enhanced calls**

##### URL BASED
###### Get completion rate for a specific project
````
curl http://localhost:5000/api/analytics/completion-rate?project_id=proj1
````

###### Get team workload filtered by project
````
curl http://localhost:5000/api/analytics/team-workload?project_id=proj1
````

###### Get productivity metrics for a specific project for the last 14 days
````
curl http://localhost:5000/api/analytics/productivity?days=14&project_id=proj1
````

###### Get complete report filtered by team
````
curl http://localhost:5000/api/analytics/report?team_id=team1
````

##### CLI BASED


###### Get completion rate for a specific project
````
python -m src.cli.commands report --type completion --project proj1
````
###### Get pending work analysis for a specific project
````
python -m src.cli.commands report --type pending --project proj1
````
###### Get team workload filtered by project
````
python -m src.cli.commands report --type team --project proj1
````
###### Get user productivity for a specific user on a specific project
````
python -m src.cli.commands user user1 --project proj1
````
###### Get complete report for a specific team
````
python -m src.cli.commands report --type full --team team1
````