import pytest
from fastapi.testclient import TestClient
# Adjust import to be relative to the src dir added to sys.path in conftest
from main.core.config import settings

# Base URL for the API endpoints under test
API_URL = f"{settings.API_PREFIX}/auth"

def test_register_user_success(client: TestClient, test_db):
    """Test successful user registration."""
    response = client.post(
        f"{API_URL}/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "contact": "1234567890"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert data["contact"] == "1234567890"
    assert "id" in data
    assert "password" not in data # Ensure password is not returned
    assert "password_hash" not in data

def test_register_user_duplicate_email(client: TestClient, test_db):
    """Test registration with an email that already exists."""
    # First, register a user
    client.post(
        f"{API_URL}/register",
        json={"name": "Existing User", "email": "existing@example.com", "password": "password123"}
    )
    
    # Attempt to register again with the same email
    response = client.post(
        f"{API_URL}/register",
        json={"name": "Another User", "email": "existing@example.com", "password": "otherpassword"}
    )
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Email already registered."

def test_login_user_success(client: TestClient, test_db):
    """Test successful user login."""
    # Register user first
    reg_response = client.post(
        f"{API_URL}/register",
        json={"name": "Login User", "email": "login@example.com", "password": "goodpassword"}
    )
    assert reg_response.status_code == 201
    registered_user = reg_response.json()

    # Attempt login
    login_response = client.post(
        f"{API_URL}/login",
        json={"email": "login@example.com", "password": "goodpassword"}
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["email"] == "login@example.com"
    assert data["name"] == "Login User"
    assert data["id"] == registered_user["id"]
    assert "password" not in data
    assert "password_hash" not in data

def test_login_user_incorrect_password(client: TestClient, test_db):
    """Test login with incorrect password."""
    # Register user
    client.post(
        f"{API_URL}/register",
        json={"name": "Login Fail User", "email": "loginfail@example.com", "password": "correct"}
    )

    # Attempt login with wrong password
    login_response = client.post(
        f"{API_URL}/login",
        json={"email": "loginfail@example.com", "password": "incorrect"}
    )
    assert login_response.status_code == 401
    data = login_response.json()
    assert data["detail"] == "Incorrect email or password"

def test_login_user_nonexistent_email(client: TestClient, test_db):
    """Test login with an email that is not registered."""
    login_response = client.post(
        f"{API_URL}/login",
        json={"email": "nosuchuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 401
    data = login_response.json()
    assert data["detail"] == "Incorrect email or password"

def test_get_user_details_success(client: TestClient, test_db):
    """Test getting details for an existing user."""
    # Register user
    reg_response = client.post(
        f"{API_URL}/register",
        json={"name": "Details User", "email": "details@example.com", "password": "password"}
    )
    assert reg_response.status_code == 201
    user_id = reg_response.json()["id"]

    # Get details
    get_response = client.get(f"{API_URL}/users/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == user_id
    assert data["name"] == "Details User"
    assert data["email"] == "details@example.com"
    assert "password" not in data
    assert "password_hash" not in data

def test_get_user_details_not_found(client: TestClient, test_db):
    """Test getting details for a user ID that does not exist."""
    non_existent_id = 9999
    get_response = client.get(f"{API_URL}/users/{non_existent_id}")
    assert get_response.status_code == 404
    data = get_response.json()
    assert data["detail"] == f"User with ID {non_existent_id} not found." 