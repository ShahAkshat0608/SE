import os
import logging
from datetime import datetime, timezone
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..models.notification_model import (
    get_pending_calendar_events,
    update_calendar_event_status
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Google Calendar API configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = os.environ.get('GOOGLE_TOKEN_FILE', 'token.json')

def get_calendar_service():
    """Build and return a Google Calendar API service."""
    creds = None
    
    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token:
            creds_data = json.load(token)
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    
    # If no valid credentials available, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.error(f"Error refreshing credentials: {e}")
                return None
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                logging.error(f"Credentials file not found: {CREDENTIALS_FILE}")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building calendar service: {e}")
        return None

def create_calendar_event_in_google(email, summary, description, start_time, end_time):
    """Create an event in Google Calendar."""
    service = get_calendar_service()
    if not service:
        logging.error("Failed to get calendar service")
        return None
    
    # Format event times according to RFC3339
    start_datetime = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_datetime = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': email}
        ],
        'reminders': {
            'useDefault': True
        }
    }
    
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        logging.info(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as error:
        logging.error(f"Error creating calendar event: {error}")
        return None

def process_pending_calendar_events(batch_size=10):
    """Process a batch of pending calendar events."""
    events = get_pending_calendar_events(limit=batch_size)
    results = {
        "success": 0,
        "failure": 0,
        "total": len(events)
    }
    
    for event in events:
        # Convert string timestamps to datetime objects
        start_time = datetime.fromisoformat(event["start_time"])
        end_time = datetime.fromisoformat(event["end_time"])
        
        google_event = create_calendar_event_in_google(
            email=event["email"],
            summary=event["summary"],
            description=event["description"] or "",
            start_time=start_time,
            end_time=end_time
        )
        
        if google_event:
            update_calendar_event_status(
                event["id"], 
                "created", 
                google_event.get('id')
            )
            results["success"] += 1
        else:
            update_calendar_event_status(event["id"], "failed")
            results["failure"] += 1
    
    logging.info(f"Processed {results['total']} calendar events: {results['success']} successful, {results['failure']} failed")
    return results

def schedule_calendar_event(user_id, email, summary, description, start_time, end_time):
    """Create and schedule a calendar event."""
    from ..models.notification_model import create_calendar_event
    
    # First create the event record
    event = create_calendar_event(
        user_id=user_id,
        email=email,
        summary=summary,
        description=description,
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat()
    )
    
    if not event:
        logging.error(f"Failed to create calendar event record for user {user_id}")
        return None
    
    # Attempt to create it in Google Calendar immediately
    google_event = create_calendar_event_in_google(
        email=email,
        summary=summary,
        description=description or "",
        start_time=start_time,
        end_time=end_time
    )
    
    # Update the status based on the result
    if google_event:
        update_calendar_event_status(
            event["id"], 
            "created", 
            google_event.get('id')
        )
        logging.info(f"Calendar event {event['id']} created successfully in Google Calendar")
    else:
        update_calendar_event_status(event["id"], "pending")
        logging.warning(f"Calendar event {event['id']} queued for later creation")
    
    return event 