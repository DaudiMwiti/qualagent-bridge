
from typing import Any, Optional, Dict
import json
import logging
import time
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, Column, String, LargeBinary, Integer, Float
from sqlalchemy.sql import text
from src.db.base import Base
from src.core.config import settings

logger = logging.getLogger(__name__)

# Cache table model
class CacheEntry(Base):
    __tablename__ = "cache_entries"
    
    key = Column(String, primary_key=True)
    value = Column(LargeBinary, nullable=False)  # Serialized value
    expiry = Column(Float, nullable=False)  # Expiry time as timestamp
    created_at = Column(Float, nullable=False)  # Creation timestamp

class DBCache:
    """Database-backed cache implementation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.default_ttl = settings.SEARCH_CACHE_TTL  # Default TTL in seconds
    
    @staticmethod
    def _hash_key(key: str) -> str:
        """Create a deterministic hash for a cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache if it exists and is not expired"""
        try:
            hashed_key = self._hash_key(key)
            now = time.time()
            
            # Query for non-expired cache entry
            result = await self.db.execute(
                select(CacheEntry.value)
                .where(CacheEntry.key == hashed_key)
                .where(CacheEntry.expiry > now)
            )
            
            entry = result.scalar_one_or_none()
            
            if entry:
                # Deserialize the value
                try:
                    return json.loads(entry.decode('utf-8'))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to deserialize cache value for key: {key}")
                    return None
            
            return None
            
        except Exception as e:
            logger.warning(f"Cache get operation failed: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store a value in the cache with expiry"""
        try:
            hashed_key = self._hash_key(key)
            now = time.time()
            ttl_seconds = ttl if ttl is not None else self.default_ttl
            expiry = now + ttl_seconds
            
            # Serialize the value
            serialized = json.dumps(value, default=str).encode('utf-8')
            
            # Upsert the cache entry
            await self.db.execute(
                text("""
                INSERT INTO cache_entries (key, value, expiry, created_at)
                VALUES (:key, :value, :expiry, :created_at)
                ON CONFLICT (key) DO UPDATE
                SET value = :value, expiry = :expiry
                """),
                {
                    "key": hashed_key,
                    "value": serialized,
                    "expiry": expiry,
                    "created_at": now
                }
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Cache set operation failed: {str(e)}")
            await self.db.rollback()
            return False
    
    async def delete(self, key: str) -> bool:
        """Remove a key from the cache"""
        try:
            hashed_key = self._hash_key(key)
            await self.db.execute(
                text("DELETE FROM cache_entries WHERE key = :key"),
                {"key": hashed_key}
            )
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Cache delete operation failed: {str(e)}")
            await self.db.rollback()
            return False
    
    async def cleanup_expired(self) -> int:
        """Delete expired cache entries, returns number of entries cleaned up"""
        try:
            now = time.time()
            result = await self.db.execute(
                text("DELETE FROM cache_entries WHERE expiry < :now RETURNING 1"),
                {"now": now}
            )
            count = len(result.all())
            await self.db.commit()
            return count
        except Exception as e:
            logger.error(f"Cache cleanup failed: {str(e)}")
            await self.db.rollback()
            return 0

class CacheService:
    """Facade for caching services that handles DB session management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._cache = DBCache(db)
    
    async def get(self, key: str) -> Optional[Any]:
        return await self._cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        return await self._cache.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        return await self._cache.delete(key)
    
    @staticmethod
    def generate_key(prefix: str, **parameters) -> str:
        """Generate a consistent cache key from parameters"""
        # Sort params to ensure consistency
        param_str = json.dumps(parameters, sort_keys=True, default=str)
        # Create hash for the parameters
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}:{param_hash}"
    
    async def cleanup(self) -> int:
        """Run maintenance tasks on the cache"""
        return await self._cache.cleanup_expired()
