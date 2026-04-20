"""
Re-ranking retrieved chunks using cross-encoder models.
"""
from typing import Any

from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.core.logging import logger


class Reranker:
    """Re-rank retrieved chunks using cross-encoder."""
    
    def __init__(self):
        """Initialize reranker with cross-encoder model."""
        try:
            self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Initialized cross-encoder reranker")
        except Exception as e:
            logger.warning(f"Failed to load cross-encoder: {e}")
            self.model = None
    
    async def rerank(
        self,
        query: str,
        chunks: list[dict[str, Any]],
        top_n: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Re-rank chunks based on relevance to query.
        
        Args:
            query: User query
            chunks: List of retrieved chunks
            top_n: Number of top chunks to return
            
        Returns:
            Re-ranked list of chunks
        """
        if not self.model or not chunks:
            return chunks[:top_n] if top_n else chunks
        
        try:
            top_n = top_n or settings.rerank_top_n
            
            # Prepare pairs for cross-encoder
            pairs = [[query, chunk["text"]] for chunk in chunks]
            
            # Get scores
            scores = self.model.predict(pairs)
            
            # Add scores to chunks and sort
            for chunk, score in zip(chunks, scores):
                chunk["rerank_score"] = float(score)
                # Update the main score with rerank score
                chunk["score"] = float(score)
            
            # Sort by rerank score
            reranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
            
            # Return top N
            result = reranked[:top_n]
            
            logger.info(f"Reranked {len(chunks)} chunks, returning top {len(result)}")
            return result
            
        except Exception as e:
            logger.warning(f"Reranking failed: {e}, returning original order")
            return chunks[:top_n] if top_n else chunks
