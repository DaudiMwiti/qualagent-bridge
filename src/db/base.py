
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import logging

from src.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Create async engine with proper connection pool settings and logging
engine = create_async_engine(
    settings.DATABASE_URI,
    echo=False,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before using them
    logging_name="sqlalchemy.engine"
)

# Create async session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for all models
Base = declarative_base()

# Connection pool monitoring function
async def get_pool_status():
    """Get current status of the connection pool"""
    return {
        "size": settings.DB_POOL_SIZE,
        "overflow": settings.DB_MAX_OVERFLOW,
        "timeout": settings.DB_POOL_TIMEOUT,
        "recycle": settings.DB_POOL_RECYCLE,
        # Not directly accessible, but useful for monitoring
        "connections_in_use": -1,  # Placeholder, actual monitoring would require additional logic
        "connections_available": -1  # Placeholder
    }
