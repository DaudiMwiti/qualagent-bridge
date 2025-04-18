
from typing import Dict, Any, List
from langchain.tools import tool
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from src.schemas.tool_inputs import GenerateInsightInput, InsightOutput
from src.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

@tool(return_direct=False)
async def generate_insight(text: str, approach: str = "thematic", document_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Extract structured insights from a passage of qualitative text.
    
    Args:
        text: The text to analyze for insights.
        approach: The analytical approach to use (e.g., 'thematic', 'grounded theory').
        document_metadata: Optional metadata about the source document.
        
    Returns:
        A list of insights with themes, quotes, summaries, and source information.
    """
    logger.info(f"Generating insights using {approach} approach")
    
    # Set default document metadata if none provided
    if document_metadata is None:
        document_metadata = {
            "document_id": "unknown",
            "filename": "unknown",
        }
    
    try:
        # Define the system prompt based on the analytical approach
        system_templates = {
            "thematic": "You are an expert qualitative researcher using thematic analysis. Extract key themes from the text.",
            "grounded theory": "You are an expert in grounded theory. Code the data and identify emerging theories.",
            "phenomenological": "You are a phenomenological researcher. Identify the lived experiences and their essence.",
            "narrative": "You are a narrative analyst. Extract key stories and their meanings.",
            "discourse": "You are a discourse analyst. Identify language patterns and their social implications."
        }
        
        # Use the specified approach or default to thematic
        system_prompt = system_templates.get(approach.lower(), system_templates["thematic"])
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", """
            Analyze the following qualitative text and extract key insights.
            
            Text: {text}
            
            For each insight:
            1. Identify a clear theme or concept
            2. Extract a relevant quote from the text
            3. Provide its approximate position in the text (rough character position)
            4. Write a brief summary of the insight
            
            Format your response as a list of JSON objects with keys:
            - theme: The identified theme or concept
            - quote: A representative quote
            - quote_start: Approximate character position start (numeric estimate)
            - quote_end: Approximate character position end (numeric estimate) 
            - summary: Brief explanation of the insight
            
            Aim to provide 3-5 high-quality insights.
            """)
        ])
        
        # Create an LLM instance
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.DEFAULT_MODEL,
            temperature=0.2
        )
        
        # Create the chain
        chain = prompt | llm
        
        # Invoke the chain
        response = await chain.ainvoke({"text": text})
        
        # Parse the response - in a real application we would use a more robust parser
        content = response.content
        
        # Check if the response is already in JSON format
        if content.strip().startswith("[") and content.strip().endswith("]"):
            raw_insights = json.loads(content)
        else:
            # Handle markdown code blocks or other formats
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0].strip()
                raw_insights = json.loads(json_content)
            elif "```" in content:
                json_content = content.split("```")[1].split("```")[0].strip()
                raw_insights = json.loads(json_content)
            else:
                # Simple fallback for other formats
                raw_insights = [
                    {
                        "theme": "Parsing Error",
                        "quote": "Could not extract structured insights",
                        "summary": "The LLM response was not in a parsable format"
                    }
                ]
        
        # Enrich the insights with source information
        insights = []
        for insight in raw_insights:
            # Add source information to each quote
            source_info = {
                "document_id": document_metadata.get("document_id", "unknown"),
                "chunk_id": document_metadata.get("chunk_id", 0),
                "start_char": insight.get("quote_start", 0),
                "end_char": insight.get("quote_end", 0),
                "metadata": {
                    "filename": document_metadata.get("filename", "unknown"),
                    "paragraph": document_metadata.get("paragraph", 0)
                }
            }
            
            # Create enriched insight with source tracking
            enriched_insight = {
                "theme": insight.get("theme"),
                "quote": insight.get("quote", ""),
                "summary": insight.get("summary", ""),
                "source": source_info
            }
            insights.append(enriched_insight)
        
        logger.info(f"Generated {len(insights)} insights with source tracking")
        return {"insights": insights}
        
    except Exception as e:
        logger.error(f"Error in generate_insight: {str(e)}")
        return {"insights": [], "error": str(e)}
