"""
Tests for RAG service integration.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.rag_service import RAGService
from app.models.response import RAGResponse


@pytest.mark.asyncio
class TestRAGService:
    """Test RAG service integration."""
    
    @patch('app.services.rag_service.Embedder')
    @patch('app.services.rag_service.QdrantManager')
    @patch('app.services.rag_service.QueryRewriter')
    @patch('app.services.rag_service.Reranker')
    async def test_query_with_fallback(
        self,
        mock_reranker,
        mock_rewriter,
        mock_qdrant,
        mock_embedder
    ):
        """Test query that should return fallback message."""
        # Setup mocks
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_text = AsyncMock(return_value=[0.1] * 768)
        mock_embedder.return_value = mock_embedder_instance
        
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search = AsyncMock(return_value=[])  # No results
        mock_qdrant.return_value = mock_qdrant_instance
        
        mock_rewriter_instance = Mock()
        mock_rewriter_instance.rewrite_query = AsyncMock(return_value=["test query"])
        mock_rewriter.return_value = mock_rewriter_instance
        
        # Create service
        service = RAGService()
        
        # Execute query
        response = await service.query("test query")
        
        # Verify fallback
        assert isinstance(response, RAGResponse)
        assert "don't have enough information" in response.answer
        assert response.confidence < 0.5
        assert len(response.citations) == 0
    
    def test_get_llm_ollama(self):
        """Test LLM provider selection - Ollama."""
        service = RAGService()
        
        llm = service._get_llm("ollama", "llama3")
        
        assert llm.provider_name == "ollama"
        assert llm.model_name == "llama3"
    
    def test_build_citations(self):
        """Test citation building."""
        service = RAGService()
        
        chunks = [
            {
                "chunk_id": "c1",
                "source": "doc.pdf",
                "page_number": 1,
                "text": "This is a test chunk with some content that is longer than 120 characters to test the excerpt truncation functionality",
                "score": 0.9
            }
        ]
        
        citations = service._build_citations(chunks)
        
        assert len(citations) == 1
        assert citations[0].source == "doc.pdf"
        assert citations[0].chunk_id == "c1"
        assert citations[0].page == 1
        assert len(citations[0].excerpt) <= 123  # 120 + "..."
        assert citations[0].score == 0.9


@pytest.mark.asyncio
class TestRAGServiceIntegration:
    """Integration tests for RAG service."""
    
    async def test_citation_structure(self):
        """Test that citations have correct structure."""
        from app.models.response import CitationItem
        
        citation = CitationItem(
            source="test.pdf",
            chunk_id="c1",
            page=1,
            excerpt="Test excerpt",
            score=0.9
        )
        
        assert citation.source == "test.pdf"
        assert citation.chunk_id == "c1"
        assert citation.page == 1
        assert citation.excerpt == "Test excerpt"
        assert citation.score == 0.9
