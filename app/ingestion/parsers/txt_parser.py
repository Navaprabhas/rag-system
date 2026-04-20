"""
Plain text document parser with encoding detection.
"""
import hashlib
from pathlib import Path
from typing import Any

import chardet

from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger


class TXTParser:
    """Parse plain text documents with automatic encoding detection."""
    
    def __init__(self):
        """Initialize TXT parser."""
        self.supported_extensions = [".txt", ".md", ".rst", ".log"]
    
    def parse(self, file_path: Path) -> dict[str, Any]:
        """
        Parse text file with encoding detection.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary containing text content and metadata
            
        Raises:
            DocumentProcessingError: If parsing fails
        """
        try:
            logger.info(f"Parsing text file: {file_path}")
            
            # Detect encoding
            encoding = self._detect_encoding(file_path)
            logger.debug(f"Detected encoding: {encoding}")
            
            # Read file with detected encoding
            with open(file_path, "r", encoding=encoding) as f:
                text = f.read()
            
            # Clean text: normalize whitespace
            text = " ".join(text.split())
            
            return {
                "text": text,
                "pages": [{"page_number": 1, "text": text}],
                "metadata": {
                    "encoding": encoding,
                    "file_size": file_path.stat().st_size,
                    "file_hash": self._compute_hash(file_path)
                }
            }
            
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to parse text file: {file_path}",
                details={"error": str(e)}
            )
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected encoding name
        """
        with open(file_path, "rb") as f:
            raw_data = f.read(10000)  # Read first 10KB for detection
        
        result = chardet.detect(raw_data)
        encoding = result.get("encoding", "utf-8")
        
        # Fallback to utf-8 if detection fails
        if not encoding or result.get("confidence", 0) < 0.7:
            encoding = "utf-8"
        
        return encoding
    
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
