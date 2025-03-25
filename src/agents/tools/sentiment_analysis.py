
from typing import Dict, Any, Optional, List
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.schemas.tool_inputs import SentimentAnalysisInput, SentimentOutput
from src.core.config import settings
import logging
import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Handles sentiment analysis using multiple providers"""
    
    def __init__(self):
        self.openai_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        )
        
        self.hf_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.HF_API_KEY}"}
        )
        
        self.symbl_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.SYMBL_API_KEY}"}
        )
        
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using the appropriate provider based on configuration"""
        # Determine which provider to use
        provider = settings.SENTIMENT_PROVIDER
        text_length = len(text.split())
        
        try:
            if provider == "hybrid":
                # Route based on text complexity
                if text_length < 15:  # Short texts
                    try:
                        if settings.SYMBL_API_KEY:
                            return await self._analyze_symbl(text)
                        else:
                            return await self._analyze_huggingface(text)
                    except Exception as e:
                        logger.warning(f"Error with primary sentiment provider: {str(e)}")
                        return await self._analyze_openai(text)
                else:
                    return await self._analyze_openai(text)
            elif provider == "symbl" and settings.SYMBL_API_KEY:
                return await self._analyze_symbl(text)
            elif provider == "huggingface" and settings.HF_API_KEY:
                return await self._analyze_huggingface(text)
            else:
                # Default to OpenAI
                return await self._analyze_openai(text)
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            # Fall back to OpenAI in case of any errors
            try:
                return await self._analyze_openai(text)
            except Exception as fallback_error:
                logger.error(f"Fallback to OpenAI also failed: {str(fallback_error)}")
                # Return a neutral sentiment with zero confidence if everything fails
                return {"sentiment": "neutral", "confidence": 0.0, "error": str(e)}
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=3))
    async def _analyze_openai(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using OpenAI"""
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
            
            logger.info(f"OpenAI sentiment analysis result: {result['sentiment']} with confidence {result['confidence']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in OpenAI sentiment analysis: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=3))
    async def _analyze_huggingface(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using HuggingFace Inference API"""
        try:
            model = settings.HF_SENTIMENT_MODEL
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            response = await self.hf_client.post(
                api_url,
                json={"inputs": text}
            )
            response.raise_for_status()
            result = response.json()
            
            # Process the result based on the model's output format
            # Most sentiment models return a list of label/score pairs
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and "label" in result[0] and "score" in result[0]:
                    # Find the highest scoring sentiment
                    highest_score = 0.0
                    highest_label = "neutral"
                    
                    for item in result:
                        if item["score"] > highest_score:
                            highest_score = item["score"]
                            highest_label = item["label"].lower()
                    
                    # Map the label to our standard format
                    sentiment_mapping = {
                        "positive": "positive",
                        "negative": "negative",
                        "neutral": "neutral",
                        "joy": "positive",
                        "happiness": "positive",
                        "sadness": "negative",
                        "anger": "negative",
                        "fear": "negative",
                        "disgust": "negative",
                        "surprise": "neutral"
                    }
                    
                    sentiment = sentiment_mapping.get(highest_label, "neutral")
                    
                    logger.info(f"HuggingFace sentiment analysis result: {sentiment} with confidence {highest_score}")
                    return {
                        "sentiment": sentiment,
                        "confidence": highest_score
                    }
            
            # Fallback for unexpected response format
            logger.warning(f"Unexpected HuggingFace response format: {result}")
            return {"sentiment": "neutral", "confidence": 0.5}
            
        except Exception as e:
            logger.error(f"Error in HuggingFace sentiment analysis: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=3))
    async def _analyze_symbl(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Symbl.ai"""
        try:
            response = await self.symbl_client.post(
                "https://api.symbl.ai/v1/process/text",
                json={
                    "messages": [{"payload": {"content": text}}],
                    "sentiment": True
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract sentiment from Symbl response
            if "sentiment" in result:
                symbl_sentiment = result["sentiment"]
                
                # Map Symbl sentiment to our standard format
                if symbl_sentiment["polarity"]["score"] > 0.3:
                    sentiment = "positive"
                elif symbl_sentiment["polarity"]["score"] < -0.3:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                # Convert score to confidence (Symbl uses -1 to 1 scale)
                confidence = (abs(symbl_sentiment["polarity"]["score"]) + 0.3) / 1.3
                confidence = min(1.0, max(0.0, confidence))
                
                logger.info(f"Symbl sentiment analysis result: {sentiment} with confidence {confidence}")
                return {
                    "sentiment": sentiment,
                    "confidence": confidence
                }
            
            # Fallback for unexpected response format
            logger.warning(f"Unexpected Symbl response format: {result}")
            return {"sentiment": "neutral", "confidence": 0.5}
            
        except Exception as e:
            logger.error(f"Error in Symbl sentiment analysis: {str(e)}")
            raise

# Create a singleton sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()

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
        result = await sentiment_analyzer.analyze(text)
        return result
    except Exception as e:
        logger.error(f"Error in sentiment_analysis: {str(e)}")
        return {"sentiment": "neutral", "confidence": 0.0, "error": str(e)}
