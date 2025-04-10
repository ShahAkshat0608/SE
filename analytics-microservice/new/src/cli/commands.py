"""Command-line interface for the analytics microservice."""

import argparse
from datetime import datetime
import json
import sys
import os
from typing import Dict, Any, Optional, List, Callable
import logging

from src.common.logging.logger import get_logger
from src.core.services.factory import ServiceFactory
from src.common.config.settings import get_settings

logger = get_logger(__name__)


class AnalyticsCLI:
    """Command-line interface for the analytics microservice."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.settings = get_settings()
        self.services = ServiceFactory.create_services_from_config()
        self.analytics_service = self.services.get('analytics_service')
        
        if not self.analytics_service:
            raise RuntimeError("Failed to initialize analytics service")
    
    def setup_parser(self) -> argparse.ArgumentParser:
        """Set up the argument parser.
        
        Returns:
            Configured argument parser
        """
        parser = argparse.ArgumentParser(
            description="Task Analytics Microservice CLI",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Create subparsers for different commands
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # Server command
        server_parser = subparsers.add_parser("server", help="Start the API server")
        server_parser.add_argument("--host", type=str, default=self.settings.API_HOST,
                                 help="Host address to bind")
        server_parser.add_argument("--port", type=int, default=self.settings.API_PORT,
                                 help="Port to bind")
        server_parser.add_argument("--debug", action="store_true", default=self.settings.API_DEBUG,
                                 help="Enable debug mode")
        
        # Report command
        report_parser = subparsers.add_parser("report", help="Generate analytics reports")
        report_parser.add_argument("--type", choices=[
                                "full", "completion", "pending", "productivity", 
                                "projects", "team"], default="full",
                                help="Type of report to generate")
        report_parser.add_argument("--days", type=int, default=self.settings.DEFAULT_TIME_PERIOD_DAYS,
                                 help="Time period in days")
        report_parser.add_argument("--json", action="store_true",
                                 help="Output in JSON format")
        report_parser.add_argument("--output", type=str,
                                 help="Output file path (defaults to stdout)")
        report_parser.add_argument("--debug", action="store_true",
                                 help="Print debug information")
        
        # Project command
        project_parser = subparsers.add_parser("project", help="Get project analytics")
        project_parser.add_argument("project_id", help="ID of the project to analyze")
        project_parser.add_argument("--json", action="store_true", help="Output in JSON format")
        
        # User command
        user_parser = subparsers.add_parser("user", help="Get user analytics")
        user_parser.add_argument("user_id", help="ID of the user to analyze")
        user_parser.add_argument("--days", type=int, default=self.settings.DEFAULT_TIME_PERIOD_DAYS,
                               help="Time period in days")
        user_parser.add_argument("--json", action="store_true", help="Output in JSON format")
        
        # Version command
        version_parser = subparsers.add_parser("version", help="Show version information")
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the given arguments.
        
        Args:
            args: Command-line arguments (uses sys.argv if None)
            
        Returns:
            Exit code (0 for success, non-zero for errors)
        """
        parser = self.setup_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return 0
            
        command_handlers = {
            "server": self.handle_server_command,
            "report": self.handle_report_command,
            "project": self.handle_project_command,
            "user": self.handle_user_command,
            "version": self.handle_version_command
        }
        
        handler = command_handlers.get(parsed_args.command)
        if not handler:
            logger.error(f"Unknown command: {parsed_args.command}")
            return 1
            
        try:
            return handler(parsed_args)
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            if parsed_args.command == "server" and hasattr(parsed_args, "debug") and parsed_args.debug:
                # In debug mode, re-raise the exception for better stack traces
                raise
            return 1
    
    def handle_server_command(self, args: argparse.Namespace) -> int:
        """Handle the 'server' command.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            Exit code
        """
        from src.main import run_server
        
        logger.info(f"Starting server on {args.host}:{args.port}")
        run_server(host=args.host, port=args.port, debug=args.debug)
        return 0
    
    def handle_report_command(self, args: argparse.Namespace) -> int:
        """Handle the 'report' command.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            Exit code
        """
        # Check data files before running
        if hasattr(args, "debug") and args.debug:
            self._check_data_files()
        
        report: Dict[str, Any] = {}
        
        if args.type == "full":
            report = self.analytics_service.get_complete_analytics_report()
        elif args.type == "completion":
            report = {"completion_rate": self.analytics_service.get_completion_rate(args.days)}
        elif args.type == "pending":
            report = {"pending_work": self.analytics_service.get_pending_work_analysis()}
        elif args.type == "productivity":
            report = {"productivity": self.analytics_service.get_productivity_metrics(args.days)}
        elif args.type == "team":
            team_data = self.analytics_service.get_team_workload()
            if hasattr(args, "debug") and args.debug:
                print(f"DEBUG - Team workload data: {json.dumps(team_data, indent=2)}")
            report = {"team_workload": team_data}
        elif args.type == "projects":
            report = {"projects": self.analytics_service.get_all_projects_progress()}
        
        # Format and output the report
        self._output_report(report, args.json, args.output)
        return 0
    
    def handle_project_command(self, args: argparse.Namespace) -> int:
        """Handle the 'project' command.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            Exit code
        """
        project_report = self.analytics_service.get_project_progress(args.project_id)
        
        if "error" in project_report:
            logger.error(f"Project error: {project_report['error']}")
            return 1
            
        # Format and output the report
        self._output_report({"project": project_report}, args.json, None)
        return 0
    
    def handle_user_command(self, args: argparse.Namespace) -> int:
        """Handle the 'user' command.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            Exit code
        """
        user_report = self.analytics_service.get_user_productivity(args.user_id, args.days)
        
        if "error" in user_report:
            logger.error(f"User error: {user_report['error']}")
            return 1
            
        # Format and output the report
        self._output_report({"user": user_report}, args.json, None)
        return 0
    
    def handle_version_command(self, _: argparse.Namespace) -> int:
        """Handle the 'version' command.
        
        Args:
            _: Parsed command-line arguments (unused)
            
        Returns:
            Exit code
        """
        print("Task Analytics Microservice v1.0.0")
        return 0
    
    def _output_report(self, report: Dict[str, Any], json_format: bool, output_file: Optional[str]) -> None:
        """Format and output a report.
        
        Args:
            report: The report data
            json_format: Whether to output in JSON format
            output_file: Path to output file (None for stdout)
        """
        if json_format:
            formatted_output = json.dumps(report, indent=2)
        else:
            formatted_output = self._format_report_text(report)
            
        if output_file:
            with open(output_file, 'w') as f:
                f.write(formatted_output)
            logger.info(f"Report written to {output_file}")
        else:
            print(formatted_output)
    
    def _format_report_text(self, report: Dict[str, Any]) -> str:
        """Format a report as human-readable text.
        
        Args:
            report: The report data
            
        Returns:
            Formatted report text
        """
        lines = ["===== TASK ANALYTICS REPORT =====\n"]
        
        # Format completion rate
        if "completion_rate" in report:
            cr = report["completion_rate"]
            lines.extend([
                "COMPLETION RATE:",
                f"  Time Period: {cr.get('time_period_days', 30)} days",
                f"  Total Tasks: {cr.get('total_tasks', 0)}",
                f"  Completed Tasks: {cr.get('completed_tasks', 0)}",
                f"  Completion Rate: {cr.get('completion_rate_percentage', 0.0)}%",
                ""
            ])
        
        # Format pending work
        if "pending_work" in report:
            pw = report["pending_work"]
            lines.extend([
                "PENDING WORK:",
                f"  Total Pending: {pw.get('total_pending', 0)}",
                f"  By Priority: {', '.join(f'{k}: {v}' for k, v in pw.get('by_priority', {}).items())}",
                f"  Overdue Tasks: {pw.get('overdue_tasks', 0)} ({pw.get('overdue_percentage', 0.0)}%)",
                f"  Average Days Pending: {pw.get('average_days_pending', 0.0)}",
                ""
            ])
        
        # Format productivity
        if "productivity" in report:
            prod = report["productivity"]
            lines.extend([
                "PRODUCTIVITY:",
                f"  Tasks Completed: {prod.get('tasks_completed', 0)}",
                f"  Average Completion Time: {prod.get('avg_completion_time_hours', 0.0)} hours",
                f"  Average Daily Completion: {prod.get('average_daily_completion', 0.0)} tasks/day",
                f"  Time Period: {prod.get('time_period_days', 30)} days",
                ""
            ])
            
            # Add daily completion breakdown if available
            if prod.get('daily_completion'):
                lines.append("  DAILY COMPLETION:")
                for date, count in prod.get('daily_completion', {}).items():
                    lines.append(f"    {date}: {count} task(s)")
                lines.append("")
                
            # Add weekly trends if available
            if prod.get('weekly_trends'):
                lines.append("  WEEKLY TRENDS:")
                for week, count in prod.get('weekly_trends', {}).items():
                    lines.append(f"    {week}: {count} task(s)")
                lines.append("")
        
        # Format project
        if "project" in report:
            proj = report["project"]
            lines.extend([
                f"PROJECT: {proj.get('project_name', 'Unknown')}",
                f"  Progress: {proj.get('completion_percentage', 0.0)}% complete",
                f"  Tasks: {proj.get('completed_tasks', 0)}/{proj.get('total_tasks', 0)}",
                f"  Days Remaining: {proj.get('days_remaining', 0)}",
                f"  On Track: {'Yes' if proj.get('on_track', False) else 'No'}",
                ""
            ])
        
        # Format user
        if "user" in report:
            user = report["user"]
            lines.extend([
                f"USER: {user.get('user_name', 'Unknown')} ({user.get('user_role', 'Unknown')})",
                f"  Tasks Completed: {user.get('tasks_completed', 0)}",
                f"  Average Completion Time: {user.get('avg_completion_time_hours', 0.0)} hours",
                ""
            ])
        
        # Format team workload
        if "team_workload" in report:
            tw = report["team_workload"]
            
            # Check for error
            if "error" in tw:
                lines.extend([
                    "TEAM WORKLOAD ERROR:",
                    f"  {tw.get('error', 'Unknown error')}",
                    ""
                ])
            else:
                lines.extend([
                    "TEAM WORKLOAD:",
                    f"  Total Users: {tw.get('total_users', 0)}",
                    f"  Total Tasks: {tw.get('total_tasks', 0)}",
                    f"  Pending Tasks: {tw.get('total_pending_tasks', 0)}",
                    ""
                ])
                
                # Add user metrics details
                if 'user_metrics' in tw and tw['user_metrics']:
                    lines.append("  USER WORKLOAD DETAILS:")
                    for user_id, metrics in tw['user_metrics'].items():
                        lines.append(f"    {metrics.get('name', 'Unknown')} ({user_id}):")
                        lines.append(f"      Pending Tasks: {metrics.get('pending_tasks', 0)}")
                        lines.append(f"      Workload: {metrics.get('workload_percentage', 0)}%")
                        lines.append(f"      Completion Rate: {metrics.get('completion_rate', 0)}%")
                        lines.append("")
                
                # Add overloaded user
                if tw.get('most_overloaded_user') and tw.get('most_overloaded_user') in tw.get('user_metrics', {}):
                    overloaded = tw['most_overloaded_user']
                    user_data = tw['user_metrics'].get(overloaded, {})
                    lines.append(f"  Most Overloaded: {user_data.get('name', overloaded)} ({user_data.get('workload_percentage', 0)}%)")
                
                # Add least loaded user
                if tw.get('least_loaded_user') and tw.get('least_loaded_user') in tw.get('user_metrics', {}):
                    least_loaded = tw['least_loaded_user']
                    user_data = tw['user_metrics'].get(least_loaded, {})
                    lines.append(f"  Least Loaded: {user_data.get('name', least_loaded)} ({user_data.get('workload_percentage', 0)}%)")
                
                lines.append("")
        
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"Generated at: {generated_at}")
        return "\n".join(lines)
    
    def _check_data_files(self) -> None:
        """Check if data files exist and have content."""
        settings = get_settings()
        file_paths = [
            ("Tasks", settings.TASKS_FILE),
            ("Projects", settings.PROJECTS_FILE),
            ("Users", settings.USERS_FILE)
        ]
        
        print("Checking data files:")
        for name, path in file_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        count = len(data) if isinstance(data, dict) else 0
                        print(f"  ✓ {name} file: {path} (contains {count} items)")
                except json.JSONDecodeError:
                    print(f"  ✗ {name} file: {path} (INVALID JSON FORMAT)")
                except Exception as e:
                    print(f"  ✗ {name} file: {path} (ERROR: {str(e)})")
            else:
                print(f"  ✗ {name} file: {path} (FILE NOT FOUND)")
        print("")


def main() -> int:
    """Entry point for the CLI.
    
    Returns:
        Exit code
    """
    cli = AnalyticsCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())