
import asyncio
import random
import time
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import async_session
from src.utils.vector_store import VectorStore
from langchain_openai import OpenAIEmbeddings
from src.core.config import settings

async def generate_test_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of test texts"""
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model="text-embedding-3-small"
    )
    
    return [await embeddings.aembed_query(text) for text in texts]

async def add_test_documents(project_id: int, count: int = 10) -> List[int]:
    """Add test documents to the vector store for testing purposes"""
    test_texts = [
        f"Test document about user interface design iteration {i}" for i in range(count//4)
    ] + [
        f"Test document about data privacy concerns example {i}" for i in range(count//4)
    ] + [
        f"Test document about mobile app performance issue {i}" for i in range(count//4)
    ] + [
        f"Test document about pricing feedback from customer {i}" for i in range(count//4)
    ]
    
    doc_ids = []
    async with async_session() as session:
        vector_store = VectorStore(session)
        
        # Ensure pgvector extension exists
        await vector_store.setup_db_extensions()
        
        # Add test documents
        for text in test_texts:
            doc_id = await vector_store.add_memory(
                text=text,
                project_id=project_id,
                memory_type="test",
                auto_tag=False
            )
            doc_ids.append(doc_id)
    
    return doc_ids

async def clean_test_documents(doc_ids: List[int]) -> None:
    """Remove test documents from the database"""
    async with async_session() as session:
        for doc_id in doc_ids:
            await session.execute(f"DELETE FROM agent_memories WHERE id = {doc_id}")
        await session.commit()

async def measure_query_latency(
    query_func, 
    queries: List[str], 
    concurrency: int = 1
) -> Dict[str, float]:
    """Measure latency of search queries"""
    start_time = time.time()
    
    # For sequential testing
    if concurrency == 1:
        results = []
        for query in queries:
            result = await query_func(query)
            results.append(result)
    # For concurrent testing
    else:
        chunks = [queries[i:i+concurrency] for i in range(0, len(queries), concurrency)]
        results = []
        for chunk in chunks:
            tasks = [query_func(q) for q in chunk]
            chunk_results = await asyncio.gather(*tasks)
            results.extend(chunk_results)
    
    end_time = time.time()
    
    # Calculate statistics
    total_time = end_time - start_time
    avg_latency = (total_time / len(queries)) * 1000  # in ms
    
    return {
        "total_queries": len(queries),
        "total_time_seconds": total_time,
        "avg_latency_ms": avg_latency,
        "results_count": sum(len(r.get("documents", [])) for r in results)
    }
