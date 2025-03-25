
from typing import Dict, Any
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.schemas.tool_inputs import SentimentAnalysisInput, SentimentOutput
from src.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

@tool(return_direct=False)
async def sentiment_analysis(text: str) -> Dict[str, Any]:
    """
    Analyze the emotional tone of text for affective insights.
    
    Args:
        text: The text to analyze for sentiment.
        
    Returns:
        Sentiment classification and confidence score.
    """
    logger.info(f"Analyzing sentiment for text of length {len(text)}")
    
    try:
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert in sentiment analysis. Analyze the emotional tone of the provided text.
            Classify it as "positive", "negative", or "neutral" with a confidence score from 0.0 to 1.0.
            
            Reply with a JSON object containing:
            - sentiment: "positive", "negative", or "neutral"
            - confidence: a float between 0.0 and 1.0
            
            Only include this JSON object in your response, nothing else.
            """),
            ("user", "{text}")
        ])
        
        # Create a smaller, faster model for sentiment analysis
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",  # Using a smaller model for efficiency
            temperature=0.0
        )
        
        # Create the chain
        chain = prompt | llm
        
        # Invoke the chain
        response = await chain.ainvoke({"text": text})
        
        # Parse the response
        content = response.content.strip()
        
        # Handle potential JSON formatting issues
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Parse the JSON response
        result = json.loads(content)
        
        # Ensure the result has the expected format
        if "sentiment" not in result or "confidence" not in result:
            raise ValueError("Invalid response format from LLM")
        
        # Validate sentiment value
        if result["sentiment"] not in ["positive", "negative", "neutral"]:
            result["sentiment"] = "neutral"
        
        # Validate confidence value
        result["confidence"] = float(min(1.0, max(0.0, result["confidence"])))
        
        logger.info(f"Sentiment analysis result: {result['sentiment']} with confidence {result['confidence']}")
        return result
        
    except Exception as e:
        logger.error(f"Error in sentiment_analysis: {str(e)}")
        return {"sentiment": "neutral", "confidence": 0.0, "error": str(e)}
