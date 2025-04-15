from typing import Optional, Any
import time
import json
from threading import Lock

class SimpleMemoryCache:
    """
    Simple in-memory cache implementation for development using Singleton pattern.
    In production, this would be replaced with Redis or another caching solution.
    """
    # Class variables for singleton pattern
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """
        Singleton implementation using __new__ to ensure only one instance exists.
        Thread-safe with double-checked locking pattern.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SimpleMemoryCache, cls).__new__(cls)
                # Initialize the instance
                cls._instance._cache = {}
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the cache only once.
        """
        # Skip initialization if already done
        if self._initialized:
            return
            
        self._initialized = True
    
    @classmethod
    def get_instance(cls):
        """
        Static access method to get the singleton instance.
        """
        if cls._instance is None:
            cls()  # This will call __new__ and create the instance
        return cls._instance
        
    async def get(self, key: str) -> Optional[Any]:
        """Get an item from cache"""
        if key not in self._cache:
            return None
            
        # Check if the item has expired
        item = self._cache[key]
        if item["expiry"] < time.time():
            # Remove expired item
            del self._cache[key]
            return None
            
        return item["value"]
        
    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Set an item in cache with TTL"""
        self._cache[key] = {
            "value": value,
            "expiry": time.time() + ttl_seconds
        }
        return True
        
    async def invalidate(self, key: str) -> bool:
        """Remove an item from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
        
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Remove all items matching a pattern (simplified implementation).
        In a real Redis implementation, this would use the KEYS command.
        """
        count = 0
        keys_to_delete = []
        
        for key in self._cache.keys():
            if pattern in key:  # Simple pattern matching
                keys_to_delete.append(key)
                
        for key in keys_to_delete:
            del self._cache[key]
            count += 1
            
        return count
        
    async def clear(self) -> bool:
        """Clear the entire cache"""
        self._cache = {}
        return True