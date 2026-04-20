"""
Web URL parser using trafilatura for clean text extraction.
"""
import hashlib
from typing import Any
from urllib.parse import urlparse

import httpx
import trafilatura
from bs4 import BeautifulSoup

from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger


class URLParser:
    """Parse web URLs and extract clean text content."""
    
    def __init__(self):
        """Initialize URL parser."""
        self.timeout = 30.0
    
    async def parse(self, url: str) -> dict[str, Any]:
        """
        Parse web URL and extract clean text.
        
        Args:
            url: URL to fetch and parse
            
        Returns:
            Dictionary containing text content and metadata
            
        Raises:
            DocumentProcessingError: If parsing fails
        """
        try:
            logger.info(f"Parsing URL: {url}")
            
            # Fetch content
            html_content = await self._fetch_url(url)
            
            # Try trafilatura first (best for article extraction)
            text = trafilatura.extract(
                html_content,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            # Fallback to BeautifulSoup if trafilatura fails
            if not text or len(text.strip()) < 100:
                logger.warning("Trafilatura extraction insufficient, using BeautifulSoup")
                text = self._extract_with_beautifulsoup(html_content)
            
            # Clean text
            text = " ".join(text.split())
            
            # Extract metadata
            metadata = self._extract_metadata(html_content, url)
            
            return {
                "text": text,
                "pages": [{"page_number": 1, "text": text}],
                "metadata": metadata
            }
            
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to parse URL: {url}",
                details={"error": str(e)}
            )
    
    async def _fetch_url(self, url: str) -> str:
        """
        Fetch HTML content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text
    
    def _extract_with_beautifulsoup(self, html_content: str) -> str:
        """
        Extract text using BeautifulSoup (fallback method).
        
        Args:
            html_content: HTML content
            
        Returns:
            Extracted text
        """
        soup = BeautifulSoup(html_content, "lxml")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator=" ", strip=True)
        
        return text
    
    def _extract_metadata(self, html_content: str, url: str) -> dict[str, Any]:
        """
        Extract metadata from HTML.
        
        Args:
            html_content: HTML content
            url: Source URL
            
        Returns:
            Metadata dictionary
        """
        soup = BeautifulSoup(html_content, "lxml")
        
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string or ""
        
        # Extract meta description
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"]
        
        # Extract author
        author = ""
        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author and meta_author.get("content"):
            author = meta_author["content"]
        
        # Parse domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        return {
            "title": title.strip(),
            "description": description.strip(),
            "author": author.strip(),
            "domain": domain,
            "url": url,
            "content_hash": hashlib.sha256(html_content.encode()).hexdigest()
        }
