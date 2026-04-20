"""
Tests for retrieval pipeline.
"""
import pytest

from app.services.context_builder import ContextBuilder
from app.services.anti_hallucination import AntiHallucinationEngine


class TestContextBuilder:
    """Test context builder functionality."""
    
    def test_build_context(self):
        """Test context building from chunks."""
        builder = ContextBuilder()
        
        chunks = [
            {
                "chunk_id": "c1",
                "source": "doc.pdf",
                "page_number": 1,
                "text": "This is chunk 1",
                "score": 0.9
            },
            {
                "chunk_id": "c2",
                "source": "doc.pdf",
                "page_number": 2,
                "text": "This is chunk 2",
                "score": 0.8
            }
        ]
        
        context, total_tokens = builder.build_context(chunks, "test query")
        
        assert len(context) > 0
        assert "c1" in context
        assert "c2" in context
        assert total_tokens > 0
    
    def test_format_chunk(self):
        """Test chunk formatting."""
        builder = ContextBuilder()
        
        chunk = {
            "chunk_id": "test_1",
            "source": "test.pdf",
            "page_number": 5,
            "text": "Test content"
        }
        
        formatted = builder._format_chunk(chunk)
        
        assert "[CHUNK: test_1" in formatted
        assert "SOURCE: test.pdf" in formatted
        assert "PAGE: 5" in formatted
        assert "Test content" in formatted


class TestAntiHallucinationEngine:
    """Test anti-hallucination validation."""
    
    def test_validate_context_no_chunks(self):
        """Test context validation with no chunks."""
        engine = AntiHallucinationEngine()
        
        is_valid, error = engine.validate_context([], 0)
        
        assert not is_valid
        assert error is not None
    
    def test_validate_context_low_score(self):
        """Test context validation with low similarity score."""
        engine = AntiHallucinationEngine()
        
        chunks = [{"score": 0.2}]
        is_valid, error = engine.validate_context(chunks, 100)
        
        assert not is_valid
        assert "not relevant enough" in error
    
    def test_validate_context_success(self):
        """Test successful context validation."""
        engine = AntiHallucinationEngine()
        
        chunks = [{"score": 0.8}, {"score": 0.7}]
        is_valid, error = engine.validate_context(chunks, 100)
        
        assert is_valid
        assert error is None
    
    def test_compute_confidence(self):
        """Test confidence computation."""
        engine = AntiHallucinationEngine()
        
        chunks = [
            {"score": 0.9},
            {"score": 0.8},
            {"score": 0.7}
        ]
        
        confidence = engine.compute_confidence(chunks)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should be high for good scores
    
    def test_validate_citations(self):
        """Test citation validation."""
        engine = AntiHallucinationEngine()
        
        # Valid citations
        citations = [
            {
                "source": "doc.pdf",
                "chunk_id": "c1",
                "excerpt": "Test excerpt"
            }
        ]
        
        is_valid, error = engine.validate_citations("Answer text", citations)
        assert is_valid
        
        # No citations
        is_valid, error = engine.validate_citations("Answer text", [])
        assert not is_valid
    
    def test_should_return_fallback(self):
        """Test fallback decision logic."""
        engine = AntiHallucinationEngine()
        
        # Good context
        chunks = [{"score": 0.8}]
        should_fallback, reason = engine.should_return_fallback(chunks, 100, 0.8)
        assert not should_fallback
        
        # Low confidence
        should_fallback, reason = engine.should_return_fallback(chunks, 100, 0.2)
        assert should_fallback
        assert "Confidence" in reason
