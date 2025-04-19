import requests
import jwt
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional
import logging
import time
from functools import lru_cache
from ...utils.auth_token_gen import create_access_token

logger = logging.getLogger(__name__)

class AnalyticsServiceClient:
    """Client for interacting with the Analytics Microservice"""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8003/api/analytics",
        service_secret: str = "your-secret-key-for-development-only",
        timeout: int = 10,
        enable_cache: bool = True,
        cache_ttl: int = 300,  # 5 minutes
        retry_attempts: int = 3
    ):
        self.base_url = base_url
        self.service_secret = service_secret
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self.retry_attempts = retry_attempts
        self._token_cache = {}

    def _get_token_for_role(self, user_id: str, role: str = "project_manager") -> str:
        """Create a test token for development purposes"""
        token_data = {
            "sub": user_id,
            "role": role,
            "name": f"Test {role.capitalize()}"
        }
        return create_access_token(token_data)
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Make a request to the analytics service with retry logic"""
        
        url = f"{self.base_url}/{endpoint}"
        
        # Determine appropriate role based on endpoint
        role = "user"
        user_id = "user-101"  # Default user
        
        if endpoint.startswith("project/"):
            role = "project_manager"
            user_id = "user-103"  # Project Manager ID
        elif endpoint.startswith("team/"):
            role = "team_lead"
            user_id = "user-102"  # Team Lead ID
        elif endpoint.startswith("user/"):
            user_id = endpoint.split("/")[1]  # Extract user ID from endpoint
        
        # Get token for the determined role and user
        token = self._get_token_for_role(user_id, role)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.request(
                    method=method, 
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )
                
                # Log more details on failure
                if response.status_code >= 400:
                    logger.error(f"Request failed with status {response.status_code}: {response.text}")
                    logger.debug(f"Request URL: {url}")
                    logger.debug(f"Request headers: {headers}")
                    logger.debug(f"Request params: {params}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request to analytics service failed (attempt {attempt+1}/{self.retry_attempts}): {str(e)}")
                if attempt == self.retry_attempts - 1:
                    logger.error(f"All attempts failed for {url}: {str(e)}")
                    raise
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff
    
    # [Rest of the class methods remain the same]
    # User Analytics Methods
    
    @lru_cache(maxsize=128)
    def get_user_progress(self, user_id: str, visualize: bool = False) -> Dict:
        """Get user progress analytics"""
        params = {"visualize": "true" if visualize else "false"}
        return self._make_request("GET", f"user/{user_id}/progress", params=params)
    
    def get_user_workload(self, user_id: str, visualize: bool = False) -> Dict:
        """Get user workload analytics"""
        params = {"visualize": "true" if visualize else "false"}
        return self._make_request("GET", f"user/{user_id}/workload", params=params)
    
    def get_user_comprehensive(self, user_id: str, visualize: bool = False) -> Dict:
        """Get comprehensive user analytics"""
        params = {"visualize": "true" if visualize else "false"}
        return self._make_request("GET", f"user/{user_id}/comprehensive", params=params)
    
    # Team Analytics Methods
    
    def get_team_progress(self, team_id: str, project_id: str = None, visualize: bool = False) -> Dict:
        """Get team progress analytics"""
        params = {"visualize": "true" if visualize else "false"}
        if project_id:
            params["project_id"] = project_id
        return self._make_request("GET", f"team/{team_id}/progress", params=params)
    
    def get_team_workload(self, team_id: str, project_id: str = None, visualize: bool = False) -> Dict:
        """Get team workload analytics"""
        params = {"visualize": "true" if visualize else "false"}
        if project_id:
            params["project_id"] = project_id
        return self._make_request("GET", f"team/{team_id}/workload", params=params)
    
    def get_team_comprehensive(self, team_id: str, project_id: str = None, visualize: bool = False) -> Dict:
        """Get comprehensive team analytics"""
        params = {"visualize": "true" if visualize else "false"}
        if project_id:
            params["project_id"] = project_id
        return self._make_request("GET", f"team/{team_id}/comprehensive", params=params)
    
    # Project Analytics Methods
    
    def get_project_progress(self, project_id: str, visualize: bool = False) -> Dict:
        """Get project progress analytics"""
        params = {"visualize": "true" if visualize else "false"}
        return self._make_request("GET", f"project/{project_id}/progress", params=params)
    
    def get_project_workload(self, project_id: str, visualize: bool = False) -> Dict:
        """Get project workload analytics"""
        params = {"visualize": "true" if visualize else "false"}
        return self._make_request("GET", f"project/{project_id}/workload", params=params)
    
    def get_project_comprehensive(self, project_id: str, visualize: bool = False) -> Dict:
        """Get comprehensive project analytics"""
        params = {"visualize": "true" if visualize else "false"}
        return self._make_request("GET", f"project/{project_id}/comprehensive", params=params)

    def invalidate_cache(self):
        """Clear the cache when data becomes stale"""
        if hasattr(self.get_user_progress, 'cache_clear'):
            self.get_user_progress.cache_clear()