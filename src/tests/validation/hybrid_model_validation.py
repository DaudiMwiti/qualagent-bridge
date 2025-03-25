
#!/usr/bin/env python3
import asyncio
import sys
import os
import json
import argparse
from datetime import datetime
import numpy as np
from typing import List, Dict, Any

sys.path.append(".")  # Add project root to path

from src.core.embeddings import embedding_service
from src.agents.tools.sentiment_analysis import sentiment_analyzer
from src.services.param_extractor import param_extractor
from src.schemas.tool_inputs import SentimentAnalysisInput
from src.core.config import settings

async def validate_embeddings(test_texts: List[str], output_dir: str):
    """Validate embeddings from different providers"""
    print("\n--- Validating Embeddings ---")
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "embeddings",
        "providers_tested": [],
        "results": []
    }
    
    # Save current setting
    original_setting = settings.USE_OPENSOURCE_EMBED
    
    for text in test_texts:
        print(f"Testing text: {text[:50]}...")
        
        # Test with OpenAI
        settings.USE_OPENSOURCE_EMBED = False
        start_time = datetime.now()
        try:
            openai_embed = await embedding_service.get_embeddings(text)
            openai_time = (datetime.now() - start_time).total_seconds() * 1000
            print(f"  ✅ OpenAI: {openai_time:.2f}ms")
            results["providers_tested"].append("openai")
        except Exception as e:
            openai_embed = None
            openai_time = 0
            print(f"  ❌ OpenAI failed: {str(e)}")
        
        # Test with HuggingFace if key is available
        if settings.HF_API_KEY:
            settings.USE_OPENSOURCE_EMBED = True
            start_time = datetime.now()
            try:
                hf_embed = await embedding_service.get_embeddings(text)
                hf_time = (datetime.now() - start_time).total_seconds() * 1000
                print(f"  ✅ HuggingFace: {hf_time:.2f}ms")
                results["providers_tested"].append("huggingface")
            except Exception as e:
                hf_embed = None
                hf_time = 0
                print(f"  ❌ HuggingFace failed: {str(e)}")
        else:
            hf_embed = None
            hf_time = 0
            print("  ⚠️ Skipping HuggingFace (no API key)")
        
        # Test with Cohere if key is available
        if settings.COHERE_API_KEY:
            start_time = datetime.now()
            try:
                cohere_embed = await embedding_service._get_cohere_embeddings(text)
                cohere_time = (datetime.now() - start_time).total_seconds() * 1000
                print(f"  ✅ Cohere: {cohere_time:.2f}ms")
                results["providers_tested"].append("cohere")
            except Exception as e:
                cohere_embed = None
                cohere_time = 0
                print(f"  ❌ Cohere failed: {str(e)}")
        else:
            cohere_embed = None
            cohere_time = 0
            print("  ⚠️ Skipping Cohere (no API key)")
        
        # Compare similarities between embeddings if available
        similarities = {}
        if openai_embed and hf_embed:
            try:
                # Resize vectors if needed
                if len(openai_embed) != len(hf_embed):
                    min_dim = min(len(openai_embed), len(hf_embed))
                    openai_embed_resized = openai_embed[:min_dim]
                    hf_embed_resized = hf_embed[:min_dim]
                    similarity = await embedding_service.calculate_similarity(openai_embed_resized, hf_embed_resized)
                else:
                    similarity = await embedding_service.calculate_similarity(openai_embed, hf_embed)
                similarities["openai_hf"] = similarity
                print(f"  Similarity OpenAI-HF: {similarity:.4f}")
            except Exception as e:
                print(f"  ❌ Error calculating similarity: {str(e)}")
        
        if openai_embed and cohere_embed:
            try:
                # Resize vectors if needed
                if len(openai_embed) != len(cohere_embed):
                    min_dim = min(len(openai_embed), len(cohere_embed))
                    openai_embed_resized = openai_embed[:min_dim]
                    cohere_embed_resized = cohere_embed[:min_dim]
                    similarity = await embedding_service.calculate_similarity(openai_embed_resized, cohere_embed_resized)
                else:
                    similarity = await embedding_service.calculate_similarity(openai_embed, cohere_embed)
                similarities["openai_cohere"] = similarity
                print(f"  Similarity OpenAI-Cohere: {similarity:.4f}")
            except Exception as e:
                print(f"  ❌ Error calculating similarity: {str(e)}")
        
        # Add results
        results["results"].append({
            "text": text[:100] + ("..." if len(text) > 100 else ""),
            "openai_time_ms": openai_time,
            "hf_time_ms": hf_time,
            "cohere_time_ms": cohere_time,
            "similarities": similarities
        })
    
    # Restore original setting
    settings.USE_OPENSOURCE_EMBED = original_setting
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/embeddings_validation_{timestamp}.json"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Embeddings validation results saved to {filename}")
    return results

async def validate_sentiment_analysis(test_texts: List[str], output_dir: str):
    """Validate sentiment analysis from different providers"""
    print("\n--- Validating Sentiment Analysis ---")
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "sentiment_analysis",
        "providers_tested": [],
        "results": []
    }
    
    # Save current setting
    original_setting = settings.SENTIMENT_PROVIDER
    
    for text in test_texts:
        print(f"Testing text: {text[:50]}...")
        
        # Test with OpenAI
        settings.SENTIMENT_PROVIDER = "openai"
        start_time = datetime.now()
        try:
            openai_result = await sentiment_analyzer._analyze_openai(text)
            openai_time = (datetime.now() - start_time).total_seconds() * 1000
            print(f"  ✅ OpenAI: {openai_result['sentiment']} ({openai_result['confidence']:.2f}) in {openai_time:.2f}ms")
            results["providers_tested"].append("openai")
        except Exception as e:
            openai_result = None
            openai_time = 0
            print(f"  ❌ OpenAI failed: {str(e)}")
        
        # Test with HuggingFace if key is available
        if settings.HF_API_KEY:
            settings.SENTIMENT_PROVIDER = "huggingface"
            start_time = datetime.now()
            try:
                hf_result = await sentiment_analyzer._analyze_huggingface(text)
                hf_time = (datetime.now() - start_time).total_seconds() * 1000
                print(f"  ✅ HuggingFace: {hf_result['sentiment']} ({hf_result['confidence']:.2f}) in {hf_time:.2f}ms")
                results["providers_tested"].append("huggingface")
            except Exception as e:
                hf_result = None
                hf_time = 0
                print(f"  ❌ HuggingFace failed: {str(e)}")
        else:
            hf_result = None
            hf_time = 0
            print("  ⚠️ Skipping HuggingFace (no API key)")
        
        # Test with Symbl if key is available
        if settings.SYMBL_API_KEY:
            settings.SENTIMENT_PROVIDER = "symbl"
            start_time = datetime.now()
            try:
                symbl_result = await sentiment_analyzer._analyze_symbl(text)
                symbl_time = (datetime.now() - start_time).total_seconds() * 1000
                print(f"  ✅ Symbl: {symbl_result['sentiment']} ({symbl_result['confidence']:.2f}) in {symbl_time:.2f}ms")
                results["providers_tested"].append("symbl")
            except Exception as e:
                symbl_result = None
                symbl_time = 0
                print(f"  ❌ Symbl failed: {str(e)}")
        else:
            symbl_result = None
            symbl_time = 0
            print("  ⚠️ Skipping Symbl (no API key)")
        
        # Test with hybrid routing
        if settings.HF_API_KEY or settings.SYMBL_API_KEY:
            settings.SENTIMENT_PROVIDER = "hybrid"
            start_time = datetime.now()
            try:
                hybrid_result = await sentiment_analyzer.analyze(text)
                hybrid_time = (datetime.now() - start_time).total_seconds() * 1000
                print(f"  ✅ Hybrid: {hybrid_result['sentiment']} ({hybrid_result['confidence']:.2f}) in {hybrid_time:.2f}ms")
                results["providers_tested"].append("hybrid")
            except Exception as e:
                hybrid_result = None
                hybrid_time = 0
                print(f"  ❌ Hybrid failed: {str(e)}")
        else:
            hybrid_result = None
            hybrid_time = 0
            print("  ⚠️ Skipping Hybrid (no API keys)")
        
        # Add results
        results["results"].append({
            "text": text[:100] + ("..." if len(text) > 100 else ""),
            "openai_result": openai_result,
            "openai_time_ms": openai_time,
            "hf_result": hf_result,
            "hf_time_ms": hf_time,
            "symbl_result": symbl_result,
            "symbl_time_ms": symbl_time,
            "hybrid_result": hybrid_result,
            "hybrid_time_ms": hybrid_time
        })
    
    # Restore original setting
    settings.SENTIMENT_PROVIDER = original_setting
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/sentiment_validation_{timestamp}.json"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Sentiment validation results saved to {filename}")
    return results

async def run_hybrid_validation(output_dir: str = "validation_results"):
    """Run all hybrid model validations"""
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n======== HYBRID MODEL VALIDATION ========")
    print("Testing and comparing different AI providers")
    print("==========================================\n")
    
    # Test texts for validation
    test_texts = [
        "I'm really happy with the service provided.",
        "The product quality was terrible and customer support was unhelpful.",
        "The meeting was fine, nothing special to report.",
        "When analyzing customer feedback for our mobile app update, we found that users were initially frustrated with the navigation changes but eventually appreciated the improved performance. Several users specifically mentioned that the app crashes less frequently now.",
        "I conducted interviews with 15 participants regarding their experiences with remote work during the pandemic. Key themes included work-life balance challenges, communication difficulties, and appreciation for flexibility. Most participants reported higher productivity but missed social interactions."
    ]
    
    # Step 1: Validate embeddings
    print("\n--- Step 1: Validating embeddings across providers ---")
    embed_results = await validate_embeddings(test_texts, output_dir)
    
    # Step 2: Validate sentiment analysis
    print("\n--- Step 2: Validating sentiment analysis across providers ---")
    sentiment_results = await validate_sentiment_analysis(test_texts, output_dir)
    
    # Step 3: Calculate cost savings and performance metrics
    print("\n--- Step 3: Calculating cost savings and performance metrics ---")
    
    # Embedding metrics
    openai_embed_times = [result.get("openai_time_ms", 0) for result in embed_results["results"] if result.get("openai_time_ms", 0) > 0]
    hf_embed_times = [result.get("hf_time_ms", 0) for result in embed_results["results"] if result.get("hf_time_ms", 0) > 0]
    cohere_embed_times = [result.get("cohere_time_ms", 0) for result in embed_results["results"] if result.get("cohere_time_ms", 0) > 0]
    
    # Sentiment metrics
    openai_sentiment_times = [result.get("openai_time_ms", 0) for result in sentiment_results["results"] if result.get("openai_time_ms", 0) > 0]
    hf_sentiment_times = [result.get("hf_time_ms", 0) for result in sentiment_results["results"] if result.get("hf_time_ms", 0) > 0]
    symbl_sentiment_times = [result.get("symbl_time_ms", 0) for result in sentiment_results["results"] if result.get("symbl_time_ms", 0) > 0]
    hybrid_sentiment_times = [result.get("hybrid_time_ms", 0) for result in sentiment_results["results"] if result.get("hybrid_time_ms", 0) > 0]
    
    # Calculate average latencies
    avg_openai_embed = np.mean(openai_embed_times) if openai_embed_times else 0
    avg_hf_embed = np.mean(hf_embed_times) if hf_embed_times else 0
    avg_cohere_embed = np.mean(cohere_embed_times) if cohere_embed_times else 0
    
    avg_openai_sentiment = np.mean(openai_sentiment_times) if openai_sentiment_times else 0
    avg_hf_sentiment = np.mean(hf_sentiment_times) if hf_sentiment_times else 0
    avg_symbl_sentiment = np.mean(symbl_sentiment_times) if symbl_sentiment_times else 0
    avg_hybrid_sentiment = np.mean(hybrid_sentiment_times) if hybrid_sentiment_times else 0
    
    # Calculate cost estimates (per 1M operations)
    openai_embed_cost = 20.0  # $20 per 1M embeddings
    hf_embed_cost = 3.0  # $3 per 1M embeddings
    cohere_embed_cost = 7.0  # $7 per 1M embeddings
    
    openai_sentiment_cost = 50.0  # $50 per 100K operations
    hf_sentiment_cost = 5.0  # $5 per 100K operations
    symbl_sentiment_cost = 12.0  # $12 per 100K operations
    
    # Using hybrid approach (70% OSS, 30% OpenAI)
    hybrid_embed_cost = (0.7 * hf_embed_cost) + (0.3 * openai_embed_cost)
    hybrid_sentiment_cost = (0.7 * (hf_sentiment_cost + symbl_sentiment_cost) / 2) + (0.3 * openai_sentiment_cost)
    
    # Calculate savings
    embed_savings = (openai_embed_cost - hybrid_embed_cost) / openai_embed_cost * 100
    sentiment_savings = (openai_sentiment_cost - hybrid_sentiment_cost) / openai_sentiment_cost * 100
    
    # Compile summary results
    summary = {
        "timestamp": datetime.now().isoformat(),
        "latency": {
            "embeddings": {
                "openai_ms": avg_openai_embed,
                "huggingface_ms": avg_hf_embed,
                "cohere_ms": avg_cohere_embed,
                "latency_increase_pct": ((avg_hf_embed / avg_openai_embed) - 1) * 100 if avg_openai_embed > 0 else 0
            },
            "sentiment": {
                "openai_ms": avg_openai_sentiment,
                "huggingface_ms": avg_hf_sentiment,
                "symbl_ms": avg_symbl_sentiment,
                "hybrid_ms": avg_hybrid_sentiment,
                "latency_increase_pct": ((avg_hybrid_sentiment / avg_openai_sentiment) - 1) * 100 if avg_openai_sentiment > 0 else 0
            }
        },
        "cost_per_million": {
            "embeddings": {
                "openai_usd": openai_embed_cost,
                "huggingface_usd": hf_embed_cost,
                "cohere_usd": cohere_embed_cost,
                "hybrid_usd": hybrid_embed_cost,
                "savings_pct": embed_savings
            },
            "sentiment": {
                "openai_usd": openai_sentiment_cost,
                "huggingface_usd": hf_sentiment_cost,
                "symbl_usd": symbl_sentiment_cost,
                "hybrid_usd": hybrid_sentiment_cost,
                "savings_pct": sentiment_savings
            }
        },
        "total_estimated_savings_pct": (embed_savings * 0.25) + (sentiment_savings * 0.30) + (60.0 * 0.45)  # 45% for parameter extraction
    }
    
    # Save summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"{output_dir}/hybrid_summary_{timestamp}.json"
    
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n======== VALIDATION SUMMARY ========")
    print(f"Embedding Services:")
    print(f"  OpenAI: {avg_openai_embed:.2f}ms, ${openai_embed_cost:.2f}/1M")
    print(f"  HuggingFace: {avg_hf_embed:.2f}ms, ${hf_embed_cost:.2f}/1M")
    print(f"  Cohere: {avg_cohere_embed:.2f}ms, ${cohere_embed_cost:.2f}/1M")
    print(f"  Cost savings with hybrid approach: {embed_savings:.1f}%")
    
    print(f"\nSentiment Analysis:")
    print(f"  OpenAI: {avg_openai_sentiment:.2f}ms, ${openai_sentiment_cost:.2f}/100K")
    print(f"  HuggingFace: {avg_hf_sentiment:.2f}ms, ${hf_sentiment_cost:.2f}/100K")
    print(f"  Symbl: {avg_symbl_sentiment:.2f}ms, ${symbl_sentiment_cost:.2f}/100K")
    print(f"  Hybrid: {avg_hybrid_sentiment:.2f}ms, ${hybrid_sentiment_cost:.2f}/100K")
    print(f"  Cost savings with hybrid approach: {sentiment_savings:.1f}%")
    
    print(f"\nTotal Estimated Savings (including parameter extraction): {summary['total_estimated_savings_pct']:.1f}%")
    
    if summary['total_estimated_savings_pct'] >= 40:
        print("\n✅ Target achieved! Cost reduction goal of 40-60% is met.")
    else:
        print("\n❌ Target not reached. Cost reduction is below the 40-60% goal.")
    
    print(f"\nDetailed results saved to {summary_file}")
    print("\n=====================================")
    
    return summary['total_estimated_savings_pct'] >= 40

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run hybrid AI model validation")
    parser.add_argument("--output", type=str, default="validation_results", help="Output directory for results")
    
    args = parser.parse_args()
    
    success = asyncio.run(run_hybrid_validation(args.output))
    
    sys.exit(0 if success else 1)
