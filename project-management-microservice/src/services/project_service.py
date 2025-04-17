from typing import List
from uuid import UUID
from ..models.project import Project
from ..database.project_dal import ProjectDAL

class ProjectService:
    def __init__(self):
        self.project_dal = ProjectDAL()

    def createProject(self, project: Project) -> Project:
        """Create a new project."""
        self.project_dal.add_project(project.to_dict())
        return project

    def getProjectByName(self, projectName: str) -> Project:
        """Get a project by its name."""
        project_data = self.project_dal.get_project_by_name(projectName)
        if not project_data:
            raise ValueError(f"Project with name {projectName} not found.")
        return Project.from_dict(project_data)

    def getProject(self, projectId: UUID) -> Project:
        """Get a project by its ID."""
        project_data = self.project_dal.get_project(str(projectId))
        if not project_data:
            raise ValueError(f"Project with ID {projectId} not found.")
        return Project.from_dict(project_data)

    def updateProject(self, project: Project) -> Project:
        """Update an existing project."""
        existing_project = self.project_dal.get_project(project.id)
        if not existing_project:
            raise ValueError(f"Project with ID {project.id} not found.")
        self.project_dal.update_project(project.id, project.to_dict())
        return project

    def deleteProject(self, projectId: UUID) -> bool:
        """Delete a project by its ID."""
        existing_project = self.project_dal.get_project(str(projectId))
        if not existing_project:
            raise ValueError(f"Project with ID {projectId} not found.")
        self.project_dal.delete_project(str(projectId))
        return True

    def assignProjectManager(self, projectId: UUID, userId: UUID) -> bool:
        """Assign a project manager to a project."""
        project_data = self.project_dal.get_project(str(projectId))
        if not project_data:
            raise ValueError(f"Project with ID {projectId} not found.")
        project_data["project_manager_id"] = str(userId)
        self.project_dal.update_project(str(projectId), project_data)
        return True

    def getAllProjects(self) -> List[Project]:
        """Get all projects."""
        projects_data = self.project_dal.get_all_projects()
        return [Project.from_dict(project) for project in projects_data]

    def getProjectsByManager(self, managerId: UUID) -> List[Project]:
        """Get all projects managed by a specific manager."""
        all_projects = self.project_dal.get_all_projects()
        manager_projects = [
            Project.from_dict(project)
            for project in all_projects
            if project["project_manager_id"] == str(managerId)
        ]
        return manager_projects

    