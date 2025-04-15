from typing import List
from uuid import UUID
from ..models.role import Role

class RoleService:
    def assignRole(self, role: Role) -> Role:
        pass

    def modifyRole(self, roleId: UUID, newRole: str) -> Role:
        pass

    def removeRole(self, roleId: UUID) -> bool:
        pass

    def getUserRoles(self, userId: UUID) -> List[Role]:
        pass

    def getProjectRoles(self, projectId: UUID) -> List[Role]:
        pass

    def checkAccess(self, userId: UUID, projectId: UUID, requiredRole: str) -> bool:
        pass

    def hasProjectManagerAccess(self, userId: UUID, projectId: UUID) -> bool:
        pass

    def hasTeamLeadAccess(self, userId: UUID, teamId: UUID) -> bool:
        pass

    def hasTeamMemberAccess(self, userId: UUID, teamId: UUID) -> bool:
        pass