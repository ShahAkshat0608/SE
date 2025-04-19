import requests
import logging
import os
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get notification service URL from environment variable or use default
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:5002")

class NotificationClient:
    """Client for interacting with the Notification Microservice"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url or NOTIFICATION_SERVICE_URL
        logger.info(f"Initializing NotificationClient with base URL: {self.base_url}")
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Helper method to make HTTP requests to the notification service"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return None
    
    def send_email(self, to_email: str, subject: str, body: str, user_id: Optional[str] = None) -> bool:
        """Send an email notification"""
        data = {
            "email": to_email,
            "subject": subject,
            "body": body
        }
        
        if user_id:
            data["user_id"] = user_id
            
        result = self._make_request("POST", "api/notifications/email", data=data)
        return result is not None and result.get("success", False)
    
    def send_emails_to_users(self, user_emails: List[Dict[str, str]], subject: str, body: str) -> Dict[str, int]:
        """
        Send emails to multiple users
        
        Args:
            user_emails: List of dicts containing user_id and email
            subject: Email subject
            body: Email body text
            
        Returns:
            Dict with success and failure counts
        """
        success_count = 0
        failure_count = 0
        
        for user in user_emails:
            if "email" not in user:
                failure_count += 1
                continue
                
            result = self.send_email(
                to_email=user["email"],
                subject=subject,
                body=body,
                user_id=user.get("user_id")
            )
            
            if result:
                success_count += 1
            else:
                failure_count += 1
        
        return {
            "success": success_count,
            "failure": failure_count,
            "total": success_count + failure_count
        } 