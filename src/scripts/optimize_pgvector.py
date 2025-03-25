
import asyncio
import sys
import argparse
from sqlalchemy import text

sys.path.append(".")  # Add project root to path

from src.db.base import async_session

async def optimize_pgvector_indexes():
    """Create optimized indexes for pgvector tables"""
    print("Creating optimized pgvector indexes...")
    
    async with async_session() as session:
        # Check if we already have the advanced index
        result = await session.execute(text(
            "SELECT indexname FROM pg_indexes WHERE indexname = 'vectors_embedding_ivfflat_idx'"
        ))
        
        if result.scalar_one_or_none():
            print("IVFFlat index already exists, skipping creation")
            return
        
        # Create an IVFFlat index for faster approximate nearest neighbor search
        # The 'lists' parameter controls the number of partitions - 100 is a good starting point
        # but may need tuning based on your dataset size
        await session.execute(text("""
        CREATE INDEX vectors_embedding_ivfflat_idx 
        ON vectors USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100)
        """))
        
        # Create an IVFFlat index for agent_memories table too
        await session.execute(text("""
        CREATE INDEX memories_embedding_ivfflat_idx 
        ON agent_memories USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 100)
        """))
        
        await session.commit()
        
        print("Created IVFFlat indexes for faster vector similarity search")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize pgvector indexes")
    
    async def main():
        await optimize_pgvector_indexes()
        print("Optimization complete!")
    
    asyncio.run(main())
