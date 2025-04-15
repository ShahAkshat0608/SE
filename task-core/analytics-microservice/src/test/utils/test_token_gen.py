from datetime import datetime, timedelta
from typing import Dict
import jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
TOKEN_EXPIRE_MINUTES = eval(os.getenv('TOKEN_EXPIRE_MINUTES'))

def create_access_token(data: Dict) -> str:
    """Create a new JWT token"""
    to_encode = data.copy()
    
    # Set expiration
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    
    # Create token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    print(f"Encoded JWT: {" generated encoded_jwt"}")  # Debugging line to print the encoded JWT
    return encoded_jwt


def create_test_token(user_id: str, role: str) -> str:
    """Create a test token for development purposes"""
    token_data = {
        "sub": user_id,
        "role": role,
        "name": f"Test {role.capitalize()}"
    }
    return create_access_token(token_data)


def create_service_token(service_name: str, target_service: str, role: str = "service") -> str:
    """
    Create a JWT token for service-to-service communication
    
    Args:
        service_name: Name/ID of the calling service
        target_service: Name of the service being called
        role: Role to assume (usually service, or a specific role like project_manager)
        
    Returns:
        JWT token string
    """
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": service_name,  # Subject (caller ID)
        "role": role,         # Role to assume
        "target": target_service,  # Target service
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp()  # Issued at
    }
    
    # Sign the token with the shared secret
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return token

