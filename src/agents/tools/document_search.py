
from typing import List, Dict, Any
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.tool_inputs import DocumentSearchInput, DocumentSearchOutput
from src.core.config import settings
from src.db.base import async_session
from src.utils.vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)

@tool(return_direct=False)
async def document_search(query: str, project_id: int = None, limit: int = 5) -> Dict[str, Any]:
    """
    Search through qualitative documents for relevant information using vector similarity.
    
    Args:
        query: The search query to find relevant documents.
        project_id: The ID of the project to search within.
        limit: Maximum number of results to return.
        
    Returns:
        A list of relevant document chunks with similarity scores.
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
            
            # If no project_id is provided, we'll need to handle that
            if not project_id:
                # For now, return mock data with a warning
                logger.warning("No project_id provided for document search")
                return {
                    "documents": [
                        {
                            "id": "mock_id",
                            "text": "This is a mock result. Please provide a project_id for actual vector search.",
                            "metadata": {"source": "mock", "warning": "No project_id provided"},
                            "score": 0.0
                        }
                    ],
                    "warning": "No project_id provided. Using mock data."
                }
            
            # Perform the actual similarity search
            results = await vector_store.similarity_search(
                query=query,
                project_id=project_id,
                k=limit,
                table_name="vectors"  # This is our documents table
            )
            
            logger.info(f"Document search returned {len(results)} results")
            return {"documents": results}
        
    except Exception as e:
        logger.error(f"Error in document_search: {str(e)}")
        return {
            "documents": [],
            "error": str(e)
        }

