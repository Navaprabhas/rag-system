"""
Dependency injection for API routes.
"""
from app.services.rag_service import RAGService
from app.retrieval.qdrant_client import QdrantManager
from app.retrieval.embedder import Embedder
from app.ingestion.chunker import SemanticChunker


# Singleton instances
_rag_service: RAGService | None = None
_qdrant_manager: QdrantManager | None = None
_embedder: Embedder | None = None
_chunker: SemanticChunker | None = None


def get_rag_service() -> RAGService:
    """Get RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


def get_qdrant_manager() -> QdrantManager:
    """Get Qdrant manager instance."""
    global _qdrant_manager
    if _qdrant_manager is None:
        _qdrant_manager = QdrantManager()
    return _qdrant_manager


def get_embedder() -> Embedder:
    """Get embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


def get_chunker() -> SemanticChunker:
    """Get chunker instance."""
    global _chunker
    if _chunker is None:
        _chunker = SemanticChunker()
    return _chunker
