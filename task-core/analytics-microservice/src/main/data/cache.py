from typing import Optional, Any
import time
import json

class SimpleMemoryCache:
    """
    Simple in-memory cache implementation for development.
    In production, this would be replaced with Redis or another caching solution.
    """
    def __init__(self):
        self._cache = {}
        
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