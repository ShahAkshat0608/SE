from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
from uuid import UUID

from ..models.enums import RoleType
from ..workflow.user_workflow import UserWorkflow
from ..workflow.project_manager_workflow import ProjectManagerWorkflow
from ..workflow.team_lead_workflow import TeamLeadWorkflow
from ..workflow.team_member_workflow import TeamMemberWorkflow
from ..utils.auth_utils import get_current_user
from ..services.clients.user_management_client import APIClient
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
import time
from ..utils.auth_token_gen import create_access_token
from ..utils.auth_utils import verify_token

router = APIRouter()
user_client = APIClient()
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyIiwiZW1haWwiOiJhYmNAZ21haWwuY29tIiwiZXhwIjoxNzQ0OTYzNzQwLjc4NjM5NH0.bILP83gyTl1BVC-AnNj6nRlWeJtKKej0VKDr1jJXZbk"
# access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1IiwiZW1haWwiOiJqa2xAZ21haWwuY29tIiwiZXhwIjoxNzQ0OTgwNDgwLjQzMzI5fQ.Qw7tGmHqR7Dgj_g_-HxhwuzTpNFMqe9WM5j9Pa0LIiE"

# --- User Workflow Endpoints ---

@router.get("/user/initial-options", response_model=Dict)
async def get_initial_options():
    """Get initial options for the current user"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = UserWorkflow()
    return workflow.get_initial_options(current_user["id"])

@router.post("/projects", response_model=Dict)
async def create_project(project_data: Dict):
    """Create a new project"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = UserWorkflow()
    return workflow.create_project(current_user["id"], project_data)

@router.get("/projects/{project_id}/role", response_model=Dict)
async def get_user_role_in_project(project_id: str):
    """Get current user's role in a specific project"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = UserWorkflow()
    role = workflow.get_user_role_in_project(current_user["id"], project_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have a role in this project")
    return {"role": role}

# --- Project Manager Endpoints ---

@router.get("/projects/{project_name}")
async def get_project_details(project_name: str):
    """Get project details"""
    workflow = ProjectManagerWorkflow()
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    try:
        project_details = workflow.get_project_details_by_name(project_name)

        # Check if user has access to this project
        user_role = workflow.get_user_role_in_project(current_user["id"], project_details["id"])
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this project")
        
        # # Get project details
        # return workflow.get_project_details(project_id)
        return project_details
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.post("/projects/{project_id}/milestones", response_model=Dict)
async def create_milestone(
    project_id: str, 
    milestone_name : str,
    milestone_description: str,
    milestone_sequence_no: int,
   # milestone due date is a string in ISO format and optional
    milestone_due_date: Optional[str] = None,
):
    """Create a milestone (Project Manager)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = ProjectManagerWorkflow()

    milestone_data = {
        "name": milestone_name,
        "description": milestone_description,
        "sequence_no": milestone_sequence_no,
    }
    if milestone_due_date:
        milestone_data["due_date"] = milestone_due_date
    try:
        return workflow.create_milestone(current_user["id"], project_id, milestone_data)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/projects/{project_id}/milestones", response_model=List[Dict])
async def get_milestones(project_id: str):
    """Get all milestones for a project"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    user_workflow = UserWorkflow()
    project_workflow = ProjectManagerWorkflow()
    try:
        # Check if user has access to this project
        user_role = user_workflow.get_user_role_in_project(current_user["id"], project_id)
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this project")
        
        # Get milestones
        return project_workflow.get_milestones(project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/projects/{project_id}/teams", response_model=Dict)
async def create_team(
    project_id: str, 
    team_name: str,
    team_lead_id: str,
    team_type: Optional[str] = None,
):  
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    """Create a team (Project Manager)"""
    workflow = ProjectManagerWorkflow()

    team_data = {
        "name": team_name,
        "team_lead_id": team_lead_id,
        "type": team_type or 'DEFAULT',
    }
    try:
        return workflow.create_team(current_user["id"], project_id, team_data)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/projects/{project_id}/teams", response_model=List[Dict])
async def get_teams(project_id: str):
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    """Get all teams for a project"""
    user_workflow = UserWorkflow()
    project_workflow = ProjectManagerWorkflow()
    try:
        # Check if user has access to this project
        user_role = user_workflow.get_user_role_in_project(current_user["id"], project_id)
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this project")
        
        # Get teams
        return project_workflow.get_teams(project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/projects/{project_id}/teams/{team_id}/tasks", response_model=Dict)
async def create_task(
    project_id: str,
    team_id: str,
    task_name: str,
    task_description: str,
    task_status: Optional[str] = "TO_DO",
    task_due_date: Optional[str] = None,
    task_priority: Optional[str] = "MEDIUM",
):
    """Create a task for a team (Project Manager)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)

    task_data = {
        "name": task_name,
        "description": task_description,
        "status": task_status,
        "priority": task_priority,
    }
    if task_due_date:
        task_data["target_due_date"] = task_due_date

    workflow = ProjectManagerWorkflow()
    try:
        return workflow.create_task(current_user["id"], project_id, team_id, task_data)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/projects/{project_id}/tasks", response_model=List[Dict])
async def get_project_tasks(project_id: str):
    """Get all tasks for a project"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    user_workflow = UserWorkflow()
    project_workflow = ProjectManagerWorkflow()
    try:
        # Check if user has access to this project
        user_role = user_workflow.get_user_role_in_project(current_user["id"], project_id)
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this project")
        
        # Get tasks
        return project_workflow.get_tasks(project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/projects/{project_id}/teams/{team_id}/tasks", response_model=List[Dict])
async def get_team_tasks(
    project_id: str,
    team_id: str,
):
    """Get all tasks for a specific team"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    user_workflow = UserWorkflow()
    project_workflow = ProjectManagerWorkflow()
    try:
        # Check if user has access to this project
        user_role = user_workflow.get_user_role_in_project(current_user["id"], project_id)
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this project")
        
        # Get team tasks
        return project_workflow.get_tasks_by_team(project_id, team_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/projects/{project_id}/analytics", response_model=Dict)
async def view_project_analytics(project_id: str):
    """View analytics for a project (Project Manager)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = ProjectManagerWorkflow()
    try:
        return workflow.view_project_analytics(current_user["id"], project_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Team Lead Endpoints ---

@router.post("/tasks/{task_id}/subtasks", response_model=Dict)
async def create_subtask(
    task_id: str,
    subtask_name: str,
    subtask_description: str,
    subtask_priority: Optional[str] = "MEDIUM",
    subtask_due_date: Optional[str] = None,
    subtask_milestone_id: Optional[str] = None,
    subtask_tags: Optional[List[str]] = None,
):
    """Create a subtask for a task (Team Lead)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamLeadWorkflow()

    subtask_data = {
        "name": subtask_name,
        "description": subtask_description,
    }
    if subtask_priority:
        subtask_data["priority"] = subtask_priority
    if subtask_due_date:
        subtask_data["due_date"] = subtask_due_date
    if subtask_milestone_id:
        subtask_data["milestone_id"] = subtask_milestone_id
    if subtask_tags:
        subtask_data["tags"] = subtask_tags

    try:
        return workflow.create_subtask(current_user["id"], task_id, subtask_data)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/tasks/{task_id}/subtasks", response_model=List[Dict])
async def get_subtasks(task_id: str):
    """Get all subtasks for a task"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    user_workflow = UserWorkflow()
    workflow = TeamLeadWorkflow()
    try:
        # Get the task to check the project
        task = workflow.get_task_details(task_id)
        
        # Check if user has access to this project
        user_role = user_workflow.get_user_role_in_project(current_user["id"], task["project_id"])
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this project")
        
        # Get subtasks
        return workflow.get_subtasks_details(task_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/subtasks/{subtask_id}", response_model=Dict)
async def update_subtask(
    subtask_id: str,
    subtask_data: Dict,
):
    """Update a subtask (Team Lead can update all fields)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamLeadWorkflow()
    try:
        return workflow.update_subtask(current_user["id"], subtask_id, subtask_data)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/subtasks/{subtask_id}", response_model=Dict)
async def delete_subtask(subtask_id: str):
    """Delete a subtask (Team Lead only)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamLeadWorkflow()
    try:
        return workflow.delete_subtask(current_user["id"], subtask_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/teams/{team_id}/members", response_model=Dict)
async def add_team_member(
    team_id: str,
    member_id : str,
):
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    """Add a member to a team (Team Lead)"""
    workflow = TeamLeadWorkflow()
    try:
        return {"success": workflow.add_team_member(current_user["id"], team_id, member_id)}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/teams/{team_id}/members/{user_id}", response_model=Dict)
async def remove_team_member(
    team_id: str,
    user_id: str,
):
    """Remove a member from a team (Team Lead)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamLeadWorkflow()
    try:
        return {"success": workflow.remove_team_member(current_user["id"], team_id, user_id)}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/subtasks/{subtask_id}/assign", response_model=Dict)
async def assign_subtask(
    subtask_id: str,
    assign_user_id: str,
):
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    """Assign a subtask to a user (Team Lead)"""
    workflow = TeamLeadWorkflow()
    try:
        return workflow.assign_subtask(current_user["id"], subtask_id, assign_user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/teams/{team_id}/analytics", response_model=Dict)
async def view_team_analytics(team_id: str):
    """View analytics for a team (Team Lead)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamLeadWorkflow()
    try:
        return workflow.view_team_analytics(current_user["id"], team_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Team Member Endpoints ---

@router.put("/subtasks/{subtask_id}/completion", response_model=Dict)
async def update_subtask_completion(
    subtask_id: str,
    isCompleted: bool,
):
    """Update subtask completion status (Team Member)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamMemberWorkflow()
    try:
        return workflow.update_subtask_completion(
            current_user["id"], 
            subtask_id, 
            isCompleted
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/subtasks/{subtask_id}/milestone", response_model=Dict)
async def update_subtask_milestone(
    subtask_id: str,
    milestone_id: str,
):
    """Update subtask milestone (Team Member)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamMemberWorkflow()
    try:
        return workflow.update_subtask_milestone(
            current_user["id"], 
            subtask_id, 
            milestone_id
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/user/subtasks", response_model=List[Dict])
async def get_assigned_subtasks():
    """Get subtasks assigned to current user (Team Member)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamMemberWorkflow()
    return workflow.get_assigned_subtasks(current_user["id"])

@router.get("/user/analytics", response_model=Dict)
async def view_user_analytics():
    """View analytics for current user (Team Member)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = TeamMemberWorkflow()
    return workflow.view_user_analytics(current_user["id"])

# --- Additional Utility Endpoints ---

@router.get("/projects/{project_id}/roles", response_model=List[Dict])
async def get_project_roles(project_id: str):
    """Get all roles assigned in a project (Project Manager)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = ProjectManagerWorkflow()
    try:
        return workflow.get_project_roles(current_user["id"], project_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/projects/{project_id}/roles", response_model=Dict)
async def replace_team_lead(
    project_id: str,
    team_id: str,
    new_team_lead_id: str,
):
    """Assign a role to a user in a project (Project Manager only)"""
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    workflow = ProjectManagerWorkflow()
    try:
        return workflow.replace_team_lead(
            current_user["id"], 
            project_id, 
            team_id,
            new_team_lead_id
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Auth Endpoints for User Management ---

@router.post("/auth/register", response_model=Dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    name: str,
    email: str,
    password: str,
    contact: Optional[str] = None
):
    """
    Register a new user through the User Management service
    """
    # Basic input validation
    if not all([name.strip(), email.strip(), password.strip()]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name, email, and password are required and cannot be empty"
        )

    response = user_client.register_user(name, email, password, contact)
    
    if "error" in response:
        status_code = {
            "Conflict": status.HTTP_409_CONFLICT,
            "Bad Request": status.HTTP_400_BAD_REQUEST
        }.get(response["error"], status.HTTP_400_BAD_REQUEST)
        raise HTTPException(
            status_code=status_code,
            detail=response.get("detail", "Registration failed")
        )
    
    return {
        "success": True,
        "message": "User registered successfully",
        "user": response
    }

@router.post("/auth/login", response_model=Dict , status_code=status.HTTP_200_OK)
async def login_user(email : str, password: str):
    """
    Login a user and return access token
    """
    # Basic input validation
    if not all([email.strip(), password.strip()]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required and cannot be empty"
        )

    auth_response = user_client.login_user(email, password)
    
    if "error" in auth_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=auth_response.get("detail", "Authentication failed"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_response  # Response is user data directly
    access_token_expires = timedelta(days=30)
    access_token = create_access_token(
        data={"sub": str(user.get("id")), "email": user.get("email")},
        # expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role", "user")  # Include global role if provided
        }
    }

@router.post("/auth/logout", response_model=Dict)
async def logout_user(current_user: Dict = Depends(get_current_user)):
    """
    Log out current user 
    
    Note: In a token-based system, true logout happens client-side by removing the token,
    but this endpoint can be used for tracking logout events or invalidating tokens 
    on the server if a token blacklist is implemented
    """
    return {
        "success": True,
        "message": "User logged out successfully"
    }

@router.get("/auth/me", response_model=Dict)
async def get_current_user_profile():
    """
    Get the current authenticated user's profile
    """
    current_user_payload = await verify_token({"credentials": access_token})
    current_user = await get_current_user(current_user_payload)
    
    user_details = user_client.get_user_details(int(current_user["id"]))
    
    if "error" in user_details:
        status_code = {
            "Not Found": status.HTTP_404_NOT_FOUND,
            "Bad Request": status.HTTP_400_BAD_REQUEST
        }.get(user_details["error"], status.HTTP_400_BAD_REQUEST)
        raise HTTPException(
            status_code=status_code,
            detail=user_details.get("detail", "Failed to retrieve user details")
        )
    
    return user_details

@router.get("/auth/users/{user_id}", response_model=Dict)
async def get_user_details(user_id: int):
    """
    Get details of a specific user
    """
    user_details = user_client.get_user_details(user_id)
    
    if "error" in user_details:
        status_code = {
            "Not Found": status.HTTP_404_NOT_FOUND,
            "Bad Request": status.HTTP_400_BAD_REQUEST
        }.get(user_details["error"], status.HTTP_400_BAD_REQUEST)
        raise HTTPException(
            status_code=status_code,
            detail=user_details.get("detail", "Failed to retrieve user details")
        )
    
    return user_details

@router.get("/health", include_in_schema=True)
async def health_check():
    """
    Health check endpoint to verify the service is up and running
    Returns basic service status
    """
    return {
        "status": "healthy",
        "service": "project-management-microservice",
        "timestamp": int(time.time())
    }