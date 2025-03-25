
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
    k: int = 5
) -> Dict[str, Any]:
    """
    Retrieve relevant memories based on semantic similarity to the query.
    
    Args:
        query: The query to find relevant memories
        project_id: The ID of the project
        memory_type: Optional filter for memory type (session, long_term, preference)
        agent_id: Optional filter for specific agent
        analysis_id: Optional filter for specific analysis
        k: Number of memories to retrieve
        
    Returns:
        List of relevant memories with their similarity scores
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
                k=k
            )
            
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
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store a new memory in the agent's memory system.
    
    Args:
        text: The text to store as a memory
        project_id: The ID of the project
        memory_type: Type of memory (session, long_term, preference)
        agent_id: Optional ID of the agent
        analysis_id: Optional ID of the analysis
        metadata: Optional metadata to associate with the memory
        
    Returns:
        Confirmation of memory storage
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
                metadata=metadata
            )
            
            return {
                "status": "success",
                "memory_id": memory_id,
                "message": "Memory stored successfully"
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
    limit: int = 5
) -> Dict[str, Any]:
    """
    Get the most recent memories to provide context for the current analysis.
    
    Args:
        project_id: The ID of the project
        memory_type: Optional filter for memory type
        agent_id: Optional filter for specific agent
        analysis_id: Optional filter for specific analysis
        limit: Maximum number of memories to retrieve
        
    Returns:
        List of recent memories ordered by recency
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
                limit=limit
            )
            
            return {"memories": memories}
            
    except Exception as e:
        logger.error(f"Error getting recent context: {str(e)}")
        return {"error": str(e), "memories": []}
