"""Entry point for the analytics microservice."""

import argparse
import json

from api import create_api
from analytics import TaskAnalytics
from repository import TaskRepository
import config


def print_report(report, format_json=False):
    """Print the analytics report to the console.
    
    Args:
        report: The report data
        format_json: Whether to format as JSON
    """
    if format_json:
        print(json.dumps(report, indent=2))
        return
    
    # Print a more human-readable format
    print("\n===== ANALYTICS REPORT =====\n")
    
    # Print completion rate
    cr = report["completion_rate"]
    print(f"COMPLETION RATE (Last {cr['time_period_days']} days)")
    print(f"  Total Tasks: {cr['total_tasks']}")
    print(f"  Completed: {cr['completed_tasks']} ({cr['completion_rate_percentage']}%)")
    print(f"  Pending: {cr['pending_tasks']}")
    print()
    
    # Print pending work
    pw = report["pending_work"]
    print("PENDING WORK")
    print(f"  Total Pending: {pw['total_pending']}")
    print(f"  By Priority: {json.dumps(pw['by_priority'])}")
    print(f"  Overdue Tasks: {pw['overdue_tasks']} ({pw['overdue_percentage']}%)")
    print(f"  Average Days Pending: {pw['average_days_pending']}")
    print()
    
    # Print productivity
    prod = report["productivity"]
    print(f"PRODUCTIVITY (Last {prod['time_period_days']} days)")
    print(f"  Tasks Completed: {prod['tasks_completed']}")
    print(f"  Avg Completion Time: {prod['avg_completion_time_hours']} hours")
    print(f"  Avg Daily Completion: {prod['average_daily_completion']} tasks/day")
    print("\n============================\n")


def main():
    """Main entry point for the CLI and API server."""
    parser = argparse.ArgumentParser(description="Task Analytics Microservice")
    parser.add_argument("--server", action="store_true", help="Run as API server")
    parser.add_argument("--report", action="store_true", help="Generate and print analytics report")
    parser.add_argument("--json", action="store_true", help="Format output as JSON")
    parser.add_argument("--tasks-file", help="Path to the tasks JSON file")
    args = parser.parse_args()
    
    # Create services
    repo = TaskRepository(args.tasks_file if args.tasks_file else config.TASKS_FILE)
    analytics = TaskAnalytics(repo)
    
    # Run as server or CLI tool
    if args.server:
        app = create_api(analytics)
        app.run(host=config.API_HOST, port=config.API_PORT, debug=config.API_DEBUG)
    elif args.report:
        report = analytics.get_complete_analytics_report()
        print_report(report, args.json)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()