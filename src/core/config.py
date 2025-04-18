
import os
from pydantic_settings import BaseSettings
from typing import List, Dict, Any, Optional

class Settings(BaseSettings):
    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "QualAgents"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "qualagents")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Database connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    
    # Vector database settings
    VECTOR_EMBEDDING_DIM: int = int(os.getenv("VECTOR_EMBEDDING_DIM", "1536"))  # For OpenAI embeddings
    VECTOR_INDEX_TYPE: str = os.getenv("VECTOR_INDEX_TYPE", "ivfflat")  # 'ivfflat' or 'hnsw'
    VECTOR_INDEX_LISTS: int = int(os.getenv("VECTOR_INDEX_LISTS", "100"))  # For IVFFlat index
    VECTOR_INDEX_M: int = int(os.getenv("VECTOR_INDEX_M", "16"))  # For HNSW index
    VECTOR_INDEX_EF_CONSTRUCTION: int = int(os.getenv("VECTOR_INDEX_EF_CONSTRUCTION", "64"))  # For HNSW index
    
    # Search settings
    SEARCH_RESULT_LIMIT: int = int(os.getenv("SEARCH_RESULT_LIMIT", "20"))
    SEARCH_MIN_SCORE: float = float(os.getenv("SEARCH_MIN_SCORE", "0.0"))
    SEARCH_CACHE_TTL: int = int(os.getenv("SEARCH_CACHE_TTL", "300"))  # 5 minutes in seconds
    
    # Caching settings
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "1") == "1"
    CACHE_CLEANUP_INTERVAL: int = int(os.getenv("CACHE_CLEANUP_INTERVAL", "3600"))  # 1 hour in seconds
    
    # Parameter extraction settings
    PARAM_EXTRACTION_MAX_RETRIES: int = int(os.getenv("PARAM_EXTRACTION_MAX_RETRIES", "2"))
    
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # LLM configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o")
    
    # Hybrid AI architecture settings
    HF_API_KEY: str = os.getenv("HF_API_KEY", "")
    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN", "")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    SYMBL_API_KEY: str = os.getenv("SYMBL_API_KEY", "")
    
    # Feature flags for hybrid architecture
    USE_OPENSOURCE_EMBED: bool = os.getenv("USE_OPENSOURCE_EMBED", "1") == "1"
    SENTIMENT_PROVIDER: str = os.getenv("SENTIMENT_PROVIDER", "hybrid")  # "openai", "symbl", "huggingface", "hybrid"
    PARAM_EXTRACTION_PROVIDER: str = os.getenv("PARAM_EXTRACTION_PROVIDER", "openai")  # "openai", "mixtral"
    
    # Model settings
    HF_EMBEDDING_MODEL: str = os.getenv("HF_EMBEDDING_MODEL", "BAAI/bge-small-en")
    HF_SENTIMENT_MODEL: str = os.getenv("HF_SENTIMENT_MODEL", "distilbert-base-uncased-emotion")
    REPLICATE_PARAM_MODEL: str = os.getenv("REPLICATE_PARAM_MODEL", "mistralai/mixtral-8x7b-instruct-v0.1")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
