from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Generic
from ...data.data_access_test import TestDataAccess
from ...data.data_access import DataAccess
from ...data.cache import SimpleMemoryCache

ResponseType = TypeVar('ResponseType')

class UserAnalyticsStrategy(ABC, Generic[ResponseType]):
    """Abstract base class for all user analytics strategies"""
    
    def __init__(self):
        self.data_access = DataAccess()
        self.cache = SimpleMemoryCache()
    
    @abstractmethod
    async def generate_report(self, user_id: str) -> ResponseType:
        """Generate an analytics report for a user"""
        pass
    
    async def get_cached_report(self, cache_key: str) -> Dict[str, Any]:
        """Get a report from cache if it exists"""
        return await self.cache.get(cache_key)
    
    async def cache_report(self, cache_key: str, report: Dict[str, Any], ttl: int = 300) -> None:
        """Cache a report with specified TTL (default 5 minutes)"""
        await self.cache.set(cache_key, report, ttl)


class UserAnalyticsContext:
    """Context class that uses a strategy to generate user analytics reports"""
    
    def __init__(self, strategy: UserAnalyticsStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: UserAnalyticsStrategy) -> None:
        """Change the strategy at runtime"""
        self._strategy = strategy
    
    async def generate_report(self, user_id: str) -> Any:
        """Generate a report using the current strategy"""
        return await self._strategy.generate_report(user_id)