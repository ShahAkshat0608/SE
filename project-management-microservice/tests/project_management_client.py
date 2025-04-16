import requests
from typing import List, Dict, Optional, Any
import json
import logging


logger = logging.getLogger(__name__)

class ProjectManagementClient:
    """
    Client for interacting with the Project Management microservice API.
    This client handles authentication and provides methods for all endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", token: str = None):
        """
        Initialize the Project Management API client.
        
        Args:
            base_url: Base URL of the Project Management microservice
            token: Authentication token (JWT)
        """
        self.base_url = base_url
        self.token = token
        
    def check_health(self) -> Dict:
        """
        Check basic health status of the service.
        
        Returns:
            Dictionary with service health information
        """
        url = f"{self.base_url}/api/health"
        response = requests.get(url)
        return self._handle_response(response)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token if available."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response and log errors."""
        try:
            if response.status_code >= 400:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_detail = error_data["detail"]
                except:
                    error_detail = response.text
                
                logger.error(f"API Error {response.status_code}: {error_detail}")
                return {"error": True, "status_code": response.status_code, "detail": error_detail}
            
            return response.json()
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return {"error": True, "status_code": 500, "detail": f"Failed to process response: {str(e)}"}
    
    def set_token(self, token: str) -> None:
        """Set the authentication token."""
        self.token = token
    
    # --- User Authentication & Management ---
    
    def login(self, email: str, password: str) -> Dict:
        """
        Login to get authentication token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict containing access token and user information if successful
        """
        url = f"{self.base_url}/api/auth/login"
        # OAuth2 expects form data, not JSON
        data = {"username": email, "password": password}
        response = requests.post(url, data=data)
        return self._handle_response(response)
    
    def register(self, name: str, email: str, password: str, contact: str = None) -> Dict:
        """
        Register a new user.
        
        Args:
            name: User's full name
            email: User's email address
            password: User's password
            contact: Optional contact information
            
        Returns:
            Dict containing the registration result
        """
        print("Registering user...")
        url = f"{self.base_url}/api/auth/register"
        params = {"name": name, "email": email, "password": password}
        if contact:
            params["contact"] = contact
        
        response = requests.post(url, params=params)
        return self._handle_response(response)
    
    def get_user_details(self, user_id: str) -> Dict:
        """Get details of a specific user."""
        url = f"{self.base_url}/api/users/{user_id}"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
        
    # --- Common User Functions ---
    
    def get_initial_options(self) -> Dict:
        """Get initial options for the current user."""
        url = f"{self.base_url}/api/user/initial-options"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def create_project(self, project_data: Dict) -> Dict:
        """Create a new project."""
        url = f"{self.base_url}/api/projects"
        response = requests.post(url, json=project_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_project_details(self, project_id: str) -> Dict:
        """Get project details."""
        url = f"{self.base_url}/api/projects/{project_id}"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_user_role_in_project(self, project_id: str) -> Dict:
        """Get current user's role in a specific project."""
        url = f"{self.base_url}/api/projects/{project_id}/role"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_milestones(self, project_id: str) -> List[Dict]:
        """Get all milestones for a project."""
        url = f"{self.base_url}/api/projects/{project_id}/milestones"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_teams(self, project_id: str) -> List[Dict]:
        """Get all teams for a project."""
        url = f"{self.base_url}/api/projects/{project_id}/teams"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_project_tasks(self, project_id: str) -> List[Dict]:
        """Get all tasks for a project."""
        url = f"{self.base_url}/api/projects/{project_id}/tasks"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_team_tasks(self, project_id: str, team_id: str) -> List[Dict]:
        """Get all tasks for a specific team."""
        url = f"{self.base_url}/api/projects/{project_id}/teams/{team_id}/tasks"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_subtasks(self, task_id: str) -> List[Dict]:
        """Get all subtasks for a task."""
        url = f"{self.base_url}/api/tasks/{task_id}/subtasks"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def search_users(self, query: Optional[str] = None) -> List[Dict]:
        """Search for users, optionally with a query string."""
        url = f"{self.base_url}/api/users"
        params = {}
        if query:
            params["q"] = query
        response = requests.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)
    
    # --- Project Manager Functions ---
    
    def create_milestone(self, project_id: str, milestone_data: Dict) -> Dict:
        """Create a milestone (Project Manager only)."""
        url = f"{self.base_url}/api/projects/{project_id}/milestones"
        response = requests.post(url, json=milestone_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def create_team(self, project_id: str, team_data: Dict) -> Dict:
        """Create a team (Project Manager only)."""
        url = f"{self.base_url}/api/projects/{project_id}/teams"
        response = requests.post(url, json=team_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def create_task(self, project_id: str, team_id: str, task_data: Dict) -> Dict:
        """Create a task for a team (Project Manager only)."""
        url = f"{self.base_url}/api/projects/{project_id}/teams/{team_id}/tasks"
        response = requests.post(url, json=task_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def view_project_analytics(self, project_id: str) -> Dict:
        """View analytics for a project (Project Manager only)."""
        url = f"{self.base_url}/api/projects/{project_id}/analytics"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_project_roles(self, project_id: str) -> List[Dict]:
        """Get all roles assigned in a project (Project Manager only)."""
        url = f"{self.base_url}/api/projects/{project_id}/roles"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def assign_project_role(self, project_id: str, user_id: str, role: str) -> Dict:
        """Assign a role to a user in a project (Project Manager only)."""
        url = f"{self.base_url}/api/projects/{project_id}/roles"
        role_data = {"user_id": user_id, "role": role}
        response = requests.post(url, json=role_data, headers=self._get_headers())
        return self._handle_response(response)
    
    # --- Team Lead Functions ---
    
    def create_subtask(self, task_id: str, subtask_data: Dict) -> Dict:
        """Create a subtask for a task (Team Lead only)."""
        url = f"{self.base_url}/api/tasks/{task_id}/subtasks"
        response = requests.post(url, json=subtask_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def update_subtask(self, subtask_id: str, subtask_data: Dict) -> Dict:
        """Update a subtask (Team Lead can update all fields)."""
        url = f"{self.base_url}/api/subtasks/{subtask_id}"
        response = requests.put(url, json=subtask_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def delete_subtask(self, subtask_id: str) -> Dict:
        """Delete a subtask (Team Lead only)."""
        url = f"{self.base_url}/api/subtasks/{subtask_id}"
        response = requests.delete(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def add_team_member(self, team_id: str, user_id: str) -> Dict:
        """Add a member to a team (Team Lead only)."""
        url = f"{self.base_url}/api/teams/{team_id}/members"
        member_data = {"user_id": user_id}
        response = requests.post(url, json=member_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def remove_team_member(self, team_id: str, user_id: str) -> Dict:
        """Remove a member from a team (Team Lead only)."""
        url = f"{self.base_url}/api/teams/{team_id}/members/{user_id}"
        response = requests.delete(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def assign_subtask(self, subtask_id: str, user_id: str) -> Dict:
        """Assign a subtask to a user (Team Lead only)."""
        url = f"{self.base_url}/api/subtasks/{subtask_id}/assign"
        assign_data = {"user_id": user_id}
        response = requests.put(url, json=assign_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def view_team_analytics(self, team_id: str) -> Dict:
        """View analytics for a team (Team Lead only)."""
        url = f"{self.base_url}/api/teams/{team_id}/analytics"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    # --- Team Member Functions ---
    
    def update_subtask_completion(self, subtask_id: str, is_completed: bool) -> Dict:
        """Update subtask completion status (Team Member)."""
        url = f"{self.base_url}/api/subtasks/{subtask_id}/completion"
        completion_data = {"is_completed": is_completed}
        response = requests.put(url, json=completion_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def update_subtask_milestone(self, subtask_id: str, milestone_id: str) -> Dict:
        """Update subtask milestone (Team Member)."""
        url = f"{self.base_url}/api/subtasks/{subtask_id}/milestone"
        milestone_data = {"milestone_id": milestone_id}
        response = requests.put(url, json=milestone_data, headers=self._get_headers())
        return self._handle_response(response)
    
    def get_assigned_subtasks(self) -> List[Dict]:
        """Get subtasks assigned to current user (Team Member)."""
        url = f"{self.base_url}/api/user/subtasks"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)
    
    def view_user_analytics(self) -> Dict:
        """View analytics for current user (Team Member)."""
        url = f"{self.base_url}/api/user/analytics"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)