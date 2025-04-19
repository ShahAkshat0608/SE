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
PROJECT_SERVICE_URL = os.environ.get("PROJECT_SERVICE_URL", "http://127.0.0.1:8002")
ANALYTICS_SERVICE_URL = os.environ.get("ANALYTICS_SERVICE_URL", "http://127.0.0.1:8003")
API_PREFIX = "/api/v1"

class TestAnalyticsService(unittest.TestCase):
    """Tests for the Analytics Service."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test data."""
        # Create test user for authentication
        cls.test_user = {
            "name": "Analytics Test User",
            "email": f"analytics.test.{int(time.time())}@example.com",
            "password": "securePassword123!",
            "contact": "1234567890"
        }
        cls.auth_token = None
        cls.user_id = None
        cls.project_id = None
        cls.test_project = {
            "name": f"Analytics Test Project {int(time.time())}",
            "description": "A test project for analytics tests"
        }
        
        # Try to register user and get auth token
        try:
            # Register user
            register_url = f"{USER_SERVICE_URL}{API_PREFIX}/auth/register"
            register_response = requests.post(register_url, json=cls.test_user)
            
            if register_response.status_code == 201:
                user_data = register_response.json()
                cls.user_id = user_data.get("id")
                
                # Login to get token
                login_url = f"{USER_SERVICE_URL}{API_PREFIX}/auth/login"
                login_payload = {
                    "email": cls.test_user["email"],
                    "password": cls.test_user["password"]
                }
                login_response = requests.post(login_url, json=login_payload)
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    cls.auth_token = login_data.get("access_token")
                    print(f"Test user created and logged in. User ID: {cls.user_id}")
                    
                    # Create a project for analytics
                    project_url = f"{PROJECT_SERVICE_URL}/projects"
                    project_headers = {"Authorization": f"Bearer {cls.auth_token}"}
                    project_payload = cls.test_project.copy()
                    project_payload["owner_id"] = cls.user_id
                    
                    project_response = requests.post(project_url, json=project_payload, headers=project_headers)
                    if project_response.status_code == 201:
                        project_data = project_response.json()
                        cls.project_id = project_data.get("id")
                        print(f"Test project created. Project ID: {cls.project_id}")
                    else:
                        print("WARNING: Failed to create test project.")
                else:
                    print("WARNING: Failed to login test user.")
            else:
                print("WARNING: Failed to create test user.")
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Failed to setup test data: {e}")
        
        # Wait for service to start if needed
        max_retries = 5
        retry_delay = 2
        for i in range(max_retries):
            try:
                response = requests.get(f"{ANALYTICS_SERVICE_URL}/health")
                if response.status_code == 200:
                    print("Analytics Service is running.")
                    break
            except requests.exceptions.ConnectionError:
                print(f"Waiting for Analytics Service to start (attempt {i+1}/{max_retries})...")
                time.sleep(retry_delay)
                
        if i == max_retries - 1:
            print("WARNING: Unable to connect to Analytics Service. Tests may fail.")
    
    def test_01_health_check(self):
        """Test the health check endpoint."""
        try:
            response = requests.get(f"{ANALYTICS_SERVICE_URL}/health")
            self.assertEqual(response.status_code, 200)
            print("Health check passed.")
        except requests.exceptions.ConnectionError:
            self.fail("Analytics service is not running.")
    
    def test_02_get_user_analytics(self):
        """Test getting user analytics."""
        if not self.__class__.auth_token or not self.__class__.user_id:
            self.skipTest("Auth token or user ID not available. Skipping test.")
            
        try:
            url = f"{ANALYTICS_SERVICE_URL}/users/{self.__class__.user_id}"
            headers = {"Authorization": f"Bearer {self.__class__.auth_token}"}
            params = {
                "report_type": "comprehensive",
                "visualize": False
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            # Note: We check for either 200 or 404
            # 404 might occur if analytics data not yet established
            if response.status_code == 404:
                print("No analytics data found for user (this is normal for a new user).")
                return
                
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIsInstance(data, dict)
            print(f"Successfully retrieved user analytics.")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_03_get_project_analytics(self):
        """Test getting project analytics."""
        if not self.__class__.auth_token or not self.__class__.project_id:
            self.skipTest("Auth token or project ID not available. Skipping test.")
            
        try:
            url = f"{ANALYTICS_SERVICE_URL}/projects/{self.__class__.project_id}"
            headers = {"Authorization": f"Bearer {self.__class__.auth_token}"}
            params = {
                "report_type": "comprehensive",
                "visualize": False
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            # Note: We check for either 200 or 404
            # 404 might occur if analytics data not yet established
            if response.status_code == 404:
                print("No analytics data found for project (this is normal for a new project).")
                return
                
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIsInstance(data, dict)
            print(f"Successfully retrieved project analytics.")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_04_get_progress_report(self):
        """Test getting progress report."""
        if not self.__class__.auth_token or not self.__class__.project_id:
            self.skipTest("Auth token or project ID not available. Skipping test.")
            
        try:
            url = f"{ANALYTICS_SERVICE_URL}/projects/{self.__class__.project_id}/progress"
            headers = {"Authorization": f"Bearer {self.__class__.auth_token}"}
            params = {"visualize": True}
            
            response = requests.get(url, params=params, headers=headers)
            
            # Note: We check for either 200 or 404
            # 404 might occur if analytics data not yet established
            if response.status_code == 404:
                print("No progress data found for project (this is normal for a new project).")
                return
                
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIsInstance(data, dict)
            print(f"Successfully retrieved progress report.")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

if __name__ == "__main__":
    unittest.main() 