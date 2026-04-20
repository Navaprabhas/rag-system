"""
PDF document parser using PyMuPDF and pdfplumber.
"""
import hashlib
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pdfplumber

from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger


class PDFParser:
    """Parse PDF documents and extract clean text."""
    
    def __init__(self):
        """Initialize PDF parser."""
        self.supported_extensions = [".pdf"]
    
    def parse(self, file_path: Path) -> dict[str, Any]:
        """
        Parse PDF file and extract text with metadata.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing text content and metadata
            
        Raises:
            DocumentProcessingError: If parsing fails
        """
        try:
            logger.info(f"Parsing PDF: {file_path}")
            
            # Try PyMuPDF first (faster)
            try:
                return self._parse_with_pymupdf(file_path)
            except Exception as e:
                logger.warning(f"PyMuPDF failed, trying pdfplumber: {e}")
                return self._parse_with_pdfplumber(file_path)
                
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to parse PDF: {file_path}",
                details={"error": str(e)}
            )
    
    def _parse_with_pymupdf(self, file_path: Path) -> dict[str, Any]:
        """
        Parse PDF using PyMuPDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted content and metadata
        """
        doc = fitz.open(file_path)
        
        pages_content = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            # Clean text: remove excessive whitespace
            text = " ".join(text.split())
            
            if text.strip():
                pages_content.append({
                    "page_number": page_num,
                    "text": text
                })
        
        # Extract metadata
        metadata = doc.metadata or {}
        
        doc.close()
        
        # Combine all text
        full_text = "\n\n".join([p["text"] for p in pages_content])
        
        return {
            "text": full_text,
            "pages": pages_content,
            "metadata": {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "page_count": len(pages_content),
                "file_hash": self._compute_hash(file_path)
            }
        }
    
    def _parse_with_pdfplumber(self, file_path: Path) -> dict[str, Any]:
        """
        Parse PDF using pdfplumber (fallback method).
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted content and metadata
        """
        pages_content = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                # Clean text
                text = " ".join(text.split())
                
                if text.strip():
                    pages_content.append({
                        "page_number": page_num,
                        "text": text
                    })
            
            # Extract metadata
            metadata = pdf.metadata or {}
        
        # Combine all text
        full_text = "\n\n".join([p["text"] for p in pages_content])
        
        return {
            "text": full_text,
            "pages": pages_content,
            "metadata": {
                "title": metadata.get("Title", ""),
                "author": metadata.get("Author", ""),
                "subject": metadata.get("Subject", ""),
                "page_count": len(pages_content),
                "file_hash": self._compute_hash(file_path)
            }
        }
    
    def _compute_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
