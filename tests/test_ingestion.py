"""
Tests for document ingestion pipeline.
"""
import pytest
from pathlib import Path

from app.ingestion.chunker import SemanticChunker


class TestSemanticChunker:
    """Test semantic chunker functionality."""
    
    def test_chunk_document(self):
        """Test basic document chunking."""
        chunker = SemanticChunker(chunk_size=100, chunk_overlap=20)
        
        text = "This is a test document. " * 50  # Create long text
        metadata = {
            "filename": "test.txt",
            "file_type": "txt"
        }
        
        chunks = chunker.chunk_document(text, metadata)
        
        assert len(chunks) > 0
        assert all("chunk_id" in chunk for chunk in chunks)
        assert all("text" in chunk for chunk in chunks)
        assert all("content_hash" in chunk for chunk in chunks)
    
    def test_deduplication(self):
        """Test chunk deduplication."""
        chunker = SemanticChunker()
        
        chunks = [
            {"chunk_id": "1", "content_hash": "hash1", "text": "text1"},
            {"chunk_id": "2", "content_hash": "hash2", "text": "text2"},
            {"chunk_id": "3", "content_hash": "hash1", "text": "text1"},  # Duplicate
        ]
        
        existing_hashes = set()
        unique_chunks = chunker.deduplicate_chunks(chunks, existing_hashes)
        
        assert len(unique_chunks) == 2
        assert unique_chunks[0]["chunk_id"] == "1"
        assert unique_chunks[1]["chunk_id"] == "2"
    
    def test_token_counting(self):
        """Test token counting."""
        chunker = SemanticChunker()
        
        text = "This is a test"
        token_count = chunker._count_tokens(text)
        
        assert token_count > 0
        assert isinstance(token_count, int)


@pytest.mark.asyncio
class TestParsers:
    """Test document parsers."""
    
    def test_txt_parser_encoding_detection(self):
        """Test TXT parser encoding detection."""
        from app.ingestion.parsers.txt_parser import TXTParser
        
        parser = TXTParser()
        
        # Test supported extensions
        assert ".txt" in parser.supported_extensions
        assert ".md" in parser.supported_extensions
