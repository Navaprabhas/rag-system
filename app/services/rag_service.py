"""
Main RAG service orchestrating the complete pipeline.
"""
from typing import Any, AsyncIterator
import json

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import InsufficientContextError
from app.retrieval.embedder import Embedder
from app.retrieval.qdrant_client import QdrantManager
from app.retrieval.query_rewriter import QueryRewriter
from app.retrieval.reranker import Reranker
from app.services.context_builder import ContextBuilder
from app.services.anti_hallucination import AntiHallucinationEngine
from app.llm.ollama_llm import OllamaLLM
from app.llm.openai_llm import OpenAILLM
from app.llm.anthropic_llm import AnthropicLLM
from app.models.response import RAGResponse, CitationItem


class RAGService:
    """Complete RAG pipeline with anti-hallucination guarantees."""
    
    def __init__(self):
        """Initialize RAG service with all components."""
        self.embedder = Embedder()
        self.qdrant = QdrantManager()
        self.query_rewriter = QueryRewriter()
        self.reranker = Reranker()
        self.context_builder = ContextBuilder()
        self.anti_hallucination = AntiHallucinationEngine()
        
        logger.info("Initialized RAG service")
    
    def _get_llm(self, provider: str | None, model_name: str | None):
        """
        Get LLM instance based on provider.
        
        Args:
            provider: LLM provider name
            model_name: Model name
            
        Returns:
            LLM instance
        """
        provider = provider or settings.llm_provider
        
        if provider == "ollama":
            return OllamaLLM(model_name)
        elif provider == "openai":
            return OpenAILLM(model_name)
        elif provider == "anthropic":
            return AnthropicLLM(model_name)
        else:
            logger.warning(f"Unknown provider {provider}, using Ollama")
            return OllamaLLM(model_name)
    
    async def query(
        self,
        query: str,
        llm_provider: str | None = None,
        model_name: str | None = None,
        top_k: int | None = None,
        rerank_top_n: int | None = None,
        filters: dict[str, str] | None = None
    ) -> RAGResponse:
        """
        Execute complete RAG pipeline.
        
        Args:
            query: User query
            llm_provider: Optional LLM provider override
            model_name: Optional model name override
            top_k: Number of chunks to retrieve
            rerank_top_n: Number of chunks after reranking
            filters: Optional metadata filters
            
        Returns:
            RAG response with answer and citations
        """
        logger.info(f"Processing query: {query[:100]}...")
        
        # Step 1: Query rewriting
        query_variations = await self.query_rewriter.rewrite_query(query)
        logger.info(f"Generated {len(query_variations)} query variations")
        
        # Step 2: Dense retrieval for all query variations
        all_chunks = []
        for query_var in query_variations:
            query_embedding = await self.embedder.embed_text(query_var)
            chunks = await self.qdrant.search(
                query_vector=query_embedding,
                top_k=top_k or settings.top_k,
                filters=filters
            )
            all_chunks.extend(chunks)
        
        # Deduplicate chunks by chunk_id
        unique_chunks = {}
        for chunk in all_chunks:
            chunk_id = chunk["chunk_id"]
            if chunk_id not in unique_chunks:
                unique_chunks[chunk_id] = chunk
            else:
                # Keep the one with higher score
                if chunk["score"] > unique_chunks[chunk_id]["score"]:
                    unique_chunks[chunk_id] = chunk
        
        chunks = list(unique_chunks.values())
        logger.info(f"Retrieved {len(chunks)} unique chunks")
        
        # Step 3: Re-ranking
        chunks = await self.reranker.rerank(
            query=query,
            chunks=chunks,
            top_n=rerank_top_n or settings.rerank_top_n
        )
        
        # Step 4: Context assembly
        context, total_tokens = self.context_builder.build_context(chunks, query)
        
        # Step 5: Anti-hallucination checks
        confidence = self.anti_hallucination.compute_confidence(chunks)
        
        should_fallback, fallback_reason = self.anti_hallucination.should_return_fallback(
            chunks=chunks,
            total_tokens=total_tokens,
            confidence=confidence
        )
        
        if should_fallback:
            logger.warning(f"Returning fallback: {fallback_reason}")
            return RAGResponse(
                answer=self.anti_hallucination.FALLBACK_MESSAGE,
                citations=[],
                confidence=confidence,
                retrieval_count=len(chunks),
                query_rewritten=" | ".join(query_variations),
                llm_provider=llm_provider or settings.llm_provider,
                model=model_name or "N/A"
            )
        
        # Step 6: LLM generation
        llm = self._get_llm(llm_provider, model_name)
        system_prompt = self.anti_hallucination.get_system_prompt()
        prompt = self.context_builder.build_prompt(query, context)
        
        answer = await llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=1000
        )
        
        # Step 7: Build citations
        citations = self._build_citations(chunks)
        
        # Step 8: Validate citations
        citations_valid, citation_error = self.anti_hallucination.validate_citations(
            answer, citations
        )
        
        if not citations_valid:
            logger.warning(f"Citation validation failed: {citation_error}")
            return RAGResponse(
                answer=self.anti_hallucination.FALLBACK_MESSAGE,
                citations=[],
                confidence=confidence,
                retrieval_count=len(chunks),
                query_rewritten=" | ".join(query_variations),
                llm_provider=llm.provider_name,
                model=llm.model_name
            )
        
        # Return successful response
        return RAGResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            retrieval_count=len(chunks),
            query_rewritten=" | ".join(query_variations),
            llm_provider=llm.provider_name,
            model=llm.model_name
        )
    
    async def query_stream(
        self,
        query: str,
        llm_provider: str | None = None,
        model_name: str | None = None,
        top_k: int | None = None,
        rerank_top_n: int | None = None,
        filters: dict[str, str] | None = None
    ) -> AsyncIterator[str]:
        """
        Execute RAG pipeline with streaming response.
        
        Args:
            query: User query
            llm_provider: Optional LLM provider override
            model_name: Optional model name override
            top_k: Number of chunks to retrieve
            rerank_top_n: Number of chunks after reranking
            filters: Optional metadata filters
            
        Yields:
            JSON strings with response chunks
        """
        logger.info(f"Processing streaming query: {query[:100]}...")
        
        # Steps 1-5: Same as non-streaming (retrieval and validation)
        query_variations = await self.query_rewriter.rewrite_query(query)
        
        all_chunks = []
        for query_var in query_variations:
            query_embedding = await self.embedder.embed_text(query_var)
            chunks = await self.qdrant.search(
                query_vector=query_embedding,
                top_k=top_k or settings.top_k,
                filters=filters
            )
            all_chunks.extend(chunks)
        
        unique_chunks = {}
        for chunk in all_chunks:
            chunk_id = chunk["chunk_id"]
            if chunk_id not in unique_chunks:
                unique_chunks[chunk_id] = chunk
            else:
                if chunk["score"] > unique_chunks[chunk_id]["score"]:
                    unique_chunks[chunk_id] = chunk
        
        chunks = list(unique_chunks.values())
        chunks = await self.reranker.rerank(query, chunks, rerank_top_n or settings.rerank_top_n)
        
        context, total_tokens = self.context_builder.build_context(chunks, query)
        confidence = self.anti_hallucination.compute_confidence(chunks)
        
        should_fallback, fallback_reason = self.anti_hallucination.should_return_fallback(
            chunks, total_tokens, confidence
        )
        
        # Send metadata first
        metadata = {
            "type": "metadata",
            "confidence": confidence,
            "retrieval_count": len(chunks),
            "query_rewritten": " | ".join(query_variations)
        }
        yield f"data: {json.dumps(metadata)}\n\n"
        
        if should_fallback:
            fallback_data = {
                "type": "answer",
                "content": self.anti_hallucination.FALLBACK_MESSAGE
            }
            yield f"data: {json.dumps(fallback_data)}\n\n"
            return
        
        # Stream LLM response
        llm = self._get_llm(llm_provider, model_name)
        system_prompt = self.anti_hallucination.get_system_prompt()
        prompt = self.context_builder.build_prompt(query, context)
        
        async for chunk_text in llm.generate_stream(prompt, system_prompt):
            chunk_data = {
                "type": "answer",
                "content": chunk_text
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"
        
        # Send citations at the end
        citations = self._build_citations(chunks)
        citations_data = {
            "type": "citations",
            "citations": [c.model_dump() for c in citations]
        }
        yield f"data: {json.dumps(citations_data)}\n\n"
    
    def _build_citations(self, chunks: list[dict[str, Any]]) -> list[CitationItem]:
        """
        Build citation items from chunks.
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            List of citation items
        """
        citations = []
        
        for chunk in chunks:
            excerpt = chunk["text"][:120]
            if len(chunk["text"]) > 120:
                excerpt += "..."
            
            citation = CitationItem(
                source=chunk["source"],
                chunk_id=chunk["chunk_id"],
                page=chunk.get("page_number"),
                excerpt=excerpt,
                score=chunk.get("score", 0.0)
            )
            citations.append(citation)
        
        return citations
