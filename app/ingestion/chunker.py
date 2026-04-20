"""
Text chunking with semantic-aware splitting and deduplication.
"""
import hashlib
from typing import Any
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

from app.core.config import settings
from app.core.logging import logger


class SemanticChunker:
    """Semantic-aware text chunker with deduplication."""
    
    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None
    ):
        """
        Initialize semantic chunker.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            logger.warning("Failed to load tiktoken, using approximate counting")
            self.tokenizer = None
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )
        
        logger.info(
            f"Initialized chunker: size={self.chunk_size}, overlap={self.chunk_overlap}"
        )
    
    def chunk_document(
        self,
        text: str,
        metadata: dict[str, Any],
        pages: list[dict[str, Any]] | None = None
    ) -> list[dict[str, Any]]:
        """
        Chunk document into semantic units with metadata.
        
        Args:
            text: Full document text
            metadata: Document metadata
            pages: Optional page-level information
            
        Returns:
            List of chunk dictionaries with metadata
        """
        logger.info(f"Chunking document: {metadata.get('filename', 'unknown')}")
        
        # Split text into chunks
        text_chunks = self.text_splitter.split_text(text)
        
        # Create chunk objects with metadata
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            # Compute chunk hash for deduplication
            chunk_hash = self._compute_hash(chunk_text)
            
            # Determine page number if available
            page_number = self._find_page_number(chunk_text, pages) if pages else None
            
            chunk = {
                "chunk_id": f"{metadata.get('filename', 'doc')}_{idx}",
                "text": chunk_text,
                "chunk_index": idx,
                "content_hash": chunk_hash,
                "source": metadata.get("filename", ""),
                "source_url": metadata.get("url", ""),
                "file_type": metadata.get("file_type", ""),
                "page_number": page_number,
                "ingestion_timestamp": datetime.utcnow().isoformat(),
                "token_count": self._count_tokens(chunk_text),
                "metadata": metadata
            }
            
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters
            return len(text) // 4
    
    def _compute_hash(self, text: str) -> str:
        """
        Compute SHA256 hash of text.
        
        Args:
            text: Text to hash
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _find_page_number(
        self,
        chunk_text: str,
        pages: list[dict[str, Any]]
    ) -> int | None:
        """
        Find page number for chunk by matching text.
        
        Args:
            chunk_text: Chunk text
            pages: List of page dictionaries
            
        Returns:
            Page number or None
        """
        if not pages:
            return None
        
        # Find the page that contains the beginning of this chunk
        chunk_start = chunk_text[:100]  # Use first 100 chars for matching
        
        for page in pages:
            if chunk_start in page.get("text", ""):
                return page.get("page_number")
        
        # Default to first page if no match
        return pages[0].get("page_number") if pages else None
    
    def deduplicate_chunks(
        self,
        chunks: list[dict[str, Any]],
        existing_hashes: set[str]
    ) -> list[dict[str, Any]]:
        """
        Remove duplicate chunks based on content hash.
        
        Args:
            chunks: List of chunk dictionaries
            existing_hashes: Set of existing content hashes
            
        Returns:
            Deduplicated list of chunks
        """
        unique_chunks = []
        seen_hashes = existing_hashes.copy()
        
        for chunk in chunks:
            chunk_hash = chunk["content_hash"]
            if chunk_hash not in seen_hashes:
                unique_chunks.append(chunk)
                seen_hashes.add(chunk_hash)
            else:
                logger.debug(f"Skipping duplicate chunk: {chunk['chunk_id']}")
        
        logger.info(
            f"Deduplication: {len(chunks)} -> {len(unique_chunks)} chunks"
        )
        return unique_chunks
