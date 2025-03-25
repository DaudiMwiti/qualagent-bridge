
import pytest
import asyncio
from pydantic import BaseModel, Field
from src.services.param_extractor import param_extractor
from src.schemas.tool_inputs import (
    DocumentSearchInput,
    GenerateInsightInput,
    SentimentAnalysisInput,
    ThemeClusterInput
)

@pytest.mark.asyncio
async def test_extract_document_search_params():
    """Test parameter extraction for document search"""
    # Simple input text
    text = "Please search for documents about user interface problems"
    
    # Extract parameters
    params, _ = await param_extractor.extract_with_fallback(
        text=text,
        schema=DocumentSearchInput,
        default_values={"query": "user interface"}
    )
    
    # Verify extraction
    assert isinstance(params, DocumentSearchInput)
    assert "user interface" in params.query.lower()
    assert "problem" in params.query.lower()

@pytest.mark.asyncio
async def test_extract_sentiment_params():
    """Test parameter extraction for sentiment analysis"""
    # Sample text with sentiment information
    text = """
    Users expressed frustration with slow load times, saying 'the app feels sluggish'.
    Many comments mentioned that the interface is confusing.
    """
    
    # Extract parameters
    params, _ = await param_extractor.extract_with_fallback(
        text=text,
        schema=SentimentAnalysisInput,
        default_values={"text": "Default text"}
    )
    
    # Verify extraction
    assert isinstance(params, SentimentAnalysisInput)
    assert "frustration" in params.text.lower()
    assert "sluggish" in params.text.lower()
    assert "confusing" in params.text.lower()

@pytest.mark.asyncio
async def test_extract_with_validation_error():
    """Test parameter extraction with validation errors and fallback"""
    # Define a schema with required fields
    class TestSchema(BaseModel):
        required_field: str = Field(..., description="This field is required")
        numeric_field: int = Field(..., description="This must be a number")
    
    # Input text missing required information
    text = "This text doesn't contain the required information"
    
    # Extract with fallback
    params, used_extraction = await param_extractor.extract_with_fallback(
        text=text,
        schema=TestSchema,
        default_values={"required_field": "default", "numeric_field": 42}
    )
    
    # Check that fallback was used
    assert not used_extraction
    assert params.required_field == "default"
    assert params.numeric_field == 42

@pytest.mark.asyncio
async def test_theme_cluster_extraction():
    """Test extraction of theme cluster parameters"""
    # Input text with multiple paragraphs/excerpts
    text = """
    We should analyze these excerpts for themes:
    
    "The mobile app crashes whenever I try to upload photos."
    "Why does the app freeze when I'm trying to share content?"
    "The performance on Android devices is terrible."
    "I can't even upload a simple image without it crashing."
    """
    
    # Extract parameters
    params, extraction_used = await param_extractor.extract_with_fallback(
        text=text,
        schema=ThemeClusterInput,
        default_values={"excerpts": ["Default excerpt"]}
    )
    
    # Verify extraction
    assert isinstance(params, ThemeClusterInput)
    assert len(params.excerpts) >= 3
    assert any("crashes" in excerpt for excerpt in params.excerpts)
    assert any("performance" in excerpt for excerpt in params.excerpts)

if __name__ == "__main__":
    asyncio.run(test_extract_document_search_params())
    asyncio.run(test_extract_sentiment_params())
    asyncio.run(test_extract_with_validation_error())
    asyncio.run(test_theme_cluster_extraction())
    print("All tests completed successfully!")
