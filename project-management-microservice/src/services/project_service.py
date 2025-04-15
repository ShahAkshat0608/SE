from typing import List
from uuid import UUID
from ..models.project import Project

class ProjectService:
    def createProject(self, project: Project) -> Project:
        pass

    def getProject(self, projectId: UUID) -> Project:
        pass

    def updateProject(self, project: Project) -> Project:
        pass

    def deleteProject(self, projectId: UUID) -> bool:
        pass

    def assignProjectManager(self, projectId: UUID, userId: UUID) -> bool:
        pass

    def getAllProjects(self) -> List[Project]:
        pass

    def getProjectsByManager(self, managerId: UUID) -> List[Project]:
        pass