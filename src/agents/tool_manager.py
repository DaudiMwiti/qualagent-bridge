
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
    elif "generate_insight" in response_lower or "insight" in response_lower:
        return "generate_insight"
    elif "sentiment_analysis" in response_lower or "sentiment" in response_lower:
        return "sentiment_analysis"
    elif "theme_cluster" in response_lower or "cluster" in response_lower:
        return "theme_cluster"
    elif "router" in response_lower:
        return "llm_router"
    elif "summarize_memory" in response_lower:
        return "summarize_memory"
    
    # Default to generate_insight if no clear tool is mentioned
    return "generate_insight"

def extract_tool_params(response_text: str, default_text: str) -> Dict[str, Any]:
    """Extract parameters for the selected tool from the LLM response"""
    # This is a simplified implementation
    tool_name = extract_tool_from_response(response_text)
    
    # Get document metadata if available
    document_metadata = extract_document_metadata(response_text)
    
    # Default parameters by tool type with source tracking
    base_params = get_default_params(tool_name, default_text)
    
    # Add source tracking data for relevant tools
    if tool_name == "generate_insight" and document_metadata:
        base_params["document_metadata"] = document_metadata
    
    return base_params

def extract_document_metadata(response_text: str) -> Dict[str, Any]:
    """Extract document metadata hints from the response"""
    metadata = {
        "document_id": None,
        "filename": None,
        "chunk_id": None,
        "paragraph": None
    }
    
    # Look for document ID hints
    if "document:" in response_text.lower():
        lines = response_text.split("\n")
        for line in lines:
            if "document:" in line.lower():
                parts = line.split(":", 1)
                if len(parts) > 1:
                    metadata["document_id"] = parts[1].strip()
                    # Extract filename if available
                    if "/" in metadata["document_id"]:
                        metadata["filename"] = metadata["document_id"].split("/")[-1]
    
    # Look for chunk hints
    if "chunk" in response_text.lower():
        import re
        chunk_match = re.search(r"chunk[:\s]+(\d+)", response_text.lower())
        if chunk_match:
            metadata["chunk_id"] = int(chunk_match.group(1))
    
    # Look for paragraph hints
    if "paragraph" in response_text.lower():
        import re
        para_match = re.search(r"paragraph[:\s]+(\d+)", response_text.lower())
        if para_match:
            metadata["paragraph"] = int(para_match.group(1))
    
    return metadata

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
