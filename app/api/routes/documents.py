"""
Document management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.response import DocumentListResponse, DocumentInfo
from app.retrieval.qdrant_client import QdrantManager
from app.api.deps import get_qdrant_manager
from app.core.logging import logger

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    qdrant: QdrantManager = Depends(get_qdrant_manager)
) -> DocumentListResponse:
    """
    List all ingested documents.
    
    Args:
        qdrant: Qdrant manager instance
        
    Returns:
        List of document information
    """
    logger.info("Listing documents")
    
    try:
        documents = await qdrant.list_documents()
        
        document_infos = [
            DocumentInfo(
                document_id=doc.get("filename", "unknown"),
                filename=doc.get("filename", "unknown"),
                file_type=doc.get("file_type", "unknown"),
                chunk_count=doc.get("chunk_count", 0),
                ingestion_timestamp=doc.get("ingestion_timestamp", ""),
                metadata={}
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            documents=document_infos,
            total_count=len(document_infos)
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    qdrant: QdrantManager = Depends(get_qdrant_manager)
) -> dict[str, str]:
    """
    Delete a document and all its chunks.
    
    Args:
        filename: Document filename to delete
        qdrant: Qdrant manager instance
        
    Returns:
        Success message
    """
    logger.info(f"Deleting document: {filename}")
    
    try:
        await qdrant.delete_document(filename)
        
        return {
            "status": "success",
            "message": f"Document '{filename}' deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
