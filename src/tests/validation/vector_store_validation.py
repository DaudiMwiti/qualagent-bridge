
import asyncio
import sys
import json
import argparse
from typing import Dict, Any, List

sys.path.append(".")  # Add project root to path

from src.db.base import async_session
from src.utils.vector_store import VectorStore
from src.agents.tools.document_search import document_search
from src.tests.utils.test_helpers import add_test_documents, clean_test_documents

VALIDATION_CRITERIA = {
    "average_latency_ms": 200,  # Target: < 200ms average latency
    "max_concurrent_requests": 15,  # Target: Handle 15+ concurrent requests
    "top1_accuracy": 0.8,  # Target: 80%+ top-1 accuracy
    "extension_installed": True  # pgvector extension must be installed
}

async def validate_vector_store(project_id: int) -> Dict[str, Any]:
    """
    Validate that the vector store implementation meets the requirements
    
    Args:
        project_id: Project ID to use for testing
        
    Returns:
        Dictionary with validation results
    """
    print("Starting vector store validation...")
    validation_results = {
        "passed": True,
        "criteria": {},
        "errors": []
    }
    
    # Add test documents
    print("Adding test documents...")
    doc_ids = await add_test_documents(project_id, count=50)
    
    try:
        # 1. Validate pgvector extension is installed
        print("Validating pgvector extension...")
        async with async_session() as session:
            try:
                vector_store = VectorStore(session)
                await vector_store.setup_db_extensions()
                validation_results["criteria"]["extension_installed"] = {
                    "result": True,
                    "target": VALIDATION_CRITERIA["extension_installed"],
                    "passed": True
                }
            except Exception as e:
                validation_results["criteria"]["extension_installed"] = {
                    "result": False,
                    "target": VALIDATION_CRITERIA["extension_installed"],
                    "passed": False,
                    "error": str(e)
                }
                validation_results["passed"] = False
                validation_results["errors"].append(f"pgvector extension error: {str(e)}")
        
        # 2. Validate search accuracy
        print("Validating search accuracy...")
        known_pairs = [
            {"query": "user interface design", "expected_text": "user interface"},
            {"query": "data privacy concerns", "expected_text": "privacy"},
            {"query": "mobile app performance", "expected_text": "performance"},
            {"query": "pricing feedback", "expected_text": "pricing"}
        ]
        
        correct_top1 = 0
        for pair in known_pairs:
            result = await document_search(
                query=pair["query"],
                project_id=project_id,
                limit=1
            )
            
            if result["documents"] and pair["expected_text"].lower() in result["documents"][0]["text"].lower():
                correct_top1 += 1
        
        accuracy = correct_top1 / len(known_pairs)
        validation_results["criteria"]["top1_accuracy"] = {
            "result": accuracy,
            "target": VALIDATION_CRITERIA["top1_accuracy"],
            "passed": accuracy >= VALIDATION_CRITERIA["top1_accuracy"]
        }
        
        if accuracy < VALIDATION_CRITERIA["top1_accuracy"]:
            validation_results["passed"] = False
            validation_results["errors"].append(f"Search accuracy ({accuracy*100:.1f}%) below target ({VALIDATION_CRITERIA['top1_accuracy']*100:.1f}%)")
        
        # 3. Validate latency
        print("Validating search latency...")
        from src.tests.benchmarks.vector_search_benchmark import run_document_search_benchmark
        
        latency_results = await run_document_search_benchmark(
            project_id=project_id,
            test_doc_count=50,  # Use existing documents
            query_count=10,
            concurrency_levels=[1]  # Just need single-thread performance
        )
        
        average_latency = latency_results["results"]["concurrency_1"]["avg_latency_ms"]
        validation_results["criteria"]["average_latency_ms"] = {
            "result": average_latency,
            "target": VALIDATION_CRITERIA["average_latency_ms"],
            "passed": average_latency < VALIDATION_CRITERIA["average_latency_ms"]
        }
        
        if average_latency >= VALIDATION_CRITERIA["average_latency_ms"]:
            validation_results["passed"] = False
            validation_results["errors"].append(f"Average latency ({average_latency:.1f}ms) above target ({VALIDATION_CRITERIA['average_latency_ms']}ms)")
        
        # 4. Validate concurrency handling
        print("Validating concurrent request handling...")
        # Test with a high concurrency level
        concurrency_results = await run_document_search_benchmark(
            project_id=project_id,
            test_doc_count=50,  # Use existing documents
            query_count=20,
            concurrency_levels=[VALIDATION_CRITERIA["max_concurrent_requests"]]
        )
        
        # Check if we got any errors during concurrent execution
        concurrent_success = "error" not in concurrency_results
        validation_results["criteria"]["max_concurrent_requests"] = {
            "result": VALIDATION_CRITERIA["max_concurrent_requests"],
            "target": VALIDATION_CRITERIA["max_concurrent_requests"],
            "passed": concurrent_success
        }
        
        if not concurrent_success:
            validation_results["passed"] = False
            validation_results["errors"].append(f"Failed to handle {VALIDATION_CRITERIA['max_concurrent_requests']} concurrent requests")
        
        return validation_results
        
    finally:
        # Clean up test documents
        print("Cleaning up test documents...")
        await clean_test_documents(doc_ids)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate vector store implementation")
    parser.add_argument("--project_id", type=int, required=True, help="Project ID to use for testing")
    parser.add_argument("--output", type=str, help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    async def main():
        validation_results = await validate_vector_store(project_id=args.project_id)
        
        # Print results
        print("\nValidation Results:")
        print(f"Overall: {'PASSED' if validation_results['passed'] else 'FAILED'}")
        
        for criterion, result in validation_results["criteria"].items():
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {criterion}: {result['result']} (target: {result['target']})")
        
        if validation_results["errors"]:
            print("\nErrors:")
            for error in validation_results["errors"]:
                print(f"- {error}")
        
        if args.output:
            with open(args.output, "w") as f:
                json.dump(validation_results, f, indent=2)
        
        print("\nValidation complete!")
    
    asyncio.run(main())
