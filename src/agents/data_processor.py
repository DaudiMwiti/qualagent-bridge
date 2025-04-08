
"""Module for processing data in analysis workflows"""
from typing import Dict, Any, List, Callable
import logging
from datetime import datetime

from src.agents.tool_manager import extract_tool_from_response, extract_tool_params, get_default_params
from src.agents.tools.summarize_memory import summarize_memory

logger = logging.getLogger(__name__)

def extract_text_data(input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract text data from various input formats"""
    text_data = []
    
    # Handle different input formats
    if "interviews" in input_data:
        text_data.extend(input_data["interviews"])
    elif "texts" in input_data:
        text_data.extend([{"text": t, "metadata": {"document_id": f"text-{i}", "filename": f"text-{i}"}} 
                          for i, t in enumerate(input_data["texts"])])
    elif "documents" in input_data:
        text_data.extend(input_data["documents"])
    elif "text" in input_data:
        text_data.append({
            "text": input_data["text"], 
            "metadata": input_data.get("metadata", {"document_id": "main-text", "filename": "main-text"})
        })
    
    # Ensure each text item has metadata with document_id and filename
    for i, item in enumerate(text_data):
        if "metadata" not in item:
            item["metadata"] = {}
        if "document_id" not in item["metadata"]:
            item["metadata"]["document_id"] = f"doc-{i}"
        if "filename" not in item["metadata"]:
            item["metadata"]["filename"] = f"document-{i}"
    
    return text_data

async def preprocess_data(state: Dict[str, Any], get_cache_fn: Callable, extract_text_fn: Callable) -> Dict[str, Any]:
    """Preprocess the input data"""
    # Extract parameters and data
    input_data = state.get("input_data", {})
    parameters = input_data.get("parameters", {})
    
    # Structure the input data for processing
    preprocessed_data = {
        "text_data": extract_text_fn(input_data),
        "parameters": parameters,
        "metadata": {
            "start_time": datetime.now().isoformat(),
            "agent_config": state.get("agent_config", {})
        }
    }
    
    # Fetch and summarize relevant memories if available in the context
    if "context" in input_data and "memories" in input_data["context"]:
        memories = input_data["context"]["memories"]
        
        # Check if we have enough memories to summarize
        if memories and len(memories) > 1:
            try:
                # Use the summarize_memory tool to generate a concise summary
                logger.info(f"Generating memory summary from {len(memories)} memories")
                
                # Call the summarize_memory tool
                summary_result = await summarize_memory.ainvoke({"memories": memories})
                
                # Add the summary to preprocessed data
                if "summary" in summary_result:
                    memory_summary = summary_result["summary"]
                    
                    # Ensure summary isn't too long (approx 400 tokens)
                    if len(memory_summary.split()) > 100:  # Very rough token estimation
                        logger.warning("Memory summary too long, truncating")
                        sentences = memory_summary.split('.')
                        truncated_summary = '.'.join(sentences[:5]) + '.'  # Take ~5 sentences
                        memory_summary = truncated_summary
                        
                    preprocessed_data["context_summary"] = memory_summary
                    logger.info("Added memory summary to context")
                else:
                    logger.warning("Failed to generate memory summary")
            except Exception as e:
                logger.error(f"Error summarizing memories: {str(e)}")
    
    logger.info(f"Preprocessed data with {len(preprocessed_data['text_data'])} text items")
    
    return {
        **state,
        "intermediate_results": {
            "preprocessed_data": preprocessed_data,
            "analysis_steps": [],
            "tool_results": []
        }
    }

def format_analysis_steps(analysis_steps: List[Dict[str, Any]]) -> str:
    """Format analysis steps for the summary prompt"""
    if not analysis_steps:
        return "No analysis steps recorded."
    
    formatted_steps = []
    for i, step in enumerate(analysis_steps):
        formatted_steps.append(f"Step {i+1}: {step.get('analysis', '')[:500]}...")
    
    return "\n\n".join(formatted_steps)

def format_tool_results(tool_results: List[Dict[str, Any]]) -> str:
    """Format tool results for the summary prompt"""
    if not tool_results:
        return "No tool results recorded."
    
    formatted_results = []
    for i, result in enumerate(tool_results):
        tool = result.get("tool", "unknown")
        result_text = str(result.get("result", {}))[:500]
        formatted_results.append(f"Tool {i+1} ({tool}): {result_text}...")
    
    return "\n\n".join(formatted_results)

def extract_themes_from_results(tool_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract themes from tool results"""
    themes = []
    
    for result in tool_results:
        tool = result.get("tool")
        result_data = result.get("result", {})
        
        # Extract themes from different tool results
        if tool == "generate_insight" and "insights" in result_data:
            for insight in result_data["insights"]:
                if "theme" in insight:
                    # Create proper theme with quote objects including source
                    theme = {
                        "name": insight.get("theme"),
                        "description": insight.get("summary", ""),
                        "keywords": [],
                        "quotes": []
                    }
                    
                    # Add quote with source information
                    if "quote" in insight:
                        quote = {
                            "text": insight.get("quote", ""),
                            "source": insight.get("source", {})
                        }
                        theme["quotes"] = [quote]
                    
                    themes.append(theme)
                    
        elif tool == "theme_cluster" and "clusters" in result_data:
            for cluster in result_data["clusters"]:
                if "theme" in cluster:
                    theme = {
                        "name": cluster.get("theme"),
                        "description": cluster.get("description", ""),
                        "keywords": cluster.get("keywords", []),
                        "quotes": []
                    }
                    
                    # Add quotes with source information if available
                    if "excerpts" in cluster:
                        for excerpt in cluster["excerpts"]:
                            if isinstance(excerpt, dict) and "text" in excerpt:
                                # Modern format with source info
                                theme["quotes"].append(excerpt)
                            else:
                                # Legacy format without source info
                                theme["quotes"].append({
                                    "text": excerpt,
                                    "source": None
                                })
                    
                    themes.append(theme)
    
    # Consolidate duplicate themes
    theme_map = {}
    for theme in themes:
        name = theme.get("name")
        if name not in theme_map:
            theme_map[name] = theme
        else:
            # Merge quotes from duplicate themes
            existing_theme = theme_map[name]
            if "quotes" in theme and theme["quotes"]:
                existing_theme["quotes"].extend(theme["quotes"])
            
            # Merge keywords if available
            if "keywords" in theme and theme["keywords"]:
                existing_keywords = set(existing_theme.get("keywords", []))
                existing_keywords.update(theme["keywords"])
                existing_theme["keywords"] = list(existing_keywords)
    
    return list(theme_map.values())

async def postprocess_results(state: Dict[str, Any], llm) -> Dict[str, Any]:
    """Postprocess the results into a structured format"""
    # Extract all data
    preprocessed_data = state["intermediate_results"]["preprocessed_data"]
    analysis_steps = state["intermediate_results"].get("analysis_steps", [])
    tool_results = state["intermediate_results"].get("tool_results", [])
    
    # Create a summary prompt based on the collected data
    summary_prompt = f"""
    You are a qualitative research expert. Synthesize the following analysis steps and tool results into a coherent summary.
    
    Research Objective: {preprocessed_data["parameters"].get("research_objective", "Identify key themes and insights")}
    
    Analysis Steps:
    {format_analysis_steps(analysis_steps)}
    
    Tool Results:
    {format_tool_results(tool_results)}
    
    Create a structured summary with:
    1. Key Themes: The main themes identified in the data
    2. Notable Insights: Specific insights derived from the data
    3. Evidence: Supporting quotes or data points
    4. Recommendations: Suggested actions or further research
    
    Format your response as clear sections with headings.
    """
    
    # Call the LLM for the summary
    response = await llm.ainvoke([
        {"role": "system", "content": "You are a qualitative research expert specializing in synthesizing findings."},
        {"role": "user", "content": summary_prompt}
    ])
    
    # Extract themes from tool results (if available)
    themes = extract_themes_from_results(tool_results)
    
    # Structure the final results
    structured_results = {
        "summary": response.content,
        "themes": themes,
        "analysis_steps": analysis_steps,
        "tool_results": tool_results,
        "metadata": {
            "completed_at": datetime.now().isoformat(),
            "model": llm.model if hasattr(llm, 'model') else 'unknown',
            "agent_config": preprocessed_data.get("metadata", {}).get("agent_config", {})
        }
    }
    
    logger.info(f"Analysis complete with {len(themes)} themes extracted")
    
    return {
        **state,
        "final_results": structured_results
    }
