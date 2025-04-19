from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Generic
# from ...data.data_access_test import TestDataAccess
from ...data.data_access import DataAccess
from ...data.cache import SimpleMemoryCache

ResponseType = TypeVar('ResponseType')

class TeamAnalyticsStrategy(ABC, Generic[ResponseType]):
    """Abstract base class for all team analytics strategies"""
    
    def __init__(self):
        self.data_access = DataAccess()
        self.cache = SimpleMemoryCache()
    
    @abstractmethod
    async def generate_report(self, team_id: str, project_id: str) -> ResponseType:
        """Generate an analytics report for a team within a project"""
        pass
    
    async def get_cached_report(self, cache_key: str) -> Dict[str, Any]:
        """Get a report from cache if it exists"""
        return await self.cache.get(cache_key)
    
    async def cache_report(self, cache_key: str, report: Dict[str, Any], ttl: int = 300) -> None:
        """Cache a report with specified TTL (default 5 minutes)"""
        await self.cache.set(cache_key, report, ttl)


class TeamAnalyticsContext:
    """Context class that uses a strategy to generate team analytics reports"""
    
    def __init__(self, strategy: TeamAnalyticsStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: TeamAnalyticsStrategy) -> None:
        """Change the strategy at runtime"""
        self._strategy = strategy
    
    async def generate_report(self, team_id: str, project_id: str) -> Any:
        """Generate a report using the current strategy"""
        return await self._strategy.generate_report(team_id, project_id)