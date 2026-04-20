"""
Main FastAPI application.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    RAGException,
    rag_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from fastapi import HTTPException
from app.api.routes import health, query, ingest, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting RAG System...")
    
    # Create data directories
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.cache_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("RAG System started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG System...")


# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="Production-grade RAG system with anti-hallucination guarantees",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(RAGException, rag_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(
    health.router,
    prefix=settings.api_v1_prefix,
    tags=["health"]
)

app.include_router(
    query.router,
    prefix=settings.api_v1_prefix,
    tags=["query"]
)

app.include_router(
    ingest.router,
    prefix=settings.api_v1_prefix,
    tags=["ingest"]
)

app.include_router(
    documents.router,
    prefix=settings.api_v1_prefix,
    tags=["documents"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
