"""
Application configuration using Pydantic Settings.
All configuration values are loaded from environment variables.
"""
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Configuration
    project_name: str = Field(default="RAG System", alias="PROJECT_NAME")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    
    # Embedding Configuration
    embedding_provider: Literal["ollama", "openai", "cohere"] = Field(
        default="ollama", alias="EMBEDDING_PROVIDER"
    )
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")
    ollama_llm_model: str = Field(default="llama3", alias="OLLAMA_LLM_MODEL")
    
    # External API Keys
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    cohere_api_key: str | None = Field(default=None, alias="COHERE_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    
    # LLM Configuration
    llm_provider: Literal["ollama", "openai", "anthropic"] = Field(
        default="ollama", alias="LLM_PROVIDER"
    )
    
    # Qdrant Configuration
    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_collection: str = Field(default="rag_documents", alias="QDRANT_COLLECTION")
    
    # Chunking Configuration
    chunk_size: int = Field(default=400, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=75, alias="CHUNK_OVERLAP")
    
    # Retrieval Configuration
    top_k: int = Field(default=10, alias="TOP_K")
    rerank_top_n: int = Field(default=5, alias="RERANK_TOP_N")
    max_context_tokens: int = Field(default=3000, alias="MAX_CONTEXT_TOKENS")
    confidence_threshold: float = Field(default=0.4, alias="CONFIDENCE_THRESHOLD")
    
    # Feature Flags
    embedding_cache_enabled: bool = Field(default=True, alias="EMBEDDING_CACHE_ENABLED")
    enable_streaming: bool = Field(default=True, alias="ENABLE_STREAMING")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Redis Cache (optional)
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    # Data directories
    data_dir: str = Field(default="./data", alias="DATA_DIR")
    cache_dir: str = Field(default="./data/cache", alias="CACHE_DIR")
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension based on provider and model."""
        dimensions = {
            "ollama": {
                "nomic-embed-text": 768,
                "mxbai-embed-large": 1024,
            },
            "openai": {
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072,
            },
            "cohere": {
                "embed-english-v3.0": 1024,
                "embed-multilingual-v3.0": 1024,
            }
        }
        
        if self.embedding_provider == "ollama":
            return dimensions["ollama"].get(self.ollama_embed_model, 768)
        elif self.embedding_provider == "openai":
            return dimensions["openai"].get("text-embedding-3-small", 1536)
        elif self.embedding_provider == "cohere":
            return dimensions["cohere"].get("embed-english-v3.0", 1024)
        
        return 768  # Default fallback


# Global settings instance
settings = Settings()
