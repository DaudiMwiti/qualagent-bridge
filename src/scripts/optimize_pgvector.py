
import asyncio
import sys
import argparse
from sqlalchemy import text

sys.path.append(".")  # Add project root to path

from src.db.base import async_session
from src.core.config import settings

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
        else:
            # Create an IVFFlat index for faster approximate nearest neighbor search
            # The 'lists' parameter controls the number of partitions
            await session.execute(text(f"""
            CREATE INDEX vectors_embedding_ivfflat_idx 
            ON vectors USING ivfflat (embedding vector_cosine_ops) 
            WITH (lists = {settings.VECTOR_INDEX_LISTS})
            """))
            print(f"Created IVFFlat index with {settings.VECTOR_INDEX_LISTS} lists")
        
        # Check for agent_memories index
        result = await session.execute(text(
            "SELECT indexname FROM pg_indexes WHERE indexname = 'memories_embedding_ivfflat_idx'"
        ))
        
        if result.scalar_one_or_none():
            print("Memories IVFFlat index already exists, skipping creation")
        else:
            # Create an IVFFlat index for agent_memories table too
            await session.execute(text(f"""
            CREATE INDEX memories_embedding_ivfflat_idx 
            ON agent_memories USING ivfflat (embedding vector_cosine_ops) 
            WITH (lists = {settings.VECTOR_INDEX_LISTS})
            """))
            print(f"Created IVFFlat index for agent_memories with {settings.VECTOR_INDEX_LISTS} lists")
        
        # Add additional indexes for common query patterns
        await session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_agent_memories_project_id ON agent_memories(project_id);
        CREATE INDEX IF NOT EXISTS idx_agent_memories_agent_id ON agent_memories(agent_id);
        """))
        
        # Update statistics for query planner
        await session.execute(text("ANALYZE vectors;"))
        await session.execute(text("ANALYZE agent_memories;"))
        
        await session.commit()
        
        print("Vector search optimization complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize pgvector indexes")
    parser.add_argument("--lists", type=int, default=settings.VECTOR_INDEX_LISTS,
                        help=f"Number of lists for IVFFlat index (default: {settings.VECTOR_INDEX_LISTS})")
    args = parser.parse_args()
    
    async def main():
        # Override settings if provided
        if args.lists:
            settings.VECTOR_INDEX_LISTS = args.lists
            print(f"Using custom list count: {args.lists}")
            
        await optimize_pgvector_indexes()
        print("Optimization complete!")
    
    asyncio.run(main())
