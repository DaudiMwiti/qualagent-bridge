
from typing import Dict, Any, List, Optional
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from src.core.config import settings
from src.utils.vector_store import VectorStore
import logging
import json

logger = logging.getLogger(__name__)

@tool(return_direct=False)
async def retrieve_memories(
    query: str, 
    project_id: int,
    memory_type: Optional[str] = None,
    agent_id: Optional[int] = None,
    analysis_id: Optional[int] = None,
    k: int = 5,
    tag_memories: bool = True,
    group_similar: bool = False
) -> Dict[str, Any]:
    """
    Retrieve relevant memories based on semantic similarity to the query, with scoring and tagging.
    
    Args:
        query: The query to find relevant memories
        project_id: The ID of the project
        memory_type: Optional filter for memory type (session, long_term, preference)
        agent_id: Optional filter for specific agent
        analysis_id: Optional filter for specific analysis
        k: Number of memories to retrieve
        tag_memories: Whether to tag memories (or use existing tags)
        group_similar: Whether to group and summarize similar memories
        
    Returns:
        List of relevant memories with their similarity scores and semantic tags
    """
    logger.info(f"Retrieving memories for query: {query}")
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from src.db.base import async_session
        
        async with async_session() as session:
            vector_store = VectorStore(session)
            
            memories = await vector_store.fetch_memories(
                query=query,
                project_id=project_id,
                memory_type=memory_type,
                agent_id=agent_id,
                analysis_id=analysis_id,
                k=k,
                tag_memories=tag_memories,
                group_similar=group_similar
            )
            
            # Sort memories by tag for better organization
            if memories:
                memories.sort(key=lambda x: (x.get("tag", "other"), -x.get("score", 0)))
            
            return {"memories": memories}
            
    except Exception as e:
        logger.error(f"Error retrieving memories: {str(e)}")
        return {"error": str(e), "memories": []}

@tool(return_direct=False)
async def store_memory(
    text: str,
    project_id: int,
    memory_type: str = "session",
    agent_id: Optional[int] = None,
    analysis_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    auto_tag: bool = True
) -> Dict[str, Any]:
    """
    Store a new memory in the agent's memory system with automatic tagging.
    
    Args:
        text: The text to store as a memory
        project_id: The ID of the project
        memory_type: Type of memory (session, long_term, preference)
        agent_id: Optional ID of the agent
        analysis_id: Optional ID of the analysis
        metadata: Optional metadata to associate with the memory
        auto_tag: Whether to automatically tag the memory
        
    Returns:
        Confirmation of memory storage with the assigned tag
    """
    logger.info(f"Storing memory: {text[:50]}...")
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from src.db.base import async_session
        
        async with async_session() as session:
            vector_store = VectorStore(session)
            
            memory_id = await vector_store.add_memory(
                text=text,
                project_id=project_id,
                memory_type=memory_type,
                agent_id=agent_id,
                analysis_id=analysis_id,
                metadata=metadata,
                auto_tag=auto_tag
            )
            
            # If auto-tagging is enabled, retrieve the tag
            tag = None
            if auto_tag:
                tag = await vector_store.tag_memory(text)
            
            return {
                "status": "success",
                "memory_id": memory_id,
                "tag": tag,
                "message": "Memory stored and tagged successfully"
            }
            
    except Exception as e:
        logger.error(f"Error storing memory: {str(e)}")
        return {"status": "error", "error": str(e)}

@tool(return_direct=False)
async def get_recent_context(
    project_id: int,
    memory_type: Optional[str] = None,
    agent_id: Optional[int] = None,
    analysis_id: Optional[int] = None,
    limit: int = 5,
    tag_memories: bool = True
) -> Dict[str, Any]:
    """
    Get the most recent memories to provide context for the current analysis, with tags.
    
    Args:
        project_id: The ID of the project
        memory_type: Optional filter for memory type
        agent_id: Optional filter for specific agent
        analysis_id: Optional filter for specific analysis
        limit: Maximum number of memories to retrieve
        tag_memories: Whether to add tags to memories
        
    Returns:
        List of recent memories ordered by recency with semantic tags
    """
    logger.info(f"Getting recent context for project: {project_id}")
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from src.db.base import async_session
        
        async with async_session() as session:
            vector_store = VectorStore(session)
            
            memories = await vector_store.get_recent_memories(
                project_id=project_id,
                memory_type=memory_type,
                agent_id=agent_id,
                analysis_id=analysis_id,
                limit=limit,
                tag_memories=tag_memories
            )
            
            # Group memories by tag for better organization
            if memories:
                grouped = {}
                for memory in memories:
                    tag = memory.get("tag", "other")
                    if tag not in grouped:
                        grouped[tag] = []
                    grouped[tag].append(memory)
                
                return {
                    "memories": memories,
                    "grouped_by_tag": grouped
                }
            
            return {"memories": memories}
            
    except Exception as e:
        logger.error(f"Error getting recent context: {str(e)}")
        return {"error": str(e), "memories": []}

@tool(return_direct=False)
async def summarize_memories(
    memories: List[Dict[str, Any]],
    project_id: int
) -> Dict[str, Any]:
    """
    Generate a summary of a group of memories.
    
    Args:
        memories: List of memory objects or memory IDs to summarize
        project_id: The ID of the project
        
    Returns:
        A summary of the memories
    """
    logger.info(f"Summarizing {len(memories)} memories")
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from src.db.base import async_session
        
        async with async_session() as session:
            vector_store = VectorStore(session)
            
            # If we received memory IDs instead of full memory objects,
            # we need to fetch the full memories first
            if isinstance(memories[0], int) or isinstance(memories[0], str) and memories[0].isdigit():
                # Convert to list of integers if they're strings
                memory_ids = [int(mem) if isinstance(mem, str) else mem for mem in memories]
                
                # Fetch the memories from the database
                q = """
                SELECT id, text, memory_type, timestamp, metadata, tag
                FROM agent_memories
                WHERE id = ANY(:memory_ids) AND project_id = :project_id
                """
                
                result = await session.execute(
                    text(q),
                    {"memory_ids": memory_ids, "project_id": project_id}
                )
                
                fetched_memories = []
                for row in result.mappings():
                    fetched_memories.append({
                        "id": row["id"],
                        "text": row["text"],
                        "memory_type": row["memory_type"],
                        "timestamp": row["timestamp"],
                        "metadata": row["metadata"] or {},
                        "tag": row["tag"]
                    })
                
                memories = fetched_memories
            
            # Generate the summary
            summary = await vector_store.summarize_memories(memories)
            
            return {
                "summary": summary,
                "memory_count": len(memories),
                "memory_ids": [mem.get("id") for mem in memories]
            }
            
    except Exception as e:
        logger.error(f"Error summarizing memories: {str(e)}")
        return {"error": str(e)}
