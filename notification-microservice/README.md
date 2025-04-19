# Notification Microservice

This microservice provides email notification and Google Calendar integration services for the Task Management System.

## Features

- Send email notifications to users (via Gmail SMTP)
- Create and manage Google Calendar events
- Queue failed operations for later retry
- RESTful API for integration with other services

## Requirements

- Python 3.8+
- Gmail account with app password set up (for email notifications)
- Google Calendar API credentials (for calendar integration)

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Google API libraries:
   ```
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

## Configuration

Set the following environment variables:

### Email Service
- `EMAIL_USERNAME`: Your Gmail address
- `EMAIL_PASSWORD`: Your Gmail app password (not your regular account password)

### Gmail App Password Setup

To use Gmail for sending emails, you need to create an app password:

1. Go to your Google Account settings: https://myaccount.google.com/
2. Select "Security" from the menu
3. Under "Signing in to Google", select "2-Step Verification" (enable it if not already enabled)
4. Scroll down and select "App passwords"
5. Generate a new app password for "Mail" and "Other" (custom name: "Task Manager")
6. Use the generated password as your `EMAIL_PASSWORD` environment variable

### Google Calendar Integration
- `GOOGLE_CREDENTIALS_FILE`: Path to your Google API credentials JSON file (default: `credentials.json`)
- `GOOGLE_TOKEN_FILE`: Path to store the OAuth token (default: `token.json`)

### Service Configuration
- `PORT`: Port for the service to run on (default: 8002)
- `LOG_LEVEL`: Logging level (default: INFO)

## Google Calendar API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON file and save it as `credentials.json` in the root directory

## Usage

### Option 1: Full Microservice

Start the complete microservice (with database & Google Calendar integration):

```
cd notification-microservice
python -m src.main.main
```

### Option 2: Simplified Standalone Mode

For quick testing of only the email functionality, use the standalone mode:

```
cd notification-microservice/src/main
python standalone.py
```

The service will be available at http://localhost:8002

## Setting Environment Variables

### Windows PowerShell
```powershell
$env:EMAIL_USERNAME = "your.email@gmail.com"
$env:EMAIL_PASSWORD = "your-app-password"
```

### Bash/Linux
```bash
export EMAIL_USERNAME="your.email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

## API Endpoints

### Email Notifications

#### Full Microservice
- `POST /notifications/email`: Create and send an email notification
  ```json
  {
    "user_id": 1,
    "email": "user@gmail.com",
    "subject": "Notification Subject",
    "body": "Notification body text"
  }
  ```

- `POST /notifications/email/process`: Process pending email notifications queue

#### Standalone Mode
- `POST /notifications/email`: Send an email notification
  ```
  ?to_email=user@gmail.com&subject=Test%20Subject&body=Test%20email%20body
  ```

### Calendar Events (Full Microservice Only)

- `POST /notifications/calendar`: Create a calendar event
  ```json
  {
    "user_id": 1,
    "email": "user@gmail.com",
    "summary": "Meeting",
    "description": "Project status meeting",
    "start_time": "2023-11-10T14:00:00",
    "end_time": "2023-11-10T15:00:00"
  }
  ```

- `POST /notifications/calendar/process`: Process pending calendar events queue

## Health Check

- `GET /health`: Service health status and configuration information 

## Troubleshooting

If you encounter issues with Gmail authentication:

1. Make sure you're using an app password, not your regular account password
2. Verify that your Gmail account has 2-step verification enabled
3. Check the logs for detailed error messages
4. Try sending to your own email address first for testing 