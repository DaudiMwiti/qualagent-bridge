
import asyncio
import sys
import time
from typing import List, Dict, Any
import random
import json
import argparse

sys.path.append(".")  # Add project root to path

from src.agents.tools.document_search import document_search
from src.db.base import async_session
from src.tests.utils.test_helpers import (
    add_test_documents,
    clean_test_documents,
    measure_query_latency
)

# Test queries that represent common search patterns
TEST_QUERIES = [
    "user interface design issues",
    "privacy concerns with data",
    "mobile application performance",
    "customer feedback about pricing",
    "user experience improvements",
    "data security problems",
    "slow loading times in app",
    "competitive pricing analysis",
    "interface usability problems",
    "data protection regulations"
]

async def run_document_search_benchmark(
    project_id: int,
    test_doc_count: int = 100,
    query_count: int = 20,
    concurrency_levels: List[int] = [1, 5, 10, 20]
) -> Dict[str, Any]:
    """
    Run benchmarks on the document search functionality
    
    Args:
        project_id: Project ID to use for testing
        test_doc_count: Number of test documents to create
        query_count: Number of queries to run in each test
        concurrency_levels: List of concurrency levels to test
        
    Returns:
        Dictionary with benchmark results
    """
    print(f"Setting up test environment with {test_doc_count} documents...")
    
    # Add test documents
    doc_ids = await add_test_documents(project_id, test_doc_count)
    print(f"Added {len(doc_ids)} test documents to project {project_id}")
    
    try:
        # Generate test queries (with variations)
        queries = []
        for _ in range(query_count):
            base_query = random.choice(TEST_QUERIES)
            # Add slight variations to prevent caching effects
            variation = f"{base_query} {random.randint(1, 1000)}"
            queries.append(variation)
        
        results = {}
        
        # Test different concurrency levels
        for concurrency in concurrency_levels:
            print(f"\nTesting with concurrency level: {concurrency}")
            
            # Create a wrapper function for the document search
            async def search_wrapper(query: str) -> Dict[str, Any]:
                return await document_search(
                    query=query,
                    project_id=project_id,
                    limit=10,
                    auto_tag=False
                )
            
            # Measure latency
            latency_results = await measure_query_latency(
                search_wrapper,
                queries,
                concurrency=concurrency
            )
            
            print(f"Results for concurrency {concurrency}:")
            print(f"  Total queries: {latency_results['total_queries']}")
            print(f"  Total time: {latency_results['total_time_seconds']:.2f} seconds")
            print(f"  Average latency: {latency_results['avg_latency_ms']:.2f} ms")
            print(f"  Results returned: {latency_results['results_count']}")
            
            results[f"concurrency_{concurrency}"] = latency_results
        
        return {
            "test_document_count": test_doc_count,
            "query_count": query_count,
            "timestamp": time.time(),
            "results": results
        }
    
    finally:
        # Clean up test documents
        print("\nCleaning up test documents...")
        await clean_test_documents(doc_ids)
        print(f"Removed {len(doc_ids)} test documents")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run vector search benchmarks")
    parser.add_argument("--project_id", type=int, required=True, help="Project ID to use for testing")
    parser.add_argument("--docs", type=int, default=100, help="Number of test documents to create")
    parser.add_argument("--queries", type=int, default=20, help="Number of queries to run in each test")
    parser.add_argument("--output", type=str, help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    async def main():
        results = await run_document_search_benchmark(
            project_id=args.project_id,
            test_doc_count=args.docs,
            query_count=args.queries
        )
        
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
        
        print("\nBenchmark complete!")
    
    asyncio.run(main())
