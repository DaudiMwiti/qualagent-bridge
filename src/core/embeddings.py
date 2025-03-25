
from typing import List, Dict, Any, Union, Optional
import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np

from src.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using various providers"""
    
    def __init__(self):
        self.openai_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        )
        
        self.hf_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.HF_API_KEY}"}
        )
        
        self.cohere_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.COHERE_API_KEY}"}
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for the given text using the configured provider"""
        if not text or not text.strip():
            logger.warning("Empty text provided for embeddings")
            # Return zero vector with correct dimension
            return [0.0] * settings.VECTOR_EMBEDDING_DIM
        
        try:
            if settings.USE_OPENSOURCE_EMBED and settings.HF_API_KEY:
                return await self._get_huggingface_embeddings(text)
            elif settings.COHERE_API_KEY:
                return await self._get_cohere_embeddings(text)
            else:
                # Fallback to OpenAI
                return await self._get_openai_embeddings(text)
        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            # Fallback to OpenAI if other providers fail
            if settings.OPENAI_API_KEY:
                logger.info("Falling back to OpenAI embeddings")
                return await self._get_openai_embeddings(text)
            else:
                raise
    
    async def _get_openai_embeddings(self, text: str) -> List[float]:
        """Get embeddings from OpenAI"""
        response = await self.openai_client.post(
            "https://api.openai.com/v1/embeddings",
            json={
                "model": "text-embedding-3-small",
                "input": text
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]
    
    async def _get_huggingface_embeddings(self, text: str) -> List[float]:
        """Get embeddings from HuggingFace Inference API"""
        model = settings.HF_EMBEDDING_MODEL
        api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
        
        response = await self.hf_client.post(
            api_url,
            json={"inputs": text, "options": {"use_cache": True}}
        )
        response.raise_for_status()
        embeddings = response.json()
        
        # Handle different response formats
        if isinstance(embeddings, list) and isinstance(embeddings[0], list):
            # Average token embeddings if we get a token-level response
            return list(np.mean(embeddings, axis=0))
        elif isinstance(embeddings, list):
            return embeddings
        else:
            raise ValueError(f"Unexpected embedding format: {type(embeddings)}")
    
    async def _get_cohere_embeddings(self, text: str) -> List[float]:
        """Get embeddings from Cohere"""
        response = await self.cohere_client.post(
            "https://api.cohere.ai/v1/embed",
            json={
                "texts": [text],
                "model": "embed-english-v3.0",
                "truncate": "END"
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["embeddings"][0]
    
    async def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Convert to numpy arrays for easier calculation
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(dot_product / (norm1 * norm2))

# Create a singleton instance for app-wide use
embedding_service = EmbeddingService()
