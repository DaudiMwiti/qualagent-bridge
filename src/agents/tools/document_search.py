
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.schemas.tool_inputs import DocumentSearchInput, DocumentSearchOutput
from src.core.config import settings
from src.db.base import async_session
from src.utils.vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)

@tool(return_direct=False)
async def document_search(
    query: str, 
    project_id: int = None, 
    limit: int = 5, 
    auto_tag: bool = True,
    offset: int = 0,
    min_score: float = 0.0
) -> Dict[str, Any]:
    """
    Search through qualitative documents for relevant information using vector similarity.
    
    Args:
        query: The search query to find relevant documents.
        project_id: The ID of the project to search within.
        limit: Maximum number of results to return.
        auto_tag: Whether to automatically tag the results.
        offset: Number of results to skip for pagination.
        min_score: Minimum similarity score threshold.
        
    Returns:
        A dictionary containing relevant document chunks with similarity scores and semantic tags.
    """
    logger.info(f"Performing document search with query: {query}")
    
    try:
        # Initialize the embeddings model
        embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        
        # Use the vector store to perform similarity search
        async with async_session() as session:
            vector_store = VectorStore(session)
            
            # Check if pgvector extension is installed
            try:
                await session.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
                extension_exists = True
            except Exception as e:
                logger.error(f"Error checking pgvector extension: {str(e)}")
                extension_exists = False
                
            if not extension_exists:
                logger.warning("pgvector extension not found, attempting to create it")
                try:
                    await vector_store.setup_db_extensions()
                except Exception as setup_error:
                    logger.error(f"Failed to setup pgvector extension: {str(setup_error)}")
                    return {
                        "documents": [],
                        "error": "Vector database not properly configured. Please contact an administrator.",
                        "metadata": {
                            "total_count": 0,
                            "offset": offset,
                            "limit": limit
                        }
                    }
            
            # Validate project_id
            if not project_id:
                logger.warning("No project_id provided for document search")
                return {
                    "documents": [],
                    "error": "Project ID is required for document search",
                    "metadata": {
                        "total_count": 0,
                        "offset": offset,
                        "limit": limit
                    }
                }
            
            # Get total count for pagination metadata
            count_query = """
            SELECT COUNT(*) 
            FROM vectors 
            WHERE project_id = :project_id
            """
            
            count_result = await session.execute(
                text(count_query),
                {"project_id": project_id}
            )
            total_count = count_result.scalar() or 0
            
            # Perform the actual similarity search
            results = await vector_store.similarity_search(
                query=query,
                project_id=project_id,
                k=limit,
                table_name="vectors",
                offset=offset,
                min_score=min_score
            )
            
            # Add tags to results if requested
            if auto_tag and results:
                for doc in results:
                    # Only tag if not already tagged
                    if "tag" not in doc or not doc["tag"]:
                        doc["tag"] = await vector_store.tag_memory(doc["text"])
            
            logger.info(f"Document search returned {len(results)} results out of {total_count} total")
            
            return {
                "documents": results,
                "metadata": {
                    "total_count": total_count,
                    "offset": offset,
                    "limit": limit
                }
            }
        
    except Exception as e:
        logger.error(f"Error in document_search: {str(e)}")
        return {
            "documents": [],
            "error": str(e),
            "metadata": {
                "total_count": 0,
                "offset": offset,
                "limit": limit
            }
        }
