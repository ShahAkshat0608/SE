#!/usr/bin/env python
import requests
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration - same as in notification_client.py
NOTIFICATION_SERVICE_URL = "http://localhost:8004"

def test_notification_connectivity():
    """Test if we can reach the notification service."""
    try:
        # First try a basic health check
        health_url = f"{NOTIFICATION_SERVICE_URL}/docs"
        logger.info(f"Testing connection to notification service docs: {health_url}")
        
        response = requests.get(health_url, timeout=5)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("Successfully connected to notification service docs!")
        else:
            logger.error(f"Failed to connect to notification service docs: {response.status_code}")
            return False

        # Now test if the email endpoint can be reached
        email_endpoint = f"{NOTIFICATION_SERVICE_URL}/notifications/email"
        logger.info(f"Testing if email endpoint exists: {email_endpoint}")
        
        # Just sending an OPTIONS request to check if endpoint exists without actually sending an email
        response = requests.options(email_endpoint, timeout=5)
        logger.info(f"Response status for OPTIONS request: {response.status_code}")
        
        if response.status_code < 500:  # Any non-server error is acceptable for OPTIONS
            logger.info("Email endpoint appears to be accessible")
            return True
        else:
            logger.error(f"Email endpoint might not be accessible: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error: {e}")
        return False

def test_send_email():
    """Attempt to send a test email through the notification service."""
    email_endpoint = f"{NOTIFICATION_SERVICE_URL}/notifications/email"
    logger.info(f"Testing sending email through: {email_endpoint}")
    
    # Create test payload
    payload = {
        "user_id": 9999,  # Test user ID
        "email": "test@example.com",
        "subject": "Test Email",
        "body": "This is a test email to verify the notification service is working."
    }
    
    try:
        response = requests.post(email_endpoint, json=payload, timeout=10)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 201:
            logger.info("Successfully submitted email notification!")
            logger.info(f"Response data: {response.json()}")
            return True
        else:
            logger.error(f"Failed to send test email: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while sending test email: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting notification service connectivity test...")
    
    if test_notification_connectivity():
        logger.info("Connectivity test successful!")
        
        # Try to send a test email
        if test_send_email():
            logger.info("Email test successful! Notification service appears to be working properly.")
            sys.exit(0)
        else:
            logger.error("Email test failed! Notification service endpoint exists but cannot process emails.")
            sys.exit(1)
    else:
        logger.error("Connectivity test failed! Cannot reach notification service.")
        sys.exit(1) 