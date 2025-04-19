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
API_PREFIX = "/api/v1"

class TestProjectManagementService(unittest.TestCase):
    """Tests for the Project Management Service."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test data."""
        # Create test user for authentication
        cls.test_user = {
            "name": "Project Test User",
            "email": f"project.test.{int(time.time())}@example.com",
            "password": "securePassword123!",
            "contact": "1234567890"
        }
        cls.auth_token = None
        cls.user_id = None
        cls.project_id = None
        cls.test_project = {
            "name": f"Test Project {int(time.time())}",
            "description": "A test project created by automated tests"
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
                else:
                    print("WARNING: Failed to login test user.")
            else:
                print("WARNING: Failed to create test user.")
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Failed to setup test user: {e}")
        
        # Wait for service to start if needed
        max_retries = 5
        retry_delay = 2
        for i in range(max_retries):
            try:
                response = requests.get(f"{PROJECT_SERVICE_URL}/health")
                if response.status_code == 200:
                    print("Project Service is running.")
                    break
            except requests.exceptions.ConnectionError:
                print(f"Waiting for Project Service to start (attempt {i+1}/{max_retries})...")
                time.sleep(retry_delay)
                
        if i == max_retries - 1:
            print("WARNING: Unable to connect to Project Service. Tests may fail.")
    
    def test_01_health_check(self):
        """Test the health check endpoint."""
        try:
            response = requests.get(f"{PROJECT_SERVICE_URL}/health")
            self.assertEqual(response.status_code, 200)
            print("Health check passed.")
        except requests.exceptions.ConnectionError:
            self.fail("Project service is not running.")
    
    def test_02_create_project(self):
        """Test project creation."""
        if not self.__class__.auth_token:
            self.skipTest("Auth token not available. Skipping test.")
            
        try:
            url = f"{PROJECT_SERVICE_URL}/projects"
            headers = {"Authorization": f"Bearer {self.__class__.auth_token}"}
            payload = self.test_project.copy()
            payload["owner_id"] = self.__class__.user_id
            
            response = requests.post(url, json=payload, headers=headers)
            
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.__class__.project_id = data.get("id")
            
            self.assertIsNotNone(data.get("id"))
            self.assertEqual(data.get("name"), self.test_project["name"])
            self.assertEqual(data.get("description"), self.test_project["description"])
            
            print(f"Created test project with ID: {self.__class__.project_id}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_03_get_project_details(self):
        """Test getting project details."""
        if not self.__class__.auth_token or not self.__class__.project_id:
            self.skipTest("Auth token or project ID not available. Skipping test.")
            
        try:
            url = f"{PROJECT_SERVICE_URL}/projects/{self.__class__.project_id}"
            headers = {"Authorization": f"Bearer {self.__class__.auth_token}"}
            
            response = requests.get(url, headers=headers)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertEqual(data.get("id"), self.__class__.project_id)
            self.assertEqual(data.get("name"), self.test_project["name"])
            self.assertEqual(data.get("description"), self.test_project["description"])
            
            print("Successfully retrieved project details.")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_04_create_milestone(self):
        """Test creating a milestone in a project."""
        if not self.__class__.auth_token or not self.__class__.project_id:
            self.skipTest("Auth token or project ID not available. Skipping test.")
            
        try:
            url = f"{PROJECT_SERVICE_URL}/projects/{self.__class__.project_id}/milestones"
            headers = {"Authorization": f"Bearer {self.__class__.auth_token}"}
            params = {
                "milestone_name": "Test Milestone",
                "milestone_description": "A test milestone",
                "milestone_sequence_no": 1,
                "milestone_due_date": "2024-12-31"
            }
            
            response = requests.post(url, params=params, headers=headers)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIsNotNone(data.get("id"))
            self.assertEqual(data.get("name"), "Test Milestone")
            
            print(f"Created test milestone with ID: {data.get('id')}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")
    
    def test_05_list_milestones(self):
        """Test listing milestones of a project."""
        if not self.__class__.auth_token or not self.__class__.project_id:
            self.skipTest("Auth token or project ID not available. Skipping test.")
            
        try:
            url = f"{PROJECT_SERVICE_URL}/projects/{self.__class__.project_id}/milestones"
            headers = {"Authorization": f"Bearer {self.__class__.auth_token}"}
            
            response = requests.get(url, headers=headers)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIsInstance(data, list)
            self.assertGreaterEqual(len(data), 1)
            
            print(f"Successfully listed {len(data)} milestones.")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")

if __name__ == "__main__":
    unittest.main() 