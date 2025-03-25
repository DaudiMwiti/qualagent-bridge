
from typing import List, Dict, Any
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from src.schemas.tool_inputs import DocumentSearchInput, DocumentSearchOutput
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

# This is a mock vector store for development
# In production, this would be replaced with a real vector store like pgvector
MOCK_DOCUMENTS = [
    {
        "id": "doc1",
        "text": "Participants frequently mentioned feeling overwhelmed by the user interface. One participant said, 'There are just too many buttons and options.'",
        "metadata": {"source": "interview_1", "page": 3}
    },
    {
        "id": "doc2",
        "text": "The focus group revealed positive sentiment about the mobile experience. A participant noted, 'The app feels intuitive and responsive.'",
        "metadata": {"source": "focus_group_2", "page": 7}
    },
    {
        "id": "doc3",
        "text": "Survey results indicated mixed feelings about pricing. 42% found it 'reasonable', while 31% thought it was 'too expensive'.",
        "metadata": {"source": "survey_results", "page": 12}
    },
    {
        "id": "doc4",
        "text": "The journey mapping exercise revealed pain points during the onboarding process. Multiple users struggled with account verification.",
        "metadata": {"source": "journey_map", "page": 2}
    },
    {
        "id": "doc5",
        "text": "Consistent feedback across demographics highlighted concerns about data privacy and security of personal information.",
        "metadata": {"source": "interview_series", "page": 15}
    }
]

@tool(return_direct=False)
async def document_search(query: str) -> Dict[str, Any]:
    """
    Search through qualitative documents for relevant information.
    
    Args:
        query: The search query to find relevant documents.
        
    Returns:
        A list of relevant document chunks.
    """
    logger.info(f"Performing document search with query: {query}")
    
    try:
        # In a real implementation, this would use vector search
        # For now, we'll use a simple keyword matching approach
        embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        
        # Get embedding for the query
        query_embedding = await embeddings.aembed_query(query)
        
        # Here we would normally search the vector DB
        # For the mock implementation, we'll just return documents that contain any words from the query
        query_words = query.lower().split()
        matched_docs = []
        
        for doc in MOCK_DOCUMENTS:
            doc_text = doc["text"].lower()
            if any(word in doc_text for word in query_words):
                matched_docs.append(doc)
        
        # If no exact matches, return some samples
        if not matched_docs and MOCK_DOCUMENTS:
            matched_docs = MOCK_DOCUMENTS[:2]  # Return first two as samples
            
        result = {
            "documents": matched_docs
        }
        
        logger.info(f"Document search returned {len(matched_docs)} results")
        return result
        
    except Exception as e:
        logger.error(f"Error in document_search: {str(e)}")
        return {"documents": [], "error": str(e)}
