#!/bin/bash

# Check if PID file exists
if [ ! -f .service_pids ]; then
    echo "No running services found."
    exit 0
fi

# Read PIDs from the file
read -r USER_PID PROJECT_PID ANALYTICS_PID NOTIFICATION_PID < .service_pids

# Function to stop a service
stop_service() {
    local pid=$1
    local name=$2
    
    if ps -p "$pid" > /dev/null; then
        echo "Stopping $name Service (PID: $pid)..."
        kill "$pid" 2>/dev/null
        sleep 1
        if ps -p "$pid" > /dev/null; then
            echo "$name Service still running, sending SIGKILL..."
            kill -9 "$pid" 2>/dev/null
        fi
    else
        echo "$name Service was not running (PID: $pid)."
    fi
}

# Stop all services
stop_service "$USER_PID" "User Management"
stop_service "$PROJECT_PID" "Project Management"
stop_service "$ANALYTICS_PID" "Analytics"
stop_service "$NOTIFICATION_PID" "Notification"

# Remove the PID file
rm -f .service_pids

echo "All services stopped." 