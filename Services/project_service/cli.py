import click
from src.project_manager import ProjectManager

project_manager = ProjectManager()

@click.group()
def cli():
    """Project Management CLI - Manage your projects efficiently."""
    pass

@cli.command()
@click.argument('name')
@click.argument('description')
@click.option('--owner', required=True, help='Owner user ID')
def create(name, description, owner):
    """Create a new project."""
    result = project_manager.create_project(name, description, owner)
    click.echo(result)

@cli.command()
@click.option('--owner', help='Filter by owner/member ID')
@click.option('--status', type=click.Choice(['active', 'completed', 'archived']))
def list(owner, status):
    """List projects with optional filtering."""
    projects = project_manager.list_projects(owner, status)
    
    if not projects:
        click.echo("No projects found.")
        return
    
    click.echo(f"\nFound {len(projects)} projects:")
    click.echo("=" * 50)
    for i, project in enumerate(projects, 1):
        click.echo(f"{i}. {project}")
        click.echo(f"   Description: {project.description}")
        click.echo(f"   Members: {len(project.members)}, Tasks: {len(project.task_ids)}")
    click.echo("=" * 50)

@cli.command()
@click.argument('project_id')
@click.argument('user_id')
def add_member(project_id, user_id):
    """Add a member to a project."""
    result = project_manager.add_member(project_id, user_id)
    click.echo(result)

@cli.command()
@click.argument('project_id')
@click.argument('task_id')
def add_task(project_id, task_id):
    """Add a task to a project."""
    result = project_manager.add_task(project_id, task_id)
    click.echo(result)

@cli.command()
@click.argument('project_id')
@click.argument('status', type=click.Choice(['active', 'completed', 'archived']))
def update_status(project_id, status):
    """Update project status."""
    result = project_manager.update_status(project_id, status)
    click.echo(result)

if __name__ == '__main__':
    cli()