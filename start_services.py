#!/usr/bin/env python
import subprocess
import time
import os
import signal
import sys
import argparse
from pathlib import Path

# Default ports
USER_MANAGEMENT_PORT = 8001
PROJECT_MANAGEMENT_PORT = 8002
ANALYTICS_PORT = 8003
NOTIFICATION_PORT = 8004

def start_service(command, service_name, log_file):
    """Start a microservice and redirect output to a log file"""
    print(f"Starting {service_name}...")
    with open(log_file, 'w') as f:
        return subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT, shell=True)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Start all microservices for Task Manager')
    parser.add_argument('--logs-dir', default='logs', help='Directory to store log files')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload (for production)')
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(exist_ok=True)
    
    # Determine reload flag
    reload_flag = "" if args.no_reload else "--reload"
    
    # Start all services
    processes = []
    
    try:
        # User Management Service
        user_cmd = f"uvicorn user-management.src.main.main:app {reload_flag} --port {USER_MANAGEMENT_PORT}"
        user_process = start_service(user_cmd, "User Management Service", logs_dir / "user_service.log")
        processes.append((user_process, "User Management"))
        
        # Project Management Service
        project_cmd = f"uvicorn project-management-microservice.src.main:app {reload_flag} --port {PROJECT_MANAGEMENT_PORT}"
        project_process = start_service(project_cmd, "Project Management Service", logs_dir / "project_service.log")
        processes.append((project_process, "Project Management"))
        
        # Analytics Service
        analytics_cmd = f"uvicorn analytics-microservice.src.main.main:app {reload_flag} --port {ANALYTICS_PORT}"
        analytics_process = start_service(analytics_cmd, "Analytics Service", logs_dir / "analytics_service.log")
        processes.append((analytics_process, "Analytics"))
        
        # Notification Service
        notification_cmd = f"python notification-microservice/run.py"
        notification_process = start_service(notification_cmd, "Notification Service", logs_dir / "notification_service.log")
        processes.append((notification_process, "Notification"))
        
        print("\nAll services started successfully!")
        print(f"User Management:    http://localhost:{USER_MANAGEMENT_PORT}/docs")
        print(f"Project Management: http://localhost:{PROJECT_MANAGEMENT_PORT}/docs")
        print(f"Analytics:          http://localhost:{ANALYTICS_PORT}/docs")
        print(f"Notification:       http://localhost:{NOTIFICATION_PORT}/docs")
        print("\nLogs are being saved to the 'logs' directory.")
        print("Press Ctrl+C to stop all services.\n")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for process, name in processes:
            print(f"Stopping {name} Service...")
            process.terminate()
            process.wait(timeout=5)
        print("All services stopped.")
    
    except Exception as e:
        print(f"Error: {e}")
        for process, name in processes:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main() 