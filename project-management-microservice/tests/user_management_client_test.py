import argparse
import os
from typing import Optional

from user_management_client import APIClient
# copy this to same dir as user_management_client.py
# run as : python -m user_management_client_test 
#for each run chane email to test succesfully
def test_register_user_success(client: APIClient) -> tuple[bool, str]:
    """Test successful user registration."""
    try:
        user = client.register_user(
            name="Test User",
            email="yes1@example.com",
            password="password123",
            contact="1234567890"
        )
        if user.get("email") == "yes1@example.com" and "id" in user and "password" not in user:
            return True, f"Registered user - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}, Contact: {user.get('contact')}"
        return False, "Invalid response structure"
    except Exception as e:
        return False, str(e)

def test_register_user_duplicate_email(client: APIClient) -> tuple[bool, str]:
    """Test registration with duplicate email."""
    try:
        client.register_user(
            name="Another User",
            email="yes1@example.com",
            password="otherpassword"
        )
        return False, "Should have failed with duplicate email"
    except Exception as e:
        if "Conflict" in str(e) and "Email already registered" in str(e):
            return True, str(e)
        return False, f"Unexpected error: {str(e)}"

def test_login_user_success(client: APIClient) -> tuple[bool, str, Optional[int]]:
    """Test successful user login."""
    try:
        user = client.login_user(
            email="yes1@example.com",
            password="password123"
        )
        if user.get("email") == "yes1@example.com" and "id" in user and "password" not in user:
            return True, f"Logged in user - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}", user["id"]
        return False, "Invalid response structure", None
    except Exception as e:
        return False, str(e), None

def test_login_user_incorrect_password(client: APIClient) -> tuple[bool, str]:
    """Test login with incorrect password."""
    try:
        client.login_user(
            email="yes1@example.com",
            password="wrongpassword"
        )
        return False, "Should have failed with incorrect password"
    except Exception as e:
        if "Unauthorized" in str(e) and "Incorrect email or password" in str(e):
            return True, str(e)
        return False, f"Unexpected error: {str(e)}"

def test_login_user_nonexistent_email(client: APIClient) -> tuple[bool, str]:
    """Test login with non-existent email."""
    try:
        client.login_user(
            email="nosuchuser@example.com",
            password="password123"
        )
        return False, "Should have failed with non-existent email"
    except Exception as e:
        if "Unauthorized" in str(e) and "Incorrect email or password" in str(e):
            return True, str(e)
        return False, f"Unexpected error: {str(e)}"

def test_get_user_details_success(client: APIClient, user_id: Optional[int]) -> tuple[bool, str]:
    """Test getting user details for an existing user."""
    if not user_id:
        return False, "No user ID available"
    try:
        user = client.get_user_details(user_id)
        if user.get("id") == user_id and "email" in user and "password" not in user:
            return True, f"Retrieved user - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}"
        return False, "Invalid response structure"
    except Exception as e:
        return False, str(e)

def test_get_user_details_not_found(client: APIClient) -> tuple[bool, str]:
    """Test getting user details for a non-existent user."""
    try:
        client.get_user_details(9999)
        return False, "Should have failed with non-existent user"
    except Exception as e:
        if "Not Found" in str(e) and "User with ID 9999 not found" in str(e):
            return True, str(e)
        return False, f"Unexpected error: {str(e)}"

def run_tests(base_url: str, api_prefix: str):
    """Run all tests against the user_management_service using APIClient.

    Args:
        base_url (str): Base URL of the service.
        api_prefix (str): API prefix.
    """
    client = APIClient(base_url=base_url, api_prefix=api_prefix)
    print(f"Testing user_management_service at {base_url}{api_prefix}\n")

    tests = [
        ("Register User (Success)", test_register_user_success, []),
        ("Register User (Duplicate Email)", test_register_user_duplicate_email, []),
        ("Login User (Success)", test_login_user_success, []),
        ("Login User (Incorrect Password)", test_login_user_incorrect_password, []),
        ("Login User (Non-existent Email)", test_login_user_nonexistent_email, []),
        ("Get User Details (Success)", test_get_user_details_success, ["user_id"]),
        ("Get User Details (Not Found)", test_get_user_details_not_found, []),
    ]

    user_id = None
    results = []
    for test_name, test_func, extra_args in tests:
        print(f"Running: {test_name}")
        if extra_args:
            success, message = test_func(client, user_id)
        else:
            result = test_func(client)
            success, message = result[:2]
            if len(result) > 2:
                user_id = result[2]
        status = "PASSED" if success else "FAILED"
        print(f"[{status}] {message}\n")
        results.append((test_name, success))

    # Print summary
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    failed_tests = total_tests - passed_tests
    passed_names = [name for name, success in results if success]
    failed_names = [name for name, success in results if not success]

    print("=== Test Summary ===")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    if passed_names:
        print("Passed Tests:")
        for name in passed_names:
            print(f"  - {name}")
    if failed_names:
        print("Failed Tests:")
        for name in failed_names:
            print(f"  - {name}")
    print("===================")

def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Test APIClient against user_management_service endpoints")
    parser.add_argument(
        "--base-url",
        default=os.getenv("USER_SERVICE_URL", "http://localhost:8001"),
        help="Base URL of the user_management_service (e.g., http://localhost:8001)"
    )
    parser.add_argument(
        "--api-prefix",
        default=os.getenv("API_PREFIX", "/api/v1"),
        help="API prefix (e.g., /api/v1)"
    )
    args = parser.parse_args()

    run_tests(args.base_url, args.api_prefix)

if __name__ == "__main__":
    main()