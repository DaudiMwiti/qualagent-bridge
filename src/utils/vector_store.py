
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, MetaData, Text, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.future import select
from sqlalchemy import func, text
from langchain_openai import OpenAIEmbeddings

from src.core.config import settings

class VectorStore:
    """
    A vector store implementation using PostgreSQL and pgvector
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        self.metadata = MetaData()
        
        # Main vectors table for document storage
        self.vectors_table = Table(
            "vectors",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("text", Text, nullable=False),
            Column("embedding", ARRAY(Float), nullable=False),
            Column("project_id", Integer, ForeignKey("projects.id"), nullable=False),
            Column("metadata", JSONB, nullable=True),
        )
        
        # Memory vectors for agent context
        self.memory_table = Table(
            "agent_memories",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("text", Text, nullable=False),
            Column("embedding", ARRAY(Float), nullable=False),
            Column("project_id", Integer, ForeignKey("projects.id"), nullable=False),
            Column("agent_id", Integer, ForeignKey("agents.id"), nullable=True),
            Column("analysis_id", Integer, ForeignKey("analyses.id"), nullable=True),
            Column("memory_type", String(50), nullable=False),  # 'session', 'long_term', 'preference'
            Column("timestamp", Float, nullable=False),  # Unix timestamp
            Column("metadata", JSONB, nullable=True),
        )
    
    async def setup_db_extensions(self):
        """Set up the necessary PostgreSQL extensions for vector operations"""
        # Create the vector extension if it doesn't exist
        await self.db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # Create indexes for vector similarity search (would need appropriate SQL here)
        # This is a placeholder - in a real implementation, you would create appropriate vector indexes
        await self.db.commit()
    
    async def add_texts(
        self, 
        texts: List[str], 
        project_id: int, 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[int]:
        """Add texts to the vector store"""
        if not texts:
            return []
        
        # Generate embeddings
        embeddings = await self.embeddings.aembed_documents(texts)
        
        # Prepare records
        records = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            records.append({
                "text": text,
                "embedding": embedding,
                "project_id": project_id,
                "metadata": metadata
            })
        
        # Insert records
        result = await self.db.execute(
            self.vectors_table.insert().returning(self.vectors_table.c.id),
            records
        )
        await self.db.commit()
        
        # Return the IDs of the inserted records
        return [row[0] for row in result]
    
    async def add_memory(
        self,
        text: str,
        project_id: int,
        memory_type: str = "session",
        agent_id: Optional[int] = None,
        analysis_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add a memory entry to the agent memory store"""
        # Generate embedding
        embedding = await self.embeddings.aembed_query(text)
        
        # Prepare record
        record = {
            "text": text,
            "embedding": embedding,
            "project_id": project_id,
            "agent_id": agent_id,
            "analysis_id": analysis_id,
            "memory_type": memory_type,
            "timestamp": float(func.extract('epoch', func.now())),
            "metadata": metadata or {}
        }
        
        # Insert record
        result = await self.db.execute(
            self.memory_table.insert().returning(self.memory_table.c.id),
            record
        )
        await self.db.commit()
        
        # Return the ID of the inserted record
        return result.scalar_one()
    
    async def similarity_search(
        self, 
        query: str, 
        project_id: int, 
        k: int = 5,
        table_name: str = "vectors"
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in the specified table"""
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Select the appropriate table
        table = self.vectors_table if table_name == "vectors" else self.memory_table
        
        # For now, return mock data
        # In a real implementation, you would use pgvector's cosine similarity search
        return [
            {"id": 1, "text": "Sample text matching query", "metadata": {"source": "sample"}, "score": 0.95}
        ]
    
    async def fetch_memories(
        self,
        query: str,
        project_id: int,
        memory_type: Optional[str] = None,
        agent_id: Optional[int] = None,
        analysis_id: Optional[int] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Fetch relevant memories based on a query and filters"""
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # In a real implementation, you would:
        # 1. Build a query with filters for project_id, memory_type, agent_id, analysis_id
        # 2. Use pgvector to find the most similar memories by cosine distance
        # 3. Return the results with their similarity scores
        
        # For now, return mock data
        return [
            {
                "id": 1, 
                "text": "Previous analysis showed strong correlations between X and Y themes",
                "memory_type": memory_type or "session",
                "timestamp": 1682541235.0,
                "metadata": {"analysis_id": 123},
                "score": 0.92
            }
        ]
    
    async def get_recent_memories(
        self,
        project_id: int,
        memory_type: Optional[str] = None,
        agent_id: Optional[int] = None,
        analysis_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get the most recent memories based on filters"""
        # In a real implementation, you would:
        # 1. Build a query with filters for project_id, memory_type, agent_id, analysis_id
        # 2. Order by timestamp descending
        # 3. Limit to the specified number of results
        
        # For now, return mock data
        return [
            {
                "id": 1, 
                "text": "User preferred detailed quotes in the analysis",
                "memory_type": memory_type or "preference",
                "timestamp": 1682541235.0,
                "metadata": {"preference_type": "quotes"}
            }
        ]
