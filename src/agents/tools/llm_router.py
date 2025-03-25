
from typing import Dict, Any
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.schemas.tool_inputs import LLMRouterInput, LLMRouterOutput
from src.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

# Define the available tools for routing
AVAILABLE_TOOLS = {
    "document_search": "Search through qualitative documents for relevant information",
    "generate_insight": "Extract structured insights from a passage of text",
    "sentiment_analysis": "Analyze the emotional tone of text",
    "theme_cluster": "Cluster related concepts from a list of statements",
}

@tool(return_direct=False)
async def llm_router(query: str) -> Dict[str, Any]:
    """
    Determine which tool is most appropriate for a given query.
    
    Args:
        query: The query to determine which tool to use.
        
    Returns:
        The suggested tool and rationale for using it.
    """
    logger.info(f"Routing query: {query}")
    
    try:
        # Format the available tools for the prompt
        tools_description = "\n".join([f"- {name}: {desc}" for name, desc in AVAILABLE_TOOLS.items()])
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are an expert system that routes user queries to the appropriate tool.
            
            Available tools:
            {tools_description}
            
            Based on the user's query, determine which tool would be most helpful.
            
            Reply with a JSON object containing:
            - tool: The name of the suggested tool (must be one from the list above)
            - rationale: A brief explanation of why this tool is appropriate
            
            Only include this JSON object in your response, nothing else.
            """),
            ("user", "{query}")
        ])
        
        # Create an LLM instance
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.0
        )
        
        # Create the chain
        chain = prompt | llm
        
        # Invoke the chain
        response = await chain.ainvoke({"query": query})
        
        # Parse the response
        content = response.content.strip()
        
        # Handle potential JSON formatting issues
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Parse the JSON response
        result = json.loads(content)
        
        # Validate tool selection
        if "tool" not in result or result["tool"] not in AVAILABLE_TOOLS:
            result["tool"] = "document_search"  # Default to search if invalid
            result["rationale"] = "Defaulting to document search as the specified tool was invalid."
        
        logger.info(f"Selected tool: {result['tool']}")
        return result
        
    except Exception as e:
        logger.error(f"Error in llm_router: {str(e)}")
        return {
            "tool": "document_search",
            "rationale": f"Error in tool selection: {str(e)}. Defaulting to document search.",
            "error": str(e)
        }
