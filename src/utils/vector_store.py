from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, MetaData, Text, Index, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.future import select
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import time

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
            Column("tag", String(50), nullable=True),  # New column for memory tags
            Column("score", Float, nullable=True),  # New column for memory relevance score
            Column("summary", Text, nullable=True),  # New column for memory summaries
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
    
    async def tag_memory(self, text: str) -> str:
        """
        Tag a memory with a semantic label using LLM
        
        Args:
            text: The memory text to tag
            
        Returns:
            A semantic tag from the predefined list
        """
        try:
            # Create a ChatOpenAI object
            llm = ChatOpenAI(
                model=settings.DEFAULT_MODEL,
                temperature=0.1,
                api_key=settings.OPENAI_API_KEY
            )
            
            # Define the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a memory tagging system. Analyze the text and assign ONE tag from this list: "
                          "['observation', 'emotion', 'recommendation', 'complaint', 'idea', 'other']. "
                          "Respond with ONLY the tag word, nothing else."),
                ("user", f"Text to tag: {text}")
            ])
            
            # Get the response
            chain = prompt | llm
            response = await chain.ainvoke({})
            
            # Extract the tag (removing extra spaces and converting to lowercase)
            tag = response.content.strip().lower()
            
            # Ensure it's one of our allowed tags
            allowed_tags = ["observation", "emotion", "recommendation", "complaint", "idea", "other"]
            if tag not in allowed_tags:
                return "other"
                
            return tag
            
        except Exception as e:
            # Log the error and return a default tag
            print(f"Error tagging memory: {str(e)}")
            return "other"
    
    async def summarize_memories(self, memories: List[Dict[str, Any]]) -> str:
        """
        Generate a concise summary of related memories
        
        Args:
            memories: List of memory objects to summarize
            
        Returns:
            A summary string
        """
        if not memories or len(memories) <= 1:
            return memories[0]["text"] if memories else ""
        
        try:
            # Extract just the text from each memory
            memory_texts = [mem["text"] for mem in memories]
            memory_text_combined = "\n- " + "\n- ".join(memory_texts)
            
            # Create a ChatOpenAI object
            llm = ChatOpenAI(
                model=settings.DEFAULT_MODEL,
                temperature=0.1,
                api_key=settings.OPENAI_API_KEY
            )
            
            # Define the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a memory summarization system. Create a concise summary (max 100 words) that captures "
                          "the key points from these related memories. Be specific and include important details."),
                ("user", f"Memories to summarize:\n{memory_text_combined}")
            ])
            
            # Get the response
            chain = prompt | llm
            response = await chain.ainvoke({})
            
            return response.content.strip()
            
        except Exception as e:
            # Log the error and return a concatenation of the original memories
            print(f"Error summarizing memories: {str(e)}")
            return " | ".join([mem["text"][:50] + "..." for mem in memories])
    
    async def similarity_search(
        self, 
        query: str, 
        project_id: int, 
        k: int = 5,
        table_name: str = "vectors",
        offset: int = 0,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in the specified table"""
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Select the appropriate table
        table = self.vectors_table if table_name == "vectors" else self.memory_table
        
        # Build the SQL query using pgvector's cosine similarity
        # This uses the <=> operator which is the cosine distance operator
        q = f"""
        WITH similarity_results AS (
            SELECT 
                id, 
                text, 
                metadata, 
                1 - (embedding <=> :query_embedding::float[]) as similarity
            FROM {table_name}
            WHERE project_id = :project_id
                AND (1 - (embedding <=> :query_embedding::float[])) >= :min_score
            ORDER BY embedding <=> :query_embedding::float[]
            LIMIT :k
            OFFSET :offset
        )
        SELECT * FROM similarity_results
        """
        
        try:
            # Execute the query with parameters
            result = await self.db.execute(
                text(q),
                {
                    "query_embedding": query_embedding,
                    "project_id": project_id,
                    "k": k,
                    "offset": offset,
                    "min_score": min_score
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
            OFFSET :offset
            """
            
            try:
                fallback_result = await self.db.execute(
                    text(fallback_query),
                    {
                        "query": query, 
                        "project_id": project_id, 
                        "k": k,
                        "offset": offset
                    }
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
        k: int = 5,
        tag_memories: bool = True,
        group_similar: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch relevant memories based on a query and filters, with scoring and tagging"""
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
            tag,
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
                memory = {
                    "id": row["id"],
                    "text": row["text"],
                    "memory_type": row["memory_type"],
                    "timestamp": row["timestamp"],
                    "metadata": row["metadata"] or {},
                    "score": float(row["similarity"]),
                }
                
                # Add tag if it exists in the database or generate a new one
                if row["tag"] and not tag_memories:
                    memory["tag"] = row["tag"]
                elif tag_memories:
                    # Generate a new tag using LLM
                    tag = await self.tag_memory(row["text"])
                    memory["tag"] = tag
                    
                    # Update the tag in the database
                    update_q = """
                    UPDATE agent_memories
                    SET tag = :tag
                    WHERE id = :id
                    """
                    await self.db.execute(text(update_q), {"tag": tag, "id": row["id"]})
                    await self.db.commit()
                
                memories.append(memory)
            
            # Group similar memories if requested
            if group_similar and memories:
                # Simple grouping by tag
                grouped_memories = {}
                for memory in memories:
                    tag = memory.get("tag", "other")
                    if tag not in grouped_memories:
                        grouped_memories[tag] = []
                    grouped_memories[tag].append(memory)
                
                # Summarize each group
                summarized_memories = []
                for tag, group in grouped_memories.items():
                    if len(group) > 1:
                        # Generate a summary for the group
                        summary = await self.summarize_memories(group)
                        
                        # Use the highest score from the group
                        max_score = max(mem["score"] for mem in group)
                        
                        summarized_memories.append({
                            "id": f"group_{tag}_{len(summarized_memories)}",
                            "text": summary,
                            "memory_type": group[0]["memory_type"],  # Use the type from the first memory
                            "timestamp": max(mem["timestamp"] for mem in group),  # Use the most recent timestamp
                            "metadata": {"group_size": len(group), "source_ids": [mem["id"] for mem in group]},
                            "score": max_score,
                            "tag": tag,
                            "is_summary": True
                        })
                    else:
                        # Just add the single memory
                        summarized_memories.append(group[0])
                
                # Sort by score again
                summarized_memories.sort(key=lambda x: x["score"], reverse=True)
                return summarized_memories[:k]  # Limit to k memories after grouping
                
            return memories
            
        except Exception as e:
            # Return empty list on error
            print(f"Error in fetch_memories: {str(e)}")
            return []
    
    async def get_recent_memories(
        self,
        project_id: int,
        memory_type: Optional[str] = None,
        agent_id: Optional[int] = None,
        analysis_id: Optional[int] = None,
        limit: int = 10,
        tag_memories: bool = True
    ) -> List[Dict[str, Any]]:
        """Get the most recent memories based on filters, with optional tagging"""
        # Build query with filters
        q = """
        SELECT id, text, memory_type, timestamp, metadata, tag
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
                memory = {
                    "id": row["id"],
                    "text": row["text"],
                    "memory_type": row["memory_type"],
                    "timestamp": row["timestamp"],
                    "metadata": row["metadata"] or {}
                }
                
                # Add tag if it exists in the database or generate a new one
                if row["tag"] and not tag_memories:
                    memory["tag"] = row["tag"]
                elif tag_memories:
                    # Generate a new tag using LLM
                    tag = await self.tag_memory(row["text"])
                    memory["tag"] = tag
                    
                    # Update the tag in the database
                    update_q = """
                    UPDATE agent_memories
                    SET tag = :tag
                    WHERE id = :id
                    """
                    await self.db.execute(text(update_q), {"tag": tag, "id": row["id"]})
                    await self.db.commit()
                
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            # Return empty list on error
            print(f"Error in get_recent_memories: {str(e)}")
            return []
    
    async def add_memory(
        self,
        text: str,
        project_id: int,
        memory_type: str = "session",
        agent_id: Optional[int] = None,
        analysis_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_tag: bool = True
    ) -> int:
        """
        Add a new memory to the agent's memory system with optional automatic tagging
        
        Args:
            text: The text content of the memory
            project_id: Project ID
            memory_type: Type of memory (session, long_term, preference)
            agent_id: Optional agent ID
            analysis_id: Optional analysis ID
            metadata: Additional metadata
            auto_tag: Whether to automatically tag the memory
            
        Returns:
            The ID of the new memory
        """
        # Generate embedding
        embedding = await self.embeddings.aembed_query(text)
        
        # Generate tag if auto_tag is enabled
        tag = None
        if auto_tag:
            tag = await self.tag_memory(text)
        
        # Current timestamp
        timestamp = time.time()
        
        # Insert the memory
        memory_insert = """
        INSERT INTO agent_memories
        (text, embedding, project_id, agent_id, analysis_id, memory_type, timestamp, metadata, tag)
        VALUES
        (:text, :embedding, :project_id, :agent_id, :analysis_id, :memory_type, :timestamp, :metadata, :tag)
        RETURNING id
        """
        
        try:
            result = await self.db.execute(
                text(memory_insert),
                {
                    "text": text,
                    "embedding": embedding,
                    "project_id": project_id,
                    "agent_id": agent_id,
                    "analysis_id": analysis_id,
                    "memory_type": memory_type,
                    "timestamp": timestamp,
                    "metadata": metadata or {},
                    "tag": tag
                }
            )
            
            memory_id = result.scalar_one()
            await self.db.commit()
            
            return memory_id
        except Exception as e:
            await self.db.rollback()
            raise e
