
import pytest
import sys
import os
import time
from typing import List, Dict, Any

sys.path.append(".")  # Add project root to path

from src.agents.tools.document_search import document_search
from src.utils.vector_store import VectorStore
from src.db.base import async_session
from src.tests.utils.test_helpers import add_test_documents, clean_test_documents

# Test project ID (should be a real project in your dev/test environment)
TEST_PROJECT_ID = 1

@pytest.fixture
async def test_docs():
    """Create test documents and clean them up after the test"""
    doc_ids = await add_test_documents(TEST_PROJECT_ID, count=20)
    yield doc_ids
    await clean_test_documents(doc_ids)

@pytest.mark.asyncio
async def test_document_search_returns_results(test_docs):
    """Test that the document search returns results"""
    # Test with a query that should match the test documents
    result = await document_search(
        query="user interface design",
        project_id=TEST_PROJECT_ID,
        limit=5
    )
    
    # Assertions
    assert "documents" in result
    assert len(result["documents"]) > 0
    assert "metadata" in result
    assert result["metadata"]["total_count"] > 0
    
    # Check document structure
    doc = result["documents"][0]
    assert "id" in doc
    assert "text" in doc
    assert "score" in doc
    assert "user interface" in doc["text"].lower()
    
    # Verify semantic search works - top result should have high relevance
    assert doc["score"] > 0.5  # Good similarity score

@pytest.mark.asyncio
async def test_document_search_respects_limit(test_docs):
    """Test that the limit parameter is respected"""
    limit = 3
    result = await document_search(
        query="test document",
        project_id=TEST_PROJECT_ID,
        limit=limit
    )
    
    assert len(result["documents"]) <= limit

@pytest.mark.asyncio
async def test_document_search_pagination(test_docs):
    """Test that pagination works correctly"""
    # First page
    limit = 5
    page1 = await document_search(
        query="test document",
        project_id=TEST_PROJECT_ID,
        limit=limit,
        offset=0
    )
    
    # Second page
    page2 = await document_search(
        query="test document",
        project_id=TEST_PROJECT_ID,
        limit=limit,
        offset=limit
    )
    
    # Assertions
    assert len(page1["documents"]) == limit
    assert page1["metadata"]["offset"] == 0
    assert page1["metadata"]["limit"] == limit
    
    # Check that pages don't overlap
    page1_ids = [doc["id"] for doc in page1["documents"]]
    page2_ids = [doc["id"] for doc in page2["documents"]]
    assert not any(doc_id in page1_ids for doc_id in page2_ids)

@pytest.mark.asyncio
async def test_document_search_min_score_filter(test_docs):
    """Test that the min_score parameter filters results correctly"""
    # Get baseline results
    baseline = await document_search(
        query="completely unrelated query about space travel",
        project_id=TEST_PROJECT_ID,
        limit=10,
        min_score=0.0  # No minimum score
    )
    
    # Get filtered results
    filtered = await document_search(
        query="completely unrelated query about space travel",
        project_id=TEST_PROJECT_ID,
        limit=10,
        min_score=0.7  # High minimum score
    )
    
    # Verify filtering worked
    assert len(baseline["documents"]) > 0
    assert len(filtered["documents"]) <= len(baseline["documents"])
    
    # Check that all filtered results have scores above threshold
    if filtered["documents"]:
        assert all(doc["score"] >= 0.7 for doc in filtered["documents"])

@pytest.mark.asyncio
async def test_document_search_auto_tagging(test_docs):
    """Test that auto-tagging works correctly"""
    result = await document_search(
        query="user interface",
        project_id=TEST_PROJECT_ID,
        limit=3,
        auto_tag=True
    )
    
    # Verify tags were added
    for doc in result["documents"]:
        assert "tag" in doc
        assert doc["tag"] in ["observation", "emotion", "recommendation", 
                             "complaint", "idea", "other"]

@pytest.mark.asyncio
async def test_document_search_error_handling():
    """Test error handling with invalid project ID"""
    # Use non-existent project ID
    result = await document_search(
        query="test query",
        project_id=99999,  # Non-existent project
        limit=5
    )
    
    # Should return graceful error
    assert "documents" in result
    assert len(result["documents"]) == 0
    assert "error" in result
