
#!/usr/bin/env python3
import asyncio
import sys
import os
import argparse
import json
from datetime import datetime

sys.path.append(".")  # Add project root to path

async def run_all_validations(project_id: int, output_dir: str = "validation_results"):
    """Run all validation tests for Phase 1 implementation"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Import the validation modules
    from src.tests.validation.vector_store_validation import validate_vector_store
    from src.tests.benchmarks.vector_search_benchmark import run_document_search_benchmark
    from src.scripts.optimize_pgvector import optimize_pgvector_indexes
    
    print("\n======== PHASE 1 VALIDATION ========")
    print("Running comprehensive validation suite")
    print("=====================================\n")
    
    # Step 1: Try to optimize pgvector indexes
    print("\n--- Step 1: Optimizing pgvector indexes ---")
    try:
        await optimize_pgvector_indexes()
        print("✅ Optimization complete")
    except Exception as e:
        print(f"❌ Optimization failed: {str(e)}")
    
    # Step 2: Run vector store validation
    print("\n--- Step 2: Running vector store validation ---")
    validation_results = await validate_vector_store(project_id)
    
    validation_file = f"{output_dir}/validation_{timestamp}.json"
    with open(validation_file, "w") as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"✅ Validation results saved to {validation_file}")
    
    # Step 3: Run detailed benchmarks
    print("\n--- Step 3: Running detailed performance benchmarks ---")
    benchmark_results = await run_document_search_benchmark(
        project_id=project_id,
        test_doc_count=100,
        query_count=50,
        concurrency_levels=[1, 5, 10, 20, 50]
    )
    
    benchmark_file = f"{output_dir}/benchmark_{timestamp}.json"
    with open(benchmark_file, "w") as f:
        json.dump(benchmark_results, f, indent=2)
    
    print(f"✅ Benchmark results saved to {benchmark_file}")
    
    # Print summary
    print("\n======== VALIDATION SUMMARY ========")
    print(f"Overall validation: {'PASSED' if validation_results['passed'] else 'FAILED'}")
    
    if validation_results["passed"]:
        print("\n✅ Phase 1 implementation meets all requirements!")
        print("Ready to proceed to Phase 2.")
    else:
        print("\n❌ Phase 1 implementation needs improvement:")
        for error in validation_results["errors"]:
            print(f"  - {error}")
        print("\nPlease fix the issues before proceeding to Phase 2.")
    
    print("\n=====================================")
    
    return validation_results["passed"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Phase 1 validation suite")
    parser.add_argument("--project_id", type=int, required=True, help="Project ID to use for testing")
    parser.add_argument("--output", type=str, default="validation_results", help="Output directory for results")
    
    args = parser.parse_args()
    
    success = asyncio.run(run_all_validations(args.project_id, args.output))
    
    sys.exit(0 if success else 1)
