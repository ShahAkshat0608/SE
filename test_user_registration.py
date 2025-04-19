#!/usr/bin/env python
import requests
import logging
import random
import string
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# User service URL
USER_SERVICE_URL = "http://127.0.0.1:8001"
API_PREFIX = "/api/v1"

def generate_random_email():
    """Generate a random test email address."""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    timestamp = int(time.time())
    return f"test.{random_str}.{timestamp}@gmail.com"

def test_user_registration(name="Test User", password="Test123!"):
    """Test registering a user directly through the API."""
    # Generate a random email to avoid conflicts
    email = generate_random_email()
    logger.info(f"Testing registration with email: {email}")
    
    # Prepare registration data
    register_url = f"{USER_SERVICE_URL}{API_PREFIX}/auth/register"
    payload = {
        "name": name,
        "email": email,
        "password": password,
        "contact": "1234567890"
    }
    
    try:
        logger.info(f"Sending registration request to {register_url}")
        logger.info(f"Registration payload: {payload}")
        
        # Make the request
        response = requests.post(register_url, json=payload, timeout=10)
        
        # Log detailed information about the response
        logger.info(f"Registration response status: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        
        try:
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
        except ValueError:
            logger.info(f"Response text (not JSON): {response.text}")
        
        if response.status_code == 201:
            logger.info("Registration successful!")
            user_data = response.json()
            logger.info(f"Created user with ID: {user_data.get('id')}")
            
            # Wait a bit to see if the welcome email is sent
            logger.info("Waiting 5 seconds to allow time for welcome email to be sent...")
            time.sleep(5)
            
            return True
        else:
            logger.error(f"Registration failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting user registration test...")
    if test_user_registration():
        logger.info("User registration test completed - check logs for welcome email information")
    else:
        logger.error("User registration test failed!") 