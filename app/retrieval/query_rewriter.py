"""
Query rewriting for improved retrieval using LLM.
"""
from typing import Any

import ollama

from app.core.config import settings
from app.core.logging import logger


class QueryRewriter:
    """Rewrite queries into multiple variations for better retrieval."""
    
    def __init__(self):
        """Initialize query rewriter."""
        self.model = settings.ollama_llm_model
    
    async def rewrite_query(self, query: str) -> list[str]:
        """
        Rewrite query into 2-3 alternative phrasings.
        
        Args:
            query: Original user query
            
        Returns:
            List of query variations (including original)
        """
        try:
            prompt = f"""Given the following question, generate 2 alternative phrasings that preserve the original meaning but use different words. Keep them concise.

Original question: {query}

Alternative phrasings (one per line):"""
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={"temperature": 0.3, "num_predict": 150}
            )
            
            # Parse response
            alternatives = []
            lines = response["response"].strip().split("\n")
            
            for line in lines:
                line = line.strip()
                # Remove numbering and bullet points
                line = line.lstrip("0123456789.-) ")
                if line and len(line) > 10:
                    alternatives.append(line)
            
            # Limit to 2 alternatives
            alternatives = alternatives[:2]
            
            # Always include original query
            queries = [query] + alternatives
            
            logger.info(f"Rewrote query into {len(queries)} variations")
            return queries
            
        except Exception as e:
            logger.warning(f"Query rewriting failed: {e}, using original query")
            return [query]
