"""
Request models for API endpoints.
"""
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    
    source_type: Literal["file", "url", "text"] = Field(
        description="Type of source to ingest"
    )
    content: str | None = Field(
        default=None,
        description="Text content for direct ingestion"
    )
    url: HttpUrl | None = Field(
        default=None,
        description="URL to fetch and ingest"
    )
    filename: str | None = Field(
        default=None,
        description="Filename for uploaded file"
    )
    metadata: dict[str, str] | None = Field(
        default=None,
        description="Additional metadata for the document"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_type": "url",
                "url": "https://example.com/document.pdf",
                "metadata": {"category": "technical", "author": "John Doe"}
            }
        }


class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    
    query: str = Field(
        min_length=1,
        max_length=1000,
        description="User query to answer"
    )
    llm_provider: Literal["ollama", "openai", "anthropic"] | None = Field(
        default=None,
        description="Override default LLM provider"
    )
    model_name: str | None = Field(
        default=None,
        description="Override default model name"
    )
    top_k: int | None = Field(
        default=None,
        ge=1,
        le=50,
        description="Number of chunks to retrieve"
    )
    rerank_top_n: int | None = Field(
        default=None,
        ge=1,
        le=20,
        description="Number of chunks after reranking"
    )
    filters: dict[str, str] | None = Field(
        default=None,
        description="Metadata filters for retrieval"
    )
    stream: bool = Field(
        default=False,
        description="Enable streaming response"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main features of the product?",
                "llm_provider": "ollama",
                "model_name": "llama3",
                "top_k": 10,
                "rerank_top_n": 5,
                "stream": False
            }
        }


class DocumentFilter(BaseModel):
    """Filter model for document queries."""
    
    filename: str | None = None
    source: str | None = None
    file_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None
