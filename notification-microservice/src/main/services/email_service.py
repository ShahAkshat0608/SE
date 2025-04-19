import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..models.notification_model import (
    get_pending_email_notifications,
    update_email_notification_status
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def send_email(to_email, subject, body):
    """Send an email using Gmail SMTP."""
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        logging.error("Email credentials not set in environment variables")
        return False

    # Log credentials availability (without revealing actual values)
    logging.info(f"Attempting to send email from {EMAIL_USERNAME} to {to_email}")
    logging.info(f"Email credentials present: Username={bool(EMAIL_USERNAME)}, Password={bool(EMAIL_PASSWORD)}")

    message = MIMEMultipart()
    message["From"] = EMAIL_USERNAME  # Simple email address format that works consistently
    message["To"] = to_email
    message["Subject"] = subject
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Debug logging
        logging.info(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}")
        
        # Create a secure connection with the server using SSL
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        
        # Login to email account
        logging.info("Attempting to login to email server...")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        logging.info("Login successful")
        
        # Send email
        logging.info("Sending email message...")
        server.send_message(message)
        logging.info("Email message sent")
        
        # Terminate the session
        server.quit()
        logging.info("SMTP connection closed")
        
        logging.info(f"Email sent successfully to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication Error: {e}")
        logging.error("This usually means incorrect username/password or Google security settings blocking the login.")
        logging.error("Check if 'Less secure app access' is enabled or use an App Password.")
        return False
    except smtplib.SMTPException as e:
        logging.error(f"SMTP Error: {e}")
        return False
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
        logging.error(f"Exception type: {type(e).__name__}")
        return False

def process_pending_notifications(batch_size=10):
    """Process a batch of pending email notifications."""
    notifications = get_pending_email_notifications(limit=batch_size)
    results = {
        "success": 0,
        "failure": 0,
        "total": len(notifications)
    }
    
    for notification in notifications:
        success = send_email(
            to_email=notification["email"],
            subject=notification["subject"],
            body=notification["body"]
        )
        
        if success:
            update_email_notification_status(notification["id"], "sent")
            results["success"] += 1
        else:
            update_email_notification_status(notification["id"], "failed")
            results["failure"] += 1
    
    logging.info(f"Processed {results['total']} notifications: {results['success']} successful, {results['failure']} failed")
    return results

def send_notification_to_user(user_id, email, subject, body):
    """Create and send an email notification to a user."""
    from ..models.notification_model import create_email_notification
    
    # First create the notification record
    notification = create_email_notification(user_id, email, subject, body)
    
    if not notification:
        logging.error(f"Failed to create notification record for user {user_id}")
        return None
    
    # Attempt to send immediately
    success = send_email(email, subject, body)
    
    # Update the status based on the send result
    if success:
        update_email_notification_status(notification["id"], "sent")
        logging.info(f"Email notification {notification['id']} sent successfully")
    else:
        update_email_notification_status(notification["id"], "pending")
        logging.warning(f"Email notification {notification['id']} queued for later delivery")
    
    return notification 