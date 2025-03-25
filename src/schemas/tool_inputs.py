
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
