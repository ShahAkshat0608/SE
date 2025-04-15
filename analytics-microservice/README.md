# Analytics Microservice Implementation Roadmap

## Architecture Overview

The analytics microservice will provide insights at three levels (user, team, and project) with three types of analytics (progress/completion, workload, and comprehensive reports).

## Core Components

### 1. Service Structure (started here)
```
analytics-service/
├── api/                    # API endpoints and controllers
├── models/                 # Data models
├── services/               # Business logic for analytics
│   ├── user-analytics/     
│   ├── team-analytics/     
│   └── project-analytics/  
├── data/                   # Data access layer
├── utils/                  # Helper functions
└── config/                 # Configuration files
```

# Summary of Design Pattern Implementation for Analytics Microservice

## Core Design Patterns Applied
1. **Strategy Pattern** - For analytics generation logic
2. **Template Method Pattern** - For route handling
3. **Facade Pattern** - For unified access to analytics strategies
4. **Singleton** - For only one instance of cache 

## File Structure & Purpose

### Strategy Pattern Implementation

#### Base Strategy Files
1. **`project_analytics_strategy.py`**
   - Abstract base class defining interface for project analytics
   - Provides common functionality like caching

2. **`team_analytics_strategy.py`**
   - Abstract base class for team analytics strategies
   - Similar structure to project analytics but with team-specific parameters

3. **`user_analytics_strategy.py`**
   - Abstract base class for user analytics strategies
   - Handles user-specific data access patterns

#### Concrete Strategy Implementations

4. **`progress_strategy.py`** (for each entity)
   - Implements progress analytics for specific entity types
   - Calculates completion rates, timeline metrics
   - Returns appropriate response models

5. **`workload_strategy.py`** (for each entity)
   - Implements workload distribution analytics
   - Analyzes resource allocation, task distribution
   - Identifies bottlenecks and overallocation

6. **`comprehensive_strategy.py`** (for each entity)
   - Combines progress and workload analytics
   - Adds additional insights and recommendations
   - Uses other strategies internally via composition

### Template Method & Route Handling

7. **`base_routes.py`**
   - Abstract base class for all analytics routes
   - Defines template methods for common route logic
   - Handles permission checking and request processing

8. **`project_routes.py`**
   - Concrete implementation for project analytics routes
   - Implements required abstract methods
   - Creates router instance for project endpoints

9. **`team_routes.py`**
   - Team-specific route handling
   - Additional logic for project_id parameter requirement
   - Permission checks for team access

10. **`user_routes.py`**
    - User-specific route handling
    - Permission checks to ensure users can only access their own data

### Facade Implementation

11. **`analytics_facade.py`**
    - Provides unified interface to all analytics strategies
    - Handles strategy selection based on report type
    - Simplifies client access to complex analytics subsystem

### Application Configuration

12. **`api/__init__.py`**
    - Creates unified router combining all endpoint groups
    - Sets up proper prefixes and tags for API documentation

13. **`main.py`**
    - Main application entry point
    - Configures FastAPI application
    - Sets up CORS and middleware
    - Registers the unified router

## Logical Flow

1. **Request Processing**:
   - Client request → FastAPI → api_router → Specific route class
   - Route checks permissions and extracts parameters
   - Route delegates to analytics facade

2. **Strategy Selection**:
   - Facade selects appropriate strategy based on report type
   - Strategy context is configured with concrete strategy

3. **Report Generation**:
   - Strategy accesses data from data sources
   - Strategy applies analytics logic
   - Response model is constructed and returned

4. **Response Handling**:
   - FastAPI handles serialization and HTTP response
   - Client receives formatted analytics data

This architecture provides a highly maintainable, extensible system where:
- New analytics types can be added with minimal changes
- Common code is reused through inheritance and composition
- Responsibilities are cleanly separated
- Testing is simplified through clear component boundaries

## Implementation Steps

1. **First Phase**: Implement core Strategy Pattern for different analytics algorithms
2. **Second Phase**: Add Factory Pattern for report creation and Observer Pattern for real-time updates
3. **Third Phase**: Implement caching and Circuit Breaker patterns for resilience
4. **Fourth Phase**: Add CQRS pattern for optimized reads/writes
5. **Fifth Phase**: Implement decorators for enhanced report capabilities

These design patterns and architectural tactics will make your analytics microservice more:

- **Maintainable**: Clear separation of responsibilities
- **Flexible**: Easy to add new analytics types or change algorithms
- **Scalable**: Better performance through caching and CQRS
- **Resilient**: Circuit breakers prevent cascading failures
- **Real-time**: Event-driven architecture keeps analytics up-to-date

The enhanced architecture also supports future growth with clear extension points for additional analytics capabilities and report types.

Similar code found with 2 license types

AdarshOnGith: ok this is good, but first give me overview how we will integrate it for the use cases (as defined earlier for the type of requests and who can request to expect what response) ?

GitHub Copilot: # Analytics Microservice Integration Overview

This overview explains how the analytics microservice integrates with the project management system to handle the three levels of analytics requests (user, team, and project) based on user roles.

## Request Flow & Authorization Pattern

All analytics requests follow this pattern:

1. **Authentication & Authorization**
   - All requests include user credentials and are verified against the auth service
   - Role-based permissions are checked (Project Manager, Team Lead, or regular User)

2. **Request Processing**
   - API Gateway routes to appropriate controller
   - Controller delegates to appropriate analytics strategy
   - Data is retrieved with caching for performance
   - Analytics are calculated and formatted as reports

3. **Response Delivery**
   - Formatted reports with optional visualizations are returned
   - Cached for subsequent identical requests

## Use Case Integration

### 1. User-Level Analytics

**Access Patterns:**
- Users can view their own analytics
- Team Leads can view analytics for their team members
- Project Managers can view analytics for any user in their project

**Integration Flow:**

```
┌─────────────┐         ┌──────────────────┐         ┌───────────────────┐
│  Requester  │         │  API Gateway     │         │  Auth Service     │
│  (User/TL/PM)├────────►│  /api/analytics/ ├────────►│  Validate roles   │
└──────┬──────┘         └────────┬─────────┘         └─────────┬─────────┘
       │                         │                             │
       │                         ▼                             ▼
┌──────▼──────┐         ┌────────────────┐         ┌───────────────────┐
│ Analytics   │         │ User Analytics │◄────────┤ Permissions Check │
│ Response    │◄────────┤ Controller     │         │ (User's own OR    │
└─────────────┘         └───────┬────────┘         │  TL's team member │
                                │                  │  OR PM's project) │
                                ▼                  └───────────────────┘
                        ┌────────────────┐         
                        │ User Analytics │         
                        │ Strategy      │         
                        └───────┬────────┘         
                                │                  
                                ▼                  
                        ┌────────────────┐         ┌───────────────────┐
                        │ Query Service  │────────►│ Cache Layer       │
                        │ (User Data)    │◄────────┤                   │
                        └───────┬────────┘         └───────────────────┘
                                │
                                ▼
                        ┌────────────────┐
                        │ Report Factory │
                        │ & Decorators   │
                        └────────────────┘
```

**Sample Request & Response:**

Request:
```http
GET /api/analytics/user/user-101?type=workload&visualize=true
Authorization: Bearer <token>
```

Response:
```json
{
  "userId": "user-101",
  "userName": "Alice",
  "workloadStats": {
    "pendingSubtasks": 5,
    "totalEstimatedHours": 42,
    "priorityDistribution": {
      "high": 2,
      "medium": 2,
      "low": 1
    },
    "dueThisWeek": 3,
    "dueThisMonth": 2
  },
  "visualizations": {
    "priorityChart": { "type": "pie", "data": { /* chart data */ } },
    "timelineChart": { "type": "gantt", "data": { /* chart data */ } }
  }
}
```

### 2. Team-Level Analytics

**Access Patterns:**
- Team Leads can view analytics for their own team
- Project Managers can view analytics for any team in their project

**Integration Flow:**

```
┌─────────────┐         ┌───────────────────┐         ┌───────────────────┐
│  Requester  │         │  API Gateway      │         │  Auth Service     │
│  (TL/PM)    ├────────►│  /api/analytics/  ├────────►│  Validate roles   │
└──────┬──────┘         └────────┬──────────┘         └─────────┬─────────┘
       │                         │                              │
       │                         ▼                              ▼
┌──────▼──────┐         ┌────────────────┐         ┌────────────────────┐
│ Analytics   │         │ Team Analytics │◄────────┤ Permissions Check  │
│ Response    │◄────────┤ Controller     │         │ (TL's own team OR  │
└─────────────┘         └───────┬────────┘         │  PM's project)     │
                                │                  └────────────────────┘
                                ▼
                        ┌────────────────┐
                        │ Team Analytics │
                        │ Strategy      │
                        └───────┬────────┘
                                │
                                ▼
                        ┌────────────────┐         ┌───────────────────┐
                        │ Query Service  │────────►│ Cache Layer       │
                        │ (Team Data)    │◄────────┤                   │
                        └───────┬────────┘         └───────────────────┘
                                │
                                ▼
                        ┌────────────────┐
                        │ Report Factory │
                        │ & Decorators   │
                        └────────────────┘
```

**Sample Request & Response:**

Request:
```http
GET /api/analytics/team/team-001?projectId=project-001&type=progress
Authorization: Bearer <token>
```

Response:
```json
{
  "teamId": "team-001",
  "teamName": "Design Team",
  "projectId": "project-001",
  "progressStats": {
    "completionRate": 65.5,
    "completedSubtasks": 13,
    "pendingSubtasks": 7,
    "milestoneProgress": {
      "milestones": [
        {
          "id": "milestone-001",
          "name": "Design Phase",
          "completionRate": 75
        },
        {
          "id": "milestone-002", 
          "name": "Development Phase",
          "completionRate": 30
        }
      ]
    }
  },
  "memberProgress": {
    "user-101": { "completionRate": 80, "completedTasks": 4, "pendingTasks": 1 },
    "user-102": { "completionRate": 60, "completedTasks": 3, "pendingTasks": 2 },
    "user-104": { "completionRate": 50, "completedTasks": 2, "pendingTasks": 2 }
  }
}
```

### 3. Project-Level Analytics

**Access Pattern:**
- Only Project Managers can view project-level analytics for their projects

**Integration Flow:**

```
┌─────────────┐         ┌───────────────────┐         ┌───────────────────┐
│  Requester  │         │  API Gateway      │         │  Auth Service     │
│  (PM)       ├────────►│  /api/analytics/  ├────────►│  Validate roles   │
└──────┬──────┘         └────────┬──────────┘         └─────────┬─────────┘
       │                         │                              │
       │                         ▼                              ▼
┌──────▼──────┐         ┌────────────────┐         ┌────────────────────┐
│ Analytics   │         │Project Analytics◄────────┤ Permissions Check  │
│ Response    │◄────────┤ Controller     │         │ (PM's own project) │
└─────────────┘         └───────┬────────┘         └────────────────────┘
                                │
                                ▼
                        ┌────────────────┐
                        │Project Analytics
                        │ Strategy      │
                        └───────┬────────┘
                                │
                                ▼
                        ┌────────────────┐         ┌───────────────────┐
                        │ Query Service  │────────►│ Cache Layer       │
                        │ (Project Data) │◄────────┤                   │
                        └───────┬────────┘         └───────────────────┘
                                │
                                ▼
                        ┌────────────────┐
                        │ Report Factory │
                        │ & Decorators   │
                        └────────────────┘
```

**Sample Request & Response:**

Request:
```http
GET /api/analytics/project/project-001?type=comprehensive
Authorization: Bearer <token>
```

Response:
```json
{
  "projectId": "project-001",
  "projectName": "Website Redesign",
  "projectManager": "user-103",
  "status": "active",
  "progressStats": {
    "completionRate": 45.5,
    "completedSubtasks": 25,
    "pendingSubtasks": 30,
    "milestoneProgress": {
      "milestones": [
        { "id": "milestone-001", "name": "Design Phase", "completionRate": 75 },
        { "id": "milestone-002", "name": "Development Phase", "completionRate": 30 },
        { "id": "milestone-003", "name": "Testing Phase", "completionRate": 5 }
      ]
    },
    "estimatedCompletion": "2023-05-15T00:00:00"
  },
  "workloadStats": {
    "pendingSubtasks": 30,
    "totalEstimatedHours": 320,
    "resourceAllocation": {
      "overallocatedTeams": ["Development Team"],
      "underallocatedTeams": []
    },
    "bottlenecks": [
      {
        "type": "resource",
        "description": "Backend development team has 60% more tasks than capacity",
        "impactedMilestone": "milestone-002"
      }
    ]
  },
  "teamReports": {
    "team-001": {
      "name": "Design Team",
      "progress": { "completionRate": 75 },
      "workload": { "estimatedHours": 40 }
    },
    "team-002": {
      "name": "Development Team",
      "progress": { "completionRate": 30 },
      "workload": { "estimatedHours": 180 }
    },
    "team-003": {
      "name": "Testing Team",
      "progress": { "completionRate": 5 },
      "workload": { "estimatedHours": 100 }
    }
  },
  "projectHealth": {
    "status": "At Risk",
    "issues": [
      "Development team workload exceeds capacity by 60%",
      "Testing phase is behind schedule by 1 week"
    ]
  }
}
```

## Event-Driven Integration

The analytics microservice maintains real-time analytics by subscribing to these events from the project management system:

### 1. Task Management Events
```
┌──────────────────┐  subtask.completed   ┌───────────────────┐
│ Task Management  ├───────────────────────► Analytics Service │
│ Service          │  subtask.assigned    │ Event Subscribers  │
└──────────────────┘  subtask.updated     └────────┬──────────┘
                      task.created                 │
                      milestone.updated            ▼
                                           ┌───────────────────┐
                                           │ Cache Invalidation│
                                           │ & Recalculation   │
                                           └───────────────────┘
```

### 2. Team Management Events
```
┌──────────────────┐  team.member_added   ┌───────────────────┐
│ Team Management  ├───────────────────────► Analytics Service │
│ Service          │  team.created        │ Event Subscribers  │
└──────────────────┘  team.updated        └────────┬──────────┘
                                                   │
                                                   ▼
                                          ┌───────────────────┐
                                          │ User/Team Cache   │
                                          │ Invalidation      │
                                          └───────────────────┘
```

## Response Formats by Analytics Type

### 1. Progress Analytics
- Completion percentages
- Milestone progress
- Timelines
- Due date analysis
- On-time vs. late completion statistics

### 2. Workload Analytics
- Pending subtasks count and distribution
- Estimated hours required
- Priority distribution
- Resource allocation
- Upcoming deadlines

### 3. Comprehensive Reports
- Combines progress and workload metrics
- Adds risk assessments
- Provides recommendations
- Includes historical trend analysis
- Predicts completion dates
- Identifies bottlenecks and issues

This integration approach ensures that each user role gets access to the appropriate level of analytics, with real-time updates as project data changes, while maintaining high performance through caching and optimized data access.



# **INFORMATION**
# Authentication Middleware and Permission Checks in the Analytics Microservice

## Authentication Middleware

The authentication middleware in your analytics microservice serves as the first line of defense for securing your API endpoints. Here's how it works:

### 1. JWT Token Validation

```python
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip auth for certain paths
    if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid authentication token"})
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        # Decode and validate token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Add decoded user info to request state for use in endpoint handlers
        request.state.user = {
            "user_id": payload.get("sub"),
            "role": payload.get("role", "user"),
            "name": payload.get("name", "Unknown User")
        }
        
    except jwt.PyJWTError as e:
        return JSONResponse(status_code=401, content={"detail": f"Invalid authentication credentials: {str(e)}"})
    
    # Continue to the endpoint handler
    return await call_next(request)
```

### 2. Logical Flow

1. **Interception**: Every request to the API passes through this middleware
2. **Exemptions**: Public endpoints like health checks are exempted
3. **Token Extraction**: The JWT token is extracted from the Authorization header
4. **Validation & Decoding**: The token is verified and its payload decoded
5. **User Context**: User information (ID, role, name) is attached to the request state
6. **Forwarding**: If everything is valid, the request proceeds to the endpoint handler

## Permission Checks

After authentication, your system performs role-based access control checks to ensure users can only access resources they have permission for:

### 1. Role Definition

```python
class RolePermission:
    """Role-based permission constants"""
    USER = "user"
    TEAM_LEAD = "team_lead"
    PROJECT_MANAGER = "project_manager"
    
    # Permission levels
    VIEW_OWN = "view_own"
    VIEW_TEAM = "view_team"
    VIEW_PROJECT = "view_project"
    
    # Resource types
    USER_ANALYTICS = "user_analytics"
    TEAM_ANALYTICS = "team_analytics" 
    PROJECT_ANALYTICS = "project_analytics"
    
    # Role-based permission mapping
    PERMISSIONS = {
        USER: {
            USER_ANALYTICS: [VIEW_OWN],
            TEAM_ANALYTICS: [],
            PROJECT_ANALYTICS: []
        },
        TEAM_LEAD: {
            USER_ANALYTICS: [VIEW_OWN, VIEW_TEAM],
            TEAM_ANALYTICS: [VIEW_TEAM],
            PROJECT_ANALYTICS: []
        },
        PROJECT_MANAGER: {
            USER_ANALYTICS: [VIEW_OWN, VIEW_TEAM, VIEW_PROJECT],
            TEAM_ANALYTICS: [VIEW_TEAM, VIEW_PROJECT],
            PROJECT_ANALYTICS: [VIEW_PROJECT]
        }
    }
```

### 2. Permission Check Function

```python
async def check_analytics_permission(
    request: Request,
    resource_type: str,
    resource_id: str,
    project_id: str = None
) -> bool:
    """Check if user has permission to access the resource"""
    
    # Get user from request state (set by auth middleware)
    current_user = request.state.user
    user_id = current_user.get("user_id")
    role = current_user.get("role", "user")
    
    # Get data access layer
    data_access = get_data_access_layer()
    
    # Get permissions for this role and resource
    permissions = RolePermission.PERMISSIONS.get(role, {}).get(resource_type, [])
    
    # USER ANALYTICS: Check if user can view this user's analytics
    if resource_type == RolePermission.USER_ANALYTICS:
        # Users can always view their own analytics
        if resource_id == user_id:
            return True
        
        # Team leads can view their team members' analytics
        if RolePermission.VIEW_TEAM in permissions:
            is_team_lead = await data_access.is_user_team_lead(user_id)
            if is_team_lead:
                # Check if requested user is in the team lead's team
                return await data_access.is_user_in_team(resource_id, await data_access.get_team_id_for_lead(user_id))
        
        # Project managers can view any user in their projects
        if RolePermission.VIEW_PROJECT in permissions:
            managed_project_id = await data_access.get_project_id_for_manager(user_id)
            return await data_access.is_user_in_project(resource_id, managed_project_id)
    
    # TEAM ANALYTICS: Check if user can view this team's analytics
    elif resource_type == RolePermission.TEAM_ANALYTICS:
        # Team leads can view their own team
        if RolePermission.VIEW_TEAM in permissions:
            # For team leads
            if role == RolePermission.TEAM_LEAD:
                led_team_id = await data_access.get_team_id_for_lead(user_id)
                return resource_id == led_team_id
        
        # Project managers can view teams in their projects
        if RolePermission.VIEW_PROJECT in permissions:
            managed_project_id = await data_access.get_project_id_for_manager(user_id)
            if project_id and managed_project_id == project_id:
                return await data_access.is_team_in_project(resource_id, project_id)
    
    # PROJECT ANALYTICS: Check if user can view this project's analytics
    elif resource_type == RolePermission.PROJECT_ANALYTICS:
        # Project managers can view their projects
        if RolePermission.VIEW_PROJECT in permissions:
            managed_project_id = await data_access.get_project_id_for_manager(user_id)
            return resource_id == managed_project_id
    
    return False
```

### 3. Dependency Injection for Endpoints

```python
def require_permission(resource_type: str):
    """
    Dependency factory for checking permissions to access a resource.
    Usage: Depends(require_permission(RolePermission.USER_ANALYTICS))
    """
    async def check_permission(
        request: Request,
        resource_id: str = Path(...),
        project_id: str = Query(None),
    ):
        has_permission = await check_analytics_permission(
            request, resource_type, resource_id, project_id
        )
        
        if not has_permission:
            resource_name = resource_type.replace("_analytics", "")
            raise HTTPException(
                status_code=403,
                detail=f"Not authorized to access this {resource_name}'s analytics"
            )
        
        return True
    
    return check_permission
```

### 4. Usage in Endpoint Handlers

```python
@router.get("/{user_id}/progress", response_model=UserProgressResponse)
async def get_user_progress(
    user_id: str,
    visualize: bool = Query(False),
    _: bool = Depends(require_permission(RolePermission.USER_ANALYTICS)),
    request: Request = None,
    progress_service: UserProgressService = Depends(get_user_progress_service)
):
    """Get progress analytics for a user"""
    report = await progress_service.get_progress_report(user_id)
    
    # Add visualizations if requested
    if visualize:
        report.visualizations = generate_visualization_data("progress", report.dict())
    
    return report
```

## Logical Flow of Authentication and Authorization

1. **Request Arrival**:
   - Client sends request with JWT bearer token
   - Example: GET `/api/analytics/user/user-102/progress`

2. **Authentication Middleware**:
   - Intercepts the request
   - Extracts and validates the JWT token
   - Decodes user information (e.g., user_id="user-101", role="user")
   - Attaches user context to the request

3. **Route Handling**:
   - Request is routed to the appropriate endpoint handler
   - In this example: `get_user_progress` in user_routes.py

4. **Permission Check** (via Dependency):
   - The `require_permission` dependency runs before the actual handler
   - It calls `check_analytics_permission` with appropriate parameters
   - This checks if user-101 (role: user) can access analytics for user-102

5. **Access Decision**:
   - For a regular user trying to access another user's analytics: Access denied (403 Forbidden)
   - For a team lead trying to access a team member's analytics: Access granted if user-102 is in their team
   - For a project manager: Access granted if user-102 is in one of their managed projects

6. **Service Execution** (if access granted):
   - The appropriate analytics service is called
   - Data is retrieved and calculations performed
   - Response is returned to the client

## Role-Specific Access Patterns

### Regular User (role="user")
- ✅ Can view their own analytics
- ❌ Cannot view other users' analytics
- ❌ Cannot view team analytics
- ❌ Cannot view project analytics

### Team Lead (role="team_lead")
- ✅ Can view their own analytics
- ✅ Can view analytics for members of their team
- ✅ Can view analytics for their team 
- ❌ Cannot view analytics for other teams
- ❌ Cannot view project analytics

### Project Manager (role="project_manager")
- ✅ Can view their own analytics
- ✅ Can view analytics for any user in their projects
- ✅ Can view analytics for any team in their projects
- ✅ Can view analytics for their projects
- ❌ Cannot view analytics for projects they don't manage

This layered approach to security ensures that users can only access the analytics they're authorized to see, while maintaining a clean separation between authentication (validating identity) and authorization (checking permissions).




# Analytics Microservice Architecture Overview

## Component Descriptions

### 1. API Layer (`/api`)
- **main.py**: The entry point of the application, configures FastAPI, middleware, and registers all routes
- **user_routes.py**: Defines endpoints for user analytics (`/api/analytics/user/{user_id}/progress`, etc.)
- **team_routes.py**: Defines endpoints for team analytics (`/api/analytics/team/{team_id}/progress`, etc.)
- **project_routes.py**: Defines endpoints for project analytics (`/api/analytics/project/{project_id}/progress`, etc.)

### 2. Models (`/models`)
- **analytics_models.py**: Core domain models representing the business entities
  - `AnalyticsLevel` (Enum): Defines levels of analytics (USER, TEAM, PROJECT)
  - `AnalyticsType` (Enum): Types of analytics reports (PROGRESS, WORKLOAD, COMPREHENSIVE)
  - `SubtaskModel`: Represents individual work items with attributes like priority, due date, completion
  - `UserModel`: User information including ID and contact details
  - `TeamModel`: Team structure including lead and project association
  - `TaskModel`: Parent task container for subtasks
  - `MilestoneModel`: Project milestone definitions with due dates
  - `ProjectModel`: Project details including timeframes and management info

- **response_models.py**: Pydantic models for API responses
  - `BaseResponse`: Common fields for all responses (success, message)
  - `UserProgressResponse`: User completion metrics and subtask details
  - `UserWorkloadResponse`: User task load metrics by priority and due dates
  - `TeamProgressResponse`: Team completion metrics and member performance
  - `TeamWorkloadResponse`: Team resource allocation and member workloads
  - `ProjectProgressResponse`: Overall project progress and team contributions
  - `ProjectWorkloadResponse`: Resource allocation and bottleneck analysis
  - Various visualization and recommendation models

### 3. Services (`/services`)
- **user_analytics/progress.py**: 
  - Calculates user completion rates, on-time vs late completions
  - Provides detailed task completion statistics

- **user_analytics/workload.py**:
  - Analyzes pending tasks by priority and due dates
  - Estimates workload hours and identifies potential overloads

- **user_analytics/comprehensive.py**:
  - Combines progress and workload analytics
  - Adds historical performance and personalized recommendations

- **team_analytics/progress.py**:
  - Aggregates team member progress metrics
  - Tracks milestone completion rates

- **team_analytics/workload.py**:
  - Analyzes distribution of work across team members
  - Identifies workload balance/imbalance

- **team_analytics/comprehensive.py**:
  - Provides holistic team performance view
  - Generates team-level recommendations

- **project_analytics/progress.py**:
  - Tracks overall project completion against targets
  - Analyzes team contributions to project progress

- **project_analytics/workload.py**:
  - Examines resource allocation across teams
  - Identifies project bottlenecks and overallocated resources

- **project_analytics/comprehensive.py**:
  - Provides project health assessment
  - Generates project-level recommendations and estimates completion dates

### 4. Data Layer (`/data`)
- **data_access.py**: Abstract interface for data retrieval operations
  - Would normally connect to a database to fetch real data

- **data_access_test.py**: Test implementation using example.json
  - Simulates database operations for development and testing

- **cache.py**: Caching mechanism to improve performance
  - Stores frequently accessed analytics calculations

### 5. Utilities (`/utils`)
- **auth_utils.py**: Authentication and authorization
  - Implements JWT token handling
  - Role-based permission system (user, team_lead, project_manager)
  - Controls access to different analytics resources

- **analytics_utils.py**: Core calculation functions
  - `calculate_completion_rate`: Computes percentage completion
  - `get_aware_datetime`: Standardizes datetime handling
  - `calculate_due_dates_distribution`: Groups tasks by due date periods
  - `calculate_milestone_completion`: Computes milestone progress
  - `calculate_estimated_completion_date`: Predicts project completion
  - Various other analytics helper functions

### 6. Configuration (`/config`)
- **settings.py**: Application configuration settings
  - Defines environment-specific configurations

## Logic Flow

1. **Request Flow**:
   - A client makes a request to an endpoint (e.g., `/api/analytics/user/user-101/progress`)
   - FastAPI routes the request to the corresponding handler in the API layer
   - Authentication middleware validates the JWT token and extracts user info

2. **Permission Check**:
   - auth_utils.py checks if the authenticated user has permission to access the requested resource
   - For example, regular users can only view their own analytics, while team leads can view their team members' analytics

3. **Service Layer Processing**:
   - The route handler calls the appropriate service (e.g., `user_analytics/progress.py`)
   - The service retrieves required data via the data access layer (`data_access.py` or `data_access_test.py`)
   - If data is already cached, it's retrieved from the cache instead

4. **Analytics Calculation**:
   - The service uses helper functions from analytics_utils.py to perform calculations
   - For example, calculating completion rates, workload distribution, etc.

5. **Response Formation**:
   - Results are mapped to the appropriate response model from response_models.py
   - If visualization is requested, the service generates visualization data
   - The complete response is returned to the API layer

6. **Comprehensive Analytics Flow**:
   - For comprehensive endpoints, the service first collects basic progress and workload data
   - It then enriches this data with additional metrics, recommendations, and visualizations
   - The complete analysis is presented in a unified response

7. **Client Integration**:
   - External services can consume these analytics through the REST API
   - The `AnalyticsServiceClient` class provides a wrapper for making authenticated requests to these endpoints

This microservice is designed with clear separation of concerns, making it easy to extend or modify specific analytics calculations without affecting the rest of the system.


#### JWT
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

##### This must be the same key used in the analytics service
JWT_SECRET_KEY = "your-secret-key-for-development-only"  # Use env vars in production
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_service_token(service_name: str, target_service: str, role: str = "service") -> str:
    """
    Create a JWT token for service-to-service communication
    
    Args:
        service_name: Name/ID of the calling service
        target_service: Name of the service being called
        role: Role to assume (usually service, or a specific role like project_manager)
        
    Returns:
        JWT token string
    """
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": service_name,  # Subject (caller ID)
        "role": role,         # Role to assume
        "target": target_service,  # Target service
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp()  # Issued at
    }
    
    # Sign the token with the shared secret
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return token





# Remove it
## Prompt
AdarshOnGith: I am building a project management subsystem:

I facillitates following things:

a user can create a project with following steps:
user need to assign a user (himself or other user) as role of project manager
project manager define teams for this project
project manger define milestones and order of milestones for the project (think as a pipeline each team need to follow for the subtask team has)
each team need to be assigned with Team Lead by project manager
project has multiple teams, team is in only one project
project manager defines Task (broad view) for project
one to one mapping for Task and Team, so each Task assigned to one team
each Task is divided into sub tasks which is actually worked by team

each Team has team members apart from team lead
each member is only in one team  within a project.
members can be added to team by respective team lead or project manager
Team Lead breaks Task into subtasks, subtasks can be assigned to a team members. (this subtask follows the milestone pipeline)

team member updates the task 

There is analytics microservice to facillitate following 3 types of analytics:
- progress/completion rate analytics
- workload analytics
- comprehensive report (pending, progress, workload analytics).

now these 3 type of analytics can be requested as follows:
- user level analytics (for all the subtask assigned to user taken into consideration) -- requested for given user

-team level analytics (team analytics has analytics related to all subtasks team has, and analytics for team members in team ) -- requested for given team given project

- project level analytics (project analytics specific to all teams present in the project contains analytics related to all subtask present in the project, all members present in project, all teams in project).

user  level analytics can be requested by user himself for all the subtasks he has ( across many projects or many teams etc)

user level analytics can be requested by Team Lead or Project Manager for the team member.

team level  analytics can be requested by team lead (for his team) or project manager for particular team in the project

project level analytics can only be requested by project manager for his project.




Refer the example.json for example schema, i wil give breif of other system to relate :
1. User Management
Users have:

id, name, email, contact.

No global roles (roles are project-specific).

Project-Specific Roles:

Assigned via projects.project_manager_id, teams.team_lead_id, or team_members table.

2. Project Structure
Projects:

Have metadata: description, status, priority, client, department, start/end dates.

Track completion_percentage.

Teams:

Belong to one project, have one lead, and multiple members.

Tasks:

Assigned to teams with target_due_date.

Subtasks:

Assigned to individuals (assigned_to).

Support dependencies (parent_subtask_id).

Track priority, due_date, estimated_hours, completed status.

Milestones
Define project phases (e.g., "Design, develop, test").

Attributes:

sequence_no (order in pipeline), due_date, description.

Linked to a single project (project_id).
Project Manager:

Creates a project (Website Redesign).

Defines milestones (Design → Development → Launch).

Assigns team leads.

Team Lead:

Breaks tasks into subtasks (e.g., "Implement Login UI").

Assigns subtasks to members.

Team Member:

Completes subtasks, marking them as done.

Progress reflects in milestones/project completion.


ok so now, 
leave the access control suppose they are in place, give implementation of analytics microserve to provide the response for the various type of valid request (suppose access level validation is in place and request reaches is requested my correct role user)
and give me complete roadmap for analytics microservice.


