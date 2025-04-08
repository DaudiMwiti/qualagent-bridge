
"""Module for managing tools used in the analysis process"""
from typing import Dict, Any, List
import logging
from src.agents.tools import (
    document_search,
    generate_insight,
    sentiment_analysis,
    theme_cluster,
    llm_router,
    summarize_memory
)

logger = logging.getLogger(__name__)

def setup_tools(agent_config: Dict[str, Any]) -> List[Any]:
    """Set up the tools available to the agent based on configuration"""
    available_tools = {
        "document_search": document_search,
        "generate_insight": generate_insight,
        "sentiment_analysis": sentiment_analysis,
        "theme_cluster": theme_cluster,
        "llm_router": llm_router,
        "summarize_memory": summarize_memory
    }
    
    # Filter tools based on agent configuration
    if "tools" in agent_config:
        enabled_tools = agent_config["tools"]
        return [tool for name, tool in available_tools.items() if name in enabled_tools]
    
    # By default, return all tools
    return list(available_tools.values())

def extract_tool_from_response(response_text: str) -> str:
    """Extract which tool to use from the LLM response"""
    response_lower = response_text.lower()
    
    # Check for explicit tool mentions
    if "document_search" in response_lower or "search" in response_lower:
        return "document_search"
    elif "generate_insight" in response_text or "insight" in response_text:
        return "generate_insight"
    elif "sentiment_analysis" in response_text or "sentiment" in response_text:
        return "sentiment_analysis"
    elif "theme_cluster" in response_text or "cluster" in response_text:
        return "theme_cluster"
    elif "router" in response_text:
        return "llm_router"
    elif "summarize_memory" in response_text:
        return "summarize_memory"
    
    # Default to generate_insight if no clear tool is mentioned
    return "generate_insight"

def extract_tool_params(response_text: str, default_text: str) -> Dict[str, Any]:
    """Extract parameters for the selected tool from the LLM response"""
    # This is a simplified implementation
    # In a real system, we would use more sophisticated parameter extraction
    
    # Default parameters by tool type
    tool_params = {
        "document_search": {"query": response_text.split("\n")[0]},
        "generate_insight": {"text": default_text, "approach": "thematic"},
        "sentiment_analysis": {"text": default_text},
        "theme_cluster": {"excerpts": default_text.split("\n\n")},
        "llm_router": {"query": response_text.split("\n")[0]},
        "summarize_memory": {"text": default_text}
    }
    
    return tool_params

def get_default_params(tool_name: str, default_text: str) -> Dict[str, Any]:
    """Get default parameters for a tool"""
    # Default parameters by tool type
    tool_params = {
        "document_search": {"query": default_text.split("\n")[0][:100]},
        "generate_insight": {"text": default_text[:5000], "approach": "thematic"},
        "sentiment_analysis": {"text": default_text[:5000]},
        "theme_cluster": {"excerpts": default_text.split("\n\n")[:10]},
        "llm_router": {"query": default_text.split("\n")[0][:100]},
        "summarize_memory": {"text": default_text[:5000]}
    }
    
    return tool_params.get(tool_name, {})
