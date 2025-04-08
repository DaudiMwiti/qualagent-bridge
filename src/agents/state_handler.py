
"""Module for handling state in the analysis workflow"""
from typing import Dict, Any, List, Type
from datetime import datetime
import logging
import json
from pydantic import BaseModel

from src.core.config import settings
from src.services.param_extractor import param_extractor
from src.schemas.tool_inputs import (
    DocumentSearchInput,
    GenerateInsightInput,
    SentimentAnalysisInput,
    ThemeClusterInput,
    LLMRouterInput,
    SummarizeMemoryInput
)
from src.agents.tool_manager import extract_tool_from_response, extract_tool_params, get_default_params
from src.agents.tools import (
    document_search,
    generate_insight,
    sentiment_analysis,
    theme_cluster,
    llm_router,
    summarize_memory
)

logger = logging.getLogger(__name__)

def get_schema_for_tool(tool_name: str) -> Type[BaseModel]:
    """Get the appropriate Pydantic schema for a tool"""
    tool_schema_map = {
        "document_search": DocumentSearchInput,
        "generate_insight": GenerateInsightInput,
        "sentiment_analysis": SentimentAnalysisInput,
        "theme_cluster": ThemeClusterInput,
        "llm_router": LLMRouterInput,
        "summarize_memory": SummarizeMemoryInput
    }
    
    return tool_schema_map.get(tool_name, GenerateInsightInput)

async def analyze_data(state: Dict[str, Any], agent_config: Dict[str, Any], llm, get_cache_fn) -> Dict[str, Any]:
    """Core analysis using LLM and tools with smart parameter extraction"""
    # Extract preprocessed data
    preprocessed_data = state["intermediate_results"]["preprocessed_data"]
    text_data = preprocessed_data["text_data"]
    parameters = preprocessed_data["parameters"]
    
    # Check if we need to continue analysis or finish
    analysis_steps = state["intermediate_results"].get("analysis_steps", [])
    
    if analysis_steps and analysis_steps[-1].get("is_final", False):
        # Analysis is complete, move to postprocessing
        logger.info("Analysis complete, moving to postprocessing")
        return {
            **state,
            "intermediate_results": {
                **state["intermediate_results"],
                "analysis_complete": True
            }
        }
    
    # Combine text data for analysis
    combined_text = "\n\n".join([item["text"] for item in text_data])
    
    # Generate cache key based on input and config
    cache = await get_cache_fn()
    cache_key = cache.generate_key(
        "analysis_plan",
        text_hash=hash(combined_text[:1000]),
        research_objective=parameters.get("research_objective", ""),
        agent_config_hash=hash(str(agent_config))
    )
    
    # Try to get cached result
    if settings.ENABLE_CACHE:
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info("Using cached analysis plan")
            return {
                **state,
                "intermediate_results": {
                    **state["intermediate_results"],
                    **cached_result,
                    "cache_hit": True
                }
            }
    
    # Create the prompt based on agent configuration
    system_prompt = agent_config.get("system_prompt", 
        "You are a qualitative research expert. Analyze the provided data and identify key themes.")
    
    # Get the research question or objective
    research_objective = parameters.get("research_objective", "Identify key themes and insights")
    
    # Include memory summary in the prompt if available
    context_summary = ""
    if "context_summary" in preprocessed_data:
        context_summary = f"""
        CONTEXT FROM PREVIOUS ANALYSES:
        {preprocessed_data['context_summary']}
        
        Consider this context when analyzing the new data. Build upon these insights.
        """
    
    user_prompt = f"""
    Research Objective: {research_objective}
    
    {context_summary}
    
    Data to analyze:
    {combined_text[:4000]}  # Limit text size for initial analysis
    
    Please analyze this data and determine what analysis steps would be most helpful.
    You have access to the following tools:
    - document_search: Search through documents for relevant information
    - generate_insight: Extract structured insights from text
    - sentiment_analysis: Analyze emotional tone of text
    - theme_cluster: Cluster related concepts from statements
    
    Explain your proposed analysis approach and which tool to use first.
    """
    
    # Call the LLM
    response = await llm.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    # Add the analysis step
    analysis_steps.append({
        "timestamp": datetime.now().isoformat(),
        "analysis": response.content,
        "is_final": False  # This will be set to True in a later step
    })
    
    # Determine which tool to use and extract parameters using the smart extractor
    tool_to_use = None
    tool_params = {}
    
    try:
        # First, try to determine the tool using the response content
        tool_to_use = extract_tool_from_response(response.content)
        
        # Get the appropriate schema for the selected tool
        schema_class = get_schema_for_tool(tool_to_use)
        
        # Extract parameters using the smart extractor
        params, extraction_method = await param_extractor.extract_with_fallback(
            text=response.content,
            schema=schema_class,
            default_values=get_default_params(tool_to_use, combined_text)
        )
        
        # Convert params to dict and add extraction metadata
        tool_params = {
            **params.model_dump(),
            "_extraction_method": "llm" if extraction_method else "fallback"
        }
        
        logger.info(f"Extracted parameters using {tool_params['_extraction_method']} method")
        
    except Exception as e:
        # Fallback to basic extraction if smart extraction fails
        logger.warning(f"Smart parameter extraction failed: {str(e)}")
        tool_to_use = extract_tool_from_response(response.content)
        tool_params = extract_tool_params(response.content, combined_text)
    
    # Prepare the result
    result = {
        **state,
        "intermediate_results": {
            **state["intermediate_results"],
            "analysis_steps": analysis_steps,
            "next_tool": tool_to_use,
            "tool_params": tool_params
        }
    }
    
    # Cache the result if caching is enabled
    if settings.ENABLE_CACHE:
        # Cache only the relevant parts of the intermediate results
        cache_data = {
            "next_tool": tool_to_use,
            "tool_params": tool_params,
            "analysis_steps": analysis_steps
        }
        await cache.set(cache_key, cache_data)
    
    return result

async def execute_tools(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the selected tools based on the analysis"""
    # Get the tool to execute and its parameters
    next_tool = state["intermediate_results"].get("next_tool")
    tool_params = state["intermediate_results"].get("tool_params", {})
    
    if not next_tool:
        logger.warning("No tool specified for execution")
        return {
            **state,
            "intermediate_results": {
                **state["intermediate_results"],
                "analysis_complete": True  # Force completion in case of error
            }
        }
    
    logger.info(f"Executing tool: {next_tool}")
    
    try:
        # Get the appropriate tool function
        tool_map = {
            "document_search": document_search,
            "generate_insight": generate_insight,
            "sentiment_analysis": sentiment_analysis,
            "theme_cluster": theme_cluster,
            "llm_router": llm_router,
            "summarize_memory": summarize_memory
        }
        
        tool_fn = tool_map.get(next_tool)
        if not tool_fn:
            raise ValueError(f"Unknown tool: {next_tool}")
        
        # Execute the tool
        result = await tool_fn.ainvoke(tool_params)
        
        # Add the result to the tool results
        tool_results = state["intermediate_results"].get("tool_results", [])
        tool_results.append({
            "timestamp": datetime.now().isoformat(),
            "tool": next_tool,
            "params": tool_params,
            "result": result
        })
        
        # Get agent config from state if available
        agent_config = state.get("agent_config", {})
        
        # Check if we've executed enough tools based on agent config
        max_tool_calls = agent_config.get("max_tool_calls", 3)
        
        if len(tool_results) >= max_tool_calls:
            # If we've reached the max tool calls, mark analysis as complete
            analysis_steps = state["intermediate_results"].get("analysis_steps", [])
            if analysis_steps:
                analysis_steps[-1]["is_final"] = True
        
        return {
            **state,
            "intermediate_results": {
                **state["intermediate_results"],
                "tool_results": tool_results
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing tool {next_tool}: {str(e)}")
        return {
            **state,
            "intermediate_results": {
                **state["intermediate_results"],
                "tool_error": str(e),
                "analysis_complete": True  # Force completion in case of error
            }
        }
