#!/usr/bin/env python
import unittest
import requests
import os
import sys
import time
import json
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

# Configuration
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:8001")
NOTIFICATION_SERVICE_URL = os.environ.get("NOTIFICATION_SERVICE_URL", "http://127.0.0.1:8004")
API_PREFIX = "/api/v1"

class TestNotificationService(unittest.TestCase):
    """Tests for the Notification Service."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test data."""
        # Create test user for notifications
        cls.test_user = {
            "name": "Notification Test User",
            "email": f"notification.test.{int(time.time())}@example.com",
            "password": "securePassword123!",
            "contact": "1234567890"
        }
        cls.user_id = None
        
        # Try to register test user
        try:
            # Register user
            register_url = f"{USER_SERVICE_URL}{API_PREFIX}/auth/register"
            register_response = requests.post(register_url, json=cls.test_user)
            
            if register_response.status_code == 201:
                user_data = register_response.json()
                cls.user_id = user_data.get("id")
                print(f"Test user created. User ID: {cls.user_id}")
            else:
                print(f"WARNING: Failed to create test user. Status: {register_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Failed to setup test user: {e}")
        
        # Wait for service to start if needed
        max_retries = 5
        retry_delay = 2
        for i in range(max_retries):
            try:
                response = requests.get(f"{NOTIFICATION_SERVICE_URL}{API_PREFIX}/notifications/health")
                if response.status_code == 200:
                    print("Notification Service is running.")
                    break
            except requests.exceptions.ConnectionError:
                print(f"Waiting for Notification Service to start (attempt {i+1}/{max_retries})...")
                time.sleep(retry_delay)
                
        if i == max_retries - 1:
            print("WARNING: Unable to connect to Notification Service. Tests may fail.")
    
    def test_01_health_check(self):
        """Test the health check endpoint."""
        try:
            response = requests.get(f"{NOTIFICATION_SERVICE_URL}{API_PREFIX}/notifications/health")
            self.assertEqual(response.status_code, 200)
            print("Health check passed.")
        except requests.exceptions.ConnectionError:
            self.fail("Notification service is not running.")
    
    def test_02_send_email_notification(self):
        """Test sending an email notification."""
        if not self.__class__.user_id:
            self.skipTest("User ID not available. Skipping test.")
            
        try:
            url = f"{NOTIFICATION_SERVICE_URL}{API_PREFIX}/notifications/email"
            payload = {
                "user_id": self.__class__.user_id,
                "email": self.test_user["email"],
                "subject": f"Test Notification {int(time.time())}",
                "body": "This is a test notification from the automated test suite."
            }
            
            response = requests.post(url, json=payload)
            
            self.assertEqual(response.status_code, 201)
            data = response.json()
            
            self.assertIsNotNone(data.get("id"))
            self.assertEqual(data.get("user_id"), self.__class__.user_id)
            self.assertEqual(data.get("email"), self.test_user["email"])
            
            print(f"Email notification created with ID: {data.get('id')}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_03_process_email_queue(self):
        """Test processing the email notification queue."""
        try:
            url = f"{NOTIFICATION_SERVICE_URL}{API_PREFIX}/notifications/email/process"
            
            response = requests.post(url)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn("message", data)
            print(f"Email processing result: {data.get('message')}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_04_schedule_calendar_event(self):
        """Test scheduling a calendar event."""
        if not self.__class__.user_id:
            self.skipTest("User ID not available. Skipping test.")
            
        try:
            url = f"{NOTIFICATION_SERVICE_URL}{API_PREFIX}/notifications/calendar"
            
            # Calculate start and end time (tomorrow)
            tomorrow = time.time() + 86400  # 24 hours in seconds
            start_time = time.strftime("%Y-%m-%d 10:00", time.localtime(tomorrow))
            end_time = time.strftime("%Y-%m-%d 11:00", time.localtime(tomorrow))
            
            payload = {
                "user_id": self.__class__.user_id,
                "email": self.test_user["email"],
                "summary": f"Test Calendar Event {int(time.time())}",
                "description": "This is a test calendar event from the automated test suite.",
                "start_time": start_time,
                "end_time": end_time
            }
            
            response = requests.post(url, json=payload)
            
            self.assertEqual(response.status_code, 201)
            data = response.json()
            
            self.assertIsNotNone(data.get("id"))
            self.assertEqual(data.get("user_id"), self.__class__.user_id)
            self.assertEqual(data.get("email"), self.test_user["email"])
            
            print(f"Calendar event scheduled with ID: {data.get('id')}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_05_process_calendar_queue(self):
        """Test processing the calendar event queue."""
        try:
            url = f"{NOTIFICATION_SERVICE_URL}{API_PREFIX}/notifications/calendar/process"
            
            response = requests.post(url)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn("message", data)
            print(f"Calendar processing result: {data.get('message')}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

if __name__ == "__main__":
    unittest.main() 