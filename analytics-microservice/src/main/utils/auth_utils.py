from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from ..data.data_access_test import TestDataAccess
from ..data.data_access import DataAccess
import os

# JWT security scheme
security = HTTPBearer()

# Use the same hard-coded secret as in project-management-microservice
JWT_SECRET_KEY = "your-secret-key-for-development-only"  # Use env vars in production
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Load environment variables from .env file - commented out for now to use hard-coded values
# JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
# JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
# Get the value, default to '1440' if not set or empty
# token_expire_str = os.getenv('TOKEN_EXPIRE_MINUTES', '1440') 
# try:
#     TOKEN_EXPIRE_MINUTES = int(token_expire_str) 
# except (ValueError, TypeError):
#     # Fallback if the value is invalid
#     TOKEN_EXPIRE_MINUTES = 1440 

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

async def verify_token(credentials) -> Dict:
    """Verify JWT token and return payload"""
    # access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJzYXJ0aGFrYmFuc2FsMzk1QGdtYWlsLmNvbSIsImV4cCI6MTc0NTE2MTc2My40MTA0NTR9.lI3DKUTAkmccBLkR9gxGxohzkr4vha4sTK5-OumXpco"
    credentials = {credentials : "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJzYXJ0aGFrYmFuc2FsMzk1QGdtYWlsLmNvbSIsImV4cCI6MTc0NTE2MTc2My40MTA0NTR9.lI3DKUTAkmccBLkR9gxGxohzkr4vha4sTK5-OumXpco"}
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        
        # Check if token is expired
        if "exp" in payload and datetime.utcnow().timestamp() > payload["exp"]:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

def create_access_token(data: Dict) -> str:
    """Create a new JWT token"""
    to_encode = data.copy()
    
    # Set expiration
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    
    # Create token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt

def create_test_token(user_id: str, role: str) -> str:
    """Create a test token for development purposes"""
    token_data = {
        "sub": user_id,
        "role": role,
        "name": f"Test {role.capitalize()}"
    }
    return create_access_token(token_data)

async def get_current_user(token: Dict = Depends(verify_token)) -> Dict:
    """Get current user from token"""
    print("Token:", token)
    return {
        "user_id": token.get("sub"),
        "role": token.get("role", "user"),
        "name": token.get("name", "Unknown User")
    }

async def check_analytics_permission(
    request: Request,
    resource_type: str,
    resource_id: str,
    project_id: str = None,
    current_user: Dict = None
) -> bool:
    """
    Check if user has permission to access the specified analytics resource
    
    Args:
        request: FastAPI request object
        resource_type: Type of resource (USER_ANALYTICS, TEAM_ANALYTICS, PROJECT_ANALYTICS)
        resource_id: ID of the resource (user_id, team_id or project_id)
        project_id: Optional project ID for team analytics
        current_user: Current user data from token
        
    Returns:
        Boolean indicating if user has permission
    """
    if not current_user:
        return False
    
    user_id = current_user.get("user_id")
    role = current_user.get("role", "user")
    
    # Get data access layer
    data_access = DataAccess()
    
    # Get permissions for this role and resource
    permissions = RolePermission.PERMISSIONS.get(role, {}).get(resource_type, [])
    
    # Check specific permissions
    if resource_type == RolePermission.USER_ANALYTICS:
        # User can always view their own analytics
        if resource_id == user_id:
            return True
        
        # Team lead can view team members' analytics
        if RolePermission.VIEW_TEAM in permissions:
            is_team_lead = await data_access.is_user_team_lead(user_id, await data_access.get_team_id_for_lead(user_id))
            target_user = await data_access.get_user_by_id(resource_id)
            
            if is_team_lead and target_user and target_user.get("team_id"):
                return await data_access.is_user_team_lead(user_id, target_user.get("team_id"))
        
        # Project manager can view any user in their projects
        if RolePermission.VIEW_PROJECT in permissions:
            managed_project_id = await data_access.get_project_id_for_manager(user_id)
            return await data_access.is_user_in_project(resource_id, managed_project_id)
    
    elif resource_type == RolePermission.TEAM_ANALYTICS:
        # Team lead can view their own team
        if RolePermission.VIEW_TEAM in permissions:
            user_team_id = None
            user_data = await data_access.get_user_by_id(user_id)
            if user_data:
                user_team_id = user_data.get("team_id")
            
            # For team leads
            if role == RolePermission.TEAM_LEAD:
                led_team_id = await data_access.get_team_id_for_lead(user_id)
                return resource_id == led_team_id or resource_id == user_team_id
        
        # Project manager can view any team in their projects
        if RolePermission.VIEW_PROJECT in permissions:
            managed_project_id = await data_access.get_project_id_for_manager(user_id)
            if not managed_project_id or not project_id:
                return False
                
            return managed_project_id == project_id
    
    elif resource_type == RolePermission.PROJECT_ANALYTICS:
        # Project manager can view their projects
        if RolePermission.VIEW_PROJECT in permissions:
            managed_project_id = await data_access.get_project_id_for_manager(user_id)
            return managed_project_id == resource_id
    
    return False

def has_role(required_roles: List[str]):
    """
    Dependency to check if user has one of the required roles
    
    Args:
        required_roles: List of allowed roles
        
    Returns:
        Dependency function that checks the user's role
    """
    async def check_role(current_user: Dict = Depends(get_current_user)):
        if current_user["role"] not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Operation requires one of these roles: {', '.join(required_roles)}"
            )
        return current_user
    return check_role