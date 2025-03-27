import click
import os
from datetime import datetime
from task_manager import TaskManager

# Create a single instance of TaskManager
task_manager = TaskManager()

@click.group()
def cli():
    """Task Manager CLI - Manage your tasks efficiently from the command line."""
    pass

@cli.command()
@click.argument('description')
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high"]), default="medium", help="Task priority level")
@click.option("--due", "-d", type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%d %H:%M"]), help="Due date (YYYY-MM-DD)")
def add(description, priority, due):
    """Add a new task with description, priority and due date."""
    result = task_manager.add_task(description, priority, due)
    click.echo(result)

@cli.command()
@click.option("--all", "-a", is_flag=True, help="Show all tasks including completed ones")
@click.option("--completed", "-c", is_flag=True, help="Show only completed tasks")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high"]), help="Filter by priority")
def list(all, completed, priority):
    """List tasks with optional filtering."""
    filter_completed = None
    if not all:
        filter_completed = True if completed else False
    
    tasks = task_manager.get_tasks(filter_completed, priority)
    
    if not tasks:
        click.echo("No tasks found.")
        return
    
    click.echo(f"\nFound {len(tasks)} tasks:")
    click.echo("=" * 50)
    for i, task in enumerate(tasks, 1):
        click.echo(f"{i}. {task}")
    click.echo("=" * 50)

@cli.command()
@click.argument('task_id')
def complete(task_id):
    """Mark a task as completed."""
    result = task_manager.complete_task(task_id)
    click.echo(result)

@cli.command()
@click.argument('task_id')
def uncomplete(task_id):
    """Mark a task as not completed."""
    result = task_manager.uncomplete_task(task_id)
    click.echo(result)

@cli.command()
@click.argument('task_id')
def remove(task_id):
    """Remove a task by its ID."""
    result = task_manager.remove_task(task_id)
    click.echo(result)

@cli.command()
@click.argument('task_id')
@click.option('--description', '-d', help="New task description")
@click.option('--priority', '-p', type=click.Choice(["low", "medium", "high"]), help="New priority")
@click.option('--due', type=click.DateTime(formats=["%Y-%m-%d", "%Y-%m-%d %H:%M"]), help="New due date (YYYY-MM-DD)")
@click.option('--clear-due', is_flag=True, help="Clear the due date")
def update(task_id, description, priority, due, clear_due):
    """Update task details."""
    if clear_due:
        due = None
    elif due is None:
        # Keep the existing due date if not specified
        pass
        
    result = task_manager.update_task(task_id, description, priority, due)
    click.echo(result)

@cli.command()
@click.argument('task_id')
def show(task_id):
    """Show details of a specific task."""
    task = task_manager.get_task(task_id)
    if task:
        click.echo(f"\nTask Details:")
        click.echo("=" * 50)
        click.echo(f"ID: {task.id}")
        click.echo(f"Description: {task.description}")
        click.echo(f"Priority: {task.priority}")
        click.echo(f"Status: {'Completed' if task.completed else 'Pending'}")
        if task.due_date:
            click.echo(f"Due date: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
        click.echo(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        click.echo("=" * 50)
    else:
        click.echo(f"Error: Task with ID '{task_id}' not found")

if __name__ == '__main__':
    # Ensure the tasks directory exists
    cli()
