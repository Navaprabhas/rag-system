"""
Embedding generation with multi-provider support and caching.
"""
import hashlib
import json
from pathlib import Path
from typing import Any

import ollama
from openai import AsyncOpenAI
import cohere

from app.core.config import settings
from app.core.exceptions import EmbeddingError
from app.core.logging import logger


class Embedder:
    """Generate embeddings with caching support."""
    
    def __init__(self):
        """Initialize embedder with configured provider."""
        self.provider = settings.embedding_provider
        self.cache_enabled = settings.embedding_cache_enabled
        self.cache_dir = Path(settings.cache_dir) / "embeddings"
        
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize clients
        self._init_clients()
        
        logger.info(f"Initialized embedder: provider={self.provider}")
    
    def _init_clients(self):
        """Initialize API clients based on provider."""
        if self.provider == "openai":
            if not settings.openai_api_key:
                raise EmbeddingError("OpenAI API key not configured")
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        elif self.provider == "cohere":
            if not settings.cohere_api_key:
                raise EmbeddingError("Cohere API key not configured")
            self.cohere_client = cohere.AsyncClient(settings.cohere_api_key)
        
        elif self.provider == "ollama":
            # Ollama client is initialized per request
            pass
    
    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        # Check cache first
        if self.cache_enabled:
            cached_embedding = self._get_from_cache(text)
            if cached_embedding:
                logger.debug("Retrieved embedding from cache")
                return cached_embedding
        
        # Generate embedding
        try:
            if self.provider == "ollama":
                embedding = await self._embed_ollama(text)
            elif self.provider == "openai":
                embedding = await self._embed_openai(text)
            elif self.provider == "cohere":
                embedding = await self._embed_cohere(text)
            else:
                raise EmbeddingError(f"Unknown provider: {self.provider}")
            
            # Cache embedding
            if self.cache_enabled:
                self._save_to_cache(text, embedding)
            
            return embedding
            
        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate embedding: {str(e)}",
                details={"provider": self.provider}
            )
    
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        
        return embeddings
    
    async def _embed_ollama(self, text: str) -> list[float]:
        """Generate embedding using Ollama."""
        response = ollama.embeddings(
            model=settings.ollama_embed_model,
            prompt=text
        )
        return response["embedding"]
    
    async def _embed_openai(self, text: str) -> list[float]:
        """Generate embedding using OpenAI."""
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    async def _embed_cohere(self, text: str) -> list[float]:
        """Generate embedding using Cohere."""
        response = await self.cohere_client.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_document"
        )
        return response.embeddings[0]
    
    def _get_cache_key(self, text: str) -> str:
        """
        Generate cache key for text.
        
        Args:
            text: Text to generate key for
            
        Returns:
            Cache key (hash)
        """
        content = f"{self.provider}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_from_cache(self, text: str) -> list[float] | None:
        """
        Retrieve embedding from cache.
        
        Args:
            text: Text to retrieve embedding for
            
        Returns:
            Cached embedding or None
        """
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                return data["embedding"]
            except Exception as e:
                logger.warning(f"Failed to read cache: {e}")
        
        return None
    
    def _save_to_cache(self, text: str, embedding: list[float]):
        """
        Save embedding to cache.
        
        Args:
            text: Text that was embedded
            embedding: Generated embedding
        """
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, "w") as f:
                json.dump({"embedding": embedding}, f)
        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")
