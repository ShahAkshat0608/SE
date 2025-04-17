from typing import List
from uuid import UUID
import uuid 
from ..models.role import Role
from ..database.role_dal import RoleDAL
from ..constants.constants import ROLE_PROJECT_MANAGER, ROLE_TEAM_LEAD, ROLE_TEAM_MEMBER, ROLE_HIERARCHY

class RoleService:
    def __init__(self, role_dal: RoleDAL = None):
        """Initialize the role service with a data access layer."""
        self.role_dal = role_dal or RoleDAL()
    
    def assignRole(self, role: Role) -> Role:
        """
        Assign a role to a user for a specific project.
        
        Args:
            role: The role object to be assigned
            
        Returns:
            The assigned role
            
        Raises:
            ValueError: If the user already has a role in this project
        """
        # Check if the user already has a role in this project
        user_roles = self.role_dal.get_roles_by_user(role.user_id)
        for existing_role in user_roles:
            if existing_role.project_id == role.project_id:
                raise ValueError(f"User {role.user_id} already has a role in project {role.project_id}")
        
        # Validate role value
        if role.role not in [ROLE_PROJECT_MANAGER, ROLE_TEAM_LEAD, ROLE_TEAM_MEMBER]:  
            raise ValueError(f"Invalid role: {role.role}. Must be one of: PROJECT_MANAGER, TEAM_LEAD, TEAM_MEMBER")
            
        # Generate ID if not provided
        if not role.id:
            role.id = f"role-{str(uuid.uuid4())[:8]}"
            
        # Add role to database
        self.role_dal.add_role(role)
        
        return role

    def modifyRole(self, roleId: UUID, newRole: str) -> Role:
        """
        Modify an existing role.
        
        Args:
            roleId: The UUID of the role to modify
            newRole: The new role value
            
        Returns:
            The updated role object
            
        Raises:
            ValueError: If role with given ID is not found or if new role is invalid
        """
        # Validate new role value
        if newRole not in [ROLE_PROJECT_MANAGER, ROLE_TEAM_LEAD, ROLE_TEAM_MEMBER]: 
            raise ValueError(f"Invalid role: {newRole}. Must be one of: PROJECT_MANAGER, TEAM_LEAD, TEAM_MEMBER")
        
        # Convert UUID to string for DAL
        role_id_str = str(roleId)
        
        # Get existing role
        existing_role = self.role_dal.get_role(role_id_str)
        if not existing_role:
            raise ValueError(f"Role with ID {roleId} not found")
        
        # Update the role
        existing_role.role = newRole
        self.role_dal.update_role(role_id_str, existing_role)
        
        return existing_role

    def removeRole(self, roleId: UUID) -> bool:
        """
        Remove a role assignment.
        
        Args:
            roleId: The UUID of the role to remove
            
        Returns:
            True if the role was successfully removed
            
        Raises:
            ValueError: If role with given ID is not found
        """
        # Convert UUID to string for DAL
        role_id_str = str(roleId)
        
        # Check if role exists
        existing_role = self.role_dal.get_role(role_id_str)
        if not existing_role:
            raise ValueError(f"Role with ID {roleId} not found")
        
        # Remove the role
        self.role_dal.delete_role(role_id_str)
        return True

    def getUserRoles(self, userId: UUID) -> List[Role]:
        """
        Get all roles for a specific user.
        
        Args:
            userId: The UUID of the user
            
        Returns:
            List of roles assigned to the user
        """
        # Convert UUID to string for DAL
        user_id_str = str(userId)
        return self.role_dal.get_roles_by_user(user_id_str)

    def getProjectRoles(self, projectId: UUID) -> List[Role]:
        """
        Get all roles in a specific project.
        
        Args:
            projectId: The UUID of the project
            
        Returns:
            List of roles assigned in the project
        """
        # Convert UUID to string for DAL
        project_id_str = str(projectId)
        return self.role_dal.get_roles_by_project(project_id_str)

    def checkAccess(self, userId: UUID, projectId: UUID, requiredRole: str) -> bool:
        """
        Check if a user has needed role or higher in a project.
        
        Args:
            userId: The UUID of the user
            projectId: The UUID of the project
            requiredRole: The role to check for
            
        Returns:
            True if the user has the required access level, False otherwise
        """
        # Convert UUIDs to strings for DAL
        user_id_str = str(userId)
        project_id_str = str(projectId)
        
        # Get user's role for this project
        user_role_obj = self.role_dal.get_role_by_user_and_project(user_id_str, project_id_str)
        
        # If user has no role in this project
        if not user_role_obj:
            return False
        
        # Check if user's role has sufficient privilege
        if user_role_obj.role in [ROLE_PROJECT_MANAGER, ROLE_TEAM_LEAD, ROLE_TEAM_MEMBER] and ROLE_HIERARCHY[user_role_obj.role] >= ROLE_HIERARCHY[requiredRole]:
            return True
            
        return False

    def hasProjectManagerAccess(self, userId: UUID, projectId: UUID) -> bool:
        """
        Check if a user has project manager access for a project.
        """
        return self.checkAccess(userId, projectId, ROLE_PROJECT_MANAGER)  

    def hasTeamLeadAccess(self, userId: UUID, projectId: UUID) -> bool:
        """
        Check if a user has team lead access for a project.
        """
        return self.checkAccess(userId, projectId, ROLE_TEAM_LEAD)  

    def hasTeamMemberAccess(self, userId: UUID, projectId: UUID) -> bool:
        """
        Check if a user has team member access for a project.
        """
        return self.checkAccess(userId, projectId, ROLE_TEAM_MEMBER) 

    def getRoleInProject(self, userId: UUID, projectId: UUID) -> Role:
        """
        Get the role of a user in a specific project.
        
        Args:
            userId: The UUID of the user
            projectId: The UUID of the project
        """
        return self.role_dal.get_role_by_user_and_project(userId, projectId)