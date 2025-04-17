from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import os
from dotenv import load_dotenv

# JWT security scheme
security = HTTPBearer()

# Constants - normally should be in config
# JWT_SECRET_KEY = "your-secret-key-for-development-only"  # Use env vars in production
# JWT_ALGORITHM = "HS256"
# TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Load environment variables from .env file
JWT_SECRET_KEY = "your-secret-key-for-development-only"  # Use env vars in production
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

async def verify_token(credentials : Dict) -> Dict:
    # print("Verifying token:", credentials.keys())
    """Verify JWT token and return payload"""
    try:
        # print(f"Verifying token: {credentials['credentials']}")
        payload = jwt.decode(
            credentials['credentials'],
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        
        # Check if token is expired
        if "exp" in payload and datetime.utcnow().timestamp() > payload["exp"]:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        
        return payload
    except jwt.PyJWTError:
        print("Invalid token")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

def create_access_token(data: Dict) -> str:
    """Create a new JWT token"""
    to_encode = data.copy()
    
    # Set expiration
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    
    # Create token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt

def create_test_token(user_id: str, role: str) -> str:
    """Create a test token for development purposes"""
    token_data = {
        "sub": user_id,
        "role": role,
        "name": f"Test {role.capitalize()}"
    }
    return create_access_token(token_data)

async def get_current_user(token: Dict = Depends(verify_token)) -> Dict:
    print("Get current user from token:", token)
    """Get current user from token"""
    return {
        "id": token.get("sub"),
        "role": token.get("role", "user"),
        "name": token.get("name", "Unknown User"),
        "email": token.get("email", ""),
    }