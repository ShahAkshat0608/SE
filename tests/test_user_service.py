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
API_PREFIX = "/api/v1"

class TestUserManagementService(unittest.TestCase):
    """Tests for the User Management Service."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test data."""
        cls.test_user = {
            "name": "Test User",
            "email": f"test.user.{int(time.time())}@example.com",
            "password": "securePassword123!",
            "contact": "1234567890"
        }
        cls.auth_token = None
        cls.user_id = None
        
        # Wait for service to start if needed
        max_retries = 5
        retry_delay = 2
        for i in range(max_retries):
            try:
                response = requests.get(f"{USER_SERVICE_URL}/health")
                if response.status_code == 200:
                    print("User Service is running.")
                    break
            except requests.exceptions.ConnectionError:
                print(f"Waiting for User Service to start (attempt {i+1}/{max_retries})...")
                time.sleep(retry_delay)
                
        if i == max_retries - 1:
            print("WARNING: Unable to connect to User Service. Tests may fail.")
    
    def test_01_health_check(self):
        """Test the health check endpoint."""
        try:
            response = requests.get(f"{USER_SERVICE_URL}/health")
            self.assertEqual(response.status_code, 200)
            print("Health check passed.")
        except requests.exceptions.ConnectionError:
            self.fail("User service is not running.")
            
    def test_02_register_user(self):
        """Test user registration."""
        try:
            url = f"{USER_SERVICE_URL}{API_PREFIX}/auth/register"
            response = requests.post(url, json=self.test_user)
            
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.__class__.user_id = data.get("id")
            
            self.assertIsNotNone(data.get("id"))
            self.assertEqual(data.get("name"), self.test_user["name"])
            self.assertEqual(data.get("email"), self.test_user["email"])
            
            print(f"Created test user with ID: {self.__class__.user_id}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_03_login(self):
        """Test user login."""
        try:
            url = f"{USER_SERVICE_URL}{API_PREFIX}/auth/login"
            payload = {
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
            response = requests.post(url, json=payload)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.__class__.auth_token = data.get("access_token")
            
            self.assertIsNotNone(data.get("id"))
            self.assertIsNotNone(data.get("access_token"))
            
            print("Login successful, received auth token.")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_04_get_user_details(self):
        """Test getting user details."""
        if not self.__class__.user_id or not self.__class__.auth_token:
            self.skipTest("Login or registration failed, skipping this test.")
            
        try:
            url = f"{USER_SERVICE_URL}{API_PREFIX}/auth/users/{self.__class__.user_id}"
            headers = {"Authorization": f"Bearer {self.__class__.auth_token}"}
            response = requests.get(url, headers=headers)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertEqual(data.get("id"), self.__class__.user_id)
            self.assertEqual(data.get("email"), self.test_user["email"])
            self.assertEqual(data.get("name"), self.test_user["name"])
            
            print("Successfully retrieved user details.")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

if __name__ == "__main__":
    unittest.main() 