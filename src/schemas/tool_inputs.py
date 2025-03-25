from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field

class DocumentSearchInput(BaseModel):
    """Input schema for document_search tool"""
    query: str = Field(..., description="The search query to find relevant documents")

class GenerateInsightInput(BaseModel):
    """Input schema for generate_insight tool"""
    text: str = Field(..., description="The text to analyze for insights")
    approach: str = Field(
        "thematic", 
        description="The analytical approach to use (e.g., 'thematic', 'grounded theory')"
    )

class SentimentAnalysisInput(BaseModel):
    """Input schema for sentiment_analysis tool"""
    text: str = Field(..., description="The text to analyze for sentiment")

class ThemeClusterInput(BaseModel):
    """Input schema for theme_cluster tool"""
    excerpts: List[str] = Field(..., description="List of text excerpts to cluster by theme")

class LLMRouterInput(BaseModel):
    """Input schema for llm_router tool"""
    query: str = Field(..., description="The query to determine which tool to use")

class RetrieveMemoriesInput(BaseModel):
    """Input schema for retrieve_memories tool"""
    query: str = Field(..., description="The query to find relevant memories")
    project_id: int = Field(..., description="The project ID to search memories for")
    memory_type: Optional[str] = Field(None, description="Type of memory to retrieve")
    agent_id: Optional[int] = Field(None, description="Filter by agent ID")
    analysis_id: Optional[int] = Field(None, description="Filter by analysis ID")
    k: int = Field(5, description="Number of memories to retrieve")

class StoreMemoryInput(BaseModel):
    """Input schema for store_memory tool"""
    text: str = Field(..., description="The text to store as a memory")
    project_id: int = Field(..., description="The project ID to associate with the memory")
    memory_type: str = Field("session", description="Type of memory (session, long_term, preference)")
    agent_id: Optional[int] = Field(None, description="The agent ID")
    analysis_id: Optional[int] = Field(None, description="The analysis ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class GetRecentContextInput(BaseModel):
    """Input schema for get_recent_context tool"""
    project_id: int = Field(..., description="The project ID to get context for")
    memory_type: Optional[str] = Field(None, description="Type of memory to retrieve")
    agent_id: Optional[int] = Field(None, description="Filter by agent ID")
    analysis_id: Optional[int] = Field(None, description="Filter by analysis ID")
    limit: int = Field(5, description="Maximum number of memories to retrieve")

class SummarizeMemoryInput(BaseModel):
    """Input schema for summarize_memory tool"""
    memories: List[Dict[str, Any]] = Field(..., description="List of memories to summarize, each containing text, tags, score, etc.")

class SentimentOutput(BaseModel):
    """Output schema for sentiment_analysis tool"""
    sentiment: Literal["positive", "negative", "neutral"] = Field(..., description="The sentiment classification")
    confidence: float = Field(..., description="Confidence score of the sentiment analysis")

class ThemeClusterOutput(BaseModel):
    """Output schema for theme_cluster tool"""
    clusters: List[Dict[str, Any]] = Field(..., description="List of theme clusters")

class InsightOutput(BaseModel):
    """Output schema for generate_insight tool"""
    insights: List[Dict[str, str]] = Field(..., description="List of insights extracted from the text")

class DocumentSearchOutput(BaseModel):
    """Output schema for document_search tool"""
    documents: List[Dict[str, Any]] = Field(..., description="List of relevant document chunks")

class LLMRouterOutput(BaseModel):
    """Output schema for llm_router tool"""
    tool: str = Field(..., description="The suggested tool to use")
    rationale: str = Field(..., description="Explanation for why this tool should be used")

class MemoriesOutput(BaseModel):
    """Output schema for memory retrieval tools"""
    memories: List[Dict[str, Any]] = Field(..., description="List of retrieved memories")
    error: Optional[str] = Field(None, description="Error message if retrieval failed")

class StoreMemoryOutput(BaseModel):
    """Output schema for store_memory tool"""
    status: str = Field(..., description="Status of the memory storage operation")
    memory_id: Optional[int] = Field(None, description="ID of the stored memory")
    message: str = Field(..., description="Detailed message about the operation")
    error: Optional[str] = Field(None, description="Error message if storage failed")

class SummarizeMemoryOutput(BaseModel):
    """Output schema for summarize_memory tool"""
    summary: str = Field(..., description="A concise summary synthesizing the most relevant ideas from the memories")
    error: Optional[str] = Field(None, description="Error message if summarization failed")
