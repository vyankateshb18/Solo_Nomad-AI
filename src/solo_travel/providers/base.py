"""Abstract Base Provider for Transport and Travel Data."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import time
import logging

logger = logging.getLogger(__name__)


class ProviderCache:
    """Lightweight in-memory cache with Time-To-Live (TTL) support."""
    def __init__(self, default_ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry["expires_at"]:
                return entry["data"]
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._cache[key] = {
            "data": value,
            "expires_at": time.time() + ttl
        }

    def clear(self) -> None:
        self._cache.clear()


class BaseTravelProvider(ABC):
    """Base class for all travel data providers with built-in cache and telemetry."""
    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache = ProviderCache(default_ttl_seconds=cache_ttl_seconds)

    @abstractmethod
    def search(self, **kwargs) -> List[Any]:
        """Perform search query and return normalized results."""
        pass
