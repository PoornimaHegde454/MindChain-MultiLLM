"""
Caching utilities for MultiLLM Router
"""

from typing import Optional, Any
import hashlib
import json
import time
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Cache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, ttl: int = None, max_size: int = None):
        self.cache = {}
        self.ttl = ttl or settings.CACHE_TTL_SECONDS
        self.max_size = max_size or settings.CACHE_MAX_SIZE
        self.access_times = {}  # For LRU eviction
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """Check if a cache entry is expired"""
        if key not in self.cache:
            return True
        
        entry = self.cache[key]
        if "expires_at" not in entry:
            return False
        
        return time.time() > entry["expires_at"]
    
    def _evict_lru(self):
        """Evict least recently used entry if cache is full"""
        if len(self.cache) < self.max_size:
            return
        
        # Find least recently used
        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        del self.cache[lru_key]
        del self.access_times[lru_key]
        logger.debug(f"Evicted LRU cache entry: {lru_key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self._is_expired(key):
            if key in self.cache:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        return self.cache[key]["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL"""
        self._evict_lru()
        
        expires_at = None
        if ttl or self.ttl:
            expires_at = time.time() + (ttl or self.ttl)
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time()
        }
        self.access_times[key] = time.time()
    
    def delete(self, key: str):
        """Delete a cache entry"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.access_times.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    def stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "entries": len(self.cache)
        }

# Global cache instance
cache = Cache()

# Redis cache implementation (optional)
try:
    import redis
    from app.config import settings
    
    class RedisCache:
        """Redis-based cache implementation"""
        
        def __init__(self, redis_url: str = None):
            redis_url = redis_url or settings.REDIS_URL
            if redis_url:
                self.client = redis.from_url(redis_url, decode_responses=True)
                self.enabled = True
            else:
                self.client = None
                self.enabled = False
        
        def get(self, key: str) -> Optional[Any]:
            """Get value from Redis cache"""
            if not self.enabled:
                return None
            
            try:
                value = self.client.get(key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                logger.error(f"Redis cache get error: {str(e)}")
                return None
        
        def set(self, key: str, value: Any, ttl: int = None):
            """Set value in Redis cache"""
            if not self.enabled:
                return
            
            try:
                ttl = ttl or settings.CACHE_TTL_SECONDS
                self.client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
            except Exception as e:
                logger.error(f"Redis cache set error: {str(e)}")
        
        def delete(self, key: str):
            """Delete a cache entry"""
            if not self.enabled:
                return
            
            try:
                self.client.delete(key)
            except Exception as e:
                logger.error(f"Redis cache delete error: {str(e)}")
        
        def clear(self):
            """Clear all cache entries (use with caution)"""
            if not self.enabled:
                return
            
            try:
                self.client.flushdb()
            except Exception as e:
                logger.error(f"Redis cache clear error: {str(e)}")
    
    # Try to initialize Redis cache
    redis_cache = RedisCache()
    
except ImportError:
    logger.info("Redis not available, using in-memory cache only")
    redis_cache = None

