
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.agents.tools import (
    document_search,
    generate_insight,
    sentiment_analysis,
    theme_cluster,
    llm_router
)

logger = logging.getLogger(__name__)

class AnalysisToolsService:
    """Service for managing and using analysis tools"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tools = {
            "document_search": document_search,
            "generate_insight": generate_insight,
            "sentiment_analysis": sentiment_analysis,
            "theme_cluster": theme_cluster,
            "llm_router": llm_router
        }
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool with the given parameters"""
        logger.info(f"Executing tool: {tool_name} with params: {params}")
        
        if tool_name not in self.tools:
            logger.error(f"Tool not found: {tool_name}")
            return {"error": f"Tool not found: {tool_name}"}
        
        try:
            tool = self.tools[tool_name]
            result = await tool.ainvoke(params)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e)}
    
    async def route_and_execute(self, query: str) -> Dict[str, Any]:
        """Use the router to determine the best tool and execute it"""
        try:
            # First, use the router to determine which tool to use
            router_result = await llm_router.ainvoke({"query": query})
            
            if "error" in router_result:
                return {"error": router_result["error"]}
            
            selected_tool = router_result["tool"]
            rationale = router_result["rationale"]
            
            logger.info(f"Router selected tool: {selected_tool} with rationale: {rationale}")
            
            # Then execute the selected tool with the query
            if selected_tool == "document_search":
                result = await document_search.ainvoke({"query": query})
            elif selected_tool == "generate_insight":
                result = await generate_insight.ainvoke({"text": query})
            elif selected_tool == "sentiment_analysis":
                result = await sentiment_analysis.ainvoke({"text": query})
            elif selected_tool == "theme_cluster":
                # For theme_cluster, we would typically expect a list of excerpts
                # For simplicity, we'll split the query into sentences as a workaround
                import re
                excerpts = [s.strip() for s in re.split(r'[.!?]', query) if s.strip()]
                result = await theme_cluster.ainvoke({"excerpts": excerpts})
            else:
                result = {"error": f"Unknown tool: {selected_tool}"}
            
            # Add the router's reasoning to the result
            result["tool_selection"] = {
                "tool": selected_tool,
                "rationale": rationale
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in route_and_execute: {str(e)}")
            return {"error": str(e)}
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get a list of all available tools with their descriptions"""
        return [
            {
                "name": name,
                "description": tool.description
            }
            for name, tool in self.tools.items()
        ]
