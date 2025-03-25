
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from src.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URI,
    echo=False,
    future=True,
    poolclass=NullPool  # Using NullPool for development, consider other pool options for production
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
