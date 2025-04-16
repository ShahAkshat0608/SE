import requests
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8001", api_prefix: str = "/api/v1"):
        """Initialize the API client.

        Args:
            base_url (str): The base URL of the API (e.g., 'http://localhost:8001').
            api_prefix (str): The API prefix (e.g., '/api/v1').
        """
        self.base_url = base_url.rstrip("/")  # Remove trailing slash
        self.api_prefix = api_prefix.rstrip("/")  # Remove trailing slash
        self.auth_url = f"{self.base_url}{self.api_prefix}/auth"
        self.timeout = 5  # Default timeout in seconds

    def register_user(self, name: str, email: str, password: str, contact: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user.

        Args:
            name (str): The user's name.
            email (str): The user's email address.
            password (str): The user's password.
            contact (Optional[str]): The user's contact information (optional).

        Returns:
            Dict[str, Any]: User data (id, name, email, contact) on success.

        Raises:
            ValueError: If required fields are empty or invalid.
            requests.HTTPError: If the API request fails with an error status code.
            requests.RequestException: If the API request fails due to network issues.
        """
        if not all([name.strip(), email.strip(), password.strip()]):
            raise ValueError("Name, email, and password are required and cannot be empty.")

        url = f"{self.auth_url}/register"
        payload = {"name": name, "email": email, "password": password}
        if contact:
            payload["contact"] = contact

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx status codes
            return response.json()  # Returns UserResponse (id, name, email, contact)
        except requests.HTTPError as e:
            raise requests.HTTPError(self._handle_error(response, str(e)))
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to register user: {str(e)}")

    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Log in a user.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            Dict[str, Any]: User data (id, name, email, contact) on success.

        Raises:
            ValueError: If required fields are empty or invalid.
            requests.HTTPError: If the API request fails with an error status code.
            requests.RequestException: If the API request fails due to network issues.
        """
        if not all([email.strip(), password.strip()]):
            raise ValueError("Email and password are required and cannot be empty.")

        url = f"{self.auth_url}/login"
        payload = {"email": email, "password": password}

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx status codes
            return response.json()  # Returns UserResponse (id, name, email, contact)
        except requests.HTTPError as e:
            raise requests.HTTPError(self._handle_error(response, str(e)))
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to log in user: {str(e)}")

    def get_user_details(self, user_id: int) -> Dict[str, Any]:
        """Retrieve details of a user by ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            Dict[str, Any]: User data (id, name, email, contact) on success.

        Raises:
            ValueError: If user_id is invalid.
            requests.HTTPError: If the API request fails with an error status code.
            requests.RequestException: If the API request fails due to network issues.
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer.")

        url = f"{self.auth_url}/users/{user_id}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx status codes
            return response.json()  # Returns UserResponse (id, name, email, contact)
        except requests.HTTPError as e:
            raise requests.HTTPError(self._handle_error(response, str(e)))
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to retrieve user details: {str(e)}")

    def _handle_error(self, response: requests.Response, default_message: str) -> str:
        """Handle API errors and return a formatted error message.

        Args:
            response (requests.Response): The API response object.
            default_message (str): Default error message if response parsing fails.

        Returns:
            str: A formatted error message including status code and detail.
        """
        try:
            error_data = response.json()
            detail = error_data.get("detail", "Unknown error")
        except ValueError:
            detail = response.text or "No response body"

        status_code = response.status_code
        error_types = {
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
            409: "Conflict"
        }
        error_type = error_types.get(status_code, f"HTTP {status_code}")
        return f"{error_type}: {detail} ({default_message})"        
    def logout_user(self, email, password):
        """Logout a user."""
        pass

    def notify_user(self, user_id, message):
        """Send a notification to a user."""
        pass    