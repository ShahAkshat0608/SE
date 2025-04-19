#!/usr/bin/env python
import requests
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Notification service URL
NOTIFICATION_SERVICE_URL = "http://localhost:8004"

def check_notification_database():
    """Check the notification database for pending emails."""
    try:
        # Create a simple GET request to a health endpoint to check if service is running
        health_url = f"{NOTIFICATION_SERVICE_URL}/"
        logger.info(f"Testing connection to notification service: {health_url}")
        
        response = requests.get(health_url, timeout=5)
        logger.info(f"Health check response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error("Health check failed!")
            return False
            
        # Try to process the email queue
        process_url = f"{NOTIFICATION_SERVICE_URL}/notifications/email/process"
        logger.info(f"Processing email queue: {process_url}")
        
        response = requests.post(process_url, timeout=10)
        logger.info(f"Process response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Process result: {result}")
            return True
        else:
            logger.error(f"Failed to process queue: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return False

def test_send_direct_email():
    """Test sending an email directly through the notification service."""
    email_endpoint = f"{NOTIFICATION_SERVICE_URL}/notifications/email"
    
    payload = {
        "user_id": 9999,
        "email": "test.direct@gmail.com",
        "subject": "Notification Queue Test",
        "body": "This is a test email sent directly to the notification service."
    }
    
    try:
        logger.info(f"Sending direct email to {email_endpoint}")
        response = requests.post(email_endpoint, json=payload, timeout=10)
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 201:
            notification_data = response.json()
            logger.info(f"Email notification created: {notification_data}")
            
            # Return the notification ID for reference
            return notification_data.get("id")
        else:
            logger.error(f"Failed to create email notification: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None

if __name__ == "__main__":
    logger.info("Starting notification queue check...")
    
    # First, test sending an email directly
    notification_id = test_send_direct_email()
    
    if notification_id:
        logger.info(f"Test email added to queue with ID: {notification_id}")
        
        # Wait a bit before processing the queue
        logger.info("Waiting 3 seconds before processing queue...")
        time.sleep(3)
        
        # Process the queue
        if check_notification_database():
            logger.info("Queue processing completed.")
        else:
            logger.error("Queue processing failed.")
    else:
        logger.error("Failed to add test email to queue.") 