"""
Document ingestion endpoints.
"""
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status

from app.models.request import IngestRequest
from app.models.response import IngestResponse
from app.ingestion.parsers.pdf_parser import PDFParser
from app.ingestion.parsers.txt_parser import TXTParser
from app.ingestion.parsers.url_parser import URLParser
from app.ingestion.chunker import SemanticChunker
from app.retrieval.embedder import Embedder
from app.retrieval.qdrant_client import QdrantManager
from app.api.deps import get_embedder, get_qdrant_manager, get_chunker
from app.core.logging import logger
from app.core.exceptions import DocumentProcessingError

router = APIRouter()


@router.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    embedder: Embedder = Depends(get_embedder),
    qdrant: QdrantManager = Depends(get_qdrant_manager),
    chunker: SemanticChunker = Depends(get_chunker)
) -> IngestResponse:
    """
    Ingest a document file (PDF or TXT).
    
    Args:
        file: Uploaded file
        embedder: Embedder instance
        qdrant: Qdrant manager instance
        chunker: Chunker instance
        
    Returns:
        Ingestion response with document info
    """
    logger.info(f"Ingesting file: {file.filename}")
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".txt", ".md"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}"
        )
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)
    
    try:
        # Parse document
        if file_ext == ".pdf":
            parser = PDFParser()
        else:
            parser = TXTParser()
        
        parsed_data = parser.parse(tmp_path)
        
        # Add filename to metadata
        parsed_data["metadata"]["filename"] = file.filename
        parsed_data["metadata"]["file_type"] = file_ext.lstrip(".")
        
        # Chunk document
        existing_hashes = await qdrant.get_existing_hashes()
        chunks = chunker.chunk_document(
            text=parsed_data["text"],
            metadata=parsed_data["metadata"],
            pages=parsed_data.get("pages")
        )
        
        # Deduplicate
        chunks = chunker.deduplicate_chunks(chunks, existing_hashes)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All chunks are duplicates, document already ingested"
            )
        
        # Generate embeddings
        embeddings = await embedder.embed_batch([c["text"] for c in chunks])
        
        # Store in Qdrant
        await qdrant.upsert_chunks(chunks, embeddings)
        
        # Clean up temp file
        tmp_path.unlink()
        
        return IngestResponse(
            status="success",
            document_id=parsed_data["metadata"].get("file_hash", "unknown"),
            chunks_created=len(chunks),
            filename=file.filename,
            file_type=file_ext.lstrip("."),
            metadata=parsed_data["metadata"]
        )
        
    except Exception as e:
        # Clean up temp file on error
        if tmp_path.exists():
            tmp_path.unlink()
        raise


@router.post("/ingest/url", response_model=IngestResponse)
async def ingest_url(
    request: IngestRequest,
    embedder: Embedder = Depends(get_embedder),
    qdrant: QdrantManager = Depends(get_qdrant_manager),
    chunker: SemanticChunker = Depends(get_chunker)
) -> IngestResponse:
    """
    Ingest content from a URL.
    
    Args:
        request: Ingest request with URL
        embedder: Embedder instance
        qdrant: Qdrant manager instance
        chunker: Chunker instance
        
    Returns:
        Ingestion response with document info
    """
    if not request.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required"
        )
    
    logger.info(f"Ingesting URL: {request.url}")
    
    try:
        # Parse URL
        parser = URLParser()
        parsed_data = await parser.parse(str(request.url))
        
        # Add metadata
        parsed_data["metadata"]["filename"] = parsed_data["metadata"].get("domain", "web_page")
        parsed_data["metadata"]["file_type"] = "url"
        
        # Merge user metadata
        if request.metadata:
            parsed_data["metadata"].update(request.metadata)
        
        # Chunk document
        existing_hashes = await qdrant.get_existing_hashes()
        chunks = chunker.chunk_document(
            text=parsed_data["text"],
            metadata=parsed_data["metadata"],
            pages=parsed_data.get("pages")
        )
        
        # Deduplicate
        chunks = chunker.deduplicate_chunks(chunks, existing_hashes)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All chunks are duplicates, content already ingested"
            )
        
        # Generate embeddings
        embeddings = await embedder.embed_batch([c["text"] for c in chunks])
        
        # Store in Qdrant
        await qdrant.upsert_chunks(chunks, embeddings)
        
        return IngestResponse(
            status="success",
            document_id=parsed_data["metadata"].get("content_hash", "unknown"),
            chunks_created=len(chunks),
            filename=parsed_data["metadata"]["filename"],
            file_type="url",
            metadata=parsed_data["metadata"]
        )
        
    except Exception as e:
        logger.error(f"URL ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest URL: {str(e)}"
        )


@router.post("/ingest/text", response_model=IngestResponse)
async def ingest_text(
    request: IngestRequest,
    embedder: Embedder = Depends(get_embedder),
    qdrant: QdrantManager = Depends(get_qdrant_manager),
    chunker: SemanticChunker = Depends(get_chunker)
) -> IngestResponse:
    """
    Ingest plain text content.
    
    Args:
        request: Ingest request with text content
        embedder: Embedder instance
        qdrant: Qdrant manager instance
        chunker: Chunker instance
        
    Returns:
        Ingestion response with document info
    """
    if not request.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required"
        )
    
    logger.info("Ingesting text content")
    
    try:
        # Prepare metadata
        metadata = {
            "filename": request.filename or "text_content",
            "file_type": "text"
        }
        
        if request.metadata:
            metadata.update(request.metadata)
        
        # Chunk document
        existing_hashes = await qdrant.get_existing_hashes()
        chunks = chunker.chunk_document(
            text=request.content,
            metadata=metadata
        )
        
        # Deduplicate
        chunks = chunker.deduplicate_chunks(chunks, existing_hashes)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All chunks are duplicates, content already ingested"
            )
        
        # Generate embeddings
        embeddings = await embedder.embed_batch([c["text"] for c in chunks])
        
        # Store in Qdrant
        await qdrant.upsert_chunks(chunks, embeddings)
        
        return IngestResponse(
            status="success",
            document_id=chunks[0]["content_hash"][:16],
            chunks_created=len(chunks),
            filename=metadata["filename"],
            file_type="text",
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Text ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest text: {str(e)}"
        )
