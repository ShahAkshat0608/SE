import requests
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
NOTIFICATION_SERVICE_URL = os.environ.get("NOTIFICATION_SERVICE_URL", "http://localhost:8004")

def send_welcome_email(user_id, email, name):
    """Send a welcome email to a newly registered user."""
    endpoint = f"{NOTIFICATION_SERVICE_URL}/notifications/email"
    
    logging.info(f"Preparing welcome email for user {user_id} ({email})")
    logging.info(f"Using notification service endpoint: {endpoint}")
    
    subject = "Welcome to our Task Management System!"
    body = f"""
    Hello {name},
    
    Welcome to our Task Management System! We're excited to have you on board.
    
    Your account has been created successfully with email: {email}.
    
    You can now start creating and managing your tasks efficiently.
    
    Best regards,
    The Task Management Team
    """
    
    # Include all required fields for the EmailNotificationCreate model
    payload = {
        "user_id": user_id,
        "email": email,
        "subject": subject,
        "body": body
    }
    
    try:
        logging.info(f"Sending welcome email to {email} via {endpoint}")
        response = requests.post(endpoint, json=payload)
        # The API returns 201 Created status
        if response.status_code == 201:
            logging.info(f"Welcome email sent to user {user_id} ({email})")
            return response.json()
        else:
            logging.error(f"Failed to send welcome email to {email}: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error connecting to notification service: {e}")
        return None

def create_calendar_event(user_id, email, event_data):
    """Create a calendar event for a user."""
    endpoint = f"{NOTIFICATION_SERVICE_URL}/notifications/calendar"
    
    # Ensure start_time and end_time are datetime objects
    if isinstance(event_data.get('start_time'), str):
        event_data['start_time'] = datetime.fromisoformat(event_data['start_time'])
    
    if isinstance(event_data.get('end_time'), str):
        event_data['end_time'] = datetime.fromisoformat(event_data['end_time'])
    
    payload = {
        "user_id": user_id,
        "email": email,
        "summary": event_data.get("summary", "New Task"),
        "description": event_data.get("description", ""),
        "start_time": event_data["start_time"].isoformat(),
        "end_time": event_data["end_time"].isoformat()
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        if response.status_code == 201:
            logging.info(f"Calendar event created for user {user_id} ({email})")
            return response.json()
        else:
            logging.error(f"Failed to create calendar event for {email}: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        logging.error(f"Error connecting to notification service: {e}")
        return None 