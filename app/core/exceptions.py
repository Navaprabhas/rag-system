"""
Custom exceptions and error handlers for the application.
"""
from typing import Any
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class RAGException(Exception):
    """Base exception for RAG system."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DocumentProcessingError(RAGException):
    """Raised when document processing fails."""
    pass


class EmbeddingError(RAGException):
    """Raised when embedding generation fails."""
    pass


class RetrievalError(RAGException):
    """Raised when retrieval fails."""
    pass


class LLMError(RAGException):
    """Raised when LLM generation fails."""
    pass


class InsufficientContextError(RAGException):
    """Raised when retrieved context is insufficient."""
    pass


class ConfigurationError(RAGException):
    """Raised when configuration is invalid."""
    pass


async def rag_exception_handler(request: Request, exc: RAGException) -> JSONResponse:
    """
    Handle RAG-specific exceptions.
    
    Args:
        request: FastAPI request object
        exc: RAG exception instance
        
    Returns:
        JSON response with error details
    """
    logger.error(
        f"RAG Exception: {exc.message}",
        extra={
            "exception_type": type(exc).__name__,
            "details": exc.details,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "details": exc.details
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.
    
    Args:
        request: FastAPI request object
        exc: HTTP exception instance
        
    Returns:
        JSON response with error details
    """
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception instance
        
    Returns:
        JSON response with error details
    """
    logger.error(
        f"Unexpected Exception: {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if logger.level == 10 else None  # Show details only in DEBUG
        }
    )
