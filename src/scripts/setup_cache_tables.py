
import asyncio
import sys
import argparse
from sqlalchemy import text

sys.path.append(".")  # Add project root to path

from src.db.base import async_session, Base, engine

async def setup_cache_tables():
    """Create cache tables in the database"""
    print("Setting up cache tables...")
    
    async with engine.begin() as conn:
        # Create cache_entries table if it doesn't exist
        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS cache_entries (
            key VARCHAR(255) PRIMARY KEY,
            value BYTEA NOT NULL,
            expiry DOUBLE PRECISION NOT NULL,
            created_at DOUBLE PRECISION NOT NULL
        )
        """))
        
        # Create index on expiry for faster cleanup
        await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_cache_entries_expiry 
        ON cache_entries (expiry)
        """))
        
        print("Cache tables created successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up cache tables")
    
    async def main():
        await setup_cache_tables()
        print("Setup complete!")
    
    asyncio.run(main())
