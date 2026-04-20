"""
Response models for API endpoints.
"""
from typing import Any
from pydantic import BaseModel, Field


class CitationItem(BaseModel):
    """Citation information for a retrieved chunk."""
    
    source: str = Field(description="Source filename or URL")
    chunk_id: str = Field(description="Unique chunk identifier")
    page: int | None = Field(default=None, description="Page number if applicable")
    excerpt: str = Field(description="First 120 characters of the chunk")
    score: float = Field(description="Relevance score")


class RAGResponse(BaseModel):
    """Response model for RAG queries."""
    
    answer: str = Field(description="Generated answer")
    citations: list[CitationItem] = Field(
        default_factory=list,
        description="List of citations supporting the answer"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score for the answer"
    )
    retrieval_count: int = Field(description="Number of chunks retrieved")
    query_rewritten: str | None = Field(
        default=None,
        description="Rewritten query used for retrieval"
    )
    llm_provider: str = Field(description="LLM provider used")
    model: str = Field(description="Model name used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The main features include...",
                "citations": [
                    {
                        "source": "product_guide.pdf",
                        "chunk_id": "c_042",
                        "page": 3,
                        "excerpt": "The product offers advanced features such as...",
                        "score": 0.89
                    }
                ],
                "confidence": 0.87,
                "retrieval_count": 5,
                "query_rewritten": "product main features capabilities",
                "llm_provider": "ollama",
                "model": "llama3"
            }
        }


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    
    status: str = Field(description="Ingestion status")
    document_id: str = Field(description="Unique document identifier")
    chunks_created: int = Field(description="Number of chunks created")
    filename: str = Field(description="Document filename")
    file_type: str = Field(description="Document file type")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Document metadata"
    )


class DocumentInfo(BaseModel):
    """Information about an ingested document."""
    
    document_id: str
    filename: str
    file_type: str
    chunk_count: int
    ingestion_timestamp: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentListResponse(BaseModel):
    """Response model for document listing."""
    
    documents: list[DocumentInfo]
    total_count: int


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str
    version: str = "1.0.0"
    services: dict[str, str] = Field(
        default_factory=dict,
        description="Status of dependent services"
    )
