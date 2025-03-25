
import asyncio
import time
import statistics
import random
import sys
import json
import argparse

sys.path.append(".")  # Add project root to path

from src.db.base import async_session
from src.services.cache import CacheService
from src.agents.orchestrator import AnalysisOrchestrator

async def benchmark_cache_performance():
    """Benchmark the performance of the caching layer"""
    print("Running cache performance benchmark...")
    
    # Create a session and cache service
    async with async_session() as session:
        cache = CacheService(session)
        
        # Test data with different sizes
        test_data = {
            "small": {"data": "x" * 100},
            "medium": {"data": "x" * 10000},
            "large": {"data": "x" * 100000}
        }
        
        results = {}
        
        # Benchmark set operations
        for size, data in test_data.items():
            # Generate unique keys
            keys = [f"benchmark:set:{size}:{i}" for i in range(50)]
            
            # Measure set operations
            start_time = time.time()
            for key in keys:
                await cache.set(key, data)
            total_time = time.time() - start_time
            
            results[f"set_{size}"] = {
                "operations": len(keys),
                "total_time": total_time,
                "avg_time": total_time / len(keys)
            }
            
            print(f"SET {size}: {len(keys)} ops in {total_time:.3f}s, avg: {(total_time / len(keys))*1000:.2f}ms")
        
        # Benchmark get operations (cache hits)
        for size, data in test_data.items():
            # Use existing keys
            keys = [f"benchmark:set:{size}:{i}" for i in range(50)]
            
            # Measure get operations
            start_time = time.time()
            for key in keys:
                await cache.get(key)
            total_time = time.time() - start_time
            
            results[f"get_hit_{size}"] = {
                "operations": len(keys),
                "total_time": total_time,
                "avg_time": total_time / len(keys)
            }
            
            print(f"GET (hit) {size}: {len(keys)} ops in {total_time:.3f}s, avg: {(total_time / len(keys))*1000:.2f}ms")
        
        # Benchmark get operations (cache misses)
        for size in test_data.keys():
            # Use non-existent keys
            keys = [f"benchmark:nonexistent:{size}:{i}" for i in range(50)]
            
            # Measure get operations
            start_time = time.time()
            for key in keys:
                await cache.get(key)
            total_time = time.time() - start_time
            
            results[f"get_miss_{size}"] = {
                "operations": len(keys),
                "total_time": total_time,
                "avg_time": total_time / len(keys)
            }
            
            print(f"GET (miss) {size}: {len(keys)} ops in {total_time:.3f}s, avg: {(total_time / len(keys))*1000:.2f}ms")
        
        # Clean up benchmark data
        print("Cleaning up benchmark data...")
        for size in test_data.keys():
            for i in range(50):
                await cache.delete(f"benchmark:set:{size}:{i}")
        
        return results

async def benchmark_orchestrator_caching():
    """Benchmark the caching in the orchestrator"""
    print("\nBenchmarking orchestrator with caching...")
    
    # Sample test data
    test_data = {
        "interviews": [
            {
                "id": "interview-1",
                "text": "User mentioned they found the interface confusing. The buttons were not clearly labeled and navigation was difficult.",
                "metadata": {"participant_id": "P001"}
            },
            {
                "id": "interview-2",
                "text": "The search functionality rarely returned relevant results. User tried searching for 'payment methods' but got blog articles instead.",
                "metadata": {"participant_id": "P002"}
            }
        ],
        "parameters": {
            "research_objective": "Identify usability issues"
        }
    }
    
    # Create orchestrator with default config
    orchestrator = AnalysisOrchestrator({
        "system_prompt": "You are a UX researcher analyzing interview data.",
        "temperature": 0.2,
        "max_tool_calls": 1  # Limit to speed up the test
    })
    
    # Run without cache first (cold start)
    print("Running without cache (first run)...")
    start_time = time.time()
    no_cache_results = await orchestrator.run_analysis(test_data)
    uncached_time = time.time() - start_time
    print(f"Without cache: {uncached_time:.3f}s")
    
    # Run with cache (should be faster)
    print("Running with cache (second run)...")
    start_time = time.time()
    cached_results = await orchestrator.run_analysis(test_data)
    cached_time = time.time() - start_time
    print(f"With cache: {cached_time:.3f}s")
    
    # Calculate improvement
    if uncached_time > 0:
        improvement = ((uncached_time - cached_time) / uncached_time) * 100
        print(f"Cache improvement: {improvement:.1f}% faster")
    
    return {
        "uncached_time": uncached_time,
        "cached_time": cached_time,
        "improvement_percent": improvement if uncached_time > 0 else 0
    }

async def main():
    parser = argparse.ArgumentParser(description="Cache benchmarking tool")
    parser.add_argument("--full", action="store_true", help="Run full benchmark suite")
    args = parser.parse_args()
    
    # Run basic cache performance tests
    cache_results = await benchmark_cache_performance()
    
    # Only run the more expensive orchestrator test if requested
    if args.full:
        orchestrator_results = await benchmark_orchestrator_caching()
        
        # Combine results
        results = {
            "cache_operations": cache_results,
            "orchestrator": orchestrator_results
        }
    else:
        results = {
            "cache_operations": cache_results
        }
    
    # Save results to file
    with open("cache_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nBenchmark complete! Results saved to cache_benchmark_results.json")

if __name__ == "__main__":
    asyncio.run(main())
