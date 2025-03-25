
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, MetaData, Text, Index, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.future import select
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
        
        # Create indexes for vector similarity search
        # Create a GIN index on the embedding column for faster vector searches
        await self.db.execute(text(
            "CREATE INDEX IF NOT EXISTS vectors_embedding_idx ON vectors USING gin (embedding vector_ops)"
        ))
        await self.db.execute(text(
            "CREATE INDEX IF NOT EXISTS memories_embedding_idx ON agent_memories USING gin (embedding vector_ops)"
        ))
        
        await self.db.commit()
    
    # ... keep existing code (add_texts, add_memory methods) the same ...
    
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
        
        # Build the SQL query using pgvector's cosine similarity
        # This uses the <=> operator which is the cosine distance operator
        q = f"""
        SELECT 
            id, 
            text, 
            metadata, 
            1 - (embedding <=> :query_embedding::float[]) as similarity
        FROM {table_name}
        WHERE project_id = :project_id
        ORDER BY embedding <=> :query_embedding::float[]
        LIMIT :k
        """
        
        try:
            # Execute the query with parameters
            result = await self.db.execute(
                text(q),
                {
                    "query_embedding": query_embedding,
                    "project_id": project_id,
                    "k": k
                }
            )
            
            # Process the results
            documents = []
            for row in result.mappings():
                documents.append({
                    "id": row["id"],
                    "text": row["text"],
                    "metadata": row["metadata"] or {},
                    "score": float(row["similarity"])
                })
            
            return documents
            
        except Exception as e:
            # If the vector operations fail (which can happen if pgvector isn't set up correctly),
            # fall back to a basic fulltext search
            fallback_query = f"""
            SELECT id, text, metadata
            FROM {table_name} 
            WHERE project_id = :project_id
                AND to_tsvector('english', text) @@ plainto_tsquery('english', :query)
            LIMIT :k
            """
            
            try:
                fallback_result = await self.db.execute(
                    text(fallback_query),
                    {"query": query, "project_id": project_id, "k": k}
                )
                
                documents = []
                for row in fallback_result.mappings():
                    documents.append({
                        "id": row["id"],
                        "text": row["text"],
                        "metadata": row["metadata"] or {},
                        "score": 0.5  # Arbitrary score for fallback results
                    })
                
                return documents
                
            except Exception as fallback_error:
                # If even the fallback fails, return an empty list
                return []
    
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
        
        # Build the SQL query with filters
        q = """
        SELECT 
            id, 
            text, 
            memory_type,
            timestamp,
            metadata,
            1 - (embedding <=> :query_embedding::float[]) as similarity
        FROM agent_memories
        WHERE project_id = :project_id
        """
        
        params = {
            "query_embedding": query_embedding,
            "project_id": project_id
        }
        
        # Add optional filters
        if memory_type:
            q += " AND memory_type = :memory_type"
            params["memory_type"] = memory_type
            
        if agent_id:
            q += " AND agent_id = :agent_id"
            params["agent_id"] = agent_id
            
        if analysis_id:
            q += " AND analysis_id = :analysis_id"
            params["analysis_id"] = analysis_id
        
        # Add ordering and limit
        q += """
        ORDER BY embedding <=> :query_embedding::float[]
        LIMIT :k
        """
        params["k"] = k
        
        try:
            # Execute the query
            result = await self.db.execute(text(q), params)
            
            # Process results
            memories = []
            for row in result.mappings():
                memories.append({
                    "id": row["id"],
                    "text": row["text"],
                    "memory_type": row["memory_type"],
                    "timestamp": row["timestamp"],
                    "metadata": row["metadata"] or {},
                    "score": float(row["similarity"])
                })
            
            return memories
            
        except Exception as e:
            # Return empty list on error
            return []
    
    async def get_recent_memories(
        self,
        project_id: int,
        memory_type: Optional[str] = None,
        agent_id: Optional[int] = None,
        analysis_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get the most recent memories based on filters"""
        # Build query with filters
        q = """
        SELECT id, text, memory_type, timestamp, metadata
        FROM agent_memories
        WHERE project_id = :project_id
        """
        
        params = {"project_id": project_id}
        
        # Add optional filters
        if memory_type:
            q += " AND memory_type = :memory_type"
            params["memory_type"] = memory_type
            
        if agent_id:
            q += " AND agent_id = :agent_id"
            params["agent_id"] = agent_id
            
        if analysis_id:
            q += " AND analysis_id = :analysis_id"
            params["analysis_id"] = analysis_id
        
        # Order by timestamp (descending) and limit
        q += """
        ORDER BY timestamp DESC
        LIMIT :limit
        """
        params["limit"] = limit
        
        try:
            # Execute the query
            result = await self.db.execute(text(q), params)
            
            # Process results
            memories = []
            for row in result.mappings():
                memories.append({
                    "id": row["id"],
                    "text": row["text"],
                    "memory_type": row["memory_type"],
                    "timestamp": row["timestamp"],
                    "metadata": row["metadata"] or {}
                })
            
            return memories
            
        except Exception as e:
            # Return empty list on error
            return []

