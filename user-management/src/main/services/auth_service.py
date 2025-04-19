import logging
from werkzeug.security import generate_password_hash, check_password_hash
# Adjust import path based on new structure
from ..models.user_model import (
    create_user as db_create_user,
    find_user_by_email,
    find_user_by_id
)
from .notification_client import send_welcome_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Note: Session management (like SESSION_FILE) is removed here.
# The CLI will handle storing login state. This service only validates/creates.

def register_user_service(name: str, email: str, password: str, contact: str | None = None) -> dict | None:
    """Registers a new user. Returns user dict or None if failed."""
    if find_user_by_email(email):
        logging.warning(f"Registration attempt for existing email: {email}")
        # Raise specific exception or return None/error marker for API
        return None # Indicate failure due to existing email

    password_hash = generate_password_hash(password)
    user = db_create_user(name, email, password_hash, contact)

    if user:
        logging.info(f"User '{email}' registered successfully.")
        # Send welcome email to the user
        try:
            send_welcome_email(user["id"], email, name)
        except Exception as e:
            logging.error(f"Failed to send welcome email to {email}: {e}")
            # Continue even if email fails, as the user is already registered
        
        # Return the created user data (excluding password hash)
        return user
    else:
        logging.error(f"User registration failed for email: {email}")
        return None

def login_user_service(email: str, password: str) -> dict | None:
    """Validates user credentials. Returns user dict (excluding hash) or None."""
    user = find_user_by_email(email)

    if user and check_password_hash(user['password_hash'], password):
        logging.info(f"Login successful for user: {email}")
        # Return user data, excluding the password hash for security
        user_data = user.copy()
        del user_data['password_hash']
        return user_data
    else:
        logging.warning(f"Failed login attempt for email: {email}")
        return None

def get_user_details_service(user_id: int) -> dict | None:
    """Gets user details by ID."""
    user = find_user_by_id(user_id)
    if user:
        return user # Already excludes password hash
    else:
        logging.warning(f"Attempted to get details for non-existent user ID: {user_id}")
        return None 