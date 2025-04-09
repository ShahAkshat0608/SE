from datetime import datetime
from .storage.project_storage import ProjectStorage
from .models.project import Project

class ProjectManager:
    def __init__(self, storage_path="projects.json"):
        self.storage = ProjectStorage(storage_path)
    
    def create_project(self, name, description, owner_id):
        project = Project(name, description, owner_id)
        self.storage.add_project(project)
        return f"Project created: {project}"
    
    def list_projects(self, owner_id=None, status=None):
        projects = self.storage.get_all_projects()
        
        if owner_id:
            projects = [p for p in projects if p.owner_id == owner_id or owner_id in p.members]
        if status:
            projects = [p for p in projects if p.status == status]
            
        return sorted(projects, key=lambda p: p.created_at, reverse=True)
    
    def add_member(self, project_id, user_id):
        project = self.storage.get_project(project_id)
        if not project:
            return f"Error: Project with ID '{project_id}' not found"
        
        if user_id not in project.members:
            project.members.append(user_id)
            project.updated_at = datetime.now()
            self.storage.update_project(project)
            return f"Member added to project: {project}"
        return f"User is already a member of the project"
    
    def add_task(self, project_id, task_id):
        project = self.storage.get_project(project_id)
        if not project:
            return f"Error: Project with ID '{project_id}' not found"
        
        if task_id not in project.task_ids:
            project.task_ids.append(task_id)
            project.updated_at = datetime.now()
            self.storage.update_project(project)
            return f"Task added to project: {project}"
        return f"Task is already in the project"
    
    def update_status(self, project_id, status):
        project = self.storage.get_project(project_id)
        if not project:
            return f"Error: Project with ID '{project_id}' not found"
        
        project.status = status
        project.updated_at = datetime.now()
        self.storage.update_project(project)
        return f"Project status updated: {project}"