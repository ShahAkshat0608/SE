#!/bin/bash

# Create logs directory
mkdir -p logs

# Start User Management Service
echo "Starting User Management Service..."
uvicorn user-management.src.main.main:app --reload --port 8001 > logs/user_service.log 2>&1 &
USER_PID=$!

# Start Project Management Service
echo "Starting Project Management Service..."
uvicorn project-management-microservice.src.main:app --reload --port 8002 > logs/project_service.log 2>&1 &
PROJECT_PID=$!

# Start Analytics Service
echo "Starting Analytics Service..."
uvicorn analytics-microservice.src.main.main:app --reload --port 8003 > logs/analytics_service.log 2>&1 &
ANALYTICS_PID=$!

# Start Notification Service
echo "Starting Notification Service..."
python notification-microservice/run.py > logs/notification_service.log 2>&1 &
NOTIFICATION_PID=$!

# Create a PID file to track the service PIDs
echo "$USER_PID $PROJECT_PID $ANALYTICS_PID $NOTIFICATION_PID" > .service_pids

echo ""
echo "All services started successfully!"
echo "User Management:    http://localhost:8001/docs"
echo "Project Management: http://localhost:8002/docs"
echo "Analytics:          http://localhost:8003/docs"
echo "Notification:       http://localhost:8004/docs"
echo ""
echo "Logs are being saved to the 'logs' directory."
echo "To stop all services, run: ./stop_services.sh"
echo "" 