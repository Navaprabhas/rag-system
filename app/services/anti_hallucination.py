"""
Anti-hallucination engine with strict validation checks.
"""
from typing import Any

from app.core.config import settings
from app.core.exceptions import InsufficientContextError
from app.core.logging import logger


class AntiHallucinationEngine:
    """Enforce strict anti-hallucination checks."""
    
    FALLBACK_MESSAGE = "I don't have enough information from the provided sources"
    
    def __init__(self):
        """Initialize anti-hallucination engine."""
        self.confidence_threshold = settings.confidence_threshold
        self.min_similarity_score = 0.35
        self.min_context_tokens = 50
    
    def validate_context(
        self,
        chunks: list[dict[str, Any]],
        total_tokens: int
    ) -> tuple[bool, str | None]:
        """
        CHECK 1: Context sufficiency gate.
        
        Args:
            chunks: Retrieved chunks
            total_tokens: Total context tokens
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if any chunks retrieved
        if not chunks or len(chunks) == 0:
            logger.warning("Context validation failed: no chunks retrieved")
            return False, "No relevant documents found"
        
        # Check maximum similarity score
        max_score = max(chunk.get("score", 0.0) for chunk in chunks)
        if max_score < self.min_similarity_score:
            logger.warning(
                f"Context validation failed: max score {max_score} < {self.min_similarity_score}"
            )
            return False, f"Retrieved documents not relevant enough (score: {max_score:.2f})"
        
        # Check total context tokens
        if total_tokens < self.min_context_tokens:
            logger.warning(
                f"Context validation failed: {total_tokens} tokens < {self.min_context_tokens}"
            )
            return False, "Insufficient context retrieved"
        
        logger.info("Context validation passed")
        return True, None
    
    def compute_confidence(self, chunks: list[dict[str, Any]]) -> float:
        """
        CHECK 2: Confidence scoring.
        
        Args:
            chunks: Retrieved chunks with scores
            
        Returns:
            Confidence score (0.0-1.0)
        """
        if not chunks:
            return 0.0
        
        # Take mean of top 3 scores
        top_scores = sorted(
            [chunk.get("score", 0.0) for chunk in chunks],
            reverse=True
        )[:3]
        
        confidence = sum(top_scores) / len(top_scores) if top_scores else 0.0
        
        logger.info(f"Computed confidence: {confidence:.3f}")
        return confidence
    
    def validate_confidence(self, confidence: float) -> tuple[bool, str | None]:
        """
        Validate confidence meets threshold.
        
        Args:
            confidence: Computed confidence score
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if confidence < self.confidence_threshold:
            logger.warning(
                f"Confidence validation failed: {confidence:.3f} < {self.confidence_threshold}"
            )
            return False, f"Confidence too low ({confidence:.2f})"
        
        logger.info("Confidence validation passed")
        return True, None
    
    def validate_citations(
        self,
        answer: str,
        citations: list[dict[str, Any]]
    ) -> tuple[bool, str | None]:
        """
        CHECK 3: Citation enforcement.
        
        Args:
            answer: Generated answer
            citations: List of citations
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if answer is the fallback message
        if answer.strip() == self.FALLBACK_MESSAGE:
            # Fallback message doesn't need citations
            return True, None
        
        # Check if citations exist
        if not citations or len(citations) == 0:
            logger.warning("Citation validation failed: no citations provided")
            return False, "No citations attached to answer"
        
        # Validate citation structure
        for citation in citations:
            required_fields = ["source", "chunk_id", "excerpt"]
            if not all(field in citation for field in required_fields):
                logger.warning("Citation validation failed: missing required fields")
                return False, "Invalid citation structure"
        
        logger.info(f"Citation validation passed: {len(citations)} citations")
        return True, None
    
    def should_return_fallback(
        self,
        chunks: list[dict[str, Any]],
        total_tokens: int,
        confidence: float
    ) -> tuple[bool, str]:
        """
        Determine if fallback message should be returned.
        
        Args:
            chunks: Retrieved chunks
            total_tokens: Total context tokens
            confidence: Confidence score
            
        Returns:
            Tuple of (should_fallback, reason)
        """
        # Run all checks
        context_valid, context_error = self.validate_context(chunks, total_tokens)
        if not context_valid:
            return True, context_error or "Context validation failed"
        
        confidence_valid, confidence_error = self.validate_confidence(confidence)
        if not confidence_valid:
            return True, confidence_error or "Confidence too low"
        
        return False, ""
    
    def get_system_prompt(self) -> str:
        """
        CHECK 4: Get strict system prompt that forbids external knowledge.
        
        Returns:
            System prompt string
        """
        return """You are a strict document QA assistant.

CRITICAL RULES:
1. Answer ONLY using the context provided below
2. If the answer is not found in the context, respond EXACTLY: "I don't have enough information from the provided sources"
3. Do not use any knowledge outside the provided context
4. Always cite sources using the chunk IDs provided in [CHUNK: ...] markers
5. Be precise and factual
6. If you're uncertain, say so

Your responses must be grounded entirely in the provided context."""
