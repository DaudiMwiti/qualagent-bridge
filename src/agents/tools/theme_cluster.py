
from typing import Dict, Any, List
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.schemas.tool_inputs import ThemeClusterInput, ThemeClusterOutput
from src.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

@tool(return_direct=False)
async def theme_cluster(excerpts: List[str]) -> Dict[str, Any]:
    """
    Cluster related concepts or excerpts from a list of qualitative statements.
    
    Args:
        excerpts: List of text excerpts to cluster by theme.
        
    Returns:
        List of clusters with theme names and related excerpts.
    """
    logger.info(f"Clustering {len(excerpts)} excerpts into themes")
    
    if not excerpts:
        return {"clusters": []}
    
    try:
        # Format excerpts for the prompt
        formatted_excerpts = "\n".join([f"- {excerpt}" for excerpt in excerpts])
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a qualitative research expert specializing in thematic analysis. 
            Your task is to identify conceptual themes from a set of excerpts and cluster them accordingly.
            
            Output only a JSON array of cluster objects, each containing:
            - theme: A clear name for the theme
            - description: A brief description of the theme
            - excerpts: An array of excerpts that belong to this theme (use exact texts from the input)
            
            Guidelines:
            - Create 3-7 themes depending on the data
            - Each excerpt can belong to only one theme
            - All excerpts should be assigned to a theme
            - Choose theme names that are concise and descriptive
            
            Return only valid JSON without any additional text.
            """),
            ("user", """
            Please cluster these excerpts into meaningful themes:
            
            {formatted_excerpts}
            """)
        ])
        
        # Create an LLM instance
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.2
        )
        
        # Create the chain
        chain = prompt | llm
        
        # Invoke the chain
        response = await chain.ainvoke({"formatted_excerpts": formatted_excerpts})
        
        # Parse the response - in a real application we would use a more robust parser
        content = response.content.strip()
        
        # Handle possible markdown code blocks
        if "```json" in content:
            json_content = content.split("```json")[1].split("```")[0].strip()
            clusters = json.loads(json_content)
        elif "```" in content:
            json_content = content.split("```")[1].split("```")[0].strip()
            clusters = json.loads(json_content)
        else:
            # Attempt to parse as raw JSON
            clusters = json.loads(content)
        
        logger.info(f"Generated {len(clusters)} theme clusters")
        return {"clusters": clusters}
        
    except Exception as e:
        logger.error(f"Error in theme_cluster: {str(e)}")
        return {"clusters": [], "error": str(e)}
