import requests
import json
import time
from utils.test_token_gen import create_test_token

# Generate tokens for testing with the actual user IDs from our test data
user_token = create_test_token("user-101", "user")
team_lead_token = create_test_token("user-102", "team_lead") 
pm_token = create_test_token("user-103", "project_manager")

print(f"Regular User Token: {user_token}")
print(f"Team Lead Token: {team_lead_token}")
print(f"Project Manager Token: {pm_token}")

# Base URL
BASE_URL = "http://localhost:8000/api/analytics"

def test_endpoint(endpoint, token, params=None, expected_status=200, description=""):
    """Test an endpoint and display complete response for 5 seconds"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n=== Testing: {description} ===")
    print(f"Endpoint: {endpoint}")
    print(f"Using token for role: {'user' if token == user_token else 'team_lead' if token == team_lead_token else 'project_manager'}")
    
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
    
    print(f"\nStatus: {response.status_code} (Expected: {expected_status})")
    
    if response.status_code == expected_status:
        print("✅ Test PASSED")
    else:
        print("❌ Test FAILED")
    
    try:
        data = response.json()
        print("\nComplete Response:")
        print(json.dumps(data, indent=2))
    except:
        print("\nRaw response:")
        print(response.text)
    
    # Wait for 5 seconds before continuing
    print("\nWaiting for 5 seconds before next test...")
    time.sleep(5)
    
    return response

def run_tests():
    """Run all endpoint tests with delay between each"""
    # Health check
    print("Performing health check...")
    health_response = requests.get("http://localhost:8000/health")
    print(f"Health check status: {health_response.status_code}")
    print("Waiting 2 seconds before starting tests...")
    time.sleep(2)
    
    print("\nStarting analytics endpoint tests...")
    
    # User analytics tests
    test_endpoint("user/user-101/progress", user_token, 
                 description="User can view their own progress")
    
    test_endpoint("user/user-102/progress", user_token, 
                 expected_status=403, 
                 description="User cannot view another user's progress")
    
    test_endpoint("user/user-101/workload?visualize=true", user_token, 
                 description="User can view their own workload with visualizations")
    
    test_endpoint("user/user-101/comprehensive", user_token, 
                 description="User can view their comprehensive analytics")
    
    # Team analytics tests
    test_endpoint("team/team-101/progress", team_lead_token, 
                 params={"project_id": "project-101"},
                 description="Team lead can view team progress")
    
    test_endpoint("team/team-101/workload", team_lead_token, 
                 params={"project_id": "project-101"},
                 description="Team lead can view team workload")
    
    test_endpoint("team/team-101/comprehensive", team_lead_token, 
                 params={"project_id": "project-101", "visualize": True},
                 description="Team lead can view team comprehensive analytics with visualizations")
    
    # Project analytics tests
    test_endpoint("project/project-101/progress", pm_token, 
                 description="Project manager can view project progress")
    
    test_endpoint("project/project-101/workload", pm_token, 
                 description="Project manager can view project workload")
    
    test_endpoint("project/project-101/comprehensive", pm_token, 
                 params={"visualize": True},
                 description="Project manager can view project comprehensive analytics with visualizations")
    
    # Permission boundaries
    test_endpoint("project/project-101/progress", user_token, 
                 expected_status=403, 
                 description="Regular user cannot access project analytics")
    
    test_endpoint("project/project-101/progress", team_lead_token, 
                 expected_status=403, 
                 description="Team lead cannot access project analytics")

    print("\nAll tests completed!")

if __name__ == "__main__":
    run_tests()