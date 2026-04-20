"""
Context assembly for LLM prompts with token management.
"""
from typing import Any

import tiktoken

from app.core.config import settings
from app.core.logging import logger


class ContextBuilder:
    """Build context for LLM prompts with token management."""
    
    def __init__(self):
        """Initialize context builder."""
        self.max_context_tokens = settings.max_context_tokens
        
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            logger.warning("Failed to load tiktoken")
            self.tokenizer = None
    
    def build_context(
        self,
        chunks: list[dict[str, Any]],
        query: str
    ) -> tuple[str, int]:
        """
        Build context string from chunks with token limit.
        
        Args:
            chunks: List of retrieved chunks
            query: User query
            
        Returns:
            Tuple of (context_string, total_tokens)
        """
        if not chunks:
            return "", 0
        
        # Sort chunks by score (descending)
        sorted_chunks = sorted(
            chunks,
            key=lambda x: x.get("score", 0.0),
            reverse=True
        )
        
        context_parts = []
        total_tokens = 0
        
        # Reserve tokens for query and system prompt (~500 tokens)
        available_tokens = self.max_context_tokens - 500
        
        for chunk in sorted_chunks:
            # Format chunk with metadata
            chunk_text = self._format_chunk(chunk)
            chunk_tokens = self._count_tokens(chunk_text)
            
            # Check if adding this chunk would exceed limit
            if total_tokens + chunk_tokens > available_tokens:
                logger.info(
                    f"Reached token limit: {total_tokens}/{available_tokens}, "
                    f"using {len(context_parts)} chunks"
                )
                break
            
            context_parts.append(chunk_text)
            total_tokens += chunk_tokens
        
        # Join all chunks
        context = "\n\n".join(context_parts)
        
        logger.info(
            f"Built context: {len(context_parts)} chunks, {total_tokens} tokens"
        )
        
        return context, total_tokens
    
    def _format_chunk(self, chunk: dict[str, Any]) -> str:
        """
        Format chunk with metadata prefix.
        
        Args:
            chunk: Chunk dictionary
            
        Returns:
            Formatted chunk string
        """
        chunk_id = chunk.get("chunk_id", "unknown")
        source = chunk.get("source", "unknown")
        page = chunk.get("page_number")
        text = chunk.get("text", "")
        
        # Build metadata prefix
        metadata = f"[CHUNK: {chunk_id} | SOURCE: {source}"
        if page:
            metadata += f" | PAGE: {page}"
        metadata += "]"
        
        return f"{metadata}\n{text}"
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count
            
        Returns:
            Number of tokens
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters
            return len(text) // 4
    
    def build_prompt(
        self,
        query: str,
        context: str
    ) -> str:
        """
        Build final prompt for LLM.
        
        Args:
            query: User query
            context: Assembled context
            
        Returns:
            Complete prompt string
        """
        prompt = f"""Context:
{context}

Question: {query}

Answer (cite sources using chunk IDs):"""
        
        return prompt
